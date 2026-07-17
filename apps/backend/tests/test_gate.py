"""Gate duyệt nháp (08a) — gate_holds: auto_reply nhạy cảm → giữ nháp; handoff/không-nhạy-cảm/tắt → không giữ.

Hàm thuần (đọc settings), offline. FR-GATE-2: human_handoff LUÔN escalate (KHÔNG bao giờ qua gate).
"""

from __future__ import annotations

import pytest

from app.api.ws.chat import gate_holds
from app.core.config import settings
from app.models.enums import ConversationStatus


def test_gate_holds_sensitive_auto_reply(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "auto_reply_review", True)
    # refund/complaint/exchange ∈ sensitive mặc định → auto_reply GIỮ nháp
    assert gate_holds(ConversationStatus.REPLIED, "refund") is True
    assert gate_holds(ConversationStatus.REPLIED, "complaint") is True


def test_gate_skips_non_sensitive(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "auto_reply_review", True)
    assert gate_holds(ConversationStatus.REPLIED, "shipping") is False
    assert gate_holds(ConversationStatus.REPLIED, "product_price") is False


def test_gate_never_holds_handoff(monkeypatch: pytest.MonkeyPatch) -> None:
    # human_handoff (IN_HUMAN_QUEUE) LUÔN escalate — bất biến FR-GATE-2, không qua gate dù intent nhạy cảm.
    monkeypatch.setattr(settings, "auto_reply_review", True)
    assert gate_holds(ConversationStatus.IN_HUMAN_QUEUE, "refund") is False


def test_gate_off_sends_directly(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "auto_reply_review", False)
    assert gate_holds(ConversationStatus.REPLIED, "refund") is False
