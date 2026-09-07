"""Route agent — công cụ DEV chạy Agent 1 + Agent 2 single-shot (KHÔNG persist):

- /analyze : Agent 1 (intent/entities) + Agent 2 (retrieval) — cho thấy TÁCH VAI đúng PRD §7.1/§7.2.

`/classify` và `/pipeline` đã GỠ (slice obs P4) — chúng chỉ phục vụ hai panel dev trên màn Quản lý tri
thức, mà việc quan sát pipeline nay là của **tab Báo cáo** — đọc lượt THẬT của khách từ `audit_log`
thay vì chạy lại một câu test không lưu vết. `/run-demo` GỠ cùng lý do (client duy nhất là panel dev đã bỏ).

Cổng chat khách THẬT (persist + bộ nhớ đa lượt) = WebSocket /ws/chat. Response Generator vẫn là điểm phát ngôn
DUY NHẤT tới khách (PRD §7.4) — route này chỉ trả METADATA.
"""

from __future__ import annotations

from fastapi import APIRouter

from ...agents.nodes.intent import classify_intent
from ...agents.nodes.knowledge import retrieve_knowledge
from ...schemas.agent import AnalyzeResult, ClassifyRequest

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("/analyze", response_model=AnalyzeResult)
async def analyze(req: ClassifyRequest) -> AnalyzeResult:
    """Chạy Agent 1 (intent/entities) + Agent 2 (retrieval) — cho thấy TÁCH VAI đúng PRD §7.1/§7.2.
    Chỉ trả METADATA (Response Generator vẫn là điểm phát ngôn DUY NHẤT tới khách, §7.4)."""
    intent = await classify_intent(req.message)  # Agent 1
    know = await retrieve_knowledge(req.message, intent=intent["intent"])  # Agent 2 (lọc theo intent)
    return AnalyzeResult(
        intent=intent["intent"],
        category=intent["category"],
        entities=intent["entities"],
        intent_confidence=intent["confidence"],
        retrieval_confidence=know["retrieval_confidence"],
        uncertainty_flags=intent["uncertainty_flags"] + know["uncertainty_flags"],
        rag_contexts=know["rag_contexts"],
    )
