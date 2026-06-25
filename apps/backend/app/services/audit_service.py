"""Service audit — ghi nhật ký kiểm toán (PRD §20, NFR-4: 100% hành động agent/Admin truy vết được).

Scaffold: helper ghi 1 dòng audit. Caller tự commit (hoặc dùng session riêng ở BackgroundTask — Phase 5).
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from ..models.audit_log import AuditLog


async def write_audit(
    session: AsyncSession,
    *,
    conversation_id: uuid.UUID | None = None,
    message_id: uuid.UUID | None = None,
    node: str | None = None,
    action: str | None = None,
    confidence: float | None = None,
    uncertainty_flags: list[str] | None = None,
    escalation_reason: str | None = None,
    detail: dict[str, Any] | None = None,
) -> AuditLog:
    entry = AuditLog(
        conversation_id=conversation_id,
        message_id=message_id,
        node=node,
        action=action,
        confidence=confidence,
        uncertainty_flags=uncertainty_flags or [],
        escalation_reason=escalation_reason,
        detail=detail or {},
    )
    session.add(entry)
    await session.flush()
    return entry
