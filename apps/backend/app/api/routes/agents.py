"""Routes agent — công cụ DEV/INSPECTOR chạy pipeline single-shot (KHÔNG persist):

- /classify: RIÊNG Agent 1 (intent/entities).   - /pipeline: ĐỦ 4 agent cho FE inspector (/rag).
- /analyze : Agent 1 + Agent 2 (tách vai RAG).  - /run-demo: minh hoạ pipeline cố định + 2 nhánh.

Cổng chat khách THẬT (persist + bộ nhớ đa lượt) = WebSocket /ws/chat. Response Generator vẫn là điểm phát ngôn
DUY NHẤT tới khách (PRD §7.4) — các route này chỉ trả METADATA / 1 câu test.
"""

from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, Query

from ...agents.graph import run_pipeline
from ...agents.nodes.intent import classify_intent
from ...agents.nodes.knowledge import retrieve_knowledge
from ...models.enums import INTENT_CATEGORY, Intent
from ...schemas.agent import (
    AgentTraceStep,
    AnalyzeResult,
    ClassifyRequest,
    ClassifyResult,
    PipelineResult,
    RunDemoResult,
)


def _category_of(intent: str | None) -> str | None:
    """Suy category từ intent (INTENT_CATEGORY) — state không lưu category. intent ngoài enum -> None."""
    if not intent:
        return None
    try:
        cat = INTENT_CATEGORY.get(Intent(intent))
    except ValueError:
        return None
    return cat.value if cat else None

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("/classify", response_model=ClassifyResult)
async def classify(req: ClassifyRequest) -> ClassifyResult:
    """Chạy RIÊNG Agent 1 (Intent Classifier) — output sạch, KHÔNG retrieval (KHÔNG chạy cả graph)."""
    return ClassifyResult(**await classify_intent(req.message))


@router.post("/analyze", response_model=AnalyzeResult)
async def analyze(req: ClassifyRequest) -> AnalyzeResult:
    """Chạy Agent 1 (intent/entities) + Agent 2 (retrieval) — cho thấy TÁCH VAI đúng PRD §7.1/§7.2.
    Chỉ trả METADATA (Response Generator vẫn là điểm phát ngôn DUY NHẤT tới khách, §7.4)."""
    intent = await classify_intent(req.message)  # Agent 1
    know = await retrieve_knowledge(req.message)  # Agent 2
    return AnalyzeResult(
        intent=intent["intent"],
        category=intent["category"],
        entities=intent["entities"],
        intent_confidence=intent["confidence"],
        retrieval_confidence=know["retrieval_confidence"],
        uncertainty_flags=intent["uncertainty_flags"] + know["uncertainty_flags"],
        rag_contexts=know["rag_contexts"],
    )


@router.post("/pipeline", response_model=PipelineResult)
async def pipeline(req: ClassifyRequest) -> PipelineResult:
    """Chạy ĐỦ pipeline cho 1 câu test (FE inspector, single-shot) — KHÔNG persist (công cụ dev). Trả slice
    của cả 4 agent: Agent 1 (intent/entities) · Agent 2 (retrieval) · Agent 3 (quyết định) · Agent 4 (reply)."""
    final = await run_pipeline(input_text=req.message)
    result = final.get("result") or {}
    intent = final.get("intent") or "unknown"
    return PipelineResult(
        intent=intent,
        category=_category_of(final.get("intent")),
        entities=final.get("entities") or {},
        intent_confidence=float(final.get("intent_confidence") or 0.0),
        retrieval_confidence=float(final.get("retrieval_confidence") or 0.0),
        rag_contexts=final.get("rag_contexts") or [],
        action=final.get("action"),
        priority=final.get("priority"),
        severity=final.get("severity"),
        escalation_reason=final.get("escalation_reason"),
        uncertainty_flags=final.get("uncertainty_flags") or [],
        reply=result.get("reply"),
    )


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
