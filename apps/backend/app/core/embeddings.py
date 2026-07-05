"""Embeddings (OpenAI) cho RAG — PRD §13.

Embeddings KHÔNG bị gate bởi ENABLE_LLM: RAG cần embeddings để chạy (ENABLE_LLM chỉ gate bước chọn
intent bằng LLM ở Intent Classifier — PRD §7.1). Async-first, config từ env (CLAUDE.md — không hardcode
key/model).
"""

from __future__ import annotations

from openai import AsyncOpenAI

from .config import settings

_client: AsyncOpenAI | None = None
_dim: int | None = None


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        # api_key có thể None -> OpenAI SDK báo lỗi rõ khi gọi. Caller (intent_node) phải degrade an toàn
        # TRƯỚC khi tới đây khi thiếu key (giữ `make test` chạy offline — plan §5).
        _client = AsyncOpenAI(api_key=settings.llm_api_key)
    return _client


async def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed danh sách chuỗi trong 1 request (giữ nguyên thứ tự đầu vào)."""
    if not texts:
        return []
    resp = await _get_client().embeddings.create(model=settings.embedding_model, input=texts)
    return [item.embedding for item in resp.data]


async def embed_text(text: str) -> list[float]:
    """Embed 1 chuỗi."""
    return (await embed_texts([text]))[0]


async def embedding_dim() -> int:
    """Số chiều vector của embedding model — suy ra bằng 1 chuỗi probe (tránh hardcode). Cache lại."""
    global _dim
    if _dim is None:
        _dim = len(await embed_text("dim probe"))
    return _dim


async def close_openai() -> None:
    """Đóng client (đối xứng close_redis/close_qdrant) — gọi ở lifespan shutdown."""
    global _client
    if _client is not None:
        await _client.close()
        _client = None
