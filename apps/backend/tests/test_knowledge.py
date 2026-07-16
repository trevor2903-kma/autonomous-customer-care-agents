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
