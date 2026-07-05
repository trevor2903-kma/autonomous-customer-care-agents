"""RAG service (PRD §7.2, §13) — chunk/embed/upsert + search, ở TẦNG SERVICE.

Truy hồi (`search`) viết Ở ĐÂY để Knowledge Agent (PRD §7.2) tái dùng về sau — KHÔNG nhét cứng vào node
intent (quyết định kiến trúc, plan). Async-first, config từ env (CLAUDE.md).

Lát cắt này: chỉ đẩy vector lên Qdrant, KHÔNG persist tài liệu xuống Postgres (bảng knowledge_document để yên).
"""

from __future__ import annotations

from qdrant_client.models import Distance, VectorParams

from ..core.config import settings
from ..core.embeddings import embedding_dim
from ..core.qdrant_client import get_qdrant


async def ensure_collection() -> None:
    """Tạo collection Qdrant nếu chưa có (idempotent). Size vector suy ra từ embedding model (probe)."""
    client = get_qdrant()
    if await client.collection_exists(settings.qdrant_collection):
        return
    await client.create_collection(
        collection_name=settings.qdrant_collection,
        vectors_config=VectorParams(size=await embedding_dim(), distance=Distance.COSINE),
    )
