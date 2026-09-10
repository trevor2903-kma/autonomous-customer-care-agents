"""Health check — ping thật API + Neon + Upstash + Qdrant (plan Phase 2).

Endpoint CÔNG KHAI (không auth — load balancer / `make health`) nên chỉ trả ok/không từng dịch vụ + status tổng.
Lỗi thật (có thể chứa hostname, tên role Postgres, URL cluster) CHỈ ghi log phía server (audit v2, SEC-XC.4).
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import APIRouter

from ...core.config import settings
from ...core.database import ping_db
from ...core.logging import get_logger
from ...core.qdrant_client import ping_qdrant
from ...core.redis_client import ping_redis

log = get_logger("health")

router = APIRouter(tags=["health"])

# Giới hạn thời gian mỗi probe để /api/health không treo khi 1 dịch vụ chậm/đang cold-start
# (vd Qdrant free-tier wake-up). Dịch vụ quá chậm -> báo not-ok thay vì treo cả endpoint.
_PROBE_TIMEOUT_SECONDS = 8.0


async def _probe(name: str, fn: Callable[[], Awaitable[Any]]) -> dict[str, bool]:
    try:
        await asyncio.wait_for(fn(), timeout=_PROBE_TIMEOUT_SECONDS)
        return {"ok": True}
    except TimeoutError:
        log.warning("health probe %s: timeout >%gs", name, _PROBE_TIMEOUT_SECONDS)
        return {"ok": False}
    except Exception as exc:  # noqa: BLE001 — health probe: gom lỗi, không raise; chi tiết CHỈ vào log server
        log.warning("health probe %s failed: %s: %s", name, type(exc).__name__, exc)
        return {"ok": False}


@router.get("/health")
async def health() -> dict[str, Any]:
    services = {
        "database": await _probe("database", ping_db),
        "redis": await _probe("redis", ping_redis),
        "qdrant": await _probe("qdrant", ping_qdrant),
    }
    healthy = all(s["ok"] for s in services.values())
    return {
        "status": "ok" if healthy else "degraded",
        "api": "ok",
        "enable_llm": settings.enable_llm,
        "services": services,
    }
