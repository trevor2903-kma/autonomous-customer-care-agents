"""escalation_service (08b) — build_escalation_card + priority_rank (hàm thuần, offline).

list_escalations (DB, sắp theo priority) verify LIVE ở Phase 1 (GET /api/admin/escalations).
"""

from __future__ import annotations

from app.services.escalation_service import build_escalation_card, priority_rank


def test_priority_rank_orders_high_first() -> None:
    assert priority_rank("high") > priority_rank("medium") > priority_rank("low") > priority_rank(None)
    assert priority_rank("weird") == 0  # ngoài bảng -> thấp nhất


def test_build_card_has_all_fields() -> None:
    final = {
        "intent": "complaint",
        "entities": {"order_id": "123"},
        "rag_contexts": [{"text": "chính sách đổi trả 7 ngày", "source": "kb.pdf", "score": 0.8}],
        "escalation_reason": "blocking_flags=['no_relevant_knowledge']",
        "priority": "high",
        "severity": "high",
    }
    card = build_escalation_card(final, "  áo bị lỗi, shop xử lý sao?  ")
    assert card["summary"] == "áo bị lỗi, shop xử lý sao?"  # đã strip
    assert card["intent"] == "complaint"
    assert card["entities"] == {"order_id": "123"}
    assert card["rag_context"][0]["source"] == "kb.pdf"
    assert card["escalation_reason"]
    assert card["priority"] == "high"
    assert card["severity"] == "high"
    assert card["suggested_reply"] == ""  # human_handoff -> nháp rỗng


def test_build_card_pending_approval_carries_draft() -> None:
    card = build_escalation_card(
        {"intent": "refund", "priority": "high", "severity": "medium"},
        "cho hỏi đổi trả bao lâu",
        suggested_reply="Dạ shop đổi trả trong 7 ngày ạ.",
    )
    assert card["suggested_reply"] == "Dạ shop đổi trả trong 7 ngày ạ."


def test_build_card_empty_state_safe() -> None:
    # final state thiếu field -> card vẫn đủ khoá, không ném.
    card = build_escalation_card({}, "   ")
    assert card["intent"] is None
    assert card["entities"] == {}
    assert card["rag_context"] == []
    assert card["priority"] is None
    assert card["suggested_reply"] == ""


def test_top_sources_caps_and_snips() -> None:
    long_text = "x" * 300
    final = {"rag_contexts": [{"text": long_text, "source": f"s{i}.pdf", "score": 0.5} for i in range(5)]}
    card = build_escalation_card(final, "câu hỏi")
    assert len(card["rag_context"]) == 3  # cap top-3
    assert card["rag_context"][0]["snippet"].endswith("…")  # snippet dài bị cắt
    assert len(card["rag_context"][0]["snippet"]) <= 161  # 160 + ký tự …
