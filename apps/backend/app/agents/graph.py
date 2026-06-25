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
from .nodes.human_handoff import human_handoff_node
from .nodes.intent import intent_node
from .nodes.knowledge import knowledge_node
from .nodes.response import response_node
from .policy import should_handoff
from .state import ConversationState


def build_graph():
    g = StateGraph(ConversationState)
    # LangGraph cấm node-id trùng state-key. State có field CSKH `intent` (PRD §7.1) nên node intent
    # đăng ký id "intent_classifier" (đúng tên agent PRD §7.1). Tên hiển thị trong trace vẫn là "intent".
    g.add_node("intent_classifier", intent_node)
    g.add_node("knowledge", knowledge_node)
    g.add_node("decision", decision_node)
    g.add_node("response", response_node)
    g.add_node("human_handoff", human_handoff_node)

    g.add_edge(START, "intent_classifier")
    g.add_edge("intent_classifier", "knowledge")
    g.add_edge("knowledge", "decision")
    # Conditional sau Decision Engine: nhánh tự động (response) vs chuyển người (human_handoff).
    g.add_conditional_edges(
        "decision",
        should_handoff,
        {"response": "response", "human_handoff": "human_handoff"},
    )
    g.add_edge("response", END)
    g.add_edge("human_handoff", END)

    # Checkpointer in-memory (scaffold).
    # TODO (PRD §10 FR-ASYNC-3/§10 FR-ASYNC-6): checkpointer Redis/Postgres + interrupt cho suspend/resume
    #   human_handoff; wiring WebSocket↔graph + Redis pub/sub phát realtime.
    return g.compile(checkpointer=MemorySaver())


# Compiled graph dùng chung (stateless-per-thread qua thread_id).
graph = build_graph()


def _initial_state(*, input_text: str, conversation_id: str, force_handoff: bool) -> ConversationState:
    return {
        "conversation_id": conversation_id,
        "input": input_text,
        # Scaffold demo: tiêm cờ bất định để ép nhánh human_handoff (Decision đọc scratchpad).
        "scratchpad": {"injected_flags": ["ambiguous_intent"]} if force_handoff else {},
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
) -> dict[str, Any]:
    """Chạy pipeline 1 lượt, trả final state. force_handoff=True -> demo nhánh human_handoff."""
    thread_id = conversation_id or str(uuid4())
    state_in = _initial_state(
        input_text=input_text, conversation_id=thread_id, force_handoff=force_handoff
    )
    return await graph.ainvoke(state_in, config={"configurable": {"thread_id": thread_id}})
