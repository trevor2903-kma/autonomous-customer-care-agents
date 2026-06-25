"""Service hội thoại — CRUD tối thiểu (scaffold).

KHÔNG chạy pipeline ở đây (Phase 4/5 + PRD §8). Lưu ý CLAUDE.md: phản hồi tới khách CHỈ phát từ
Response Generator — service này KHÔNG tự sinh tin nhắn AI.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

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
) -> Message:
    # Append qua relationship: vừa set FK vừa cập nhật collection trong bộ nhớ (back_populates),
    # nhờ vậy object trả về phản ánh đúng số tin nhắn ngay sau commit.
    msg = Message(sender=sender, content=content, intent=intent, confidence=confidence)
    conversation.messages.append(msg)
    conversation.last_message_at = datetime.now(timezone.utc)
    return msg


async def create_conversation(
    session: AsyncSession,
    *,
    customer_identifier: str | None = None,
    first_message: str | None = None,
) -> Conversation:
    conversation = Conversation(
        customer_identifier=customer_identifier,
        status=ConversationStatus.NEW,
    )
    session.add(conversation)
    if first_message:
        _append_message(conversation, sender=MessageSender.CUSTOMER, content=first_message)
    await session.commit()
    # Đọc lại (populate_existing) để trả về trạng thái chuẩn từ DB sau commit.
    return await get_conversation(session, conversation.id)


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
    await session.commit()
    return await get_conversation(session, conversation_id)


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


async def list_conversations(session: AsyncSession, *, limit: int = 50) -> list[Conversation]:
    stmt = (
        select(Conversation)
        .order_by(Conversation.created_at.desc())
        .limit(limit)
        .options(selectinload(Conversation.messages))
    )
    return list((await session.execute(stmt)).scalars().all())
