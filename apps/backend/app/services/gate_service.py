"""Gate động (slice 11 P3) — đọc/ghi cấu hình gate từ DB (thay env), cache nhẹ TTL (1 worker).

§4: gate = VAN cho nhánh auto_reply (status REPLIED). Escalation an toàn (blocking flags của Agent 3 →
human_handoff) KHÔNG đọc gate, KHÔNG toggle. `retrieval_threshold` chỉ để hiển thị read-only slice này
(Agent 2 VẪN đọc env — P3-b hoãn); `update_gate_config` KHÔNG nhận nó.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

from sqlalchemy import select

from ..core.database import AsyncSessionLocal
from ..core.logging import get_logger
from ..models.enums import ConversationStatus
from ..models.gate_config import GateConfig
from ..models.gate_intent_rule import GateIntentRule

log = get_logger("gate")

_TTL_SECONDS = 5.0
_GATE_CONFIG_ID = 1

# Thứ tự hiển thị bảng per-intent (plan §3.3) — KHÔNG theo alphabet.
_INTENT_ORDER = [
    "product_price",
    "product_information",
    "size_consulting",
    "shipping",
    "order_status",
    "promotion",
    "refund",
    "exchange",
    "complaint",
    "other",
]
_ORDER_INDEX = {name: i for i, name in enumerate(_INTENT_ORDER)}


@dataclass(frozen=True)
class GateIntentRuleView:
    intent: str
    label: str
    sensitive: bool
    send_directly: bool


@dataclass(frozen=True)
class GateSnapshot:
    auto_reply_enabled: bool
    auto_resolve_enabled: bool
    auto_resolve_minutes: int
    retrieval_threshold: float
    rules: tuple[GateIntentRuleView, ...]

    def send_directly_for(self, intent: str | None) -> bool:
        for r in self.rules:
            if r.intent == intent:
                return r.send_directly
        return False  # intent không có luật → coi như KHÔNG gửi thẳng (giữ nháp — an toàn)


_cache: GateSnapshot | None = None
_cache_at: float = 0.0


def _invalidate() -> None:
    global _cache
    _cache = None


async def _load_snapshot() -> GateSnapshot:
    async with AsyncSessionLocal() as s:
        cfg = await s.get(GateConfig, _GATE_CONFIG_ID)
        rules = list((await s.execute(select(GateIntentRule))).scalars().all())
    if cfg is None:
        raise RuntimeError("gate_config (id=1) chưa có — chạy migration seed")
    rules.sort(key=lambda r: _ORDER_INDEX.get(r.intent, len(_ORDER_INDEX)))
    return GateSnapshot(
        auto_reply_enabled=cfg.auto_reply_enabled,
        auto_resolve_enabled=cfg.auto_resolve_enabled,
        auto_resolve_minutes=cfg.auto_resolve_minutes,
        retrieval_threshold=cfg.retrieval_threshold,
        rules=tuple(
            GateIntentRuleView(intent=r.intent, label=r.label, sensitive=r.sensitive, send_directly=r.send_directly)
            for r in rules
        ),
    )


async def get_gate_config(*, force: bool = False) -> GateSnapshot:
    """Snapshot cấu hình gate (cache TTL). Raise nếu DB lỗi/thiếu seed — call-site quyết định fallback."""
    global _cache, _cache_at
    now = time.monotonic()
    if not force and _cache is not None and (now - _cache_at) < _TTL_SECONDS:
        return _cache
    snap = await _load_snapshot()
    _cache = snap
    _cache_at = now
    return snap


def holds_auto_reply(snapshot: GateSnapshot, status_out: str | None, intent: str | None) -> bool:
    """§4 (thuần, offline-testable): auto_reply (REPLIED) qua van gate.

    master TẮT → giữ nháp TẤT CẢ; else giữ nếu intent KHÔNG "gửi thẳng". Escalation an toàn
    (human_handoff, status IN_HUMAN_QUEUE) KHÔNG đi qua đây.
    """
    if status_out != ConversationStatus.REPLIED:
        return False
    if not snapshot.auto_reply_enabled:
        return True
    return not snapshot.send_directly_for(intent)


async def update_gate_config(
    *,
    auto_reply_enabled: bool | None = None,
    auto_resolve_enabled: bool | None = None,
    auto_resolve_minutes: int | None = None,
    rules: list[tuple[str, bool]] | None = None,
) -> GateSnapshot:
    """Cập nhật toggle hệ thống + `send_directly` per-intent. KHÔNG nhận retrieval_threshold (§4). Invalidate cache.

    Chỉ cập nhật intent ĐÃ CÓ luật (tập đóng) — bỏ qua intent lạ.
    """
    async with AsyncSessionLocal() as s:
        cfg = await s.get(GateConfig, _GATE_CONFIG_ID)
        if cfg is None:
            raise RuntimeError("gate_config (id=1) chưa có — chạy migration seed")
        if auto_reply_enabled is not None:
            cfg.auto_reply_enabled = auto_reply_enabled
        if auto_resolve_enabled is not None:
            cfg.auto_resolve_enabled = auto_resolve_enabled
        if auto_resolve_minutes is not None:
            cfg.auto_resolve_minutes = auto_resolve_minutes
        if rules:
            existing = {r.intent: r for r in (await s.execute(select(GateIntentRule))).scalars().all()}
            for intent, send_directly in rules:
                rule = existing.get(intent)
                if rule is not None:
                    rule.send_directly = send_directly
        await s.commit()
    _invalidate()
    return await get_gate_config(force=True)
