"""Route khách — mạch ghép hội thoại của khách đã đăng nhập (slice 11 P2).

Khách thấy MỘT mạch liền (mọi ca, cũ→mới); admin vẫn thấy các ca RIÊNG (routes/admin.py không đổi).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_session
from ...models import User
from ...schemas.conversation import ThreadMessageOut, ThreadOut
from ...services import conversation_service
from ..deps import get_current_user

router = APIRouter(prefix="/me", tags=["me"])


@router.get("/thread", response_model=ThreadOut)
async def get_my_thread(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ThreadOut:
    """Mạch liền của khách: mọi tin của mọi ca (cũ→mới) + ca đang mở (active_status = custStatus)."""
    messages = await conversation_service.get_customer_thread_messages(session, user.id)
    active = await conversation_service.get_active_conversation_for_customer(session, user.id)
    return ThreadOut(
        messages=[ThreadMessageOut.model_validate(m) for m in messages],
        active_conversation_id=active.id if active else None,
        active_status=active.status if active else None,
    )
