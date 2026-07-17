"""WebSocket chat khách — pipeline + persist + REALTIME 2 chiều (hub) + STATUS-GATE (PRD §6/§8/§10/§12/§16).

Mỗi kết nối khách chạy HAI task (`asyncio.wait` FIRST_COMPLETED):
- `_customer_reader`: đọc tin khách. **STATUS-GATE (08c):** nếu hội thoại đang có người xử lý (IN_HUMAN_QUEUE/
  HUMAN_HANDLING/PENDING_APPROVAL) → AI KHÔNG chạy; lưu tin + đẩy lên admin qua hub. Ngược lại chạy ĐỦ pipeline
  (intent→knowledge→decision→response) rồi trả lời (Response Generator = điểm phát ngôn TỰ ĐỘNG duy nhất, §7.4).
- `_hub_listener`: nhận tin admin (từ hub) → đẩy xuống socket khách (`{type:"message", from:"admin"}`).

Persist guarded (DB lỗi KHÔNG chặn chat). `db_conversation_id` = khoá hub (TÁCH khỏi thread_id checkpointer).
Hub IN-PROCESS 1 worker (Redis pub/sub đa-worker = sau, FR-ASYNC-7). Handoff → EscalationCard vào hàng đợi (08b).
"""

from __future__ import annotations

import asyncio
import uuid
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ...agents.graph import run_pipeline
from ...core.config import settings
from ...core.database import AsyncSessionLocal
from ...core.logging import get_logger
from ...models.enums import ConversationStatus, MessageSender
from ...services import conversation_service, escalation_service
from .hub import hub

router = APIRouter()
log = get_logger("ws.chat")

# Câu xin lỗi khi pipeline lỗi bất ngờ — KHÔNG rớt WS (phanh cuối, đừng để khách thấy stacktrace).
_ERROR_REPLY = (
    "Dạ hệ thống đang gặp trục trặc tạm thời, em xin phép chuyển yêu cầu tới nhân viên hỗ trợ ạ. "
    "Mong anh/chị thông cảm."
)

# Status-gate (08c): hội thoại đang có người xử lý → AI KHÔNG chạy (chỉ định tuyến tin khách sang admin).
HUMAN_HANDLED_STATUSES = frozenset(
    {
        ConversationStatus.IN_HUMAN_QUEUE,
        ConversationStatus.HUMAN_HANDLING,
        ConversationStatus.PENDING_APPROVAL,
    }
)


def should_run_ai(status: str | None) -> bool:
    """AI chỉ chạy khi hội thoại KHÔNG ở trạng thái người-đang-xử-lý (status-gate 08c). Hàm thuần (test offline)."""
    return status not in HUMAN_HANDLED_STATUSES


# ── Persist / load helpers (guarded — DB lỗi KHÔNG chặn chat) ─────────────────
async def _persist_message(conv_id: uuid.UUID | None, sender: str, content: str) -> None:
    """Lưu 1 message (session NGẮN)."""
    if conv_id is None:
        return
    try:
        async with AsyncSessionLocal() as s:
            await conversation_service.add_message(s, conv_id, content=content, sender=sender)
    except Exception as exc:  # noqa: BLE001 — persist là phụ, đừng để hỏng chat.
        log.warning("persist message failed (bỏ qua): %s", exc)


async def _persist_status(conv_id: uuid.UUID | None, status: str | None) -> None:
    if conv_id is None or not status:
        return
    try:
        async with AsyncSessionLocal() as s:
            await conversation_service.set_status(s, conv_id, status)
    except Exception as exc:  # noqa: BLE001
        log.warning("set status failed (bỏ qua): %s", exc)


async def _persist_escalation_card(
    conv_id: uuid.UUID | None, final: dict[str, Any], trigger_message: str
) -> None:
    """Handoff → lưu EscalationCard (dựng từ final state) + priority/severity/reason lên conversation (08b)."""
    if conv_id is None:
        return
    try:
        card = escalation_service.build_escalation_card(final, trigger_message)
        async with AsyncSessionLocal() as s:
            await escalation_service.persist_escalation(
                s,
                conv_id,
                card=card,
                priority=final.get("priority"),
                severity=final.get("severity"),
                reason=final.get("escalation_reason"),
            )
    except Exception as exc:  # noqa: BLE001 — persist card là phụ, đừng để hỏng chat.
        log.warning("persist escalation card failed (bỏ qua): %s", exc)


async def _load_history(conv_id: uuid.UUID | None) -> list[dict[str, str]]:
    """Nạp N tin gần nhất (history_window) từ DB — bộ nhớ đa lượt. Guarded: DB lỗi → [] (chat vẫn chạy)."""
    if conv_id is None:
        return []
    try:
        async with AsyncSessionLocal() as s:
            return await conversation_service.get_recent_messages(s, conv_id, settings.history_window)
    except Exception as exc:  # noqa: BLE001
        log.warning("load history failed (bỏ qua): %s", exc)
        return []


async def _load_status(conv_id: uuid.UUID | None) -> str | None:
    """conversation.status cho status-gate (nhẹ). Guarded: DB lỗi → None (coi như AI-active, an toàn UX)."""
    if conv_id is None:
        return None
    try:
        async with AsyncSessionLocal() as s:
            return await conversation_service.get_status(s, conv_id)
    except Exception as exc:  # noqa: BLE001
        log.warning("load status failed (bỏ qua): %s", exc)
        return None


async def _run_pipeline_safe(
    msg: str, history: list[dict[str, str]] | None
) -> tuple[str | None, dict[str, Any] | None, str]:
    """Chạy pipeline → (status, final, reply). Lỗi → (None, None, _ERROR_REPLY), KHÔNG rớt WS."""
    try:
        final = await run_pipeline(input_text=msg, history=history)
        reply = (final.get("result") or {}).get("reply") or _ERROR_REPLY
        return final.get("status"), final, reply
    except Exception as exc:  # noqa: BLE001 — lỗi pipeline → xin lỗi, KHÔNG rớt kết nối.
        log.warning("pipeline failed on WS message -> apology: %s", exc)
        return None, None, _ERROR_REPLY


# ── Hai task cho một kết nối khách ───────────────────────────────────────────
async def _customer_reader(
    websocket: WebSocket,
    conv_id: uuid.UUID,
    conv_key: str,
    self_queue: asyncio.Queue[dict[str, Any]],
) -> None:
    """Đọc tin khách. STATUS-GATE: người đang xử lý → route sang admin (hub); ngược lại chạy pipeline + trả lời."""
    try:
        while True:
            msg = await websocket.receive_text()
            if not should_run_ai(await _load_status(conv_id)):
                # Đang có người xử lý → KHÔNG chạy AI: lưu tin khách + đẩy lên admin qua hub.
                await _persist_message(conv_id, MessageSender.CUSTOMER, msg)
                await hub.publish(
                    conv_key, {"type": "message", "from": "customer", "content": msg}, exclude=self_queue
                )
                continue
            # AI-active: pipeline đầy đủ + trả lời. history = lượt TRƯỚC (nạp trước khi lưu tin hiện tại).
            await websocket.send_json({"type": "typing"})
            history = await _load_history(conv_id)
            await _persist_message(conv_id, MessageSender.CUSTOMER, msg)
            status_out, final, reply = await _run_pipeline_safe(msg, history)
            await websocket.send_json({"type": "reply", "content": reply})
            await _persist_message(conv_id, MessageSender.AI, reply)
            await _persist_status(conv_id, status_out)
            # Handoff → EscalationCard vào hàng đợi admin (08b). Chỉ khi pipeline chạy xong (final có).
            if status_out == ConversationStatus.IN_HUMAN_QUEUE and final is not None:
                await _persist_escalation_card(conv_id, final, msg)
    except WebSocketDisconnect:
        log.info("customer WS disconnected (conv=%s)", conv_id)


async def _hub_listener(websocket: WebSocket, queue: asyncio.Queue[dict[str, Any]]) -> None:
    """Nhận payload (tin admin) từ hub → đẩy xuống socket khách."""
    while True:
        payload = await queue.get()
        await websocket.send_json(payload)


async def _customer_ai_only(websocket: WebSocket) -> None:
    """Degrade: KHÔNG tạo được conversation → chạy AI trực tiếp, KHÔNG persist/hub/status-gate."""
    try:
        while True:
            msg = await websocket.receive_text()
            await websocket.send_json({"type": "typing"})
            _, _, reply = await _run_pipeline_safe(msg, None)
            await websocket.send_json({"type": "reply", "content": reply})
    except WebSocketDisconnect:
        log.info("customer WS (ai-only) disconnected")


@router.websocket("/ws/chat")
async def chat_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    sid = websocket.query_params.get("sid") or str(uuid4())  # guest, KHÔNG auth (tài khoản = slice 11)

    db_conversation_id: uuid.UUID | None = None
    try:
        async with AsyncSessionLocal() as s:
            conv = await conversation_service.create_conversation(s, customer_identifier=sid)
            db_conversation_id = conv.id
    except Exception as exc:  # noqa: BLE001 — không tạo được conversation -> chat vẫn chạy, chỉ không persist.
        log.warning("create_conversation failed (chat vẫn chạy, KHÔNG persist): %s", exc)

    await websocket.send_json({"type": "system", "message": "connected"})
    log.info("customer WS connected (sid=%s conv=%s)", sid, db_conversation_id)

    if db_conversation_id is None:  # không persist được → không có khoá hub → chạy AI-only.
        await _customer_ai_only(websocket)
        return

    # Realtime 2 chiều: đăng ký hub theo conversation, chạy reader + hub-listener song song.
    conv_key = str(db_conversation_id)
    queue = hub.register(conv_key)
    reader = asyncio.create_task(_customer_reader(websocket, db_conversation_id, conv_key, queue))
    listener = asyncio.create_task(_hub_listener(websocket, queue))
    try:
        _, pending = await asyncio.wait({reader, listener}, return_when=asyncio.FIRST_COMPLETED)
        for task in pending:  # một task xong (rớt kết nối) → huỷ task còn lại
            task.cancel()
        await asyncio.gather(*pending, return_exceptions=True)
    finally:
        hub.unregister(conv_key, queue)
        log.info("customer WS closed (conv=%s)", db_conversation_id)
