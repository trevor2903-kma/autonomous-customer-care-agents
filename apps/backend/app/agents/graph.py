"""LangGraph pipeline cố định (PRD §5–§8): intent → knowledge → decision → [route] → response | human_handoff.

KHÔNG Supervisor (PRD §5 trụ cột 1). Thứ tự & nhánh rẽ do graph quy định trước, không do agent quyết runtime.
Scaffold: node là stub; checkpointer là MemorySaver in-memory.
"""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from ..models.enums import ConversationStatus
from .nodes.decision import decision_node
from .nodes.intent import intent_node
from .nodes.knowledge import knowledge_node
from .nodes.response import response_node
from .state import ConversationState

# Node `human_handoff` (EscalationCard + admin queue + suspend/resume) và `policy.should_handoff` = slice 08b —
# GIỮ file, CHƯA cắm vào graph. Slice này SOLE-EGRESS: Response Generator phát cả câu trả lời lẫn thông báo handoff.


def build_graph():
    g = StateGraph(ConversationState)
    # LangGraph cấm node-id trùng state-key. State có field CSKH `intent` (PRD §7.1) nên node intent
    # đăng ký id "intent_classifier" (đúng tên agent PRD §7.1). Tên hiển thị trong trace vẫn là "intent".
    g.add_node("intent_classifier", intent_node)
    g.add_node("knowledge", knowledge_node)
    g.add_node("decision", decision_node)
    g.add_node("response", response_node)

    g.add_edge(START, "intent_classifier")
    g.add_edge("intent_classifier", "knowledge")
    g.add_edge("knowledge", "decision")
    # SOLE-EGRESS: Response Generator (điểm phát ngôn DUY NHẤT) branch theo state["action"] — phát câu trả lời
    # grounded (auto_reply) HOẶC thông báo chuyển người (human_handoff). Node human_handoff (side-effect:
    # EscalationCard + admin queue) = slice 08b: khi đó thêm conditional should_handoff -> human_handoff.
    g.add_edge("decision", "response")
    g.add_edge("response", END)

    # Checkpointer in-memory (scaffold).
    # TODO (PRD §10 FR-ASYNC-3/§10 FR-ASYNC-6): checkpointer Redis/Postgres + interrupt cho suspend/resume
    #   human_handoff; wiring WebSocket↔graph + Redis pub/sub phát realtime.
    return g.compile(checkpointer=MemorySaver())


# Compiled graph dùng chung (stateless-per-thread qua thread_id).
graph = build_graph()


def _initial_state(
    *, input_text: str, conversation_id: str, force_handoff: bool, history: list[dict[str, Any]] | None
) -> ConversationState:
    return {
        "conversation_id": conversation_id,
        "input": input_text,
        "history": history or [],  # đầu vào chỉ-đọc (lịch sử đa lượt từ DB)
        # Demo: tiêm cờ CHẶN (∈ BLOCKING_FLAGS) để ép nhánh human_handoff (Decision đọc scratchpad).
        "scratchpad": {"injected_flags": ["out_of_domain"]} if force_handoff else {},
        "messages": [],
        "trace": [],
        "status": ConversationStatus.NEW,
        "result": None,
        "error": None,
        "confidence": 1.0,
        "uncertainty_flags": [],
        "escalation_reason": None,
        "require_human_handoff": False,
        "intent": None,
        "entities": {},
        "rag_contexts": [],
        "action": None,
        "draft_reply": None,
        "awaiting_customer": False,
    }


async def run_pipeline(
    *,
    input_text: str,
    force_handoff: bool = False,
    conversation_id: str | None = None,
    history: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Chạy pipeline 1 lượt, trả final state. force_handoff=True -> demo nhánh human_handoff.

    `thread_id` sinh MỚI mỗi lượt (MemorySaver in-memory tích luỹ reduce-channel nếu tái dùng) → bộ nhớ đa lượt
    KHÔNG từ checkpointer mà từ `history` (nạp từ DB, đầu vào chỉ-đọc). Durable checkpointer = slice 09b.
    """
    thread_id = str(uuid4())
    state_in = _initial_state(
        input_text=input_text,
        conversation_id=conversation_id or thread_id,
        force_handoff=force_handoff,
        history=history,
    )
    return await graph.ainvoke(state_in, config={"configurable": {"thread_id": thread_id}})
