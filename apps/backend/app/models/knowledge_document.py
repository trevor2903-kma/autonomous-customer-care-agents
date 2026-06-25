"""KnowledgeDocument — tài liệu tri thức cho RAG (PRD §13, §20).

Scaffold: chỉ lưu metadata tài liệu; chunk/embedding/index thật là phase sau (PRD §22).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, UUIDMixin


class KnowledgeDocument(UUIDMixin, Base):
    __tablename__ = "knowledge_document"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str | None] = mapped_column(String(16), nullable=True)  # pdf|docx|txt|md
    file_ref: Mapped[str | None] = mapped_column(String(512), nullable=True)
    # 'metadata' là thuộc tính dành riêng của DeclarativeBase -> đặt attr 'doc_metadata', cột DB 'metadata'.
    doc_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONB, default=dict, nullable=False
    )
    status: Mapped[str] = mapped_column(String(16), default="pending", nullable=False)  # indexed|pending
    embedding_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)  # Qdrant ref
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    indexed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
