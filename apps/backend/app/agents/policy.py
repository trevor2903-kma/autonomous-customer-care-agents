"""Routing policy — định tuyến sau Decision Engine (PRD §8, §9)."""

from __future__ import annotations

from .state import ConversationState


def should_handoff(state: ConversationState) -> str:
    """Trả về nhánh kế tiếp: 'human_handoff' hoặc 'response'.

    An toàn KHÔNG bị gate ghi đè (PRD §9 FR-GATE-2): ca có cờ bất định / confidence thấp luôn
    human_handoff. Decision Engine đã đặt require_human_handoff; policy chỉ đọc để route.

    TODO (PRD §9/§10): mở rộng nhánh — gate auto-reply (gửi thẳng vs PENDING_APPROVAL theo category),
    clarification (AWAITING_CUSTOMER), suspend/resume. Scaffold chỉ tách 2 nhánh.
    """
    return "human_handoff" if state.get("require_human_handoff") else "response"
