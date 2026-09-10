"""Audit v2 — WS admin: chỉ admin ĐANG GIỮ ca mới gửi được tin, ack kèm message_id, kênh inbox. Offline.

FE-03.2 / GRAPH-02.4 (hai admin cùng nói với khách), FE-01.4 (ack), FE-01.3 (frame status), FE-01.5 (inbox).
"""

from __future__ import annotations

import asyncio
import json
import uuid
from typing import Any

import pytest
from starlette.routing import Match

from app.api.ws import admin as ws_admin
from app.api.ws.hub import INBOX_KEY, ConnectionHub
from app.models.enums import ConversationStatus as S
from tests.test_state_support import FakeStore, FakeWebSocket, drain, install_service_fakes, until

ME = uuid.uuid4()
OTHER = uuid.uuid4()


@pytest.fixture
def env(monkeypatch: pytest.MonkeyPatch) -> tuple[FakeStore, ConnectionHub]:
    store = FakeStore()
    install_service_fakes(monkeypatch, store)
    hub = ConnectionHub()
    monkeypatch.setattr(ws_admin, "hub", hub)
    monkeypatch.setattr(ws_admin, "AsyncSessionLocal", store.session)

    async def auth(websocket: Any, role: str) -> dict[str, Any] | None:
        token = websocket.query_params.get("token")
        return {"sub": token, "role": role} if token else None

    monkeypatch.setattr(ws_admin, "authenticate_websocket", auth)
    return store, hub


def _msg(content: str, cid: str | None = None) -> str:
    return json.dumps({"type": "message", "content": content, "client_msg_id": cid})


async def _open(conv_id: uuid.UUID, admin_id: uuid.UUID) -> tuple[FakeWebSocket, asyncio.Task[None]]:
    ws = FakeWebSocket(name="admin")
    ws.query_params = {"token": str(admin_id)}
    task = asyncio.create_task(ws_admin.admin_ws(ws, conv_id))  # type: ignore[arg-type]
    await until(lambda: bool(ws.frames("system")))
    return ws, task


async def _close(ws: FakeWebSocket, task: asyncio.Task[None]) -> None:
    ws.drop()
    await asyncio.wait_for(task, 2)


async def test_connect_frame_carries_status_and_holder(env: tuple[FakeStore, ConnectionHub]) -> None:
    store, _ = env
    cid = store.add_conv(status=S.HUMAN_HANDLING, assigned_admin_id=ME)
    ws, task = await _open(cid, ME)
    assert ws.sent[0] == {
        "type": "system", "message": "admin connected", "status": "HUMAN_HANDLING", "assigned_admin_id": str(ME)
    }
    await _close(ws, task)


@pytest.mark.parametrize(("status", "holder"), [(S.HUMAN_HANDLING, OTHER), (S.IN_HUMAN_QUEUE, None)])
async def test_non_assigned_admin_gets_error_and_nothing_is_persisted_or_sent(
    env: tuple[FakeStore, ConnectionHub], status: str, holder: uuid.UUID | None
) -> None:
    store, hub = env
    cid = store.add_conv(status=status, assigned_admin_id=holder)
    customer_q = hub.register(str(cid))
    inbox_q = hub.register(INBOX_KEY)
    ws, task = await _open(cid, ME)

    ws.push(_msg("em chào anh", "c-1"))
    await until(lambda: bool(ws.frames("error")))
    assert ws.frames("error") == [{"type": "error", "code": "not_assigned", "client_msg_id": "c-1"}]
    assert store.messages == [] and drain(customer_q) == [] and drain(inbox_q) == []
    assert ws.frames("ack") == []
    await _close(ws, task)


async def test_assigned_admin_message_is_persisted_published_then_acked(
    env: tuple[FakeStore, ConnectionHub],
) -> None:
    store, hub = env
    cid = store.add_conv(status=S.HUMAN_HANDLING, assigned_admin_id=ME)
    customer_q = hub.register(str(cid))
    inbox_q = hub.register(INBOX_KEY)
    ws, task = await _open(cid, ME)

    ws.push(_msg("Dạ em kiểm tra đơn giúp anh ạ", "c-1"))
    await until(lambda: bool(ws.frames("ack")))
    saved = store.msgs(cid, "admin")
    assert len(saved) == 1 and saved[0].client_msg_id == "c-1"
    assert ws.frames("ack") == [
        {"type": "ack", "client_msg_id": "c-1", "message_id": str(saved[0].id), "duplicate": False}
    ]
    assert drain(customer_q) == [
        {"type": "message", "from": "admin", "content": "Dạ em kiểm tra đơn giúp anh ạ",
         "message_id": str(saved[0].id), "client_msg_id": "c-1"}
    ]
    assert [e["event"] for e in drain(inbox_q)] == ["message"]
    await _close(ws, task)


async def test_holder_check_locks_the_row_until_the_message_is_committed(
    env: tuple[FakeStore, ConnectionHub],
) -> None:
    store, _ = env
    cid = store.add_conv(status=S.HUMAN_HANDLING, assigned_admin_id=ME)
    ws, task = await _open(cid, ME)
    ws.push(_msg("Dạ em gửi anh mã vận đơn ạ", "l-1"))
    await until(lambda: bool(ws.frames("ack")))
    # SELECT … FOR UPDATE: resolve (kể cả của CHÍNH admin này ở tab/PWA khác) phải CHỜ tin được lưu — không có tin
    # admin nằm trong ca đã đóng.
    assert store.log.index("lock") < store.log.index("commit")
    await _close(ws, task)


async def test_resend_with_same_client_msg_id_reaches_customer_once(
    env: tuple[FakeStore, ConnectionHub],
) -> None:
    store, hub = env
    cid = store.add_conv(status=S.HUMAN_HANDLING, assigned_admin_id=ME)
    customer_q = hub.register(str(cid))
    ws, task = await _open(cid, ME)

    ws.push(_msg("xin chào", "c-1"))
    ws.push(_msg("xin chào", "c-1"))  # gửi lại (không nhận được ack lần đầu)
    await until(lambda: len(ws.frames("ack")) == 2)
    assert [a["duplicate"] for a in ws.frames("ack")] == [False, True]
    assert len(store.msgs(cid)) == 1 and len(drain(customer_q)) == 1
    await _close(ws, task)


async def test_legacy_raw_text_and_ping(env: tuple[FakeStore, ConnectionHub]) -> None:
    store, _ = env
    cid = store.add_conv(status=S.HUMAN_HANDLING, assigned_admin_id=ME)
    ws, task = await _open(cid, ME)
    ws.push('{"type":"ping"}')
    ws.push("chào anh")  # client cũ gửi chữ thô
    await until(lambda: bool(ws.frames("ack")))
    assert ws.frames("pong") == [{"type": "pong"}]
    assert ws.frames("ack")[0]["client_msg_id"] is None
    assert [m.content for m in store.msgs(cid)] == ["chào anh"]
    await _close(ws, task)


async def test_status_frames_from_hub_reach_admin_socket(env: tuple[FakeStore, ConnectionHub]) -> None:
    store, hub = env
    cid = store.add_conv(status=S.REPLIED)
    ws, task = await _open(cid, ME)
    await until(lambda: hub.subscriber_count(str(cid)) == 1)
    await hub.notify_status(cid, status=S.IN_HUMAN_QUEUE, assigned_admin_id=None)
    await until(lambda: bool(ws.frames("status")))
    assert ws.frames("status") == [{"type": "status", "status": "IN_HUMAN_QUEUE", "assigned_admin_id": None}]
    await _close(ws, task)


async def test_status_published_while_the_snapshot_is_read_is_not_lost(
    env: tuple[FakeStore, ConnectionHub], monkeypatch: pytest.MonkeyPatch
) -> None:
    store, hub = env
    cid = store.add_conv(status=S.REPLIED)
    real = ws_admin._current_state

    async def snapshot_then_escalate(conv_id: uuid.UUID) -> Any:
        state = await real(conv_id)  # snapshot: REPLIED…
        store.convs[cid]["status"] = S.IN_HUMAN_QUEUE  # …ngay sau đó lượt AI escalate + phát status (FE-01.3)
        await hub.notify_status(cid, status=S.IN_HUMAN_QUEUE, assigned_admin_id=None)
        return state

    monkeypatch.setattr(ws_admin, "_current_state", snapshot_then_escalate)
    ws, task = await _open(cid, ME)
    await until(lambda: bool(ws.frames("status")))
    assert ws.sent[0]["status"] == "REPLIED"
    assert ws.frames("status") == [{"type": "status", "status": "IN_HUMAN_QUEUE", "assigned_admin_id": None}]
    await _close(ws, task)


# ── Kênh inbox (FE-01.5) ─────────────────────────────────────────────────────
def test_inbox_route_is_not_shadowed_by_conversation_route() -> None:
    routes = {r.path: r for r in ws_admin.router.routes}
    scope = {"type": "websocket", "path": "/ws/admin-inbox", "root_path": ""}
    assert routes["/ws/admin-inbox"].matches(scope)[0] is Match.FULL
    assert routes["/ws/admin/{conversation_id}"].matches(scope)[0] is Match.NONE


async def test_inbox_forwards_events_and_answers_ping(env: tuple[FakeStore, ConnectionHub]) -> None:
    _, hub = env
    ws = FakeWebSocket(name="inbox")
    ws.query_params = {"token": str(ME)}
    task = asyncio.create_task(ws_admin.admin_inbox_ws(ws))  # type: ignore[arg-type]
    await until(lambda: hub.subscriber_count(INBOX_KEY) == 1)

    cid = uuid.uuid4()
    await hub.notify_status(cid, status=S.IN_HUMAN_QUEUE, assigned_admin_id=None)
    await hub.notify_message(cid, sender="customer", content="alo", message_id=None)
    ws.push('{"type":"ping"}')
    await until(lambda: len(ws.frames("inbox")) == 2 and bool(ws.frames("pong")))
    assert ws.frames("inbox") == [
        {"type": "inbox", "conversation_id": str(cid), "event": "status", "status": "IN_HUMAN_QUEUE"},
        {"type": "inbox", "conversation_id": str(cid), "event": "message", "status": None},
    ]
    await _close(ws, task)
    assert hub.subscriber_count(INBOX_KEY) == 0


async def test_inbox_requires_admin(env: tuple[FakeStore, ConnectionHub]) -> None:
    _, hub = env
    ws = FakeWebSocket(name="inbox")
    ws.query_params = {}
    await ws_admin.admin_inbox_ws(ws)  # type: ignore[arg-type]
    assert hub.subscriber_count(INBOX_KEY) == 0
