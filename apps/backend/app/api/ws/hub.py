"""In-process pub/sub hub (08c) — realtime 2 chiều khách ↔ admin CÙNG một hội thoại. KHÔNG Redis (1 worker).

Event-driven (mỗi kết nối 1 `asyncio.Queue`), KHÔNG polling. Đằng sau interface nhỏ (register/unregister/publish)
để sau SWAP sang Redis pub/sub cho ĐA-WORKER (PRD §10 FR-ASYNC-7) mà không đụng call-site. Chỉ sống trong
tiến trình → giữ 1 uvicorn worker ở slice này.
"""

from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Any

Payload = dict[str, Any]


class ConnectionHub:
    """conversation_id -> tập subscriber (mỗi subscriber 1 asyncio.Queue). `publish` đẩy payload vào queue của
    các subscriber KHÁC (exclude = người gửi, để không tự nghe lại). Mỗi WS chạy 1 task đọc queue → forward socket."""

    def __init__(self) -> None:
        self._subs: dict[str, set[asyncio.Queue[Payload]]] = defaultdict(set)

    def register(self, conversation_id: str) -> asyncio.Queue[Payload]:
        """Đăng ký một kết nối vào hội thoại; trả queue để task hub-listener của kết nối đó đọc."""
        queue: asyncio.Queue[Payload] = asyncio.Queue()
        self._subs[conversation_id].add(queue)
        return queue

    def unregister(self, conversation_id: str, queue: asyncio.Queue[Payload]) -> None:
        subs = self._subs.get(conversation_id)
        if subs is None:
            return
        subs.discard(queue)
        if not subs:
            self._subs.pop(conversation_id, None)

    async def publish(
        self, conversation_id: str, payload: Payload, *, exclude: asyncio.Queue[Payload] | None = None
    ) -> None:
        """Phát payload tới các subscriber khác của hội thoại (bỏ qua `exclude`). Không có subscriber → no-op."""
        for queue in list(self._subs.get(conversation_id, ())):
            if queue is exclude:
                continue
            await queue.put(payload)

    def subscriber_count(self, conversation_id: str) -> int:
        """Số kết nối đang mở của hội thoại (dùng cho test/health)."""
        return len(self._subs.get(conversation_id, ()))


# Singleton in-process — 1 worker (PRD §10: đa-worker cần Redis pub/sub, để dành).
hub = ConnectionHub()
