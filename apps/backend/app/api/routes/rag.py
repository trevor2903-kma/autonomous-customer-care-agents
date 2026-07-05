"""Routes RAG — nạp tri thức vào Qdrant (PRD §13, plan lát cắt RAG-intent).

Lát cắt này: chỉ .md/.txt → embed → Qdrant. KHÔNG persist tài liệu xuống Postgres; KHÔNG PDF/DOCX;
KHÔNG RAG management UI/re-index (để layer sau). `/reset` tiện chạy lại nhiều lần khi test.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, UploadFile

from ...core.config import settings
from ...services import rag_service

router = APIRouter(prefix="/rag", tags=["rag"])

_ALLOWED_SUFFIXES = (".md", ".txt")


@router.post("/upload")
async def upload(file: UploadFile) -> dict[str, Any]:
    name = file.filename or ""
    if not name.lower().endswith(_ALLOWED_SUFFIXES):
        raise HTTPException(status_code=400, detail=f"Chỉ nhận {_ALLOWED_SUFFIXES}; nhận: {name!r}")
    raw = await file.read()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail=f"File không phải UTF-8: {exc}") from exc
    chunks = await rag_service.ingest_document(text, source=name)
    return {"source": name, "chunks": chunks, "collection": settings.qdrant_collection}


@router.get("/info")
async def info() -> dict[str, Any]:
    return await rag_service.collection_info()


@router.post("/reset")
async def reset() -> dict[str, Any]:
    await rag_service.reset_collection()
    return await rag_service.collection_info()
