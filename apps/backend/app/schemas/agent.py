"""Pydantic schemas — agent trace / run-demo (khớp shared-types AgentTraceStep)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class AgentTraceStep(BaseModel):
    node: str
    confidence: float | None = None
    branch: str | None = None
    detail: dict[str, Any] = {}


class RunDemoResult(BaseModel):
    thread_id: str
    branch: str  # response | human_handoff
    status: str
    action: str | None = None
    confidence: float | None = None
    require_human_handoff: bool = False
    escalation_reason: str | None = None
    reply: str | None = None
    trace: list[AgentTraceStep] = []


class ClassifyRequest(BaseModel):
    # Điểm test Agent 1 (Intent Classifier) — chạy RIÊNG bước intent, KHÔNG cả pipeline.
    message: str


class ClassifyResult(BaseModel):
    # Agent 1 SẠCH (PRD §7.1): metadata phân loại — KHÔNG rag_contexts (đó là của Agent 2, §7.2).
    intent: str
    category: str | None = None
    entities: dict[str, Any] = {}
    confidence: float
    uncertainty_flags: list[str] = []
