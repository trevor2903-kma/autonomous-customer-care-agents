"""Agent 2 / `rag_service.search` — lọc theo intent + fallback gộp (P4). Offline, KHÔNG network."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest

from app.services import rag_service


@dataclass
class _Point:
    id: str
    score: float
    payload: dict[str, Any] = field(default_factory=dict)


def _pt(pid: str, score: float, intent: str = "shipping") -> _Point:
    return _Point(pid, score, {"text": f"t{pid}", "source": f"{pid}.md", "chunk_index": 0,
                               "type": "faq", "title": pid, "intent": intent, "question": None})


@pytest.fixture(autouse=True)
def _no_embedding(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_embed(text: str) -> list[float]:
        return [0.1, 0.2]

    monkeypatch.setattr(rag_service, "embed_text", fake_embed)
    monkeypatch.setattr(rag_service.settings, "retrieval_threshold", 0.35)


def _stub_query(monkeypatch: pytest.MonkeyPatch, narrow: list[_Point], broad: list[_Point]) -> list[str | None]:
    """Ghi lại thứ tự các lượt truy vấn (intent của mỗi lượt) để khẳng định có/không fallback."""
    calls: list[str | None] = []

    async def fake_query(vector: list[float], top_k: int, intent: str | None) -> list[_Point]:
        calls.append(intent)
        return list(narrow if intent else broad)

    monkeypatch.setattr(rag_service, "_query", fake_query)
    return calls


async def test_filtered_hits_enough_and_strong_skips_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    narrow = [_pt("a", 0.9), _pt("b", 0.8), _pt("c", 0.7), _pt("d", 0.6)]
    calls = _stub_query(monkeypatch, narrow, [_pt("z", 0.99)])

    hits = await rag_service.search("phí ship", top_k=4, intent="shipping")
    assert calls == ["shipping"]  # đủ top_k + điểm mạnh -> KHÔNG chạy lượt không lọc
    assert [h["source"] for h in hits] == ["a.md", "b.md", "c.md", "d.md"]
    assert hits[0]["type"] == "faq" and hits[0]["title"] == "a"


async def test_empty_filter_falls_back_to_unfiltered(monkeypatch: pytest.MonkeyPatch) -> None:
    # Nhãn intent thiếu/sai trong KB không được làm mất tri thức đúng.
    calls = _stub_query(monkeypatch, [], [_pt("z", 0.88)])
    hits = await rag_service.search("phí ship", top_k=4, intent="shipping")
    assert calls == ["shipping", None]
    assert [h["source"] for h in hits] == ["z.md"]


async def test_weak_filtered_top_hit_triggers_merge_and_sort(monkeypatch: pytest.MonkeyPatch) -> None:
    narrow = [_pt("a", 0.20), _pt("b", 0.10), _pt("c", 0.05), _pt("d", 0.02)]
    broad = [_pt("a", 0.20), _pt("x", 0.95), _pt("y", 0.50)]  # 'a' trùng -> khử một lần
    calls = _stub_query(monkeypatch, narrow, broad)

    hits = await rag_service.search("phí ship", top_k=4, intent="shipping")
    assert calls == ["shipping", None]  # top-1 lọc dưới ngưỡng -> mở rộng
    assert [h["source"] for h in hits] == ["x.md", "y.md", "a.md", "b.md"]  # gộp, khử trùng, xếp theo điểm
    assert len({h["source"] for h in hits}) == 4


async def test_intent_other_never_filters(monkeypatch: pytest.MonkeyPatch) -> None:
    # `other` = ngoài phạm vi, không có chunk nào mang nhãn đó -> lọc là chắc chắn rỗng, bỏ luôn lượt lọc.
    calls = _stub_query(monkeypatch, [], [_pt("z", 0.7)])
    await rag_service.search("vé xem phim", top_k=4, intent="other")
    assert calls == [None]


async def test_no_intent_behaves_like_before(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _stub_query(monkeypatch, [], [_pt("z", 0.7)])
    hits = await rag_service.search("phí ship", top_k=4)
    assert calls == [None]
    assert hits[0]["source"] == "z.md"
