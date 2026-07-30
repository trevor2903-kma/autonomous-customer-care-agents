"""Routes Báo cáo (slice obs P2) — đọc + tổng hợp `audit_log`.

**Nguồn dữ liệu là `audit_log` (Postgres), KHÔNG phải Langfuse.** Langfuse là observability cấp LLM có
dashboard riêng (P3); tab Báo cáo phải chạy được cả khi không cấu hình Langfuse, nên chỉ link sang.

Chỉ ĐỌC — không route nào ở đây đổi trạng thái hội thoại hay đụng pipeline.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query

from ...models.enums import AuditNode
from ...schemas.report import (
    IntentRowOut,
    RagSourceOut,
    SummaryOut,
    TurnDetailOut,
    TurnListItemOut,
    TurnListOut,
    TurnStepOut,
)
from ...services import report_service
from ..deps import require_admin

router = APIRouter(prefix="/admin/reports", tags=["reports"], dependencies=[Depends(require_admin)])

_RANGE = Query(default="7d", pattern="^(today|7d|all)$", description="today | 7d | all")
_RESULT = Query(default="all", pattern="^(all|auto|draft|handoff)$", description="lọc theo kết cục")


def _item(view) -> TurnListItemOut:
    return TurnListItemOut(
        turn_id=str(view.turn_id),
        short_id=view.short_id,
        created_at=view.created_at,
        conversation_id=str(view.conversation_id) if view.conversation_id else None,
        customer_text=view.customer_text,
        intent=view.intent,
        agent_action=view.agent_action,
        outcome=view.outcome,
        duration_ms=view.duration_ms,
        flags=view.flags,
    )


@router.get("/summary", response_model=SummaryOut)
async def summary(range: str = _RANGE) -> SummaryOut:
    """KPI tổng: %auto/%duyệt/%chuyển người/%fallback · độ trễ avg/p50/p95 · %≤NFR-1 · lý do escalate."""
    turns = await report_service.fetch_turns(range)
    return SummaryOut(range=range, since=report_service.range_start(range), **report_service.summarize(turns))


@router.get("/by-intent", response_model=list[IntentRowOut])
async def by_intent(range: str = _RANGE) -> list[IntentRowOut]:
    turns = await report_service.fetch_turns(range)
    return [IntentRowOut(**row) for row in report_service.summarize_by_intent(turns)]


@router.get("/turns", response_model=TurnListOut)
async def turns(
    range: str = _RANGE,
    result: str = _RESULT,
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> TurnListOut:
    total, views = await report_service.fetch_turn_page(range, result=result, limit=limit, offset=offset)
    return TurnListOut(total=total, limit=limit, offset=offset, items=[_item(v) for v in views])


@router.get("/turns/{turn_id}", response_model=TurnDetailOut)
async def turn_detail(turn_id: uuid.UUID) -> TurnDetailOut:
    """Drill-down một lượt: 4 bước agent + 2 sự kiện bao quanh, kèm `duration_ms` từng bước."""
    rows = await report_service.fetch_turn_steps(turn_id)
    if not rows:
        raise HTTPException(status_code=404, detail="Không thấy lượt này trong nhật ký kiểm toán.")

    view = report_service.build_turn_view(rows)
    if view is None:
        raise HTTPException(status_code=409, detail="Lượt chưa hoàn tất (thiếu bước giao kết quả).")

    by_node = {r.node: r for r in rows}
    knowledge = by_node.get(AuditNode.KNOWLEDGE)
    response = by_node.get(AuditNode.RESPONSE)
    return TurnDetailOut(
        turn_id=str(view.turn_id),
        short_id=view.short_id,
        conversation_id=str(view.conversation_id) if view.conversation_id else None,
        created_at=view.created_at,
        customer_text=view.customer_text,
        intent=view.intent,
        agent_action=view.agent_action,
        outcome=view.outcome,
        priority=view.priority,
        severity=view.severity,
        escalation_reason=view.escalation_reason,
        total_ms=view.duration_ms,
        steps=[
            TurnStepOut(
                node=r.node or "",
                action=r.action,
                confidence=r.confidence,
                duration_ms=r.duration_ms,
                flags=list(r.uncertainty_flags or []),
                escalation_reason=r.escalation_reason,
                detail=r.detail or {},
                created_at=r.created_at,
            )
            for r in rows
        ],
        rag_sources=[
            RagSourceOut(**src) for src in ((knowledge.detail or {}).get("rag_sources") or [])
        ] if knowledge is not None else [],
        reply_preview=((response.detail or {}).get("reply_preview") if response is not None else None),
    )
