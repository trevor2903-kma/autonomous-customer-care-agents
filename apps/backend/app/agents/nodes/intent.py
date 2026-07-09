"""Node 1 — Intent Classifier (PRD §7.1). Phân loại intent + trích ENTITIES theo RAG.

- Chunk truy hồi là GENERIC (không mang nhãn) → intent do **LLM** quyết (không còn similarity-top-1-nhãn).
- ENTITIES = LLM (schema + few-shot) ⊕ regex (`extract_entities_rule`), merge `{**rule, **llm}` (LLM đè, regex
  bù). Regex chạy MỌI nhánh (kể cả degrade) → `order_id` luôn bắt được (fix bug entities rỗng).
- `category` suy từ map tĩnh `INTENT_CATEGORY` (chunk generic không mang category).
- Degrade AN TOÀN khi offline/thiếu key/LLM lỗi → `intent="unknown"` + cờ (`llm_unavailable`/`search_error`/
  `no_relevant_knowledge`), KHÔNG network, KHÔNG ném lỗi → `make test` offline. Embeddings KHÔNG gate bởi ENABLE_LLM.
- `classify_intent` = hàm THUẦN (tái dùng ở /api/agents/classify + WS). Trả METADATA phân loại (KHÔNG phải câu
  trả lời khách — Response Generator mới phát ngôn, PRD §7.4).
"""

from __future__ import annotations

import json
from typing import Any

from ...core.config import settings
from ...core.embeddings import get_openai
from ...core.logging import get_logger
from ...models.enums import INTENT_CATEGORY, ConversationStatus, Intent
from ...services import rag_service
from ..state import ConversationState
from ._entities import extract_entities_rule

log = get_logger("agent.intent")

_VALID_INTENTS = {i.value for i in Intent}


def _degrade(rule: dict[str, str], flags: list[str], rag_contexts: list[dict] | None = None) -> dict[str, Any]:
    """Kết quả degrade an toàn. entities = regex (bù) — order_id không bị mất kể cả khi không có LLM."""
    return {
        "intent": "unknown",
        "category": None,
        "entities": dict(rule),
        "confidence": 0.0,
        "uncertainty_flags": flags,
        "rag_contexts": rag_contexts or [],
    }


def _rag_contexts(hits: list[dict]) -> list[dict]:
    return [{"source": h.get("source"), "score": round(float(h["score"]), 4)} for h in hits]


def _system_prompt() -> str:
    return (
        "Bạn là bộ phân loại intent + trích entities cho CSKH shop quần áo.\n"
        "1) CHỈ chọn intent trong tập đóng: " + ", ".join(sorted(_VALID_INTENTS)) + ".\n"
        "2) Trích entities theo schema THEO intent (giá trị là CHUỖI; KHÔNG bịa key ngoài schema):\n"
        "   - order_status/refund/exchange/complaint: order_id (chỉ chữ số)\n"
        "   - product_price/product_information: product_name, color\n"
        "   - size_consulting: height, weight, size\n"
        "   - shipping: destination (option: order_id)\n"
        "   - promotion: promo_code\n"
        "   - other: {}\n"
        "3) confidence trong [0,1].\n"
        'Trả JSON: {"intent": <str>, "entities": {<key>: <chuỗi>}, "confidence": <float>}.\n'
        "Ví dụ:\n"
        '- "Đơn hàng 6578 của tôi sắp giao tới nơi chưa?" -> '
        '{"intent":"order_status","entities":{"order_id":"6578"},"confidence":0.95}\n'
        '- "Mình cao 1m60 nặng 50kg mặc size gì?" -> '
        '{"intent":"size_consulting","entities":{"height":"1m60","weight":"50kg"},"confidence":0.9}'
    )


async def _classify_llm(text: str, hits: list[dict], rule: dict[str, str]) -> dict[str, Any]:
    """Chọn intent + trích entities bằng LLM, dựa trên ngữ cảnh RAG (chunk generic)."""
    context = "\n\n".join(
        f"[{h.get('source')}#{h.get('chunk_index')}] {(h.get('text') or '')[:500]}" for h in hits
    )
    user = f"Ngữ cảnh RAG:\n{context}\n\nCâu khách: {text!r}"

    resp = await get_openai().chat.completions.create(
        model=settings.llm_model,
        messages=[{"role": "system", "content": _system_prompt()}, {"role": "user", "content": user}],
        response_format={"type": "json_object"},
        temperature=0,
    )
    data = json.loads(resp.choices[0].message.content or "{}")

    flags: list[str] = []
    raw_intent = str(data.get("intent", "")).strip()
    if raw_intent in _VALID_INTENTS:
        intent = raw_intent
    else:
        intent = "other"
        flags.append("out_of_domain")

    llm_entities_raw = data.get("entities")
    llm_entities = (
        {k: str(v) for k, v in llm_entities_raw.items() if v is not None and str(v).strip()}
        if isinstance(llm_entities_raw, dict)
        else {}
    )
    entities = {**rule, **llm_entities}  # LLM đè trùng key; regex bù key thiếu

    try:
        confidence = max(0.0, min(1.0, float(data.get("confidence"))))
    except (TypeError, ValueError):
        confidence = float(hits[0]["score"])

    category = INTENT_CATEGORY.get(Intent(intent))
    top_score = float(hits[0]["score"])
    if top_score < settings.confidence_threshold:
        flags.append("low_retrieval_score")
    if len(hits) > 1 and abs(top_score - float(hits[1]["score"])) < settings.intent_ambiguous_margin:
        flags.append("ambiguous_intent")

    return {
        "intent": intent,
        "category": category.value if category else None,
        "entities": entities,
        "confidence": confidence,
        "uncertainty_flags": flags,
        "rag_contexts": _rag_contexts(hits),
    }


async def classify_intent(text: str) -> dict[str, Any]:
    """Phân loại intent + trích entities theo RAG. Trả {intent, category, entities, confidence,
    uncertainty_flags, rag_contexts}. Degrade an toàn khi offline (KHÔNG network, KHÔNG ném lỗi)."""
    # Tính regex SỚM — dùng cho MỌI nhánh (kể cả degrade) để order_id không bao giờ mất.
    rule = extract_entities_rule(text)

    # 1) Thiếu key -> không embed/search/LLM -> degrade (không network).
    if not settings.llm_api_key:
        return _degrade(rule, ["llm_unavailable"])

    # 2) Truy hồi ngữ cảnh (tầng service — Knowledge Agent tái dùng, PRD §7.2).
    try:
        hits = await rag_service.search(text)
    except Exception as exc:  # noqa: BLE001 — Qdrant/embed lỗi -> degrade, KHÔNG ném.
        log.warning("intent.search failed -> degrade: %s", exc)
        return _degrade(rule, ["search_error"])

    if not hits:
        return _degrade(rule, ["no_relevant_knowledge"])

    # 3) LLM bắt buộc cho intent (chunk generic không có nhãn).
    if settings.enable_llm:
        try:
            return await _classify_llm(text, hits, rule)
        except Exception as exc:  # noqa: BLE001 — LLM lỗi -> degrade + cờ (đừng im lặng), entities=regex.
            log.warning("intent.llm failed -> degrade llm_unavailable: %s", exc)
            return _degrade(rule, ["llm_unavailable"], _rag_contexts(hits))

    # ENABLE_LLM=false: chunk generic không phân loại được nếu không LLM -> degrade + entities regex.
    return _degrade(rule, ["llm_unavailable"], _rag_contexts(hits))


async def intent_node(state: ConversationState) -> dict[str, Any]:
    """Node graph: chạy classify_intent rồi ghi vào state + trace. Chỉ Agent 1 có logic thật (PRD §7.1)."""
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
                "detail": {"intent": result["intent"], "entities": result["entities"]},
            }
        ],
    }
