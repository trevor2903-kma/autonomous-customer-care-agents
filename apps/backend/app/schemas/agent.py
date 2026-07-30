"""Pydantic schemas — agent trace / run-demo (khớp shared-types AgentTraceStep)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class AgentTraceStep(BaseModel):
    node: str
    confidence: float | None = None
    branch: str | None = None
    detail: dict[str, Any] = {}
    duration_ms: int | None = None  # observability P1 (lớp bọc `_observed` đo)
    flags: list[str] = []  # cờ MỚI của riêng node này (khác tập cờ gộp cuối lượt)


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
    # Câu test cho /analyze (Agent 1 + Agent 2).
    message: str


class AnalyzeResult(BaseModel):
    # Agent 1 (intent/entities) + Agent 2 (rag_contexts) — cho thấy TÁCH VAI. Metadata (KHÔNG phải câu trả lời khách).
    intent: str  # Agent 1
    category: str | None = None  # Agent 1
    entities: dict[str, Any] = {}  # Agent 1
    intent_confidence: float  # Agent 1
    retrieval_confidence: float  # Agent 2
    uncertainty_flags: list[str] = []  # gộp cờ Agent 1 + Agent 2
    rag_contexts: list[dict[str, Any]] = []  # Agent 2
