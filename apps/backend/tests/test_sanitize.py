"""Lớp A chống prompt-injection (slice 13, P0) — chuẩn hoá + cap tin khách. Hàm thuần, offline."""

from __future__ import annotations

from app.core.config import settings
from app.core.sanitize import sanitize_customer_message


def test_cap_do_dai_cat_bot_khong_bao_loi() -> None:
    # "Tường văn bản" nhồi chỉ dẫn → CẮT BỚT (không rớt, không ném lỗi).
    assert len(sanitize_customer_message("x" * 50_000)) == settings.max_message_chars


def test_bo_ky_tu_dieu_khien_va_zero_width() -> None:
    # zero-width (U+200B) + bidi override (U+202E) + control (\x07) = chỗ giấu chỉ dẫn khỏi mắt người đọc.
    assert sanitize_customer_message("xin​chào\x07 shop‮") == "xinchào shop"


def test_nfkc_gom_bien_the_hinh_thuc() -> None:
    # Chữ/số fullwidth nhìn giống ASCII → NFKC đưa về một dạng, không né được bằng "chữ lạ".
    assert sanitize_customer_message("Đơn ６５７８") == "Đơn 6578"


def test_gop_khoang_trang_thua() -> None:
    assert sanitize_customer_message("  đơn   6578\t\tgiao chưa?  ") == "đơn 6578 giao chưa?"


def test_cau_hoi_binh_thuong_khong_doi() -> None:
    text = "Đơn hàng 6578 của tôi sắp giao tới nơi chưa?"
    assert sanitize_customer_message(text) == text
