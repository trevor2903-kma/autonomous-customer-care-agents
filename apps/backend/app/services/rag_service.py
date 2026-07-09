"""RAG service (PRD §7.2, §13) — extract/chunk/embed/upsert + search, ở TẦNG SERVICE.

Truy hồi (`search`) viết Ở ĐÂY để Knowledge Agent (PRD §7.2) tái dùng — KHÔNG nhét cứng vào node intent.
Chunking TỔNG QUÁT (không theo heading); payload GENERIC {text, source, chunk_index} (chunk không mang nhãn
intent/category). Async-first, config từ env (CLAUDE.md).

Lát cắt này: chỉ đẩy vector lên Qdrant, KHÔNG persist tài liệu xuống Postgres (bảng knowledge_document để yên).
"""

from __future__ import annotations

import re
from uuid import NAMESPACE_URL, uuid5

from qdrant_client.models import Distance, PointStruct, VectorParams

from ..core.config import settings
from ..core.embeddings import embed_text, embed_texts, embedding_dim
from ..core.qdrant_client import get_qdrant

_WS_RE = re.compile(r"[ \t]+")
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?…])\s+")


async def ensure_collection() -> None:
    """Tạo collection Qdrant nếu chưa có (idempotent). Size vector suy ra từ embedding model (probe)."""
    client = get_qdrant()
    if await client.collection_exists(settings.qdrant_collection):
        return
    await client.create_collection(
        collection_name=settings.qdrant_collection,
        vectors_config=VectorParams(size=await embedding_dim(), distance=Distance.COSINE),
    )


def _normalize(text: str) -> str:
    """Chuẩn hoá khoảng trắng theo dòng; giữ ranh giới đoạn (dòng trống)."""
    lines = [_WS_RE.sub(" ", ln).strip() for ln in text.splitlines()]
    return re.sub(r"\n{2,}", "\n\n", "\n".join(lines)).strip()


def chunk_text(text: str, size: int = 800, overlap: int = 120) -> list[str]:
    """Chunking TỔNG QUÁT (không theo heading): chuẩn hoá → tách câu → gộp cửa sổ ~size ký tự,
    chồng lấn ~overlap (giữ vài câu cuối), ưu tiên ranh giới câu."""
    normalized = _normalize(text)
    if not normalized:
        return []

    segments: list[str] = []
    for para in normalized.split("\n\n"):
        for sent in _SENTENCE_SPLIT_RE.split(para.strip()):
            sent = sent.strip()
            if sent:
                segments.append(sent)
    if not segments:
        return []

    chunks: list[str] = []
    cur: list[str] = []
    cur_len = 0
    for seg in segments:
        if cur and cur_len + len(seg) + 1 > size:
            chunks.append(" ".join(cur))
            # overlap: giữ lại các câu cuối tổng ~overlap ký tự cho chunk kế.
            keep: list[str] = []
            klen = 0
            for s in reversed(cur):
                if keep and klen + len(s) + 1 > overlap:
                    break
                keep.insert(0, s)
                klen += len(s) + 1
            cur, cur_len = keep, klen
        cur.append(seg)
        cur_len += len(seg) + 1
    if cur:
        chunks.append(" ".join(cur))
    return chunks


async def ingest_document(text: str, source: str) -> int:
    """Chunk (tổng quát) → embed → upsert Qdrant với payload GENERIC. Trả số chunk. KHÔNG persist Postgres."""
    await ensure_collection()
    chunks = chunk_text(text)
    if not chunks:
        return 0
    vectors = await embed_texts(chunks)
    points = [
        PointStruct(
            id=str(uuid5(NAMESPACE_URL, f"{source}#{i}")),
            vector=vec,
            payload={"text": chunk, "source": source, "chunk_index": i},
        )
        for i, (chunk, vec) in enumerate(zip(chunks, vectors))
    ]
    await get_qdrant().upsert(collection_name=settings.qdrant_collection, points=points, wait=True)
    return len(points)


async def collection_info() -> dict:
    """Thông tin collection: points_count + danh sách distinct source (scroll toàn bộ payload.source)."""
    await ensure_collection()
    client = get_qdrant()
    info = await client.get_collection(settings.qdrant_collection)

    sources: set[str] = set()
    offset = None
    while True:
        points, offset = await client.scroll(
            collection_name=settings.qdrant_collection,
            limit=256,
            offset=offset,
            with_payload=True,
            with_vectors=False,
        )
        for point in points:
            src = (point.payload or {}).get("source")
            if src:
                sources.add(src)
        if offset is None:
            break

    return {
        "collection": settings.qdrant_collection,
        "points_count": info.points_count,
        "sources": sorted(sources),
    }


async def reset_collection() -> None:
    """Drop + tạo lại collection (payload đổi so với bản seed → cần reset trước khi upload lại)."""
    client = get_qdrant()
    if await client.collection_exists(settings.qdrant_collection):
        await client.delete_collection(settings.qdrant_collection)
    await ensure_collection()


async def search(query: str, top_k: int = 4) -> list[dict]:
    """Truy hồi top-k chunk gần nhất (cosine). Trả [{text, source, score, chunk_index}] (payload generic).

    TẦNG SERVICE để Knowledge Agent (PRD §7.2) tái dùng — Intent Classifier gọi để lấy ngữ cảnh phân loại.
    """
    vector = await embed_text(query)
    res = await get_qdrant().query_points(
        collection_name=settings.qdrant_collection,
        query=vector,
        limit=top_k,
        with_payload=True,
    )
    hits: list[dict] = []
    for point in res.points:
        payload = point.payload or {}
        hits.append(
            {
                "text": payload.get("text"),
                "source": payload.get("source"),
                "chunk_index": payload.get("chunk_index"),
                "score": point.score,
            }
        )
    return hits
