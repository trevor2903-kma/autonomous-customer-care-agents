"""Tổng hợp báo cáo từ `audit_log` (slice obs P2) — NGUỒN của tab Báo cáo.

Kiến trúc: **truy vấn mỏng + tổng hợp thuần**.
- `fetch_*` chỉ lấy dòng cần trong khoảng thời gian.
- `build_turn_view` gộp các dòng CÙNG `turn_id` thành một cái nhìn về LƯỢT; mọi phép tính KPI sau đó
  chạy trên `list[TurnView]` bằng hàm THUẦN → test offline được, không cần DB.

Vì sao gộp theo lượt thay vì tính thẳng bằng SQL: một KPI như "%auto theo intent" phải nối dòng
`delivery` (kết cục) với `intent` (nhãn) của CÙNG lượt; viết bằng SQL thì thành nhiều self-join mà
vẫn không kiểm thử được. Dữ liệu cỡ báo cáo nội bộ nên gộp ở Python là đủ và rõ ràng hơn nhiều.

Dòng audit CŨ (task nền REST, trước slice này) KHÔNG có `turn_id` → bị loại khỏi mọi truy vấn: chúng
không thuộc lượt khách nào và sẽ làm lệch mọi tỉ lệ.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import func, select

from ..core.config import settings
from ..core.database import AsyncSessionLocal
from ..models.audit_log import AuditLog
from ..models.enums import AuditNode, TurnOutcome

# Khoảng thời gian hợp lệ cho tham số `range`.
RANGES = ("today", "7d", "all")
# Bộ lọc kết quả ở danh sách lượt (khớp nhãn UI).
RESULT_FILTERS: dict[str, str | None] = {
    "all": None,
    "auto": TurnOutcome.SENT,
    "draft": TurnOutcome.HELD_FOR_APPROVAL,
    "handoff": TurnOutcome.QUEUED_FOR_HUMAN,
}
# Cờ đánh dấu Agent 4 phải dùng câu FALLBACK (không đủ tri thức) — khác với escalate của Agent 3.
_FALLBACK_FLAG = "hallucination_risk"


def range_start(range_key: str) -> datetime | None:
    """Mốc bắt đầu (UTC) của khoảng. `all` → None. `today` = nửa đêm theo giờ địa phương shop."""
    now = datetime.now(UTC)
    if range_key == "7d":
        return now - timedelta(days=7)
    if range_key == "today":
        offset = timedelta(hours=settings.reports_tz_offset_hours)
        local_midnight = (now + offset).replace(hour=0, minute=0, second=0, microsecond=0)
        return local_midnight - offset
    return None


# ── Cái nhìn về MỘT LƯỢT (thuần, dựng từ các dòng audit cùng turn_id) ─────────
@dataclass(frozen=True)
class TurnView:
    turn_id: uuid.UUID
    conversation_id: uuid.UUID | None
    created_at: datetime
    customer_text: str
    intent: str | None
    outcome: str
    agent_action: str | None  # quyết định Agent 3 (auto_reply|human_handoff)
    priority: str | None
    severity: str | None
    duration_ms: int | None  # end-to-end cả lượt
    confidence: float | None  # retrieval_confidence
    flags: list[str] = field(default_factory=list)
    escalation_reason: str | None = None
    blocking_flags: list[str] = field(default_factory=list)
    fallback: bool = False

    @property
    def short_id(self) -> str:
        return f"trc_{str(self.turn_id)[:8]}"


def build_turn_view(rows: list[AuditLog]) -> TurnView | None:
    """Gộp các dòng CÙNG lượt thành `TurnView`. Không có dòng `delivery` → lượt chưa hoàn tất → bỏ.

    (Lượt dở dang = tiến trình chết giữa chừng; đếm nó vào KPI sẽ bịa ra kết cục không có thật.)
    """
    by_node = {r.node: r for r in rows}
    delivery = by_node.get(AuditNode.DELIVERY)
    if delivery is None:
        return None

    detail = delivery.detail or {}
    decision = by_node.get(AuditNode.DECISION)
    response = by_node.get(AuditNode.RESPONSE)
    return TurnView(
        turn_id=delivery.turn_id,
        conversation_id=delivery.conversation_id,
        created_at=delivery.created_at,
        customer_text=detail.get("customer_text") or "",
        intent=detail.get("intent"),
        outcome=str(delivery.action or ""),
        agent_action=detail.get("agent_action"),
        priority=detail.get("priority"),
        severity=detail.get("severity"),
        duration_ms=delivery.duration_ms,
        confidence=delivery.confidence,
        flags=list(delivery.uncertainty_flags or []),
        escalation_reason=(decision.escalation_reason if decision is not None else None),
        blocking_flags=list(((decision.detail or {}).get("blocking_flags") or []) if decision else []),
        fallback=_FALLBACK_FLAG in list((response.uncertainty_flags or []) if response else []),
    )


def group_turns(rows: list[AuditLog]) -> list[TurnView]:
    """Nhóm dòng theo `turn_id` → danh sách lượt, mới nhất trước."""
    buckets: dict[uuid.UUID, list[AuditLog]] = {}
    for row in rows:
        if row.turn_id is not None:
            buckets.setdefault(row.turn_id, []).append(row)
    views = [v for v in (build_turn_view(rs) for rs in buckets.values()) if v is not None]
    views.sort(key=lambda v: v.created_at, reverse=True)
    return views


# ── Phép tính KPI (thuần) ────────────────────────────────────────────────────
def percentile(values: list[int], pct: float) -> int | None:
    """Phân vị theo NEAREST-RANK (không nội suy) — với n nhỏ, nội suy tạo ra con số không tồn tại."""
    if not values:
        return None
    ordered = sorted(values)
    rank = max(1, min(len(ordered), int(-(-pct * len(ordered) // 100))))  # ceil
    return ordered[rank - 1]


def _pct(part: int, total: int) -> float:
    return round(100.0 * part / total, 1) if total else 0.0


def summarize(turns: list[TurnView]) -> dict[str, Any]:
    """KPI tổng: tỉ lệ kết cục · fallback · độ trễ (avg/p50/p95, %≤NFR-1) · bóc tách lý do escalate."""
    total = len(turns)
    counts = {o: 0 for o in (TurnOutcome.SENT, TurnOutcome.HELD_FOR_APPROVAL,
                             TurnOutcome.QUEUED_FOR_HUMAN, TurnOutcome.ERROR)}
    for t in turns:
        if t.outcome in counts:
            counts[t.outcome] += 1

    latencies = [t.duration_ms for t in turns if t.duration_ms is not None]
    within = sum(1 for ms in latencies if ms <= settings.nfr_latency_ms)

    # Lý do escalate: đếm theo CỜ CHẶN thật (dòng decision), không phải theo chuỗi escalation_reason —
    # một lượt có thể bị chặn bởi nhiều cờ, và cờ mới là thứ định tuyến.
    reasons: dict[str, int] = {}
    escalated = [t for t in turns if t.outcome == TurnOutcome.QUEUED_FOR_HUMAN]
    for t in escalated:
        for flag in t.blocking_flags or ["(không rõ)"]:
            reasons[flag] = reasons.get(flag, 0) + 1

    return {
        "turns": total,
        "outcomes": {str(k): v for k, v in counts.items()},
        "auto_reply_pct": _pct(counts[TurnOutcome.SENT], total),
        "draft_pct": _pct(counts[TurnOutcome.HELD_FOR_APPROVAL], total),
        "handoff_pct": _pct(counts[TurnOutcome.QUEUED_FOR_HUMAN], total),
        "error_pct": _pct(counts[TurnOutcome.ERROR], total),
        "fallback_pct": _pct(sum(1 for t in turns if t.fallback), total),
        "latency": {
            "avg_ms": round(sum(latencies) / len(latencies)) if latencies else None,
            "p50_ms": percentile(latencies, 50),
            "p95_ms": percentile(latencies, 95),
            "nfr_threshold_ms": settings.nfr_latency_ms,
            "within_nfr_pct": _pct(within, len(latencies)),
            "measured": len(latencies),
        },
        "escalation_reasons": [
            {"flag": flag, "count": n, "pct": _pct(n, len(escalated))}
            for flag, n in sorted(reasons.items(), key=lambda kv: kv[1], reverse=True)
        ],
    }


def summarize_by_intent(turns: list[TurnView]) -> list[dict[str, Any]]:
    """Mỗi intent: số lượt · %auto vs chuyển người · độ trễ TB · confidence TB. Nhiều lượt nhất lên đầu."""
    buckets: dict[str, list[TurnView]] = {}
    for t in turns:
        buckets.setdefault(t.intent or "(không rõ)", []).append(t)

    rows: list[dict[str, Any]] = []
    for intent, group in buckets.items():
        lat = [t.duration_ms for t in group if t.duration_ms is not None]
        conf = [t.confidence for t in group if t.confidence is not None]
        rows.append(
            {
                "intent": intent,
                "turns": len(group),
                "auto_pct": _pct(sum(1 for t in group if t.outcome == TurnOutcome.SENT), len(group)),
                "draft_pct": _pct(sum(1 for t in group if t.outcome == TurnOutcome.HELD_FOR_APPROVAL), len(group)),
                "handoff_pct": _pct(sum(1 for t in group if t.outcome == TurnOutcome.QUEUED_FOR_HUMAN), len(group)),
                "avg_latency_ms": round(sum(lat) / len(lat)) if lat else None,
                "avg_confidence": round(sum(conf) / len(conf), 4) if conf else None,
            }
        )
    rows.sort(key=lambda r: r["turns"], reverse=True)
    return rows


# ── Truy vấn ─────────────────────────────────────────────────────────────────
_AGG_NODES = (AuditNode.DELIVERY, AuditNode.DECISION, AuditNode.RESPONSE)


def _in_range(stmt, start: datetime | None):
    stmt = stmt.where(AuditLog.turn_id.isnot(None))
    return stmt.where(AuditLog.created_at >= start) if start else stmt


async def fetch_turns(range_key: str) -> list[TurnView]:
    """Lượt trong khoảng — chỉ lấy 3 loại dòng cần cho KPI (bỏ customer/intent/knowledge cho nhẹ)."""
    start = range_start(range_key)
    async with AsyncSessionLocal() as s:
        rows = list((await s.execute(
            _in_range(select(AuditLog).where(AuditLog.node.in_([str(n) for n in _AGG_NODES])), start)
        )).scalars().all())
    return group_turns(rows)


async def fetch_turn_page(
    range_key: str, result: str = "all", limit: int = 25, offset: int = 0
) -> tuple[int, list[TurnView]]:
    """Danh sách lượt gần đây (phân trang). Dòng `delivery` đã đủ mọi thứ danh sách cần → 1 truy vấn."""
    start = range_start(range_key)
    outcome = RESULT_FILTERS.get(result)

    base = select(AuditLog).where(AuditLog.node == str(AuditNode.DELIVERY))
    if outcome is not None:
        base = base.where(AuditLog.action == str(outcome))
    base = _in_range(base, start)

    async with AsyncSessionLocal() as s:
        total = (await s.execute(
            select(func.count()).select_from(base.subquery())
        )).scalar_one()
        rows = list((await s.execute(
            base.order_by(AuditLog.created_at.desc()).limit(limit).offset(offset)
        )).scalars().all())

    views = [v for v in (build_turn_view([r]) for r in rows) if v is not None]
    return total, views


async def fetch_turn_steps(turn_id: uuid.UUID) -> list[AuditLog]:
    """MỌI dòng của một lượt, theo thứ tự thời gian → drill-down 4 agent."""
    async with AsyncSessionLocal() as s:
        return list((await s.execute(
            select(AuditLog).where(AuditLog.turn_id == turn_id).order_by(AuditLog.created_at)
        )).scalars().all())
