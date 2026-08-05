"""Service đơn hàng — tra cứu SCOPED theo khách đang đăng nhập.

**Quyền riêng tư (bất biến)**: "đơn 1234 của TÔI" là dữ liệu cá nhân. `lookup` trả đơn CHỈ KHI mã tồn tại
**VÀ** thuộc `customer_id`. Mã của người khác → `None`, GIỐNG HỆT mã không tồn tại: không lộ cả nội dung
lẫn SỰ TỒN TẠI của đơn người khác (nếu tách hai trường hợp, bot sẽ vô tình xác nhận "đơn này có thật").

Slice này CHỈ TRA CỨU — không huỷ/hoàn/đổi đơn.
"""

from __future__ import annotations

import uuid

from sqlalchemy import select

from ..core.database import AsyncSessionLocal
from ..models.enums import ORDER_STATUS_LABEL_VI, OrderStatus
from ..models.order import Order


def status_label_vi(status: str | None) -> str:
    """Nhãn tiếng Việt của trạng thái đơn; giá trị lạ (dữ liệu cũ) → trả nguyên trạng, KHÔNG ném."""
    try:
        return ORDER_STATUS_LABEL_VI[OrderStatus(status)]
    except ValueError:
        return str(status or "")


async def lookup(order_code: str | None, customer_id: uuid.UUID | None) -> Order | None:
    """Tra đơn theo mã, GIỚI HẠN trong đơn của `customer_id`. Thiếu mã / thiếu danh tính → None."""
    code = (order_code or "").strip()
    if not code or customer_id is None:
        return None
    async with AsyncSessionLocal() as session:
        return (
            await session.execute(
                select(Order).where(Order.order_code == code, Order.customer_id == customer_id)
            )
        ).scalar_one_or_none()


def to_context(order: Order) -> dict[str, str]:
    """Khối dữ liệu đơn cho Agent 4 (grounded). Chỉ đưa trường CÓ giá trị — trường vắng nghĩa là CHƯA CÓ
    mốc đó (đơn chưa gửi thì không có ngày gửi), KHÔNG phải 'không có' để Agent 4 suy diễn."""
    fields: list[tuple[str, str | None]] = [
        ("Mã đơn", order.order_code),
        ("Trạng thái", status_label_vi(order.status)),
        ("Sản phẩm", order.items_summary),
        ("Khu vực giao", order.region),
        ("Ngày đặt", _date(order.ordered_at)),
        ("Ngày bàn giao vận chuyển", _date(order.shipped_at)),
        ("Ngày giao thành công", _date(order.delivered_at)),
        ("Ngày huỷ", _date(order.cancelled_at)),
        ("Dự kiến giao", _date(order.estimated_delivery)),
        ("Mã vận đơn", order.tracking_code),
    ]
    return {label: value for label, value in fields if value}


def _date(value) -> str | None:  # noqa: ANN001 — datetime | None
    return value.strftime("%d/%m/%Y") if value else None
