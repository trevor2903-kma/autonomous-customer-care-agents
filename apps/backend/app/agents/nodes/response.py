"""Node 4 — Response Generator (Agent 4). ĐIỂM PHÁT NGÔN DUY NHẤT tới khách. PRD §7.4, §14 FR-PIPE-5.

- `generate_reply(query, intent, entities, rag_contexts)` = hàm THUẦN (tái dùng): sinh câu trả lời CSKH
  tiếng Việt GROUNDED **chỉ từ `rag_contexts`**. Phanh anti-hallucination (PRD §5 trụ cột 3, §14 FR-PIPE-5):
  `rag_contexts` rỗng **hoặc** thiếu `settings.llm_api_key` → KHÔNG gọi LLM bịa → câu fallback lịch sự + cờ
  `hallucination_risk`. (Phanh này TẠM gánh vai an toàn thay Decision Engine/Agent 3 — xem ROADMAP 05.)
- `response_node` là **NODE DUY NHẤT** được ghi tin nhắn AI vào `state["messages"]` (PRD §7.4).
- Degrade AN TOÀN: thiếu key / LLM lỗi / LLM trả rỗng → fallback (KHÔNG ném lỗi) → pipeline không rớt,
  `make test` chạy offline.
"""

from __future__ import annotations

from typing import Any

from ...core.config import settings
from ...core.embeddings import get_openai
from ...core.logging import get_logger
from ...models.enums import ConversationStatus
from ..state import ConversationState

log = get_logger("agent.response")

# Câu fallback lịch sự khi KHÔNG đủ tri thức để trả lời chắc chắn (KHÔNG bịa — PRD §14 FR-PIPE-5).
FALLBACK_REPLY = (
    "Dạ câu hỏi này em xin phép chuyển tới nhân viên hỗ trợ để được giải đáp chính xác hơn ạ. "
    "Mong anh/chị thông cảm và chờ trong giây lát ạ."
)


def _system_prompt() -> str:
    return (
        "Bạn là nhân viên chăm sóc khách hàng của một shop quần áo. "
        "Soạn câu trả lời tiếng Việt thân thiện, lịch sự, NGẮN GỌN cho khách. "
        "CHỈ dựa trên các ĐOẠN TRI THỨC được cung cấp bên dưới — TUYỆT ĐỐI KHÔNG bịa thông tin ngoài các đoạn đó. "
        "Nếu các đoạn tri thức KHÔNG đủ để trả lời chắc chắn, hãy nói rằng bạn sẽ chuyển câu hỏi tới nhân viên hỗ "
        "trợ, KHÔNG được bịa. Không nhắc tới 'đoạn tri thức'/'context' trong câu trả lời."
    )


def _context_block(rag_contexts: list[dict[str, Any]]) -> str:
    """Ghép các đoạn tri thức (kèm source) thành context cho prompt."""
    parts: list[str] = []
    for i, c in enumerate(rag_contexts, 1):
        text = (c.get("text") or "").strip()
        source = c.get("source") or "?"
        parts.append(f"[Đoạn {i} · nguồn: {source}]\n{text}")
    return "\n\n".join(parts)


async def generate_reply(
    query: str,
    intent: str | None,
    entities: dict[str, Any] | None,
    rag_contexts: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    """Sinh câu trả lời GROUNDED chỉ từ `rag_contexts`. Trả `{reply, uncertainty_flags}`.

    Phanh: rag_contexts rỗng HOẶC thiếu llm_api_key → fallback + `hallucination_risk` (KHÔNG gọi LLM bịa)."""
    contexts = rag_contexts or []
    if not contexts or not settings.llm_api_key:
        # KHÔNG có tri thức để bám (hoặc không thể gọi LLM) → KHÔNG bịa (PRD §14 FR-PIPE-5).
        return {"reply": FALLBACK_REPLY, "uncertainty_flags": ["hallucination_risk"]}

    user_msg = (
        f"Câu hỏi của khách: {query!r}\n"
        f"(intent: {intent}; entities: {entities or {}})\n\n"
        f"ĐOẠN TRI THỨC:\n{_context_block(contexts)}"
    )
    try:
        resp = await get_openai().chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": _system_prompt()},
                {"role": "user", "content": user_msg},
            ],
            temperature=0,
        )
        reply = (resp.choices[0].message.content or "").strip()
    except Exception as exc:  # noqa: BLE001 — LLM lỗi → fallback (đừng ném, đừng bịa) → pipeline không rớt.
        log.warning("response.llm failed -> fallback: %s", exc)
        return {"reply": FALLBACK_REPLY, "uncertainty_flags": ["hallucination_risk"]}

    if not reply:  # LLM trả rỗng → fallback an toàn.
        return {"reply": FALLBACK_REPLY, "uncertainty_flags": ["hallucination_risk"]}
    return {"reply": reply, "uncertainty_flags": []}


async def response_node(state: ConversationState) -> dict[str, Any]:
    """Node 4 — sinh phản hồi grounded rồi ghi state + trace. NODE DUY NHẤT ghi tin nhắn AI (PRD §7.4)."""
    result = await generate_reply(
        query=state.get("input", ""),
        intent=state.get("intent"),
        entities=state.get("entities") or {},
        rag_contexts=state.get("rag_contexts") or [],
    )
    reply = result["reply"]
    return {
        "status": ConversationStatus.REPLIED,
        "draft_reply": reply,
        "messages": [{"sender": "ai", "content": reply}],
        "result": {"branch": "response", "action": state.get("action"), "reply": reply},
        # Reducer `add`: CHỈ cờ MỚI của node này (hallucination_risk khi phải fallback).
        "uncertainty_flags": result["uncertainty_flags"],
        "trace": [
            {
                "node": "response",
                "confidence": state.get("confidence"),
                "branch": "response",
                "detail": {
                    "flags": result["uncertainty_flags"],
                    "grounded": not result["uncertainty_flags"],
                },
            }
        ],
    }
