"""Pydantic schemas — Auth (slice 11): register/login request + token/user response."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict, Field


class RegisterRequest(BaseModel):
    """Đăng ký khách (role=customer luôn được ép ở tầng route)."""

    email: str
    password: str = Field(min_length=6)
    display_name: str | None = None


class LoginRequest(BaseModel):
    email: str
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
