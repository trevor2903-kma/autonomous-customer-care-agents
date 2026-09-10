"""Bộ giả lập dùng chung cho test cụm A (module HỖ TRỢ — không có hàm test_*). Offline hoàn toàn.

- `FakeStore`: "DB" in-memory (conversation + message + audit) + nhật ký sự kiện `log` (commit, frame đã gửi…) để
  khẳng định THỨ TỰ (vd ghi DB trước khi báo khách).
- `FakeSession`: một transaction — ghi được STAGE, chỉ áp vào store khi `commit`; `rollback`/đóng session = bỏ.
- `install_service_fakes`: thay các hàm service bằng bản giả CÙNG CHỮ KÝ (keyword-only như bản thật) → gọi sai
  tham số là TypeError ngay, không che lỗi.
- `FakeWebSocket`: socket điều khiển được từ test (đẩy frame vào, đọc frame ra, rớt kết nối).
"""

from __future__ import annotations

import asyncio
import itertools
import uuid
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi import WebSocketDisconnect
from sqlalchemy.exc import IntegrityError

from app.models.enums import ConversationStatus
from app.models.message import CLIENT_MSG_ID_INDEX
from app.services import conversation_service, escalation_service

_CLOSED = {ConversationStatus.RESOLVED, ConversationStatus.CLOSED}


@dataclass
class FakeMessage:
    id: uuid.UUID
    conversation_id: uuid.UUID
    sender: str
    content: str
    client_msg_id: str | None


class FakeSession:
    def __init__(self, store: FakeStore) -> None:
        self.store = store
        self.staged: list[Callable[[], None]] = []
        self.added: list[Any] = []
        self.commits = 0
        self.rollbacks = 0

    async def __aenter__(self) -> FakeSession:
        return self

    async def __aexit__(self, *exc: object) -> None:
        self.staged.clear()  # đóng session = rollback phần chưa commit (như AsyncSession.close)
        self.added.clear()

    def add(self, obj: Any) -> None:
        self.added.append(obj)

    async def flush(self) -> None:
        return None

    async def commit(self) -> None:
        if self.store.fail_commit:
            raise RuntimeError("DB down")
        for apply in self.staged:
            apply()
        self.store.audit.extend(self.added)
        self.staged.clear()
        self.added.clear()
        self.commits += 1
        self.store.log.append("commit")

    async def rollback(self) -> None:
        self.rollbacks += 1
        self.staged.clear()
        self.added.clear()


class FakeStore:
    def __init__(self) -> None:
        self.convs: dict[uuid.UUID, dict[str, Any]] = {}
        self.messages: list[FakeMessage] = []
        self.audit: list[Any] = []
        self.log: list[str] = []
        self.sessions = 0
        self.fail_commit = False
        self._seq = itertools.count()

    def session(self) -> FakeSession:
        self.sessions += 1
        return FakeSession(self)

    def add_conv(
        self,
        *,
        customer_id: uuid.UUID | None = None,
        status: str = ConversationStatus.REPLIED,
        assigned_admin_id: uuid.UUID | None = None,
        card: dict[str, Any] | None = None,
        current_intent: str | None = None,
    ) -> uuid.UUID:
        cid = uuid.uuid4()
        self.convs[cid] = {
            "id": cid,
            "customer_id": customer_id,
            "status": status,
            "assigned_admin_id": assigned_admin_id,
            "escalation_card": card,
            "current_intent": current_intent,
            "priority": None,
            "severity": None,
            "escalation_reason": None,
            "seq": next(self._seq),
        }
        return cid

    def msgs(self, conv_id: uuid.UUID, sender: str | None = None) -> list[FakeMessage]:
        return [m for m in self.messages if m.conversation_id == conv_id and (sender is None or m.sender == sender)]

    def admin_audit(self) -> list[Any]:
        return [a for a in self.audit if getattr(a, "node", None) == "admin"]


def install_service_fakes(monkeypatch: pytest.MonkeyPatch, store: FakeStore) -> None:
    """Thay hàm service thật bằng bản giả trên `store` (cùng chữ ký)."""

    async def transition_status(
        session: FakeSession,
        conversation_id: uuid.UUID,
        *,
        to: str,
        allowed_from: Iterable[str],
        current_intent: str | None = None,
        assigned_admin_id: uuid.UUID | None = None,
        not_held_by_other_than: uuid.UUID | None = None,
    ) -> bool:
        conv = store.convs.get(conversation_id)
        if conv is None or conv["status"] not in set(allowed_from):
            return False
        held = conv["assigned_admin_id"]
        if (
            not_held_by_other_than is not None
            and conv["status"] == ConversationStatus.HUMAN_HANDLING
            and held is not None
            and held != not_held_by_other_than
        ):
            return False

        def apply() -> None:
            conv["status"] = to
            if current_intent is not None:
                conv["current_intent"] = current_intent
            if assigned_admin_id is not None:
                conv["assigned_admin_id"] = assigned_admin_id

        session.staged.append(apply)
        return True

    async def insert_message(
        session: FakeSession,
        conversation_id: uuid.UUID,
        *,
        sender: str,
        content: str,
        client_msg_id: str | None = None,
        bump_activity: bool = True,
    ) -> FakeMessage:
        if conversation_id not in store.convs:
            raise IntegrityError("INSERT INTO message", {}, Exception("violates foreign key constraint"))
        if client_msg_id is not None and any(
            m.client_msg_id == client_msg_id for m in store.msgs(conversation_id)
        ):
            raise IntegrityError(
                "INSERT INTO message",
                {},
                Exception(f'duplicate key value violates unique constraint "{CLIENT_MSG_ID_INDEX}"'),
            )
        msg = FakeMessage(uuid.uuid4(), conversation_id, str(sender), content, client_msg_id)
        session.staged.append(lambda: store.messages.append(msg))
        return msg

    async def apply_escalation(
        session: FakeSession,
        conversation_id: uuid.UUID,
        *,
        card: dict[str, Any],
        priority: str | None,
        severity: str | None,
        reason: str | None,
    ) -> None:
        def apply() -> None:
            store.convs[conversation_id].update(
                escalation_card=card, priority=priority, severity=severity, escalation_reason=reason
            )

        session.staged.append(apply)

    async def get_status_and_admin(
        session: FakeSession, conversation_id: uuid.UUID
    ) -> tuple[str, uuid.UUID | None] | None:
        conv = store.convs.get(conversation_id)
        return (conv["status"], conv["assigned_admin_id"]) if conv else None

    async def get_status_and_intent(
        session: FakeSession, conversation_id: uuid.UUID
    ) -> tuple[str | None, str | None]:
        conv = store.convs.get(conversation_id)
        return (conv["status"], conv["current_intent"]) if conv else (None, None)

    async def get_active_conversation_for_customer(
        session: FakeSession, customer_id: uuid.UUID
    ) -> SimpleNamespace | None:
        await asyncio.sleep(0)  # nhường vòng lặp — lộ race nếu không có khoá khách
        open_convs = [
            c for c in store.convs.values() if c["customer_id"] == customer_id and c["status"] not in _CLOSED
        ]
        if not open_convs:
            return None
        return SimpleNamespace(**max(open_convs, key=lambda c: c["seq"]))

    async def open_case_for_customer(
        session: FakeSession, customer_id: uuid.UUID, *, display: str | None = None
    ) -> SimpleNamespace:
        await asyncio.sleep(0)
        cid = store.add_conv(customer_id=customer_id, status=ConversationStatus.ACTIVE_AI)
        return SimpleNamespace(**store.convs[cid])

    async def get_recent_messages(
        session: FakeSession, conversation_id: uuid.UUID, limit: int
    ) -> list[dict[str, str]]:
        return [{"sender": m.sender, "content": m.content} for m in store.msgs(conversation_id)][-limit:]

    async def get_conversation(session: FakeSession, conversation_id: uuid.UUID) -> SimpleNamespace | None:
        conv = store.convs.get(conversation_id)
        if conv is None:
            return None
        return SimpleNamespace(**conv, messages=list(store.msgs(conversation_id)))

    for name, fn in {
        "transition_status": transition_status,
        "insert_message": insert_message,
        "get_status_and_admin": get_status_and_admin,
        "get_status_and_intent": get_status_and_intent,
        "get_active_conversation_for_customer": get_active_conversation_for_customer,
        "open_case_for_customer": open_case_for_customer,
        "get_recent_messages": get_recent_messages,
        "get_conversation": get_conversation,
    }.items():
        monkeypatch.setattr(conversation_service, name, fn)
    monkeypatch.setattr(escalation_service, "apply_escalation", apply_escalation)


class FakeWebSocket:
    """Socket giả: test đẩy frame (`push`), `drop()` = khách rớt kết nối; frame server gửi nằm ở `sent`."""

    def __init__(self, store: FakeStore | None = None, *, name: str = "ws") -> None:
        self.incoming: asyncio.Queue[str | None] = asyncio.Queue()
        self.sent: list[dict[str, Any]] = []
        self.closed = False
        self.close_code: int | None = None
        self.query_params = {"token": "t"}
        self.store = store
        self.name = name

    async def accept(self) -> None:
        return None

    async def close(self, code: int = 1000) -> None:
        self.closed = True
        self.close_code = code

    async def receive_text(self) -> str:
        item = await self.incoming.get()
        if item is None:
            self.closed = True
            raise WebSocketDisconnect(code=1000)
        return item

    async def send_json(self, payload: dict[str, Any]) -> None:
        if self.closed:
            raise RuntimeError("socket closed")
        self.sent.append(payload)
        if self.store is not None:
            self.store.log.append(f"{self.name}:{payload.get('type')}")

    def push(self, raw: str) -> None:
        self.incoming.put_nowait(raw)

    def drop(self) -> None:
        self.incoming.put_nowait(None)

    def frames(self, type_: str) -> list[dict[str, Any]]:
        return [f for f in self.sent if f.get("type") == type_]


async def until(predicate: Callable[[], bool], timeout: float = 2.0) -> None:
    """Chờ tới khi `predicate()` đúng (vòng lặp sự kiện chạy tiếp); quá hạn → AssertionError."""
    loop = asyncio.get_running_loop()
    deadline = loop.time() + timeout
    while not predicate():
        if loop.time() > deadline:
            raise AssertionError("điều kiện không xảy ra trong thời hạn")
        await asyncio.sleep(0.002)


def drain(queue: asyncio.Queue[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    while not queue.empty():
        out.append(queue.get_nowait())
    return out
