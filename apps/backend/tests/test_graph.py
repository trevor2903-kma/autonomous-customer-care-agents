"""Graph compile + chạy CẢ 2 NHÁNH (response / human_handoff).

Kiểm ĐỊNH TUYẾN graph, KHÔNG kiểm chất lượng phân loại RAG (xem test_intent.py). Agent 1 (intent) giờ có
logic THẬT gọi network → patch `classify_intent` bằng stub tất định để test chạy OFFLINE.
asyncio_mode=auto (pyproject) -> async test chạy tự động.
"""

from __future__ import annotations

import pytest

from app.agents.graph import build_graph, run_pipeline
from app.agents.nodes.response import HANDOFF_NOTICE


@pytest.fixture(autouse=True)
def _offline_agents(monkeypatch: pytest.MonkeyPatch) -> None:
    """Giữ pipeline test offline: Agent 1 (classify_intent) + Agent 2 (retrieve_knowledge) + Agent 4
    (generate_reply) đều gọi network -> thay bằng stub tất định."""

    async def fake_classify(text: str, history=None) -> dict:  # type: ignore[no-untyped-def]
        return {
            "intent": "product_information",
            "category": "pre_sale",
            "entities": {},
            "confidence": 0.9,
            "uncertainty_flags": [],
        }

    async def fake_retrieve(query: str, top_k: int = 4, intent: str | None = None) -> dict:
        return {
            "rag_contexts": [
                {"text": "chính sách", "source": "kb.pdf", "type": "reference", "title": "KB", "score": 0.8}
            ],
            "retrieval_confidence": 0.8,
            "uncertainty_flags": [],
        }

    async def fake_generate(query, intent, entities, rag_contexts, history=None) -> dict:  # type: ignore[no-untyped-def]
        return {"reply": "[stub] phản hồi grounded", "uncertainty_flags": []}

    monkeypatch.setattr("app.agents.nodes.intent.classify_intent", fake_classify)
    monkeypatch.setattr("app.agents.nodes.knowledge.retrieve_knowledge", fake_retrieve)
    monkeypatch.setattr("app.agents.nodes.response.generate_reply", fake_generate)


def test_graph_compiles() -> None:
    graph = build_graph()
    assert graph is not None


async def test_auto_reply_branch() -> None:
    final = await run_pipeline(input_text="demo", force_handoff=False)

    assert final["result"]["branch"] == "response"
    assert final["action"] == "auto_reply"
    assert final["require_human_handoff"] is False
    assert final["status"] == "REPLIED"
    assert final["confidence"] == 1.0
    # Pipeline cố định: intent -> knowledge -> decision -> response
    assert [t["node"] for t in final["trace"]] == ["intent", "knowledge", "decision", "response"]
    # Response Generator là node duy nhất ghi tin nhắn AI
    assert any(m["sender"] == "ai" for m in final["messages"])


async def test_human_handoff_branch() -> None:
    final = await run_pipeline(input_text="demo", force_handoff=True)

    assert final["result"]["branch"] == "human_handoff"
    assert final["action"] == "human_handoff"
    assert final["require_human_handoff"] is True
    assert final["status"] == "IN_HUMAN_QUEUE"
    assert final["escalation_reason"]  # có lý do chuyển tiếp
    # SOLE-EGRESS: Response Generator phát thông báo handoff (KHÔNG qua human_handoff node — để dành 08b).
    assert final["result"]["reply"] == HANDOFF_NOTICE
    assert [t["node"] for t in final["trace"]] == ["intent", "knowledge", "decision", "response"]
    assert any(m["sender"] == "ai" for m in final["messages"])


async def test_golden_complaint_auto_reply_high_priority(monkeypatch: pytest.MonkeyPatch) -> None:
    """Golden e2e (mocked agents): complaint sạch cờ + có tri thức → auto_reply grounded, priority=high/high.
    Xác nhận Agent 3 THẬT (không còn pass_through trong trace)."""

    async def fake_classify(text: str, history=None) -> dict:  # type: ignore[no-untyped-def]
        return {
            "intent": "complaint",
            "category": "after_sale",
            "entities": {},
            "confidence": 0.9,
            "uncertainty_flags": [],
        }

    monkeypatch.setattr("app.agents.nodes.intent.classify_intent", fake_classify)
    final = await run_pipeline(input_text="áo mình bị lỗi rách chỉ, shop xử lý sao?")

    assert final["action"] == "auto_reply"
    assert final["priority"] == "high"
    assert final["severity"] == "high"
    assert final["status"] == "REPLIED"
    assert final["result"]["reply"]
    # Agent 3 THẬT: decision trace có blocking_flags, KHÔNG còn pass_through (pass-through đã bỏ hẳn).
    dec = next(t for t in final["trace"] if t["node"] == "decision")
    assert "blocking_flags" in dec["detail"]
    assert "pass_through" not in dec["detail"]


async def test_blocking_flag_forces_handoff_once(monkeypatch: pytest.MonkeyPatch) -> None:
    """Agent 3 TẤT ĐỊNH: cờ THẬT ∈ BLOCKING_FLAGS (Agent 1/2) → human_handoff (route trên CỜ, không blend
    confidence). Cờ vẫn tích luỹ đúng 1 lần (reducer `add`, decision không trả lại cờ đã tích luỹ)."""

    async def fake_classify(text: str, history=None) -> dict:  # type: ignore[no-untyped-def]
        return {
            "intent": "other",
            "category": "general",
            "entities": {},
            "confidence": 0.5,
            "uncertainty_flags": ["multi_intent"],  # ∈ BLOCKING_FLAGS
        }

    monkeypatch.setattr("app.agents.nodes.intent.classify_intent", fake_classify)
    final = await run_pipeline(input_text="demo", force_handoff=False)

    # Deterministic: multi_intent ∈ BLOCKING_FLAGS -> handoff.
    assert final["require_human_handoff"] is True
    assert final["action"] == "human_handoff"
    assert "multi_intent" in final["escalation_reason"]
    # Reducer `add`: multi_intent xuất hiện đúng 1 lần (decision không trả lại cờ đã tích luỹ).
    assert final["uncertainty_flags"].count("multi_intent") == 1
