"""Xử lý bất đồng bộ — FastAPI BackgroundTasks (PRD §10, CLAUDE.md).

Đường nhanh mỗi tin nhắn: route trả về ngay, việc xử lý chạy nền (KHÔNG worker polling Redis — giữ
free-tier Upstash). Scaffold: chạy stub pipeline (KHÔNG LLM) + ghi audit_log mỗi bước (PRD §14 FR-PIPE-4).

KHÔNG gửi phản hồi cho khách ở đây — Response Generator là điểm phát ngôn DUY NHẤT (PRD §7.4), wiring sau.
"""

from __future__ import annotations

import uuid

from ..agents.graph import run_pipeline
from ..core.database import AsyncSessionLocal
from ..core.logging import get_logger
from ..models.message import Message
from ..services.audit_service import write_audit

log = get_logger("tasks.background")


async def process_message(conversation_id: uuid.UUID, message_id: uuid.UUID) -> None:
    log.info("process_message start conv=%s msg=%s", conversation_id, message_id)
    try:
        async with AsyncSessionLocal() as session:
            msg = await session.get(Message, message_id)
            input_text = msg.content if msg else ""

            # Stub pipeline (KHÔNG LLM). thread_id = conversation_id (mỗi hội thoại 1 state — PRD §14 FR-PIPE-1).
            final = await run_pipeline(input_text=input_text, conversation_id=str(conversation_id))
            result = final.get("result") or {}

            # Audit mỗi bước agent (PRD §14 FR-PIPE-4: mọi bước agent ghi audit_log)
            for step in final.get("trace", []):
                is_decision = step.get("node") == "decision"
                await write_audit(
                    session,
                    conversation_id=conversation_id,
                    message_id=message_id,
                    node=step.get("node"),
                    action=str(final.get("action")) if is_decision and final.get("action") else None,
                    confidence=step.get("confidence"),
                    detail=step.get("detail") or {},
                )

            # Audit tổng kết pipeline (nhánh + trạng thái cuối)
            await write_audit(
                session,
                conversation_id=conversation_id,
                message_id=message_id,
                node="pipeline",
                action=str(final.get("action")) if final.get("action") else None,
                confidence=final.get("confidence"),
                uncertainty_flags=final.get("uncertainty_flags") or [],
                escalation_reason=final.get("escalation_reason"),
                detail={"branch": result.get("branch"), "status": str(final.get("status"))},
            )
            await session.commit()
        log.info("process_message done conv=%s branch=%s", conversation_id, result.get("branch"))
    except Exception:  # noqa: BLE001 — task nền: log lỗi, KHÔNG để task chết âm thầm
        log.exception("process_message FAILED conv=%s msg=%s", conversation_id, message_id)

    # TODO (PRD §10):
    #   - FR-ASYNC-7: phát realtime tới client/Admin qua Redis pub/sub (event-driven), KHÔNG polling.
    #   - FR-ASYNC-3: human_handoff -> tạm dừng AI (LangGraph interrupt + checkpointer Redis/Postgres).
    #   - PRD §7.4/§9: phản hồi tới khách CHỈ qua Response Generator + theo gate (gửi thẳng | PENDING_APPROVAL).
