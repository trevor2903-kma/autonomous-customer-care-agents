"""Escalation service (08b) — dựng EscalationCard từ FINAL STATE + persist + list hàng đợi (PRD §11, §17).

Card KHÔNG re-wire graph: gom intent/entities/rag_context/reason/priority/severity (+ nháp cho ca PENDING_APPROVAL)
từ final state của pipeline → lưu lên conversation. `list_escalations` sắp priority GIẢM DẦN (high→low) rồi
last_message_at mới nhất. `build_escalation_card` + `priority_rank` là hàm THUẦN (test offline); phần DB verify live.
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import case, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.conversation import Conversation

# Xếp hạng ưu tiên cho sort hàng đợi (cao = xử lý trước). Priority ngoài bảng / None -> 0 (thấp nhất).
_PRIORITY_RANK: dict[str, int] = {"high": 3, "medium": 2, "low": 1}


def priority_rank(priority: str | None) -> int:
    """Rank số của priority (cao = ưu tiên hơn) cho sort hàng đợi. Hàm thuần."""
    return _PRIORITY_RANK.get(priority or "", 0)


def _top_sources(rag_contexts: list[dict[str, Any]], limit: int = 3) -> list[dict[str, Any]]:
    """Gọn rag_contexts thành nguồn hàng đầu (source + score + snippet ngắn) cho card."""
    out: list[dict[str, Any]] = []
    for c in rag_contexts[:limit]:
        text = (c.get("text") or "").strip()
        out.append(
            {
                "source": c.get("source") or "?",
                "score": c.get("score"),
                "snippet": text[:160] + ("…" if len(text) > 160 else ""),
            }
        )
    return out


def build_escalation_card(
    final_state: dict[str, Any], trigger_message: str, suggested_reply: str = ""
) -> dict[str, Any]:
    """Dựng EscalationCard từ final state (PRD §11): tóm tắt (tin khách kích hoạt) + intent/entities + nguồn RAG
    + escalation_reason + priority/severity + nháp gợi ý. `suggested_reply` rỗng cho human_handoff, = nháp Agent 4
    cho PENDING_APPROVAL. Hàm THUẦN (không DB) — test offline."""
    return {
        "summary": trigger_message.strip(),
        "intent": final_state.get("intent"),
        "entities": final_state.get("entities") or {},
        "rag_context": _top_sources(final_state.get("rag_contexts") or []),
        "escalation_reason": final_state.get("escalation_reason"),
        "priority": final_state.get("priority"),
        "severity": final_state.get("severity"),
        "suggested_reply": suggested_reply or "",
    }


async def persist_escalation(
    session: AsyncSession,
    conversation_id: uuid.UUID,
    *,
    card: dict[str, Any],
    priority: str | None,
    severity: str | None,
    reason: str | None,
) -> None:
    """Lưu card + priority/severity/reason lên conversation (session NGẮN — Neon free). Không load messages."""
    conv = await session.get(Conversation, conversation_id)
    if conv is None:
        return
    conv.escalation_card = card
    conv.priority = priority
    conv.severity = severity
    conv.escalation_reason = reason
    await session.commit()


async def list_escalations(
    session: AsyncSession, statuses: list[str], limit: int = 50
) -> list[Conversation]:
    """Hàng đợi escalation: conversation ∈ statuses, sắp priority GIẢM DẦN (high→low) rồi last_message_at mới nhất.
    Ưu tiên bằng CASE (string priority KHÔNG sort đúng theo bảng chữ) — PRD §11/§17."""
    rank = case(
        (Conversation.priority == "high", 3),
        (Conversation.priority == "medium", 2),
        (Conversation.priority == "low", 1),
        else_=0,
    )
    stmt = (
        select(Conversation)
        .where(Conversation.status.in_(statuses))
        .order_by(rank.desc(), Conversation.last_message_at.desc())
        .limit(limit)
        .options(selectinload(Conversation.messages))
    )
    return list((await session.execute(stmt)).scalars().all())
