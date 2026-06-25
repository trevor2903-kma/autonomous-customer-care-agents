"""Phase 1 smoke test — kiểm tra kết nối 3 dịch vụ managed (Neon · Upstash · Qdrant).

Chạy độc lập, KHÔNG phụ thuộc backend project (Phase 2):

    uv run --python 3.12 --with asyncpg --with redis --with qdrant-client \
           --with python-dotenv scripts/check_connections.py

hoặc:  make check-conn

Đây KHÔNG phải logic nghiệp vụ — chỉ xác minh `.env` nối được hạ tầng trước khi build backend.
"""

from __future__ import annotations

import asyncio
import os
import ssl
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

OK = "OK  "
FAIL = "FAIL"


async def check_postgres() -> tuple[bool, str]:
    import asyncpg

    url = os.getenv("DATABASE_URL", "")
    if not url:
        return False, "DATABASE_URL chưa đặt"
    # asyncpg dùng DSN `postgresql://` (bỏ '+asyncpg' của SQLAlchemy) và tham số ssl riêng;
    # bỏ mọi query (?sslmode=...) vì asyncpg không hiểu.
    dsn = url.replace("postgresql+asyncpg://", "postgresql://").split("?")[0]
    try:
        ctx = ssl.create_default_context()
        conn = await asyncpg.connect(dsn, ssl=ctx, timeout=15)
        try:
            ver = await conn.fetchval("SELECT version()")
        finally:
            await conn.close()
        return True, str(ver).split(" on ")[0]
    except Exception as e:  # noqa: BLE001 — smoke test: gom mọi lỗi để báo cáo
        return False, f"{type(e).__name__}: {e}"


async def check_redis() -> tuple[bool, str]:
    import redis.asyncio as aioredis

    url = os.getenv("REDIS_URL", "")
    if not url:
        return False, "REDIS_URL chưa đặt"
    try:
        client = aioredis.from_url(url, socket_connect_timeout=15)
        try:
            pong = await client.ping()
        finally:
            await client.aclose()
        return bool(pong), f"PING -> {pong}"
    except Exception as e:  # noqa: BLE001
        return False, f"{type(e).__name__}: {e}"


async def check_qdrant() -> tuple[bool, str]:
    from qdrant_client import QdrantClient

    url = os.getenv("QDRANT_URL", "")
    if not url:
        return False, "QDRANT_URL chưa đặt"
    api_key = os.getenv("QDRANT_API_KEY") or None

    def _ping() -> int:
        client = QdrantClient(url=url, api_key=api_key, timeout=15)
        try:
            return len(client.get_collections().collections)
        finally:
            client.close()

    try:
        n = await asyncio.to_thread(_ping)
        return True, f"{n} collection(s)"
    except Exception as e:  # noqa: BLE001
        return False, f"{type(e).__name__}: {e}"


async def main() -> int:
    checks = (
        ("Neon (Postgres)", check_postgres),
        ("Upstash (Redis)", check_redis),
        ("Qdrant Cloud", check_qdrant),
    )
    results = await asyncio.gather(*(fn() for _, fn in checks))

    print("=== Phase 1 — connection check ===")
    all_ok = True
    for (name, _), (ok, detail) in zip(checks, results):
        print(f"[{OK if ok else FAIL}] {name:<18} {detail}")
        all_ok = all_ok and ok
    print("===================================")
    if not all_ok:
        print(
            "Một số dịch vụ chưa nối được. Kiểm tra .env (xem checklist trong .env.example) "
            "hoặc chạy local: `make local-infra-up`."
        )
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
