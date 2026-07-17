"""Bất biến HITL (08a/08b/08c) — buộc hàng đợi admin ↔ status-gate khách nhất quán. Offline.

Chống hồi quy khi ai đó đổi tập trạng thái ở một nơi mà quên nơi kia (vd bỏ PENDING_APPROVAL khỏi hàng đợi
nhưng vẫn gate ở WS khách → ca kẹt vô hình).
"""

from __future__ import annotations

from app.api.routes.admin import _QUEUE_STATUSES
from app.api.ws.chat import HUMAN_HANDLED_STATUSES, should_run_ai
from app.models.enums import ConversationStatus


def test_queue_shows_waiting_cases() -> None:
    # Hàng đợi admin = ca ĐANG CHỜ người: escalate (IN_HUMAN_QUEUE) + chờ duyệt nháp (PENDING_APPROVAL).
    assert ConversationStatus.IN_HUMAN_QUEUE in _QUEUE_STATUSES
    assert ConversationStatus.PENDING_APPROVAL in _QUEUE_STATUSES


def test_queued_cases_gate_the_ai() -> None:
    # Mọi trạng thái trong hàng đợi PHẢI gate AI (khách nhắn → không chạy pipeline, route sang admin).
    for status in _QUEUE_STATUSES:
        assert should_run_ai(status) is False


def test_human_handling_gated_but_not_in_queue() -> None:
    # Đang tiếp quản chat: AI gated NHƯNG KHÔNG nằm hàng đợi (đã có người xử lý, không còn "chờ").
    assert should_run_ai(ConversationStatus.HUMAN_HANDLING) is False
    assert ConversationStatus.HUMAN_HANDLING in HUMAN_HANDLED_STATUSES
    assert ConversationStatus.HUMAN_HANDLING not in _QUEUE_STATUSES


def test_replied_and_new_not_gated() -> None:
    # Sau khi trả lời / hội thoại mới → AI chạy bình thường.
    assert should_run_ai(ConversationStatus.REPLIED) is True
    assert should_run_ai(ConversationStatus.NEW) is True
