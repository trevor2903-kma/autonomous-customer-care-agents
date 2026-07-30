"""Cấu hình chung cho test — giữ `make test` OFFLINE (CLAUDE.md §4).

Langfuse đọc key từ `.env` GỐC REPO, nên trên máy đã cấu hình thật thì test sẽ dựng client thật và
BẮN TELEMETRY mỗi lần chạy: chậm, phụ thuộc mạng, và làm bẩn dữ liệu quan sát bằng số liệu của test.
Tắt cứng ở đây; test nào cần kiểm tra chính lớp tracing thì tự bật lại bằng monkeypatch.
"""

from __future__ import annotations

import pytest

from app.core import tracing


@pytest.fixture(autouse=True)
def _tracing_off(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(tracing.settings, "langfuse_public_key", None)
    monkeypatch.setattr(tracing.settings, "langfuse_secret_key", None)
    monkeypatch.setattr(tracing, "_client", None)
    monkeypatch.setattr(tracing, "_init_done", False)
