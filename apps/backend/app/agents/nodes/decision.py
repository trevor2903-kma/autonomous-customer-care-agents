"""Node 3 — Decision Engine (Agent 3). NODE RA QUYẾT ĐỊNH — PRD §7.3, §5 trụ cột 3 (an toàn) + trụ cột 1 (audit).

Policy **TẤT ĐỊNH** — KHÔNG LLM/reasoning cho phần an toàn (thừa + hại NFR-1 latency). Định tuyến trên **CỜ**,
**KHÔNG blend confidence**: `intent_confidence` (LLM tự khai) và `retrieval_confidence` (cosine) là HAI THANG
khác nhau → đừng `min` rồi so một ngưỡng. Safety gate: bất kỳ cờ nào ∈ `BLOCKING_FLAGS` (cờ có mặt TẠI decision,
từ Agent 1+2) → `human_handoff`. `priority`/`severity` theo intent (cho Agent Monitoring + audit). Giữ CẢ HAI
confidence trong `trace`.
"""

from __future__ import annotations

from typing import Any

from ...models.enums import AgentAction, ConversationStatus, Priority, Severity
from ..state import ConversationState

# Tập ĐÓNG cờ CHẶN (→ human_handoff). Nguyên tắc: escalate khi KHÔNG trả lời được, KHÔNG phải khi nhãn mờ.
#   - Cờ grounding (no_relevant_knowledge / low_retrieval_score) là gate "trả lời-được-hay-không" thật sự.
#   - `ambiguous_intent` KHÔNG chặn: nhãn mờ NHƯNG grounding mạnh (vd "đổi trả", cosine cao) vẫn trả lời được;
#     nếu grounding yếu thì chính cờ grounding đã chặn. Giữ ambiguous_intent như cờ THÔNG TIN (priority/audit).
#   - `multi_intent` VẪN chặn: khách hỏi HAI việc khác nhau → trả một cái là thiếu (xử lý multi-intent = sau).
#   - `out_of_domain`: câu ngoài phạm vi CSKH (intent=other) → handoff.
#   - `hallucination_risk` KHÔNG thuộc: Agent 4 phát SAU decision (phanh dự phòng cuối, không định tuyến ở đây).
BLOCKING_FLAGS: frozenset[str] = frozenset(
    {
        "multi_intent",
        "out_of_domain",
        "no_relevant_knowledge",
        "low_retrieval_score",
        "llm_unavailable",
        "search_error",
    }
)

# Bảng priority/severity theo intent (tất định). intent ngoài bảng (vd "unknown") → low/low.
_PRIORITY_SEVERITY: dict[str, tuple[Priority, Severity]] = {
    "complaint": (Priority.HIGH, Severity.HIGH),
    "refund": (Priority.HIGH, Severity.MEDIUM),
    "exchange": (Priority.MEDIUM, Severity.LOW),
    "order_status": (Priority.MEDIUM, Severity.LOW),
    "product_price": (Priority.LOW, Severity.LOW),
    "product_information": (Priority.LOW, Severity.LOW),
    "size_consulting": (Priority.LOW, Severity.LOW),
    "shipping": (Priority.LOW, Severity.LOW),
    "promotion": (Priority.LOW, Severity.LOW),
    "payment": (Priority.LOW, Severity.LOW),
    "membership": (Priority.LOW, Severity.LOW),
    "store_information": (Priority.LOW, Severity.LOW),
    "return_exchange_policy": (Priority.LOW, Severity.LOW),  # HỎI chính sách = tra cứu, không phải ca giao dịch
    "greeting": (Priority.LOW, Severity.LOW),
    "other": (Priority.LOW, Severity.LOW),
}


def decision_node(state: ConversationState) -> dict[str, Any]:
    accumulated = list(state.get("uncertainty_flags") or [])  # cờ tích luỹ Agent 1+2 (reducer add)
    injected = list((state.get("scratchpad") or {}).get("injected_flags") or [])  # demo (run-demo)

    # Safety gate TẤT ĐỊNH (PRD §5 trụ cột 3): cờ ∈ BLOCKING_FLAGS → human_handoff. KHÔNG blend confidence.
    blocking = sorted((set(accumulated) | set(injected)) & BLOCKING_FLAGS)
    handoff = bool(blocking)
    action = AgentAction.HUMAN_HANDOFF if handoff else AgentAction.AUTO_REPLY
    escalation_reason = f"blocking_flags={blocking}" if handoff else None

    intent = state.get("intent") or "other"
    priority, severity = _PRIORITY_SEVERITY.get(intent, (Priority.LOW, Severity.LOW))

    # TODO (PRD §9, slice 08a): gate auto-reply theo category nhạy cảm → PENDING_APPROVAL (duyệt nháp).
    # TODO (sau): LLM sentiment nhẹ (non-reasoning) → cờ `frustrated_customer` nâng priority. KHÔNG làm ở đây.
    return {
        "status": ConversationStatus.DECIDING,
        "action": action,
        "priority": str(priority),
        "severity": str(severity),
        "require_human_handoff": handoff,
        "escalation_reason": escalation_reason,
        # Reducer `add`: CHỈ trả cờ MỚI (injected của demo) — cờ tích luỹ đã có sẵn, đừng trả lại (tránh nhân đôi).
        "uncertainty_flags": injected,
        "trace": [
            {
                "node": "decision",
                "confidence": state.get("intent_confidence"),
                "branch": str(action),
                "detail": {
                    "blocking_flags": blocking,
                    "priority": str(priority),
                    "severity": str(severity),
                    # Giữ CẢ HAI confidence (KHÔNG blend) cho audit + Agent Monitoring (PRD §5 trụ cột 1).
                    "intent_confidence": state.get("intent_confidence"),
                    "retrieval_confidence": state.get("retrieval_confidence"),
                },
            }
        ],
    }
