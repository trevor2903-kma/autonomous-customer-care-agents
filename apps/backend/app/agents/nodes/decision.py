"""Node 3 — Decision Engine (STUB) — NODE RA QUYẾT ĐỊNH. PRD §7.3.

Nơi hội tụ tín hiệu an toàn (PRD §5 trụ cột 3). Quy tắc an toàn BẤT BIẾN: có uncertainty_flag bất kỳ
hoặc confidence < ngưỡng -> action=human_handoff (độc lập với gate §9).
"""

from __future__ import annotations

from typing import Any

from ...core.config import settings
from ...models.enums import AgentAction, ConversationStatus
from ..state import ConversationState


def decision_node(state: ConversationState) -> dict[str, Any]:
    # STUB: KHÔNG đánh giá priority/severity/rủi ro thật. Chỉ áp quy tắc an toàn bất biến lên cờ/confidence.
    flags = list(state.get("uncertainty_flags") or [])

    # Scaffold demo: run-demo có thể tiêm cờ qua scratchpad["injected_flags"] để ép nhánh an toàn.
    # TODO: trong hệ thật, uncertainty_flags do intent/knowledge sinh — KHÔNG tiêm từ ngoài.
    injected = list((state.get("scratchpad") or {}).get("injected_flags") or [])
    flags = flags + injected

    confidence = float(state.get("confidence", 1.0))
    handoff = bool(flags) or confidence < settings.confidence_threshold
    action = AgentAction.HUMAN_HANDOFF if handoff else AgentAction.AUTO_REPLY

    escalation_reason: str | None = None
    if handoff:
        escalation_reason = (
            f"uncertainty_flags={flags}"
            if flags
            else f"confidence {confidence} < threshold {settings.confidence_threshold}"
        )

    # TODO (PRD §7.3): priority/severity; intent nhạy cảm (refund/complaint/exchange) KHÔNG tự là cờ
    #   bất định — gửi thẳng vs Duyệt nháp do gate auto-reply theo category quyết định (§9).
    return {
        "status": ConversationStatus.DECIDING,
        "action": action,
        "uncertainty_flags": flags,
        "require_human_handoff": handoff,
        "escalation_reason": escalation_reason,
        "trace": [
            {"node": "decision", "confidence": confidence, "branch": str(action), "detail": {"flags": flags}}
        ],
    }
