"""GateConfig — cấu hình gate toàn cục (singleton id=1). Slice 11 P0 (gate động DB).

Van cho nhánh auto_reply (§4 plan): master `auto_reply_enabled` + auto_resolve.

KHÔNG có `retrieval_threshold` ở đây: ngưỡng truy hồi là giá trị ĐO (`scripts/measure_threshold.py`),
nguồn chân lý là `settings.retrieval_threshold` — pipeline chưa bao giờ đọc cột này, giữ lại chỉ tổ hiển
thị một con số khác với con số đang chạy.
"""

from __future__ import annotations

from sqlalchemy import Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class GateConfig(Base):
    __tablename__ = "gate_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    auto_reply_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    auto_resolve_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    auto_resolve_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
