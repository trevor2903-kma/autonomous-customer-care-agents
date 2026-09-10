"""Bảo mật — hash/verify mật khẩu (bcrypt) + issue/verify JWT (HS256). Slice 11.

Dùng `bcrypt` trực tiếp (KHÔNG passlib): passlib 1.7.4 (2020, không còn bảo trì) hỏng với
bcrypt >=5 — probe backend gọi hashpw với secret >72 byte và bcrypt 5 raise thay vì cắt.
bcrypt chỉ dùng tối đa 72 byte đầu → cắt trước cho nhất quán giữa hash & verify.

JWT (P1): payload `sub`=user_id, `role`, `iat`, `exp`; ký HS256 bằng `settings.jwt_secret`.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt

from .config import settings

_BCRYPT_MAX_BYTES = 72
JWT_ALGORITHM = "HS256"


def _to_bcrypt_bytes(password: str) -> bytes:
    # bcrypt chỉ xét 72 byte đầu; cắt ở tầng byte để hash & verify luôn khớp.
    return password.encode("utf-8")[:_BCRYPT_MAX_BYTES]


def hash_password(password: str) -> str:
    """Băm mật khẩu (bcrypt), trả chuỗi để lưu DB."""
    return bcrypt.hashpw(_to_bcrypt_bytes(password), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """So khớp mật khẩu thô với hash đã lưu."""
    try:
        return bcrypt.checkpw(_to_bcrypt_bytes(password), password_hash.encode("utf-8"))
    except ValueError:
        # hash không hợp lệ (dữ liệu hỏng) → coi như sai mật khẩu.
        return False


def create_access_token(*, user_id: str, role: str, expire_minutes: int | None = None) -> str:
    """Phát JWT đăng nhập (sub=user_id, role, type=access, exp theo `jwt_access_expire_minutes`)."""
    now = datetime.now(timezone.utc)
    exp_minutes = expire_minutes if expire_minutes is not None else settings.jwt_access_expire_minutes
    payload = {
        "sub": str(user_id),
        "role": role,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=exp_minutes)).timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=JWT_ALGORITHM)


def create_refresh_token(*, user_id: str, expire_days: int | None = None) -> str:
    """Phát JWT refresh token (sub=user_id, type=refresh, exp theo `jwt_refresh_expire_days`)."""
    now = datetime.now(timezone.utc)
    exp_days = expire_days if expire_days is not None else settings.jwt_refresh_expire_days
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(days=exp_days)).timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Giải mã + xác thực access token. Token sai/hết hạn hoặc sai type → None (không raise)."""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[JWT_ALGORITHM])
        if payload.get("type", "access") != "access":
            return None
        return payload
    except jwt.PyJWTError:
        return None


def decode_refresh_token(token: str) -> dict[str, Any] | None:
    """Giải mã + xác thực refresh token. Token sai/hết hạn hoặc sai type → None (không raise)."""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            return None
        return payload
    except jwt.PyJWTError:
        return None

