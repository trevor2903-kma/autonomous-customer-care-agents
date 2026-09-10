"""Pydantic schemas — Message."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    sender: str
    content: str
    intent: str | None = None
    confidence: float | None = None
    # Id do client sinh (audit v2) — FE khớp bong bóng lạc quan với bản đã lưu; None cho tin hệ thống/legacy.
    client_msg_id: str | None = None
    created_at: datetime
