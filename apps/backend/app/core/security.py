"""Bảo mật — hash/verify mật khẩu (bcrypt). Slice 11.

Dùng `bcrypt` trực tiếp (KHÔNG passlib): passlib 1.7.4 (2020, không còn bảo trì) hỏng với
bcrypt >=5 — probe backend gọi hashpw với secret >72 byte và bcrypt 5 raise thay vì cắt.
bcrypt chỉ dùng tối đa 72 byte đầu → cắt trước cho nhất quán giữa hash & verify.

P0: chỉ hash/verify mật khẩu (đủ cho script seed admin).
P1 (bổ sung sau): issue/verify JWT (sub=user_id, role, exp) dùng cho login + auth-over-WS.
"""

from __future__ import annotations

import bcrypt

_BCRYPT_MAX_BYTES = 72


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
