"""ConnectionHub (08c) — pub/sub in-process: publish tới subscriber KHÁC, exclude người gửi. Offline (asyncio)."""

from __future__ import annotations

from app.api.ws.hub import ConnectionHub


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
