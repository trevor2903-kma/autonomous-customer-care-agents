"""SEC-XC.2 (phần HTTP) — bcrypt ngoài event loop, hash giả chống dò email, rate limit login/register.

Offline: session DB giả qua `dependency_overrides`; bộ đếm được reset giữa các ca.
"""

from __future__ import annotations

import asyncio
import uuid
from typing import Any

import httpx
import pytest
from fastapi import FastAPI

from app.api.routes import auth as auth_routes
from app.core.config import settings
from app.core.database import get_session
from app.core.rate_limit import SlidingWindowLimiter
from app.core.security import hash_password
from app.models import User
from app.models.enums import UserRole

PASSWORD = "matkhau-dung"
EXISTING = User(
    id=uuid.uuid4(), email="khach@shop.vn", password_hash=hash_password(PASSWORD), role=UserRole.CUSTOMER
)


class _Result:
    def __init__(self, value: Any) -> None:
        self._value = value

    def scalar_one_or_none(self) -> Any:
        return self._value


class _FakeSession:
    """Đủ cho routes auth: tra user theo email (execute) + tạo user (add/commit/refresh)."""

    async def execute(self, stmt: Any) -> _Result:
        email = next(iter(stmt.compile().params.values()))  # select(User).where(User.email == email)
        return _Result(EXISTING if email == EXISTING.email else None)

    def add(self, user: User) -> None:
        return None

    async def commit(self) -> None:
        return None

    async def refresh(self, user: User) -> None:
        user.id = user.id or uuid.uuid4()


@pytest.fixture(autouse=True)
def _fresh_limiters():
    limiters = (auth_routes._login_ip_limiter, auth_routes._login_email_limiter, auth_routes._register_ip_limiter)
    for lim in limiters:
        lim.reset()
    yield
    for lim in limiters:
        lim.reset()


@pytest.fixture
async def client():
    app = FastAPI()
    app.include_router(auth_routes.router, prefix="/api")

    async def _session():
        yield _FakeSession()

    app.dependency_overrides[get_session] = _session
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as c:
        yield c


def _on_event_loop() -> bool:
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return False
    return True


async def _login(client: httpx.AsyncClient, email: str, password: str = "sai") -> httpx.Response:
    return await client.post("/api/auth/login", json={"email": email, "password": password})


# ── bcrypt ngoài event loop ──────────────────────────────────────────────────
async def test_login_ok_and_bcrypt_runs_off_the_event_loop(
    client: httpx.AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    seen: list[bool] = []
    real = auth_routes.verify_password

    def _spy(password: str, password_hash: str) -> bool:
        seen.append(_on_event_loop())
        return real(password, password_hash)

    monkeypatch.setattr(auth_routes, "verify_password", _spy)
    r = await _login(client, " Khach@Shop.VN ", PASSWORD)
    assert r.status_code == 200 and r.json()["role"] == "customer"
    assert seen == [False]  # chạy trong threadpool → không chặn event loop của worker duy nhất


async def test_register_hashes_off_the_event_loop(
    client: httpx.AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    seen: list[bool] = []

    def _spy(password: str) -> str:
        seen.append(_on_event_loop())
        return "hashed"

    monkeypatch.setattr(auth_routes, "hash_password", _spy)
    r = await client.post("/api/auth/register", json={"email": "moi@shop.vn", "password": "123456"})
    assert r.status_code == 201
    assert seen == [False]


# ── Chống dò email bằng thời gian phản hồi ───────────────────────────────────
async def test_unknown_email_still_runs_exactly_one_bcrypt_against_dummy_hash(
    client: httpx.AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    hashes: list[str] = []

    def _spy(password: str, password_hash: str) -> bool:
        hashes.append(password_hash)
        return False

    monkeypatch.setattr(auth_routes, "verify_password", _spy)
    unknown = await _login(client, "khong-co@shop.vn")
    wrong_pw = await _login(client, EXISTING.email)
    assert unknown.status_code == wrong_pw.status_code == 401
    assert unknown.json()["detail"] == wrong_pw.json()["detail"]  # cùng câu lỗi
    assert hashes == [auth_routes._DUMMY_HASH, EXISTING.password_hash]  # MỖI nhánh đúng một lần bcrypt


def test_dummy_hash_costs_the_same_as_a_real_hash() -> None:
    # Hash giả phải là bcrypt HỢP LỆ cùng cost — hash hỏng thì checkpw ném ValueError tức thì → lộ thời gian.
    dummy_cost = auth_routes._DUMMY_HASH.split("$")[2]
    assert dummy_cost == EXISTING.password_hash.split("$")[2]
    assert auth_routes.verify_password("bat-ky", auth_routes._DUMMY_HASH) is False


# ── Giới hạn tần suất ─────────────────────────────────────────────────────────
def test_limiters_are_built_from_settings() -> None:
    window = settings.rate_limit_window_seconds
    assert (auth_routes._login_ip_limiter.limit, auth_routes._login_ip_limiter.window) == (
        settings.login_rate_per_ip, window)
    assert auth_routes._login_email_limiter.limit == settings.login_rate_per_email
    assert auth_routes._register_ip_limiter.limit == settings.register_rate_per_ip


async def test_login_rate_limited_per_ip_with_retry_after(
    client: httpx.AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[str] = []

    def _spy(password: str, password_hash: str) -> bool:
        calls.append(password_hash)
        return False

    monkeypatch.setattr(auth_routes, "_login_ip_limiter", SlidingWindowLimiter(2, 60))
    monkeypatch.setattr(auth_routes, "verify_password", _spy)
    codes = [(await _login(client, f"u{i}@shop.vn")).status_code for i in range(2)]
    blocked = await _login(client, "u9@shop.vn")
    assert codes == [401, 401]
    assert blocked.status_code == 429
    assert 1 <= int(blocked.headers["Retry-After"]) <= 60
    assert "thử lại" in blocked.json()["detail"]
    assert len(calls) == 2  # lần bị chặn KHÔNG tốn bcrypt


async def test_login_rate_limited_per_normalised_email(
    client: httpx.AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(auth_routes, "_login_ip_limiter", SlidingWindowLimiter(0, 60))  # tách riêng luật theo email
    monkeypatch.setattr(auth_routes, "_login_email_limiter", SlidingWindowLimiter(2, 60))
    monkeypatch.setattr(auth_routes, "verify_password", lambda *_: False)
    codes = [(await _login(client, e)).status_code for e in (" KHACH@shop.vn", "khach@shop.vn ", "Khach@Shop.VN")]
    assert codes == [401, 401, 429]  # cùng một email sau chuẩn hoá
    assert (await _login(client, "khac@shop.vn")).status_code == 401  # email khác không bị vạ lây


async def test_register_rate_limited_per_ip(client: httpx.AsyncClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(auth_routes, "_register_ip_limiter", SlidingWindowLimiter(2, 60))
    monkeypatch.setattr(auth_routes, "hash_password", lambda _password: "hashed")
    codes = [
        (await client.post("/api/auth/register", json={"email": f"moi{i}@shop.vn", "password": "123456"})).status_code
        for i in range(3)
    ]
    assert codes == [201, 201, 429]
