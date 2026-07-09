"""Trích văn bản từ file upload (PDF/Word/txt/md) — plan Phase 2.

KHÔNG OCR: PDF scan (không text layer) -> trả text rỗng/khoảng trắng; route /upload sẽ trả 422.
Import pypdf/docx cục bộ (chỉ nạp khi cần) để giữ import module nhẹ.
"""

from __future__ import annotations

from io import BytesIO


def extract_text(filename: str, data: bytes) -> str:
    """Trích text theo đuôi file. Hỗ trợ .pdf/.docx/.txt/.md; đuôi khác -> ValueError."""
    name = filename.lower()
    if name.endswith(".pdf"):
        from pypdf import PdfReader

        reader = PdfReader(BytesIO(data))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    if name.endswith(".docx"):
        from docx import Document

        doc = Document(BytesIO(data))
        return "\n".join(p.text for p in doc.paragraphs)
    if name.endswith((".txt", ".md")):
        return data.decode("utf-8", errors="ignore")
    raise ValueError(f"Định dạng không hỗ trợ: {filename!r} (chỉ .pdf/.docx/.txt/.md)")
