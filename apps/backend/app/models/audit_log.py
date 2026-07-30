"""AuditLog — nhật ký kiểm toán mỗi bước agent + hành động Admin (PRD §20, NFR-4).

Đủ cột để truy vết: node, action, confidence, uncertainty_flags, escalation_reason, detail.
conversation_id/message_id để indexed UUID (không FK cứng) — audit phải bền dù hội thoại bị xóa.

**Đây là NGUỒN của tab Báo cáo** (Langfuse chỉ bổ trợ). Một LƯỢT khách = nhiều dòng chia sẻ `turn_id`:
`customer` (nhận tin) → 4 node pipeline → `delivery` (kết cục giao) — xem `AuditNode`/`TurnOutcome`.

Ý nghĩa `duration_ms` KHÁC nhau theo dòng, đừng cộng lẫn:
- dòng node (intent/knowledge/decision/response) = thời gian chạy CỦA NODE đó;
- dòng `delivery` = **end-to-end của cả lượt**, đo từ lúc nhận tin tới lúc khách NHẬN phản hồi → đây
  mới là con số cho NFR-1 (≤ 5s), KHÔNG phải tổng các node (tổng node bỏ sót I/O ngoài pipeline).
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Float, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, UUIDMixin


class AuditLog(UUIDMixin, Base):
    __tablename__ = "audit_log"

    conversation_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True), index=True, nullable=True
    )
    message_id: Mapped[uuid.UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    # Khoá GOM MỘT LƯỢT: mọi dòng của cùng lượt khách chia sẻ 1 giá trị (UI hiển thị ngắn `trc_…`).
    # Không gom được thì không nối được dòng `intent` với dòng `decision` của CÙNG lượt → không tính
    # được "%auto theo intent", và drill-down 4 agent cũng không dựng lại được.
    turn_id: Mapped[uuid.UUID | None] = mapped_column(PGUUID(as_uuid=True), index=True, nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)  # xem docstring module
    node: Mapped[str | None] = mapped_column(String(32), nullable=True)  # AuditNode
    action: Mapped[str | None] = mapped_column(String(64), nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    uncertainty_flags: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    escalation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    detail: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    # index: MỌI truy vấn của tab Báo cáo lọc theo khoảng thời gian (hôm nay/7 ngày) → thiếu index là full-scan.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True, nullable=False
    )
