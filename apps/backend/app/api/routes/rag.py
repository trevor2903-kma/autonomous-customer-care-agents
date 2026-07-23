"""Routes RAG — console tri thức (PRD §13, §17 Module 1).

**Đổi vai ở P3** (Reset-and-reingest, plan §1): `knowledge/` trong repo là NGUỒN CHÂN LÝ.
- `POST /reindex` — nạp lại toàn bộ KB từ repo (đường nạp CHÍNH).
- `GET /documents` — sổ tài liệu đang index (từ `knowledge_document`).
- `POST /upload` — AD-HOC, non-canonical: nạp nhanh một file lẻ, **mất khi reindex**.
- `DELETE /documents/{id}` — chỉ gỡ được doc ad-hoc; doc canonical phải xoá file trong repo rồi reindex.
- `POST /reset` — drop collection + xoá sổ.

KHÔNG OCR (PDF scan không text layer → 422). Cả router yêu cầu admin: reindex/reset xoá sạch KB.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, UploadFile

from ...core.config import settings
from ...services import knowledge_service, rag_service
from ...services.extract import extract_text
from ...schemas.knowledge import KnowledgeDocumentOut, ReindexResult
from ..deps import require_admin

router = APIRouter(prefix="/rag", tags=["rag"], dependencies=[Depends(require_admin)])

_ALLOWED_SUFFIXES = (".pdf", ".docx", ".txt", ".md")


def _out(doc) -> KnowledgeDocumentOut:
    return KnowledgeDocumentOut(
        id=str(doc.id),
        source=doc.file_ref or "",
        title=doc.title,
        doc_type=doc.doc_type,
        intent=doc.intent,
        format=doc.source_type,
        status=doc.status,
        chunks=doc.chunks,
        canonical=knowledge_service.is_canonical(doc),
        indexed_at=doc.indexed_at,
    )


@router.get("/documents", response_model=list[KnowledgeDocumentOut])
async def documents() -> list[KnowledgeDocumentOut]:
    return [_out(d) for d in await knowledge_service.list_documents()]


@router.post("/reindex", response_model=ReindexResult)
async def reindex() -> ReindexResult:
    """Reset-and-reingest từ `apps/backend/knowledge/` — cùng đường nạp với `make ingest-kb`."""
    report = await knowledge_service.reindex_from_repo()
    return ReindexResult(**{k: report[k] for k in ("documents", "points", "collection")})


@router.delete("/documents/{doc_id}", response_model=KnowledgeDocumentOut)
async def delete_document(doc_id: str) -> KnowledgeDocumentOut:
    try:
        doc = await knowledge_service.delete_upload(doc_id)
    except ValueError as exc:  # doc canonical — repo là nguồn chân lý
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if doc is None:
        raise HTTPException(status_code=404, detail="Không thấy tài liệu.")
    return _out(doc)


@router.post("/upload")
async def upload(file: UploadFile) -> dict[str, Any]:
    """Nạp AD-HOC một file lẻ (non-canonical). Không có frontmatter → `intent=None`, chunking tổng quát."""
    name = file.filename or ""
    if not name.lower().endswith(_ALLOWED_SUFFIXES):
        raise HTTPException(
            status_code=415, detail=f"Định dạng không hỗ trợ. Chỉ nhận {_ALLOWED_SUFFIXES}; nhận {name!r}"
        )
    data = await file.read()
    try:
        text = extract_text(name, data)
    except ValueError as exc:  # đuôi lạ (phòng hờ — đã lọc ở trên)
        raise HTTPException(status_code=415, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001 — file hỏng/không đọc được
        raise HTTPException(status_code=422, detail=f"Không đọc được file: {type(exc).__name__}: {exc}") from exc

    if not text.strip():
        raise HTTPException(
            status_code=422,
            detail="Không trích được văn bản (PDF scan không có text layer? — lát cắt KHÔNG OCR).",
        )

    chunks = await rag_service.ingest_document(text, source=name, title=name)
    await knowledge_service.record_upload(
        source=name, title=name, fmt=name.rsplit(".", 1)[-1].lower(),
        chunks=chunks, collection=settings.qdrant_collection,
    )
    return {"source": name, "chunks": chunks, "collection": settings.qdrant_collection, "canonical": False}


@router.get("/info")
async def info() -> dict[str, Any]:
    return await rag_service.collection_info()


@router.post("/reset")
async def reset() -> dict[str, Any]:
    """Xoá sạch: drop collection + xoá sổ tài liệu (dựng lại bằng `POST /reindex`)."""
    await knowledge_service.reset_all()
    return await rag_service.collection_info()
