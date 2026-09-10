"""Routes auth (slice 11 P1) — đăng ký (khách) / đăng nhập / danh tính hiện tại.

Response Generator vẫn là egress DUY NHẤT của luồng tự động — auth KHÔNG phát tin cho khách.
Đăng ký chỉ tạo khách (role=customer); admin tạo qua scripts/seed_admin.py.

Chống lạm dụng (audit v2, SEC-XC.2):
- bcrypt (~250ms CPU mỗi lần) chạy trong threadpool — gọi thẳng trong route async là chặn event loop của worker
  DUY NHẤT (mọi /ws/chat đứng hình theo).
- Email không tồn tại vẫn verify MỘT lần với hash giả → thời gian phản hồi không lộ email nào có tài khoản.
- Giới hạn tần suất in-process (`core/rate_limit`): login theo IP + theo email, register theo IP → 429 + Retry-After.
- Email có trần độ dài ở schema (`EMAIL_MAX_LENGTH`): email là KHOÁ của bộ đếm theo email → email cỡ MB bị 422
  trước khi vào route, không găm được vào RAM của bộ đếm.
- Đánh đổi CÓ CHỦ ĐÍCH của bộ đếm theo email: đếm MỌI lần thử (cả đúng mật khẩu) và chặn TRƯỚC khi verify → ai
  biết email (vd admin) gõ sai `login_rate_per_email` lần/cửa sổ là chủ tài khoản bị 429 tới hết cửa sổ, kể cả từ
  IP khác. Không bỏ được mà vẫn chặn dò mật khẩu phân tán lên MỘT tài khoản (chưa có CAPTCHA/2FA); khoá theo
  (email, IP) thì mất tác dụng đó. Bị lợi dụng thật → `login_rate_per_email=0` tắt qua env.
"""

from __future__ import annotations

import secrets
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from ...core.config import settings
from ...core.database import get_session
from ...core.rate_limit import SlidingWindowLimiter
from ...core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from ...models import User
from ...models.enums import UserRole
from ...schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenOut, UserOut
from ..deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

ACCESS_TOKEN_COOKIE = "access_token"
REFRESH_TOKEN_COOKIE = "refresh_token"


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    """Ghi access_token và refresh_token vào httpOnly cookies."""
    secure = settings.effective_cookie_secure
    samesite = settings.effective_cookie_samesite
    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE,
        value=access_token,
        httponly=True,
        secure=secure,
        samesite=samesite,
        domain=settings.cookie_domain,
        max_age=settings.jwt_access_expire_minutes * 60,
        path="/",
    )
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE,
        value=refresh_token,
        httponly=True,
        secure=secure,
        samesite=samesite,
        domain=settings.cookie_domain,
        max_age=settings.jwt_refresh_expire_days * 86400,
        path="/",
    )


def _clear_auth_cookies(response: Response) -> None:
    """Xoá access_token và refresh_token cookies."""
    secure = settings.effective_cookie_secure
    samesite = settings.effective_cookie_samesite
    response.delete_cookie(
        key=ACCESS_TOKEN_COOKIE,
        path="/",
        domain=settings.cookie_domain,
        secure=secure,
        httponly=True,
        samesite=samesite,
    )
    response.delete_cookie(
        key=REFRESH_TOKEN_COOKIE,
        path="/",
        domain=settings.cookie_domain,
        secure=secure,
        httponly=True,
        samesite=samesite,
    )

# Hash giả cho nhánh email không tồn tại: tốn đúng một lần bcrypt như email có thật. Mật khẩu ngẫu nhiên theo
# tiến trình — không ai khớp được, và nhánh đó luôn trả 401 bất kể kết quả.
_DUMMY_HASH = hash_password(secrets.token_urlsafe(16))

# Bộ đếm cửa sổ trượt (settings; 0 = tắt). In-process như hub — 1 worker. Test gọi `.reset()`.
_login_ip_limiter = SlidingWindowLimiter(settings.login_rate_per_ip, settings.rate_limit_window_seconds)
_login_email_limiter = SlidingWindowLimiter(settings.login_rate_per_email, settings.rate_limit_window_seconds)
_register_ip_limiter = SlidingWindowLimiter(settings.register_rate_per_ip, settings.rate_limit_window_seconds)


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _client_ip(request: Request) -> str:
    # Sau reverse proxy (deploy — slice 14) phải chạy uvicorn `--proxy-headers` (+ `--forwarded-allow-ips`),
    # nếu không mọi request mang IP của proxy → cả thiên hạ dùng CHUNG một bộ đếm.
    return request.client.host if request.client else "unknown"


def _check_rate(limiter: SlidingWindowLimiter, key: str) -> None:
    """Vượt trần → 429 + `Retry-After` (lần bị chặn KHÔNG được ghi vào bộ đếm)."""
    if not limiter.hit(key):
        retry_after = limiter.retry_after(key)
        raise HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS,
            f"Bạn thử quá nhiều lần, vui lòng thử lại sau {retry_after} giây.",
            headers={"Retry-After": str(retry_after)},
        )


def _token_response(user: User, response: Response | None = None) -> TokenOut:
    access_token = create_access_token(user_id=str(user.id), role=user.role)
    refresh_token = create_refresh_token(user_id=str(user.id))
    if response is not None:
        _set_auth_cookies(response, access_token, refresh_token)
    return TokenOut(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=user.id,
        role=user.role,
        display_name=user.display_name,
    )


@router.post("/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_session),
) -> TokenOut:
    """Tạo tài khoản KHÁCH + auto-login (trả JWT & ghi httpOnly cookie). Email trùng → 409. Quá nhiều lần theo IP → 429."""
    _check_rate(_register_ip_limiter, _client_ip(request))
    email = _normalize_email(payload.email)
    if "@" not in email:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "email không hợp lệ")
    existing = (await session.execute(select(User).where(User.email == email))).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "email đã tồn tại")
    user = User(
        email=email,
        password_hash=await run_in_threadpool(hash_password, payload.password),  # bcrypt ngoài event loop
        role=UserRole.CUSTOMER,
        display_name=(payload.display_name or "").strip() or None,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return _token_response(user, response)


@router.post("/login", response_model=TokenOut)
async def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_session),
) -> TokenOut:
    """Đăng nhập (admin hoặc khách) → JWT + role + display_name + ghi httpOnly cookies. Quá nhiều lần → 429."""
    email = _normalize_email(payload.email)
    _check_rate(_login_ip_limiter, _client_ip(request))
    _check_rate(_login_email_limiter, email)
    user = (await session.execute(select(User).where(User.email == email))).scalar_one_or_none()
    # Email không tồn tại vẫn chạy MỘT lần bcrypt (hash giả) → thời gian phản hồi không lộ email nào có thật.
    password_ok = await run_in_threadpool(
        verify_password, payload.password, user.password_hash if user is not None else _DUMMY_HASH
    )
    if user is None or not password_ok:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "email hoặc mật khẩu không đúng")
    return _token_response(user, response)


@router.post("/refresh", response_model=TokenOut)
async def refresh(
    request: Request,
    response: Response,
    payload: RefreshRequest | None = None,
    session: AsyncSession = Depends(get_session),
) -> TokenOut:
    """Làm mới access token (và refresh token) qua cookie refresh_token (hoặc body)."""
    token = request.cookies.get(REFRESH_TOKEN_COOKIE)
    if not token and payload and payload.refresh_token:
        token = payload.refresh_token
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "refresh token không tồn tại")

    decoded = decode_refresh_token(token)
    sub = (decoded or {}).get("sub")
    if not sub:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "refresh token không hợp lệ hoặc đã hết hạn")

    try:
        user_id = uuid.UUID(str(sub))
    except (ValueError, TypeError):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "refresh token không hợp lệ")

    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "người dùng không tồn tại")

    return _token_response(user, response)


@router.post("/logout")
async def logout(response: Response) -> dict[str, Any]:
    """Đăng xuất — xoá các httpOnly cookie access_token và refresh_token."""
    _clear_auth_cookies(response)
    return {"ok": True, "message": "logged out"}


@router.get("/me", response_model=UserOut)
async def me(user: User = Depends(get_current_user)) -> UserOut:
    return user

