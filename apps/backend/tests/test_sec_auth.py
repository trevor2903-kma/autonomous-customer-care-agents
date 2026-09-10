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
from app.schemas.auth import EMAIL_MAX_LENGTH

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

    async def get(self, model: type, ident: Any) -> User | None:
        if ident == EXISTING.id:
            return EXISTING
        return None


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


# ── Trần độ dài email: khoá của bộ đếm theo email không phình tuỳ ý ──────────
def _email_of_length(n: int) -> str:
    domain = "@shop.vn"
    return "a" * (n - len(domain)) + domain


async def test_oversized_login_email_is_rejected_before_any_limiter_keeps_a_key(client: httpx.AsyncClient) -> None:
    r = await _login(client, _email_of_length(EMAIL_MAX_LENGTH + 1))
    assert r.status_code == 422  # pydantic chặn trước khi vào route
    assert auth_routes._login_email_limiter._hits == {}  # không găm được khoá cỡ tuỳ ý vào RAM
    assert auth_routes._login_ip_limiter._hits == {}


async def test_login_email_at_max_length_still_reaches_the_route(
    client: httpx.AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(auth_routes, "verify_password", lambda *_: False)
    assert (await _login(client, _email_of_length(EMAIL_MAX_LENGTH))).status_code == 401


async def test_register_rejects_oversized_email(client: httpx.AsyncClient) -> None:
    body = {"email": _email_of_length(EMAIL_MAX_LENGTH + 1), "password": "123456"}
    assert (await client.post("/api/auth/register", json=body)).status_code == 422
    assert auth_routes._register_ip_limiter._hits == {}


# ── httpOnly Cookies & Refresh Token ─────────────────────────────────────────
async def test_login_sets_httponly_cookies(client: httpx.AsyncClient) -> None:
    r = await _login(client, EXISTING.email, PASSWORD)
    assert r.status_code == 200
    # Cả access_token và refresh_token đều có trong cookies
    cookies = r.cookies
    assert "access_token" in cookies
    assert "refresh_token" in cookies
    # Kiểm tra cờ httponly trong Set-Cookie headers
    set_cookies = r.headers.get_list("set-cookie")
    assert any("access_token=" in c and "httponly" in c.lower() for c in set_cookies)
    assert any("refresh_token=" in c and "httponly" in c.lower() for c in set_cookies)


async def test_register_sets_httponly_cookies(client: httpx.AsyncClient) -> None:
    r = await client.post("/api/auth/register", json={"email": "new_user@shop.vn", "password": "password123"})
    assert r.status_code == 201
    assert "access_token" in r.cookies
    assert "refresh_token" in r.cookies
    set_cookies = r.headers.get_list("set-cookie")
    assert any("access_token=" in c and "httponly" in c.lower() for c in set_cookies)


async def test_refresh_with_valid_cookie_succeeds(client: httpx.AsyncClient) -> None:
    # Đăng nhập để lấy cookie refresh_token
    login_res = await _login(client, EXISTING.email, PASSWORD)
    assert login_res.status_code == 200
    refresh_token = login_res.cookies["refresh_token"]

    # Gọi /refresh với cookie refresh_token
    r = await client.post("/api/auth/refresh", headers={"Cookie": f"refresh_token={refresh_token}"})
    assert r.status_code == 200
    assert "access_token" in r.cookies
    data = r.json()
    assert data["role"] == "customer"
    assert data["user_id"] == str(EXISTING.id)


async def test_refresh_without_cookie_fails_401(client: httpx.AsyncClient) -> None:
    r = await client.post("/api/auth/refresh")
    assert r.status_code == 401


async def test_logout_clears_cookies(client: httpx.AsyncClient) -> None:
    r = await client.post("/api/auth/logout")
    assert r.status_code == 200
    assert r.json() == {"ok": True, "message": "logged out"}
    set_cookies = r.headers.get_list("set-cookie")
    # Kiểm tra cookie bị xoá (Max-Age=0 hoặc expires trong quá khứ)
    assert any("access_token=" in c and ("max-age=0" in c.lower() or "expires=" in c.lower()) for c in set_cookies)
    assert any("refresh_token=" in c and ("max-age=0" in c.lower() or "expires=" in c.lower()) for c in set_cookies)


async def test_me_route_with_cookie_access_token(client: httpx.AsyncClient) -> None:
    login_res = await _login(client, EXISTING.email, PASSWORD)
    assert login_res.status_code == 200
    access_token = login_res.cookies["access_token"]

    # Gọi /me bằng cookie access_token (không gắn Bearer header)
    r = await client.get("/api/auth/me", headers={"Cookie": f"access_token={access_token}"})
    assert r.status_code == 200
    assert r.json()["email"] == EXISTING.email


async def test_logout_in_production_includes_secure_and_samesite_none(
    client: httpx.AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "env", "production")
    r = await client.post("/api/auth/logout")
    assert r.status_code == 200
    set_cookies = r.headers.get_list("set-cookie")
    for cookie_name in ("access_token=", "refresh_token="):
        matching = [c for c in set_cookies if cookie_name in c]
        assert len(matching) == 1
        c = matching[0].lower()
        assert "secure" in c
        assert "samesite=none" in c
        assert "httponly" in c
        assert "max-age=0" in c or "expires=" in c


