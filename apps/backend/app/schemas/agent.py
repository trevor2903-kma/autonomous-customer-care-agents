"""Pydantic schemas — công cụ dev `/agents/analyze` (Agent 1 + Agent 2)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ..core.config import settings


class ClassifyRequest(BaseModel):
    # Câu test cho /analyze (Agent 1 + Agent 2). Chặn như biên WS (SEC-XC.1): tối đa `max_message_chars`
    # (không nhồi cả megabyte vào prompt); rỗng / chỉ khoảng trắng → 422.
    model_config = ConfigDict(str_strip_whitespace=True)

    message: str = Field(min_length=1, max_length=settings.max_message_chars)


class AnalyzeResult(BaseModel):
    # Agent 1 (intent/entities) + Agent 2 (rag_contexts) — cho thấy TÁCH VAI. Metadata (KHÔNG phải câu trả lời khách).
    intent: str  # Agent 1
    category: str | None = None  # Agent 1
    entities: dict[str, Any] = {}  # Agent 1
    intent_confidence: float  # Agent 1
    retrieval_confidence: float  # Agent 2
    uncertainty_flags: list[str] = []  # gộp cờ Agent 1 + Agent 2
    rag_contexts: list[dict[str, Any]] = []  # Agent 2
