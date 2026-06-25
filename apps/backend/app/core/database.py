"""SQLAlchemy 2.0 async engine/session (Neon Postgres).

CLAUDE.md: Neon cần SSL qua connect_args={"ssl": True}; KHÔNG dùng '?sslmode=' (asyncpg không hiểu).
Async-first: engine/session/route đều async.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .config import settings

engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
    connect_args={"ssl": settings.database_ssl},
)

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency: cấp một AsyncSession theo request."""
    async with AsyncSessionLocal() as session:
        yield session


async def ping_db() -> None:
    """Health check: SELECT 1."""
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
