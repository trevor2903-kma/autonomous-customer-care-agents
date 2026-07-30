"""Pydantic schemas — tab Báo cáo (slice obs P2). Nguồn: `audit_log` (KHÔNG phải Langfuse)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class LatencyOut(BaseModel):
    avg_ms: int | None = None
    p50_ms: int | None = None
    p95_ms: int | None = None
    nfr_threshold_ms: int  # ngưỡng NFR-1 (env `NFR_LATENCY_MS`)
    within_nfr_pct: float  # % lượt ≤ ngưỡng
    measured: int  # số lượt có số đo (mẫu của p50/p95)


class EscalationReasonOut(BaseModel):
    flag: str  # cờ CHẶN đã đẩy lượt sang người (vd low_retrieval_score)
    count: int
    pct: float  # % trong các lượt chuyển người


class SummaryOut(BaseModel):
    range: str
    since: datetime | None  # None = toàn bộ lịch sử
    turns: int
    outcomes: dict[str, int]
    auto_reply_pct: float
    draft_pct: float
    handoff_pct: float
    error_pct: float
    fallback_pct: float
    latency: LatencyOut
    escalation_reasons: list[EscalationReasonOut]


class IntentRowOut(BaseModel):
    intent: str
    turns: int
    auto_pct: float
    draft_pct: float
    handoff_pct: float
    avg_latency_ms: int | None = None
    avg_confidence: float | None = None


class TurnListItemOut(BaseModel):
    turn_id: str
    short_id: str  # trc_xxxxxxxx (hiển thị)
    created_at: datetime
    conversation_id: str | None = None
    customer_text: str
    intent: str | None = None
    agent_action: str | None = None
    outcome: str
    duration_ms: int | None = None
    flags: list[str] = []


class TurnListOut(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[TurnListItemOut]


class TurnStepOut(BaseModel):
    node: str  # customer|intent|knowledge|decision|response|delivery
    action: str | None = None
    confidence: float | None = None
    duration_ms: int | None = None
    flags: list[str] = []
    escalation_reason: str | None = None
    detail: dict[str, Any] = {}
    created_at: datetime


class RagSourceOut(BaseModel):
    source: str | None = None  # tệp `.md` trong knowledge/ (KHÔNG phải PDF)
    type: str | None = None
    title: str | None = None
    score: float | None = None


class TurnDetailOut(BaseModel):
    turn_id: str
    short_id: str
    conversation_id: str | None = None
    created_at: datetime
    customer_text: str
    intent: str | None = None
    agent_action: str | None = None
    outcome: str
    priority: str | None = None
    severity: str | None = None
    escalation_reason: str | None = None
    total_ms: int | None = None
    steps: list[TurnStepOut]
    rag_sources: list[RagSourceOut] = []
    reply_preview: str | None = None
