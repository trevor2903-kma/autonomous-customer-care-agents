"""Giờ hỗ trợ (09c offline) — hàm THUẦN xác định trong/ngoài giờ để chọn câu handoff.

Ngoài giờ AI VẪN auto-reply (facts.md); CHỈ nhánh human_handoff đổi câu ("nhân viên sẽ phản hồi sớm").
Khung [start, end) đọc từ config (NFR-10), đánh giá theo `support_timezone` (shop VN).
"""

from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from ..core.config import settings


def is_within_support_hours(now: datetime) -> bool:
    """True nếu `now` rơi trong khung [start, end) giờ tại timezone hỗ trợ. `now` naive → coi là UTC."""
    aware = now if now.tzinfo is not None else now.replace(tzinfo=timezone.utc)
    local = aware.astimezone(ZoneInfo(settings.support_timezone))
    return settings.support_hours_start <= local.hour < settings.support_hours_end
