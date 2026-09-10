"""Observability P1 — hình dạng dòng audit của MỘT lượt + degrade an toàn. Offline, KHÔNG DB/network.

Hình dạng dòng audit là HỢP ĐỒNG với tab Báo cáo (P2/P4): sai một khoá là báo cáo sai âm thầm.
"""

from __future__ import annotations

import inspect
import uuid

import pytest

from app.agents.nodes.decision import decision_node
from app.agents.nodes.knowledge import knowledge_node
from app.api.ws import chat as ws_chat
from app.models.enums import AuditNode, ConversationStatus, TurnOutcome
from app.services import audit_service

TURN = uuid.uuid4()
CONV = uuid.uuid4()

FINAL = {
    "intent": "shipping",
    "action": "auto_reply",
    "priority": "low",
    "severity": "low",
    "status": ConversationStatus.REPLIED,
    "retrieval_confidence": 0.86,
    "intent_confidence": 0.9,
    "escalation_reason": None,
    "uncertainty_flags": [],
    "rag_contexts": [
        {"text": "Phí ship 30.000đ", "source": "reference/chinh-sach-van-chuyen.md",
         "type": "reference", "title": "Chính sách vận chuyển", "score": 0.8603},
    ],
    "trace": [
        {"node": "intent", "confidence": 0.9, "branch": None, "duration_ms": 700, "flags": [],
         "detail": {"intent": "shipping", "entities": {}}},
        {"node": "knowledge", "confidence": 0.86, "branch": None, "duration_ms": 300, "flags": [],
         "detail": {"contexts": 1, "intent": "shipping", "skipped": False}},
        {"node": "decision", "confidence": 0.9, "branch": "auto_reply", "duration_ms": 0, "flags": [],
         "detail": {"blocking_flags": [], "priority": "low", "severity": "low"}},
        {"node": "response", "confidence": 1.0, "branch": "response", "duration_ms": 1200, "flags": [],
         "detail": {"action": "auto_reply", "flags": []}},
    ],
}


def _rows(**over):
    kwargs = dict(
        turn_id=TURN, conversation_id=CONV, customer_text="ship về Đà Nẵng bao nhiêu",
        final=FINAL, reply="Phí ship 30.000đ ạ.", outcome=TurnOutcome.SENT, total_ms=2300,
    )
    kwargs.update(over)
    return audit_service.build_turn_rows(**kwargs)


def test_turn_rows_cover_customer_four_nodes_and_delivery() -> None:
    rows = _rows()
    assert [r["node"] for r in rows] == [
        AuditNode.CUSTOMER, "intent", "knowledge", "decision", "response", AuditNode.DELIVERY
    ]
    # MỌI dòng chia sẻ turn_id + conversation_id -> P2 gom lại dựng được drill-down 4 agent.
    assert all(r["turn_id"] == TURN and r["conversation_id"] == CONV for r in rows)


def test_knowledge_row_carries_md_sources_not_pdf() -> None:
    know = next(r for r in _rows() if r["node"] == "knowledge")
    src = know["detail"]["rag_sources"]
    assert src == [{"source": "reference/chinh-sach-van-chuyen.md", "type": "reference",
                    "title": "Chính sách vận chuyển", "score": 0.8603}]
    assert src[0]["source"].endswith(".md")  # nguồn canonical từ repo, KHÔNG phải PDF upload thời cũ
    assert know["detail"]["retrieval_confidence"] == 0.86


def _final_with_decision(*, action: str, agent3_reason: str | None, final_reason: str | None) -> dict:
    """FINAL với lý do CỦA Agent 3 trong bước trace decision; `final_reason` = final state (Agent 4 có thể ghi đè)."""
    trace = [
        {**s, "detail": {**s["detail"], "escalation_reason": agent3_reason}} if s["node"] == "decision" else s
        for s in FINAL["trace"]
    ]
    return {**FINAL, "action": action, "escalation_reason": final_reason, "trace": trace}


def test_decision_row_carries_agent3_action_and_reason() -> None:
    reason = "blocking_flags=['low_retrieval_score']"
    rows = _rows(final=_final_with_decision(action="human_handoff", agent3_reason=reason, final_reason=reason))
    dec = next(r for r in rows if r["node"] == "decision")
    assert dec["action"] == "human_handoff"
    assert dec["escalation_reason"] == reason
    assert "escalation_reason" not in dec["detail"]  # lý do nằm ở CỘT của dòng, không lặp lại trong detail


def test_decision_row_never_takes_agent4s_reason() -> None:
    # AGENT-03.1 / NFR-4: Agent 4 fallback → final state mang lý do CỦA Agent 4; dòng decision vẫn chỉ ghi quyết định
    # của Agent 3 (auto_reply, không lý do). Lý do của lượt vẫn còn ở dòng delivery (final state).
    rows = _rows(final=_final_with_decision(
        action="auto_reply", agent3_reason=None, final_reason="blocking_flags=['hallucination_risk']"
    ))
    dec = next(r for r in rows if r["node"] == "decision")
    assert (dec["action"], dec["escalation_reason"]) == ("auto_reply", None)
    assert rows[-1]["escalation_reason"] == "blocking_flags=['hallucination_risk']"


def test_delivery_row_is_the_nfr1_number() -> None:
    delivery = _rows()[-1]
    assert delivery["action"] == TurnOutcome.SENT
    # duration_ms dòng delivery = END-TO-END cả lượt, KHÔNG phải tổng các node (2300 != 700+300+0+1200).
    assert delivery["duration_ms"] == 2300
    assert sum(r["duration_ms"] or 0 for r in _rows() if r["node"] in {"intent", "knowledge", "decision", "response"}) == 2200
    assert delivery["detail"]["intent"] == "shipping"
    assert delivery["detail"]["outcome"] == TurnOutcome.SENT


def test_failed_pipeline_still_audited() -> None:
    # final=None (pipeline ném lỗi) -> vẫn còn 2 dòng bao quanh: lượt hỏng là lượt CẦN nhìn nhất.
    rows = _rows(final=None, outcome=TurnOutcome.ERROR, reply="xin lỗi…")
    assert [r["node"] for r in rows] == [AuditNode.CUSTOMER, AuditNode.DELIVERY]
    assert rows[-1]["action"] == TurnOutcome.ERROR


def test_long_texts_are_capped() -> None:
    rows = _rows(customer_text="x" * 5000, reply="y" * 5000)
    assert len(rows[0]["detail"]["customer_text"]) == audit_service._TEXT_CAP
    resp = next(r for r in rows if r["node"] == "response")
    assert len(resp["detail"]["reply_preview"]) == audit_service._PREVIEW_CAP
    assert resp["detail"]["reply_len"] == 5000  # độ dài THẬT vẫn giữ, chỉ cắt bản lưu


def test_turn_rows_link_the_customer_message() -> None:
    # PERF-01.5: mọi dòng của lượt mang id tin KHÁCH đã lưu → nối thẳng về nguyên văn ở bảng message.
    mid = uuid.uuid4()
    assert all(r["message_id"] == mid for r in _rows(message_id=mid))
    assert all(r["message_id"] is None for r in _rows())  # không lưu được tin (DB lỗi) → NULL như cũ


def test_delivery_detail_is_merged_into_delivery_row_only() -> None:
    extra = {"timings": {"pipeline_ms": 1800, "send_ms": 2}, "discarded": True, "status_now": "HUMAN_HANDLING"}
    rows = _rows(delivery_detail=extra)
    assert rows[-1]["detail"]["timings"] == {"pipeline_ms": 1800, "send_ms": 2}
    assert rows[-1]["detail"]["discarded"] is True and rows[-1]["detail"]["intent"] == "shipping"
    assert all("timings" not in r["detail"] for r in rows[:-1])


async def test_record_turn_writes_message_id(monkeypatch: pytest.MonkeyPatch) -> None:
    written: list = []

    class _S:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *a: object) -> None:
            return None

        def add_all(self, objs: list) -> None:
            written.extend(objs)

        async def commit(self) -> None:
            return None

    monkeypatch.setattr(audit_service, "AsyncSessionLocal", _S)
    mid = uuid.uuid4()
    n = await audit_service.record_turn(
        turn_id=TURN, conversation_id=CONV, customer_text="x", final=FINAL,
        reply="y", outcome=TurnOutcome.SENT, total_ms=1, message_id=mid,
    )
    assert n == len(written) == 6
    assert {row.message_id for row in written} == {mid}  # cột audit_log.message_id KHÔNG còn luôn NULL


async def test_record_turn_never_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    """Bất biến §1: audit hỏng KHÔNG được làm rớt lượt trả lời khách."""

    def boom(*a: object, **k: object):
        raise RuntimeError("DB down")

    monkeypatch.setattr(audit_service, "AsyncSessionLocal", boom)
    assert await audit_service.record_turn(
        turn_id=TURN, conversation_id=CONV, customer_text="x", final=FINAL,
        reply="y", outcome=TurnOutcome.SENT, total_ms=1,
    ) == 0


# ── Kết cục giao (hàm thuần trong WS) ────────────────────────────────────────
def test_outcome_reads_real_delivery_not_agent_action() -> None:
    assert ws_chat._outcome_of(ConversationStatus.REPLIED, FINAL) == TurnOutcome.SENT
    assert ws_chat._outcome_of(ConversationStatus.IN_HUMAN_QUEUE, FINAL) == TurnOutcome.QUEUED_FOR_HUMAN
    assert ws_chat._outcome_of(None, None) == TurnOutcome.ERROR


# ── Lớp bọc quan sát: đo thời gian + quy cờ về đúng node ─────────────────────
async def test_observed_wrapper_stamps_duration_and_node_flags(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.agents import graph as graph_mod
    from app.agents.nodes import knowledge as kn

    monkeypatch.setattr(kn.settings, "llm_api_key", "sk-test")
    out = await graph_mod._observed(knowledge_node)({"input": "xin chào", "intent": "greeting"})
    step = out["trace"][0]
    assert step["duration_ms"] is not None and step["duration_ms"] >= 0
    assert step["flags"] == []  # greeting: Agent 2 bỏ qua retrieval, KHÔNG phát cờ (slice RAG P4)


def test_observed_keeps_sync_node_sync() -> None:
    # decision_node là hàm SYNC (Agent 3 tất định, không I/O) — wrapper KHÔNG được biến nó thành async.
    from app.agents import graph as graph_mod

    wrapped = graph_mod._observed(decision_node)
    assert not inspect.iscoroutinefunction(wrapped)
    out = wrapped({"uncertainty_flags": ["low_retrieval_score"], "intent": "shipping"})
    step = out["trace"][0]
    assert step["duration_ms"] is not None
    assert out["action"] == "human_handoff"  # logic Agent 3 KHÔNG đổi vì bị bọc
