"""Luồng đơn hàng XUYÊN NODE (Agent 1 → 2 → 3 → 4) trên graph thật (`run_pipeline`) — offline.

Stub đúng ba biên I/O: LLM (`get_openai` / `classify_intent`), Qdrant (`rag_service.search`) và DB đơn
(`order_service.lookup`, scoped như truy vấn thật). Kiểm WIRING giữa các node, không chỉ từng hàm.
"""

from __future__ import annotations

from typing import Any

import pytest

from app.agents import graph as graph_mod
from app.agents.nodes import intent as intent_mod
from app.agents.nodes import knowledge as kn
from app.agents.nodes import response as resp

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
