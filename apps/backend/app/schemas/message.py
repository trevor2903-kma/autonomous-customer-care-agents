"""Pydantic schemas — Message."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from ..models.enums import MessageSender


class MessageCreate(BaseModel):
    content: str
    sender: MessageSender = MessageSender.CUSTOMER


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    sender: str
    content: str
    intent: str | None = None
    confidence: float | None = None
    created_at: datetime
