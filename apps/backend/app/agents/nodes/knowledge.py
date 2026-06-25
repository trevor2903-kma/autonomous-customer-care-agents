"""Node 2 — Knowledge Agent / RAG (STUB). PRD §7.2, §13."""

from __future__ import annotations

from typing import Any

from ...models.enums import ConversationStatus
from ..state import ConversationState


def knowledge_node(state: ConversationState) -> dict[str, Any]:
    # STUB: KHÔNG RAG thật (chưa embed/truy hồi Qdrant). rag_contexts rỗng.
    # TODO (PRD §7.2/§13): truy hồi tri thức từ Qdrant theo intent/entities -> contexts + điểm truy hồi;
    #   cờ no_relevant_knowledge / low_retrieval_score / stale_knowledge. Grounding: không có tri thức
    #   -> Decision Engine chuyển human_handoff, KHÔNG để Response bịa (PRD §14 FR-PIPE-5).
    return {
        "status": ConversationStatus.RETRIEVING,
        "rag_contexts": [],
        "confidence": 1.0,
        "trace": [
            {"node": "knowledge", "confidence": 1.0, "branch": None, "detail": {"stub": True, "contexts": 0}}
        ],
    }
