"""RAG service (PRD §7.2, §13) — extract/chunk/embed/upsert + search, ở TẦNG SERVICE.

Truy hồi (`search`) viết Ở ĐÂY để Knowledge Agent (PRD §7.2) tái dùng — KHÔNG nhét cứng vào node intent.
Async-first, config từ env (CLAUDE.md).

**Reset-and-reingest** (plan §1): `apps/backend/knowledge/` là NGUỒN CHÂN LÝ; Qdrant là bản phái sinh,
dựng lại từ repo. Upload qua UI = ad-hoc, non-canonical (mất khi reindex).

**Blue/green qua ALIAS** (audit v2, RAG-01.1): tên phục vụ `settings.qdrant_collection` là ALIAS trỏ tới
một collection VẬT LÝ `<tên>__<mốc>`. Reindex dựng collection vật lý MỚI, nạp đủ KB vào đó rồi mới đổi
alias (một lời gọi nguyên tử) và bỏ bản cũ — retrieval không bao giờ thấy collection rỗng/nạp dở.

Hai đường nạp:
- **KB repo** (canonical): frontmatter → chunk theo section `##` → + query-expansion. Payload MANG NHÃN
  `type/intent/title` để Agent 2 lọc theo intent (P4).
- **Upload ad-hoc**: chunking tổng quát (`chunk_text`) như cũ, payload cùng schema với `type="upload"` +
  `upload_version` (upload lại cùng tên = THAY bản cũ, không gộp). Section `## Internal Note` bị loại như KB repo.

Lát cắt này: chỉ đẩy vector lên Qdrant, KHÔNG persist tài liệu xuống Postgres (bảng knowledge_document để yên).
"""

from __future__ import annotations

import contextvars
import re
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from uuid import NAMESPACE_URL, uuid4, uuid5

import frontmatter
from qdrant_client.models import (
    CreateAlias,
    CreateAliasOperation,
    DeleteAlias,
    DeleteAliasOperation,
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
from ..core.sanitize import normalize_text, sanitize_untrusted_document
from ..models.enums import Intent

log = get_logger("rag")

_WS_RE = re.compile(r"[ \t]+")
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?…])\s+")
# Heading cấp 2+ ở đầu dòng = ranh giới section (một `#` là tiêu đề tài liệu, đã có ở frontmatter `title`).
_SECTION_RE = re.compile(r"^#{2,}\s+.*$", re.MULTILINE)

def _resolve_knowledge_dir() -> Path:
    curr = Path(__file__).resolve().parent
    for p in [curr, *curr.parents]:
        candidate = p / "knowledge"
        if candidate.is_dir():
            return candidate
    return Path(__file__).resolve().parents[1] / "knowledge"


KNOWLEDGE_DIR = _resolve_knowledge_dir()
# `facts.md` KHÔNG vào Qdrant — Agent 4 nạp thẳng vào system prompt (plan §2.6). README không phải tri thức.
_ROOT_FILES_SKIPPED = {"facts.md", "README.md"}
# Section giữ NGUYÊN KHỐI dù dài: cắt câu giữa chừng làm mất thứ tự các bước chẩn đoán (plan §2.4).
_ATOMIC_HEADINGS = ("bot diagnostic flow",)
# Section KHÔNG index: ghi chú nội bộ cho nhân viên. Chặn ở NGUỒN (ingest) chắc hơn dạy prompt đừng trích —
# nội dung này hay chứa hành động shop sẽ làm ("xử lý hoàn tiền…") mà bot KHÔNG được hứa với khách.
_EXCLUDED_HEADING_RE = re.compile(r"^internal note\b", re.IGNORECASE)


# Payload phải có INDEX mới filter được — Qdrant trả 400 "Index required but not found" nếu thiếu.
# `source`: xoá doc upload ad-hoc (P3). `intent`: retrieve theo intent (P4).
# `upload_version`: upload lại cùng tên = THAY bản cũ — gỡ point theo phiên bản (RAG-02.2).
_UPLOAD_VERSION = "upload_version"
_INDEXED_PAYLOAD_FIELDS = ("source", "intent", _UPLOAD_VERSION)


async def ensure_collection() -> None:
    """Bảo đảm tên phục vụ (`settings.qdrant_collection`) dùng được + có payload index (idempotent).

    Tên phục vụ là ALIAS trỏ tới collection vật lý (blue/green — `ingest_knowledge_base`). Chưa có gì (cài
    mới) → tạo collection vật lý + alias. Collection THẬT mang tên đó (bản cũ trước alias) vẫn dùng như
    thường — reindex kế tiếp mới chuyển sang alias. KHÔNG bao giờ tạo collection thật trùng tên alias.
    Hàm này có thể TẠO collection → chỉ gọi từ đường GHI (dưới khoá của `knowledge_service`).
    """
    if not await _serving_exists():
        await _activate(await _create_physical_collection())
        return
    # Chạy MỌI lần (không chỉ khi vừa tạo): collection dựng bởi bản code cũ chưa có index này.
    await _ensure_payload_indexes(settings.qdrant_collection)


async def _ensure_payload_indexes(collection: str) -> None:
    client = get_qdrant()
    for field in _INDEXED_PAYLOAD_FIELDS:
        try:
            await client.create_payload_index(
                collection_name=collection,
                field_name=field,
                field_schema=PayloadSchemaType.KEYWORD,
            )
        except Exception as exc:  # noqa: BLE001 — index đã có / race khi chạy song song: không chặn ingest.
            log.debug("payload index %r: %s", field, exc)


async def _alias_target(alias: str) -> str | None:
    """Collection vật lý mà `alias` đang trỏ tới; None nếu tên đó (chưa) là alias."""
    aliases = (await get_qdrant().get_aliases()).aliases
    return next((a.collection_name for a in aliases if a.alias_name == alias), None)


async def _serving_exists() -> bool:
    """Tên phục vụ đã dùng được chưa: là alias, HOẶC collection thật (bản cũ trước alias). Hỏi alias TRƯỚC —
    không dựa vào việc `collection_exists` có resolve alias hay không."""
    name = settings.qdrant_collection
    return await _alias_target(name) is not None or await get_qdrant().collection_exists(name)


async def _create_physical_collection() -> str:
    """Collection VẬT LÝ mới `<tên phục vụ>__<mốc>` (cùng vectors config + payload index như mọi khi). Chưa
    phục vụ ai cho tới khi `_activate` trỏ alias vào nó."""
    name = f"{settings.qdrant_collection}__{datetime.now(UTC):%Y%m%d%H%M%S}_{uuid4().hex[:6]}"
    await get_qdrant().create_collection(
        collection_name=name,
        vectors_config=VectorParams(size=await embedding_dim(), distance=Distance.COSINE),
    )
    await _ensure_payload_indexes(name)
    return name


async def _drop_quietly(collection: str) -> None:
    """Xoá một collection VẬT LÝ; lỗi chỉ log — dọn dẹp không được che lỗi chính hay làm hỏng việc đã xong."""
    try:
        await get_qdrant().delete_collection(collection)
    except Exception as exc:  # noqa: BLE001
        log.warning("qdrant: không xoá được collection %r (xoá tay): %s", collection, exc)


async def _sweep_orphans(keep: str) -> None:
    """Dọn collection vật lý `<tên phục vụ>__*` bị bỏ lại (restart giữa reindex, dọn dẹp hỏng, đổi alias
    không rõ kết quả…): mỗi bản mồ côi là nguyên một bản KB chiếm bộ nhớ Qdrant free-tier. Gọi SAU khi đổi
    alias xong (dưới khoá ghi); KHÔNG đụng `keep` hay collection nào đang có alias trỏ tới. Best-effort."""
    client = get_qdrant()
    prefix = f"{settings.qdrant_collection}__"
    try:
        names = [c.name for c in (await client.get_collections()).collections]
        served = {a.collection_name for a in (await client.get_aliases()).aliases}
    except Exception as exc:  # noqa: BLE001 — dọn dẹp không được làm hỏng lần đổi alias vừa xong.
        log.warning("qdrant: không liệt kê được collection để dọn bản mồ côi: %s", exc)
        return
    for name in names:
        if name.startswith(prefix) and name != keep and name not in served:
            await _drop_quietly(name)


async def _settle_failed_activate(alias: str, target: str, *, legacy: bool) -> bool:
    """`_activate` gặp lỗi → đọc lại trạng thái THẬT rồi mới dọn. qdrant-client gói MỌI lỗi transport (kể cả
    timeout đọc SAU khi server đã áp) thành `ResponseHandlingException`, task bị huỷ cũng tới giữa chừng →
    "lời gọi báo lỗi" KHÔNG có nghĩa "chưa gì thay đổi". Xoá `target` khi alias đã trỏ vào nó = Qdrant bỏ luôn
    alias → tên phục vụ biến mất, mọi lượt khách rơi sang người.

    True = alias ĐÃ trỏ `target`. False = chưa đổi: bỏ `target` khi chắc an toàn; bản cũ đã mất hoặc không
    đọc được trạng thái → GIỮ `target` và log (lần đổi alias thành công sau sẽ dọn qua `_sweep_orphans`).
    """
    try:
        if await _alias_target(alias) == target:
            return True
        only_copy = legacy and not await get_qdrant().collection_exists(alias)
    except Exception as exc:  # noqa: BLE001 — không biết Qdrant đang ở đâu: đừng đoán, đừng xoá gì.
        log.error(
            "qdrant: không đọc được alias %r sau khi đổi -> %r lỗi (%s) — GIỮ %r; kiểm tra rồi chạy lại reindex.",
            alias, target, exc, target,
        )
        return False
    if only_copy:  # collection thật cũ đã mất: `target` là bản DUY NHẤT còn lại — giữ, đừng xoá.
        log.error(
            "qdrant: đã xoá collection thật %r nhưng tạo alias -> %r lỗi — tên phục vụ đang trống; "
            "chạy lại reindex.",
            alias, target,
        )
    else:
        await _drop_quietly(target)
    return False


async def _activate(target: str) -> None:
    """Trỏ tên phục vụ sang collection vật lý `target` rồi bỏ collection vật lý cũ (blue/green).

    - Đã là alias → MỘT lời gọi `update_collection_aliases` (xoá + tạo): Qdrant đổi NGUYÊN TỬ, không gián đoạn.
    - Chưa có gì (cài mới) → cùng lời gọi đó (xoá alias chưa tồn tại = no-op).
    - Bản cũ: tên phục vụ là collection THẬT → Qdrant cấm alias trùng tên collection, nên phải xoá nó trước
      rồi mới tạo alias: gián đoạn ngắn (có log), CHỈ lần đầu.
    Hỏng → `_settle_failed_activate` đọc lại trạng thái: chưa đổi → bỏ `target` rồi raise (không gì thay đổi);
    ĐÃ đổi (lỗi tới sau khi Qdrant áp) → đi tiếp như thành công. Xong → dọn bản mồ côi (`_sweep_orphans`).
    """
    client = get_qdrant()
    alias = settings.qdrant_collection
    previous: str | None = None
    legacy = False
    started = 0.0
    try:
        previous = await _alias_target(alias)
        if previous is None and await client.collection_exists(alias):
            legacy = True
            started = time.perf_counter()
            await client.delete_collection(alias)
        await client.update_collection_aliases(
            change_aliases_operations=[
                DeleteAliasOperation(delete_alias=DeleteAlias(alias_name=alias)),
                CreateAliasOperation(create_alias=CreateAlias(collection_name=target, alias_name=alias)),
            ]
        )
    except BaseException as exc:
        if not await _settle_failed_activate(alias, target, legacy=legacy):
            raise
        # Đã đổi thật → giữ bản mới để sổ được ghi theo nó; task bị huỷ (CancelledError…) thì vẫn phải raise.
        log.warning("qdrant: đổi alias %r -> %r báo lỗi (%r) nhưng Qdrant ĐÃ áp — giữ bản mới.", alias, target, exc)
        if not isinstance(exc, Exception):
            raise
    if legacy:
        log.warning(
            "qdrant: chuyển collection thật %r sang alias -> %r (gián đoạn ~%d ms, chỉ lần đầu)",
            alias, target, round((time.perf_counter() - started) * 1000),
        )
    elif previous is not None and previous != target:
        await _drop_quietly(previous)
    await _sweep_orphans(keep=target)


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
        heading = _section_heading(section)
        if heading and _EXCLUDED_HEADING_RE.match(heading):
            continue
        atomic = any(h in heading for h in _ATOMIC_HEADINGS)
        if atomic or len(section) <= max_chars:
            chunks.append(section)
        else:
            chunks.extend(chunk_text(section, size=max_chars))
    return chunks


def _section_heading(section: str) -> str:
    """Heading (chữ thường) của một section; '' nếu section không mở bằng dòng `#`.

    Chỉ dòng `##...` mới là heading — mở bài (section 0) không có heading, đừng suy diễn từ câu đầu.
    """
    first = section.splitlines()[0] if section else ""
    return first.lstrip("#").strip().lower() if first.startswith("#") else ""


def drop_excluded_sections(text: str) -> str:
    """Bỏ các section KHÔNG index (`## Internal Note…`) theo CÙNG luật với `chunk_sections` (đường KB repo) —
    dùng cho upload ad-hoc (RAG-02.3). Phần còn lại giữ NGUYÊN VĂN (không đổi ranh giới đoạn/câu)."""
    bounds = [m.start() for m in _SECTION_RE.finditer(text)]
    cuts = [0, *bounds, len(text)]
    return "".join(
        text[a:b]
        for a, b in zip(cuts, cuts[1:])
        if not _EXCLUDED_HEADING_RE.match(_section_heading(text[a:b].strip()))
    )


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


async def ingest_kb_document(doc: KbDocument, *, collection: str) -> int:
    """Chunk-theo-section + query-expansion → embed → upsert vào `collection` (collection VẬT LÝ reindex đang
    dựng — chưa phục vụ khách). Trả số point. KHÔNG persist Postgres (P3)."""
    chunks = chunk_sections(doc.body)
    if not chunks:
        return 0
    # Một request embed cho cả thân lẫn câu hỏi (giữ thứ tự: chunks trước, questions sau).
    vectors = await embed_texts([f"{doc.title}\n{c}" for c in chunks] + list(doc.questions))
    points = _kb_points(doc, chunks, vectors)
    await get_qdrant().upsert(collection_name=collection, points=points, wait=True)
    return len(points)


async def ingest_knowledge_base(root: Path | None = None) -> dict:
    """Nạp lại TOÀN BỘ KB repo kiểu **blue/green** (RAG-01.1): dựng collection vật lý MỚI, nạp từng doc vào
    đó, xong hết mới đổi alias (nguyên tử) rồi bỏ bản cũ. Trả thống kê.

    Trong lúc nạp khách vẫn được phục vụ bằng bản CŨ — retrieval không bao giờ thấy collection rỗng/nạp dở.
    Nạp hỏng giữa chừng → bỏ bản dựng dở, alias GIỮ NGUYÊN, raise (sổ ở `knowledge_service` không bị đụng).
    Upload ad-hoc chỉ nằm ở bản cũ nên biến mất theo (đúng nghĩa non-canonical).

    Dùng chung cho `scripts/ingest_kb.py` và `POST /rag/reindex` (P3) — một đường nạp duy nhất.
    """
    docs = load_kb_documents(root)
    target = await _create_physical_collection()
    per_doc: list[dict] = []
    try:
        for doc in docs:
            points = await ingest_kb_document(doc, collection=target)
            per_doc.append(
                {"source": doc.source, "type": doc.type, "intent": doc.intent, "title": doc.title,
                 "questions": len(doc.questions), "points": points}
            )
            log.info("kb.ingest %s -> %d points", doc.source, points)
    except BaseException:
        await _drop_quietly(target)
        raise
    await _activate(target)
    return {
        "documents": len(docs),
        "points": sum(d["points"] for d in per_doc),
        "collection": settings.qdrant_collection,
        "physical_collection": target,
        "per_document": per_doc,
    }


async def ingest_document(
    text: str, source: str, *, version: str, type: str = "upload", title: str | None = None
) -> int:
    """Upload AD-HOC: chuẩn hoá → bỏ section nội bộ → sanitize → chunk tổng quát → embed → upsert. Payload
    cùng schema KB nhưng `intent=None` (không có frontmatter) → Agent 2 chỉ thấy nó ở lượt không-filter.
    Trả số chunk.

    Sanitize (Lớp D, slice 13): file ad-hoc KHÔNG do team viết nên là bề mặt injection GIÁN TIẾP —
    chuẩn hoá + vô hiệu câu ra lệnh TRƯỚC khi thành vector. Đường KB repo (`ingest_kb_document`)
    KHÔNG đi qua đây: tài liệu canonical là nguồn tin cậy.

    `## Internal Note` (RAG-02.3): loại y như đường KB repo — lọc SAU chuẩn hoá (heading giấu bằng ký tự vô
    hình / chữ fullwidth vẫn bị bắt) và TRƯỚC Lớp D (câu bị vô hiệu không được nuốt mất dòng heading).

    `version` (RAG-02.2): id + payload mang phiên bản của lần upload này → bản cũ còn nguyên cho tới khi
    `knowledge_service` ghi sổ xong rồi gỡ bản cũ (hoặc gỡ chính bản này nếu ghi sổ hỏng).
    """
    await ensure_collection()
    chunks = chunk_text(sanitize_untrusted_document(drop_excluded_sections(normalize_text(text))))
    if not chunks:
        return 0
    vectors = await embed_texts(chunks)
    points = [
        PointStruct(
            id=str(uuid5(NAMESPACE_URL, f"{source}@{version}#{i}")),
            vector=vec,
            payload={
                **_payload(
                    text=chunk, source=source, chunk_index=i, type=type,
                    intent=None, title=title or source, question=None,
                ),
                _UPLOAD_VERSION: version,
            },
        )
        for i, (chunk, vec) in enumerate(zip(chunks, vectors))
    ]
    await get_qdrant().upsert(collection_name=settings.qdrant_collection, points=points, wait=True)
    return len(points)


async def collection_info() -> dict:
    """Thông tin collection: points_count + danh sách distinct source (scroll toàn bộ payload.source).

    CHỈ ĐỌC: chưa có collection → trả rỗng, KHÔNG tạo (tạo là việc GHI — phải đi dưới khoá của
    `knowledge_service`). Tên phục vụ là alias → Qdrant tự resolve sang collection vật lý.
    """
    client = get_qdrant()
    if not await _serving_exists():
        return {"collection": settings.qdrant_collection, "points_count": 0, "sources": []}
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


def _match(key: str, value: str) -> FieldCondition:
    return FieldCondition(key=key, match=MatchValue(value=value))


async def _delete_where(flt: Filter) -> None:
    await ensure_collection()  # bảo đảm có payload index (`source`, `upload_version`), nếu không Qdrant trả 400
    await get_qdrant().delete(
        collection_name=settings.qdrant_collection,
        points_selector=FilterSelector(filter=flt),
        wait=True,
    )


async def delete_by_source(source: str) -> None:
    """Xoá mọi point của một tài liệu (theo `payload.source`) — dùng khi gỡ doc upload ad-hoc (P3)."""
    await _delete_where(Filter(must=[_match("source", source)]))


async def delete_upload_version(source: str, version: str) -> None:
    """Xoá ĐÚNG các point một lần upload đã ghi — bù trừ khi ghi sổ hỏng (RAG-01.3)."""
    await _delete_where(Filter(must=[_match("source", source), _match(_UPLOAD_VERSION, version)]))


async def delete_stale_versions(source: str, keep_version: str) -> None:
    """Xoá mọi point của `source` KHÔNG thuộc bản `keep_version` (kể cả point cũ chưa mang phiên bản) —
    upload lại cùng tên = THAY, không gộp (RAG-02.2)."""
    await _delete_where(
        Filter(must=[_match("source", source)], must_not=[_match(_UPLOAD_VERSION, keep_version)])
    )


async def reset_collection() -> None:
    """Thay tên phục vụ bằng một collection vật lý RỖNG (đổi alias nguyên tử) rồi bỏ bản cũ."""
    await _activate(await _create_physical_collection())


def _hit(point) -> dict:
    payload = point.payload or {}
    return {
        "text": payload.get("text"),
        "source": payload.get("source"),
        "chunk_index": payload.get("chunk_index"),
        "type": payload.get("type"),
        "title": payload.get("title"),
        "question": payload.get("question"),  # != None -> khớp qua point query-expansion
        "score": point.score,
    }


async def _query(vector: list[float], top_k: int, intent: str | None) -> list:
    flt = (
        Filter(must=[FieldCondition(key="intent", match=MatchValue(value=intent))])
        if intent
        else None
    )
    res = await get_qdrant().query_points(
        collection_name=settings.qdrant_collection,
        query=vector,
        limit=top_k,
        with_payload=True,
        query_filter=flt,
    )
    return list(res.points)


async def search(query: str, top_k: int = 4, intent: str | None = None) -> list[dict]:
    """Truy hồi top-k chunk gần nhất (cosine), ưu tiên chunk CÙNG INTENT (plan §2.5).

    Có `intent` (≠ `other`) → lượt lọc theo `payload.intent` trước. Nếu lọc **không đủ top_k** hoặc
    **hit tốt nhất vẫn dưới `retrieval_threshold`** → chạy thêm lượt KHÔNG lọc rồi gộp-khử-trùng theo
    điểm. Không hard-fail khi lọc rỗng: nhãn intent sai/thiếu không được làm mất tri thức đúng.
    Ngưỡng dùng ở đây là `retrieval_threshold` sẵn có — KHÔNG thêm ngưỡng số thứ hai (bất biến §1).

    TẦNG SERVICE để Knowledge Agent (PRD §7.2) tái dùng. Số đo embed / Qdrant của lần gọi → `take_search_timings`.
    """
    started = time.perf_counter()
    vector = await embed_text(query)
    embedded = time.perf_counter()
    narrow = intent if intent and intent != Intent.OTHER else None

    points = await _query(vector, top_k, narrow) if narrow else []
    if not narrow or len(points) < top_k or points[0].score < settings.retrieval_threshold:
        seen = {p.id for p in points}
        points += [p for p in await _query(vector, top_k, None) if p.id not in seen]
        points.sort(key=lambda p: p.score, reverse=True)

    # PERF-01.2: embed (OpenAI) tách khỏi Qdrant (một hoặc hai lượt query_points) — ghi cho task hiện tại.
    _search_timings.set(
        {"embed_ms": int((embedded - started) * 1000), "qdrant_ms": int((time.perf_counter() - embedded) * 1000)}
    )
    return [_hit(p) for p in points[:top_k]]


# Số đo của lần `search` gần nhất trong TASK hiện tại (ContextVar — các lượt khách chạy song song không lẫn số của
# nhau). `knowledge_node` đọc qua `take_search_timings` để tách embed khỏi Qdrant mà KHÔNG phải đổi chữ ký `search`
# (nhiều test thay nó bằng bản giả — khi đó không có số đo nào).
_search_timings: contextvars.ContextVar[dict[str, int] | None] = contextvars.ContextVar(
    "rag_search_timings", default=None
)


def take_search_timings() -> dict[str, int]:
    """`{"embed_ms", "qdrant_ms"}` của lần `search` gần nhất trong task này; đọc xong là xoá. Không có → `{}`."""
    timings = _search_timings.get()
    _search_timings.set(None)
    return dict(timings or {})
