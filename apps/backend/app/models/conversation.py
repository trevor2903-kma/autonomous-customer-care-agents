"""Conversation — hội thoại (PRD §20). status theo tập canonical PRD §15.

Chừa sẵn chỗ CSKH/an toàn (PRD §5, §7): current_intent, entities, confidence, uncertainty_flags,
escalation_reason, assigned_admin_id — KHÔNG có logic thật ở scaffold.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, Float, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin
from .enums import ConversationStatus

if TYPE_CHECKING:
    from .message import Message


class Conversation(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "conversation"

    customer_identifier: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(
        String(32), default=ConversationStatus.NEW, nullable=False, index=True
    )
    current_intent: Mapped[str | None] = mapped_column(String(64), nullable=True)
    entities: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    uncertainty_flags: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    escalation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    assigned_admin_id: Mapped[uuid.UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    last_message_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )
