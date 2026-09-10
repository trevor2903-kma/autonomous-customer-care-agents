"""PERF-01.1 — client OpenAI dùng chung mang timeout + max_retries từ env (không phải mặc định SDK 600s × 3)."""

from __future__ import annotations

import pytest

from app.core import embeddings


async def test_shared_openai_client_uses_env_timeout_and_retries(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(embeddings, "_client", None)
    monkeypatch.setattr(embeddings.settings, "llm_api_key", "sk-test")
    monkeypatch.setattr(embeddings.settings, "llm_timeout_seconds", 7.5)
    monkeypatch.setattr(embeddings.settings, "llm_max_retries", 0)

    client = embeddings.get_openai()
    try:
        assert client.timeout == 7.5
        assert client.max_retries == 0
        assert embeddings.get_openai() is client  # vẫn MỘT client dùng chung (Agent 1 + RAG + Agent 4)
    finally:
        await client.close()
