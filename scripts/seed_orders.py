"""Seed đơn hàng mock cho MỌI khách đã có trong DB (role=customer).

Mỗi khách ~6–8 đơn phủ ĐỦ 6 `OrderStatus`, dữ liệu thật-như: mã đơn duy nhất, mặt hàng/khu vực biến hoá,
**ngày & mã vận đơn nhất quán với trạng thái** (delivered có đủ đặt/gửi/giao + tracking; delivering có gửi +
tracking chưa giao; pending/processing chỉ mới đặt, tracking null; cancelled có ngày huỷ, không tracking).

KHÔNG cần env chỉ-định-khách — tự truy vấn từ DB. **Idempotent**: `order_code` đã tồn tại thì BỎ QUA, nên
chạy lại vô hại; thêm khách mới rồi chạy lại thì chỉ khách mới được seed.

Dữ liệu sinh DETERMINISTIC theo `customer.id` (`random.Random(uuid.int)`): chạy lại ra đúng bộ mã cũ →
idempotency mới thật sự đúng, và mã đơn dùng để verify không đổi giữa các lần chạy.

Chạy (cần .env cấu hình DATABASE_URL + đã `alembic upgrade head`):
    cd apps/backend && uv run python ../../scripts/seed_orders.py
"""

from __future__ import annotations

import asyncio
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv

_REPO_ROOT = Path(__file__).resolve().parents[1]
# Nạp .env gốc repo vào os.environ (như scripts/seed_admin.py) — settings đọc từ đó.
load_dotenv(_REPO_ROOT / ".env")

# Cho `import app...` chạy khi gọi script từ gốc repo (app cài editable trong apps/backend/.venv).
sys.path.insert(0, str(_REPO_ROOT / "apps" / "backend"))

from sqlalchemy import select  # noqa: E402

from app.core.database import AsyncSessionLocal, engine  # noqa: E402
from app.models import Order, User  # noqa: E402
from app.models.enums import OrderStatus, UserRole  # noqa: E402

REGIONS = [
    "Hà Nội",
    "TP. Hồ Chí Minh",
    "Đà Nẵng",
    "Hải Phòng",
    "Cần Thơ",
    "Nghệ An",
    "Bình Dương",
    "Lâm Đồng",
]

ITEMS = [
    "Áo khoác dù nam size L",
    "Quần jean nữ ống suông size 28",
    "Áo thun cotton basic size M",
    "Váy hoa nhí size S",
    "Áo sơ mi trắng công sở size XL",
    "Set đồ thể thao nữ size M",
    "Chân váy tennis size S",
    "Áo hoodie nỉ bông size L",
    "Quần short kaki nam size 32",
    "Áo len cổ lọ size M",
]

CARRIERS = ["GHN", "GHTK", "VNPost", "SPX"]

# Mã đơn CHỈ CHỮ SỐ (6 chữ số) — khớp tầng trích entity (`order_id` dạng số). Base suy từ UUID khách
# nên ổn định qua các lần chạy và không phụ thuộc thứ tự/số lượng khách.
_CODE_MIN = 100_000
_CODE_SPAN = 899_000


def _items_summary(rng: random.Random) -> str:
    picked = rng.sample(ITEMS, rng.randint(1, 2))
    return ", ".join(f"{name} x{rng.randint(1, 2)}" for name in picked)


def _tracking(rng: random.Random) -> str:
    return f"{rng.choice(CARRIERS)}{rng.randint(100_000_000, 999_999_999)}"


def _build_order(
    *, code: str, customer_id, status: OrderStatus, rng: random.Random, now: datetime
) -> Order:
    """Dựng 1 đơn với mốc thời gian + tracking NHẤT QUÁN với trạng thái (không có 'đã giao' mà thiếu ngày gửi)."""
    ordered_at = shipped_at = delivered_at = cancelled_at = estimated = None
    tracking = None

    if status is OrderStatus.PENDING:
        ordered_at = now - timedelta(hours=rng.randint(2, 20))
        estimated = ordered_at + timedelta(days=rng.randint(3, 5))
    elif status is OrderStatus.PROCESSING:
        ordered_at = now - timedelta(days=rng.randint(1, 2))
        estimated = ordered_at + timedelta(days=rng.randint(3, 5))
    elif status is OrderStatus.SHIPPED:
        ordered_at = now - timedelta(days=rng.randint(2, 4))
        shipped_at = ordered_at + timedelta(days=1)
        estimated = ordered_at + timedelta(days=rng.randint(4, 6))
        tracking = _tracking(rng)
    elif status is OrderStatus.DELIVERING:
        ordered_at = now - timedelta(days=rng.randint(3, 5))
        shipped_at = ordered_at + timedelta(days=1)
        estimated = now + timedelta(days=rng.randint(0, 1))
        tracking = _tracking(rng)
    elif status is OrderStatus.DELIVERED:
        ordered_at = now - timedelta(days=rng.randint(8, 25))
        shipped_at = ordered_at + timedelta(days=1)
        delivered_at = shipped_at + timedelta(days=rng.randint(1, 3))
        estimated = ordered_at + timedelta(days=4)
        tracking = _tracking(rng)
    else:  # CANCELLED — huỷ trước khi gửi: KHÔNG ngày gửi, KHÔNG mã vận đơn.
        ordered_at = now - timedelta(days=rng.randint(5, 15))
        cancelled_at = ordered_at + timedelta(hours=rng.randint(3, 48))

    return Order(
        order_code=code,
        customer_id=customer_id,
        status=status,
        items_summary=_items_summary(rng),
        region=rng.choice(REGIONS),
        ordered_at=ordered_at,
        shipped_at=shipped_at,
        delivered_at=delivered_at,
        cancelled_at=cancelled_at,
        estimated_delivery=estimated,
        tracking_code=tracking,
    )


async def main() -> int:
    now = datetime.now(timezone.utc)

    async with AsyncSessionLocal() as session:
        customers = list(
            (
                await session.execute(
                    select(User).where(User.role == UserRole.CUSTOMER).order_by(User.created_at)
                )
            ).scalars()
        )
        if not customers:
            print("FAIL: chưa có khách nào (role=customer) trong DB — đăng ký một tài khoản khách trước.")
            return 1

        existing_codes = set((await session.execute(select(Order.order_code))).scalars())

        created = skipped = 0
        for customer in customers:
            rng = random.Random(customer.id.int)
            # Phủ ĐỦ 6 trạng thái + 0–2 đơn lặp lại ngẫu nhiên → 6–8 đơn/khách.
            statuses = list(OrderStatus) + [
                rng.choice(list(OrderStatus)) for _ in range(rng.randint(0, 2))
            ]
            rng.shuffle(statuses)

            base = _CODE_MIN + (customer.id.int % _CODE_SPAN)
            lines: list[str] = []
            for i, status in enumerate(statuses):
                code = str(base + i)
                if code in existing_codes:  # idempotent: mã đã có → bỏ qua
                    skipped += 1
                    lines.append(f"{code}={status} (đã có)")
                    continue
                session.add(_build_order(code=code, customer_id=customer.id, status=status, rng=rng, now=now))
                existing_codes.add(code)
                created += 1
                lines.append(f"{code}={status}")

            print(f"  {customer.email}: {' · '.join(lines)}")

        await session.commit()

    await engine.dispose()
    print(f"\nOK: {len(customers)} khách — tạo mới {created} đơn, bỏ qua {skipped} đơn đã có.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
