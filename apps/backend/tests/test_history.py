"""format_history (bộ nhớ đa lượt) — hàm thuần, offline. Định dạng lịch sử cho prompt Agent 1 + Agent 4."""

from __future__ import annotations

from app.agents.nodes._history import format_history


def test_empty_history_returns_empty() -> None:
    assert format_history(None) == ""
    assert format_history([]) == ""


def test_formats_customer_and_shop() -> None:
    h = [{"sender": "customer", "content": "phí ship nội thành?"}, {"sender": "ai", "content": "25-30k"}]
    out = format_history(h)
    assert "Khách: phí ship nội thành?" in out
    assert "Shop: 25-30k" in out
    assert out.endswith("\n\n")


def test_respects_limit() -> None:
    h = [{"sender": "customer", "content": f"tin{i}"} for i in range(10)]
    out = format_history(h, limit=3)
    assert "tin9" in out and "tin8" in out and "tin7" in out
    assert "tin6" not in out  # ngoài cửa sổ limit=3


def test_skips_empty_content() -> None:
    h = [{"sender": "customer", "content": "   "}, {"sender": "ai", "content": "ok ạ"}]
    out = format_history(h)
    assert "Shop: ok ạ" in out
    assert "Khách:" not in out  # content rỗng/khoảng trắng bị bỏ qua
