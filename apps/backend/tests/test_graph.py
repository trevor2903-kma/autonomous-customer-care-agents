"""Graph compile + chạy CẢ 2 NHÁNH (response / human_handoff).

Kiểm ĐỊNH TUYẾN graph, KHÔNG kiểm chất lượng phân loại RAG (xem test_intent.py). Agent 1 (intent) giờ có
logic THẬT gọi network → patch `classify_intent` bằng stub tất định để test chạy OFFLINE.
asyncio_mode=auto (pyproject) -> async test chạy tự động.
"""

from __future__ import annotations

import pytest

from app.agents.graph import build_graph, run_pipeline


@pytest.fixture(autouse=True)
def _offline_agents(monkeypatch: pytest.MonkeyPatch) -> None:
    """Giữ pipeline test offline: Agent 1 (classify_intent) + Agent 2 (retrieve_knowledge) + Agent 4
    (generate_reply) đều gọi network -> thay bằng stub tất định."""

    async def fake_classify(text: str) -> dict:
        return {
            "intent": "product_information",
            "category": "pre_sale",
            "entities": {},
            "confidence": 0.9,
            "uncertainty_flags": [],
        }

    async def fake_retrieve(query: str, top_k: int = 4) -> dict:
        return {
            "rag_contexts": [{"text": "chính sách", "source": "kb.pdf", "score": 0.8}],
            "retrieval_confidence": 0.8,
            "uncertainty_flags": [],
        }

    async def fake_generate(query, intent, entities, rag_contexts) -> dict:  # type: ignore[no-untyped-def]
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
    assert "escalation_card" in final["result"]
    # Pipeline cố định: intent -> knowledge -> decision -> human_handoff
    assert [t["node"] for t in final["trace"]] == ["intent", "knowledge", "decision", "human_handoff"]


async def test_pass_through_ignores_real_flags_accumulate_once(monkeypatch: pytest.MonkeyPatch) -> None:
    """Phase 1 pass-through (TẠM bỏ Agent 3): cờ THẬT của Agent 1/2 KHÔNG còn ép handoff — traffic thật
    (không tiêm) → auto_reply. Cờ vẫn tích luỹ đúng 1 lần (reducer `add`, không nhân đôi)."""

    async def fake_classify(text: str) -> dict:
        return {
            "intent": "other",
            "category": "general",
            "entities": {},
            "confidence": 0.5,
            "uncertainty_flags": ["multi_intent"],
        }

    monkeypatch.setattr("app.agents.nodes.intent.classify_intent", fake_classify)
    final = await run_pipeline(input_text="demo", force_handoff=False)

    # Pass-through: cờ thật multi_intent KHÔNG còn ép handoff (Agent 3 tạm bỏ) -> đi nhánh response.
    assert final["require_human_handoff"] is False
    assert final["action"] == "auto_reply"
    assert final["result"]["branch"] == "response"
    # Reducer `add`: multi_intent tích luỹ đúng 1 lần (decision không trả lại cờ đã tích luỹ).
    assert final["uncertainty_flags"].count("multi_intent") == 1
