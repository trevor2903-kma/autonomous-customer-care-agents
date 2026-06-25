"""Node 5 — human_handoff (STUB). PRD §8.4, §11.

Nhánh chuyển người: vào hàng đợi Admin (IN_HUMAN_QUEUE) kèm EscalationCard.

LƯU Ý (PRD §7.4 + CLAUDE.md): thông báo "đã chuyển nhân viên" tới khách do RESPONSE GENERATOR phát khi
wiring — node này KHÔNG gửi tin trực tiếp cho khách (giữ điểm phát ngôn DUY NHẤT). Ở scaffold, thông báo
nằm trong result.notice + dựng EscalationCard, CHƯA gửi.
"""

from __future__ import annotations

from typing import Any

from ...models.enums import ConversationStatus
from ..state import ConversationState


def human_handoff_node(state: ConversationState) -> dict[str, Any]:
    reason = state.get("escalation_reason") or "uncertain_case"

    # TODO (PRD §11): EscalationCard đầy đủ (thông tin khách + tóm tắt + intent/entities + RAG context +
    #   output Decision + escalation_reason + nháp gợi ý + link transcript/trace).
    escalation_card = {
        "summary": "(stub) tóm tắt hội thoại",
        "intent": state.get("intent"),
        "entities": state.get("entities") or {},
        "rag_context": state.get("rag_contexts") or [],
        "escalation_reason": reason,
        "suggested_reply": "(stub) nháp gợi ý cho Admin",
    }

    # TODO (PRD §10 FR-ASYNC-3): tạm dừng AI cho hội thoại (LangGraph interrupt + checkpointer); push + badge
    #   tới Admin; tin nhắn khách giai đoạn này định tuyến tới Admin, KHÔNG tới AI.
    return {
        "status": ConversationStatus.IN_HUMAN_QUEUE,
        "require_human_handoff": True,
        "escalation_reason": reason,
        "result": {
            "branch": "human_handoff",
            "escalation_reason": reason,
            "notice": "Yêu cầu của bạn đã được chuyển tới nhân viên hỗ trợ.",
            "escalation_card": escalation_card,
        },
        "trace": [
            {
                "node": "human_handoff",
                "confidence": state.get("confidence"),
                "branch": "human_handoff",
                "detail": {"reason": reason},
            }
        ],
    }
