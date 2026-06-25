"""ConversationState — state điều phối pipeline (LangGraph).

Chừa sẵn chỗ kiến trúc cho 4 trụ cột (PRD §5) và xử lý bất đồng bộ/chuyển tiếp (PRD §10):
- An toàn/bất định: confidence, uncertainty_flags, escalation_reason, require_human_handoff.
- Trường CSKH (PRD §7): intent, entities, rag_contexts, action, draft_reply, awaiting_customer.

Scaffold: node chỉ set giá trị stub; KHÔNG logic thật.
"""

from __future__ import annotations

from operator import add
from typing import Annotated, Any, TypedDict


class ConversationState(TypedDict, total=False):
    # ── Lõi điều phối ─────────────────────────────────────────────────────────
    conversation_id: str | None
    input: str
    scratchpad: dict[str, Any]
    messages: Annotated[list[dict[str, Any]], add]  # append-only (tin nhắn hội thoại)
    trace: Annotated[list[dict[str, Any]], add]  # append-only (agent-trace: node/confidence/branch)
    status: str
    result: dict[str, Any] | None
    error: str | None

    # ── Chừa chỗ an toàn/bất định (PRD §5 trụ cột 3, §7.3) ────────────────────
    confidence: float
    uncertainty_flags: list[str]
    escalation_reason: str | None
    require_human_handoff: bool

    # ── Trường CSKH (PRD §7) ──────────────────────────────────────────────────
    intent: str | None
    entities: dict[str, Any]
    rag_contexts: list[dict[str, Any]]
    action: str | None  # auto_reply | human_handoff (Decision Engine, PRD §7.3)
    draft_reply: str | None
    awaiting_customer: bool  # PRD §10 FR-ASYNC-2 (clarification)
