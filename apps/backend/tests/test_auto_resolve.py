"""Auto-resolve (09c) – classify_idle thuần, tất định, offline (không DB/LLM)."""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

from app.models.enums import ConversationStatus
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
