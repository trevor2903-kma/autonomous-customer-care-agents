"""Giờ hỗ trợ (09c offline) — is_within_support_hours THUẦN, tất định, offline (config 9–21, Asia/Ho_Chi_Minh)."""

from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from app.services.business_hours import is_within_support_hours

VN = ZoneInfo("Asia/Ho_Chi_Minh")


def test_within_hours_midday() -> None:
    assert is_within_support_hours(datetime(2026, 8, 28, 10, 0, tzinfo=VN)) is True


def test_before_open_is_outside() -> None:
    assert is_within_support_hours(datetime(2026, 8, 28, 8, 59, tzinfo=VN)) is False


def test_boundary_open_inclusive() -> None:
    # 9:00 đúng mở cửa → trong giờ [start, end)
    assert is_within_support_hours(datetime(2026, 8, 28, 9, 0, tzinfo=VN)) is True


def test_boundary_close_exclusive() -> None:
    # 21:00 đúng đóng cửa → NGOÀI giờ (end loại trừ)
    assert is_within_support_hours(datetime(2026, 8, 28, 21, 0, tzinfo=VN)) is False


def test_late_night_is_outside() -> None:
    assert is_within_support_hours(datetime(2026, 8, 28, 23, 30, tzinfo=VN)) is False


def test_utc_input_converted_to_support_tz() -> None:
    # 02:00 UTC = 09:00 VN → trong giờ; 01:00 UTC = 08:00 VN → ngoài giờ
    assert is_within_support_hours(datetime(2026, 8, 28, 2, 0, tzinfo=timezone.utc)) is True
    assert is_within_support_hours(datetime(2026, 8, 28, 1, 0, tzinfo=timezone.utc)) is False


def test_naive_treated_as_utc() -> None:
    # naive 15:00 coi là 15:00 UTC = 22:00 VN → ngoài giờ
    assert is_within_support_hours(datetime(2026, 8, 28, 15, 0)) is False
