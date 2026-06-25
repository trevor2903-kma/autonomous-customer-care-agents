"""Node 4 — Response Generator (STUB) — ĐIỂM PHÁT NGÔN DUY NHẤT tới khách. PRD §7.4, CLAUDE.md."""

from __future__ import annotations

from typing import Any

from ...models.enums import ConversationStatus
from ..state import ConversationState


def response_node(state: ConversationState) -> dict[str, Any]:
    # STUB: KHÔNG LLM/grounding thật. Sinh phản hồi mẫu (placeholder).
    # TODO (PRD §7.4, §14 FR-PIPE-5): sinh phản hồi GROUNDED theo rag_contexts; nếu context yếu ->
    #   KHÔNG bịa, chuyển human_handoff (hallucination_risk). Gửi theo gate (§9: gửi thẳng | PENDING_APPROVAL).
    # Đây là node DUY NHẤT được phép ghi tin nhắn AI vào state["messages"].
    draft = "[stub auto_reply] Cảm ơn bạn đã liên hệ shop — đây là phản hồi mẫu (chưa sinh nội dung thật)."
    return {
        "status": ConversationStatus.REPLIED,
        "draft_reply": draft,
        "messages": [{"sender": "ai", "content": draft}],
        "result": {"branch": "response", "action": state.get("action"), "reply": draft},
        "trace": [
            {"node": "response", "confidence": state.get("confidence"), "branch": "response", "detail": {"stub": True}}
        ],
    }
