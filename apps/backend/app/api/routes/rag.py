"""Routes RAG — nạp tri thức vào Qdrant (PRD §13, §17 Module 1). Đa định dạng: .pdf/.docx/.txt/.md.

Lát cắt này: trích văn bản → chunking tổng quát → embed → Qdrant (payload generic). KHÔNG persist tài liệu
xuống Postgres; KHÔNG OCR (PDF scan không text layer → 422). `/reset` tiện chạy lại khi test / khi đổi payload.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, UploadFile

from ...core.config import settings
from ...services import rag_service
from ...services.extract import extract_text

router = APIRouter(prefix="/rag", tags=["rag"])

_ALLOWED_SUFFIXES = (".pdf", ".docx", ".txt", ".md")


@router.post("/upload")
async def upload(file: UploadFile) -> dict[str, Any]:
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

    chunks = await rag_service.ingest_document(text, source=name)
    return {"source": name, "chunks": chunks, "collection": settings.qdrant_collection}


@router.get("/info")
async def info() -> dict[str, Any]:
    return await rag_service.collection_info()


@router.post("/reset")
async def reset() -> dict[str, Any]:
    await rag_service.reset_collection()
    return await rag_service.collection_info()
