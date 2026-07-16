"""Node 1 — Intent Classifier (PRD §7.1). Phân loại intent + trích ENTITIES từ MESSAGE + TAXONOMY.

- Agent 1 **KHÔNG** gọi `rag_service` (retrieval là việc Agent 2 — PRD §7.2). Taxonomy cố định (mô tả + ví dụ
  mỗi intent) nằm trong prompt để bù cho việc bỏ retrieval.
- Output SẠCH: `{intent, category, entities, confidence, uncertainty_flags}` — **KHÔNG** `rag_contexts`,
  **KHÔNG** `low_retrieval_score`.
- ENTITIES = LLM (schema + few-shot) ⊕ regex (`extract_entities_rule`), merge `{**rule, **llm}`; regex chạy MỌI
  nhánh (kể cả degrade) → `order_id` không bao giờ mất.
- `confidence` = độ tự tin LLM (KHÔNG phải điểm cosine). `category` từ `INTENT_CATEGORY`. Cờ Agent 1:
  `ambiguous_intent`/`multi_intent` (LLM báo) + `out_of_domain` (intent ngoài enum).
- Degrade AN TOÀN: thiếu key / ENABLE_LLM=false / LLM lỗi → `intent="unknown"`, `confidence=0.0`,
  `["llm_unavailable"]`, entities = regex (KHÔNG network, KHÔNG ném lỗi) → `make test` offline.
"""

from __future__ import annotations

import json
from typing import Any

from ...core.config import settings
from ...core.embeddings import get_openai
from ...core.logging import get_logger
from ...models.enums import INTENT_CATEGORY, ConversationStatus, Intent
from ..state import ConversationState
from ._entities import extract_entities_rule
from ._history import format_history
from .taxonomy import render_taxonomy

log = get_logger("agent.intent")

_VALID_INTENTS = {i.value for i in Intent}
_AGENT1_FLAGS = {"ambiguous_intent", "multi_intent"}  # cờ hợp lệ Agent 1 (ngoài out_of_domain)


def _degrade(rule: dict[str, str], flags: list[str]) -> dict[str, Any]:
    """Degrade an toàn. entities = regex (bù) — order_id không mất kể cả khi không có LLM."""
    return {
        "intent": "unknown",
        "category": None,
        "entities": dict(rule),
        "confidence": 0.0,
        "uncertainty_flags": flags,
    }


def _system_prompt() -> str:
    return (
        "Bạn là bộ phân loại intent + trích entities cho CSKH shop quần áo.\n"
        "Phân loại câu khách theo TAXONOMY sau (chọn ĐÚNG 1 intent trong danh sách):\n"
        f"{render_taxonomy()}\n\n"
        "Quy tắc:\n"
        "1) intent PHẢI thuộc taxonomy. CHỈ chọn 'other' khi câu NGOÀI phạm vi CSKH (chào hỏi, cảm ơn, spam,\n"
        "   lạc đề). Câu về sản phẩm/giá/size/đơn/ship/đổi/trả/hoàn tiền/khuyến mãi LUÔN thuộc intent nghiệp vụ\n"
        "   tương ứng — vd hỏi chính sách/thời hạn 'đổi trả' → refund (hoặc exchange nếu rõ là đổi).\n"
        "2) Trích entities theo schema của intent đã chọn (giá trị CHUỖI; order_id chỉ chữ số; KHÔNG bịa key ngoài schema).\n"
        "3) confidence trong [0,1] = độ tự tin của bạn.\n"
        "4) flags: thêm 'ambiguous_intent' nếu mơ hồ giữa nhiều intent; 'multi_intent' nếu câu có NHIỀU ý.\n"
        'Trả JSON: {"intent": <str>, "entities": {<key>: <chuỗi>}, "confidence": <float>, "flags": [<str>]}.\n'
        "Ví dụ:\n"
        '- "Đơn hàng 6578 của tôi sắp giao tới nơi chưa?" -> '
        '{"intent":"order_status","entities":{"order_id":"6578"},"confidence":0.95,"flags":[]}\n'
        '- "Mình cao 1m60 nặng 50kg mặc size gì?" -> '
        '{"intent":"size_consulting","entities":{"height":"1m60","weight":"50kg"},"confidence":0.9,"flags":[]}'
    )


async def _classify_llm(
    text: str, rule: dict[str, str], history: list[dict[str, Any]] | None
) -> dict[str, Any]:
    """LLM phân loại intent + trích entities từ message + taxonomy (KHÔNG dùng RAG). Lịch sử (nếu có) giúp
    hiểu tham chiếu đa lượt (vd "thế còn size L?" → cùng sản phẩm ở lượt trước)."""
    resp = await get_openai().chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": _system_prompt()},
            {"role": "user", "content": f"{format_history(history, settings.history_window)}Câu khách: {text!r}"},
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )
    data = json.loads(resp.choices[0].message.content or "{}")

    flags: list[str] = []
    raw_intent = str(data.get("intent", "")).strip()
    intent = raw_intent if raw_intent in _VALID_INTENTS else "other"
    # intent="other" = NGOÀI taxonomy CSKH (chào hỏi/spam/lạc đề — hoặc nhãn LLM trôi) → out_of_domain.
    # Agent 3 dùng out_of_domain làm cờ chặn: câu ngoài phạm vi shop → human_handoff (không auto trả).
    if intent == "other":
        flags.append("out_of_domain")

    for flag in data.get("flags") or []:  # chỉ nhận cờ hợp lệ của Agent 1
        if flag in _AGENT1_FLAGS and flag not in flags:
            flags.append(flag)

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
        confidence = 0.5

    category = INTENT_CATEGORY.get(Intent(intent))
    return {
        "intent": intent,
        "category": category.value if category else None,
        "entities": entities,
        "confidence": confidence,
        "uncertainty_flags": flags,
    }


async def classify_intent(
    text: str, history: list[dict[str, Any]] | None = None
) -> dict[str, Any]:
    """Phân loại intent + trích entities từ message (taxonomy prompt, KHÔNG retrieval). `history` (đầu vào
    chỉ-đọc) giúp hiểu ngữ cảnh đa lượt. Trả {intent, category, entities, confidence, uncertainty_flags}.
    Degrade an toàn khi offline."""
    rule = extract_entities_rule(text)  # tính sớm — dùng cho MỌI nhánh (order_id không mất)
    if not settings.llm_api_key or not settings.enable_llm:
        return _degrade(rule, ["llm_unavailable"])
    try:
        return await _classify_llm(text, rule, history)
    except Exception as exc:  # noqa: BLE001 — LLM lỗi -> degrade + cờ (đừng im lặng), entities = regex.
        log.warning("intent.llm failed -> degrade llm_unavailable: %s", exc)
        return _degrade(rule, ["llm_unavailable"])


async def intent_node(state: ConversationState) -> dict[str, Any]:
    """Node graph: classify_intent rồi ghi state + trace. Ghi `intent_confidence` (Agent 1) — KHÔNG ghi
    `rag_contexts` (của Agent 2) hay `confidence` chung (Decision tính min)."""
    result = await classify_intent(state.get("input", ""), history=state.get("history"))
    return {
        "status": ConversationStatus.CLASSIFYING,
        "intent": result["intent"],
        "entities": result["entities"],
        "intent_confidence": result["confidence"],
        "uncertainty_flags": result["uncertainty_flags"],
        "trace": [
            {
                "node": "intent",
                "confidence": result["confidence"],
                "branch": None,
                "detail": {"intent": result["intent"], "entities": result["entities"]},
            }
        ],
    }
