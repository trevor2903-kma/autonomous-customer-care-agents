"""Trích entities bằng REGEX (neo theo từ khoá) — chạy ở MỌI nhánh của Intent Classifier (kể cả degrade).

Mục đích: `order_id` luôn bắt được kể cả khi không có LLM (fix bug entities rỗng). LLM (schema + few-shot)
trích entities giàu hơn; merge `{**rule, **llm}` (LLM đè, regex bù). Giá trị entity luôn là CHUỖI.
"""

from __future__ import annotations

import re

# order_id: neo theo từ khoá "đơn/đơn hàng/order/mã/mã đơn/#", giá trị ≥3 chữ số (lấy TRỌN dãy số). Giữa từ khoá
# và số CHỈ cho khoảng trắng + vài từ nối ("số", "là", ":", "#", "mã" sau "đơn", "của em/mình/tôi/anh/chị",
# "bên", "nè", "giúp", "order no.") và tiền tố "DH" ("mã đơn DH865277" → 865277: mã trong DB đều là số, "DH"
# chỉ là cách khách viết — AGENT-01.5) — `\D{0,8}` cũ nuốt cả "giá"/"trên"/"từ" nên "đơn giá 250000", "đơn trên
# 500000" thành mã giả (AGENT-01.2). Vì vậy "mã giảm/voucher/otp/bưu…", "đơn giá/trên/từ/dưới/tối thiểu/hơn"
# không khớp; "vận đơn" (mã vận chuyển) loại bằng lookbehind.
_ORDER_ID_RE = re.compile(
    r"(?:mã\s*đơn(?:\s*hàng)?|(?<!vận\s)đơn(?:\s*hàng)?|order|mã|#)"
    r"(?:[\s:#-]|số|là|mã|của|em|mình|tôi|anh|chị|bên|nè|giúp|no\.?|dh)*?"
    r"(\d{3,})(?!\d)",
    re.IGNORECASE,
)
# Ngữ cảnh SỐ TIỀN của một dãy số — MỘT luật dùng chung cho regex lẫn entities đã merge với LLM (AGENT-01.2):
# đứng SAU từ chỉ giá/ngưỡng, hoặc đứng TRƯỚC đơn vị tiền / nhóm nghìn. "k"/"tr"/"đ" phải DÍNH số ("500k"):
# viết tắt chat "đơn 716449 k thấy" (k = không) không được biến mã thật thành số tiền; `\b` giữ "không"/"đã"/
# "trả" khỏi dính. "đồng" TRỪ từ ghép ("đồng thời/ý/bộ/kiểm/phục/giá"): "đơn 716449 đồng thời…" vẫn là mã.
_AMOUNT_BEFORE_RE = re.compile(r"(?<!\w)(?:giá|trên|từ|dưới|tối\s*thiểu|hơn)\s*$", re.IGNORECASE)
_AMOUNT_AFTER_RE = re.compile(
    r"(?:k|tr|đ)\b|\s*(?:đồng(?!\s*(?:thời|ý|bộ|kiểm|phục|giá)\b)|vnđ|vnd|nghìn|ngàn|triệu)\b|[.,]\d{3}",
    re.IGNORECASE,
)
# Mã đơn TRƠ = CẢ tin nhắn chỉ là con số (cho phép '#' và một dấu câu cuối). `_ORDER_ID_RE` neo TỪ KHOÁ để không
# nhận nhầm giá/số lượng; số trơ chỉ là mã ở ngữ cảnh VỪA HỎI MÃ — xem `intent.resume_order_code`.
_BARE_ORDER_CODE_RE = re.compile(r"^\s*#?\s*(\d{3,})\s*[.!,]?\s*$")
# size: neo theo từ khoá "size".
_SIZE_RE = re.compile(r"\bsize\s*([SMLX]{1,3}|\d{2,3})\b", re.IGNORECASE)
# height/weight: neo theo đơn vị. Height hỗ trợ "1m60"/"1.6m"/"160cm".
_HEIGHT_RE = re.compile(r"(\d{2,3}\s*cm|\d[.,]?\d*\s*m(?:\s*\d{1,2})?)", re.IGNORECASE)
_WEIGHT_RE = re.compile(r"(\d{2,3})\s*kg\b", re.IGNORECASE)


def _is_amount_at(text: str, start: int, end: int) -> bool:
    """Dãy số `text[start:end]` có nằm trong ngữ cảnh số tiền không."""
    return bool(_AMOUNT_BEFORE_RE.search(text, 0, start) or _AMOUNT_AFTER_RE.match(text, end))


def appears_only_as_amount(text: str, code: str | None) -> bool:
    """`code` CÓ trong `text` và MỌI lần xuất hiện đều là số tiền → True (không phải mã đơn).

    Không có trong `text` → False: Agent 1 có thể giải mã đơn từ LỊCH SỬ ("đơn đó của mình"), đừng xoá nhầm.
    """
    if not code:
        return False
    spans = [m.span() for m in re.finditer(rf"(?<!\d){re.escape(code)}(?!\d)", text)]
    return bool(spans) and all(_is_amount_at(text, start, end) for start, end in spans)


def bare_order_code(text: str) -> str | None:
    """Mã nếu CẢ tin nhắn chỉ là một con số ≥3 chữ số ("716449", "#716449."), ngược lại None."""
    m = _BARE_ORDER_CODE_RE.match(text or "")
    return m.group(1) if m else None


def extract_entities_rule(text: str) -> dict[str, str]:
    """Trích entities theo regex neo từ khoá. Trả dict giá trị CHUỖI (chỉ key bắt được)."""
    entities: dict[str, str] = {}

    for m in _ORDER_ID_RE.finditer(text):
        if not _is_amount_at(text, m.start(1), m.end(1)):  # "đơn 500k" là số tiền, không phải mã
            entities["order_id"] = m.group(1)
            break

    m = _SIZE_RE.search(text)
    if m:
        entities["size"] = m.group(1).upper()

    m = _HEIGHT_RE.search(text)
    if m:
        entities["height"] = re.sub(r"\s+", "", m.group(1))

    m = _WEIGHT_RE.search(text)
    if m:
        entities["weight"] = f"{m.group(1)}kg"

    return entities
