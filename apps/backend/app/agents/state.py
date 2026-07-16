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
    # ĐẦU VÀO chỉ-đọc (KHÔNG reducer): lịch sử hội thoại các lượt TRƯỚC (từ DB) để hiểu ngữ cảnh đa lượt —
    # KHÁC `messages` (output lượt này). Lịch sử KHÔNG thay `rag_contexts` (phanh chống bịa còn nguyên). PRD §12.
    history: list[dict[str, Any]]
    scratchpad: dict[str, Any]
    messages: Annotated[list[dict[str, Any]], add]  # append-only (tin nhắn hội thoại)
    trace: Annotated[list[dict[str, Any]], add]  # append-only (agent-trace: node/confidence/branch)
    status: str
    result: dict[str, Any] | None
    error: str | None

    # ── Chừa chỗ an toàn/bất định (PRD §5 trụ cột 3, §7.3) ────────────────────
    confidence: float
    intent_confidence: float  # Agent 1 — Intent Classifier (PRD §7.1)
    retrieval_confidence: float  # Agent 2 — Knowledge Agent (PRD §7.2)
    # TÍCH LUỸ (reducer add) như trace/messages — MỖI node chỉ trả CỜ MỚI của nó (nếu trả lại cờ cũ sẽ nhân đôi).
    uncertainty_flags: Annotated[list[str], add]
    escalation_reason: str | None
    require_human_handoff: bool

    # ── Trường CSKH (PRD §7) ──────────────────────────────────────────────────
    intent: str | None
    entities: dict[str, Any]
    rag_contexts: list[dict[str, Any]]
    action: str | None  # auto_reply | human_handoff (Decision Engine, PRD §7.3)
    priority: str | None  # low | medium | high (Decision Engine — theo intent, PRD §7.3)
    severity: str | None  # low | medium | high (Decision Engine — theo intent, PRD §7.3)
    draft_reply: str | None
    awaiting_customer: bool  # PRD §10 FR-ASYNC-2 (clarification)
