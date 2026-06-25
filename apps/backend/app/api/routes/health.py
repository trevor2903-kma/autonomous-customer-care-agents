"""Health check — ping thật API + Neon + Upstash + Qdrant (plan Phase 2)."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import APIRouter

from ...core.config import settings
from ...core.database import ping_db
from ...core.qdrant_client import ping_qdrant
from ...core.redis_client import ping_redis

router = APIRouter(tags=["health"])

# Giới hạn thời gian mỗi probe để /api/health không treo khi 1 dịch vụ chậm/đang cold-start
# (vd Qdrant free-tier wake-up). Dịch vụ quá chậm -> báo not-ok thay vì treo cả endpoint.
_PROBE_TIMEOUT_SECONDS = 8.0


async def _probe(fn: Callable[[], Awaitable[Any]]) -> dict[str, Any]:
    try:
        result = await asyncio.wait_for(fn(), timeout=_PROBE_TIMEOUT_SECONDS)
        return {"ok": True, "detail": "ok" if result is None else result}
    except TimeoutError:
        return {"ok": False, "detail": f"timeout >{_PROBE_TIMEOUT_SECONDS:g}s"}
    except Exception as exc:  # noqa: BLE001 — health probe: gom lỗi để báo cáo, không raise
        return {"ok": False, "detail": f"{type(exc).__name__}: {exc}"}


@router.get("/health")
async def health() -> dict[str, Any]:
    services = {
        "database": await _probe(ping_db),
        "redis": await _probe(ping_redis),
        "qdrant": await _probe(ping_qdrant),
    }
    healthy = all(s["ok"] for s in services.values())
    return {
        "status": "ok" if healthy else "degraded",
        "api": "ok",
        "enable_llm": settings.enable_llm,
        "services": services,
    }
