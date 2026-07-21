"""Gate động (P3) — holds_auto_reply thuần trên GateSnapshot (đọc DB ở runtime; hàm quyết định offline).

§4: gate = van cho auto_reply (REPLIED). master TẮT → giữ tất; else giữ nếu intent không "gửi thẳng".
FR-GATE-2: human_handoff (IN_HUMAN_QUEUE) LUÔN escalate — KHÔNG bao giờ qua gate.
"""

from __future__ import annotations

from app.models.enums import ConversationStatus
from app.services.gate_service import GateIntentRuleView, GateSnapshot, holds_auto_reply


def _snap(*, auto_reply_enabled: bool = True, rules: list[GateIntentRuleView] | None = None) -> GateSnapshot:
    return GateSnapshot(
        auto_reply_enabled=auto_reply_enabled,
        auto_resolve_enabled=True,
        auto_resolve_minutes=30,
        retrieval_threshold=0.35,
        rules=tuple(rules or ()),
    )


def _rule(intent: str, send_directly: bool, *, sensitive: bool = False) -> GateIntentRuleView:
    return GateIntentRuleView(intent=intent, label=intent, sensitive=sensitive, send_directly=send_directly)


def test_holds_when_not_send_directly() -> None:
    snap = _snap(rules=[_rule("refund", False, sensitive=True), _rule("shipping", True)])
    assert holds_auto_reply(snap, ConversationStatus.REPLIED, "refund") is True
    # intent không có luật → coi như không gửi thẳng → giữ nháp (an toàn)
    assert holds_auto_reply(snap, ConversationStatus.REPLIED, "unknown_intent") is True


def test_no_hold_when_send_directly() -> None:
    snap = _snap(rules=[_rule("shipping", True), _rule("product_price", True)])
    assert holds_auto_reply(snap, ConversationStatus.REPLIED, "shipping") is False
    assert holds_auto_reply(snap, ConversationStatus.REPLIED, "product_price") is False


def test_never_holds_handoff() -> None:
    # human_handoff (IN_HUMAN_QUEUE) LUÔN escalate — bất biến FR-GATE-2, không qua gate.
    snap = _snap(rules=[_rule("refund", False)])
    assert holds_auto_reply(snap, ConversationStatus.IN_HUMAN_QUEUE, "refund") is False


def test_master_off_holds_all() -> None:
    # master auto_reply_enabled=False → giữ nháp TẤT CẢ auto_reply (kể cả intent gửi thẳng).
    snap = _snap(auto_reply_enabled=False, rules=[_rule("shipping", True)])
    assert holds_auto_reply(snap, ConversationStatus.REPLIED, "shipping") is True
