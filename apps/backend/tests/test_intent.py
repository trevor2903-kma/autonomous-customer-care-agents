"""Intent Classifier — degrade AN TOÀN khi offline (plan §5). Các test này KHÔNG chạm network."""

from __future__ import annotations

import pytest

from app.agents.nodes import intent as intent_mod


async def test_classify_degrades_without_key(monkeypatch: pytest.MonkeyPatch) -> None:
    # Thiếu LLM_API_KEY -> degrade NGAY, không embed/search (không network).
    monkeypatch.setattr(intent_mod.settings, "llm_api_key", "")
    result = await intent_mod.classify_intent("áo này còn size M không shop?")
    assert result["intent"] == "unknown"
    assert result["confidence"] == 0.0
    assert "no_relevant_knowledge" in result["uncertainty_flags"]
    assert result["rag_contexts"] == []


async def test_classify_degrades_on_search_error(monkeypatch: pytest.MonkeyPatch) -> None:
    # Có key nhưng Qdrant/search lỗi -> degrade an toàn, KHÔNG ném lỗi ra ngoài.
    monkeypatch.setattr(intent_mod.settings, "llm_api_key", "sk-test")

    async def boom(*args: object, **kwargs: object) -> list[dict]:
        raise RuntimeError("qdrant down")

    monkeypatch.setattr(intent_mod.rag_service, "search", boom)
    result = await intent_mod.classify_intent("test")
    assert result["intent"] == "unknown"
    assert "no_relevant_knowledge" in result["uncertainty_flags"]


async def test_classify_similarity_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    # ENABLE_LLM=false -> similarity top-1 (không gọi LLM). Patch search -> hits tất định (không network).
    monkeypatch.setattr(intent_mod.settings, "llm_api_key", "sk-test")
    monkeypatch.setattr(intent_mod.settings, "enable_llm", False)

    async def fake_search(query: str, top_k: int = 3) -> list[dict]:
        return [
            {"intent": "shipping", "category": "general", "text": "phí ship...", "score": 0.82},
            {"intent": "order_status", "category": "after_sale", "text": "đơn tới đâu...", "score": 0.40},
        ]

    monkeypatch.setattr(intent_mod.rag_service, "search", fake_search)
    result = await intent_mod.classify_intent("ship về Đà Nẵng bao nhiêu shop?")
    assert result["intent"] == "shipping"
    assert result["confidence"] == 0.82
    assert result["entities"] == {}
    assert result["rag_contexts"][0]["intent"] == "shipping"
