"""Auto-resolve (09c) – classify_idle thuần, tất định, offline (không DB/LLM)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

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
