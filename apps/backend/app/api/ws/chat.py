"""WebSocket chat — cổng chat khách chạy ĐỦ pipeline + LƯU hội thoại (PRD §6, §8, §12, §16).

Mỗi tin khách → `{"type":"typing"}` → chạy pipeline (intent → knowledge → decision → response) → `{"type":"reply"}`
(câu trả lời/thông báo handoff do RESPONSE GENERATOR sinh — điểm phát ngôn DUY NHẤT, PRD §7.4). Lỗi pipeline →
câu xin lỗi, KHÔNG rớt kết nối.

Persistence (slice 09a): guest `?sid=` (hoặc uuid) → tạo Conversation; lưu message khách & AI vào Postgres
(session NGẮN — Neon free) + cập nhật `conversation.status`. Persist ĐƯỢC BỌC try/except: DB lỗi KHÔNG chặn chat.
`db_conversation_id` (persist) TÁCH khỏi `thread_id` checkpointer (run_pipeline tự sinh mỗi lượt). Bộ nhớ đa lượt
lấy từ DB (Phase 4), KHÔNG từ checkpointer.

Phạm vi: 1 khách/1 kết nối → gửi thẳng qua WS (KHÔNG Redis pub/sub — FR-ASYNC-7, để dành). Định tuyến tin tới
Admin khi IN_HUMAN_QUEUE/HUMAN_HANDLING = slice 08b/08c.
"""

from __future__ import annotations

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

router = APIRouter()
log = get_logger("ws.chat")

# Câu xin lỗi khi pipeline lỗi bất ngờ — KHÔNG rớt WS (phanh cuối, đừng để khách thấy stacktrace).
_ERROR_REPLY = (
    "Dạ hệ thống đang gặp trục trặc tạm thời, em xin phép chuyển yêu cầu tới nhân viên hỗ trợ ạ. "
    "Mong anh/chị thông cảm."
)


async def _persist_message(conv_id: uuid.UUID | None, sender: str, content: str) -> None:
    """Lưu 1 message (session NGẮN). Guarded: DB lỗi KHÔNG chặn chat (chỉ log)."""
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
    """Handoff → lưu EscalationCard (dựng từ final state) + priority/severity/reason lên conversation (08b).
    Guarded: DB lỗi KHÔNG chặn chat."""
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


@router.websocket("/ws/chat")
async def chat_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    sid = websocket.query_params.get("sid") or str(uuid4())  # guest, KHÔNG auth (tài khoản = slice 11)

    # Tạo Conversation (session NGẮN). db_conversation_id TÁCH khỏi thread_id checkpointer.
    db_conversation_id: uuid.UUID | None = None
    try:
        async with AsyncSessionLocal() as s:
            conv = await conversation_service.create_conversation(s, customer_identifier=sid)
            db_conversation_id = conv.id
    except Exception as exc:  # noqa: BLE001 — không tạo được conversation -> chat vẫn chạy, chỉ không persist.
        log.warning("create_conversation failed (chat vẫn chạy, KHÔNG persist): %s", exc)

    await websocket.send_json({"type": "system", "message": "connected"})
    log.info("WebSocket client connected (sid=%s conv=%s)", sid, db_conversation_id)
    try:
        while True:
            msg = await websocket.receive_text()
            await websocket.send_json({"type": "typing"})  # UX: hiện "đang trả lời…"
            # Nạp lịch sử các lượt TRƯỚC (từ DB) — TRƯỚC khi lưu tin hiện tại (history = lượt trước, không gồm msg).
            history = await _load_history(db_conversation_id)
            await _persist_message(db_conversation_id, MessageSender.CUSTOMER, msg)

            status: str | None = None
            final: dict[str, Any] | None = None
            try:
                final = await run_pipeline(input_text=msg, history=history)
                reply = (final.get("result") or {}).get("reply") or _ERROR_REPLY
                status = final.get("status")
            except Exception as exc:  # noqa: BLE001 — lỗi pipeline → xin lỗi, KHÔNG rớt kết nối.
                log.warning("pipeline failed on WS message -> apology: %s", exc)
                reply = _ERROR_REPLY

            await websocket.send_json({"type": "reply", "content": reply})
            await _persist_message(db_conversation_id, MessageSender.AI, reply)
            await _persist_status(db_conversation_id, status)
            # Handoff → EscalationCard vào hàng đợi admin (08b). Chỉ khi pipeline chạy xong (final có).
            if status == ConversationStatus.IN_HUMAN_QUEUE and final is not None:
                await _persist_escalation_card(db_conversation_id, final, msg)
    except WebSocketDisconnect:
        log.info("WebSocket client disconnected (sid=%s conv=%s)", sid, db_conversation_id)
