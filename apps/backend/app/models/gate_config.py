"""GateConfig — cấu hình gate toàn cục (singleton id=1). Slice 11 P0 (gate động DB).

Van cho nhánh auto_reply (§4 plan): master `auto_reply_enabled` + auto_resolve.
`retrieval_threshold` chỉ để FE hiển thị read-only slice này (Agent 2 VẪN đọc env — P3-b hoãn).
"""

from __future__ import annotations

from sqlalchemy import Boolean, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class GateConfig(Base):
    __tablename__ = "gate_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    auto_reply_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    auto_resolve_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    auto_resolve_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    retrieval_threshold: Mapped[float] = mapped_column(Float, nullable=False, default=0.35)
