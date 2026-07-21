"""Routes auth (slice 11 P1) — đăng ký (khách) / đăng nhập / danh tính hiện tại.

Response Generator vẫn là egress DUY NHẤT của luồng tự động — auth KHÔNG phát tin cho khách.
Đăng ký chỉ tạo khách (role=customer); admin tạo qua scripts/seed_admin.py.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_session
from ...core.security import create_access_token, hash_password, verify_password
from ...models import User
from ...models.enums import UserRole
from ...schemas.auth import LoginRequest, RegisterRequest, TokenOut, UserOut
from ..deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _token_response(user: User) -> TokenOut:
    return TokenOut(
        access_token=create_access_token(user_id=str(user.id), role=user.role),
        user_id=user.id,
        role=user.role,
        display_name=user.display_name,
    )


@router.post("/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, session: AsyncSession = Depends(get_session)) -> TokenOut:
    """Tạo tài khoản KHÁCH + auto-login (trả JWT ngay). Email trùng → 409."""
    email = _normalize_email(payload.email)
    if "@" not in email:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "email không hợp lệ")
    existing = (await session.execute(select(User).where(User.email == email))).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "email đã tồn tại")
    user = User(
        email=email,
        password_hash=hash_password(payload.password),
        role=UserRole.CUSTOMER,
        display_name=(payload.display_name or "").strip() or None,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return _token_response(user)


@router.post("/login", response_model=TokenOut)
async def login(payload: LoginRequest, session: AsyncSession = Depends(get_session)) -> TokenOut:
    """Đăng nhập (admin hoặc khách) → JWT + role + display_name."""
    email = _normalize_email(payload.email)
    user = (await session.execute(select(User).where(User.email == email))).scalar_one_or_none()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "email hoặc mật khẩu không đúng")
    return _token_response(user)


@router.get("/me", response_model=UserOut)
async def me(user: User = Depends(get_current_user)) -> UserOut:
    return user
