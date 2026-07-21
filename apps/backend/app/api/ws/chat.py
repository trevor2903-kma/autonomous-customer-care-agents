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

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ...agents.graph import run_pipeline
from ...core.config import settings
from ...core.database import AsyncSessionLocal
from ...core.logging import get_logger
from ...models import User
from ...models.enums import ConversationStatus, MessageSender, UserRole
from ...services import conversation_service, escalation_service
from .auth import WS_AUTH_CLOSE_CODE, authenticate_websocket
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

# Ca "đã đóng" (P2): khách nhắn tiếp → mở ca MỚI (AI-first), KHÔNG chạy lại trên ca cũ.
_CLOSED_STATUSES = frozenset({ConversationStatus.RESOLVED, ConversationStatus.CLOSED})


def should_run_ai(status: str | None) -> bool:
    """AI chỉ chạy khi hội thoại KHÔNG ở trạng thái người-đang-xử-lý (status-gate 08c). Hàm thuần (test offline)."""
    return status not in HUMAN_HANDLED_STATUSES


def gate_holds(status_out: str | None, intent: str | None) -> bool:
    """Gate duyệt nháp (08a, FR-GATE): auto_reply (status REPLIED) + intent NHẠY CẢM + review bật → GIỮ nháp
    (PENDING_APPROVAL, chờ admin duyệt). human_handoff (IN_HUMAN_QUEUE) KHÔNG qua đây (luôn escalate). Hàm thuần."""
    return (
        settings.auto_reply_review
        and status_out == ConversationStatus.REPLIED
        and (intent or "") in settings.sensitive_intent_set
    )


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
    conv_id: uuid.UUID | None, final: dict[str, Any], trigger_message: str, suggested_reply: str = ""
) -> None:
    """Lưu EscalationCard (dựng từ final state) + priority/severity/reason lên conversation. `suggested_reply`
    rỗng cho handoff (08b); = nháp Agent 4 cho ca PENDING_APPROVAL (08a)."""
    if conv_id is None:
        return
    try:
        card = escalation_service.build_escalation_card(final, trigger_message, suggested_reply)
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


# ── Trạng thái 1 kết nối khách (P2) — ca hiện tại có thể ĐỔI khi ca cũ bị đóng ────
_SWITCH = object()  # sentinel: đánh thức _hub_listener để đọc queue của ca mới


class _CustomerSession:
    """Khách + ca đang mở + queue hub của ca đó. `conv_id/conv_key/queue` đổi khi mở ca mới."""

    def __init__(self, customer_id: uuid.UUID, display: str | None) -> None:
        self.customer_id = customer_id
        self.display = display
        self.conv_id: uuid.UUID | None = None
        self.conv_key: str | None = None
        self.queue: asyncio.Queue[dict[str, Any]] | None = None


def _switch_conversation(st: _CustomerSession, new_conv_id: uuid.UUID) -> None:
    """Chuyển kết nối sang ca mới: đăng ký hub queue mới, huỷ đăng ký cũ, đánh thức listener (sentinel)."""
    old_queue, old_key = st.queue, st.conv_key
    st.conv_id = new_conv_id
    st.conv_key = str(new_conv_id)
    st.queue = hub.register(st.conv_key)
    if old_key is not None and old_queue is not None:
        hub.unregister(old_key, old_queue)
        old_queue.put_nowait(_SWITCH)  # đánh thức _hub_listener để đọc st.queue mới


async def _open_new_case(st: _CustomerSession) -> None:
    """Mở ca MỚI (AI-first) cho khách + chuyển hub sang ca mới. DB lỗi → giữ ca cũ (đừng rớt WS)."""
    try:
        async with AsyncSessionLocal() as s:
            conv = await conversation_service.open_case_for_customer(
                s, st.customer_id, display=st.display
            )
        _switch_conversation(st, conv.id)
    except Exception as exc:  # noqa: BLE001 — không mở được ca mới → giữ ca cũ.
        log.warning("open new case failed (giữ ca cũ): %s", exc)


async def _load_customer_display(customer_id: uuid.UUID) -> str | None:
    """display cho customer_identifier (hiển thị admin) = display_name hoặc email. Guarded."""
    try:
        async with AsyncSessionLocal() as s:
            user = await s.get(User, customer_id)
            return (user.display_name or user.email) if user else None
    except Exception as exc:  # noqa: BLE001
        log.warning("load customer display failed (bỏ qua): %s", exc)
        return None


# ── Hai task cho một kết nối khách ───────────────────────────────────────────
async def _customer_reader(websocket: WebSocket, st: _CustomerSession) -> None:
    """Đọc tin khách. Ca đóng giữa lượt → mở ca mới (AI-first). Người đang xử lý → route admin; ngược lại pipeline."""
    try:
        while True:
            msg = await websocket.receive_text()
            status = await _load_status(st.conv_id)
            if status in _CLOSED_STATUSES:
                # Ca đã đóng (admin resolve giữa các lượt) → mở ca mới, agent chạy lại từ đầu (AI-first).
                await _open_new_case(st)
                status = ConversationStatus.ACTIVE_AI
            if not should_run_ai(status):
                # Đang có người xử lý → KHÔNG chạy AI: lưu tin khách + đẩy lên admin qua hub.
                await _persist_message(st.conv_id, MessageSender.CUSTOMER, msg)
                await hub.publish(
                    st.conv_key, {"type": "message", "from": "customer", "content": msg}, exclude=st.queue
                )
                continue
            # AI-active: pipeline đầy đủ. history = lượt TRƯỚC (nạp trước khi lưu tin hiện tại) — THEO CA.
            await websocket.send_json({"type": "typing"})
            history = await _load_history(st.conv_id)
            await _persist_message(st.conv_id, MessageSender.CUSTOMER, msg)
            status_out, final, reply = await _run_pipeline_safe(msg, history)

            # Gate 08a: auto_reply nhạy cảm → GIỮ nháp (PENDING_APPROVAL), KHÔNG gửi thẳng cho khách.
            if final is not None and gate_holds(status_out, final.get("intent")):
                await websocket.send_json({"type": "pending"})  # gỡ typing ở FE (KHÔNG gửi nội dung — sole-egress)
                await _persist_status(st.conv_id, ConversationStatus.PENDING_APPROVAL)
                await _persist_escalation_card(st.conv_id, final, msg, suggested_reply=reply)
                continue  # nháp giữ trong card, chờ admin duyệt/sửa/gửi

            await websocket.send_json({"type": "reply", "content": reply})
            await _persist_message(st.conv_id, MessageSender.AI, reply)
            await _persist_status(st.conv_id, status_out)
            # Handoff → EscalationCard vào hàng đợi admin (08b). Chỉ khi pipeline chạy xong (final có).
            if status_out == ConversationStatus.IN_HUMAN_QUEUE and final is not None:
                await _persist_escalation_card(st.conv_id, final, msg)
    except WebSocketDisconnect:
        log.info("customer WS disconnected (conv=%s)", st.conv_id)


async def _hub_listener(websocket: WebSocket, st: _CustomerSession) -> None:
    """Nhận payload (tin admin) từ hub của ca HIỆN TẠI → đẩy xuống socket khách.

    `_SWITCH` = ca đã chuyển (mở ca mới) → vòng sau đọc st.queue mới. Nhờ vậy khách vẫn nhận được tin admin
    nếu ca mới sau này escalate + có người tiếp quản, dù conv_id đã đổi giữa kết nối.
    """
    while True:
        queue = st.queue
        if queue is None:
            return
        payload = await queue.get()
        if payload is _SWITCH:
            continue  # ca đã chuyển → đọc st.queue mới ở vòng sau
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
    auth = await authenticate_websocket(websocket, UserRole.CUSTOMER)  # JWT ?token= (P1)
    if auth is None:
        return  # helper đã đóng 4401 (thiếu/sai token hoặc sai role)
    try:
        customer_id = uuid.UUID(str(auth.get("sub")))
    except (ValueError, TypeError):
        await websocket.close(code=WS_AUTH_CLOSE_CODE)
        return

    display = await _load_customer_display(customer_id)
    st = _CustomerSession(customer_id, display)

    # Mô hình hội thoại theo khách (P2): tìm-ca-active-hoặc-mở-ca-mới (thay tạo-ca-mỗi-kết-nối).
    try:
        async with AsyncSessionLocal() as s:
            conv = await conversation_service.get_active_conversation_for_customer(s, customer_id)
            if conv is None:
                conv = await conversation_service.open_case_for_customer(s, customer_id, display=display)
            initial_conv_id = conv.id
    except Exception as exc:  # noqa: BLE001 — DB lỗi → chat AI-only (KHÔNG persist/hub/status-gate).
        log.warning("resolve conversation failed (ai-only): %s", exc)
        await _customer_ai_only(websocket)
        return

    _switch_conversation(st, initial_conv_id)  # đăng ký hub cho ca hiện tại
    await websocket.send_json({"type": "system", "message": "connected"})
    log.info("customer WS connected (customer=%s conv=%s)", customer_id, st.conv_id)

    # Realtime 2 chiều: reader + hub-listener song song (queue theo ca hiện tại của st).
    reader = asyncio.create_task(_customer_reader(websocket, st))
    listener = asyncio.create_task(_hub_listener(websocket, st))
    try:
        _, pending = await asyncio.wait({reader, listener}, return_when=asyncio.FIRST_COMPLETED)
        for task in pending:  # một task xong (rớt kết nối) → huỷ task còn lại
            task.cancel()
        await asyncio.gather(*pending, return_exceptions=True)
    finally:
        if st.conv_key is not None and st.queue is not None:
            hub.unregister(st.conv_key, st.queue)
        log.info("customer WS closed (conv=%s)", st.conv_id)
