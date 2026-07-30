"""Service audit — ghi nhật ký kiểm toán (PRD §20, NFR-4: 100% hành động agent/Admin truy vết được).

Hai lớp:
- `write_audit` (cũ): ghi 1 dòng vào session của CALLER (caller tự commit).
- `record_turn` (P1): ghi CẢ MỘT LƯỢT khách từ luồng WS thật — nguồn dữ liệu của tab Báo cáo.

`build_turn_rows` tách riêng làm HÀM THUẦN (không DB, không I/O) để test offline được: hình dạng dòng
audit là hợp đồng với tab Báo cáo (P2/P4), sai một khoá là hỏng cả báo cáo mà không ai biết.

**Degrade an toàn (bất biến §1):** `record_turn` KHÔNG BAO GIỜ ném lỗi. Ghi log là việc PHỤ — hỏng
audit không được phép làm rớt lượt trả lời khách. Caller không cần try/except.
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import AsyncSessionLocal
from ..core.logging import get_logger
from ..models.audit_log import AuditLog
from ..models.enums import AuditNode, TurnOutcome

log = get_logger("audit")

# Độ dài tối đa lưu lại của câu khách / câu trả lời. Audit là để TRUY VẾT, không phải bản sao hội thoại
# (nội dung đầy đủ đã nằm ở bảng `message`) — cắt để bảng audit không phình theo độ dài chat.
_TEXT_CAP = 400
_PREVIEW_CAP = 200

# node -> action mặc định cho các bước không tự mang "hành động" (decision/response lấy từ state).
_NODE_ACTION = {
    AuditNode.INTENT: "classify",
    AuditNode.KNOWLEDGE: "retrieve",
}


async def write_audit(
    session: AsyncSession,
    *,
    conversation_id: uuid.UUID | None = None,
    message_id: uuid.UUID | None = None,
    turn_id: uuid.UUID | None = None,
    node: str | None = None,
    action: str | None = None,
    confidence: float | None = None,
    duration_ms: int | None = None,
    uncertainty_flags: list[str] | None = None,
    escalation_reason: str | None = None,
    detail: dict[str, Any] | None = None,
) -> AuditLog:
    entry = AuditLog(
        conversation_id=conversation_id,
        message_id=message_id,
        turn_id=turn_id,
        node=node,
        action=action,
        confidence=confidence,
        duration_ms=duration_ms,
        uncertainty_flags=uncertainty_flags or [],
        escalation_reason=escalation_reason,
        detail=detail or {},
    )
    session.add(entry)
    await session.flush()
    return entry


# ── Nhật ký MỘT LƯỢT khách (P1) ───────────────────────────────────────────────
def _clip(text: str | None, cap: int) -> str:
    return (text or "")[:cap]


def rag_sources(final: dict[str, Any]) -> list[dict[str, Any]]:
    """Nguồn tri thức Agent 2 đã dùng — `.md` trong repo (KHÔNG phải PDF từ thời upload)."""
    return [
        {
            "source": c.get("source"),
            "type": c.get("type"),
            "title": c.get("title"),
            "score": c.get("score"),
        }
        for c in (final.get("rag_contexts") or [])
    ]


def _step_row(step: dict[str, Any], final: dict[str, Any], reply: str) -> dict[str, Any]:
    """Một dòng audit cho một bước pipeline, dựng từ trace step + làm giàu bằng final state."""
    node = str(step.get("node") or "")
    detail = dict(step.get("detail") or {})
    action = _NODE_ACTION.get(node)
    escalation_reason = None

    if node == AuditNode.KNOWLEDGE:
        # `rag_contexts` không nằm trong trace (trace chỉ đếm số lượng) → lấy từ final state.
        detail["rag_sources"] = rag_sources(final)
        detail["retrieval_confidence"] = final.get("retrieval_confidence")
    elif node == AuditNode.DECISION:
        # action ở đây = QUYẾT ĐỊNH của Agent 3 (auto_reply|human_handoff) — khác kết cục giao cuối lượt.
        action = str(final.get("action")) if final.get("action") else None
        escalation_reason = final.get("escalation_reason")
    elif node == AuditNode.RESPONSE:
        action = step.get("branch")  # response | human_handoff
        detail["reply_len"] = len(reply or "")
        detail["reply_preview"] = _clip(reply, _PREVIEW_CAP)

    return {
        "node": node,
        "action": action,
        "confidence": step.get("confidence"),
        "duration_ms": step.get("duration_ms"),
        # Cờ RIÊNG của node (lớp bọc `_observed` gắn) — quy được cờ về đúng agent đã phát ra nó.
        "uncertainty_flags": list(step.get("flags") or []),
        "escalation_reason": escalation_reason,
        "detail": detail,
    }


def build_turn_rows(
    *,
    turn_id: uuid.UUID,
    conversation_id: uuid.UUID | None,
    customer_text: str,
    final: dict[str, Any] | None,
    reply: str,
    outcome: str,
    total_ms: int,
) -> list[dict[str, Any]]:
    """Dựng các dòng audit của MỘT lượt: `customer` → các node pipeline → `delivery`. HÀM THUẦN.

    `final=None` (pipeline ném lỗi) → vẫn dựng 2 dòng bao quanh: lượt hỏng cũng phải truy vết được,
    và đó chính là lượt cần nhìn nhất.
    """
    common = {"turn_id": turn_id, "conversation_id": conversation_id}
    rows: list[dict[str, Any]] = [
        {
            **common,
            "node": str(AuditNode.CUSTOMER),
            "action": "message_received",
            "detail": {"customer_text": _clip(customer_text, _TEXT_CAP)},
        }
    ]

    final = final or {}
    for step in final.get("trace") or []:
        rows.append({**common, **_step_row(step, final, reply)})

    rows.append(
        {
            **common,
            "node": str(AuditNode.DELIVERY),
            "action": str(outcome),
            # End-to-end CẢ LƯỢT (không phải tổng node) — con số dùng cho NFR-1 ≤ 5s.
            "duration_ms": total_ms,
            "confidence": final.get("retrieval_confidence"),
            "uncertainty_flags": list(final.get("uncertainty_flags") or []),
            "escalation_reason": final.get("escalation_reason"),
            "detail": {
                "outcome": str(outcome),
                "intent": final.get("intent"),
                "agent_action": str(final.get("action")) if final.get("action") else None,
                "priority": final.get("priority"),
                "severity": final.get("severity"),
                "status": str(final.get("status")) if final.get("status") else None,
                "reply_len": len(reply or ""),
                "customer_text": _clip(customer_text, _TEXT_CAP),
            },
        }
    )
    return rows


async def record_turn(
    *,
    turn_id: uuid.UUID,
    conversation_id: uuid.UUID | None,
    customer_text: str,
    final: dict[str, Any] | None,
    reply: str,
    outcome: str,
    total_ms: int,
) -> int:
    """Ghi nhật ký một lượt (session NGẮN, 1 commit). Trả số dòng đã ghi; **KHÔNG BAO GIỜ ném lỗi**.

    Gọi SAU khi khách đã nhận phản hồi → độ trễ khách thấy không đổi.
    """
    try:
        rows = build_turn_rows(
            turn_id=turn_id,
            conversation_id=conversation_id,
            customer_text=customer_text,
            final=final,
            reply=reply,
            outcome=outcome,
            total_ms=total_ms,
        )
        async with AsyncSessionLocal() as session:
            session.add_all([AuditLog(**row) for row in rows])
            await session.commit()
        return len(rows)
    except Exception as exc:  # noqa: BLE001 — audit là việc PHỤ, không được làm hỏng lượt trả lời.
        log.warning("record_turn failed (bỏ qua) turn=%s: %s", turn_id, exc)
        return 0


__all__ = ["write_audit", "build_turn_rows", "record_turn", "rag_sources", "TurnOutcome"]
