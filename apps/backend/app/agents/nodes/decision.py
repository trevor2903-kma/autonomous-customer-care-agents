"""Node 3 — Decision Engine. PRD §7.3. **TẠM PASS-THROUGH** (Agent 3 bỏ tạm — xem ROADMAP 05).

Bản chất đúng: đây là NODE RA QUYẾT ĐỊNH — nơi hội tụ tín hiệu an toàn (PRD §5 trụ cột 3), đánh giá
priority/severity + cờ bất định/confidence → `auto_reply` vs `human_handoff`.

TRONG SLICE HAPPY-CASE NÀY: bỏ tạm đánh giá thật. `decision_node` chỉ giữ **nhánh demo** — handoff KHI VÀ
CHỈ KHI có `scratchpad.injected_flags` (do run-demo tiêm) — nên **traffic thật → luôn `auto_reply`**. Phanh
an toàn (không có tri thức → không bịa) TẠM chuyển sang Agent 4 (`response.py` fallback + hallucination_risk).
"""

from __future__ import annotations

from typing import Any

from ...models.enums import AgentAction, ConversationStatus
from ..state import ConversationState


def decision_node(state: ConversationState) -> dict[str, Any]:
    # TẠM (ROADMAP 05): pass-through. Chỉ nhánh demo — run-demo tiêm scratchpad.injected_flags để ép handoff
    # (giữ test 2 nhánh xanh). Traffic thật (không tiêm) → injected rỗng → auto_reply (happy case).
    injected = list((state.get("scratchpad") or {}).get("injected_flags") or [])
    handoff = bool(injected)
    action = AgentAction.HUMAN_HANDOFF if handoff else AgentAction.AUTO_REPLY
    escalation_reason = f"injected_flags={injected}" if handoff else None

    # TODO (PRD §7.3, ROADMAP 05 — KHÔI PHỤC AGENT 3): đánh giá THẬT priority/severity + quy tắc an toàn bất
    #   biến: cờ tích luỹ (uncertainty_flags từ Agent 1/2) HOẶC min(intent_confidence, retrieval_confidence)
    #   < settings.confidence_threshold → human_handoff. Khi khôi phục, chuyển quyết định về ĐÂY; Agent 4 quay
    #   lại chỉ lo sinh câu trả lời (KHÔNG để logic quyết định "vĩnh viễn" nằm trong Agent 4).
    return {
        "status": ConversationStatus.DECIDING,
        "action": action,
        # Reducer `add`: CHỈ trả cờ MỚI (injected của demo) — KHÔNG trả lại cờ đã tích luỹ (tránh nhân đôi).
        "uncertainty_flags": injected,
        "require_human_handoff": handoff,
        "escalation_reason": escalation_reason,
        "trace": [
            {
                "node": "decision",
                "confidence": state.get("confidence"),
                "branch": str(action),
                "detail": {"pass_through": True, "injected": injected},
            }
        ],
    }
