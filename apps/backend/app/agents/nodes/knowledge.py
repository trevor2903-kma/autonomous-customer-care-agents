"""Node 2 — Knowledge Agent / RAG (PRD §7.2, §13). Truy hồi tri thức từ KHO TRI THỨC (chính sách/FAQ/sản phẩm).

- `retrieve_knowledge(query)` = hàm THUẦN (tái dùng): gọi `rag_service.search` (tầng service) → `rag_contexts`
  (text+source+score) + `retrieval_confidence` + cờ. Đây là VAI của Agent 2 (Agent 1 KHÔNG retrieval nữa).
- Cờ Agent 2: `no_relevant_knowledge` (không tri thức) / `low_retrieval_score` (điểm thấp).
- Grounding (PRD §5 trụ cột 3, FR-PIPE-5): Agent 2 chỉ PHÁT cờ; Decision Engine (sau) đọc cờ → human_handoff
  nếu không có tri thức. Agent 2 KHÔNG tự quyết.
- Degrade AN TOÀN offline: thiếu key / Qdrant lỗi / collection trống / không hits → `rag_contexts=[]`,
  `retrieval_confidence=0.0`, `["no_relevant_knowledge"]` (KHÔNG network vô ích, KHÔNG ném lỗi) → `make test` offline.
"""

from __future__ import annotations

from typing import Any

from ...core.config import settings
from ...core.logging import get_logger
from ...models.enums import ConversationStatus
from ...services import rag_service
from ..state import ConversationState

log = get_logger("agent.knowledge")

# Lượt KHÔNG cần tri thức: xã giao không phát biểu sự thật nào → không có gì để "không grounded".
# Bỏ qua retrieval và KHÔNG phát cờ grounding (nếu phát, Agent 3 sẽ escalate một lời chào — lỗi cũ).
# Đây là KHOANH PHẠM VI grounding, KHÔNG phải nới lỏng: Agent 3 giữ nguyên, BLOCKING_FLAGS không đổi.
NO_RETRIEVAL_INTENTS: frozenset[str] = frozenset({"greeting"})


def _degrade(flags: list[str]) -> dict[str, Any]:
    return {"rag_contexts": [], "retrieval_confidence": 0.0, "uncertainty_flags": flags}


async def retrieve_knowledge(query: str, top_k: int = 4, intent: str | None = None) -> dict[str, Any]:
    """Truy hồi tri thức cho `query`, ưu tiên chunk cùng `intent`. Trả
    {rag_contexts, retrieval_confidence, uncertainty_flags}."""
    if intent in NO_RETRIEVAL_INTENTS:
        return _degrade([])  # rỗng nhưng KHÔNG cờ — Agent 4 trả câu chào mẫu (P5)

    # Thiếu key -> không embed/search được -> degrade (không network).
    if not settings.llm_api_key:
        return _degrade(["no_relevant_knowledge"])

    try:
        hits = await rag_service.search(query, top_k, intent=intent)
    except Exception as exc:  # noqa: BLE001 — Qdrant/embed lỗi / collection chưa có -> degrade, KHÔNG ném.
        log.warning("knowledge.search failed -> degrade no_relevant_knowledge: %s", exc)
        return _degrade(["no_relevant_knowledge"])

    if not hits:
        return _degrade(["no_relevant_knowledge"])

    # `type`/`title` để Agent 4 gắn nhãn loại tri thức (quy trình xử lý vs tra cứu) — plan §2.5/§3-P5.
    rag_contexts = [
        {
            "text": h.get("text"),
            "source": h.get("source"),
            "type": h.get("type"),
            "title": h.get("title"),
            "score": round(float(h["score"]), 4),
        }
        for h in hits
    ]
    retrieval_confidence = float(hits[0]["score"])
    flags: list[str] = []
    # Ngưỡng RIÊNG cho cosine (retrieval_threshold) — KHÔNG dùng confidence_threshold (thang intent LLM).
    if retrieval_confidence < settings.retrieval_threshold:
        flags.append("low_retrieval_score")

    return {
        "rag_contexts": rag_contexts,
        "retrieval_confidence": retrieval_confidence,
        "uncertainty_flags": flags,
    }


async def knowledge_node(state: ConversationState) -> dict[str, Any]:
    """Node graph: retrieve_knowledge trên input (ưu tiên intent của Agent 1) rồi ghi state + trace.
    Ghi `rag_contexts` (VAI Agent 2) + `retrieval_confidence`; `uncertainty_flags` tích luỹ (reducer add)."""
    intent = state.get("intent")
    result = await retrieve_knowledge(state.get("input", ""), intent=intent)
    return {
        "status": ConversationStatus.RETRIEVING,
        "rag_contexts": result["rag_contexts"],
        "retrieval_confidence": result["retrieval_confidence"],
        "uncertainty_flags": result["uncertainty_flags"],
        "trace": [
            {
                "node": "knowledge",
                "confidence": result["retrieval_confidence"],
                "branch": None,
                # `skipped` để audit thấy RÕ lượt xã giao không retrieve (khác với retrieve xong rỗng).
                "detail": {
                    "contexts": len(result["rag_contexts"]),
                    "intent": intent,
                    "skipped": intent in NO_RETRIEVAL_INTENTS,
                },
            }
        ],
    }
