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
    # Id do client sinh (audit v2) — FE khớp bong bóng lạc quan/gửi lại với bản đã lưu; None cho tin hệ thống/legacy.
    client_msg_id: str | None = None
    created_at: datetime


class ThreadOut(BaseModel):
    """Mạch liền của khách (P2): messages xuyên ca (cũ→mới) + ca đang mở (custStatus cho header)."""

    messages: list[ThreadMessageOut] = []
    active_conversation_id: uuid.UUID | None = None
    active_status: str | None = None
