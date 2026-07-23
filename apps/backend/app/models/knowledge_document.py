"""KnowledgeDocument — tài liệu tri thức cho RAG (PRD §13, §20).

Sổ tài liệu của console (P3): mỗi dòng = một tài liệu ĐÃ index, khớp 1-1 với các point cùng
`payload.source` trong Qdrant. Nguồn chân lý vẫn là `knowledge/` (repo) + Qdrant; bảng này là **sổ
hiển thị** dựng lại mỗi lần reindex.

`doc_type` phân biệt canonical (`faq|case|reference|promotion` — từ repo) với ad-hoc (`upload` — tạm
thời, mất khi reindex).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, UUIDMixin


class KnowledgeDocument(UUIDMixin, Base):
    __tablename__ = "knowledge_document"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str | None] = mapped_column(String(16), nullable=True)  # ĐỊNH DẠNG: pdf|docx|txt|md
    # Khoá ổn định của tài liệu = `payload.source` trong Qdrant (vd 'faq/gia-san-pham.md', 'policy.pdf').
    file_ref: Mapped[str | None] = mapped_column(String(512), unique=True, nullable=True)
    # Thư mục KB (faq|case|reference|promotion) hoặc 'upload' cho tài liệu ad-hoc non-canonical.
    doc_type: Mapped[str | None] = mapped_column(String(16), nullable=True)
    intent: Mapped[str | None] = mapped_column(String(64), nullable=True)  # frontmatter; None = upload
    chunks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # số point đã upsert
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
