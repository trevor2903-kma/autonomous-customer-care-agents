"""Pydantic schemas — sổ tài liệu tri thức (P3, console RAG).

`canonical=False` (doc_type='upload') = tài liệu ad-hoc: sống tới lần reindex kế tiếp. FE gắn badge
theo cờ này thay vì tự đoán từ `doc_type`.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class KnowledgeDocumentOut(BaseModel):
    id: str
    source: str  # = payload.source ở Qdrant (vd 'faq/gia-san-pham.md')
    title: str
    doc_type: str | None  # faq|case|reference|promotion|upload
    intent: str | None
    format: str | None  # md|pdf|docx|txt
    status: str
    chunks: int
    canonical: bool
    indexed_at: datetime | None


class ReindexResult(BaseModel):
    documents: int
    points: int
    collection: str
