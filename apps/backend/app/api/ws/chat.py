"""WebSocket chat khách — pipeline + persist + REALTIME 2 chiều (hub) + STATUS-GATE (PRD §6/§8/§10/§12/§16).

Mỗi kết nối khách chạy HAI task (`asyncio.wait` FIRST_COMPLETED):
- `_customer_reader`: đọc frame khách (giao thức v2 — contract §4.1). `ping` → `pong` NGAY. Tin nhắn → chống trùng
  `client_msg_id` (tin gửi lại → ack duplicate, KHÔNG tốn hạn mức) → rate-limit (SEC-XC.2) → `ack` NGAY → xếp một
  TASK LƯỢT. Reader KHÔNG chờ lượt chạy xong.
- `_hub_listener`: nhận frame từ hub (tin admin, trả lời AI cho tab khác / cho lượt mà socket gốc đã chết, `status`)
  → đẩy xuống socket khách.

TASK LƯỢT (`_run_turn`) — TUẦN TỰ theo KHÁCH (mọi tab/socket) dưới một `asyncio.Lock` đánh thức FIFO (GRAPH-02.3):
chọn ca (tìm-hoặc-mở DƯỚI khoá → hai tab không đẻ hai ca) → status+intent trước lượt → lưu tin khách → STATUS-GATE
(08c: người đang xử lý → AI KHÔNG chạy, chỉ đẩy tin lên admin) → pipeline (intent→knowledge→decision→response;
Response Generator = điểm phát ngôn TỰ ĐỘNG duy nhất, §7.4) → MỘT bước ghi được shield: CAS status + tin AI +
EscalationCard trong MỘT transaction (GRAPH-02.1) → CHỈ SAU commit mới báo khách → hub → audit. Task lượt KHÔNG bị
huỷ khi socket đóng: khách đóng tab thì lượt vẫn chạy xong + lưu; trả lời tới socket mới qua hub hoặc /me/thread.

CAS (GRAPH-02.2): status chỉ được ghi nếu VẪN là status đọc ở đầu lượt. Admin tiếp quản / đóng ca trong lúc pipeline
chạy → lượt bị BỎ (không lưu gì của lượt), khách nhận frame `status` (status hiện tại) THAY cho câu trả lời.

Tín hiệu ra socket khách: `ack` → `typing` → `reply` (trả lời tự động) | `handoff` (ca vào hàng đợi người) |
`pending` (gate giữ nháp chờ duyệt) | `status` (lượt bị bỏ vì status đổi). `handoff` là TYPE riêng để FE bám
TRẠNG THÁI THẬT thay vì dò chữ trong câu trả lời.

Ca sinh LƯỜI: lúc `accept()` chỉ TÌM ca đang mở; chưa có thì để trống và chỉ mở ca ở tin nhắn ĐẦU TIÊN —
mở /chat rồi thoát KHÔNG để lại ca rỗng trong hàng đợi admin.

Persist guarded (DB lỗi KHÔNG chặn chat — `reply` vẫn gửi). Riêng `handoff`/`pending` hứa một trạng thái ĐÃ commit:
bước ghi của lượt hỏng cả sau 1 lần thử lại → khách nhận `FALLBACK_REPLY` (không hứa gì) thay cho hai frame đó
(GRAPH-02.1). `db_conversation_id` = khoá hub (TÁCH khỏi thread_id checkpointer).
Hub, khoá khách, registry chống trùng, rate limiter đều IN-PROCESS (1 worker; đa-worker = Redis, FR-ASYNC-7).
"""

from __future__ import annotations

import asyncio
import time
import uuid
import weakref
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Literal

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.exc import IntegrityError

from ...agents.graph import run_pipeline
from ...agents.nodes.response import FALLBACK_REPLY
from ...core import tracing
from ...core.config import settings
from ...core.database import AsyncSessionLocal
from ...core.logging import get_logger
from ...core.rate_limit import SlidingWindowLimiter
from ...core.sanitize import sanitize_customer_message
from ...models import User
from ...models.enums import ConversationStatus, MessageSender, Priority, TurnOutcome, UserRole
from ...models.message import CLIENT_MSG_ID_INDEX
from ...services import audit_service, conversation_service, escalation_service, gate_service
from .auth import WS_AUTH_CLOSE_CODE, authenticate_websocket
from .hub import hub, parse_client_frame

router = APIRouter()
log = get_logger("ws.chat")

# Câu xin lỗi khi pipeline lỗi bất ngờ — KHÔNG rớt WS (phanh cuối, đừng để khách thấy stacktrace).
_ERROR_REPLY = (
    "Dạ hệ thống đang gặp trục trặc tạm thời, em xin phép chuyển yêu cầu tới nhân viên hỗ trợ ạ. "
    "Mong anh/chị thông cảm."
)
# PRD §15: lỗi kỹ thuật → IN_HUMAN_QUEUE gắn nhãn [error] — lời hứa chuyển nhân viên của `_ERROR_REPLY` là thật.
ERROR_ESCALATION_REASON = "[error] pipeline lỗi kỹ thuật — chuyển nhân viên tự động"

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

# Status mà lượt AI được phép ghi đè khi KHÔNG đọc được status đầu lượt (DB lỗi): không ai đang xử lý, chưa đóng.
_AI_ACTIVE_STATUSES = frozenset(ConversationStatus) - HUMAN_HANDLED_STATUSES - _CLOSED_STATUSES

# SEC-XC.2: trần tin/cửa sổ theo KHÁCH (cộng dồn mọi tab) — mỗi tin là 2 lời gọi LLM + 1 embedding. 0 = tắt.
_chat_limiter = SlidingWindowLimiter(settings.chat_rate_per_customer, settings.rate_limit_window_seconds)

# GRAPH-02.3: lượt của CÙNG một khách (mọi tab/socket) chạy TUẦN TỰ dưới một asyncio.Lock (đánh thức FIFO → giữ
# thứ tự tới). WeakValueDictionary: không còn lượt nào giữ khoá thì khoá tự thu hồi (không rò theo số khách).
_customer_locks: weakref.WeakValueDictionary[uuid.UUID, asyncio.Lock] = weakref.WeakValueDictionary()
# asyncio chỉ giữ tham chiếu YẾU tới task → giữ MẠNH ở đây, bỏ ra khi xong. KHÔNG huỷ khi socket đóng.
_turn_tasks: set[asyncio.Task[None]] = set()

# IDEM-XC.1: client_msg_id đã nhận gần đây theo khách (in-process, có trần) — chặn tin GỬI LẠI ngay lúc nhận, kể cả
# khi lượt gốc còn đang xếp hàng. Bảo đảm BỀN = partial unique index (conversation_id, client_msg_id) ở DB.
_RECENT_IDS_PER_CUSTOMER = 200
_RECENT_CUSTOMERS_MAX = 10_000
_recent_client_ids: OrderedDict[uuid.UUID, OrderedDict[str, None]] = OrderedDict()

# Kết quả lưu tin khách: "closed" = ca vừa bị đóng dưới chân → chọn lại ca; "unsaved" = chưa có ca / DB lỗi.
_Saved = Literal["ok", "duplicate", "closed", "unsaved"]


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


def _sid(value: Any) -> str | None:
    return str(value) if value is not None else None


def _ms(start: float, end: float) -> int:
    return int((end - start) * 1000)


async def _send(websocket: WebSocket, payload: dict[str, Any]) -> bool:
    """Gửi 1 frame. Socket đã đóng/đứt → bỏ qua: lượt vẫn chạy xong + lưu (khách thấy qua hub hoặc /me/thread)."""
    try:
        await websocket.send_json(payload)
        return True
    except Exception as exc:  # noqa: BLE001 — socket chết KHÔNG được làm chết task lượt.
        log.info("send to closed customer socket (bỏ qua): %s", exc)
        return False


# ── Chống trùng + tuần tự hoá theo khách (in-process) ────────────────────────
def _already_accepted(customer_id: uuid.UUID, client_msg_id: str) -> bool:
    """True nếu id này đã được NHẬN cho khách (tin gửi lại). CHỈ ĐỌC — ghi nhận là `_remember`, SAU rate-limit."""
    ids = _recent_client_ids.get(customer_id)
    return ids is not None and client_msg_id in ids


def _remember(customer_id: uuid.UUID, client_msg_id: str) -> None:
    """Ghi nhận id vừa NHẬN cho khách (có trần: bỏ khách lâu không nhắn nhất / id cũ nhất)."""
    ids = _recent_client_ids.get(customer_id)
    if ids is None:
        if len(_recent_client_ids) >= _RECENT_CUSTOMERS_MAX:
            _recent_client_ids.popitem(last=False)  # bỏ khách lâu không nhắn nhất
        ids = _recent_client_ids[customer_id] = OrderedDict()
    else:
        _recent_client_ids.move_to_end(customer_id)
    ids[client_msg_id] = None
    if len(ids) > _RECENT_IDS_PER_CUSTOMER:
        ids.popitem(last=False)


def _forget(customer_id: uuid.UUID, client_msg_id: str) -> None:
    """Bỏ id khỏi registry — tin KHÔNG lưu được: bản gửi lại khi FE nối lại phải được XỬ LÝ, không bị nuốt (IDEM-XC.1)."""
    ids = _recent_client_ids.get(customer_id)
    if ids is not None:
        ids.pop(client_msg_id, None)


def _customer_lock(customer_id: uuid.UUID) -> asyncio.Lock:
    lock = _customer_locks.get(customer_id)
    if lock is None:
        lock = asyncio.Lock()
        _customer_locks[customer_id] = lock
    return lock


# ── Persist / load helpers (guarded — DB lỗi KHÔNG chặn chat) ─────────────────
async def _persist_customer_message(
    conv_id: uuid.UUID | None, content: str, client_msg_id: str | None
) -> tuple[uuid.UUID | None, _Saved]:
    """Lưu tin khách (session NGẮN) → `(message_id, kết quả)`.

    KHOÁ hàng conversation (SELECT … FOR UPDATE) rồi mới chèn (GRAPH-02.2): ca đã bị đóng (admin resolve / auto-resolve
    commit giữa lúc lượt đọc status và lúc lưu) → `"closed"`, KHÔNG chèn vào ca đã đóng — caller chọn lại ca (ca MỚI,
    PRD §15). Khoá giữ tới commit nên không ai đóng ca xen giữa lúc kiểm và lúc chèn; tin khách xoá mốc đã-nhắc trong
    CÙNG transaction → RESOLVE của auto-resolve tự thua CAS.
    Vi phạm partial unique index (conversation_id, client_msg_id) = tin GỬI LẠI đã có trong DB → `"duplicate"`: caller
    bỏ lượt (pipeline KHÔNG chạy lần hai). Chưa có ca / DB lỗi khác → `(None, "unsaved")`: chat vẫn chạy, không
    persist (như cũ)."""
    if conv_id is None:
        return None, "unsaved"
    try:
        async with AsyncSessionLocal() as s:
            state = await conversation_service.get_status_and_admin(s, conv_id, for_update=True)
            if state is not None and state[0] in _CLOSED_STATUSES:
                return None, "closed"
            message = await conversation_service.insert_message(
                s, conv_id, sender=MessageSender.CUSTOMER, content=content, client_msg_id=client_msg_id
            )
            await s.commit()
            return message.id, "ok"
    except IntegrityError as exc:
        if client_msg_id is not None and CLIENT_MSG_ID_INDEX in str(exc):
            log.info("tin gửi lại (client_msg_id trùng, conv=%s) → bỏ lượt", conv_id)
            return None, "duplicate"
        log.warning("persist message failed (bỏ qua): %s", exc)
        return None, "unsaved"
    except Exception as exc:  # noqa: BLE001 — persist là phụ, đừng để hỏng chat.
        log.warning("persist message failed (bỏ qua): %s", exc)
        return None, "unsaved"


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


async def _load_prior(conv_id: uuid.UUID | None) -> tuple[str | None, str | None]:
    """`(status, current_intent)` TRƯỚC lượt này (nhẹ) — status cho status-gate + loop-guard + CAS, intent gốc để
    resume clarify. Guarded: DB lỗi → (None, None) (coi như AI-active, an toàn UX)."""
    if conv_id is None:
        return (None, None)
    try:
        async with AsyncSessionLocal() as s:
            return await conversation_service.get_status_and_intent(s, conv_id)
    except Exception as exc:  # noqa: BLE001
        log.warning("load prior status/intent failed (bỏ qua): %s", exc)
        return (None, None)


async def _run_pipeline_safe(
    msg: str,
    history: list[dict[str, str]] | None,
    turn_id: uuid.UUID,
    customer_id: uuid.UUID | None = None,
    prior_status: str | None = None,
    prior_intent: str | None = None,
) -> tuple[str | None, dict[str, Any] | None, str]:
    """Chạy pipeline → (status, final, reply). Lỗi → (None, None, _ERROR_REPLY), KHÔNG rớt WS.

    `customer_id` = danh tính khách từ JWT → Agent 2 tra đơn SCOPED (chỉ đơn của chính khách này).
    `prior_status` = status hội thoại TRƯỚC lượt này (09b loop-guard clarify — Decision đọc để biết đã hỏi
    mã đơn 1 lần chưa). `prior_intent` = intent lượt trước → Agent 1 khôi phục đúng intent gốc khi khách
    trả lời câu hỏi clarify bằng mã đơn TRƠ."""
    try:
        final = await run_pipeline(
            input_text=msg,
            history=history,
            turn_id=str(turn_id),
            customer_id=str(customer_id) if customer_id else None,
            prior_status=prior_status,
            prior_intent=prior_intent,
        )
        reply = (final.get("result") or {}).get("reply") or _ERROR_REPLY
        return final.get("status"), final, reply
    except Exception as exc:  # noqa: BLE001 — lỗi pipeline → xin lỗi, KHÔNG rớt kết nối.
        log.warning("pipeline failed on WS message -> apology: %s", exc)
        return None, None, _ERROR_REPLY


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


# ── Quyết định giao + MỘT bước ghi của lượt ──────────────────────────────────
@dataclass(frozen=True)
class TurnPlan:
    """Kết cục giao của một lượt AI: frame báo khách + những gì phải ghi (trong MỘT transaction)."""

    frame: str  # "reply" | "handoff" | "pending"
    status_to: str
    allowed_from: frozenset[str]  # CAS: status đọc ở đầu lượt
    ai_message: str | None  # tin gửi khách + lưu (sender=ai); None cho "pending" — nháp giữ trong card, KHÔNG gửi
    outcome: str
    current_intent: str | None = None
    card: dict[str, Any] | None = None
    priority: str | None = None
    severity: str | None = None
    reason: str | None = None


def plan_delivery(
    *,
    prior_status: str | None,
    status_out: str | None,
    final: dict[str, Any] | None,
    reply: str,
    customer_text: str,
    held: bool,
) -> TurnPlan:
    """Quyết định giao từ kết quả pipeline (HÀM THUẦN, test offline).

    - Pipeline NÉM LỖI (`final` None) → PRD §15: IN_HUMAN_QUEUE gắn nhãn [error] + EscalationCard (priority high);
      khách nhận `handoff` với `_ERROR_REPLY`.
    - Gate giữ nháp → PENDING_APPROVAL + card mang nháp (`suggested_reply`); khách chỉ nhận `pending`.
    - IN_HUMAN_QUEUE (Agent 3 chuyển người, hoặc Agent 4 phải fallback) → EscalationCard + `handoff`.
    - Còn lại (REPLIED / AWAITING_CUSTOMER) → `reply`; AWAITING_CUSTOMER ghi KÈM intent gốc → lượt sau khách gõ mã đơn
      trơ vẫn resume đúng intent (09b).
    CAS: `allowed_from` = status đọc ở đầu lượt; không đọc được → mọi status AI-active.
    """
    allowed = frozenset({prior_status}) if prior_status else _AI_ACTIVE_STATUSES
    if final is None:
        card = escalation_service.build_escalation_card(
            {"escalation_reason": ERROR_ESCALATION_REASON, "priority": Priority.HIGH}, customer_text
        )
        return TurnPlan(
            "handoff",
            ConversationStatus.IN_HUMAN_QUEUE,
            allowed,
            reply,
            _outcome_of(status_out, final),
            card=card,
            priority=Priority.HIGH,
            reason=ERROR_ESCALATION_REASON,
        )
    if held:
        return TurnPlan(
            "pending",
            ConversationStatus.PENDING_APPROVAL,
            allowed,
            None,
            TurnOutcome.HELD_FOR_APPROVAL,
            card=escalation_service.build_escalation_card(final, customer_text, suggested_reply=reply),
            priority=final.get("priority"),
            severity=final.get("severity"),
            reason=final.get("escalation_reason"),
        )
    if status_out == ConversationStatus.IN_HUMAN_QUEUE:
        return TurnPlan(
            "handoff",
            ConversationStatus.IN_HUMAN_QUEUE,
            allowed,
            reply,
            _outcome_of(status_out, final),
            card=escalation_service.build_escalation_card(final, customer_text),
            priority=final.get("priority"),
            severity=final.get("severity"),
            reason=final.get("escalation_reason"),
        )
    # Pipeline luôn trả status; phòng hờ thiếu → REPLIED (khách đang nhận một câu trả lời tự động).
    status_to = status_out or ConversationStatus.REPLIED
    return TurnPlan(
        "reply",
        status_to,
        allowed,
        reply,
        _outcome_of(status_out, final),
        current_intent=final.get("intent") if status_to == ConversationStatus.AWAITING_CUSTOMER else None,
    )


@dataclass(frozen=True)
class _PersistResult:
    applied: bool = False  # CAS thắng + commit xong
    discarded: bool = False  # CAS thua: status đã đổi dưới chân → KHÔNG lưu gì của lượt
    message_id: uuid.UUID | None = None
    status_now: str | None = None


async def _persist_turn(conv_id: uuid.UUID | None, plan: TurnPlan) -> _PersistResult:
    """MỘT transaction cho kết quả lượt: CAS status + tin AI + EscalationCard (GRAPH-02.1). Caller bọc `shield`.

    CAS thua (admin tiếp quản / đóng ca trong lúc pipeline chạy) → rollback, trả status HIỆN TẠI để báo khách (đọc lại
    lỗi → status không rõ, lượt VẪN bị bỏ). Chưa có ca / DB lỗi khi GHI → `_PersistResult()` (không applied, không
    discarded): caller thử lại MỘT lần; vẫn hỏng thì `reply` vẫn gửi (DB lỗi KHÔNG chặn chat — bất biến §1) nhưng
    `handoff`/`pending` thì KHÔNG — xem `_turn`.
    """
    if conv_id is None:
        return _PersistResult()
    lost_cas = False
    try:
        async with AsyncSessionLocal() as s:
            ok = await conversation_service.transition_status(
                s,
                conv_id,
                to=plan.status_to,
                allowed_from=plan.allowed_from,
                current_intent=plan.current_intent,
            )
            if not ok:
                lost_cas = True
                await s.rollback()
                state = await conversation_service.get_status_and_admin(s, conv_id)
                return _PersistResult(discarded=True, status_now=state[0] if state is not None else None)
            message_id = None
            if plan.ai_message is not None:
                message = await conversation_service.insert_message(
                    s, conv_id, sender=MessageSender.AI, content=plan.ai_message
                )
                message_id = message.id
            if plan.card is not None:
                await escalation_service.apply_escalation(
                    s,
                    conv_id,
                    card=plan.card,
                    priority=plan.priority,
                    severity=plan.severity,
                    reason=plan.reason,
                )
            await s.commit()
            return _PersistResult(applied=True, message_id=message_id)
    except Exception as exc:  # noqa: BLE001 — DB lỗi: caller thử lại / quyết frame, đừng để kẹt chat.
        if lost_cas:
            # CAS ĐÃ thua (status đổi dưới chân) mà đọc lại status lỗi → lượt VẪN bị bỏ: nhánh "ghi hỏng" (thử lại rồi
            # báo khách) chỉ dành cho GHI hỏng, không bao giờ cho CAS thua (GRAPH-02.2 — AI không nói chen vào ca người
            # đã nhận).
            log.warning("read status after lost CAS failed (bỏ lượt, conv=%s): %s", conv_id, exc)
            return _PersistResult(discarded=True)
        log.warning("persist turn failed (không lưu, conv=%s): %s", conv_id, exc)
        return _PersistResult()


async def _audit_turn(
    st: _CustomerSession,
    turn_id: uuid.UUID,
    customer_text: str,
    final: dict[str, Any] | None,
    reply: str,
    outcome: str,
    total_ms: int,
    *,
    message_id: uuid.UUID | None = None,
    delivery_detail: dict[str, Any] | None = None,
) -> None:
    """Ghi nhật ký lượt — gọi SAU khi frame đã trao cho socket và hub đã phát, nên không cộng vào độ trễ.

    `conversation_id` lấy từ `st.conv_id` (ca THẬT trong DB): WS gọi `run_pipeline` không truyền
    conversation_id nên `final["conversation_id"]` chỉ là thread_id ngẫu nhiên của checkpointer.
    `record_turn` tự nuốt lỗi (bất biến §1) → không cần try/except ở đây.

    **`asyncio.shield`**: task lượt không bị huỷ khi khách đóng tab, nhưng vẫn giữ shield (tắt server giữa
    lượt…): không shield thì chính lượt vừa xong mất dòng audit, và mọi KPI lệch âm thầm.
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
            message_id=message_id,
            delivery_detail=delivery_detail,
        )
    )


# ── Trạng thái 1 kết nối khách (P2) — ca hiện tại có thể ĐỔI khi ca cũ bị đóng ────
_SWITCH = object()  # sentinel: đánh thức _hub_listener để đọc queue của ca mới


class _CustomerSession:
    """Khách + ca đang mở + queue hub của ca đó. `conv_id/conv_key/queue` đổi khi mở ca mới.

    Tạo ca LƯỜI: mở chat mà chưa nhắn thì `conv_id` còn None (chưa có ca nào trong DB). `attached` báo cho
    `_hub_listener` biết lúc đã có ca để bắt đầu đọc queue. `closed`: socket đã đóng — lượt còn chạy nốt KHÔNG
    được đăng ký queue hub mới cho socket chết (không ai đọc → rò bộ nhớ).
    """

    def __init__(self, customer_id: uuid.UUID, display: str | None) -> None:
        self.customer_id = customer_id
        self.display = display
        self.conv_id: uuid.UUID | None = None
        self.conv_key: str | None = None
        self.queue: asyncio.Queue[dict[str, Any]] | None = None
        self.attached = asyncio.Event()  # set khi kết nối đã gắn vào MỘT ca (lần đầu)
        self.closed = False


def _switch_conversation(st: _CustomerSession, new_conv_id: uuid.UUID) -> None:
    """Chuyển kết nối sang ca mới: đăng ký hub queue mới, huỷ đăng ký cũ, đánh thức listener (sentinel)."""
    old_queue, old_key = st.queue, st.conv_key
    st.conv_id = new_conv_id
    st.conv_key = str(new_conv_id)
    if st.closed:
        st.queue = None  # socket đã đóng (queue cũ đã gỡ lúc đóng) → KHÔNG đăng ký queue mới
        return
    st.queue = hub.register(st.conv_key)
    st.attached.set()  # gỡ chốt cho _hub_listener (kết nối mở trước khi có ca — tạo lười)
    if old_key is not None and old_queue is not None:
        hub.unregister(old_key, old_queue)
        old_queue.put_nowait(_SWITCH)  # đánh thức _hub_listener để đọc st.queue mới


async def _find_or_open_case(st: _CustomerSession) -> tuple[str | None, str | None]:
    """Ca đang MỞ của khách (tab khác có thể vừa mở) — chưa có thì MỞ ca mới (AI-first) → `(status, intent)`.

    Gọi DƯỚI khoá khách nên hai tab không bao giờ đẻ hai ca (GRAPH-02.3). DB lỗi → giữ nguyên ca hiện tại (có thể
    CHƯA có ca) và báo status không rõ → lượt vẫn chạy nhưng không persist/hub; KHÔNG rớt WS.
    """
    try:
        async with AsyncSessionLocal() as s:
            conv = await conversation_service.get_active_conversation_for_customer(s, st.customer_id)
            if conv is None:
                conv = await conversation_service.open_case_for_customer(
                    s, st.customer_id, display=st.display
                )
    except Exception as exc:  # noqa: BLE001 — không mở được ca → chạy tiếp không persist.
        log.warning("open new case failed (chạy tiếp, không persist): %s", exc)
        return None, None
    if conv.id != st.conv_id:
        _switch_conversation(st, conv.id)
    for other in list(_live_sessions.get(st.customer_id, ())):
        if other is not st and other.conv_id != conv.id:
            _switch_conversation(other, conv.id)  # socket khác của khách chưa ở ca này — xem `_live_sessions`
    return conv.status, conv.current_intent


# Socket khách ĐANG SỐNG theo khách (in-process): lượt mở / chuyển sang ca đang mở thì gắn luôn các socket KHÁC
# của khách chưa ở ca đó — nối lúc chưa có ca (tạo lười) hoặc còn ở ca cũ đã đóng — để chúng nhận frame hub của ca:
# trả lời của lượt mà socket gốc đã chết, tin gõ ở tab khác (IDEM-XC.1, contract §4.1). Ghi danh lúc nối, gỡ lúc đóng.
_live_sessions: dict[uuid.UUID, set[_CustomerSession]] = {}


def _untrack(st: _CustomerSession) -> None:
    sessions = _live_sessions.get(st.customer_id)
    if sessions is not None:
        sessions.discard(st)
        if not sessions:
            del _live_sessions[st.customer_id]


async def _resolve_case(st: _CustomerSession) -> tuple[str | None, str | None]:
    """`(status, current_intent)` TRƯỚC lượt của ca sẽ nhận tin này. Gọi DƯỚI khoá khách."""
    if st.conv_id is not None:
        status, prior_intent = await _load_prior(st.conv_id)
        if status not in _CLOSED_STATUSES:
            return status, prior_intent
    # TẠO LƯỜI (chưa có ca) hoặc ca đã đóng (admin resolve / auto-resolve giữa các lượt) → ca đang mở do tab khác
    # vừa mở, hoặc ca MỚI (AI-first, agent chạy lại từ đầu).
    return await _find_or_open_case(st)


async def _load_customer_display(customer_id: uuid.UUID) -> str | None:
    """display cho customer_identifier (hiển thị admin) = display_name hoặc email. Guarded."""
    try:
        async with AsyncSessionLocal() as s:
            user = await s.get(User, customer_id)
            return (user.display_name or user.email) if user else None
    except Exception as exc:  # noqa: BLE001
        log.warning("load customer display failed (bỏ qua): %s", exc)
        return None


async def _notify_message(
    st: _CustomerSession,
    sender: str,
    content: str,
    message_id: uuid.UUID | None,
    client_msg_id: str | None = None,
) -> None:
    """Tin mới → admin đang mở ca + tab khác của khách (+ inbox). Chưa có ca → bỏ qua. `client_msg_id` (tin khách):
    socket mới của chính khách (mở lại sau khi rớt) khớp được bong bóng của mình (IDEM-XC.1)."""
    if st.conv_key is not None:
        await hub.notify_message(
            st.conv_key,
            sender=sender,
            content=content,
            message_id=message_id,
            client_msg_id=client_msg_id,
            exclude=st.queue,
        )


# ── Một lượt khách (task riêng, tuần tự theo khách) ──────────────────────────
async def _run_turn(
    websocket: WebSocket,
    st: _CustomerSession,
    msg: str,
    client_msg_id: str | None,
    received: float,
    lock: asyncio.Lock,
) -> None:
    """Task của MỘT tin khách — chạy DƯỚI khoá của khách (tuần tự mọi tab, đúng thứ tự tới). Không bao giờ ném."""
    try:
        async with lock:
            await _turn(websocket, st, msg, client_msg_id, received)
    except Exception as exc:  # noqa: BLE001 — lượt hỏng KHÔNG được làm sập task / kết nối.
        log.warning("customer turn failed (conv=%s): %s", st.conv_id, exc)


async def _turn(
    websocket: WebSocket, st: _CustomerSession, msg: str, client_msg_id: str | None, received: float
) -> None:
    started = time.perf_counter()  # đã có khoá (hết xếp hàng sau lượt trước của khách)
    for _attempt in range(2):
        status, prior_intent = await _resolve_case(st)
        run_ai = should_run_ai(status)
        # history = lượt TRƯỚC (nạp trước khi lưu tin hiện tại) — THEO CA. Chỉ lượt AI mới cần.
        history = await _load_history(st.conv_id) if run_ai else []
        customer_message_id, saved = await _persist_customer_message(st.conv_id, msg, client_msg_id)
        if saved != "closed":
            break
        # Ca vừa bị đóng dưới chân (giữa lúc đọc status và lúc lưu tin): tin KHÔNG vào ca đã đóng — vòng sau
        # `_resolve_case` thấy ca đóng → ca đang mở / ca MỚI (PRD §15). Đóng lần hai liền (gần như không thể) → chạy
        # tiếp như DB lỗi (không persist).
    if client_msg_id is not None and saved in ("unsaved", "closed"):
        # Tin khách KHÔNG nằm trong DB (DB lỗi / chưa có ca / ca bị đóng hai lần liền) → quên id đã ghi nhận lúc nhận:
        # FE nối lại sẽ gửi lại tin chưa thấy trong /me/thread, bản đó phải được XỬ LÝ chứ không bị ack duplicate rồi
        # mất hẳn (IDEM-XC.1). Lượt này vẫn chạy tiếp như cũ (DB lỗi KHÔNG chặn chat).
        _forget(st.customer_id, client_msg_id)
    if saved == "duplicate":
        # Tin gửi lại đã có trong DB (registry in-process không còn nhớ — vd tiến trình vừa khởi động lại):
        # KHÔNG chạy lại pipeline; báo client đây là bản trùng.
        await _send(
            websocket, {"type": "ack", "client_msg_id": client_msg_id, "message_id": None, "duplicate": True}
        )
        return
    t_fan0 = time.perf_counter()
    # Admin đang mở ca (và tab khác của khách) thấy câu hỏi NGAY — trước cả pipeline.
    await _notify_message(st, MessageSender.CUSTOMER, msg, customer_message_id, client_msg_id)
    t_fan1 = time.perf_counter()
    if not run_ai:
        return  # STATUS-GATE (08c): đang có người xử lý → AI KHÔNG chạy; tin đã tới admin qua hub.

    # `turn_id` sinh Ở ĐÂY (không trong pipeline): lượt pipeline NÉM LỖI vẫn ghi audit được.
    turn_id = uuid.uuid4()
    # Ngữ cảnh lượt cho Langfuse (P3) — đặt TRONG task lượt (contextvar riêng của task). No-op nếu chưa cấu hình.
    tracing.set_turn(str(turn_id), str(st.conv_id) if st.conv_id else None)
    await _send(websocket, {"type": "typing"})
    t_pipeline = time.perf_counter()
    status_out, final, reply = await _run_pipeline_safe(
        msg, history, turn_id, st.customer_id, status, prior_intent
    )
    t_decide = time.perf_counter()
    # Gate động P3: auto_reply không "gửi thẳng" → GIỮ nháp (PENDING_APPROVAL), KHÔNG gửi thẳng cho khách.
    held = final is not None and await gate_holds(status_out, final.get("intent"))
    plan = plan_delivery(
        prior_status=status, status_out=status_out, final=final, reply=reply, customer_text=msg, held=held
    )
    # Ghi TRƯỚC, báo khách SAU: khách không bao giờ được hứa "đã chuyển nhân viên" cho một ca vắng mặt trong hàng
    # đợi admin (GRAPH-02.1). Shield: không gì cắt ngang được bước ghi này.
    result = await asyncio.shield(_persist_turn(st.conv_id, plan))
    if not (result.applied or result.discarded):
        # Ghi hỏng (DB lỗi / chưa có ca): thử lại MỘT lần trên session MỚI (pool_pre_ping lấy kết nối mới sau khi Neon
        # rớt kết nối).
        result = await asyncio.shield(_persist_turn(st.conv_id, plan))
    # Vẫn chưa commit mà kết cục là `handoff`/`pending` (kể cả [error]) → KHÔNG gửi hai frame đó: chúng hứa một trạng
    # thái (ca trong hàng đợi admin / nháp chờ duyệt) không có thật. Khách nhận `FALLBACK_REPLY` — không hứa gì.
    # `reply` thường vẫn gửi như cũ (DB lỗi KHÔNG chặn chat).
    persist_failed = plan.frame != "reply" and not (result.applied or result.discarded)
    delivered = FALLBACK_REPLY if persist_failed else plan.ai_message
    t_send = time.perf_counter()
    if result.discarded:
        # Admin tiếp quản / đóng ca trong lúc pipeline chạy → AI KHÔNG nói chen; báo status hiện tại (FE gỡ typing).
        # Khách KHÔNG nhận id tài khoản nhân viên (`sub` của token admin) — `assigned_admin_id` luôn null.
        await _send(websocket, {"type": "status", "status": _sid(result.status_now), "assigned_admin_id": None})
    elif persist_failed:
        log.error("persist turn failed twice (conv=%s) → %s thay bằng câu không hứa hẹn", st.conv_id, plan.frame)
        await _send(websocket, {"type": "reply", "content": FALLBACK_REPLY, "message_id": None})
    elif plan.frame == "pending":
        await _send(websocket, {"type": "pending"})  # gỡ typing ở FE (KHÔNG gửi nội dung — sole-egress)
    else:
        await _send(
            websocket,
            {"type": plan.frame, "content": plan.ai_message, "message_id": _sid(result.message_id)},
        )
    t_sent = time.perf_counter()
    # Độ trễ PHÍA SERVER: từ lúc đọc được tin tới lúc frame được trao cho socket (không gồm mạng / render client).
    total_ms = _ms(received, t_sent)

    # Sau khi báo khách (không tính vào total_ms): phát cho admin đang theo dõi + tab khác của khách.
    t_fan2 = time.perf_counter()
    if not result.discarded:
        if delivered is not None:
            await _notify_message(st, MessageSender.AI, delivered, result.message_id)
        if result.applied and plan.status_to != status and st.conv_key is not None:
            await hub.notify_status(st.conv_key, status=plan.status_to, assigned_admin_id=None, exclude=st.queue)
    t_fan3 = time.perf_counter()

    # PERF-01.3: tách xếp hàng / I/O trước pipeline / pipeline / bước ghi / gửi socket; fan-out hub ghi riêng.
    delivery_detail: dict[str, Any] = {
        "timings": {
            "queue_ms": _ms(received, started),
            "pre_pipeline_ms": _ms(started, t_fan0) + _ms(t_fan1, t_pipeline),
            "pipeline_ms": _ms(t_pipeline, t_decide),
            "persist_ms": _ms(t_decide, t_send),
            "send_ms": _ms(t_send, t_sent),
            "fanout_ms": _ms(t_fan0, t_fan1) + _ms(t_fan2, t_fan3),
        }
    }
    outcome = plan.outcome
    if result.discarded:
        # Không lưu/gửi gì; ca đang trong tay người (admin tiếp quản / đóng) → kết cục ít gây hiểu lầm nhất là
        # QUEUED_FOR_HUMAN; `discarded` trong detail phân biệt với handoff thật của Agent 3.
        delivery_detail.update(discarded=True, reason="status_changed", status_now=_sid(result.status_now))
        outcome = TurnOutcome.QUEUED_FOR_HUMAN
    elif persist_failed:
        # Ca KHÔNG vào hàng đợi / nháp mất theo rollback → kết cục thật là lỗi kỹ thuật (khách nhận câu không hứa hẹn).
        delivery_detail["persist_failed"] = True
        outcome = TurnOutcome.ERROR
    await _audit_turn(
        st,
        turn_id,
        msg,
        final,
        reply,
        outcome,
        total_ms,
        message_id=customer_message_id,
        delivery_detail=delivery_detail,
    )


def _spawn_turn(
    websocket: WebSocket, st: _CustomerSession, msg: str, client_msg_id: str | None, received: float
) -> None:
    task = asyncio.create_task(
        _run_turn(websocket, st, msg, client_msg_id, received, _customer_lock(st.customer_id))
    )
    _turn_tasks.add(task)
    task.add_done_callback(_turn_tasks.discard)


# ── Hai task cho một kết nối khách ───────────────────────────────────────────
async def _customer_reader(websocket: WebSocket, st: _CustomerSession) -> None:
    """Đọc frame khách (giao thức v2). KHÔNG chạy lượt tại chỗ: tin → chống trùng → rate-limit → `ack` NGAY → xếp
    task lượt; `ping` → `pong` NGAY kể cả khi một lượt đang chạy (heartbeat phát hiện socket half-open — FE-01.4)."""
    try:
        while True:
            raw = await websocket.receive_text()
            received = time.perf_counter()
            frame = parse_client_frame(raw)
            if frame.kind == "ping":
                await _send(websocket, {"type": "pong"})
                continue
            cid = frame.client_msg_id
            # Tin GỬI LẠI (id đã nhận) → ack duplicate NGAY, KHÔNG tốn hạn mức (IDEM-XC.1): trả `rate_limited` ("KHÔNG
            # lưu") cho một tin ĐÃ lưu + đã trả lời sẽ khiến FE đánh dấu nhầm là gửi lỗi.
            if cid is not None and _already_accepted(st.customer_id, cid):
                await _send(websocket, {"type": "ack", "client_msg_id": cid, "message_id": None, "duplicate": True})
                continue
            # SEC-XC.2: vượt trần tin/cửa sổ của KHÁCH → báo lỗi, KHÔNG lưu, KHÔNG xử lý.
            if not _chat_limiter.hit(str(st.customer_id)):
                await _send(websocket, {"type": "error", "code": "rate_limited", "client_msg_id": cid})
                continue
            # Lớp A (slice 13): chuẩn hoá + cap NGAY tại biên — mọi đường phía sau (persist, hub,
            # pipeline, prompt LLM) chỉ thấy bản đã sạch. Cắt bớt, KHÔNG rớt kết nối.
            msg = sanitize_customer_message(frame.content)
            if cid is not None:
                _remember(st.customer_id, cid)
            await _send(websocket, {"type": "ack", "client_msg_id": cid, "message_id": None, "duplicate": False})
            _spawn_turn(websocket, st, msg, cid, received)
    except WebSocketDisconnect:
        log.info("customer WS disconnected (conv=%s)", st.conv_id)


async def _hub_listener(websocket: WebSocket, st: _CustomerSession) -> None:
    """Nhận payload từ hub của ca HIỆN TẠI (tin admin, trả lời AI, status…) → đẩy xuống socket khách.

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
        if payload.get("type") == "status" and payload.get("assigned_admin_id") is not None:
            # Khách KHÔNG nhận id tài khoản nhân viên đang giữ ca (`sub` của token admin — FE khách không dùng). Dict hub
            # dùng CHUNG cho mọi subscriber (socket admin cần trường này) → tạo bản mới, KHÔNG sửa tại chỗ.
            payload = {**payload, "assigned_admin_id": None}
        await websocket.send_json(payload)


async def _customer_ai_only(websocket: WebSocket, customer_id: uuid.UUID) -> None:
    """Degrade: KHÔNG tạo được conversation → chạy AI trực tiếp, KHÔNG persist/hub/status-gate.

    Vẫn nói giao thức v2 (ack/pong/rate limit/chống trùng in-process); lượt chạy tuần tự ngay trong reader như
    trước (nhánh hiếm — DB đang chết)."""
    try:
        while True:
            frame = parse_client_frame(await websocket.receive_text())
            if frame.kind == "ping":
                await _send(websocket, {"type": "pong"})
                continue
            cid = frame.client_msg_id
            if cid is not None and _already_accepted(customer_id, cid):  # gửi lại: KHÔNG tốn hạn mức (IDEM-XC.1)
                await _send(websocket, {"type": "ack", "client_msg_id": cid, "message_id": None, "duplicate": True})
                continue
            if not _chat_limiter.hit(str(customer_id)):
                await _send(websocket, {"type": "error", "code": "rate_limited", "client_msg_id": cid})
                continue
            msg = sanitize_customer_message(frame.content)  # Lớp A (slice 13)
            if cid is not None:
                # KHÔNG `_forget` như `_turn`: nhánh degrade trả lời nhưng KHÔNG BAO GIỜ lưu (cố ý) → nhớ id để tin gửi
                # lại trong tiến trình này không chạy pipeline lần hai.
                _remember(customer_id, cid)
            await _send(websocket, {"type": "ack", "client_msg_id": cid, "message_id": None, "duplicate": False})
            await websocket.send_json({"type": "typing"})
            # KHÔNG audit nhánh này: tới đây nghĩa là DB không dùng được, ghi audit chỉ tổ sinh log lỗi.
            # Vẫn truyền danh tính khách: DB hồi lại giữa chừng thì tra đơn scoped vẫn chạy đúng (AGENT-01.4).
            _, _, reply = await _run_pipeline_safe(msg, None, uuid.uuid4(), customer_id)
            await websocket.send_json({"type": "reply", "content": reply, "message_id": None})
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
    # Ghi danh TRƯỚC khi tìm ca: lượt của tab khác mở ca trong lúc đọc DB bên dưới vẫn gắn được socket này.
    _live_sessions.setdefault(customer_id, set()).add(st)
    try:
        # Mô hình hội thoại theo khách: chỉ TÌM ca đang mở. KHÔNG mở ca mới ở đây — ca sinh LƯỜI ở tin nhắn
        # ĐẦU TIÊN (task lượt), nếu không thì mỗi lần khách mở /chat rồi thoát lại đẻ một ca rỗng.
        try:
            async with AsyncSessionLocal() as s:
                conv = await conversation_service.get_active_conversation_for_customer(s, customer_id)
        except Exception as exc:  # noqa: BLE001 — DB lỗi → chat AI-only (KHÔNG persist/hub/status-gate).
            log.warning("resolve conversation failed (ai-only): %s", exc)
            _untrack(st)  # nhánh degrade không đọc hub → lượt của tab khác đừng gắn nó vào ca
            await _customer_ai_only(websocket, customer_id)
            return

        if conv is not None and conv.id != st.conv_id:
            _switch_conversation(st, conv.id)  # đăng ký hub cho ca đang mở (lịch sử nạp qua GET /me/thread)
        await websocket.send_json({"type": "system", "message": "connected"})
        log.info("customer WS connected (customer=%s conv=%s)", customer_id, st.conv_id)

        # Realtime 2 chiều: reader + hub-listener song song (queue theo ca hiện tại của st).
        reader = asyncio.create_task(_customer_reader(websocket, st))
        listener = asyncio.create_task(_hub_listener(websocket, st))
        _, pending = await asyncio.wait({reader, listener}, return_when=asyncio.FIRST_COMPLETED)
        for task in pending:  # một task xong (rớt kết nối) → huỷ task còn lại
            task.cancel()
        await asyncio.gather(*pending, return_exceptions=True)
    finally:
        # Task lượt đang chạy KHÔNG bị huỷ — nó chạy nốt + lưu; `closed` chặn nó đăng ký queue cho socket chết.
        st.closed = True
        _untrack(st)
        if st.conv_key is not None and st.queue is not None:
            hub.unregister(st.conv_key, st.queue)
        log.info("customer WS closed (conv=%s)", st.conv_id)
