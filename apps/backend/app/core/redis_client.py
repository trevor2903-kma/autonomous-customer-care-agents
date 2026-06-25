"""Redis client (Upstash) — session memory ngắn hạn + (TODO) pub/sub realtime.

PRD §10 (FR-ASYNC-7): phát realtime tới client/Admin bằng WebSocket + Redis pub/sub (event-driven),
KHÔNG worker polling (giữ free-tier Upstash). Scaffold mới chỉ dựng client + ping; pub/sub là TODO.
"""

from __future__ import annotations

import redis.asyncio as redis

from .config import settings

_client: redis.Redis | None = None


def get_redis() -> redis.Redis:
    global _client
    if _client is None:
        _client = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
    return _client


async def ping_redis() -> None:
    """Health check: PING."""
    await get_redis().ping()


async def close_redis() -> None:
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None
