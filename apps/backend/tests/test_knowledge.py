"""Agent 2 — Knowledge Agent (retrieval). Degrade AN TOÀN offline + cờ retrieval. KHÔNG network."""

from __future__ import annotations

import pytest

from app.agents.nodes import knowledge as kn
from app.agents.nodes._entities import extract_entities_rule
from app.agents.nodes.decision import BLOCKING_FLAGS


async def test_retrieve_degrades_without_key() -> None:
    # Thiếu key -> degrade no_relevant_knowledge, KHÔNG network.
    with pytest.MonkeyPatch.context() as m:
        m.setattr(kn.settings, "llm_api_key", "")
        r = await kn.retrieve_knowledge("chính sách đổi trả bao nhiêu ngày")
    assert r["rag_contexts"] == []
    assert r["retrieval_confidence"] == 0.0
    assert "no_relevant_knowledge" in r["uncertainty_flags"]


async def test_retrieve_degrades_on_search_error(monkeypatch: pytest.MonkeyPatch) -> None:
    # Qdrant/embed LỖI → `search_error`, KHÔNG `no_relevant_knowledge`: sự cố hạ tầng không được dán nhãn
    # "KB không phủ" trong audit/báo cáo (AGENT-02.2). Cờ vẫn chặn → định tuyến không đổi.
    monkeypatch.setattr(kn.settings, "llm_api_key", "sk-test")

    async def boom(*args: object, **kwargs: object) -> list[dict]:
        raise RuntimeError("qdrant down")

    monkeypatch.setattr(kn.rag_service, "search", boom)
    r = await kn.retrieve_knowledge("x")
    assert r["rag_contexts"] == []
    assert r["retrieval_confidence"] == 0.0
    assert r["uncertainty_flags"] == ["search_error"]
    assert "search_error" in BLOCKING_FLAGS


async def test_retrieve_no_hits_flags_no_relevant(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(kn.settings, "llm_api_key", "sk-test")

    async def empty(*args: object, **kwargs: object) -> list[dict]:
        return []

    monkeypatch.setattr(kn.rag_service, "search", empty)
    r = await kn.retrieve_knowledge("bla bla xyz")
    assert r["rag_contexts"] == []
    assert "no_relevant_knowledge" in r["uncertainty_flags"]


async def test_retrieve_low_score_flags_low_retrieval(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(kn.settings, "llm_api_key", "sk-test")
    monkeypatch.setattr(kn.settings, "retrieval_threshold", 0.35)

    async def hits(*args: object, **kwargs: object) -> list[dict]:
        return [{"text": "đổi trả trong 7 ngày", "source": "kb.pdf", "chunk_index": 0, "score": 0.30}]

    monkeypatch.setattr(kn.rag_service, "search", hits)
    r = await kn.retrieve_knowledge("đổi trả")
    assert r["rag_contexts"][0]["source"] == "kb.pdf"
    assert r["rag_contexts"][0]["text"] == "đổi trả trong 7 ngày"
    assert r["retrieval_confidence"] == 0.30
    assert "low_retrieval_score" in r["uncertainty_flags"]  # 0.30 < retrieval_threshold 0.35


async def test_retrieve_high_score_no_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(kn.settings, "llm_api_key", "sk-test")

    async def hits(*args: object, **kwargs: object) -> list[dict]:
        return [{"text": "phí ship nội thành 20k", "source": "kb.pdf", "chunk_index": 1, "score": 0.85}]

    monkeypatch.setattr(kn.rag_service, "search", hits)
    r = await kn.retrieve_knowledge("phí ship")
    assert r["retrieval_confidence"] == 0.85
    assert r["uncertainty_flags"] == []


async def test_greeting_skips_retrieval_without_any_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    """Lượt xã giao KHÔNG retrieve và KHÔNG phát cờ grounding.

    Nếu phát cờ, Agent 3 (BLOCKING_FLAGS) sẽ escalate một lời chào — đúng lỗi cũ, chỉ đổi tên cờ từ
    `out_of_domain` sang `low_retrieval_score`.
    """
    called = False

    async def spy(*args: object, **kwargs: object) -> list[dict]:
        nonlocal called
        called = True
        return []

    monkeypatch.setattr(kn.settings, "llm_api_key", "sk-test")
    monkeypatch.setattr(kn.rag_service, "search", spy)

    r = await kn.retrieve_knowledge("xin chào shop", intent="greeting")
    assert called is False  # không tốn embedding/Qdrant cho lời chào
    assert r["rag_contexts"] == []
    assert r["uncertainty_flags"] == []  # RỖNG — khác hẳn nhánh degrade


async def test_knowledge_node_passes_intent_and_types_contexts(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict[str, object] = {}

    async def spy(query: str, top_k: int = 4, intent: str | None = None) -> list[dict]:
        seen["query"], seen["intent"] = query, intent
        return [
            {"text": "1. Hỏi mã đơn.", "source": "case/don-giao-cham.md", "chunk_index": 2,
             "type": "case", "title": "Đơn giao chậm", "question": None, "score": 0.91}
        ]

    monkeypatch.setattr(kn.settings, "llm_api_key", "sk-test")
    monkeypatch.setattr(kn.rag_service, "search", spy)

    out = await kn.knowledge_node({"input": "đơn của em lâu quá", "intent": "order_status"})
    assert seen == {"query": "đơn của em lâu quá", "intent": "order_status"}
    ctx = out["rag_contexts"][0]
    assert ctx["type"] == "case" and ctx["title"] == "Đơn giao chậm"  # Agent 4 gắn nhãn loại (P5)
    assert out["trace"][0]["detail"]["skipped"] is False


async def test_knowledge_node_greeting_marks_skipped_in_trace(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(kn.settings, "llm_api_key", "sk-test")
    out = await kn.knowledge_node({"input": "xin chào", "intent": "greeting"})
    assert out["uncertainty_flags"] == []
    assert out["trace"][0]["detail"]["skipped"] is True  # audit phân biệt "bỏ qua" với "tìm mà rỗng"


# ── Tra đơn SCOPED (plan §2.3) — 3 nhánh. KHÔNG chạm DB thật: stub order_service.lookup ────────────
_CUSTOMER = "11111111-1111-1111-1111-111111111111"


class _FakeOrder:
    order_code, status, items_summary, region = "865276", "delivering", "Áo thun x1", "Hà Nội"
    ordered_at = shipped_at = delivered_at = cancelled_at = estimated_delivery = None
    tracking_code = "GHN123456789"


async def test_resolve_order_found_gives_context_no_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict[str, object] = {}

    async def fake_lookup(code: str, customer_id: object) -> _FakeOrder:
        seen["code"], seen["customer_id"] = code, str(customer_id)
        return _FakeOrder()

    monkeypatch.setattr(kn.order_service, "lookup", fake_lookup)
    r = await kn.resolve_order("order_status", {"order_id": "865276"}, _CUSTOMER)
    # Tra ĐÚNG mã + ĐÚNG chủ đơn (scoped) — không lộ đơn người khác.
    assert seen == {"code": "865276", "customer_id": _CUSTOMER}
    assert r["uncertainty_flags"] == []
    assert r["order_context"]["Mã đơn"] == "865276"
    assert r["order_context"]["Trạng thái"] == "đang trên đường giao"  # nhãn VI, không phải mã enum


async def test_resolve_order_not_found_informs_instead_of_escalating(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # LẦN ĐẦU không thấy (mã lạ HOẶC của người khác — cùng kết quả None, không lộ sự tồn tại):
    # BÁO cho khách kiểm tra lại mã, KHÔNG escalate. Phần lớn ca này là khách gõ nhầm.
    async def fake_lookup(code: str, customer_id: object) -> None:
        return None

    monkeypatch.setattr(kn.order_service, "lookup", fake_lookup)
    r = await kn.resolve_order("order_status", {"order_id": "9999"}, _CUSTOMER)
    assert r["order_context"] is None
    assert r["order_not_found"] == "9999"  # Agent 4 nhắc lại đúng mã khách đưa
    assert r["uncertainty_flags"] == []


async def test_resolve_order_second_failure_in_case_escalates(monkeypatch: pytest.MonkeyPatch) -> None:
    # Lần THỨ HAI vẫn không ra trong CÙNG ca → chuyển người. Lần hỏng trước = lượt Agent 4 đã PHÁT câu "không tìm
    # thấy" CỐ ĐỊNH (khớp nguyên văn hằng, không dò chữ mờ) + tra lại vẫn không ra.
    async def fake_lookup(code: str, customer_id: object) -> None:
        return None

    monkeypatch.setattr(kn.order_service, "lookup", fake_lookup)
    history = [
        {"sender": "customer", "content": "đơn 111222 của mình đâu rồi"},
        {"sender": "ai", "content": kn.ORDER_NOT_FOUND_TEMPLATE.format(code="111222")},
    ]
    r = await kn.resolve_order("order_status", {"order_id": "9999"}, _CUSTOMER, history)
    assert r["order_not_found"] is None
    assert r["uncertainty_flags"] == ["order_unresolved"]


async def test_resolve_order_prior_success_does_not_escalate(monkeypatch: pytest.MonkeyPatch) -> None:
    # Lượt trước tra RA đơn, lượt này gõ nhầm mã khác → vẫn chỉ là lần hỏng ĐẦU TIÊN → báo, đừng escalate.
    async def fake_lookup(code: str, customer_id: object):  # type: ignore[no-untyped-def]
        return _FakeOrder() if code == "111222" else None

    monkeypatch.setattr(kn.order_service, "lookup", fake_lookup)
    history = [{"sender": "customer", "content": "đơn 111222 tới đâu rồi"}]
    r = await kn.resolve_order("order_status", {"order_id": "9999"}, _CUSTOMER, history)
    assert r["order_not_found"] == "9999"
    assert r["uncertainty_flags"] == []


async def test_resolve_order_no_code_does_not_escalate(monkeypatch: pytest.MonkeyPatch) -> None:
    # KHÔNG mã đơn → KHÔNG cờ (Agent 4 hỏi mã); và KHÔNG được gọi lookup.
    async def boom(*args: object, **kwargs: object) -> None:
        raise AssertionError("không được tra đơn khi khách chưa đưa mã")

    monkeypatch.setattr(kn.order_service, "lookup", boom)
    r = await kn.resolve_order("order_status", {}, _CUSTOMER)
    assert r == {"order_context": None, "order_not_found": None, "uncertainty_flags": []}


async def test_resolve_order_skips_non_order_intent(monkeypatch: pytest.MonkeyPatch) -> None:
    # Intent không gắn với đơn (hỏi size) → không tra đơn dù câu có con số trông như mã.
    async def boom(*args: object, **kwargs: object) -> None:
        raise AssertionError("không được tra đơn cho intent ngoài ORDER_INTENTS")

    monkeypatch.setattr(kn.order_service, "lookup", boom)
    r = await kn.resolve_order("size_consulting", {"order_id": "865276"}, _CUSTOMER)
    assert r == {"order_context": None, "order_not_found": None, "uncertainty_flags": []}


async def test_resolve_order_db_error_escalates(monkeypatch: pytest.MonkeyPatch) -> None:
    # DB lỗi → escalate, KHÔNG hạ xuống "không tìm thấy": lookup HỎNG khác lookup TRẢ RỖNG, nói "không thấy
    # đơn trong tài khoản của bạn" khi chưa tra được là nói SAI.
    async def boom(*args: object, **kwargs: object) -> None:
        raise RuntimeError("db down")

    monkeypatch.setattr(kn.order_service, "lookup", boom)
    r = await kn.resolve_order("order_status", {"order_id": "865276"}, _CUSTOMER)
    assert r["order_not_found"] is None
    assert r["uncertainty_flags"] == ["order_unresolved"]


async def test_resolve_order_without_identity_never_leaks(monkeypatch: pytest.MonkeyPatch) -> None:
    # Chưa có (hoặc hỏng) danh tính khách → KHÔNG trả đơn của bất kỳ ai, VÀ cũng KHÔNG nói "không thấy đơn trong
    # tài khoản của anh/chị": chưa tra được ≠ tra rỗng (AGENT-01.4) → order_unresolved (chuyển người).
    async def fake_lookup(code: str, customer_id: object) -> None:
        assert customer_id is None
        return None

    monkeypatch.setattr(kn.order_service, "lookup", fake_lookup)
    for customer_id in (None, "khong-phai-uuid"):
        r = await kn.resolve_order("order_status", {"order_id": "865276"}, customer_id)
        assert r["order_context"] is None
        assert r["order_not_found"] is None  # KHÔNG phát câu "không tìm thấy đơn"
        assert r["uncertainty_flags"] == ["order_unresolved"]


async def test_shipping_without_identity_answers_policy(monkeypatch: pytest.MonkeyPatch) -> None:
    # Không danh tính (nhánh WS AI-only): số trong câu hỏi ship thường là TIỀN → trả lời chính sách như nhánh
    # "không thấy", KHÔNG order_unresolved (review AGENT-01.4). Intent đơn khác vẫn order_unresolved (test trên).
    async def boom(*args: object, **kwargs: object) -> None:
        raise AssertionError("không danh tính → không được tra đơn")

    monkeypatch.setattr(kn.order_service, "lookup", boom)
    r = await kn.resolve_order("shipping", {"order_id": "500000"}, None)
    assert r == {"order_context": None, "order_not_found": None, "uncertainty_flags": []}


# ── refund/exchange/complaint cũng tra đơn scoped (AGENT-01.1) + shipping không báo "không thấy" (AGENT-01.2) ──
_OTHER = "22222222-2222-2222-2222-222222222222"


def _scoped_db(owners: dict[str, str]):  # type: ignore[no-untyped-def]
    """`order_service.lookup` giả: trả đơn CHỈ khi mã có VÀ thuộc đúng khách (như truy vấn scoped thật)."""

    async def lookup(code: str, customer_id: object) -> _FakeOrder | None:
        if owners.get(code) != str(customer_id):
            return None
        order = _FakeOrder()
        order.order_code = code
        return order

    return lookup


@pytest.mark.parametrize("intent", ["refund", "exchange", "complaint"])
async def test_after_sale_intents_look_the_order_up(monkeypatch: pytest.MonkeyPatch, intent: str) -> None:
    monkeypatch.setattr(kn.order_service, "lookup", _scoped_db({"716449": _CUSTOMER}))
    r = await kn.resolve_order(intent, {"order_id": "716449"}, _CUSTOMER)
    assert r["order_context"]["Mã đơn"] == "716449"
    assert r["uncertainty_flags"] == []


async def test_refund_other_customers_code_same_as_nonexistent(monkeypatch: pytest.MonkeyPatch) -> None:
    # Mã của KHÁCH KHÁC và mã KHÔNG tồn tại → CÙNG kết quả: không lộ sự tồn tại của đơn người khác.
    monkeypatch.setattr(kn.order_service, "lookup", _scoped_db({"794798": _OTHER}))
    of_other = await kn.resolve_order("refund", {"order_id": "794798"}, _CUSTOMER)
    monkeypatch.setattr(kn.order_service, "lookup", _scoped_db({}))
    missing = await kn.resolve_order("refund", {"order_id": "794798"}, _CUSTOMER)
    assert of_other == missing == {"order_context": None, "order_not_found": "794798", "uncertainty_flags": []}


async def test_shipping_not_found_gives_no_order_signal(monkeypatch: pytest.MonkeyPatch) -> None:
    # Số trong câu hỏi ship thường là TIỀN → tra không ra thì KHÔNG "không tìm thấy đơn", KHÔNG cờ — kể cả
    # khi ca đã từng có mã hỏng (không escalate một câu hỏi phí ship).
    monkeypatch.setattr(kn.order_service, "lookup", _scoped_db({}))
    history = [{"sender": "customer", "content": "đơn 111222 của mình đâu rồi"}]
    r = await kn.resolve_order("shipping", {"order_id": "500000"}, _CUSTOMER, history)
    assert r == {"order_context": None, "order_not_found": None, "uncertainty_flags": []}


async def test_shipping_found_order_still_gives_context(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(kn.order_service, "lookup", _scoped_db({"716449": _CUSTOMER}))
    r = await kn.resolve_order("shipping", {"order_id": "716449"}, _CUSTOMER)
    assert r["order_context"]["Mã đơn"] == "716449"


async def test_knowledge_node_shipping_amount_question_answers_policy(monkeypatch: pytest.MonkeyPatch) -> None:
    # Tái hiện live: "đơn 500000 có được freeship không" → regex vẫn ra 500000 (không có đơn vị tiền), nhưng
    # shipping tra không ra → KHÔNG order_not_found, KHÔNG cờ đơn → Agent 4 trả lời chính sách freeship.
    text = "đơn 500000 có được freeship không"

    async def hits(*args: object, **kwargs: object) -> list[dict]:
        return [{"text": "Miễn phí ship cho đơn từ 500.000đ.", "source": "facts", "score": 0.82}]

    monkeypatch.setattr(kn.settings, "llm_api_key", "sk-test")
    monkeypatch.setattr(kn.rag_service, "search", hits)
    monkeypatch.setattr(kn.order_service, "lookup", _scoped_db({}))
    out = await kn.knowledge_node(
        {"input": text, "intent": "shipping", "entities": extract_entities_rule(text), "customer_id": _CUSTOMER}
    )
    assert out["order_not_found"] is None
    assert out["order_context"] is None
    assert out["uncertainty_flags"] == []


# ── Chỉ lượt ĐÃ BÁO "không tìm thấy" mới là một lần hỏng (review AGENT-01.2) ──────────────────────────────
@pytest.mark.parametrize(
    "earlier",
    [
        "đơn 500000 có được freeship không shop",  # số TIỀN ở lượt hỏi ship (regex vẫn ra 500000)
        "0901234567",  # số điện thoại gửi trơ
    ],
)
async def test_numbers_never_reported_not_found_do_not_count(monkeypatch: pytest.MonkeyPatch, earlier: str) -> None:
    monkeypatch.setattr(kn.order_service, "lookup", _scoped_db({}))
    history = [{"sender": "customer", "content": earlier}, {"sender": "ai", "content": "Dạ vâng ạ."}]
    r = await kn.resolve_order("order_status", {"order_id": "716448"}, _CUSTOMER, history)
    # Mã gõ nhầm LẦN ĐẦU → báo "không tìm thấy", KHÔNG chuyển người vì một con số chưa từng được tra như mã.
    assert r == {"order_context": None, "order_not_found": "716448", "uncertainty_flags": []}


async def test_prefixed_code_reported_not_found_counts(monkeypatch: pytest.MonkeyPatch) -> None:
    # Mã LLM tách từ "mã đơn DH716448" đã được báo "không tìm thấy" → mã sai lần hai chuyển người, không lặp mãi.
    monkeypatch.setattr(kn.order_service, "lookup", _scoped_db({}))
    history = [
        {"sender": "customer", "content": "mã đơn DH716448 tới đâu rồi shop"},
        {"sender": "ai", "content": kn.ORDER_NOT_FOUND_TEMPLATE.format(code="716448")},
    ]
    r = await kn.resolve_order("order_status", {"order_id": "716447"}, _CUSTOMER, history)
    assert r["uncertainty_flags"] == ["order_unresolved"]


# ── Lượt resume mã trơ + miễn cờ grounding khi đã có đơn (AGENT-02.1) + số đo con (PERF-01.2) ───────────
_RESUME_HISTORY = [
    {"sender": "customer", "content": "đơn của mình tới đâu rồi ạ"},
    {"sender": "ai", "content": "Dạ anh/chị cho em xin mã đơn hàng để em kiểm tra giúp ạ."},
]


def _search(monkeypatch: pytest.MonkeyPatch, score: float | None) -> list[str]:
    """Qdrant giả: `score=None` → ném lỗi (hạ tầng). Trả list query đã truy hồi."""
    queries: list[str] = []

    async def search(query: str, top_k: int = 4, intent: str | None = None) -> list[dict]:
        queries.append(query)
        if score is None:
            raise RuntimeError("qdrant down")
        return [{"text": "chính sách", "source": "kb.md", "score": score}]

    monkeypatch.setattr(kn.settings, "llm_api_key", "sk-test")
    monkeypatch.setattr(kn.settings, "retrieval_threshold", 0.40)
    monkeypatch.setattr(kn.rag_service, "search", search)
    return queries


def _order_state(text: str, code: str, **extra: object) -> dict:
    return {"input": text, "intent": "order_status", "entities": {"order_id": code},
            "customer_id": _CUSTOMER, **extra}


def test_original_question_skips_bare_codes() -> None:
    history = [
        *_RESUME_HISTORY,
        {"sender": "customer", "content": "716448"},  # lần đáp mã trước (gõ nhầm) — không phải câu hỏi gốc
        {"sender": "ai", "content": "Dạ em không tìm thấy đơn 716448 trong tài khoản của anh/chị ạ."},
    ]
    assert kn._original_question(history) == "đơn của mình tới đâu rồi ạ"
    assert kn._original_question([]) is None


async def test_resume_turn_retrieves_with_original_question(monkeypatch: pytest.MonkeyPatch) -> None:
    queries = _search(monkeypatch, 0.8)
    monkeypatch.setattr(kn.order_service, "lookup", _scoped_db({"716449": _CUSTOMER}))
    out = await kn.knowledge_node(
        _order_state("716449", "716449", history=_RESUME_HISTORY,
                     prior_status="AWAITING_CUSTOMER", prior_intent="order_status")
    )
    assert queries == ["đơn của mình tới đâu rồi ạ"]  # KHÔNG truy hồi bằng con số
    assert out["trace"][0]["detail"]["resumed"] is True


async def test_resume_turn_without_history_falls_back_to_input(monkeypatch: pytest.MonkeyPatch) -> None:
    queries = _search(monkeypatch, 0.8)
    monkeypatch.setattr(kn.order_service, "lookup", _scoped_db({"716449": _CUSTOMER}))
    await kn.knowledge_node(
        _order_state("716449", "716449", history=[], prior_status="AWAITING_CUSTOMER", prior_intent="order_status")
    )
    assert queries == ["716449"]


async def test_non_resume_turn_retrieves_with_input(monkeypatch: pytest.MonkeyPatch) -> None:
    queries = _search(monkeypatch, 0.8)
    monkeypatch.setattr(kn.order_service, "lookup", _scoped_db({"716449": _CUSTOMER}))
    out = await kn.knowledge_node(
        _order_state("đơn 716449 tới đâu", "716449", history=_RESUME_HISTORY,
                     prior_status="REPLIED", prior_intent="order_status")
    )
    assert queries == ["đơn 716449 tới đâu"]
    assert out["trace"][0]["detail"]["resumed"] is False


@pytest.mark.parametrize(("score", "waived"), [(0.2, "low_retrieval_score"), (None, "search_error")])
async def test_found_order_waives_retrieval_grounding_flags(
    monkeypatch: pytest.MonkeyPatch, score: float | None, waived: str
) -> None:
    _search(monkeypatch, score)
    monkeypatch.setattr(kn.order_service, "lookup", _scoped_db({"716449": _CUSTOMER}))
    out = await kn.knowledge_node(_order_state("đơn 716449 tới đâu", "716449"))
    assert out["order_context"]["Mã đơn"] == "716449"
    assert out["uncertainty_flags"] == []  # dữ liệu đơn LÀ grounding → không chặn
    assert out["trace"][0]["detail"]["waived_flags"] == [waived]  # nhưng audit vẫn thấy


async def test_grounding_flags_still_block_without_order(monkeypatch: pytest.MonkeyPatch) -> None:
    # Miễn cờ CHỈ khi đơn tra ĐƯỢC: không thấy đơn → cờ grounding giữ nguyên.
    _search(monkeypatch, 0.2)
    monkeypatch.setattr(kn.order_service, "lookup", _scoped_db({}))
    out = await kn.knowledge_node(_order_state("đơn 716449 tới đâu", "716449"))
    assert out["order_not_found"] == "716449"
    assert out["uncertainty_flags"] == ["low_retrieval_score"]
    assert out["trace"][0]["detail"]["waived_flags"] == []


async def test_order_lookup_error_keeps_every_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    _search(monkeypatch, 0.2)

    async def boom(*args: object, **kwargs: object) -> None:
        raise RuntimeError("db down")

    monkeypatch.setattr(kn.order_service, "lookup", boom)
    out = await kn.knowledge_node(_order_state("đơn 716449 tới đâu", "716449"))
    assert out["uncertainty_flags"] == ["low_retrieval_score", "order_unresolved"]


async def test_knowledge_node_records_sub_timings(monkeypatch: pytest.MonkeyPatch) -> None:
    _search(monkeypatch, 0.8)
    monkeypatch.setattr(kn.order_service, "lookup", _scoped_db({"716449": _CUSTOMER}))
    out = await kn.knowledge_node(_order_state("đơn 716449 tới đâu", "716449"))
    timings = out["trace"][0]["detail"]["timings"]
    assert set(timings) == {"retrieval_ms", "order_ms"}
    assert all(isinstance(v, int) and v >= 0 for v in timings.values())
