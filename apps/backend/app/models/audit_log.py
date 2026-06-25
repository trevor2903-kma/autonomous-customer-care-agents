"""AuditLog — nhật ký kiểm toán mỗi bước agent + hành động Admin (PRD §20, NFR-4).

Đủ cột để truy vết: node, action, confidence, uncertainty_flags, escalation_reason, detail.
conversation_id/message_id để indexed UUID (không FK cứng) — audit phải bền dù hội thoại bị xóa.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Float, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, UUIDMixin


class AuditLog(UUIDMixin, Base):
    __tablename__ = "audit_log"

    conversation_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True), index=True, nullable=True
    )
    message_id: Mapped[uuid.UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    node: Mapped[str | None] = mapped_column(String(32), nullable=True)  # intent|knowledge|decision|response|human_handoff
    action: Mapped[str | None] = mapped_column(String(64), nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    uncertainty_flags: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    escalation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    detail: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
