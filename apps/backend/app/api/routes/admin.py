"""Routes admin (HITL 08b) — hàng đợi escalation + xem hội thoại cho màn admin.

Admin identity tối giản (demo) — auth/RBAC thật = slice 11. Chỉ ĐỌC ở phase này; takeover/approve = 08c/08a.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_session
from ...models.enums import ConversationStatus
from ...schemas.admin import AdminConversationOut, EscalationOut
from ...services import conversation_service, escalation_service

router = APIRouter(prefix="/admin", tags=["admin"])

# Hàng đợi = ca đang chờ người: escalate (IN_HUMAN_QUEUE) + chờ duyệt nháp (PENDING_APPROVAL, slice 08a).
_QUEUE_STATUSES = [ConversationStatus.IN_HUMAN_QUEUE, ConversationStatus.PENDING_APPROVAL]


@router.get("/escalations", response_model=list[EscalationOut])
async def get_escalations(session: AsyncSession = Depends(get_session)) -> list[EscalationOut]:
    """Hàng đợi escalation, sắp priority cao → thấp rồi mới nhất (PRD §11/§17)."""
    convs = await escalation_service.list_escalations(session, _QUEUE_STATUSES)
    return [
        EscalationOut(
            conversation_id=c.id,
            customer_identifier=c.customer_identifier,
            status=c.status,
            priority=c.priority,
            severity=c.severity,
            escalation_reason=c.escalation_reason,
            escalation_card=c.escalation_card,
            last_message_at=c.last_message_at,
        )
        for c in convs
    ]


@router.get("/conversations/{conversation_id}", response_model=AdminConversationOut)
async def get_admin_conversation(
    conversation_id: uuid.UUID, session: AsyncSession = Depends(get_session)
) -> AdminConversationOut:
    """Hội thoại đầy đủ (messages + EscalationCard) cho màn admin tiếp quản/duyệt nháp."""
    conv = await conversation_service.get_conversation(session, conversation_id)
    if conv is None:
        raise HTTPException(status_code=404, detail="conversation not found")
    return conv
