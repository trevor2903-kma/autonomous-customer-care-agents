"""Auto-resolve (09c) – classify_idle thuần, tất định, offline (không DB/LLM).

Phần sweep I/O (audit v2 — OPS-01.1/01.2/01.3) test bằng session giả: CAS + tin cùng transaction, guard im lặng
trên row, session ngắn riêng từng ca, RESOLVE phát frame status.
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.dialects import postgresql

from app.api.ws.hub import INBOX_KEY, ConnectionHub
from app.models.enums import ConversationStatus
from app.services import auto_resolve
from app.services.auto_resolve import IdleAction, classify_idle

NOW = datetime(2026, 8, 28, 12, 0, 0, tzinfo=timezone.utc)


def _ago(minutes: int) -> datetime:
    return NOW - timedelta(minutes=minutes)


def test_noop_before_t1() -> None:
    # im lặng 10' < T1=30 → chưa làm gì
    assert (
        classify_idle(
            status=ConversationStatus.REPLIED,
            last_message_at=_ago(10),
            reminded_at=None,
            now=NOW,
            t1_minutes=30,
            t2_minutes=15,
        )
        == IdleAction.NOOP
    )


def test_remind_after_t1_not_yet_reminded() -> None:
    assert (
        classify_idle(
            status=ConversationStatus.REPLIED,
            last_message_at=_ago(31),
            reminded_at=None,
            now=NOW,
            t1_minutes=30,
            t2_minutes=15,
        )
        == IdleAction.REMIND
    )


def test_awaiting_customer_also_reminded() -> None:
    assert (
        classify_idle(
            status=ConversationStatus.AWAITING_CUSTOMER,
            last_message_at=_ago(31),
            reminded_at=None,
            now=NOW,
            t1_minutes=30,
            t2_minutes=15,
        )
        == IdleAction.REMIND
    )


def test_noop_after_remind_before_t2() -> None:
    # đã nhắc 10' trước, T2=15 → chờ tiếp
    assert (
        classify_idle(
            status=ConversationStatus.REPLIED,
            last_message_at=_ago(45),
            reminded_at=_ago(10),
            now=NOW,
            t1_minutes=30,
            t2_minutes=15,
        )
        == IdleAction.NOOP
    )


def test_resolve_after_remind_past_t2() -> None:
    assert (
        classify_idle(
            status=ConversationStatus.REPLIED,
            last_message_at=_ago(50),
            reminded_at=_ago(16),
            now=NOW,
            t1_minutes=30,
            t2_minutes=15,
        )
        == IdleAction.RESOLVE
    )


def test_customer_replied_after_remind_is_noop() -> None:
    # khách nhận SAU khi đã nhắc (last_message_at > reminded_at) → thoát vòng đóng
    assert (
        classify_idle(
            status=ConversationStatus.REPLIED,
            last_message_at=_ago(2),
            reminded_at=_ago(16),
            now=NOW,
            t1_minutes=30,
            t2_minutes=15,
        )
        == IdleAction.NOOP
    )


def test_excluded_status_never_acts() -> None:
    for status in (
        ConversationStatus.IN_HUMAN_QUEUE,
        ConversationStatus.PENDING_APPROVAL,
        ConversationStatus.HUMAN_HANDLING,
        ConversationStatus.ACTIVE_AI,
    ):
        assert (
            classify_idle(
                status=status,
                last_message_at=_ago(999),
                reminded_at=None,
                now=NOW,
                t1_minutes=30,
                t2_minutes=15,
            )
            == IdleAction.NOOP
        )


def test_none_last_message_is_noop() -> None:
    assert (
        classify_idle(
            status=ConversationStatus.REPLIED,
            last_message_at=None,
            reminded_at=None,
            now=NOW,
            t1_minutes=30,
            t2_minutes=15,
        )
        == IdleAction.NOOP
    )


def test_run_sweep_once_noop_when_gate_off() -> None:
    """Gate auto_resolve OFF → sweep không truy vấn ca, trả 0 (spec §6)."""

    class _Snap:
        auto_resolve_enabled = False
        auto_resolve_minutes = 30
        auto_resolve_grace_minutes = 15

    async def _run() -> int:
        with patch(
            "app.services.auto_resolve.gate_service.get_gate_config",
            new=AsyncMock(return_value=_Snap()),
        ):
            from app.services.auto_resolve import run_sweep_once

            return await run_sweep_once(NOW)

    assert asyncio.run(_run()) == 0


def test_candidate_stmt_has_prefilter_and_limit() -> None:
    """Query ứng viên thu hẹp trong SQL: chỉ ca im lặng ≥ T1 HOẶC đã nhắc, có LIMIT (sub-project A)."""
    from app.services.auto_resolve import _build_candidate_stmt

    stmt = _build_candidate_stmt(now=NOW, t1_minutes=30, limit=250)
    sql = str(stmt.compile(compile_kwargs={"literal_binds": True})).upper()

    assert "LIMIT 250" in sql
    assert "STATUS IN" in sql  # vẫn chỉ REPLIED/AWAITING_CUSTOMER
    assert "LAST_MESSAGE_AT <" in sql  # pre-filter T1
    assert "AUTO_RESOLVE_REMINDED_AT IS NOT NULL" in sql  # ca đã nhắc luôn được xét (để RESOLVE)


# ── Sweep I/O (audit v2) — session giả, KHÔNG DB ─────────────────────────────
class _Sess:
    def __init__(self, owner: _Factory, first: bool) -> None:
        self.owner = owner
        self.first = first
        self.executed: list[Any] = []
        self.commits = 0
        self.closed = False

    async def __aenter__(self) -> _Sess:
        return self

    async def __aexit__(self, *exc: object) -> None:
        self.closed = True  # AsyncSession.close(): phần chưa commit bị rollback

    async def execute(self, stmt: Any) -> Any:
        self.executed.append(stmt)
        if self.first:  # SELECT ứng viên
            return SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: list(self.owner.rows)))
        return SimpleNamespace(rowcount=self.owner.rowcount)

    async def commit(self) -> None:
        self.commits += 1
        self.owner.log.append("commit")


class _Factory:
    """AsyncSessionLocal giả: session ĐẦU cho SELECT ứng viên, mỗi session sau là CAS của một ca."""

    def __init__(self, rows: list[Any], rowcount: int = 1) -> None:
        self.rows = rows
        self.rowcount = rowcount
        self.made: list[_Sess] = []
        self.log: list[str] = []

    def __call__(self) -> _Sess:
        s = _Sess(self, first=not self.made)
        self.made.append(s)
        return s


class _Snap:
    auto_resolve_enabled = True
    auto_resolve_minutes = 30
    auto_resolve_grace_minutes = 15


def _row(*, last: int, reminded: int | None = None) -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid.uuid4(),
        status=ConversationStatus.REPLIED,
        last_message_at=_ago(last),
        auto_resolve_reminded_at=_ago(reminded) if reminded is not None else None,
        assigned_admin_id=None,
    )


@pytest.fixture
def sweep(monkeypatch: pytest.MonkeyPatch) -> SimpleNamespace:
    env = SimpleNamespace(inserted=[], fail_insert=False, hub=ConnectionHub())

    async def insert_message(session: Any, conversation_id: uuid.UUID, *, sender: str, content: str,
                             client_msg_id: str | None = None, bump_activity: bool = True) -> Any:
        if env.fail_insert:
            raise RuntimeError("Neon ngắt kết nối giữa chừng")
        env.inserted.append({"conv": conversation_id, "content": content, "bump": bump_activity})
        return SimpleNamespace(id=uuid.uuid4())

    class _LogHub(ConnectionHub):
        async def publish(self, conversation_id: str, payload: dict[str, Any], *, exclude: Any = None) -> None:
            env.factory.log.append(f"publish:{payload['type']}")
            await super().publish(conversation_id, payload, exclude=exclude)

    env.hub = _LogHub()
    monkeypatch.setattr(auto_resolve.conversation_service, "insert_message", insert_message)
    monkeypatch.setattr(auto_resolve.gate_service, "get_gate_config", AsyncMock(return_value=_Snap()))
    monkeypatch.setattr(auto_resolve, "hub", env.hub)

    def use(rows: list[Any], rowcount: int = 1) -> _Factory:
        env.factory = _Factory(rows, rowcount)
        monkeypatch.setattr(auto_resolve, "AsyncSessionLocal", env.factory)
        return env.factory

    env.use = use
    return env


async def test_remind_commits_cas_and_message_together_then_broadcasts(sweep: SimpleNamespace) -> None:
    row = _row(last=31)
    factory = sweep.use([row])
    customer_q = sweep.hub.register(str(row.id))
    assert await auto_resolve.run_sweep_once(NOW) == 1

    cas = factory.made[1]
    assert cas.commits == 1  # CAS + tin nhắc landing CÙNG MỘT commit
    assert sweep.inserted == [{"conv": row.id, "content": auto_resolve.REMIND_TEMPLATE, "bump": False}]
    frame = customer_q.get_nowait()
    assert frame["type"] == "message" and frame["from"] == "ai" and frame["message_id"]
    assert factory.log.index("commit") < factory.log.index("publish:message")  # phát SAU commit


async def test_insert_failure_rolls_back_the_cas_and_the_sweep_goes_on(sweep: SimpleNamespace) -> None:
    broken, fine = _row(last=40), _row(last=31)
    factory = sweep.use([broken, fine])
    sweep.fail_insert = True
    assert await auto_resolve.run_sweep_once(NOW) == 0
    cas = factory.made[1]
    # KHÔNG commit → mốc đã-nhắc không bao giờ được ghi mà thiếu tin nhắc; vòng sau thử lại sạch (OPS-01.1).
    assert cas.commits == 0 and cas.closed
    assert [e for e in factory.log if e.startswith("publish")] == []
    # Một ca lỗi không giết vòng quét: ca sau vẫn được xét (và cũng chỉ thử, không commit nửa vời).
    assert len(factory.made) == 3


def test_remind_cas_rechecks_silence_on_the_row() -> None:
    compiled = auto_resolve._remind_stmt(uuid.uuid4(), now=NOW, t1_minutes=30).compile(dialect=postgresql.dialect())
    sql = str(compiled)
    assert "conversation.last_message_at <= " in sql  # OPS-01.2: tin khách chen giữa → rowcount 0
    assert "conversation.auto_resolve_reminded_at IS NULL" in sql and "conversation.status IN" in sql
    assert NOW - timedelta(minutes=30) in compiled.params.values()


async def test_customer_message_between_select_and_cas_prevents_the_reminder(sweep: SimpleNamespace) -> None:
    row = _row(last=31)  # SELECT thấy im lặng 31'…
    factory = sweep.use([row], rowcount=0)  # …nhưng khách vừa nhắn: CAS (re-check im lặng trên row) không khớp
    customer_q = sweep.hub.register(str(row.id))
    assert await auto_resolve.run_sweep_once(NOW) == 0
    assert sweep.inserted == [] and customer_q.empty() and factory.made[1].commits == 0


async def test_resolve_also_emits_a_status_frame(sweep: SimpleNamespace) -> None:
    row = _row(last=50, reminded=16)
    sweep.use([row])
    customer_q = sweep.hub.register(str(row.id))
    inbox_q = sweep.hub.register(INBOX_KEY)
    assert await auto_resolve.run_sweep_once(NOW) == 1
    msg, status = customer_q.get_nowait(), customer_q.get_nowait()
    assert msg["type"] == "message" and msg["content"] == auto_resolve.RESOLVE_TEMPLATE
    assert status == {"type": "status", "status": "RESOLVED", "assigned_admin_id": None}
    assert [inbox_q.get_nowait()["event"] for _ in range(2)] == ["message", "status"]


async def test_each_acted_case_uses_its_own_short_session(sweep: SimpleNamespace) -> None:
    rows = [_row(last=31), _row(last=10), _row(last=45)]  # ca giữa chưa tới T1 → NOOP, không mở session
    factory = sweep.use(rows)
    assert await auto_resolve.run_sweep_once(NOW) == 2
    assert len(factory.made) == 1 + 2  # 1 session SELECT + 1 session ngắn cho MỖI ca được hành động
    assert all(s.closed for s in factory.made)
