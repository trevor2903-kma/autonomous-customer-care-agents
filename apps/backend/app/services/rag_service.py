"""RAG service (PRD §7.2, §13) — chunk/embed/upsert + search, ở TẦNG SERVICE.

Truy hồi (`search`) viết Ở ĐÂY để Knowledge Agent (PRD §7.2) tái dùng về sau — KHÔNG nhét cứng vào node
intent (quyết định kiến trúc, plan). Async-first, config từ env (CLAUDE.md).

Lát cắt này: chỉ đẩy vector lên Qdrant, KHÔNG persist tài liệu xuống Postgres (bảng knowledge_document để yên).
"""

from __future__ import annotations

import re
from uuid import NAMESPACE_URL, uuid5

from qdrant_client.models import Distance, PointStruct, VectorParams

from ..core.config import settings
from ..core.embeddings import embed_text, embed_texts, embedding_dim
from ..core.qdrant_client import get_qdrant

_HEADING = "## "
_CATEGORY_RE = re.compile(r"^\s*-\s*category\s*:\s*(.+?)\s*$", re.IGNORECASE)


async def ensure_collection() -> None:
    """Tạo collection Qdrant nếu chưa có (idempotent). Size vector suy ra từ embedding model (probe)."""
    client = get_qdrant()
    if await client.collection_exists(settings.qdrant_collection):
        return
    await client.create_collection(
        collection_name=settings.qdrant_collection,
        vectors_config=VectorParams(size=await embedding_dim(), distance=Distance.COSINE),
    )


def chunk_by_heading(text: str) -> list[dict]:
    """Tách tài liệu theo dòng '## <intent>' → mỗi section = 1 chunk {intent, category, text}.

    Nội dung trước heading đầu tiên (tiêu đề/giới thiệu) bị bỏ qua. `text` giữ CẢ section (kể cả heading)
    để embed giàu ngữ cảnh; `category` lấy từ dòng '- category: <...>' nếu có.
    """
    sections: list[dict] = []
    intent: str | None = None
    lines: list[str] = []

    def flush() -> None:
        if intent is None:
            return
        category: str | None = None
        for ln in lines:
            m = _CATEGORY_RE.match(ln)
            if m:
                category = m.group(1).strip()
                break
        sections.append({"intent": intent, "category": category, "text": "\n".join(lines).strip()})

    for raw in text.splitlines():
        if raw.startswith(_HEADING):
            flush()
            intent = raw[len(_HEADING):].strip()
            lines = [raw]
        elif intent is not None:
            lines.append(raw)
    flush()
    return sections


def _point_id(source: str, intent: str) -> str:
    """UUID ổn định theo (source, intent) → re-upload ghi đè đúng point (idempotent)."""
    return str(uuid5(NAMESPACE_URL, f"{source}#{intent}"))


async def ingest_document(text: str, source: str) -> int:
    """Chunk → embed → upsert Qdrant. Trả số chunk đã nạp. KHÔNG persist xuống Postgres."""
    await ensure_collection()
    chunks = chunk_by_heading(text)
    if not chunks:
        return 0
    vectors = await embed_texts([c["text"] for c in chunks])
    points = [
        PointStruct(
            id=_point_id(source, c["intent"]),
            vector=vec,
            payload={"intent": c["intent"], "category": c["category"], "text": c["text"], "source": source},
        )
        for c, vec in zip(chunks, vectors)
    ]
    await get_qdrant().upsert(collection_name=settings.qdrant_collection, points=points, wait=True)
    return len(points)


async def collection_info() -> dict:
    """Thông tin collection (points_count, vector_size). Bảo đảm collection tồn tại trước."""
    await ensure_collection()
    info = await get_qdrant().get_collection(settings.qdrant_collection)
    return {
        "collection": settings.qdrant_collection,
        "points_count": info.points_count,
        "vector_size": info.config.params.vectors.size,
    }


async def reset_collection() -> None:
    """Drop + tạo lại collection (tiện test lại nhiều lần)."""
    client = get_qdrant()
    if await client.collection_exists(settings.qdrant_collection):
        await client.delete_collection(settings.qdrant_collection)
    await ensure_collection()


async def search(query: str, top_k: int = 3) -> list[dict]:
    """Truy hồi top-k chunk gần nhất (cosine). Trả [{intent, category, text, score}].

    TẦNG SERVICE để Knowledge Agent (PRD §7.2) tái dùng — Intent Classifier ở lát cắt này gọi tạm để
    tự phân loại (không nhét truy hồi cứng vào node intent).
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
                "intent": payload.get("intent"),
                "category": payload.get("category"),
                "text": payload.get("text"),
                "score": point.score,
            }
        )
    return hits
