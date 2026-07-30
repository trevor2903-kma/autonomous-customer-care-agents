"""LangGraph pipeline cố định (PRD §5–§8): intent → knowledge → decision → [route] → response | human_handoff.

KHÔNG Supervisor (PRD §5 trụ cột 1). Thứ tự & nhánh rẽ do graph quy định trước, không do agent quyết runtime.
Nodes THẬT (intent/knowledge/decision/response); checkpointer MemorySaver in-memory (durable = slice 09b).
"""

from __future__ import annotations

import inspect
import time
from collections.abc import Callable
from functools import wraps
from typing import Any
from uuid import uuid4

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from ..core import tracing
from ..models.enums import ConversationStatus
from .nodes.decision import decision_node
from .nodes.intent import intent_node
from .nodes.knowledge import knowledge_node
from .nodes.response import response_node
from .state import ConversationState

# Node `human_handoff` (EscalationCard + admin queue + suspend/resume) và `policy.should_handoff` = slice 08b —
# GIỮ file, CHƯA cắm vào graph. Slice này SOLE-EGRESS: Response Generator phát cả câu trả lời lẫn thông báo handoff.

def _stamp(out: dict[str, Any], started: float) -> dict[str, Any]:
    """Gắn `duration_ms` + `flags` (cờ MỚI của node) vào trace step mà node vừa trả về."""
    elapsed_ms = int((time.perf_counter() - started) * 1000)
    node_flags = list(out.get("uncertainty_flags") or [])
    for step in out.get("trace") or []:
        step.setdefault("duration_ms", elapsed_ms)
        step.setdefault("flags", node_flags)
    return out


def _observed(fn: Callable[..., Any]) -> Callable[..., Any]:
    """Bọc node để QUAN SÁT: đo thời gian chạy + quy cờ về đúng node đã phát ra nó.

    Đo ở LỚP BỌC chứ không sửa từng node — slice observability chỉ quan sát, không đụng logic agent
    (bất biến §1); node thêm về sau tự động có số đo. Wrapper KHÔNG đọc/đổi state và KHÔNG nuốt lỗi
    (node lỗi vẫn ném lên như cũ để `_run_pipeline_safe` xử lý).

    `flags` = `out["uncertainty_flags"]` = cờ node VỪA phát (reducer `add` chỉ nhận cờ mới), nên quy
    được cờ về đúng agent sinh ra nó thay vì chỉ có tập cờ gộp cuối lượt.

    GIỮ NGUYÊN tính sync/async của node gốc: `decision_node` là hàm SYNC (Agent 3 tất định, không I/O)
    — bọc thành async sẽ đổi cách LangGraph chạy nó. Wrapper async chỉ dành cho node async.
    """
    if inspect.iscoroutinefunction(fn):

        @wraps(fn)
        async def async_wrapper(state: ConversationState) -> dict[str, Any]:
            started = time.perf_counter()
            return _stamp(await fn(state), started)

        return async_wrapper

    @wraps(fn)
    def sync_wrapper(state: ConversationState) -> dict[str, Any]:
        started = time.perf_counter()
        return _stamp(fn(state), started)

    return sync_wrapper


def build_graph():
    g = StateGraph(ConversationState)
    # LangGraph cấm node-id trùng state-key. State có field CSKH `intent` (PRD §7.1) nên node intent
    # đăng ký id "intent_classifier" (đúng tên agent PRD §7.1). Tên hiển thị trong trace vẫn là "intent".
    g.add_node("intent_classifier", _observed(intent_node))
    g.add_node("knowledge", _observed(knowledge_node))
    g.add_node("decision", _observed(decision_node))
    g.add_node("response", _observed(response_node))

    g.add_edge(START, "intent_classifier")
    g.add_edge("intent_classifier", "knowledge")
    g.add_edge("knowledge", "decision")
    # SOLE-EGRESS: Response Generator (điểm phát ngôn DUY NHẤT) branch theo state["action"] — phát câu trả lời
    # grounded (auto_reply) HOẶC thông báo chuyển người (human_handoff). Node human_handoff (side-effect:
    # EscalationCard + admin queue) = slice 08b: khi đó thêm conditional should_handoff -> human_handoff.
    g.add_edge("decision", "response")
    g.add_edge("response", END)

    # Checkpointer in-memory (MemorySaver).
    # TODO (PRD §10 FR-ASYNC-3/§10 FR-ASYNC-6): checkpointer Redis/Postgres + interrupt cho suspend/resume
    #   human_handoff; wiring WebSocket↔graph + Redis pub/sub phát realtime.
    return g.compile(checkpointer=MemorySaver())


# Compiled graph dùng chung (stateless-per-thread qua thread_id).
graph = build_graph()


def _initial_state(
    *,
    input_text: str,
    conversation_id: str,
    turn_id: str,
    force_handoff: bool,
    history: list[dict[str, Any]] | None,
) -> ConversationState:
    return {
        "conversation_id": conversation_id,
        "turn_id": turn_id,
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
    turn_id: str | None = None,
) -> dict[str, Any]:
    """Chạy pipeline 1 lượt, trả final state. force_handoff=True -> demo nhánh human_handoff.

    `thread_id` sinh MỚI mỗi lượt (MemorySaver in-memory tích luỹ reduce-channel nếu tái dùng) → bộ nhớ đa lượt
    KHÔNG từ checkpointer mà từ `history` (nạp từ DB, đầu vào chỉ-đọc). Durable checkpointer = slice 09b.

    `turn_id` (observability P1) do CALLER truyền vào để lượt vẫn ghi được audit khi pipeline NÉM LỖI —
    tự sinh ở đây thì lỗi là mất luôn khoá gom. Không truyền → sinh tại chỗ (route dev/demo).
    """
    thread_id = str(uuid4())
    state_in = _initial_state(
        input_text=input_text,
        conversation_id=conversation_id or thread_id,
        turn_id=turn_id or str(uuid4()),
        force_handoff=force_handoff,
        history=history,
    )
    # Span GỐC cho Langfuse (obs P3): các lời gọi LLM/embedding bên trong lượt nằm lồng vào đây, nên
    # xem được tổng độ trễ + chi phí của MỘT lượt. No-op nếu chưa cấu hình Langfuse.
    with tracing.observe_turn(input_text) as span:
        final = await graph.ainvoke(state_in, config={"configurable": {"thread_id": thread_id}})
        span.finish(
            output=(final.get("result") or {}).get("reply"),
            metadata={"intent": final.get("intent"), "action": final.get("action"),
                      "flags": final.get("uncertainty_flags") or []},
        )
        return final
