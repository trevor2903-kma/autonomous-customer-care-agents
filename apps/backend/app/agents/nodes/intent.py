"""Node 1 — Intent Classifier (PRD §7.1). Phân loại intent theo RAG (lát cắt walking-skeleton).

- `classify_intent(text)` = hàm THUẦN, tái dùng ở `/api/agents/classify` + WS. Trả METADATA phân loại
  (KHÔNG phải câu trả lời khách — Response Generator mới là điểm phát ngôn duy nhất, PRD §7.4).
- `intent_node(state)` bọc `classify_intent` vào graph (chỉ Agent 1 có logic thật; các node khác vẫn stub).
- Degrade AN TOÀN khi offline (thiếu key / Qdrant lỗi / collection trống) → `unknown` + `no_relevant_knowledge`,
  KHÔNG gọi network, KHÔNG ném lỗi → giữ `make test` chạy offline (plan §5).
- `ENABLE_LLM` chỉ gate BƯỚC CHỌN intent bằng LLM. Embeddings/RAG luôn chạy (không gate).
"""

from __future__ import annotations

import json
from typing import Any

from ...core.config import settings
from ...core.embeddings import get_openai
from ...core.logging import get_logger
from ...models.enums import ConversationStatus, Intent
from ...services import rag_service
from ..state import ConversationState

log = get_logger("agent.intent")

_VALID_INTENTS = {i.value for i in Intent}


def _degrade(reason: str) -> dict[str, Any]:
    """Kết quả an toàn khi không truy hồi được tri thức (không network / lỗi). Grounding: PRD §5 trụ cột 3."""
    return {
        "intent": "unknown",
        "category": None,
        "entities": {},
        "confidence": 0.0,
        "uncertainty_flags": ["no_relevant_knowledge"],
        "rag_contexts": [],
    }


def _contexts(hits: list[dict]) -> list[dict]:
    """Rút gọn hits thành rag_contexts nhẹ (intent + category + score) cho metadata."""
    return [
        {"intent": h["intent"], "category": h.get("category"), "score": round(float(h["score"]), 4)}
        for h in hits
    ]


def _category_for(intent: str, hits: list[dict]) -> str | None:
    for h in hits:
        if h["intent"] == intent:
            return h.get("category")
    return hits[0].get("category") if hits else None


def _classify_similarity(hits: list[dict]) -> dict[str, Any]:
    """Chọn intent = similarity top-1 (chế độ ENABLE_LLM=false hoặc fallback khi LLM lỗi)."""
    top = hits[0]
    intent = top["intent"] if top["intent"] in _VALID_INTENTS else "other"
    score = float(top["score"])

    flags: list[str] = []
    if score < settings.confidence_threshold:
        flags.append("low_retrieval_score")
    if intent == "other":
        flags.append("out_of_domain")
    if len(hits) > 1 and abs(score - float(hits[1]["score"])) < settings.intent_ambiguous_margin:
        flags.append("ambiguous_intent")

    return {
        "intent": intent,
        "category": top.get("category"),
        "entities": {},
        "confidence": score,
        "uncertainty_flags": flags,
        "rag_contexts": _contexts(hits),
    }


async def _classify_llm(text: str, hits: list[dict]) -> dict[str, Any]:
    """Chọn intent bằng LLM (ENABLE_LLM=true): dựa trên ứng viên RAG, chọn 1 intent + trích entities."""
    candidates = "\n".join(
        f"- {h['intent']} (category={h.get('category')}, score={float(h['score']):.3f}): "
        f"{(h.get('text') or '')[:400]}"
        for h in hits
    )
    system = (
        "Bạn là bộ phân loại intent cho CSKH shop quần áo. "
        "CHỈ chọn intent trong tập đóng: " + ", ".join(sorted(_VALID_INTENTS)) + ". "
        "Dựa trên các intent ứng viên (kèm mô tả/ví dụ truy hồi từ RAG) và câu của khách, chọn ĐÚNG 1 intent, "
        "trích entities nếu có (vd order_id, product_name, size), và cho confidence 0..1. "
        'Trả JSON: {"intent": <str>, "entities": {<key>: <value>}, "confidence": <float>}.'
    )
    user = f"Câu khách: {text!r}\n\nCác intent ứng viên (RAG):\n{candidates}"

    resp = await get_openai().chat.completions.create(
        model=settings.llm_model,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        response_format={"type": "json_object"},
        temperature=0,
    )
    data = json.loads(resp.choices[0].message.content or "{}")

    flags: list[str] = []
    # Chống trôi nhãn: intent phải ∈ Intent enum; lệch -> other + out_of_domain.
    raw_intent = str(data.get("intent", "")).strip()
    if raw_intent in _VALID_INTENTS:
        intent = raw_intent
    else:
        intent = "other"
        flags.append("out_of_domain")

    try:
        confidence = max(0.0, min(1.0, float(data.get("confidence"))))
    except (TypeError, ValueError):
        confidence = float(hits[0]["score"])

    entities = data.get("entities")
    if not isinstance(entities, dict):
        entities = {}

    top_score = float(hits[0]["score"])
    if len(hits) > 1 and abs(top_score - float(hits[1]["score"])) < settings.intent_ambiguous_margin:
        flags.append("ambiguous_intent")
    if intent == "other" and top_score < settings.confidence_threshold and "out_of_domain" not in flags:
        flags.append("out_of_domain")

    return {
        "intent": intent,
        "category": _category_for(intent, hits),
        "entities": entities,
        "confidence": confidence,
        "uncertainty_flags": flags,
        "rag_contexts": _contexts(hits),
    }


async def classify_intent(text: str) -> dict[str, Any]:
    """Phân loại intent của câu khách theo RAG. Trả {intent, category, entities, confidence,
    uncertainty_flags, rag_contexts}. Degrade an toàn khi offline (KHÔNG network, KHÔNG ném lỗi)."""
    # 1) Thiếu key -> không thể embed/search -> degrade ngay (không chạm network; giữ make test offline).
    if not settings.llm_api_key:
        return _degrade("no_llm_api_key")

    # 2) Truy hồi top-k ứng viên (tầng service — Knowledge Agent tái dùng, PRD §7.2).
    try:
        hits = await rag_service.search(text, top_k=3)
    except Exception as exc:  # noqa: BLE001 — Qdrant/embed lỗi -> degrade an toàn, KHÔNG ném.
        log.warning("intent.search failed -> degrade: %s", exc)
        return _degrade(f"search_error:{type(exc).__name__}")

    if not hits:
        return _degrade("no_hits")

    # 3) Chọn intent: LLM (nếu bật) hoặc similarity top-1.
    if settings.enable_llm:
        try:
            return await _classify_llm(text, hits)
        except Exception as exc:  # noqa: BLE001 — LLM lỗi -> fallback similarity (vẫn có hits RAG).
            log.warning("intent.llm failed -> similarity fallback: %s", exc)
    return _classify_similarity(hits)


async def intent_node(state: ConversationState) -> dict[str, Any]:
    """Node graph: chạy classify_intent rồi ghi vào state + trace. Chữ ký node giữ như cũ (PRD §7.1)."""
    result = await classify_intent(state.get("input", ""))
    return {
        "status": ConversationStatus.CLASSIFYING,
        "intent": result["intent"],
        "entities": result["entities"],
        "confidence": result["confidence"],
        "uncertainty_flags": result["uncertainty_flags"],
        "rag_contexts": result["rag_contexts"],
        "trace": [
            {
                "node": "intent",
                "confidence": result["confidence"],
                "branch": None,
                "detail": {"intent": result["intent"], "top": result["rag_contexts"]},
            }
        ],
    }
