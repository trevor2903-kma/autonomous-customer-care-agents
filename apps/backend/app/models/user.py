"""User — tài khoản admin + khách (RBAC theo `role`). Slice 11 (auth).

`role` lưu dạng String (khớp pattern String+StrEnum của repo, tránh Postgres ENUM type) —
giá trị từ `enums.UserRole`. `email` UNIQUE (định danh đăng nhập; chuẩn hoá lowercase ở tầng auth).
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, UUIDMixin


class User(UUIDMixin, Base):
    __tablename__ = "user"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(16), nullable=False)  # admin | customer (UserRole)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
