"""Agent 2 — Knowledge Agent (retrieval). Degrade AN TOÀN offline + cờ retrieval. KHÔNG network."""

from __future__ import annotations

import pytest

from app.agents.nodes import knowledge as kn


async def test_retrieve_degrades_without_key() -> None:
    # Thiếu key -> degrade no_relevant_knowledge, KHÔNG network.
    with pytest.MonkeyPatch.context() as m:
        m.setattr(kn.settings, "llm_api_key", "")
        r = await kn.retrieve_knowledge("chính sách đổi trả bao nhiêu ngày")
    assert r["rag_contexts"] == []
    assert r["retrieval_confidence"] == 0.0
    assert "no_relevant_knowledge" in r["uncertainty_flags"]


async def test_retrieve_degrades_on_search_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(kn.settings, "llm_api_key", "sk-test")

    async def boom(*args: object, **kwargs: object) -> list[dict]:
        raise RuntimeError("qdrant down")

    monkeypatch.setattr(kn.rag_service, "search", boom)
    r = await kn.retrieve_knowledge("x")
    assert r["rag_contexts"] == []
    assert "no_relevant_knowledge" in r["uncertainty_flags"]


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
    # Lần THỨ HAI vẫn không ra trong CÙNG ca → chuyển người. Suy từ LỜI KHÁCH trong history + sự thật DB,
    # KHÔNG dò chữ trong câu trả lời của bot.
    async def fake_lookup(code: str, customer_id: object) -> None:
        return None

    monkeypatch.setattr(kn.order_service, "lookup", fake_lookup)
    history = [
        {"sender": "customer", "content": "đơn 111222 của mình đâu rồi"},
        {"sender": "ai", "content": "Dạ em không tìm thấy đơn 111222…"},
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
    # Chưa có danh tính khách → lookup luôn scoped theo None → KHÔNG trả đơn của bất kỳ ai.
    async def fake_lookup(code: str, customer_id: object) -> None:
        assert customer_id is None
        return None

    monkeypatch.setattr(kn.order_service, "lookup", fake_lookup)
    r = await kn.resolve_order("order_status", {"order_id": "865276"}, None)
    assert r["order_context"] is None
