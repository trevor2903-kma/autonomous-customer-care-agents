"""Sổ tài liệu tri thức (P3) — nối Qdrant (vector) với `knowledge_document` (metadata cho console).

`rag_service` chỉ biết Qdrant; module này là chỗ DUY NHẤT hai kho đi cùng nhau, để bảng không bao giờ
nói dối về những gì thật sự đang được index.

**Reset-and-reingest** (plan §1): reindex = dựng collection mới từ repo rồi đổi alias (blue/green, xem
`rag_service`) → mọi doc upload ad-hoc biến mất theo (đúng nghĩa "non-canonical"). Vì vậy reindex cũng
xoá sạch bảng rồi ghi lại — CHỈ sau khi alias đã đổi xong.

**Khoá ghi** (audit v2, RAG-01.3): mọi thao tác GHI (reindex / upload / xoá / reset) đi TUẦN TỰ qua MỘT
`asyncio.Lock` — upload không thể rơi vào collection sắp bị thay, hay ghi sổ giữa lúc reindex dựng lại sổ.
Khoá chỉ trong MỘT process (1 worker, như hub); `make ingest-kb` là process riêng → đừng chạy song song
với thao tác trên console.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from sqlalchemy import delete, select

from ..core.config import settings
from ..core.database import AsyncSessionLocal
from ..core.logging import get_logger
from ..models.knowledge_document import KnowledgeDocument
from . import rag_service

log = get_logger("knowledge")

UPLOAD_TYPE = "upload"  # doc_type của tài liệu ad-hoc — mọi type khác là canonical (từ repo)

_write_lock = asyncio.Lock()  # tuần tự hoá mọi thao tác GHI tri thức trong process (docstring module)


def is_canonical(doc: KnowledgeDocument) -> bool:
    return doc.doc_type != UPLOAD_TYPE


async def list_documents() -> list[KnowledgeDocument]:
    """Tài liệu đã index: canonical trước (theo source), upload ad-hoc sau (mới nhất trước)."""
    async with AsyncSessionLocal() as s:
        rows = list((await s.execute(select(KnowledgeDocument))).scalars().all())
    rows.sort(key=lambda d: (d.doc_type == UPLOAD_TYPE, d.file_ref or ""))
    return rows


async def reindex_from_repo(root: Path | None = None) -> dict:
    """Nạp lại toàn bộ KB repo vào Qdrant (blue/green) rồi DỰNG LẠI sổ tài liệu. Trả report của `rag_service`.

    Nạp hỏng → `rag_service` giữ nguyên alias và sổ không bị đụng: hai kho vẫn khớp nhau (RAG-01.2). Sổ
    chỉ được ghi lại SAU khi alias đã đổi, trong MỘT transaction; bước này hỏng thì Qdrant đã sang bản mới
    mà sổ còn bản cũ → log lỗi đủ chi tiết để chạy lại reindex rồi raise (KHÔNG nuốt im lặng).
    """
    async with _write_lock:
        report = await rag_service.ingest_knowledge_base(root)
        now = datetime.now(UTC)
        try:
            async with AsyncSessionLocal() as s:
                # Alias vừa chuyển sang collection mới (chỉ có KB repo) → mọi dòng cũ (kể cả upload) không
                # còn vector nào ở Qdrant.
                await s.execute(delete(KnowledgeDocument))
                s.add_all(
                    [
                        KnowledgeDocument(
                            title=d["title"],
                            source_type="md",
                            file_ref=d["source"],
                            doc_type=d["type"],
                            intent=d["intent"],
                            chunks=d["points"],
                            status="indexed",
                            embedding_ref=report["collection"],
                            indexed_at=now,
                        )
                        for d in report["per_document"]
                    ]
                )
                await s.commit()
        except Exception:
            log.exception(
                "knowledge.reindex: Qdrant ĐÃ chuyển %r sang %r (%d tài liệu, %d point) nhưng ghi sổ "
                "knowledge_document LỖI — sổ đang lệch với Qdrant; chạy lại reindex (POST /rag/reindex "
                "hoặc make ingest-kb).",
                report["collection"], report.get("physical_collection"), report["documents"], report["points"],
            )
            raise
    log.info("knowledge.reindex %d docs -> %d points", report["documents"], report["points"])
    return report


async def upload_document(text: str, *, source: str, title: str, fmt: str) -> int:
    """Nạp AD-HOC một file (non-canonical) vào Qdrant + sổ. Trả số chunk.

    Vector TRƯỚC, sổ SAU; mỗi lần upload là một PHIÊN BẢN mới (`rag_service.ingest_document`):
    - ghi sổ hỏng (hoặc bị từ chối vì trùng doc canonical) → gỡ ĐÚNG các point của lần này rồi raise —
      không để vector mồ côi mà UI không thấy, không xoá được (RAG-01.3); bản cũ vẫn khớp dòng sổ cũ;
    - ghi sổ xong → gỡ point của bản cũ: upload lại cùng tên = THAY, không gộp (RAG-02.2).
    """
    async with _write_lock:
        version = uuid4().hex
        try:
            chunks = await rag_service.ingest_document(text, source=source, title=title, version=version)
            await record_upload(
                source=source, title=title, fmt=fmt, chunks=chunks, collection=settings.qdrant_collection
            )
        except BaseException:
            await _discard_upload_version(source, version)
            raise
        try:
            await rag_service.delete_stale_versions(source, keep_version=version)
        except Exception:
            log.exception(
                "knowledge.upload: %r bản %s đã ghi sổ nhưng gỡ point bản cũ LỖI — tài liệu đang lẫn hai "
                "bản; upload lại hoặc xoá tài liệu để dọn.",
                source, version,
            )
            raise
    return chunks


async def _discard_upload_version(source: str, version: str) -> None:
    """Bù trừ cho một upload hỏng: gỡ các point bản `version`. Lỗi ở đây KHÔNG được che lỗi gốc."""
    try:
        await rag_service.delete_upload_version(source, version)
    except Exception as exc:  # noqa: BLE001 — bù trừ hỏng: giữ lỗi gốc, nhưng phải để lại dấu vết.
        log.error(
            "knowledge.upload: không gỡ được point của %r (bản %s) — có thể còn vector mồ côi: %s",
            source, version, exc,
        )


async def record_upload(*, source: str, title: str, fmt: str, chunks: int, collection: str) -> None:
    """Ghi/cập nhật sổ cho một tài liệu upload ad-hoc (non-canonical). Upload lại cùng tên = cập nhật.

    Raise `ValueError` khi `source` trùng một dòng canonical (repo): hạ doc canonical thành 'upload' sẽ mở
    nút Xoá trên console và `delete_by_source` quét sạch point canonical (RAG-01.4).
    """
    now = datetime.now(UTC)
    async with AsyncSessionLocal() as s:
        existing = (
            await s.execute(select(KnowledgeDocument).where(KnowledgeDocument.file_ref == source))
        ).scalar_one_or_none()
        if existing is not None and is_canonical(existing):
            raise ValueError(
                f"'{source}' trùng tài liệu canonical (repo) — đổi tên file, hoặc sửa file trong knowledge/ "
                "rồi reindex."
            )
        if existing is not None:
            existing.title, existing.source_type, existing.doc_type = title, fmt, UPLOAD_TYPE
            existing.intent, existing.chunks = None, chunks
            existing.status, existing.embedding_ref, existing.indexed_at = "indexed", collection, now
        else:
            s.add(
                KnowledgeDocument(
                    title=title, source_type=fmt, file_ref=source, doc_type=UPLOAD_TYPE,
                    intent=None, chunks=chunks, status="indexed", embedding_ref=collection, indexed_at=now,
                )
            )
        await s.commit()


async def delete_upload(doc_id: str) -> KnowledgeDocument | None:
    """Gỡ một tài liệu upload ad-hoc (Qdrant + sổ). Trả None nếu không thấy.

    Raise `ValueError` với doc canonical: repo là nguồn chân lý, xoá ở console thì reindex lại mọc ra —
    muốn bỏ thì xoá file `.md` trong repo rồi reindex.
    """
    async with _write_lock, AsyncSessionLocal() as s:
        doc = await s.get(KnowledgeDocument, doc_id)
        if doc is None:
            return None
        if is_canonical(doc):
            raise ValueError(
                f"'{doc.file_ref}' là tài liệu canonical (repo) — xoá file trong knowledge/ rồi reindex."
            )
        # Vector TRƯỚC, dòng sổ SAU: Qdrant lỗi thì dòng còn nguyên (thử lại được), thay vì bỏ lại
        # vector mồ côi mà sổ không còn nhắc tới.
        if doc.file_ref:
            await rag_service.delete_by_source(doc.file_ref)
        await s.delete(doc)
        await s.commit()
    return doc


async def reset_all() -> None:
    """Drop collection + xoá sổ (giữ hai kho đồng bộ).

    Xoá sổ TRONG transaction → reset Qdrant → commit (RAG-01.2): Postgres hỏng lộ ra TRƯỚC khi đụng Qdrant; Qdrant
    hỏng → không commit (đóng session = rollback), sổ còn nguyên và vẫn khớp Qdrant chưa đổi. Kẽ còn lại: commit hỏng
    SAU khi Qdrant đã sạch → log rõ kho nào đang lệch rồi raise.
    """
    async with _write_lock, AsyncSessionLocal() as s:
        await s.execute(delete(KnowledgeDocument))
        await rag_service.reset_collection()
        try:
            await s.commit()
        except Exception:
            log.exception(
                "knowledge.reset: Qdrant ĐÃ xoá sạch nhưng commit xoá sổ knowledge_document LỖI — sổ còn liệt kê "
                "tài liệu không còn vector; bấm reset lại."
            )
            raise
