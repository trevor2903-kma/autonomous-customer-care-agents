"""Dependencies dùng chung cho route — DB session + auth JWT/RBAC (slice 11).

`get_current_user`: giải mã Bearer JWT → nạp User. Thiếu/sai token → 401.
`require_admin`: yêu cầu role=admin (dùng bảo vệ toàn bộ /api/admin/*). Không phải admin → 403.
"""

from __future__ import annotations

import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_session
from ..core.security import decode_access_token
from ..models import User
from ..models.enums import UserRole

__all__ = ["get_session", "get_current_user", "require_admin"]

_bearer = HTTPBearer(auto_error=False)
_UNAUTH_HEADERS = {"WWW-Authenticate": "Bearer"}


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    session: AsyncSession = Depends(get_session),
) -> User:
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "not authenticated", headers=_UNAUTH_HEADERS)
    payload = decode_access_token(credentials.credentials)
    sub = (payload or {}).get("sub")
    if not sub:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid token", headers=_UNAUTH_HEADERS)
    try:
        user_id = uuid.UUID(str(sub))
    except (ValueError, TypeError):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid token", headers=_UNAUTH_HEADERS)
    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "user not found", headers=_UNAUTH_HEADERS)
    return user


async def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.ADMIN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "admin only")
    return user
