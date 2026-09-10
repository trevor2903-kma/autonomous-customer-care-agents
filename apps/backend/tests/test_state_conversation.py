"""Audit v2 — primitive ghi trạng thái/tin của conversation_service. Offline (compile SQL + session giả).

`transition_status` là CÁCH DUY NHẤT ghi status (GRAPH-02.2/FE-03): UPDATE compare-and-set + rowcount == 1.
`insert_message` là INSERT nhẹ KHÔNG commit (ghép transaction của caller — GRAPH-02.1/OPS-01.3).
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.dialects import postgresql

from app.models.enums import ConversationStatus, MessageSender
from app.models.message import Message
from app.services import conversation_service as cs

CONV = uuid.uuid4()
ADMIN = uuid.uuid4()


def _sql(stmt: Any) -> tuple[str, dict[str, Any]]:
    compiled = stmt.compile(dialect=postgresql.dialect())
    return str(compiled), dict(compiled.params)


def test_transition_stmt_is_compare_and_set_on_status() -> None:
    sql, params = _sql(
        cs.transition_stmt(
            CONV,
            to=ConversationStatus.REPLIED,
            allowed_from=[ConversationStatus.PENDING_APPROVAL],
        )
    )
    assert sql.startswith("UPDATE conversation SET status=")
    assert "WHERE conversation.id = " in sql and "conversation.status IN" in sql
    assert params["status"] == ConversationStatus.REPLIED
    # KHÔNG đụng assigned_admin_id / current_intent khi không yêu cầu (blind write cũ ghi đè cả hàng).
    assert "assigned_admin_id" not in sql.split("WHERE")[0]
    assert "current_intent" not in sql


def test_transition_stmt_takeover_assigns_in_same_update_with_held_guard() -> None:
    sql, params = _sql(
        cs.transition_stmt(
            CONV,
            to=ConversationStatus.HUMAN_HANDLING,
            allowed_from=[ConversationStatus.IN_HUMAN_QUEUE],
            assigned_admin_id=ADMIN,
            not_held_by_other_than=ADMIN,
        )
    )
    set_part, where_part = sql.split("WHERE")
    assert "assigned_admin_id=" in set_part  # gán người giữ trong CÙNG câu UPDATE
    # Guard "ca do admin KHÁC giữ": NOT (HUMAN_HANDLING AND có người giữ AND người đó != mình)
    assert "NOT (conversation.status = " in where_part
    assert "conversation.assigned_admin_id IS NOT NULL" in where_part
    assert "conversation.assigned_admin_id != " in where_part
    assert ADMIN in params.values()


def test_transition_stmt_writes_current_intent_only_when_given() -> None:
    sql, params = _sql(
        cs.transition_stmt(
            CONV,
            to=ConversationStatus.AWAITING_CUSTOMER,
            allowed_from=[ConversationStatus.REPLIED],
            current_intent="refund",
        )
    )
    assert "current_intent=" in sql.split("WHERE")[0]
    assert params["current_intent"] == "refund"


class _Result:
    def __init__(self, rowcount: int) -> None:
        self.rowcount = rowcount


class _Session:
    """Session giả: ghi lại add/flush/execute/commit — đủ để khẳng định hàm KHÔNG commit, KHÔNG nạp hội thoại."""

    def __init__(self, rowcount: int = 1) -> None:
        self.rowcount = rowcount
        self.added: list[Any] = []
        self.executed: list[Any] = []
        self.flushes = 0
        self.commits = 0

    def add(self, obj: Any) -> None:
        self.added.append(obj)

    async def flush(self) -> None:
        self.flushes += 1

    async def execute(self, stmt: Any) -> _Result:
        self.executed.append(stmt)
        return _Result(self.rowcount)

    async def commit(self) -> None:
        self.commits += 1


async def test_transition_status_true_only_when_one_row_changed() -> None:
    ok = _Session(rowcount=1)
    lost = _Session(rowcount=0)
    kwargs = dict(to=ConversationStatus.REPLIED, allowed_from=[ConversationStatus.PENDING_APPROVAL])
    assert await cs.transition_status(ok, CONV, **kwargs) is True
    assert await cs.transition_status(lost, CONV, **kwargs) is False
    assert ok.commits == 0 and lost.commits == 0  # ghép được vào transaction của caller


async def test_insert_message_is_light_insert_without_commit() -> None:
    s = _Session()
    msg = await cs.insert_message(
        s, CONV, sender=MessageSender.CUSTOMER, content="size M còn không", client_msg_id="cid-1"
    )
    assert isinstance(msg, Message) and s.added == [msg]
    assert msg.conversation_id == CONV and msg.client_msg_id == "cid-1"
    assert s.flushes == 1 and s.commits == 0
    # Chỉ MỘT câu UPDATE conversation (bump + xoá mốc đã-nhắc) — không SELECT nạp hội thoại/lịch sử.
    assert len(s.executed) == 1
    sql, params = _sql(s.executed[0])
    assert sql.startswith("UPDATE conversation SET")
    assert "last_message_at" in params and params["auto_resolve_reminded_at"] is None


async def test_insert_message_system_message_keeps_silence_clock() -> None:
    s = _Session()
    await cs.insert_message(s, CONV, sender=MessageSender.AI, content="nhắc", bump_activity=False)
    assert s.executed == []  # tin hệ thống auto-resolve KHÔNG bump last_message_at, KHÔNG xoá mốc đã-nhắc


async def test_insert_message_admin_bumps_activity_but_keeps_reminder_mark() -> None:
    s = _Session()
    await cs.insert_message(s, CONV, sender=MessageSender.ADMIN, content="chào anh")
    _, params = _sql(s.executed[0])
    assert "last_message_at" in params
    assert "auto_resolve_reminded_at" not in params  # chỉ tin KHÁCH mới thoát vòng auto-resolve
