"""Langfuse (slice obs P3) — BỔ TRỢ, phải no-op hoàn toàn khi thiếu key. Offline, KHÔNG network."""

from __future__ import annotations

import pytest

from app.core import tracing


@pytest.fixture(autouse=True)
def _reset_client(monkeypatch: pytest.MonkeyPatch) -> None:
    # Client là singleton lười — reset giữa các test để `enabled()` được đọc lại.
    monkeypatch.setattr(tracing, "_client", None)
    monkeypatch.setattr(tracing, "_init_done", False)


def test_disabled_without_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(tracing.settings, "langfuse_public_key", None)
    monkeypatch.setattr(tracing.settings, "langfuse_secret_key", None)
    assert tracing.enabled() is False
    assert tracing.trace_url() is None


def test_half_configured_counts_as_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    # Chỉ có public key = cấu hình nửa vời → sẽ lỗi lúc gửi. Coi như tắt còn hơn lỗi giữa lượt khách.
    monkeypatch.setattr(tracing.settings, "langfuse_public_key", "pk-test")
    monkeypatch.setattr(tracing.settings, "langfuse_secret_key", None)
    assert tracing.enabled() is False


def test_observe_llm_is_noop_and_never_touches_network(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(tracing.settings, "langfuse_public_key", None)
    monkeypatch.setattr(tracing.settings, "langfuse_secret_key", None)

    def _boom(*a: object, **k: object):
        raise AssertionError("KHÔNG được dựng client Langfuse khi thiếu key")

    monkeypatch.setattr(tracing, "_get_client", lambda: None if True else _boom())

    with tracing.observe_llm("agent1.classify", model="gpt", input="x") as span:
        span.finish(output="y", usage={"prompt_tokens": 10})  # không được ném
    assert tracing._client is None


def test_client_init_failure_degrades_silently(monkeypatch: pytest.MonkeyPatch) -> None:
    """Sai cấu hình / thiếu gói → tắt vĩnh viễn, KHÔNG ném lên pipeline."""
    monkeypatch.setattr(tracing.settings, "langfuse_public_key", "pk-test")
    monkeypatch.setattr(tracing.settings, "langfuse_secret_key", "sk-test")

    import builtins

    real_import = builtins.__import__

    def fake_import(name: str, *a: object, **k: object):
        if name == "langfuse":
            raise ImportError("gói không có")
        return real_import(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    assert tracing._get_client() is None
    with tracing.observe_llm("x") as span:
        span.finish(output="y")


def test_span_update_error_is_swallowed() -> None:
    """Bất biến §1: tracing hỏng KHÔNG được làm hỏng lượt trả lời khách."""

    class _Broken:
        def update(self, **kw: object) -> None:
            raise RuntimeError("langfuse down")

    tracing._Span(_Broken()).finish(output="x", usage={"prompt_tokens": 1})  # không ném


def test_usage_dict_maps_openai_fields() -> None:
    class _Usage:
        prompt_tokens = 120
        completion_tokens = 45
        total_tokens = 165

    assert tracing._usage_dict(_Usage()) == {"input": 120, "output": 45, "total": 165}
    assert tracing._usage_dict({"input": 5, "output": 6}) == {"input": 5, "output": 6}
    assert tracing._usage_dict(None) == {}  # usage vắng (một số provider) → không bịa số


def test_flush_safe_when_disabled() -> None:
    tracing.flush()  # không ném dù chưa có client


def test_set_turn_context_roundtrip() -> None:
    tracing.set_turn("t-1", "c-1")
    assert tracing._ctx() == {"turn_id": "t-1", "conversation_id": "c-1"}
    tracing.set_turn(None, None)
    assert tracing._ctx() == {"turn_id": "", "conversation_id": ""}
