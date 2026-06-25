"""Routes agent — run-demo chạy pipeline LangGraph và trả trace (scaffold).

KHÔNG wiring vào hội thoại/WebSocket thật ở scaffold — chỉ minh hoạ pipeline cố định + 2 nhánh.
"""

from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, Query

from ...agents.graph import run_pipeline
from ...schemas.agent import AgentTraceStep, RunDemoResult

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("/run-demo", response_model=RunDemoResult)
async def run_demo(
    force: str | None = Query(
        default=None,
        description="ép nhánh: 'handoff' -> demo human_handoff; mặc định -> nhánh auto_reply (response)",
    ),
) -> RunDemoResult:
    thread_id = str(uuid4())
    final = await run_pipeline(
        input_text="demo: khách hỏi chính sách đổi trả",
        force_handoff=(force == "handoff"),
        conversation_id=thread_id,
    )
    result = final.get("result") or {}
    return RunDemoResult(
        thread_id=final.get("conversation_id") or thread_id,
        branch=result.get("branch", "unknown"),
        status=str(final.get("status", "")),
        action=final.get("action"),
        confidence=final.get("confidence"),
        require_human_handoff=bool(final.get("require_human_handoff")),
        escalation_reason=final.get("escalation_reason"),
        reply=result.get("reply") or result.get("notice"),
        trace=[AgentTraceStep(**step) for step in final.get("trace", [])],
    )
