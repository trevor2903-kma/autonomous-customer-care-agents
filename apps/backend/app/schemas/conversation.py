"""Pydantic schemas — Conversation."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from .message import MessageOut


class ConversationCreate(BaseModel):
    customer_identifier: str | None = None
    # Tin nhắn đầu tiên của khách (tùy chọn). Scaffold: chỉ lưu, CHƯA chạy pipeline.
    message: str | None = None


class ConversationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    customer_identifier: str | None = None
    status: str
    current_intent: str | None = None
    entities: dict[str, Any] = {}
    confidence: float | None = None
    uncertainty_flags: list[str] = []
    escalation_reason: str | None = None
    created_at: datetime
    updated_at: datetime
    last_message_at: datetime | None = None
    messages: list[MessageOut] = []


class ThreadMessageOut(BaseModel):
    """Một tin trong mạch ghép của khách — kèm conversation_id để FE nhận biết ranh giới ca (P2)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    conversation_id: uuid.UUID
    sender: str
    content: str
    created_at: datetime


class ThreadOut(BaseModel):
    """Mạch liền của khách (P2): messages xuyên ca (cũ→mới) + ca đang mở (custStatus cho header)."""

    messages: list[ThreadMessageOut] = []
    active_conversation_id: uuid.UUID | None = None
    active_status: str | None = None
