"""GateIntentRule — luật per-intent cho gate auto_reply. Slice 11 P0.

`send_directly`: true = "Gửi thẳng" (REPLIED gửi ngay); false = "Duyệt nháp" (PENDING_APPROVAL).
Bản tổng quát hoá của `sensitive_intents` cũ. `sensitive` chỉ để hiển thị tag (không chi phối logic).
"""

from __future__ import annotations

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class GateIntentRule(Base):
    __tablename__ = "gate_intent_rule"

    intent: Mapped[str] = mapped_column(String(64), primary_key=True)
    label: Mapped[str] = mapped_column(String(64), nullable=False)
    sensitive: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    send_directly: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
