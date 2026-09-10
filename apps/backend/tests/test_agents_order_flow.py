"""Luồng đơn hàng XUYÊN NODE (Agent 1 → 2 → 3 → 4) trên graph thật (`run_pipeline`) — offline.

Stub đúng ba biên I/O: LLM (`get_openai` / `classify_intent`), Qdrant (`rag_service.search`) và DB đơn
(`order_service.lookup`, scoped như truy vấn thật). Kiểm WIRING giữa các node, không chỉ từng hàm.
"""

from __future__ import annotations

import uuid
from typing import Any

import pytest

from app.agents import graph as graph_mod
from app.agents.nodes import intent as intent_mod
from app.agents.nodes import knowledge as kn
from app.agents.nodes import response as resp
from app.models.audit_log import AuditLog
from app.models.enums import TurnOutcome
from app.services import audit_service, report_service
from app.services.escalation_service import build_escalation_card

_CUSTOMER = "11111111-1111-1111-1111-111111111111"
_OTHER = "22222222-2222-2222-2222-222222222222"


class _Order:
    status, items_summary, region = "delivering", "Áo thun x1", "Hà Nội"
    ordered_at = shipped_at = delivered_at = cancelled_at = estimated_delivery = None
    tracking_code = "GHN123456789"

    def __init__(self, code: str) -> None:
        self.order_code = code


def _scoped_db(monkeypatch: pytest.MonkeyPatch, owners: dict[str, str]) -> None:
    """Đơn chỉ trả về khi mã có VÀ thuộc đúng khách — mã người khác = mã không tồn tại (None)."""

    async def lookup(code: str, customer_id: object) -> _Order | None:
        return _Order(code) if owners.get(code) == str(customer_id) else None

    monkeypatch.setattr(kn.order_service, "lookup", lookup)


def _search_returns(monkeypatch: pytest.MonkeyPatch, score: float) -> list[str]:
    """Qdrant giả trả 1 hit với điểm cho trước; trả về list các query đã được truy hồi."""
    queries: list[str] = []

    async def search(query: str, top_k: int = 4, intent: str | None = None) -> list[dict]:
        queries.append(query)
        return [
            {"text": "Đổi/trả trong 30 ngày kể từ khi nhận.", "source": "reference/chinh-sach-doi-tra.md",
             "type": "reference", "title": "Đổi trả", "score": score}
        ]

    monkeypatch.setattr(kn.rag_service, "search", search)
    return queries


def _classify_as(monkeypatch: pytest.MonkeyPatch, intent: str, entities: dict[str, str]) -> None:
    async def fake(text: str, history: object = None, **_kw: object) -> dict[str, Any]:
        return {"intent": intent, "category": None, "entities": dict(entities), "confidence": 0.9,
                "uncertainty_flags": []}

    monkeypatch.setattr(intent_mod, "classify_intent", fake)


class _CapturingLLM:
    """Client OpenAI giả cho Agent 4 — ghi lại messages mỗi lần gọi (kiểm prompt nhận được gì)."""

    def __init__(self, reply: str = "Dạ đơn của anh/chị đang trên đường giao ạ.") -> None:
        self.calls: list[list[dict[str, str]]] = []
        calls = self.calls

        async def create(*args: object, **kwargs: Any) -> object:
            calls.append(kwargs["messages"])
            msg = type("Msg", (), {"content": reply})
            return type("Resp", (), {"choices": [type("Choice", (), {"message": msg})]})

        self.chat = type("Chat", (), {"completions": type("C", (), {"create": staticmethod(create)})})


@pytest.fixture(autouse=True)
def _offline(monkeypatch: pytest.MonkeyPatch) -> _CapturingLLM:
    # `settings` là object DÙNG CHUNG → retrieve_knowledge + generate_reply đều không degrade vì thiếu key.
    monkeypatch.setattr(kn.settings, "llm_api_key", "sk-test")
    monkeypatch.setattr(kn.settings, "retrieval_threshold", 0.40)  # ngưỡng đo thật, không phụ thuộc .env máy
    monkeypatch.setattr(resp, "is_within_support_hours", lambda now: True)  # handoff notice tất định
    llm = _CapturingLLM()
    monkeypatch.setattr(resp, "get_openai", lambda: llm)
    return llm


# ── AGENT-01.1: refund/exchange/complaint tra đơn scoped trước khi trả lời ────
async def test_refund_own_code_order_context_reaches_agent4(
    monkeypatch: pytest.MonkeyPatch, _offline: _CapturingLLM
) -> None:
    _classify_as(monkeypatch, "refund", {"order_id": "716449"})
    _search_returns(monkeypatch, 0.8)
    _scoped_db(monkeypatch, {"716449": _CUSTOMER})

    final = await graph_mod.run_pipeline(input_text="đơn 716449 bị lỗi, cho em hoàn tiền", customer_id=_CUSTOMER)

    assert final["action"] == "auto_reply"
    assert final["order_context"]["Mã đơn"] == "716449"
    user_prompt = _offline.calls[0][1]["content"]  # dữ liệu đơn vào đúng prompt Agent 4
    assert "ĐƠN HÀNG CỦA KHÁCH" in user_prompt and "Mã đơn: 716449" in user_prompt


async def test_refund_other_customers_code_gets_fixed_not_found(
    monkeypatch: pytest.MonkeyPatch, _offline: _CapturingLLM
) -> None:
    # Mã của khách KHÁC → câu "không tìm thấy" CỐ ĐỊNH (như mã không tồn tại), KHÔNG soạn nháp hoàn tiền.
    _classify_as(monkeypatch, "refund", {"order_id": "794798"})
    _search_returns(monkeypatch, 0.8)
    _scoped_db(monkeypatch, {"794798": _OTHER})

    final = await graph_mod.run_pipeline(input_text="mình muốn hoàn tiền đơn 794798", customer_id=_CUSTOMER)

    assert final["order_context"] is None
    assert final["result"]["reply"] == resp.ORDER_NOT_FOUND_TEMPLATE.format(code="794798")
    assert _offline.calls == []  # câu cố định, KHÔNG qua LLM


# ── AGENT-02.1: lượt resume mã TRƠ được trả lời, không bị escalate oan ────────
@pytest.mark.parametrize(
    ("prior_intent", "question"),
    [("order_status", "đơn của mình tới đâu rồi ạ"), ("refund", "mình muốn hoàn tiền đơn hàng")],
)
async def test_bare_code_resume_turn_is_answered_not_escalated(
    monkeypatch: pytest.MonkeyPatch, _offline: _CapturingLLM, prior_intent: str, question: str
) -> None:
    # Tái hiện live: bot hỏi mã → khách đáp "865277" → đơn TRA ĐƯỢC nhưng cosine của con số là 0.253 < 0.40
    # → trước đây human_handoff với blocking_flags=['low_retrieval_score'].
    queries = _search_returns(monkeypatch, 0.253)
    _scoped_db(monkeypatch, {"865277": _CUSTOMER})
    history = [
        {"sender": "customer", "content": question},
        {"sender": "ai", "content": resp.CLARIFY_QUESTION["order_id"]},
    ]

    final = await graph_mod.run_pipeline(
        input_text="865277", history=history, customer_id=_CUSTOMER,
        prior_status="AWAITING_CUSTOMER", prior_intent=prior_intent,
    )

    assert final["intent"] == prior_intent  # Agent 1 khôi phục intent gốc (tất định, không LLM)
    assert queries == [question]  # truy hồi bằng CÂU HỎI GỐC, không bằng con số
    decision = next(t for t in final["trace"] if t["node"] == "decision")
    assert decision["detail"]["blocking_flags"] == []
    assert final["action"] == "auto_reply"
    assert final["status"] == "REPLIED"
    assert "Mã đơn: 865277" in _offline.calls[0][1]["content"]  # dữ liệu đơn tới được Agent 4


# ── AGENT-02.3: "không tìm thấy" chờ khách → mã trơ resume; mã sai lần hai → chuyển người ──
async def _turn(text: str, history: list[dict[str, str]], prior: dict[str, Any] | None) -> dict[str, Any]:
    """Một lượt như WS chạy: `history` = các lượt TRƯỚC; prior_status/prior_intent = status lượt trước + intent
    đã lưu (WS chỉ lưu `current_intent` khi vào AWAITING_CUSTOMER). Xong thì nối lượt này vào `history`."""
    prior = prior or {}
    awaiting = prior.get("status") == "AWAITING_CUSTOMER"
    final = await graph_mod.run_pipeline(
        input_text=text, history=list(history), customer_id=_CUSTOMER,
        prior_status=prior.get("status"), prior_intent=prior.get("intent") if awaiting else None,
    )
    history += [{"sender": "customer", "content": text}, {"sender": "ai", "content": final["result"]["reply"]}]
    return final


async def _not_found_first_turn(monkeypatch: pytest.MonkeyPatch, history: list[dict[str, str]]) -> dict[str, Any]:
    real_classify = intent_mod.classify_intent
    _classify_as(monkeypatch, "order_status", {"order_id": "716448"})
    _search_returns(monkeypatch, 0.8)
    _scoped_db(monkeypatch, {"716449": _CUSTOMER})
    t1 = await _turn("đơn 716448 tới đâu rồi", history, None)
    assert t1["result"]["reply"] == resp.ORDER_NOT_FOUND_TEMPLATE.format(code="716448")
    assert t1["status"] == "AWAITING_CUSTOMER"  # trước đây REPLIED → mã trơ lượt sau không resume được
    monkeypatch.setattr(intent_mod, "classify_intent", real_classify)  # lượt sau: Agent 1 thật (short-circuit)
    return t1


async def test_not_found_then_bare_code_resumes_and_answers(monkeypatch: pytest.MonkeyPatch) -> None:
    history: list[dict[str, str]] = []
    t1 = await _not_found_first_turn(monkeypatch, history)
    t2 = await _turn("716449", history, t1)
    assert t2["intent"] == "order_status" and t2["entities"]["order_id"] == "716449"
    assert t2["action"] == "auto_reply" and t2["status"] == "REPLIED"
    assert t2["order_context"]["Mã đơn"] == "716449"


async def test_not_found_then_second_wrong_bare_code_escalates(monkeypatch: pytest.MonkeyPatch) -> None:
    history: list[dict[str, str]] = []
    t1 = await _not_found_first_turn(monkeypatch, history)
    t2 = await _turn("716447", history, t1)
    assert t2["intent"] == "order_status"  # resume tất định vẫn giữ intent gốc
    assert t2["status"] == "IN_HUMAN_QUEUE"
    assert "order_unresolved" in t2["escalation_reason"]
    assert t2["result"]["reply"] == resp.HANDOFF_NOTICE


async def test_clarify_then_two_wrong_bare_codes_escalates(monkeypatch: pytest.MonkeyPatch) -> None:
    # Hỏi mã (clarify) → mã trơ sai → "không tìm thấy" (chờ tiếp) → mã trơ sai lần hai → chuyển người, KHÔNG lặp.
    real_classify = intent_mod.classify_intent
    _classify_as(monkeypatch, "order_status", {})
    _search_returns(monkeypatch, 0.8)
    _scoped_db(monkeypatch, {"716449": _CUSTOMER})
    history: list[dict[str, str]] = []
    t1 = await _turn("đơn của mình tới đâu rồi ạ", history, None)
    assert t1["result"]["branch"] == "clarify" and t1["status"] == "AWAITING_CUSTOMER"

    monkeypatch.setattr(intent_mod, "classify_intent", real_classify)
    t2 = await _turn("716448", history, t1)
    assert t2["result"]["reply"] == resp.ORDER_NOT_FOUND_TEMPLATE.format(code="716448")
    assert t2["status"] == "AWAITING_CUSTOMER"
    t3 = await _turn("716447", history, t2)
    assert t3["status"] == "IN_HUMAN_QUEUE"
    assert "order_unresolved" in t3["escalation_reason"]


# ── AGENT-01.2 (review): số tiền ở lượt hỏi ship KHÔNG làm bẩn bộ đếm mã hỏng của lượt sau ──
async def test_amount_in_shipping_turn_does_not_poison_later_lookup(monkeypatch: pytest.MonkeyPatch) -> None:
    # Tái hiện live: "đơn 500000 có được freeship không" — regex lẫn LLM vẫn ra 500000 — được trả lời chính sách;
    # lượt SAU khách gõ nhầm mã LẦN ĐẦU phải nhận câu "không tìm thấy", KHÔNG bị chuyển người vì con số 500000.
    _search_returns(monkeypatch, 0.8)
    _scoped_db(monkeypatch, {"716449": _CUSTOMER})
    history: list[dict[str, str]] = []
    _classify_as(monkeypatch, "shipping", {"order_id": "500000"})
    t1 = await _turn("đơn 500000 có được freeship không shop", history, None)
    assert t1["action"] == "auto_reply" and t1["status"] == "REPLIED"
    assert t1["order_not_found"] is None

    _classify_as(monkeypatch, "order_status", {"order_id": "716448"})
    t2 = await _turn("đơn 716448 tới đâu rồi", history, t1)
    assert t2["action"] == "auto_reply"
    assert t2["result"]["reply"] == resp.ORDER_NOT_FOUND_TEMPLATE.format(code="716448")


# ── AGENT-03.1: lượt Agent 4 phải fallback → chuyển người, card mang đúng lý do ──
async def test_fallback_turn_is_handed_to_a_human_with_reason(monkeypatch: pytest.MonkeyPatch) -> None:
    _classify_as(monkeypatch, "product_price", {})
    _search_returns(monkeypatch, 0.8)
    monkeypatch.setattr(resp, "get_openai", lambda: _CapturingLLM(reply="   "))  # LLM trả rỗng → phanh fallback
    question = "áo thun basic giá bao nhiêu"

    final = await graph_mod.run_pipeline(input_text=question, customer_id=_CUSTOMER)

    assert final["action"] == "auto_reply"  # Agent 3 cho trả lời…
    assert final["status"] == "IN_HUMAN_QUEUE"  # …nhưng Agent 4 không có câu grounded → chuyển người
    assert final["result"]["reply"] == resp.HANDOFF_NOTICE
    assert final["require_human_handoff"] is True
    assert final["escalation_reason"] == "blocking_flags=['hallucination_risk']"
    assert build_escalation_card(final, question)["escalation_reason"] == "blocking_flags=['hallucination_risk']"


async def test_fallback_turn_audit_gives_the_reason_to_agent4_not_agent3(monkeypatch: pytest.MonkeyPatch) -> None:
    # Repro review (AGENT-03.1): dòng audit decision của lượt fallback từng mang lý do CỦA Agent 4 → quy cho Agent 3 một
    # lý do nó không phát ra (NFR-4). Báo cáo + tiêu đề lượt vẫn phải ra hallucination_risk.
    _classify_as(monkeypatch, "product_price", {})
    _search_returns(monkeypatch, 0.8)
    monkeypatch.setattr(resp, "get_openai", lambda: _CapturingLLM(reply="   "))  # LLM trả rỗng → phanh fallback
    question = "áo thun basic giá bao nhiêu"
    final = await graph_mod.run_pipeline(input_text=question, customer_id=_CUSTOMER)

    rows = audit_service.build_turn_rows(
        turn_id=uuid.uuid4(), conversation_id=uuid.uuid4(), customer_text=question, final=final,
        reply=final["result"]["reply"], outcome=TurnOutcome.QUEUED_FOR_HUMAN, total_ms=1200,
    )
    dec = next(r for r in rows if r["node"] == "decision")
    assert (dec["action"], dec["escalation_reason"], dec["detail"]["blocking_flags"]) == ("auto_reply", None, [])
    view = report_service.build_turn_view([AuditLog(**{**r, "created_at": None}) for r in rows])
    assert view is not None and view.escalation_reason == "blocking_flags=['hallucination_risk']"
    assert report_service.summarize([view])["escalation_reasons"][0]["flag"] == "hallucination_risk"
