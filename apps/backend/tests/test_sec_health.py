"""SEC-XC.4 — /api/health công khai KHÔNG trả nguyên văn lỗi hạ tầng; chi tiết chỉ vào log server. Offline."""

from __future__ import annotations

import asyncio
import json
import logging

import pytest

from app.api.routes import health as health_routes


async def _ok() -> None:
    return None


async def test_health_hides_exception_text_but_logs_it(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    async def _db_down() -> None:
        raise RuntimeError('password authentication failed for user "neondb_owner"')

    async def _redis_down() -> None:
        raise ConnectionError("Error 111 connecting to xxxxx.upstash.io:6379")

    async def _qdrant_ok() -> int:
        return 3  # số collection — cũng không cần lộ ra ngoài

    monkeypatch.setattr(health_routes, "ping_db", _db_down)
    monkeypatch.setattr(health_routes, "ping_redis", _redis_down)
    monkeypatch.setattr(health_routes, "ping_qdrant", _qdrant_ok)

    with caplog.at_level(logging.WARNING):
        body = await health_routes.health()

    assert body["status"] == "degraded"
    assert body["services"] == {"database": {"ok": False}, "redis": {"ok": False}, "qdrant": {"ok": True}}
    dumped = json.dumps(body)
    for leak in ("neondb_owner", "upstash.io", "RuntimeError", "ConnectionError", "detail"):
        assert leak not in dumped
    # ...nhưng người vận hành vẫn đọc được nguyên nhân trong log phía server.
    assert "neondb_owner" in caplog.text and "upstash.io" in caplog.text


async def test_health_timeout_is_not_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    async def _slow() -> None:
        await asyncio.sleep(1)

    monkeypatch.setattr(health_routes, "_PROBE_TIMEOUT_SECONDS", 0.01)
    monkeypatch.setattr(health_routes, "ping_db", _ok)
    monkeypatch.setattr(health_routes, "ping_redis", _ok)
    monkeypatch.setattr(health_routes, "ping_qdrant", _slow)
    body = await health_routes.health()
    assert body["status"] == "degraded"
    assert body["services"]["qdrant"] == {"ok": False}


async def test_health_all_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("ping_db", "ping_redis", "ping_qdrant"):
        monkeypatch.setattr(health_routes, name, _ok)
    body = await health_routes.health()
    assert body["status"] == "ok"
    assert all(s == {"ok": True} for s in body["services"].values())
