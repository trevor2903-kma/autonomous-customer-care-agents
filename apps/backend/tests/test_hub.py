"""ConnectionHub (08c) — pub/sub in-process: publish tới subscriber KHÁC, exclude người gửi. Offline (asyncio)."""

from __future__ import annotations

import json
import uuid

from app.api.ws.hub import INBOX_KEY, ConnectionHub, parse_client_frame


async def test_publish_reaches_other_excludes_sender() -> None:
    h = ConnectionHub()
    a = h.register("c1")
    b = h.register("c1")
    await h.publish("c1", {"from": "admin", "content": "hi"}, exclude=a)
    assert b.get_nowait() == {"from": "admin", "content": "hi"}  # subscriber khác nhận
    assert a.empty()  # người gửi KHÔNG tự nghe lại


async def test_publish_isolated_per_conversation() -> None:
    h = ConnectionHub()
    q1 = h.register("c1")
    q2 = h.register("c2")
    await h.publish("c1", {"x": 1})
    assert q1.get_nowait() == {"x": 1}
    assert q2.empty()  # hội thoại khác KHÔNG nhận


async def test_unregister_cleans_up() -> None:
    h = ConnectionHub()
    q = h.register("c1")
    assert h.subscriber_count("c1") == 1
    h.unregister("c1", q)
    assert h.subscriber_count("c1") == 0


async def test_publish_no_subscribers_is_noop() -> None:
    h = ConnectionHub()
    await h.publish("nobody", {"x": 1})  # không ném khi không có subscriber


# ── Helper giao thức v2 (audit v2, contract §4.4) ────────────────────────────
async def test_notify_message_reaches_conversation_and_inbox() -> None:
    h = ConnectionHub()
    sender_q = h.register("c1")
    other_q = h.register("c1")
    inbox_q = h.register(INBOX_KEY)
    mid = uuid.uuid4()
    await h.notify_message("c1", sender="customer", content="hi", message_id=mid, exclude=sender_q)
    assert other_q.get_nowait() == {"type": "message", "from": "customer", "content": "hi", "message_id": str(mid)}
    assert sender_q.empty()  # socket đã có frame trực tiếp KHÔNG nhận lại
    # Inbox admin nhận MỌI tin mới (kể cả của socket bị exclude) — thay polling 10s (FE-01.5).
    assert inbox_q.get_nowait() == {"type": "inbox", "conversation_id": "c1", "event": "message", "status": None}


async def test_notify_status_reaches_every_subscriber_and_inbox() -> None:
    h = ConnectionHub()
    customer_q = h.register("c1")
    admin_q = h.register("c1")
    inbox_q = h.register(INBOX_KEY)
    admin = uuid.uuid4()
    await h.notify_status("c1", status="HUMAN_HANDLING", assigned_admin_id=admin)
    frame = {"type": "status", "status": "HUMAN_HANDLING", "assigned_admin_id": str(admin)}
    assert customer_q.get_nowait() == frame and admin_q.get_nowait() == frame
    assert inbox_q.get_nowait() == {
        "type": "inbox", "conversation_id": "c1", "event": "status", "status": "HUMAN_HANDLING"
    }


async def test_notify_never_raises_when_publish_breaks() -> None:
    h = ConnectionHub()

    async def boom(*a: object, **k: object) -> None:
        raise RuntimeError("hub down")

    h.publish = boom  # type: ignore[method-assign]
    await h.notify_message("c1", sender="ai", content="x", message_id=None)  # realtime là phụ: không ném
    await h.notify_status("c1", status="RESOLVED", assigned_admin_id=None)


def test_parse_client_frame_protocol_v2() -> None:
    f = parse_client_frame(json.dumps({"type": "message", "content": "size M?", "client_msg_id": "abc"}))
    assert (f.kind, f.content, f.client_msg_id) == ("message", "size M?", "abc")
    assert parse_client_frame('{"type":"ping"}').kind == "ping"


def test_parse_client_frame_legacy_and_odd_frames_are_raw_messages() -> None:
    for raw in ("chào shop", "123", '{"type":"foo"}', '{"type":"message","content":5}', "[1,2]", '{"type":'):
        f = parse_client_frame(raw)
        assert (f.kind, f.content, f.client_msg_id) == ("message", raw, None)


def test_parse_client_frame_drops_unusable_client_msg_id() -> None:
    # Không phải chuỗi / rỗng / dài hơn cột DB (64) → coi như không có id (KHÔNG làm hỏng lần lưu tin).
    for cid in (123, "", "x" * 65, None):
        f = parse_client_frame(json.dumps({"type": "message", "content": "a", "client_msg_id": cid}))
        assert f.kind == "message" and f.content == "a" and f.client_msg_id is None
