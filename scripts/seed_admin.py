"""Seed 1 admin user từ env (ADMIN_EMAIL, ADMIN_PASSWORD). Slice 11 P0.

KHÔNG hardcode secret — đọc env (CLAUDE.md). Idempotent: email đã tồn tại → cập nhật
password_hash/role/display_name (đổi mật khẩu = chạy lại). Optional: ADMIN_DISPLAY_NAME.

Chạy (cần .env cấu hình DATABASE_URL + đã `alembic upgrade head`):
    cd apps/backend && uv run python ../../scripts/seed_admin.py
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

_REPO_ROOT = Path(__file__).resolve().parents[1]
# Nạp .env gốc repo vào os.environ (như scripts/check_connections.py) — os.getenv KHÔNG tự đọc .env.
load_dotenv(_REPO_ROOT / ".env")

# Cho `import app...` chạy khi gọi script từ gốc repo (app cài editable trong apps/backend/.venv).
sys.path.insert(0, str(_REPO_ROOT / "apps" / "backend"))

from sqlalchemy import select  # noqa: E402

from app.core.database import AsyncSessionLocal, engine  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.models import User  # noqa: E402
from app.models.enums import UserRole  # noqa: E402


async def main() -> int:
    email = os.getenv("ADMIN_EMAIL", "").strip().lower()
    password = os.getenv("ADMIN_PASSWORD", "")
    display_name = os.getenv("ADMIN_DISPLAY_NAME", "Quản trị viên").strip()

    if not email or not password:
        print("FAIL: cần đặt ADMIN_EMAIL và ADMIN_PASSWORD trong .env (gốc repo).")
        return 1

    async with AsyncSessionLocal() as session:
        existing = (
            await session.execute(select(User).where(User.email == email))
        ).scalar_one_or_none()
        if existing is not None:
            existing.password_hash = hash_password(password)
            existing.role = UserRole.ADMIN
            existing.display_name = display_name
            action = "cập nhật"
        else:
            session.add(
                User(
                    email=email,
                    password_hash=hash_password(password),
                    role=UserRole.ADMIN,
                    display_name=display_name,
                )
            )
            action = "tạo mới"
        await session.commit()

    await engine.dispose()
    print(f"OK: admin '{email}' ({display_name}) — {action}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
