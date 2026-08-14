"""Chuẩn hoá & giới hạn văn bản KHÔNG TIN CẬY — Lớp A chống prompt-injection (slice 13, NFR-7).

Văn bản không tin cậy = tin nhắn khách (biên WS) và tài liệu upload ad-hoc (`POST /rag/upload`).
Cả hai đi thẳng vào prompt LLM, nên phải qua một cửa DUY NHẤT trước khi vào pipeline:

- **NFKC**: gộp các biến thể hình thức (fullwidth, ký tự tương thích) về dạng chuẩn — chặn mẹo né
  bằng chữ "lạ mà nhìn giống".
- **Bỏ ký tự điều khiển + vô hình** (Cc/Cf: zero-width, bidi override): chỗ giấu chỉ dẫn mà người
  đọc log không thấy.
- **Gộp khoảng trắng** thừa, **cap độ dài** (`settings.max_message_chars`) — CẮT BỚT, không rớt kết nối.

Đây KHÔNG phải detector: không có cờ, không đếm, không chặn. Phòng thủ nằm ở Lớp A–D + bảo đảm cấu
trúc của pipeline (Agent 3 tất định, lookup scoped theo khách, Agent 4 grounded).
"""

from __future__ import annotations

import re
import unicodedata

from .config import settings
from .logging import get_logger

log = get_logger("sanitize")

_HSPACE_RE = re.compile(r"[ \t]+")
_BLANKLINE_RE = re.compile(r"\n{3,}")


def _strip_invisible(text: str) -> str:
    """Bỏ ký tự điều khiển (Cc) + định dạng vô hình (Cf — zero-width, bidi override).

    GIỮ `\\n`/`\\t`: chúng cũng là Cc nhưng là khoảng trắng THẬT của văn bản dán vào — xoá thẳng thì
    "6578\\tgiao chưa" dính liền thành một từ. Bước gộp khoảng trắng ngay sau đưa `\\t` về dấu cách.
    """
    return "".join(ch for ch in text if ch in "\n\t" or unicodedata.category(ch) not in ("Cc", "Cf"))


def normalize_text(text: str) -> str:
    """NFKC → bỏ ký tự vô hình → gộp khoảng trắng (giữ ranh giới đoạn). KHÔNG cap: độ dài tuỳ ngữ cảnh."""
    cleaned = _strip_invisible(unicodedata.normalize("NFKC", text))
    lines = [_HSPACE_RE.sub(" ", ln).strip() for ln in cleaned.splitlines()]
    return _BLANKLINE_RE.sub("\n\n", "\n".join(lines)).strip()


def sanitize_customer_message(text: str) -> str:
    """Tin nhắn khách tại biên WS: chuẩn hoá + cap `max_message_chars`.

    Degrade AN TOÀN (bất biến §1): lỗi ở bước phụ này KHÔNG được làm rớt lượt chat hợp lệ — cùng lắm
    tin đi tiếp ở dạng thô, chỉ bị cắt độ dài.
    """
    try:
        cleaned = normalize_text(text)
    except Exception as exc:  # noqa: BLE001 — sanitize hỏng → vẫn cho khách nhắn (chỉ cap độ dài).
        log.warning("sanitize tin khách lỗi (đi tiếp, chỉ cap độ dài): %s", exc)
        cleaned = text
    return cleaned[: settings.max_message_chars]
