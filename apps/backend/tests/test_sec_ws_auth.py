"""SEC-XC.3 — WS đọc role từ DB (như `require_admin`), không tin claim trong JWT. Offline: session DB giả."""

from __future__ import annotations

import uuid
from typing import Any

import pytest

from app.api.ws import auth as ws_auth
from app.core.security import create_access_token
from app.models import User
from app.models.enums import UserRole


class _FakeWebSocket:
    def __init__(self, token: str | None) -> None:
        self.query_params = {"token": token} if token is not None else {}
        self.closed_with: int | None = None

    async def close(self, code: int = 1000) -> None:
        self.closed_with = code


class _FakeSession:
    def __init__(self, users: dict[uuid.UUID, User], *, boom: bool) -> None:
        self.users, self.boom = users, boom

    async def __aenter__(self) -> _FakeSession:
        return self

    async def __aexit__(self, *exc: object) -> None:
        return None

    async def get(self, model: type, ident: uuid.UUID) -> User | None:
        if self.boom:
            raise ConnectionError("db down")
        return self.users.get(ident)


def _use_db(monkeypatch: pytest.MonkeyPatch, *users: User, boom: bool = False) -> list[int]:
    """Thay AsyncSessionLocal bằng DB giả; trả danh sách đếm số session đã mở."""
    opened: list[int] = []

    def _factory() -> _FakeSession:
        opened.append(1)
        return _FakeSession({u.id: u for u in users}, boom=boom)

    monkeypatch.setattr(ws_auth, "AsyncSessionLocal", _factory)
    return opened


def _user(role: str) -> User:
    return User(id=uuid.uuid4(), email=f"{role}@shop.vn", password_hash="x", role=role)


def _ws(user_id: Any, role: str) -> _FakeWebSocket:
    return _FakeWebSocket(create_access_token(user_id=str(user_id), role=role))


async def test_admin_with_admin_role_in_db_is_accepted(monkeypatch: pytest.MonkeyPatch) -> None:
    admin = _user(UserRole.ADMIN)
    _use_db(monkeypatch, admin)
    ws = _ws(admin.id, UserRole.ADMIN)
    payload = await ws_auth.authenticate_websocket(ws, UserRole.ADMIN)
    assert payload is not None and payload["sub"] == str(admin.id)  # vẫn trả payload JWT như cũ
    assert ws.closed_with is None


async def test_demoted_admin_old_token_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    # Nhân viên nghỉ việc: DB đã hạ về customer, token cũ vẫn ghi role=admin → KHÔNG được mở WS admin.
    demoted = _user(UserRole.CUSTOMER)
    _use_db(monkeypatch, demoted)
    ws = _ws(demoted.id, UserRole.ADMIN)
    assert await ws_auth.authenticate_websocket(ws, UserRole.ADMIN) is None
    assert ws.closed_with == ws_auth.WS_AUTH_CLOSE_CODE


async def test_deleted_user_old_token_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    _use_db(monkeypatch)  # user không còn trong DB
    for role in (UserRole.ADMIN, UserRole.CUSTOMER):
        ws = _ws(uuid.uuid4(), role)
        assert await ws_auth.authenticate_websocket(ws, role) is None
        assert ws.closed_with == ws_auth.WS_AUTH_CLOSE_CODE


async def test_customer_socket_accepts_customer_and_rejects_admin_account(monkeypatch: pytest.MonkeyPatch) -> None:
    customer, admin = _user(UserRole.CUSTOMER), _user(UserRole.ADMIN)
    _use_db(monkeypatch, customer, admin)
    ok = _ws(customer.id, UserRole.CUSTOMER)
    assert await ws_auth.authenticate_websocket(ok, UserRole.CUSTOMER) is not None
    wrong = _ws(admin.id, UserRole.ADMIN)
    assert await ws_auth.authenticate_websocket(wrong, UserRole.CUSTOMER) is None
    assert wrong.closed_with == ws_auth.WS_AUTH_CLOSE_CODE


async def test_db_error_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    admin = _user(UserRole.ADMIN)
    _use_db(monkeypatch, admin, boom=True)
    ws = _ws(admin.id, UserRole.ADMIN)
    assert await ws_auth.authenticate_websocket(ws, UserRole.ADMIN) is None
    # Vẫn KHÔNG cho vào, nhưng là lỗi server (1011) chứ không phải lỗi xác thực (4401): token còn hợp lệ → FE nối lại.
    assert ws.closed_with == ws_auth.WS_INTERNAL_ERROR_CODE != ws_auth.WS_AUTH_CLOSE_CODE


@pytest.mark.parametrize("token", [None, "", "khong-phai-jwt"], ids=["missing", "empty", "garbage"])
async def test_missing_or_invalid_token_never_touches_db(monkeypatch: pytest.MonkeyPatch, token: str | None) -> None:
    opened = _use_db(monkeypatch)
    ws = _FakeWebSocket(token)
    assert await ws_auth.authenticate_websocket(ws, UserRole.ADMIN) is None
    assert ws.closed_with == ws_auth.WS_AUTH_CLOSE_CODE
    assert opened == []


async def test_non_uuid_sub_is_rejected_without_db(monkeypatch: pytest.MonkeyPatch) -> None:
    opened = _use_db(monkeypatch)
    ws = _ws("khong-phai-uuid", UserRole.ADMIN)
    assert await ws_auth.authenticate_websocket(ws, UserRole.ADMIN) is None
    assert ws.closed_with == ws_auth.WS_AUTH_CLOSE_CODE
    assert opened == []
