"""WebSocket chat khách — pipeline + persist + REALTIME 2 chiều (hub) + STATUS-GATE (PRD §6/§8/§10/§12/§16).

Mỗi kết nối khách chạy HAI task (`asyncio.wait` FIRST_COMPLETED):
- `_customer_reader`: đọc tin khách. **STATUS-GATE (08c):** nếu hội thoại đang có người xử lý (IN_HUMAN_QUEUE/
  HUMAN_HANDLING/PENDING_APPROVAL) → AI KHÔNG chạy; lưu tin + đẩy lên admin qua hub. Ngược lại chạy ĐỦ pipeline
  (intent→knowledge→decision→response) rồi trả lời (Response Generator = điểm phát ngôn TỰ ĐỘNG duy nhất, §7.4).
  MỌI lượt (kể cả lượt AI tự trả lời) đều dội tin khách + trả lời lên hub → admin mở ca thấy realtime, không F5.
- `_hub_listener`: nhận tin admin (từ hub) → đẩy xuống socket khách (`{type:"message", from:"admin"}`).

Tín hiệu ra socket khách: `typing` → `reply` (trả lời tự động) | `handoff` (Agent 3 đã chuyển người, ca vào
hàng đợi) | `pending` (gate giữ nháp chờ duyệt). `handoff` là TYPE riêng để FE bám TRẠNG THÁI THẬT thay vì
dò chữ trong câu trả lời.

Ca sinh LƯỜI: lúc `accept()` chỉ TÌM ca đang mở; chưa có thì để trống và chỉ mở ca ở tin nhắn ĐẦU TIÊN —
mở /chat rồi thoát KHÔNG để lại ca rỗng trong hàng đợi admin.

Persist guarded (DB lỗi KHÔNG chặn chat). `db_conversation_id` = khoá hub (TÁCH khỏi thread_id checkpointer).
Hub IN-PROCESS 1 worker (Redis pub/sub đa-worker = sau, FR-ASYNC-7). Handoff → EscalationCard vào hàng đợi (08b).
"""

from __future__ import annotations

import asyncio
import time
import uuid
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ...agents.graph import run_pipeline
from ...core import tracing
from ...core.config import settings
from ...core.database import AsyncSessionLocal
from ...core.logging import get_logger
from ...core.sanitize import sanitize_customer_message
from ...models import User
from ...models.enums import ConversationStatus, MessageSender, TurnOutcome, UserRole
from ...services import audit_service, conversation_service, escalation_service, gate_service
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


async def gate_holds(status_out: str | None, intent: str | None) -> bool:
    """Gate động (P3): auto_reply (status REPLIED) qua VAN gate DB — master `auto_reply_enabled` + per-intent
    `send_directly` (§4). human_handoff (IN_HUMAN_QUEUE) KHÔNG qua đây (escalation an toàn luôn bật).
    DB lỗi → KHÔNG giữ (reply đã grounded + qua Agent 3) để chat không kẹt."""
    try:
        snapshot = await gate_service.get_gate_config()
    except Exception as exc:  # noqa: BLE001 — không đọc được gate → gửi thẳng (đừng kẹt chat).
        log.warning("read gate config failed (gửi thẳng): %s", exc)
        return False
    return gate_service.holds_auto_reply(snapshot, status_out, intent)


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


async def _publish(
    conv_key: str | None,
    payload: dict[str, Any],
    *,
    exclude: asyncio.Queue[dict[str, Any]] | None = None,
) -> None:
    """Phát 1 payload lên hub của ca (admin đang MỞ ca thấy ngay, không phải F5).

    Degrade AN TOÀN: chưa có ca / hub lỗi → bỏ qua, KHÔNG làm rớt hay chậm lượt của khách (bất biến §1).
    """
    if conv_key is None:
        return
    try:
        await hub.publish(conv_key, payload, exclude=exclude)
    except Exception as exc:  # noqa: BLE001 — realtime admin là phụ, đừng để hỏng chat.
        log.warning("publish to hub failed (bỏ qua): %s", exc)


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
    msg: str,
    history: list[dict[str, str]] | None,
    turn_id: uuid.UUID,
    customer_id: uuid.UUID | None = None,
) -> tuple[str | None, dict[str, Any] | None, str]:
    """Chạy pipeline → (status, final, reply). Lỗi → (None, None, _ERROR_REPLY), KHÔNG rớt WS.

    `customer_id` = danh tính khách từ JWT → Agent 2 tra đơn SCOPED (chỉ đơn của chính khách này)."""
    try:
        final = await run_pipeline(
            input_text=msg,
            history=history,
            turn_id=str(turn_id),
            customer_id=str(customer_id) if customer_id else None,
        )
        reply = (final.get("result") or {}).get("reply") or _ERROR_REPLY
        return final.get("status"), final, reply
    except Exception as exc:  # noqa: BLE001 — lỗi pipeline → xin lỗi, KHÔNG rớt kết nối.
        log.warning("pipeline failed on WS message -> apology: %s", exc)
        return None, None, _ERROR_REPLY


def _elapsed_ms(started: float) -> int:
    return int((time.perf_counter() - started) * 1000)


def _outcome_of(status_out: str | None, final: dict[str, Any] | None) -> str:
    """Kết cục GIAO của lượt (hàm thuần) — nguồn KPI %auto/%chuyển người ở tab Báo cáo.

    Đọc kết cục THẬT chứ không đọc `action` của Agent 3: ca `auto_reply` vẫn có thể bị gate giữ nháp
    (nhánh đó tự gắn HELD_FOR_APPROVAL trước khi tới đây).
    """
    if final is None:
        return TurnOutcome.ERROR
    if status_out == ConversationStatus.IN_HUMAN_QUEUE:
        return TurnOutcome.QUEUED_FOR_HUMAN
    return TurnOutcome.SENT


async def _audit_turn(
    st: _CustomerSession,
    turn_id: uuid.UUID,
    customer_text: str,
    final: dict[str, Any] | None,
    reply: str,
    outcome: str,
    total_ms: int,
) -> None:
    """Ghi nhật ký lượt — gọi SAU khi khách đã nhận phản hồi nên không ảnh hưởng độ trễ khách thấy.

    `conversation_id` lấy từ `st.conv_id` (ca THẬT trong DB): WS gọi `run_pipeline` không truyền
    conversation_id nên `final["conversation_id"]` chỉ là thread_id ngẫu nhiên của checkpointer.
    `record_turn` tự nuốt lỗi (bất biến §1) → không cần try/except ở đây.

    **`asyncio.shield`**: khách đóng tab NGAY sau khi nhận trả lời → WS đứt → task reader bị huỷ giữa
    chừng. Không shield thì chính lượt vừa xong mất dòng audit, và mọi KPI lệch âm thầm (đo được:
    lượt cuối của kịch bản verify biến mất khỏi audit_log). Shield cho phép việc ghi chạy nốt sau khi
    task bị huỷ.
    """
    await asyncio.shield(
        audit_service.record_turn(
            turn_id=turn_id,
            conversation_id=st.conv_id,
            customer_text=customer_text,
            final=final,
            reply=reply,
            outcome=outcome,
            total_ms=total_ms,
        )
    )


# ── Trạng thái 1 kết nối khách (P2) — ca hiện tại có thể ĐỔI khi ca cũ bị đóng ────
_SWITCH = object()  # sentinel: đánh thức _hub_listener để đọc queue của ca mới


class _CustomerSession:
    """Khách + ca đang mở + queue hub của ca đó. `conv_id/conv_key/queue` đổi khi mở ca mới.

    Tạo ca LƯỜI: mở chat mà chưa nhắn thì `conv_id` còn None (chưa có ca nào trong DB). `attached` báo cho
    `_hub_listener` biết lúc đã có ca để bắt đầu đọc queue.
    """

    def __init__(self, customer_id: uuid.UUID, display: str | None) -> None:
        self.customer_id = customer_id
        self.display = display
        self.conv_id: uuid.UUID | None = None
        self.conv_key: str | None = None
        self.queue: asyncio.Queue[dict[str, Any]] | None = None
        self.attached = asyncio.Event()  # set khi kết nối đã gắn vào MỘT ca (lần đầu)


def _switch_conversation(st: _CustomerSession, new_conv_id: uuid.UUID) -> None:
    """Chuyển kết nối sang ca mới: đăng ký hub queue mới, huỷ đăng ký cũ, đánh thức listener (sentinel)."""
    old_queue, old_key = st.queue, st.conv_key
    st.conv_id = new_conv_id
    st.conv_key = str(new_conv_id)
    st.queue = hub.register(st.conv_key)
    st.attached.set()  # gỡ chốt cho _hub_listener (kết nối mở trước khi có ca — tạo lười)
    if old_key is not None and old_queue is not None:
        hub.unregister(old_key, old_queue)
        old_queue.put_nowait(_SWITCH)  # đánh thức _hub_listener để đọc st.queue mới


async def _open_new_case(st: _CustomerSession) -> None:
    """Mở ca MỚI (AI-first) cho khách + chuyển hub sang ca mới.

    Dùng ở HAI chỗ: tin nhắn đầu tiên (tạo lười) và khi ca cũ đã đóng. DB lỗi → giữ nguyên ca hiện tại
    (có thể là CHƯA có ca) → lượt vẫn chạy nhưng không persist/hub; KHÔNG rớt WS.
    """
    try:
        async with AsyncSessionLocal() as s:
            conv = await conversation_service.open_case_for_customer(
                s, st.customer_id, display=st.display
            )
        _switch_conversation(st, conv.id)
    except Exception as exc:  # noqa: BLE001 — không mở được ca → chạy tiếp không persist.
        log.warning("open new case failed (chạy tiếp, không persist): %s", exc)


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
            # Lớp A (slice 13): chuẩn hoá + cap NGAY tại biên — mọi đường phía sau (persist, hub,
            # pipeline, prompt LLM) chỉ thấy bản đã sạch. Cắt bớt, KHÔNG rớt kết nối.
            msg = sanitize_customer_message(await websocket.receive_text())
            if st.conv_id is None:
                # TẠO LƯỜI: ca chỉ sinh khi khách THỰC SỰ nhắn. Mở /chat rồi thoát KHÔNG để lại ca rỗng
                # `ACTIVE_AI` làm loãng hàng đợi admin.
                await _open_new_case(st)
                status = ConversationStatus.ACTIVE_AI
            else:
                status = await _load_status(st.conv_id)
                if status in _CLOSED_STATUSES:
                    # Ca đã đóng (admin resolve giữa các lượt) → mở ca mới, agent chạy lại từ đầu (AI-first).
                    await _open_new_case(st)
                    status = ConversationStatus.ACTIVE_AI
            if not should_run_ai(status):
                # Đang có người xử lý → KHÔNG chạy AI: lưu tin khách + đẩy lên admin qua hub.
                await _persist_message(st.conv_id, MessageSender.CUSTOMER, msg)
                await _publish(
                    st.conv_key, {"type": "message", "from": "customer", "content": msg}, exclude=st.queue
                )
                continue
            # AI-active: pipeline đầy đủ. history = lượt TRƯỚC (nạp trước khi lưu tin hiện tại) — THEO CA.
            # `turn_id` sinh Ở ĐÂY (không trong pipeline): lượt pipeline NÉM LỖI vẫn ghi audit được.
            turn_id = uuid.uuid4()
            started = time.perf_counter()
            # Gắn ngữ cảnh lượt cho Langfuse (P3): trace LLM tra ngược được về `trc_…` ở tab Báo cáo.
            # No-op nếu chưa cấu hình Langfuse.
            tracing.set_turn(str(turn_id), str(st.conv_id) if st.conv_id else None)
            await websocket.send_json({"type": "typing"})
            history = await _load_history(st.conv_id)
            await _persist_message(st.conv_id, MessageSender.CUSTOMER, msg)
            # Trước khi chạy pipeline: admin đang mở ca thấy câu hỏi NGAY (mọi nhánh sau đó — reply thường,
            # gate giữ nháp, handoff — đều đã đi qua đây).
            await _publish(
                st.conv_key, {"type": "message", "from": "customer", "content": msg}, exclude=st.queue
            )
            status_out, final, reply = await _run_pipeline_safe(msg, history, turn_id, st.customer_id)

            # Gate động P3: auto_reply không "gửi thẳng" → GIỮ nháp (PENDING_APPROVAL), KHÔNG gửi thẳng cho khách.
            if final is not None and await gate_holds(status_out, final.get("intent")):
                await websocket.send_json({"type": "pending"})  # gỡ typing ở FE (KHÔNG gửi nội dung — sole-egress)
                total_ms = _elapsed_ms(started)  # chốt NGAY khi khách nhận tín hiệu (đúng nghĩa NFR-1)
                # Audit NGAY sau tín hiệu cho khách: càng để sau càng nhiều cơ hội bị huỷ vì khách đóng tab.
                await _audit_turn(st, turn_id, msg, final, reply, TurnOutcome.HELD_FOR_APPROVAL, total_ms)
                await _persist_status(st.conv_id, ConversationStatus.PENDING_APPROVAL)
                await _persist_escalation_card(st.conv_id, final, msg, suggested_reply=reply)
                continue  # nháp giữ trong card, chờ admin duyệt/sửa/gửi

            # TÍN HIỆU chuyển người là TYPE riêng, không để FE đoán qua nội dung câu chữ: escalation là
            # QUYẾT ĐỊNH của Agent 3 (status IN_HUMAN_QUEUE), nên FE phải bám state chứ không dò chữ
            # "nhân viên hỗ trợ" — auto_reply nhắc tới nhân viên KHÔNG phải là đã chuyển người.
            queued = status_out == ConversationStatus.IN_HUMAN_QUEUE
            await websocket.send_json({"type": "handoff" if queued else "reply", "content": reply})
            total_ms = _elapsed_ms(started)  # đo tới lúc khách NHẬN reply, chưa tính persist phía sau
            # Sau khi khách nhận (không tính vào total_ms): dội trả lời AI lên hub cho admin đang theo dõi.
            await _publish(
                st.conv_key, {"type": "message", "from": "ai", "content": reply}, exclude=st.queue
            )
            await _audit_turn(st, turn_id, msg, final, reply, _outcome_of(status_out, final), total_ms)
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

    Chưa có ca (tạo lười) → CHỜ `attached` chứ KHÔNG kết thúc task: task này xong là `asyncio.wait`
    (FIRST_COMPLETED) sẽ huỷ luôn reader và đóng kết nối của khách chưa kịp nhắn gì.
    """
    while True:
        queue = st.queue
        if queue is None:
            await st.attached.wait()
            continue
        payload = await queue.get()
        if payload is _SWITCH:
            continue  # ca đã chuyển → đọc st.queue mới ở vòng sau
        await websocket.send_json(payload)


async def _customer_ai_only(websocket: WebSocket) -> None:
    """Degrade: KHÔNG tạo được conversation → chạy AI trực tiếp, KHÔNG persist/hub/status-gate."""
    try:
        while True:
            msg = sanitize_customer_message(await websocket.receive_text())  # Lớp A (slice 13)
            await websocket.send_json({"type": "typing"})
            # KHÔNG audit nhánh này: tới đây nghĩa là DB không dùng được, ghi audit chỉ tổ sinh log lỗi.
            _, _, reply = await _run_pipeline_safe(msg, None, uuid.uuid4())
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

    # Mô hình hội thoại theo khách: chỉ TÌM ca đang mở. KHÔNG mở ca mới ở đây — ca sinh LƯỜI ở tin nhắn
    # ĐẦU TIÊN (`_customer_reader`), nếu không thì mỗi lần khách mở /chat rồi thoát lại đẻ một ca rỗng.
    try:
        async with AsyncSessionLocal() as s:
            conv = await conversation_service.get_active_conversation_for_customer(s, customer_id)
    except Exception as exc:  # noqa: BLE001 — DB lỗi → chat AI-only (KHÔNG persist/hub/status-gate).
        log.warning("resolve conversation failed (ai-only): %s", exc)
        await _customer_ai_only(websocket)
        return

    if conv is not None:
        _switch_conversation(st, conv.id)  # đăng ký hub cho ca đang mở (lịch sử nạp qua GET /me/thread)
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
