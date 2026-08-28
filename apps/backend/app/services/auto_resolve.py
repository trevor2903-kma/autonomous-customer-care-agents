"""Auto-resolve (09c) – tự nhắc rồi đóng ca phía-AI im lặng quá ngưỡng.

Lõi `classify_idle` THUẦN (offline-testable): route trên trạng thái + hai mức thời gian.
Sweep (I/O) thêm ở task sau. Chỉ REPLIED/AWAITING_CUSTOMER; các trạng thái khác NOOP.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from enum import StrEnum

from ..models.enums import ConversationStatus

# Trạng thái phía-AI, bên phải hàng đợi là KHÁCH → im lặng = khách bỏ đi (spec §5, D5).
_SWEEPABLE = frozenset({ConversationStatus.REPLIED, ConversationStatus.AWAITING_CUSTOMER})


class IdleAction(StrEnum):
    NOOP = "noop"
    REMIND = "remind"
    RESOLVE = "resolve"


def classify_idle(
    *,
    status: str,
    last_message_at: datetime | None,
    reminded_at: datetime | None,
    now: datetime,
    t1_minutes: int,
    t2_minutes: int,
) -> IdleAction:
    """Quyết định cho MỘT ca. Tất định, không đọc gate/DB (call-site đã lọc gate ON).

    - status ngoài {REPLIED, AWAITING_CUSTOMER} → NOOP (chết an toàn kép).
    - chưa nhắc & im lặng ≥ T1 → REMIND.
    - Đã nhắc & khách chưa nhận lại (last_message_at ≤ reminded_at) & quá T2 kể từ khi nhắc → RESOLVE.
    """
    if status not in _SWEEPABLE or last_message_at is None:
        return IdleAction.NOOP
    if reminded_at is None:
        if now - last_message_at >= timedelta(minutes=t1_minutes):
            return IdleAction.REMIND
        return IdleAction.NOOP
    # Đã nhắc: khách nhận lại sau khi nhắc → thoát vòng đóng
    if last_message_at > reminded_at:
        return IdleAction.NOOP
    if now - reminded_at >= timedelta(minutes=t2_minutes):
        return IdleAction.RESOLVE
    return IdleAction.NOOP
