"""Routes admin (HITL 08b) — hàng đợi escalation + xem hội thoại cho màn admin.

Admin identity tối giản (demo) — auth/RBAC thật = slice 11. Chỉ ĐỌC ở phase này; takeover/approve = 08c/08a.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_session
from ...models.enums import ConversationStatus, MessageSender
from ...schemas.admin import AdminConversationOut, ApproveRequest, EscalationOut
from ...services import conversation_service, escalation_service
from ..ws.hub import hub

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


@router.post("/conversations/{conversation_id}/resolve", response_model=AdminConversationOut)
async def resolve_conversation(
    conversation_id: uuid.UUID, session: AsyncSession = Depends(get_session)
) -> AdminConversationOut:
    """Đóng ca sau khi admin xử lý xong → status RESOLVED (08c)."""
    conv = await conversation_service.set_status(session, conversation_id, ConversationStatus.RESOLVED)
    if conv is None:
        raise HTTPException(status_code=404, detail="conversation not found")
    return await conversation_service.get_conversation(session, conversation_id)


@router.post("/conversations/{conversation_id}/approve", response_model=AdminConversationOut)
async def approve_draft(
    conversation_id: uuid.UUID,
    payload: ApproveRequest,
    session: AsyncSession = Depends(get_session),
) -> AdminConversationOut:
    """Duyệt nháp (08a): gửi nháp (đã duyệt/sửa) tới khách qua hub + lưu (sender=AI) + status REPLIED.
    Bỏ trống `content` → dùng `suggested_reply` trong EscalationCard."""
    conv = await conversation_service.get_conversation(session, conversation_id)
    if conv is None:
        raise HTTPException(status_code=404, detail="conversation not found")
    content = (payload.content or "").strip() or (conv.escalation_card or {}).get("suggested_reply") or ""
    if not content:
        raise HTTPException(status_code=400, detail="no draft to send")
    await conversation_service.add_message(
        session, conversation_id, content=content, sender=MessageSender.AI
    )
    await conversation_service.set_status(session, conversation_id, ConversationStatus.REPLIED)
    # Nháp đã duyệt → khách nhận realtime (hub). Egress này do ADMIN kích hoạt (duyệt) — vẫn là câu của shop/AI.
    await hub.publish(str(conversation_id), {"type": "message", "from": "ai", "content": content})
    return await conversation_service.get_conversation(session, conversation_id)


@router.post("/conversations/{conversation_id}/reject", response_model=AdminConversationOut)
async def reject_draft(
    conversation_id: uuid.UUID, session: AsyncSession = Depends(get_session)
) -> AdminConversationOut:
    """Từ chối nháp (08a) → IN_HUMAN_QUEUE (admin tự tiếp quản xử lý)."""
    conv = await conversation_service.set_status(
        session, conversation_id, ConversationStatus.IN_HUMAN_QUEUE
    )
    if conv is None:
        raise HTTPException(status_code=404, detail="conversation not found")
    return await conversation_service.get_conversation(session, conversation_id)
