"""Sổ tài liệu tri thức (P3) — nối Qdrant (vector) với `knowledge_document` (metadata cho console).

`rag_service` chỉ biết Qdrant; module này là chỗ DUY NHẤT hai kho đi cùng nhau, để bảng không bao giờ
nói dối về những gì thật sự đang được index.

**Reset-and-reingest** (plan §1): reindex = drop toàn bộ collection rồi nạp lại từ repo → mọi doc upload
ad-hoc biến mất theo (đúng nghĩa "non-canonical"). Vì vậy reindex cũng xoá sạch bảng rồi ghi lại.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import delete, select

from ..core.database import AsyncSessionLocal
from ..core.logging import get_logger
from ..models.knowledge_document import KnowledgeDocument
from . import rag_service

log = get_logger("knowledge")

UPLOAD_TYPE = "upload"  # doc_type của tài liệu ad-hoc — mọi type khác là canonical (từ repo)


def is_canonical(doc: KnowledgeDocument) -> bool:
    return doc.doc_type != UPLOAD_TYPE


async def list_documents() -> list[KnowledgeDocument]:
    """Tài liệu đã index: canonical trước (theo source), upload ad-hoc sau (mới nhất trước)."""
    async with AsyncSessionLocal() as s:
        rows = list((await s.execute(select(KnowledgeDocument))).scalars().all())
    rows.sort(key=lambda d: (d.doc_type == UPLOAD_TYPE, d.file_ref or ""))
    return rows


async def reindex_from_repo(root: Path | None = None) -> dict:
    """Nạp lại toàn bộ KB repo vào Qdrant rồi DỰNG LẠI sổ tài liệu. Trả report của `rag_service`."""
    report = await rag_service.ingest_knowledge_base(root)
    now = datetime.now(UTC)
    async with AsyncSessionLocal() as s:
        # Collection vừa bị drop → mọi dòng cũ (kể cả upload) không còn vector nào ở Qdrant.
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
    log.info("knowledge.reindex %d docs -> %d points", report["documents"], report["points"])
    return report


async def record_upload(*, source: str, title: str, fmt: str, chunks: int, collection: str) -> None:
    """Ghi/cập nhật sổ cho một tài liệu upload ad-hoc (non-canonical). Upload lại cùng tên = cập nhật."""
    now = datetime.now(UTC)
    async with AsyncSessionLocal() as s:
        existing = (
            await s.execute(select(KnowledgeDocument).where(KnowledgeDocument.file_ref == source))
        ).scalar_one_or_none()
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
    async with AsyncSessionLocal() as s:
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
    """Drop collection + xoá sổ (giữ hai kho đồng bộ)."""
    await rag_service.reset_collection()
    async with AsyncSessionLocal() as s:
        await s.execute(delete(KnowledgeDocument))
        await s.commit()
