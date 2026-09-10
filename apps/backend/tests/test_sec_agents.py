"""SEC-XC.1 — /api/agents/analyze chỉ cho admin + chặn độ dài `message`. Offline: session DB giả, pipeline giả."""

from __future__ import annotations

import uuid
from typing import Any

import httpx
import pytest
from fastapi import FastAPI

from app.api.routes import agents as agents_routes
from app.core.config import settings
from app.core.database import get_session
from app.core.security import create_access_token
from app.models import User
from app.models.enums import UserRole

URL = "/api/agents/analyze"


def _user(role: str) -> User:
    return User(id=uuid.uuid4(), email=f"{role}@shop.vn", password_hash="x", role=role)


ADMIN = _user(UserRole.ADMIN)
CUSTOMER = _user(UserRole.CUSTOMER)


def _bearer(user: User) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(user_id=str(user.id), role=user.role)}"}


class _FakeSession:
    """Chỉ đủ cho `deps.get_current_user` (session.get theo id)."""

    async def get(self, model: type, ident: uuid.UUID) -> User | None:
        return {ADMIN.id: ADMIN, CUSTOMER.id: CUSTOMER}.get(ident)


@pytest.fixture
def pipeline_calls(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Agent 1 + Agent 2 giả — ghi lại mỗi lần bị gọi (= mỗi lần đốt tiền LLM ở bản thật)."""
    calls: list[str] = []

    async def _classify(message: str) -> dict[str, Any]:
        calls.append(message)
        return {"intent": "shipping", "category": "pre_sale", "entities": {}, "confidence": 0.9,
                "uncertainty_flags": []}

    async def _retrieve(message: str, intent: str | None = None) -> dict[str, Any]:
        return {"retrieval_confidence": 0.8, "uncertainty_flags": [], "rag_contexts": []}

    monkeypatch.setattr(agents_routes, "classify_intent", _classify)
    monkeypatch.setattr(agents_routes, "retrieve_knowledge", _retrieve)
    return calls


@pytest.fixture
async def client():
    app = FastAPI()
    app.include_router(agents_routes.router, prefix="/api")

    async def _session():
        yield _FakeSession()

    app.dependency_overrides[get_session] = _session
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as c:
        yield c


async def test_analyze_without_token_is_401(client: httpx.AsyncClient, pipeline_calls: list[str]) -> None:
    r = await client.post(URL, json={"message": "phí ship bao nhiêu"})
    assert r.status_code == 401
    assert pipeline_calls == []  # chặn TRƯỚC khi gọi LLM


async def test_analyze_with_customer_token_is_403(client: httpx.AsyncClient, pipeline_calls: list[str]) -> None:
    r = await client.post(URL, json={"message": "phí ship bao nhiêu"}, headers=_bearer(CUSTOMER))
    assert r.status_code == 403
    assert pipeline_calls == []


async def test_analyze_admin_runs_agent1_and_agent2(client: httpx.AsyncClient, pipeline_calls: list[str]) -> None:
    r = await client.post(URL, json={"message": "phí ship bao nhiêu"}, headers=_bearer(ADMIN))
    assert r.status_code == 200
    assert r.json()["intent"] == "shipping"
    assert pipeline_calls == ["phí ship bao nhiêu"]


@pytest.mark.parametrize(
    "message", ["", "   ", "x" * (settings.max_message_chars + 1)], ids=["empty", "blank", "over-cap"]
)
async def test_analyze_rejects_empty_or_oversized_message(
    client: httpx.AsyncClient, pipeline_calls: list[str], message: str
) -> None:
    r = await client.post(URL, json={"message": message}, headers=_bearer(ADMIN))
    assert r.status_code == 422
    assert pipeline_calls == []  # không nhồi được cả megabyte vào prompt


async def test_analyze_accepts_message_exactly_at_cap(client: httpx.AsyncClient, pipeline_calls: list[str]) -> None:
    r = await client.post(URL, json={"message": "x" * settings.max_message_chars}, headers=_bearer(ADMIN))
    assert r.status_code == 200
