"""Qdrant client (Cloud) — vector DB cho RAG (PRD §13).

Scaffold: chỉ dựng client + ping (đếm collection). Embedding/nạp/truy hồi tri thức là phase sau
(KHÔNG embed/retrieve thật ở scaffold — PRD §22).
"""

from __future__ import annotations

from qdrant_client import AsyncQdrantClient

from .config import settings

_client: AsyncQdrantClient | None = None


def get_qdrant() -> AsyncQdrantClient:
    global _client
    if _client is None:
        _client = AsyncQdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)
    return _client


async def ping_qdrant() -> int:
    """Health check: trả số collection hiện có."""
    result = await get_qdrant().get_collections()
    return len(result.collections)


async def close_qdrant() -> None:
    global _client
    if _client is not None:
        await _client.close()
        _client = None
