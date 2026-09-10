"""Intent Classifier — trích entities (fix bug rỗng) + degrade AN TOÀN offline. KHÔNG network."""

from __future__ import annotations

import pytest

from app.agents.nodes import intent as intent_mod
from app.agents.nodes._entities import appears_only_as_amount, extract_entities_rule


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


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        # Số TIỀN / mã khác bị "đơn"/"mã" đứng trước — KHÔNG phải mã đơn (AGENT-01.2, tái hiện live).
        ("Áo này đơn giá 250000 thì ship về Đà Nẵng bao nhiêu?", None),
        ("đơn trên 500k có freeship không", None),
        ("đơn từ 500.000đ", None),
        ("đơn dưới 300k", None),
        ("đơn 500000đ", None),
        ("mã vận đơn GHN123456", None),
        ("mã vận đơn 123456789", None),
        ("mã giảm giá 123456 dùng được không", None),
        ("mã otp 123456", None),
        # Mã đơn thật: chỉ khoảng trắng + từ nối giữa từ khoá và số.
        ("Đơn hàng 6578 của tôi", "6578"),
        ("mã đơn: 716449", "716449"),
        ("order #716449", "716449"),
        ("đơn hàng số 716449", "716449"),
        ("đơn của em 716449 tới đâu", "716449"),
        ("đơn em 716449 k thấy giao", "716449"),  # "k" = "không" (viết tắt chat), không phải "nghìn"
        ("đơn 500k, mã đơn 716449", "716449"),  # bỏ số tiền, lấy mã thật phía sau
        # Cách khách hay viết mã THẬT (review AGENT-01.2): tiền tố "DH" dính số (mã trong DB đều là số —
        # AGENT-01.5), từ đệm khẩu ngữ; "đồng thời/ý" sau mã KHÔNG phải đơn vị tiền.
        ("mã đơn DH865277", "865277"),
        ("đơn hàng DH865277 của em", "865277"),
        ("đơn nè 716449", "716449"),
        ("order no. 716449", "716449"),
        ("đơn hàng bên em 716449", "716449"),
        ("đơn của anh 716449 giao chưa em", "716449"),
        ("tra đơn giúp mình: 716449", "716449"),
        ("đơn 716449 đồng thời cho mình hỏi phí ship", "716449"),
        ("đơn 716449 đồng ý đổi size", "716449"),
        # …nhưng vẫn KHÔNG nhận: tiền tố lạ sau "mã", "đồng" là đơn vị tiền.
        ("mã otp123456", None),
        ("đơn 500000 đồng", None),
        ("đơn 500000 đồng có freeship không", None),
    ],
)
def test_extract_order_id_ignores_amounts(text: str, expected: str | None) -> None:
    assert extract_entities_rule(text).get("order_id") == expected


def test_appears_only_as_amount() -> None:
    assert appears_only_as_amount("Áo này đơn giá 250000 thì ship về Đà Nẵng bao nhiêu?", "250000")
    assert appears_only_as_amount("đơn trên 500000 có freeship không", "500000")
    assert not appears_only_as_amount("đơn 716449 giá 250000", "716449")
    # Mã KHÔNG có trong câu hiện tại → giữ (Agent 1 có thể lấy mã từ lịch sử).
    assert not appears_only_as_amount("đơn đó của mình tới đâu rồi", "716449")
    assert not appears_only_as_amount("bất kỳ", None)
    # "đồng" trong từ ghép KHÔNG phải đơn vị tiền → mã LLM trả đúng thì giữ; "đồng" đứng một mình vẫn là tiền.
    assert not appears_only_as_amount("đơn 716449 đồng thời cho mình hỏi phí ship", "716449")
    assert appears_only_as_amount("đơn 500000 đồng có freeship không", "500000")


class _FakeLLM:
    """Client OpenAI giả cho Agent 1 — trả đúng JSON cho trước (offline)."""

    def __init__(self, content: str) -> None:
        async def create(*args: object, **kwargs: object) -> object:
            msg = type("Msg", (), {"content": content})
            return type("Resp", (), {"choices": [type("Choice", (), {"message": msg})]})

        self.chat = type("Chat", (), {"completions": type("C", (), {"create": staticmethod(create)})})


def _llm_returns(monkeypatch: pytest.MonkeyPatch, content: str) -> None:
    monkeypatch.setattr(intent_mod.settings, "llm_api_key", "sk-test")
    monkeypatch.setattr(intent_mod.settings, "enable_llm", True)
    monkeypatch.setattr(intent_mod, "get_openai", lambda: _FakeLLM(content))


async def test_classify_drops_amount_order_id_from_llm(monkeypatch: pytest.MonkeyPatch) -> None:
    # LLM cũng lấy số tiền làm order_id (tái hiện live) → CÙNG luật số tiền với regex bỏ nó đi.
    _llm_returns(monkeypatch, '{"intent":"shipping","entities":{"order_id":"250000"},"confidence":0.9,"flags":[]}')
    r = await intent_mod.classify_intent("Áo này đơn giá 250000 thì ship về Đà Nẵng bao nhiêu?")
    assert r["intent"] == "shipping"
    assert "order_id" not in r["entities"]


async def test_classify_falls_back_to_regex_code_when_llm_picks_amount(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _llm_returns(monkeypatch, '{"intent":"order_status","entities":{"order_id":"250000"},"confidence":0.9,"flags":[]}')
    r = await intent_mod.classify_intent("đơn 716449 giá 250000 giao chưa")
    assert r["entities"]["order_id"] == "716449"


async def test_classify_keeps_code_resolved_from_history(monkeypatch: pytest.MonkeyPatch) -> None:
    # Mã không có trong câu hiện tại (Agent 1 giải tham chiếu từ lịch sử) → KHÔNG bị luật số tiền xoá.
    _llm_returns(monkeypatch, '{"intent":"order_status","entities":{"order_id":"716449"},"confidence":0.9,"flags":[]}')
    r = await intent_mod.classify_intent(
        "đơn đó của mình tới đâu rồi", [{"sender": "customer", "content": "đơn 716449 tới đâu"}]
    )
    assert r["entities"]["order_id"] == "716449"


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
