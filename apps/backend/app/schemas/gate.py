"""Pydantic schemas — Gate config (slice 11 P3, admin).

Per-intent chỉ chỉnh được `send_directly` (label/sensitive cố định theo seed).
KHÔNG có `retrieval_threshold`: ngưỡng truy hồi thuộc `settings` (giá trị ĐO), không phải cấu hình UI.
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
    rules: list[GateIntentRuleSchema]


class GateIntentRuleUpdate(BaseModel):
    intent: str
    send_directly: bool


class GateConfigUpdate(BaseModel):
    """PUT — mọi field optional (chỉ cập nhật field gửi lên)."""

    auto_reply_enabled: bool | None = None
    auto_resolve_enabled: bool | None = None
    auto_resolve_minutes: int | None = Field(default=None, ge=1)
    rules: list[GateIntentRuleUpdate] | None = None
