"""Phase 4 verify — graph compile + chạy CẢ 2 NHÁNH (response / human_handoff).

Không cần DB/network (nodes là stub). asyncio_mode=auto (pyproject) -> async test chạy tự động.
"""

from __future__ import annotations

from app.agents.graph import build_graph, run_pipeline


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
