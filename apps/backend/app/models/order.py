"""Order — đơn hàng của khách (dữ liệu mock, nạp bằng `scripts/seed_orders.py`).

Slice này CHỈ TRA CỨU: Agent 2 tra đơn theo mã → Agent 4 báo trạng thái grounded. KHÔNG huỷ/hoàn/đổi đơn
(thao tác thật = sau).

`order_code` là mã khách đọc cho shop — **chỉ chữ số**, khớp tầng trích entity đã chuẩn hoá quanh
`order_id` dạng số (`_entities._ORDER_ID_RE` bắt `\\d{3,}`; prompt Agent 1 dặn "order_id chỉ chữ số").
Mã chữ-số-lẫn-chữ sẽ KHÔNG trích được khi không có LLM → mất bất biến "order_id không bao giờ mất".

Mốc thời gian tách riêng theo trạng thái (`shipped_at`/`delivered_at`/`cancelled_at`) thay vì một cột
chung: đơn `delivered` phải nói được NGÀY GIAO THẬT, không phải ngày *dự kiến* (`estimated_delivery`) —
nói nhầm hai cái đó với khách là sai sự thật.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, UUIDMixin


class Order(UUIDMixin, Base):
    __tablename__ = "order"

    # Mã đơn khách đọc cho shop (UNIQUE toàn hệ thống) — chỉ chữ số.
    order_code: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    # CHỦ đơn — khoá của tra cứu SCOPED: đơn chỉ trả về cho đúng khách đang đăng nhập.
    customer_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(16), nullable=False)  # OrderStatus
    items_summary: Mapped[str] = mapped_column(String(255), nullable=False)
    region: Mapped[str] = mapped_column(String(64), nullable=False)

    ordered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    shipped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    estimated_delivery: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    tracking_code: Mapped[str | None] = mapped_column(String(64), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
