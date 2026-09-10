"""Message — một tin nhắn (khách/AI/admin) trong hội thoại (PRD §20)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Index, String, Text, func, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, UUIDMixin

if TYPE_CHECKING:
    from .conversation import Conversation

# Tên partial unique index (conversation_id, client_msg_id) — vi phạm index này = tin GỬI LẠI (audit v2, IDEM-XC.1).
CLIENT_MSG_ID_INDEX = "uq_message_conversation_client_msg_id"


class Message(UUIDMixin, Base):
    __tablename__ = "message"
    __table_args__ = (
        Index(
            CLIENT_MSG_ID_INDEX,
            "conversation_id",
            "client_msg_id",
            unique=True,
            postgresql_where=text("client_msg_id IS NOT NULL"),
        ),
    )

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("conversation.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    sender: Mapped[str] = mapped_column(String(16), nullable=False)  # customer | ai | admin
    content: Mapped[str] = mapped_column(Text, nullable=False)
    intent: Mapped[str | None] = mapped_column(String(64), nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    # Id do CLIENT sinh (uuid v4) cho tin gửi đi, dùng lại NGUYÊN VĂN khi gửi lại. Duy nhất trong một ca khi có giá
    # trị (index trên) → tin gửi lại không chạy pipeline lần hai; FE dùng nó để khớp bong bóng lạc quan với DB.
    client_msg_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    conversation: Mapped["Conversation"] = relationship(back_populates="messages")
