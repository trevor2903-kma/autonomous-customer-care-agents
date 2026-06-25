"""Routes hội thoại — tạo / liệt kê / xem + thêm tin nhắn khách (scaffold).

CHƯA chạy pipeline (PRD §8) — đó là Phase 4/5. Mọi phát ngôn tới khách sẽ CHỈ đến từ Response
Generator (PRD §7.4) khi wiring sau; route này KHÔNG tự sinh tin nhắn AI.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_session
from ...schemas.conversation import ConversationCreate, ConversationOut
from ...schemas.message import MessageCreate
from ...services import conversation_service as svc

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("", response_model=ConversationOut, status_code=201)
async def create_conversation(
    payload: ConversationCreate, session: AsyncSession = Depends(get_session)
) -> ConversationOut:
    conversation = await svc.create_conversation(
        session,
        customer_identifier=payload.customer_identifier,
        first_message=payload.message,
    )
    return conversation


@router.get("", response_model=list[ConversationOut])
async def list_conversations(
    session: AsyncSession = Depends(get_session),
) -> list[ConversationOut]:
    return await svc.list_conversations(session)


@router.get("/{conversation_id}", response_model=ConversationOut)
async def get_conversation(
    conversation_id: uuid.UUID, session: AsyncSession = Depends(get_session)
) -> ConversationOut:
    conversation = await svc.get_conversation(session, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="conversation not found")
    return conversation


@router.post("/{conversation_id}/messages", response_model=ConversationOut)
async def post_message(
    conversation_id: uuid.UUID,
    payload: MessageCreate,
    session: AsyncSession = Depends(get_session),
) -> ConversationOut:
    conversation = await svc.add_message(
        session, conversation_id, content=payload.content, sender=payload.sender
    )
    if conversation is None:
        raise HTTPException(status_code=404, detail="conversation not found")
    # TODO (Phase 5, PRD §8/§10): kích hoạt pipeline qua BackgroundTasks -> ghi audit_log ->
    #   phát realtime (Redis pub/sub). Phản hồi khách CHỈ từ Response Generator (PRD §7.4).
    return conversation
