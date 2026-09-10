"""In-process pub/sub hub (08c) — realtime 2 chiều khách ↔ admin CÙNG một hội thoại. KHÔNG Redis (1 worker).

Event-driven (mỗi kết nối 1 `asyncio.Queue`), KHÔNG polling. Đằng sau interface nhỏ (register/unregister/publish)
để sau SWAP sang Redis pub/sub cho ĐA-WORKER (PRD §10 FR-ASYNC-7) mà không đụng call-site. Chỉ sống trong
tiến trình → giữ 1 uvicorn worker ở slice này.

Giao thức realtime v2 (audit v2, contract §4). MỌI publisher đi qua HAI helper — nhờ vậy kênh inbox admin
(`INBOX_KEY`, WS `/ws/admin-inbox`, thay polling 10s — FE-01.5) không bao giờ sót sự kiện:
- `hub.notify_message(conv, sender=, content=, message_id=, exclude=)` → frame
  `{"type":"message","from","content","message_id"}` tới subscriber của ca + `{"type":"inbox","event":"message"}`.
- `hub.notify_status(conv, status=, assigned_admin_id=, exclude=)` → frame
  `{"type":"status","status","assigned_admin_id"}` tới MỌI subscriber của ca (khách + admin) + inbox `"status"`.
`exclude` = queue của socket ĐÃ nhận frame tương đương trực tiếp (không tự nghe lại). Hub lỗi → log, KHÔNG ném:
realtime là phụ, không được làm hỏng lượt chat hay route admin.

`parse_client_frame`: đọc frame client (khách + admin) — JSON `{"type":"message"|"ping",...}` hoặc chữ thô (legacy).
"""

from __future__ import annotations

import asyncio
import json
import uuid
from collections import defaultdict
from typing import Any, NamedTuple

from ...core.logging import get_logger

Payload = dict[str, Any]

log = get_logger("ws.hub")

# Kênh sự kiện inbox admin (danh sách ca + hàng đợi). KHÔNG trùng được khoá ca (khoá ca là UUID).
INBOX_KEY = "admin-inbox"

# = độ dài cột `message.client_msg_id`; id dài hơn / không phải chuỗi → coi như KHÔNG có id (không chống trùng được).
_CLIENT_MSG_ID_MAX = 64


def _sid(value: Any) -> str | None:
    return str(value) if value is not None else None


class ClientFrame(NamedTuple):
    """Frame client đã đọc: `kind` ∈ {"message", "ping"}; `content` = nội dung tin (thô, CHƯA sanitize)."""

    kind: str
    content: str
    client_msg_id: str | None


def parse_client_frame(raw: str) -> ClientFrame:
    """Đọc 1 frame client (hàm THUẦN). JSON object có `type` biết → theo type; mọi thứ khác (chữ thô, JSON không phải
    object, type lạ, content không phải chuỗi) = tin nhắn legacy: content = nguyên văn frame, client_msg_id = None."""
    try:
        data = json.loads(raw)
    except (ValueError, RecursionError):
        data = None
    if isinstance(data, dict):
        kind = data.get("type")
        if kind == "ping":
            return ClientFrame("ping", "", None)
        content = data.get("content")
        if kind == "message" and isinstance(content, str):
            cid = data.get("client_msg_id")
            valid = isinstance(cid, str) and 0 < len(cid) <= _CLIENT_MSG_ID_MAX
            return ClientFrame("message", content, cid if valid else None)
    return ClientFrame("message", raw, None)


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

    async def notify_message(
        self,
        conversation_id: str | uuid.UUID,
        *,
        sender: str,
        content: str,
        message_id: uuid.UUID | str | None,
        exclude: asyncio.Queue[Payload] | None = None,
    ) -> None:
        """Tin mới (khách/AI/admin) → subscriber của ca + sự kiện inbox. `message_id` = id đã lưu (None nếu chưa lưu)."""
        key = str(conversation_id)
        payload = {"type": "message", "from": str(sender), "content": content, "message_id": _sid(message_id)}
        await self._publish_safe(key, payload, exclude)
        await self._publish_safe(INBOX_KEY, _inbox_event(key, "message", None))

    async def notify_status(
        self,
        conversation_id: str | uuid.UUID,
        *,
        status: str | None,
        assigned_admin_id: uuid.UUID | str | None,
        exclude: asyncio.Queue[Payload] | None = None,
    ) -> None:
        """Status đổi → MỌI subscriber của ca (khách + admin, trừ `exclude`) + sự kiện inbox."""
        key = str(conversation_id)
        payload = {"type": "status", "status": _sid(status), "assigned_admin_id": _sid(assigned_admin_id)}
        await self._publish_safe(key, payload, exclude)
        await self._publish_safe(INBOX_KEY, _inbox_event(key, "status", status))

    async def _publish_safe(
        self, key: str, payload: Payload, exclude: asyncio.Queue[Payload] | None = None
    ) -> None:
        try:
            await self.publish(key, payload, exclude=exclude)
        except Exception as exc:  # noqa: BLE001 — realtime là phụ, đừng để hỏng chat / route admin.
            log.warning("publish to hub failed (bỏ qua): %s", exc)


def _inbox_event(conversation_id: str, event: str, status: str | None) -> Payload:
    return {"type": "inbox", "conversation_id": conversation_id, "event": event, "status": _sid(status)}


# Singleton in-process — 1 worker (PRD §10: đa-worker cần Redis pub/sub, để dành).
hub = ConnectionHub()
