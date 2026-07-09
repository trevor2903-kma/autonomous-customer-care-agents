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
    # Có key nhưng ENABLE_LLM=false -> degrade llm_unavailable; regex vẫn bắt order_id.
    monkeypatch.setattr(intent_mod.settings, "llm_api_key", "sk-test")
    monkeypatch.setattr(intent_mod.settings, "enable_llm", False)

    async def fake_search(query: str, top_k: int = 4) -> list[dict]:
        return [{"text": "chính sách", "source": "doc.pdf", "chunk_index": 0, "score": 0.5}]

    monkeypatch.setattr(intent_mod.rag_service, "search", fake_search)
    r = await intent_mod.classify_intent("đơn 6578 sắp tới chưa shop")
    assert r["intent"] == "unknown"
    assert "llm_unavailable" in r["uncertainty_flags"]
    assert r["entities"].get("order_id") == "6578"
    assert r["rag_contexts"] == [{"source": "doc.pdf", "score": 0.5}]


async def test_classify_degrades_on_search_error_keeps_order_id(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(intent_mod.settings, "llm_api_key", "sk-test")

    async def boom(*args: object, **kwargs: object) -> list[dict]:
        raise RuntimeError("qdrant down")

    monkeypatch.setattr(intent_mod.rag_service, "search", boom)
    r = await intent_mod.classify_intent("mã đơn 6578")
    assert r["intent"] == "unknown"
    assert "search_error" in r["uncertainty_flags"]
    assert r["entities"].get("order_id") == "6578"
