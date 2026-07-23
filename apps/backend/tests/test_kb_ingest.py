"""Ingest KB có cấu trúc (P2): chunk-theo-section + query-expansion + payload. Offline, KHÔNG network."""

from __future__ import annotations

from app.services import rag_service
from app.services.rag_service import KbDocument, chunk_sections, load_kb_documents

_FLOW_DOC = """Mở bài ngắn.

## Triệu chứng
Khách báo chưa nhận hàng.

## Bot Diagnostic Flow
1. Hỏi mã đơn.
2. Hỏi ngày đặt và khu vực nhận.
3. Đối chiếu thời gian dự kiến rồi trấn an hoặc chuyển nhân viên.

## Internal Note (cho CSKH)
Nếu thất lạc thì xử lý hoàn tiền theo phương thức thanh toán ban đầu.
"""


def test_chunk_sections_splits_on_h2_and_keeps_preamble() -> None:
    chunks = chunk_sections(_FLOW_DOC)
    assert len(chunks) == 3
    assert chunks[0] == "Mở bài ngắn."
    assert chunks[1].startswith("## Triệu chứng")
    assert chunks[2].startswith("## Bot Diagnostic Flow")


def test_chunk_sections_excludes_internal_note() -> None:
    # Ghi chú nội bộ KHÔNG được index — bot không được nói quy trình/hành động nội bộ với khách.
    body = "\n".join(chunk_sections(_FLOW_DOC))
    assert "Internal Note" not in body
    assert "hoàn tiền theo phương thức thanh toán ban đầu" not in body
    # Không phân biệt hoa thường, và không cần hậu tố "(cho CSKH)".
    assert chunk_sections("## INTERNAL NOTE\nbí mật") == []
    assert chunk_sections("## internal note (cho CSKH)\nbí mật") == []


def test_real_kb_never_indexes_internal_notes() -> None:
    indexed = "\n".join(c for d in load_kb_documents() for c in chunk_sections(d.body))
    assert "Internal Note" not in indexed


def test_chunk_sections_keeps_diagnostic_flow_atomic() -> None:
    # Flow dài hơn max_chars vẫn là MỘT chunk — cắt câu giữa chừng làm mất thứ tự các bước.
    long_flow = "## Bot Diagnostic Flow\n" + "\n".join(f"{i}. Bước xử lý số {i}." for i in range(200))
    chunks = chunk_sections(long_flow, max_chars=200)
    assert len(chunks) == 1
    assert chunks[0].endswith("199.")


def test_chunk_sections_long_normal_section_falls_back_to_sentence_window() -> None:
    long_section = "## Ghi chú\n" + " ".join(f"Câu số {i} viết dài cho đủ ký tự." for i in range(80))
    chunks = chunk_sections(long_section, max_chars=300)
    assert len(chunks) > 1


def test_chunk_sections_without_h2_is_single_chunk() -> None:
    assert chunk_sections("# Giá sản phẩm\n\nGiá niêm yết trên trang sản phẩm.") == [
        "# Giá sản phẩm\n\nGiá niêm yết trên trang sản phẩm."
    ]
    assert chunk_sections("   \n  ") == []


def test_load_kb_documents_infers_type_from_folder_and_skips_root_files() -> None:
    docs = load_kb_documents()
    assert docs, "knowledge/ phải có tài liệu"
    sources = {d.source for d in docs}
    # facts.md do Agent 4 nạp riêng; README.md không phải tri thức.
    assert "facts.md" not in sources and "README.md" not in sources
    assert {d.type for d in docs} <= {"faq", "case", "reference", "promotion"}
    for d in docs:
        assert d.type == d.source.split("/")[0]
        assert d.title and d.body


def test_kb_points_stable_ids_and_payload() -> None:
    doc = KbDocument(
        source="faq/x.md", type="faq", intent="shipping", title="Vận chuyển",
        body="thân", questions=("phí ship bao nhiêu", "ship mấy ngày"),
    )
    chunks = ["## A\nnội dung A", "## B\nnội dung B"]
    vectors = [[0.0]] * (len(chunks) + len(doc.questions))
    points = rag_service._kb_points(doc, chunks, vectors)

    assert len(points) == 4  # 2 chunk thân + 2 point query-expansion
    assert [p.id for p in points] == [p.id for p in rag_service._kb_points(doc, chunks, vectors)]  # ổn định
    assert len({p.id for p in points}) == 4

    body0 = points[0].payload
    assert body0["source"] == "faq/x.md" and body0["type"] == "faq"
    assert body0["intent"] == "shipping" and body0["title"] == "Vận chuyển"
    assert body0["chunk_index"] == 0 and body0["question"] is None

    expansion = points[2].payload
    assert expansion["question"] == "phí ship bao nhiêu"
    # Point query-expansion trả THÂN đầy đủ (vector là câu hỏi, text là đáp án).
    assert expansion["text"] == "## A\nnội dung A\n\n## B\nnội dung B"
