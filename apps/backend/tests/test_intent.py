"""Intent Classifier — trích entities (fix bug rỗng) + degrade AN TOÀN offline. KHÔNG network."""

from __future__ import annotations

import pytest

from app.agents.nodes import intent as intent_mod
from app.agents.nodes._entities import extract_entities_rule


def test_extract_order_id_keyword_anchored() -> None:
    # Bug cũ: entities={}. Giờ regex neo từ khoá bắt order_id (giá trị chuỗi).
    assert extract_entities_rule("Đơn hàng 6578 của tôi sắp giao tới nơi chưa?") == {"order_id": "6578"}
    assert extract_entities_rule("cho mình hỏi mã đơn 12345 với")["order_id"] == "12345"
    assert extract_entities_rule("kiểm tra giúp đơn #98765 nhé")["order_id"] == "98765"


def test_wants_human_detects_explicit_requests() -> None:
    # Taxonomy KHÔNG có intent "xin gặp nhân viên" (đo thực tế: LLM xếp mấy câu này vào `greeting`),
    # nên phải bắt bằng LUẬT trên LỜI KHÁCH — không phải dò chữ trong câu trả lời của bot.
    for text in (
        "cho mình gặp nhân viên với",
        "mình muốn nói chuyện với nhân viên thật",
        "cho tôi gặp người hỗ trợ đi, bot không giải quyết được",
        "chuyển cho nhân viên giúp mình",
        "cho gặp cskh",
    ):
        assert intent_mod.wants_human(text), text


def test_wants_human_no_false_positive() -> None:
    # Nhắc tới "nhân viên" KHÔNG phải là xin gặp nhân viên — neo theo ĐỘNG TỪ LIÊN HỆ đứng trước.
    for text in (
        "nhân viên trả lời trống không, thái độ quá tệ",
        "shop có bao nhiêu nhân viên vậy",
        "cho mình hỏi chính sách đổi trả với",
    ):
        assert not intent_mod.wants_human(text), text


def test_extract_no_false_positive_order_id() -> None:
    # Số không neo từ khoá đơn/mã -> KHÔNG nhận nhầm là order_id.
    assert "order_id" not in extract_entities_rule("áo này giá 250000 đồng phải không shop")


def test_extract_size_height_weight() -> None:
    ents = extract_entities_rule("mình cao 1m60 nặng 50kg, lấy size L được không")
    assert ents["size"] == "L"
    assert ents["weight"] == "50kg"
    assert "height" in ents


async def test_classify_degrades_without_key_keeps_order_id(monkeypatch: pytest.MonkeyPatch) -> None:
    # Thiếu key -> degrade llm_unavailable, KHÔNG network — nhưng order_id VẪN có (regex bù).
    monkeypatch.setattr(intent_mod.settings, "llm_api_key", "")
    r = await intent_mod.classify_intent("Đơn hàng 6578 của tôi sắp giao tới nơi chưa?")
    assert r["intent"] == "unknown"
    assert "llm_unavailable" in r["uncertainty_flags"]
    assert r["entities"].get("order_id") == "6578"
    assert r["category"] is None


async def test_classify_llm_off_keeps_order_id(monkeypatch: pytest.MonkeyPatch) -> None:
    # ENABLE_LLM=false -> degrade llm_unavailable; regex vẫn bắt order_id.
    monkeypatch.setattr(intent_mod.settings, "llm_api_key", "sk-test")
    monkeypatch.setattr(intent_mod.settings, "enable_llm", False)
    r = await intent_mod.classify_intent("đơn 6578 sắp tới chưa shop")
    assert r["intent"] == "unknown"
    assert "llm_unavailable" in r["uncertainty_flags"]
    assert r["entities"].get("order_id") == "6578"


async def test_classify_output_is_clean_no_retrieval(monkeypatch: pytest.MonkeyPatch) -> None:
    # Agent 1 SẠCH (§7.1): KHÔNG import rag_service (không retrieval); output KHÔNG có rag_contexts.
    assert not hasattr(intent_mod, "rag_service")
    monkeypatch.setattr(intent_mod.settings, "llm_api_key", "")
    r = await intent_mod.classify_intent("áo này giá bao nhiêu shop")
    assert "rag_contexts" not in r


# ── Resume clarify bằng mã đơn TRƠ (follow-up 09b) ────────────────────────────
# Regex order_id neo TỪ KHOÁ (chống false-positive "giá 250000"), nên "716449" trơ KHÔNG bắt được.
# Trong ngữ cảnh resume (vừa hỏi mã, AWAITING_CUSTOMER) thì số trơ CHÍNH LÀ câu trả lời → luật riêng.


def test_resume_order_code_bare_number_in_awaiting_context() -> None:
    assert intent_mod.resume_order_code("716449", "AWAITING_CUSTOMER", "order_status") == "716449"
    assert intent_mod.resume_order_code("  #716449 ", "AWAITING_CUSTOMER", "refund") == "716449"
    assert intent_mod.resume_order_code("716449.", "AWAITING_CUSTOMER", "exchange") == "716449"


def test_resume_order_code_requires_awaiting_context() -> None:
    # NGOÀI ngữ cảnh resume: số trơ ở tin thường KHÔNG được coi là order_id (giữ chống false-positive).
    assert intent_mod.resume_order_code("716449", "REPLIED", "order_status") is None
    assert intent_mod.resume_order_code("716449", None, "order_status") is None


def test_resume_order_code_requires_clarifiable_prior_intent() -> None:
    assert intent_mod.resume_order_code("716449", "AWAITING_CUSTOMER", "product_price") is None
    assert intent_mod.resume_order_code("716449", "AWAITING_CUSTOMER", None) is None


def test_resume_order_code_rejects_non_bare_message() -> None:
    # Có chữ → đi đường LLM⊕regex cũ; số quá ngắn → không phải mã đơn.
    assert intent_mod.resume_order_code("đơn 716449 sao rồi", "AWAITING_CUSTOMER", "order_status") is None
    assert intent_mod.resume_order_code("mình muốn hoàn đơn", "AWAITING_CUSTOMER", "refund") is None
    assert intent_mod.resume_order_code("12", "AWAITING_CUSTOMER", "order_status") is None


async def test_classify_short_circuits_resume_clarify(monkeypatch: pytest.MonkeyPatch) -> None:
    # Mã trơ + AWAITING + prior_intent=refund → KHÔI PHỤC refund + order_id, KHÔNG gọi LLM (tất định).
    monkeypatch.setattr(intent_mod.settings, "llm_api_key", "sk-test")
    monkeypatch.setattr(intent_mod.settings, "enable_llm", True)

    def _spy() -> object:
        raise AssertionError("KHÔNG được gọi LLM cho mã đơn trơ ở lượt resume")

    monkeypatch.setattr(intent_mod, "get_openai", _spy)
    r = await intent_mod.classify_intent(
        "716449", prior_status="AWAITING_CUSTOMER", prior_intent="refund"
    )
    assert r["intent"] == "refund"  # giữ ĐÚNG intent gốc (không biến thành order_status)
    assert r["entities"]["order_id"] == "716449"
    assert r["uncertainty_flags"] == []  # KHÔNG out_of_domain, KHÔNG llm_unavailable
    assert r["confidence"] == 1.0
    assert r["category"] == "after_sale"


async def test_intent_node_reads_prior_context_from_state(monkeypatch: pytest.MonkeyPatch) -> None:
    # Wiring state → classify: node đọc prior_status/prior_intent để short-circuit resume.
    monkeypatch.setattr(intent_mod.settings, "llm_api_key", "sk-test")
    monkeypatch.setattr(intent_mod.settings, "enable_llm", True)

    def _spy() -> object:
        raise AssertionError("KHÔNG được gọi LLM cho mã đơn trơ ở lượt resume")

    monkeypatch.setattr(intent_mod, "get_openai", _spy)
    out = await intent_mod.intent_node(
        {"input": "716449", "prior_status": "AWAITING_CUSTOMER", "prior_intent": "order_status"}
    )
    assert out["intent"] == "order_status"
    assert out["entities"]["order_id"] == "716449"
    assert out["intent_confidence"] == 1.0
