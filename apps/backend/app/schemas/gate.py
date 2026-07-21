"""Pydantic schemas — Gate config (slice 11 P3, admin).

`GET` trả kèm `retrieval_threshold` (chỉ hiển thị read-only); `PUT` KHÔNG nhận nó (plan §4).
Per-intent chỉ chỉnh được `send_directly` (label/sensitive cố định theo seed).
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class GateIntentRuleSchema(BaseModel):
    intent: str
    label: str
    sensitive: bool
    send_directly: bool


class GateConfigOut(BaseModel):
    auto_reply_enabled: bool
    auto_resolve_enabled: bool
    auto_resolve_minutes: int
    retrieval_threshold: float  # READ-ONLY hiển thị (P3-b hoãn — Agent 2 vẫn đọc env)
    rules: list[GateIntentRuleSchema]


class GateIntentRuleUpdate(BaseModel):
    intent: str
    send_directly: bool


class GateConfigUpdate(BaseModel):
    """PUT — mọi field optional (chỉ cập nhật field gửi lên). KHÔNG có retrieval_threshold."""

    auto_reply_enabled: bool | None = None
    auto_resolve_enabled: bool | None = None
    auto_resolve_minutes: int | None = Field(default=None, ge=1)
    rules: list[GateIntentRuleUpdate] | None = None
