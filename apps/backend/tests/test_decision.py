"""Agent 3 — Decision Engine: policy TẤT ĐỊNH (safety gate trên CỜ + priority/severity theo intent).

Đơn vị, KHÔNG network: decision_node là hàm thuần đọc state → quyết định. Kiểm FR: cờ → action;
intent → priority/severity; KHÔNG blend confidence.
"""

from __future__ import annotations

from app.agents.nodes.decision import BLOCKING_FLAGS, decision_node


def _decide(**state) -> dict:  # type: ignore[no-untyped-def]
    return decision_node(state)


def test_blocking_flag_routes_handoff() -> None:
    out = _decide(intent="product_information", uncertainty_flags=["no_relevant_knowledge"])
    assert out["action"] == "human_handoff"
    assert out["require_human_handoff"] is True
    assert "no_relevant_knowledge" in out["escalation_reason"]


def test_clean_flags_routes_auto_reply() -> None:
    out = _decide(intent="product_price", uncertainty_flags=[])
    assert out["action"] == "auto_reply"
    assert out["require_human_handoff"] is False
    assert out["escalation_reason"] is None
    assert out["priority"] == "low"
    assert out["severity"] == "low"


def test_complaint_priority_high_high() -> None:
    # complaint sạch cờ vẫn auto_reply (priority/severity chỉ để audit/monitor, KHÔNG tự ép handoff).
    out = _decide(intent="complaint", uncertainty_flags=[])
    assert out["action"] == "auto_reply"
    assert out["priority"] == "high"
    assert out["severity"] == "high"


def test_refund_priority_high_severity_medium() -> None:
    out = _decide(intent="refund", uncertainty_flags=[])
    assert out["priority"] == "high"
    assert out["severity"] == "medium"


def test_no_blend_confidence_low_intent_conf_still_auto_reply() -> None:
    # intent_confidence THẤP nhưng KHÔNG có cờ chặn → vẫn auto_reply (route trên CỜ, KHÔNG blend confidence).
    out = _decide(intent="shipping", uncertainty_flags=[], intent_confidence=0.2, retrieval_confidence=0.9)
    assert out["action"] == "auto_reply"


def test_injected_flag_forces_handoff_and_emits_new_flag() -> None:
    out = _decide(intent="other", uncertainty_flags=[], scratchpad={"injected_flags": ["ambiguous_intent"]})
    assert out["action"] == "human_handoff"
    assert out["uncertainty_flags"] == ["ambiguous_intent"]  # emit CỜ MỚI (demo), không trả lại cờ tích luỹ


def test_hallucination_risk_not_blocking() -> None:
    # hallucination_risk KHÔNG ∈ BLOCKING_FLAGS (Agent 4 phát SAU) → KHÔNG tự route handoff ở decision.
    assert "hallucination_risk" not in BLOCKING_FLAGS
    out = _decide(intent="shipping", uncertainty_flags=["hallucination_risk"])
    assert out["action"] == "auto_reply"


def test_unknown_intent_defaults_low_low() -> None:
    out = _decide(intent="unknown", uncertainty_flags=[])
    assert out["priority"] == "low"
    assert out["severity"] == "low"
