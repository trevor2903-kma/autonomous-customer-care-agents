"""Pydantic schemas — Admin HITL (08b/08c): hàng đợi escalation + hội thoại cho màn admin."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from .message import MessageOut


class EscalationOut(BaseModel):
    """Một mục hàng đợi escalation (PRD §11/§17). `conversation_id` = id hội thoại để mở màn admin."""

    conversation_id: uuid.UUID
    customer_identifier: str | None = None
    status: str
    priority: str | None = None
    severity: str | None = None
    escalation_reason: str | None = None
    escalation_card: dict[str, Any] | None = None
    last_message_at: datetime | None = None


class ConversationListItem(BaseModel):
    """Một dòng trong danh sách hội thoại admin (10a). `preview` = nội dung tin cuối cùng."""

    id: uuid.UUID
    customer_identifier: str | None = None
    status: str
    current_intent: str | None = None
    last_message_at: datetime | None = None
    preview: str | None = None


class ApproveRequest(BaseModel):
    """Duyệt nháp (08a): `content` = nháp đã sửa (nếu admin chỉnh); bỏ trống → dùng suggested_reply trong card."""

    content: str | None = None


class AdminConversationOut(BaseModel):
    """Hội thoại đầy đủ cho màn admin — kèm EscalationCard + toàn bộ tin nhắn (customer/ai/admin)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    customer_identifier: str | None = None
    status: str
    priority: str | None = None
    severity: str | None = None
    escalation_reason: str | None = None
    escalation_card: dict[str, Any] | None = None
    assigned_admin_id: uuid.UUID | None = None
    created_at: datetime
    last_message_at: datetime | None = None
    messages: list[MessageOut] = []
