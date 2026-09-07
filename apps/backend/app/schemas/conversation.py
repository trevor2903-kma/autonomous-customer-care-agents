"""Pydantic schemas — Conversation."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


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
