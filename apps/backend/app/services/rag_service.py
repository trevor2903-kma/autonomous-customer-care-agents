"""RAG service (PRD §7.2, §13) — extract/chunk/embed/upsert + search, ở TẦNG SERVICE.

Truy hồi (`search`) viết Ở ĐÂY để Knowledge Agent (PRD §7.2) tái dùng — KHÔNG nhét cứng vào node intent.
Async-first, config từ env (CLAUDE.md).

**Reset-and-reingest** (plan §1): `apps/backend/knowledge/` là NGUỒN CHÂN LÝ; Qdrant là bản phái sinh,
dựng lại từ repo. Upload qua UI = ad-hoc, non-canonical (mất khi reindex).

Hai đường nạp:
- **KB repo** (canonical): frontmatter → chunk theo section `##` → + query-expansion. Payload MANG NHÃN
  `type/intent/title` để Agent 2 lọc theo intent (P4).
- **Upload ad-hoc**: chunking tổng quát (`chunk_text`) như cũ, payload cùng schema với `type="upload"`.

Lát cắt này: chỉ đẩy vector lên Qdrant, KHÔNG persist tài liệu xuống Postgres (bảng knowledge_document để yên).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

import frontmatter
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    FilterSelector,
    MatchValue,
    PayloadSchemaType,
    PointStruct,
    VectorParams,
)

from ..core.config import settings
from ..core.embeddings import embed_text, embed_texts, embedding_dim
from ..core.logging import get_logger
from ..core.qdrant_client import get_qdrant

log = get_logger("rag")

_WS_RE = re.compile(r"[ \t]+")
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?…])\s+")
# Heading cấp 2+ ở đầu dòng = ranh giới section (một `#` là tiêu đề tài liệu, đã có ở frontmatter `title`).
_SECTION_RE = re.compile(r"^#{2,}\s+.*$", re.MULTILINE)

# rag_service.py = apps/backend/app/services/... -> parents[2] = apps/backend
KNOWLEDGE_DIR = Path(__file__).resolve().parents[2] / "knowledge"
# `facts.md` KHÔNG vào Qdrant — Agent 4 nạp thẳng vào system prompt (plan §2.6). README không phải tri thức.
_ROOT_FILES_SKIPPED = {"facts.md", "README.md"}
# Section giữ NGUYÊN KHỐI dù dài: cắt câu giữa chừng làm mất thứ tự các bước chẩn đoán (plan §2.4).
_ATOMIC_HEADINGS = ("bot diagnostic flow",)
# Section KHÔNG index: ghi chú nội bộ cho nhân viên. Chặn ở NGUỒN (ingest) chắc hơn dạy prompt đừng trích —
# nội dung này hay chứa hành động shop sẽ làm ("xử lý hoàn tiền…") mà bot KHÔNG được hứa với khách.
_EXCLUDED_HEADING_RE = re.compile(r"^internal note\b", re.IGNORECASE)


# Payload phải có INDEX mới filter được — Qdrant trả 400 "Index required but not found" nếu thiếu.
# `source`: xoá doc upload ad-hoc (P3). `intent`: retrieve theo intent (P4).
_INDEXED_PAYLOAD_FIELDS = ("source", "intent")


async def ensure_collection() -> None:
    """Tạo collection Qdrant + payload index nếu chưa có (idempotent). Size vector suy từ embedding model."""
    client = get_qdrant()
    if not await client.collection_exists(settings.qdrant_collection):
        await client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=VectorParams(size=await embedding_dim(), distance=Distance.COSINE),
        )
    # Chạy MỌI lần (không chỉ khi vừa tạo): collection dựng bởi bản code cũ chưa có index này.
    for field in _INDEXED_PAYLOAD_FIELDS:
        try:
            await client.create_payload_index(
                collection_name=settings.qdrant_collection,
                field_name=field,
                field_schema=PayloadSchemaType.KEYWORD,
            )
        except Exception as exc:  # noqa: BLE001 — index đã có / race khi chạy song song: không chặn ingest.
            log.debug("payload index %r: %s", field, exc)


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


def chunk_sections(body: str, max_chars: int = 1200) -> list[str]:
    """Chunk theo SECTION (`##`) — plan §2.4. Phần trước `##` đầu tiên là section 0 (mở bài).

    Mỗi section giữ NGUYÊN VĂN (kể cả bảng markdown/danh sách đánh số — cắt câu sẽ phá cấu trúc).
    Section dài > `max_chars` mới rơi về sentence-window (`chunk_text`), TRỪ section atomic
    (`## Bot Diagnostic Flow`) luôn giữ nguyên khối. Section `## Internal Note` bị LOẠI khỏi index
    (vẫn nằm trong file `.md` cho người đọc).
    """
    body = body.strip()
    if not body:
        return []

    bounds = [m.start() for m in _SECTION_RE.finditer(body)]
    cuts = [0, *bounds, len(body)] if bounds else [0, len(body)]
    sections = [body[a:b].strip() for a, b in zip(cuts, cuts[1:]) if body[a:b].strip()]

    chunks: list[str] = []
    for section in sections:
        first = section.splitlines()[0]
        # Chỉ dòng `##...` mới là heading — mở bài (section 0) không có heading, đừng suy diễn từ câu đầu.
        heading = first.lstrip("#").strip().lower() if first.startswith("#") else ""
        if heading and _EXCLUDED_HEADING_RE.match(heading):
            continue
        atomic = any(h in heading for h in _ATOMIC_HEADINGS)
        if atomic or len(section) <= max_chars:
            chunks.append(section)
        else:
            chunks.extend(chunk_text(section, size=max_chars))
    return chunks


@dataclass(frozen=True)
class KbDocument:
    """Một file `.md` canonical trong `knowledge/<type>/`. `type` SUY TỪ THƯ MỤC (plan §2.3)."""

    source: str  # đường dẫn tương đối gốc KB, vd 'faq/gia-san-pham.md' — khoá ổn định của tài liệu
    type: str
    intent: str | None
    title: str
    body: str
    questions: tuple[str, ...]


def load_kb_documents(root: Path | None = None) -> list[KbDocument]:
    """Duyệt `knowledge/<type>/*.md` → KbDocument. Bỏ file ở gốc (`facts.md`, `README.md`): không có
    thư mục thì không có `type`, và facts do Agent 4 nạp riêng."""
    root = root or KNOWLEDGE_DIR
    docs: list[KbDocument] = []
    for path in sorted(root.rglob("*.md")):
        rel = path.relative_to(root)
        if len(rel.parts) == 1 or path.name in _ROOT_FILES_SKIPPED:
            continue
        post = frontmatter.load(path)
        questions = post.get("questions") or []
        docs.append(
            KbDocument(
                source=rel.as_posix(),
                type=rel.parts[0],
                intent=post.get("intent"),
                title=post.get("title") or path.stem,
                body=post.content.strip(),
                questions=tuple(str(q).strip() for q in questions if str(q).strip()),
            )
        )
    return docs


def _payload(
    *, text: str, source: str, chunk_index: int, type: str, intent: str | None, title: str, question: str | None
) -> dict:
    """Payload chuẩn cho MỌI point (plan §2.3). `question` = câu hỏi sinh ra point query-expansion (None nếu
    là chunk thân) — cần để P6 đo ngưỡng tách riêng hit-faq và hit-thân, và để Inspector hiển thị nguồn khớp."""
    return {
        "text": text,
        "source": source,
        "chunk_index": chunk_index,
        "type": type,
        "intent": intent,
        "title": title,
        "question": question,
    }


def _kb_points(doc: KbDocument, chunks: list[str], vectors: list[list[float]]) -> list[PointStruct]:
    """Point thân (1/chunk) + point query-expansion (1/câu hỏi, vector=embed(câu hỏi), text=THÂN tài liệu).

    ID ổn định theo `source` → reset/reingest idempotent, sửa 1 file không đụng file khác.
    """
    n = len(chunks)
    points = [
        PointStruct(
            id=str(uuid5(NAMESPACE_URL, f"{doc.source}#c{i}")),
            vector=vectors[i],
            payload=_payload(
                text=chunk, source=doc.source, chunk_index=i, type=doc.type,
                intent=doc.intent, title=doc.title, question=None,
            ),
        )
        for i, chunk in enumerate(chunks)
    ]
    # Query-expansion (plan §2.4): khách hỏi bằng giọng nói thường, KB viết bằng giọng văn bản → khớp
    # câu-hỏi-với-câu-hỏi thay vì câu-hỏi-với-văn-bản. Trả về THÂN đầy đủ (doc KB ngắn) để không cắt cụt đáp án.
    answer = "\n\n".join(chunks)
    points += [
        PointStruct(
            id=str(uuid5(NAMESPACE_URL, f"{doc.source}#q{j}")),
            vector=vectors[n + j],
            payload=_payload(
                text=answer, source=doc.source, chunk_index=0, type=doc.type,
                intent=doc.intent, title=doc.title, question=question,
            ),
        )
        for j, question in enumerate(doc.questions)
    ]
    return points


async def ingest_kb_document(doc: KbDocument) -> int:
    """Chunk-theo-section + query-expansion → embed → upsert. Trả số point. KHÔNG persist Postgres (P3)."""
    await ensure_collection()
    chunks = chunk_sections(doc.body)
    if not chunks:
        return 0
    # Một request embed cho cả thân lẫn câu hỏi (giữ thứ tự: chunks trước, questions sau).
    vectors = await embed_texts([f"{doc.title}\n{c}" for c in chunks] + list(doc.questions))
    points = _kb_points(doc, chunks, vectors)
    await get_qdrant().upsert(collection_name=settings.qdrant_collection, points=points, wait=True)
    return len(points)


async def ingest_knowledge_base(root: Path | None = None) -> dict:
    """**Reset-and-reingest** toàn bộ KB repo: drop collection → nạp lại từng doc. Trả thống kê.

    Dùng chung cho `scripts/ingest_kb.py` và `POST /rag/reindex` (P3) — một đường nạp duy nhất.
    """
    docs = load_kb_documents(root)
    await reset_collection()
    per_doc: list[dict] = []
    for doc in docs:
        points = await ingest_kb_document(doc)
        per_doc.append(
            {"source": doc.source, "type": doc.type, "intent": doc.intent, "title": doc.title,
             "questions": len(doc.questions), "points": points}
        )
        log.info("kb.ingest %s -> %d points", doc.source, points)
    return {
        "documents": len(docs),
        "points": sum(d["points"] for d in per_doc),
        "collection": settings.qdrant_collection,
        "per_document": per_doc,
    }


async def ingest_document(text: str, source: str, *, type: str = "upload", title: str | None = None) -> int:
    """Upload AD-HOC: chunk tổng quát → embed → upsert. Payload cùng schema KB nhưng `intent=None`
    (không có frontmatter) → Agent 2 chỉ thấy nó ở lượt không-filter. Trả số chunk."""
    await ensure_collection()
    chunks = chunk_text(text)
    if not chunks:
        return 0
    vectors = await embed_texts(chunks)
    points = [
        PointStruct(
            id=str(uuid5(NAMESPACE_URL, f"{source}#{i}")),
            vector=vec,
            payload=_payload(
                text=chunk, source=source, chunk_index=i, type=type,
                intent=None, title=title or source, question=None,
            ),
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


async def delete_by_source(source: str) -> None:
    """Xoá mọi point của một tài liệu (theo `payload.source`) — dùng khi gỡ doc upload ad-hoc (P3)."""
    await ensure_collection()  # bảo đảm có payload index `source`, nếu không Qdrant trả 400
    await get_qdrant().delete(
        collection_name=settings.qdrant_collection,
        points_selector=FilterSelector(
            filter=Filter(must=[FieldCondition(key="source", match=MatchValue(value=source))])
        ),
        wait=True,
    )


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
