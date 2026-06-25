"""Node 1 — Intent Classifier (STUB). PRD §7.1."""

from __future__ import annotations

from typing import Any

from ...models.enums import ConversationStatus
from ..state import ConversationState


def intent_node(state: ConversationState) -> dict[str, Any]:
    # STUB: KHÔNG phân loại intent thật (ENABLE_LLM=false). Pass-through + giá trị stub.
    # TODO (PRD §7.1): LLM phân loại intent+category, trích entities -> JSON; cờ ambiguous_intent /
    #   multi_intent / out_of_domain. Tự trị: hỏi lại tối đa 1 lần (clarification) -> AWAITING_CUSTOMER
    #   (PRD §10 FR-ASYNC-2).
    return {
        "status": ConversationStatus.CLASSIFYING,
        "intent": "unknown",
        "entities": {},
        "confidence": 1.0,
        "uncertainty_flags": [],
        "trace": [{"node": "intent", "confidence": 1.0, "branch": None, "detail": {"stub": True}}],
    }
