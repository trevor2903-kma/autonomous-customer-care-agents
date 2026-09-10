"""Pydantic schemas — Auth (slice 11): register/login request + token/user response."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict, Field

# Trần độ dài email (RFC 5321: địa chỉ tối đa 254 ký tự) — hằng số giao thức, không phải ngưỡng tinh chỉnh.
# Bắt buộc từ khi login có bộ đếm THEO EMAIL (audit v2, SEC-XC.2): email là KHOÁ của bộ đếm, bộ đếm chỉ bỏ khoá
# khi đầy `max_keys` → không có trần thì mỗi IP găm được email cỡ MB vào RAM mãi. Quá trần → 422 trước khi vào
# route (không chạm bộ đếm/DB/bcrypt). Đăng ký cùng trần: không tạo được tài khoản mà login từ chối.
EMAIL_MAX_LENGTH = 254


class RegisterRequest(BaseModel):
    """Đăng ký khách (role=customer luôn được ép ở tầng route)."""

    email: str = Field(max_length=EMAIL_MAX_LENGTH)
    password: str = Field(min_length=6)
    display_name: str | None = None


class LoginRequest(BaseModel):
    email: str = Field(max_length=EMAIL_MAX_LENGTH)
    password: str


class TokenOut(BaseModel):
    """Kết quả đăng nhập/đăng ký — JWT + danh tính tối thiểu cho FE điều hướng."""

    access_token: str
    token_type: str = "bearer"
    user_id: uuid.UUID
    role: str
    display_name: str | None = None


class UserOut(BaseModel):
    """/auth/me — danh tính người dùng hiện tại."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    role: str
    display_name: str | None = None
