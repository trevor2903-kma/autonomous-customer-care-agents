"""Status-gate (08c) — should_run_ai: người đang xử lý → AI KHÔNG chạy. Hàm thuần, offline."""

from __future__ import annotations

from app.api.ws.chat import should_run_ai
from app.models.enums import ConversationStatus


def test_ai_runs_for_active_new_and_none() -> None:
    assert should_run_ai(None) is True  # hội thoại mới → AI chạy
    assert should_run_ai(ConversationStatus.NEW) is True
    assert should_run_ai(ConversationStatus.REPLIED) is True
    assert should_run_ai("REPLIED") is True  # str từ DB


def test_ai_gated_when_human_handling() -> None:
    assert should_run_ai(ConversationStatus.IN_HUMAN_QUEUE) is False
    assert should_run_ai(ConversationStatus.HUMAN_HANDLING) is False
    assert should_run_ai(ConversationStatus.PENDING_APPROVAL) is False
    assert should_run_ai("IN_HUMAN_QUEUE") is False  # str từ DB khớp StrEnum
