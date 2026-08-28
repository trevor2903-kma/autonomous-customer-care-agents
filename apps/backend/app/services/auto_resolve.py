"""Auto-resolve (09c) – tự nhắc rồi đóng ca phía-AI im lặng quá ngưỡng.

Lõi `classify_idle` THUẦN (offline-testable): route trên trạng thái + hai mức thời gian.
Sweep (I/O) thêm ở task sau. Chỉ REPLIED/AWAITING_CUSTOMER; các trạng thái khác NOOP.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from enum import StrEnum

from sqlalchemy import select

from ..api.ws.hub import hub
from ..core.config import settings
from ..core.database import AsyncSessionLocal
from ..core.logging import get_logger
from ..models.conversation import Conversation
from ..models.enums import ConversationStatus
from ..services import conversation_service, gate_service

log = get_logger("auto_resolve")

# Trạng thái phía-AI, bên phải hàng đợi là KHÁCH → im lặng = khách bỏ đi (spec §5, D5).
_SWEEPABLE = frozenset({ConversationStatus.REPLIED, ConversationStatus.AWAITING_CUSTOMER})

REMIND_TEMPLATE = (
    "Anh/chị còn cần em hỗ trợ thêm gì không ạ? "
    "Nếu không, em xin phép tạm đóng cuộc trò chuyện này ạ."
)
RESOLVE_TEMPLATE = (
    "Em xin phép tạm đóng cuộc trò chuyện. "
    "Anh/chị cần hỗ trợ thì nhắn lại bất cứ lúc nào ạ."
)


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


async def _broadcast_ai(conv_id, content: str) -> None:
    """Dội tin hệ thống lên hub (admin/khách đang mở thấy realtime). Guarded — hub lỗi KHÔNG chặn sweep."""
    try:
        await hub.publish(str(conv_id), {"type": "message", "from": "ai", "content": content})
    except Exception as exc:  # noqa: BLE001
        log.warning("auto-resolve broadcast failed (bỏ qua): %s", exc)


async def run_sweep_once(now: datetime) -> int:
    """Một vòng quét. Gate OFF → 0. Lọc thô status phía-AI, rồi classify_idle từng ca."""
    try:
        snap = await gate_service.get_gate_config()
    except Exception as exc:  # noqa: BLE001 — không đọc được gate → an toàn: không đóng gì.
        log.warning("auto-resolve read gate failed (skip vòng): %s", exc)
        return 0
    if not snap.auto_resolve_enabled:
        return 0

    acted = 0
    async with AsyncSessionLocal() as s:
        rows = list(
            (
                await s.execute(
                    select(Conversation).where(
                        Conversation.status.in_(tuple(_SWEEPABLE))
                    )
                )
            )
            .scalars()
            .all()
        )
        for conv in rows:
            action = classify_idle(
                status=conv.status,
                last_message_at=conv.last_message_at,
                reminded_at=conv.auto_resolve_reminded_at,
                now=now,
                t1_minutes=snap.auto_resolve_minutes,
                t2_minutes=snap.auto_resolve_grace_minutes,
            )
            if action is IdleAction.REMIND:
                conv.auto_resolve_reminded_at = now
                await s.commit()
                await conversation_service.send_auto_message(s, conv.id, content=REMIND_TEMPLATE)
                await _broadcast_ai(conv.id, REMIND_TEMPLATE)
                acted += 1
            elif action is IdleAction.RESOLVE:
                conv.status = ConversationStatus.RESOLVED
                await s.commit()
                await conversation_service.send_auto_message(s, conv.id, content=RESOLVE_TEMPLATE)
                await _broadcast_ai(conv.id, RESOLVE_TEMPLATE)
                acted += 1
    if acted:
        log.info("auto-resolve sweep: %d ca đã xử lý", acted)
    return acted


async def sweep_loop(stop: asyncio.Event) -> None:
    """Lặp mỗi sweep_interval_seconds tới khi stop set. Nuốt lỗi mỗi vòng (đừng để task chết)."""
    log.info("auto-resolve sweep loop bắt đầu (mỗi %ds)", settings.sweep_interval_seconds)
    while not stop.is_set():
        try:
            await run_sweep_once(datetime.now(timezone.utc))
        except Exception as exc:  # noqa: BLE001
            log.warning("auto-resolve sweep vòng lỗi (bỏ qua): %s", exc)
        try:
            await asyncio.wait_for(stop.wait(), timeout=settings.sweep_interval_seconds)
        except asyncio.TimeoutError:
            pass
    log.info("auto-resolve sweep loop dừng")
