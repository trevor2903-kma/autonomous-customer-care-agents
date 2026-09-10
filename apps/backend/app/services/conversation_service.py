"""Service hội thoại — CRUD conversation + message (persistence, PRD §12).

KHÔNG chạy pipeline ở đây (PRD §8 — pipeline là việc của graph). Lưu ý CLAUDE.md: phản hồi tới khách CHỈ phát
từ Response Generator — service này KHÔNG tự sinh tin nhắn AI.

Ghi status CHỈ qua `transition_status` (audit v2, GRAPH-02.2 / FE-03): UPDATE có điều kiện — compare-and-set cùng
pattern `auto_resolve` — trả True khi đúng 1 dòng đổi. `transition_status` và `insert_message` KHÔNG commit: caller
gộp nhiều ghi (status + tin + card + audit) vào MỘT transaction rồi tự commit.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterable
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import and_, func, not_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import Update

from ..models.conversation import Conversation
from ..models.enums import ConversationStatus, MessageSender
from ..models.message import Message


def _append_message(
    conversation: Conversation,
    *,
    sender: str,
    content: str,
    intent: str | None = None,
    confidence: float | None = None,
    bump_activity: bool = True,
) -> Message:
    # Append qua relationship: vừa set FK vừa cập nhật collection trong bộ nhớ (back_populates),
    # nhờ vậy object trả về phản ánh đúng số tin nhắn ngay sau commit.
    msg = Message(sender=sender, content=content, intent=intent, confidence=confidence)
    conversation.messages.append(msg)
    # Tin hệ thống auto-resolve (nhắc/đóng) KHÔNG được reset đồng hồ im-lặng của KHÁCH (bump_activity=False).
    if bump_activity:
        conversation.last_message_at = datetime.now(timezone.utc)
    return msg


async def add_message(
    session: AsyncSession,
    conversation_id: uuid.UUID,
    *,
    content: str,
    sender: str = MessageSender.CUSTOMER,
) -> Conversation | None:
    conversation = await get_conversation(session, conversation_id)  # selectinload messages
    if conversation is None:
        return None
    _append_message(conversation, sender=sender, content=content)
    # Khách nhắn lại → thoát vòng auto-resolve (09c): xoá mốc đã-nhắc.
    if sender == MessageSender.CUSTOMER:
        conversation.auto_resolve_reminded_at = None
    await session.commit()
    return await get_conversation(session, conversation_id)


async def send_auto_message(
    session: AsyncSession, conversation_id: uuid.UUID, *, content: str
) -> Conversation | None:
    """Persist tin hệ thống auto-resolve (sender=ai) KHÔNG bump last_message_at (09c).

    Đồng hồ im-lặng của khách phải giữ nguyên để grace/đóng đo đúng. Broadcast hub do call-site lo."""
    conversation = await get_conversation(session, conversation_id)
    if conversation is None:
        return None
    _append_message(conversation, sender=MessageSender.AI, content=content, bump_activity=False)
    await session.commit()
    return await get_conversation(session, conversation_id)


async def set_status(
    session: AsyncSession,
    conversation_id: uuid.UUID,
    status: str,
    *,
    current_intent: str | None = None,
) -> Conversation | None:
    """Cập nhật `conversation.status` (theo final state của pipeline). Session NGẮN (Neon free).

    `current_intent` (tuỳ chọn): ghi kèm intent của lượt — dùng khi vào `AWAITING_CUSTOMER` để lượt resume
    khôi phục ĐÚNG intent gốc lúc khách chỉ gõ mã đơn trơ (follow-up 09b).
    """
    conversation = await get_conversation(session, conversation_id)
    if conversation is None:
        return None
    conversation.status = status
    if current_intent is not None:
        conversation.current_intent = current_intent
    await session.commit()
    return conversation


async def insert_message(
    session: AsyncSession,
    conversation_id: uuid.UUID,
    *,
    sender: str,
    content: str,
    client_msg_id: str | None = None,
    bump_activity: bool = True,
) -> Message:
    """Chèn 1 tin — INSERT nhẹ: KHÔNG nạp hội thoại/lịch sử, KHÔNG commit (caller commit, OPS-01.3 / GRAPH-02.1).

    `bump_activity`: tin thật (khách/AI/admin) đẩy `last_message_at`; tin hệ thống auto-resolve (nhắc/đóng) thì KHÔNG
    — đồng hồ im-lặng của KHÁCH phải giữ nguyên để grace/đóng đo đúng (09c). Tin KHÁCH còn xoá mốc đã-nhắc (thoát
    vòng auto-resolve). `client_msg_id` trùng trong cùng ca → IntegrityError ngay lúc flush (tin GỬI LẠI).
    """
    message = Message(
        conversation_id=conversation_id, sender=sender, content=content, client_msg_id=client_msg_id
    )
    session.add(message)
    await session.flush()  # lộ IntegrityError (trùng client_msg_id) TRƯỚC khi đụng tới hàng conversation
    values: dict[str, Any] = {}
    if bump_activity:
        values["last_message_at"] = datetime.now(timezone.utc)
    if sender == MessageSender.CUSTOMER:
        values["auto_resolve_reminded_at"] = None
    if values:
        await session.execute(
            update(Conversation)
            .where(Conversation.id == conversation_id)
            .values(**values)
            .execution_options(synchronize_session=False)
        )
    return message


def transition_stmt(
    conversation_id: uuid.UUID,
    *,
    to: str,
    allowed_from: Iterable[str],
    current_intent: str | None = None,
    assigned_admin_id: uuid.UUID | None = None,
    not_held_by_other_than: uuid.UUID | None = None,
) -> Update:
    """Câu UPDATE compare-and-set của `transition_status` (tách riêng để test hình dạng SQL offline)."""
    conditions = [Conversation.id == conversation_id, Conversation.status.in_(tuple(allowed_from))]
    if not_held_by_other_than is not None:
        # "Ca do admin KHÁC giữ": HUMAN_HANDLING + có người giữ + người đó không phải mình. HUMAN_HANDLING mà KHÔNG
        # có người giữ (dữ liệu cũ) không tính là bị giữ — nếu không ca đó kẹt vĩnh viễn, không ai nhận/đóng được.
        conditions.append(
            not_(
                and_(
                    Conversation.status == ConversationStatus.HUMAN_HANDLING,
                    Conversation.assigned_admin_id.is_not(None),
                    Conversation.assigned_admin_id != not_held_by_other_than,
                )
            )
        )
    values: dict[str, Any] = {"status": to}
    if current_intent is not None:
        values["current_intent"] = current_intent
    if assigned_admin_id is not None:
        values["assigned_admin_id"] = assigned_admin_id
    return (
        update(Conversation)
        .where(*conditions)
        .values(**values)
        .execution_options(synchronize_session=False)
    )


async def transition_status(
    session: AsyncSession,
    conversation_id: uuid.UUID,
    *,
    to: str,
    allowed_from: Iterable[str],
    current_intent: str | None = None,
    assigned_admin_id: uuid.UUID | None = None,
    not_held_by_other_than: uuid.UUID | None = None,
) -> bool:
    """Đổi status CÓ ĐIỀU KIỆN (compare-and-set): chỉ ghi khi status hiện tại ∈ `allowed_from` [và ca không do admin
    KHÁC giữ]. True ⇔ đúng 1 dòng đổi; False = trạng thái đã đổi dưới chân (admin tiếp quản / đóng ca / từ chối…)
    → caller KHÔNG được ghi tiếp gì của hành động đó. KHÔNG commit — ghép được vào transaction của caller.

    `current_intent` (tuỳ chọn): ghi kèm intent lượt khi vào AWAITING_CUSTOMER (resume clarify 09b).
    `assigned_admin_id` (tuỳ chọn): gán người giữ trong CÙNG câu UPDATE (takeover).
    """
    result = await session.execute(
        transition_stmt(
            conversation_id,
            to=to,
            allowed_from=allowed_from,
            current_intent=current_intent,
            assigned_admin_id=assigned_admin_id,
            not_held_by_other_than=not_held_by_other_than,
        )
    )
    return result.rowcount == 1


async def get_status_and_admin(
    session: AsyncSession, conversation_id: uuid.UUID
) -> tuple[str, uuid.UUID | None] | None:
    """`(status, assigned_admin_id)` đọc TƯƠI từ DB (không qua identity map, không load messages). None = không có ca."""
    row = (
        await session.execute(
            select(Conversation.status, Conversation.assigned_admin_id).where(
                Conversation.id == conversation_id
            )
        )
    ).first()
    return (row.status, row.assigned_admin_id) if row is not None else None


async def get_status_and_intent(
    session: AsyncSession, conversation_id: uuid.UUID
) -> tuple[str | None, str | None]:
    """`(status, current_intent)` — nhẹ (KHÔNG load messages). WS cần CẢ HAI cho lượt resume clarify:
    status cho status-gate + loop-guard, intent gốc để khôi phục khi khách gõ mã đơn trơ."""
    conv = await session.get(Conversation, conversation_id)
    return (conv.status, conv.current_intent) if conv else (None, None)


async def get_conversation(
    session: AsyncSession, conversation_id: uuid.UUID
) -> Conversation | None:
    stmt = (
        select(Conversation)
        .where(Conversation.id == conversation_id)
        .options(selectinload(Conversation.messages))
        # populate_existing: ghi đè trạng thái identity-map bằng dữ liệu mới từ DB (làm tươi collection
        # sau khi thêm tin nhắn trong cùng session).
        .execution_options(populate_existing=True)
    )
    return (await session.execute(stmt)).scalar_one_or_none()


async def get_recent_messages(
    session: AsyncSession, conversation_id: uuid.UUID, limit: int
) -> list[dict[str, str]]:
    """N tin GẦN NHẤT của hội thoại (cap `limit` = history_window, NFR-10), trả theo thứ tự THỜI GIAN
    (cũ → mới) dạng `{sender, content}` cho bộ nhớ đa lượt. Session NGẮN."""
    stmt = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    rows = list((await session.execute(stmt)).scalars().all())
    rows.reverse()  # desc (mới→cũ) → thứ tự thời gian (cũ→mới) cho prompt
    return [{"sender": m.sender, "content": m.content} for m in rows]


# Ca "đã đóng" — khách nhắn tiếp sẽ MỞ ca mới (slice 11 P2).
_CLOSED_STATUSES = (ConversationStatus.RESOLVED, ConversationStatus.CLOSED)


async def get_active_conversation_for_customer(
    session: AsyncSession, customer_id: uuid.UUID
) -> Conversation | None:
    """Ca đang MỞ của khách (status ∉ {RESOLVED, CLOSED}), mới nhất trước. Nhẹ — KHÔNG load messages."""
    stmt = (
        select(Conversation)
        .where(
            Conversation.customer_id == customer_id,
            Conversation.status.not_in(_CLOSED_STATUSES),
        )
        .order_by(func.coalesce(Conversation.last_message_at, Conversation.created_at).desc())
        .limit(1)
    )
    return (await session.execute(stmt)).scalar_one_or_none()


async def open_case_for_customer(
    session: AsyncSession, customer_id: uuid.UUID, *, display: str | None = None
) -> Conversation:
    """Mở ca MỚI cho khách: status ACTIVE_AI, gắn customer_id + customer_identifier (display)."""
    conversation = Conversation(
        customer_id=customer_id,
        customer_identifier=display,
        status=ConversationStatus.ACTIVE_AI,
    )
    session.add(conversation)
    await session.commit()
    return conversation


async def get_customer_thread_messages(
    session: AsyncSession, customer_id: uuid.UUID
) -> list[Message]:
    """Mọi message của MỌI ca của khách, xếp theo created_at (cũ→mới) — mạch ghép xuyên ca (P2).

    CHỈ để hiển thị mạch liền cho khách. Bộ nhớ agent VẪN theo ca (`get_recent_messages`) — bất biến §1.
    """
    stmt = (
        select(Message)
        .join(Conversation, Message.conversation_id == Conversation.id)
        .where(Conversation.customer_id == customer_id)
        .order_by(Message.created_at.asc())
    )
    return list((await session.execute(stmt)).scalars().all())


async def list_conversations(
    session: AsyncSession, *, statuses: list[str] | None = None, limit: int = 50
) -> list[Conversation]:
    """Danh sách hội thoại (10a) — lọc theo NHÓM status (tùy chọn), hoạt động gần nhất lên đầu.

    coalesce(last_message_at, created_at): hội thoại chưa có tin vẫn xếp đúng chỗ (không rơi về cuối vì NULL).
    """
    stmt = (
        select(Conversation)
        .order_by(func.coalesce(Conversation.last_message_at, Conversation.created_at).desc())
        .limit(limit)
        .options(selectinload(Conversation.messages))
    )
    if statuses:
        stmt = stmt.where(Conversation.status.in_(statuses))
    return list((await session.execute(stmt)).scalars().all())
