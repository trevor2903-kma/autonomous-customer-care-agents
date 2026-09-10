"""Auto-resolve (09c) – tự nhắc rồi đóng ca phía-AI im lặng quá ngưỡng.

Lõi `classify_idle` THUẦN (offline-testable): route trên trạng thái + hai mức thời gian.
Sweep (I/O): lọc ứng viên trong MỘT session ngắn, rồi mỗi ca cần hành động chạy trong session NGẮN riêng — CAS + tin
nhắc/đóng CÙNG một transaction, commit rồi mới phát hub (audit v2, OPS-01.1/OPS-01.3).
Chỉ REPLIED/AWAITING_CUSTOMER; các trạng thái khác NOOP.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from enum import StrEnum

from sqlalchemy import or_, select, update
from sqlalchemy.sql import Select, Update

from ..api.ws.hub import hub
from ..core.config import settings
from ..core.database import AsyncSessionLocal
from ..core.logging import get_logger
from ..models.conversation import Conversation
from ..models.enums import ConversationStatus, MessageSender
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


def _build_candidate_stmt(*, now: datetime, t1_minutes: int, limit: int) -> Select:
    """Ứng viên sweep: CHỈ ca có thể cần hành động — im lặng ≥ T1 (chưa nhắc) HOẶC đã nhắc (để RESOLVE),
    giới hạn `limit` (sub-project A). Thu hẹp trong SQL để KHÔNG nạp mọi ca REPLIED/AWAITING_CUSTOMER mỗi vòng;
    `classify_idle` vẫn là trọng tài cuối trên từng row nên logic remind/resolve không đổi."""
    t1_cutoff = now - timedelta(minutes=t1_minutes)
    return (
        select(Conversation)
        .where(
            Conversation.status.in_(tuple(_SWEEPABLE)),
            or_(
                Conversation.last_message_at < t1_cutoff,
                Conversation.auto_resolve_reminded_at.is_not(None),
            ),
        )
        .order_by(Conversation.last_message_at.asc())  # ca im lặng lâu nhất trước
        .limit(limit)
    )


def _remind_stmt(conv_id, *, now: datetime, t1_minutes: int) -> Update:
    """CAS nhánh REMIND — guard: status vẫn _SWEEPABLE (chưa bị admin takeover), CHƯA nhắc, VÀ vẫn im lặng ≥ T1 đo
    trên CHÍNH row đang ghi (OPS-01.2): khách nhắn xen giữa lúc SELECT ứng viên và lúc ghi (tin khách đẩy
    `last_message_at`) → rowcount 0 → KHÔNG nhắc. Status + mốc đã-nhắc thôi thì không đủ: tin khách không đổi status."""
    return (
        update(Conversation)
        .where(
            Conversation.id == conv_id,
            Conversation.status.in_(tuple(_SWEEPABLE)),
            Conversation.auto_resolve_reminded_at.is_(None),
            Conversation.last_message_at <= now - timedelta(minutes=t1_minutes),
        )
        .values(auto_resolve_reminded_at=now)
    )


def _resolve_stmt(conv_id) -> Update:
    """CAS nhánh RESOLVE — guard kép: status vẫn _SWEEPABLE (chưa bị admin takeover) VÀ mốc đã-nhắc vẫn còn (chưa
    bị tin khách reset về None khi khách nhắn lại) — cả hai race đều tự loại ở đây."""
    return (
        update(Conversation)
        .where(
            Conversation.id == conv_id,
            Conversation.status.in_(tuple(_SWEEPABLE)),
            Conversation.auto_resolve_reminded_at.is_not(None),
        )
        .values(status=ConversationStatus.RESOLVED)
    )


async def _act(conv: Conversation, action: IdleAction, *, now: datetime, t1_minutes: int) -> bool:
    """Hành động trên MỘT ca, session NGẮN riêng: CAS + tin nhắc/đóng trong CÙNG một transaction (OPS-01.1) — hoặc cả
    hai cùng landing, hoặc cả hai cùng rollback và vòng sau thử lại sạch. Chỉ phát hub SAU commit. True = đã làm."""
    remind = action is IdleAction.REMIND
    stmt = _remind_stmt(conv.id, now=now, t1_minutes=t1_minutes) if remind else _resolve_stmt(conv.id)
    content = REMIND_TEMPLATE if remind else RESOLVE_TEMPLATE
    async with AsyncSessionLocal() as s:
        result = await s.execute(stmt)
        if result.rowcount != 1:
            return False  # bất biến đã đổi (admin takeover / khách vừa nhắn) → bỏ qua; đóng session = rollback
        # Tin hệ thống KHÔNG bump last_message_at: đồng hồ im-lặng của khách giữ nguyên để T2 đo đúng.
        message = await conversation_service.insert_message(
            s, conv.id, sender=MessageSender.AI, content=content, bump_activity=False
        )
        await s.commit()
    # Sole-egress: câu cố định (không LLM) tới khách + admin đang mở ca; hub lỗi KHÔNG chặn sweep (helper tự guard).
    await hub.notify_message(conv.id, sender=MessageSender.AI, content=content, message_id=message.id)
    if not remind:
        # Khách rời "đang chờ"/"đang kiểm tra"; màn admin + inbox cập nhật trạng thái đã đóng.
        await hub.notify_status(
            conv.id, status=ConversationStatus.RESOLVED, assigned_admin_id=conv.assigned_admin_id
        )
    return True


async def run_sweep_once(now: datetime) -> int:
    """Một vòng quét. Gate OFF → 0. Lọc ứng viên (im lặng ≥ T1 hoặc đã nhắc, LIMIT), rồi classify_idle từng ca."""
    try:
        snap = await gate_service.get_gate_config()
    except Exception as exc:  # noqa: BLE001 — không đọc được gate → an toàn: không đóng gì.
        log.warning("auto-resolve read gate failed (skip vòng): %s", exc)
        return 0
    if not snap.auto_resolve_enabled:
        return 0

    async with AsyncSessionLocal() as s:
        rows = list(
            (
                await s.execute(
                    _build_candidate_stmt(
                        now=now,
                        t1_minutes=snap.auto_resolve_minutes,
                        limit=settings.sweep_batch_limit,
                    )
                )
            )
            .scalars()
            .all()
        )
    # Session ứng viên đã đóng — KHÔNG giữ một connection Neon suốt cả batch (OPS-01.3). Các cột đã nạp đủ nên đọc
    # thuộc tính của object (đã tách khỏi session) vẫn an toàn, không lazy-load.
    acted = 0
    for conv in rows:
        try:
            action = classify_idle(
                status=conv.status,
                last_message_at=conv.last_message_at,
                reminded_at=conv.auto_resolve_reminded_at,
                now=now,
                t1_minutes=snap.auto_resolve_minutes,
                t2_minutes=snap.auto_resolve_grace_minutes,
            )
            if action is not IdleAction.NOOP and await _act(
                conv, action, now=now, t1_minutes=snap.auto_resolve_minutes
            ):
                acted += 1
        except Exception as exc:  # noqa: BLE001 — cô lập 1 ca lỗi (CAS đã rollback cùng tin), KHÔNG làm hỏng vòng quét.
            log.warning("auto-resolve sweep: ca %s lỗi (bỏ qua): %s", conv.id, exc)
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
