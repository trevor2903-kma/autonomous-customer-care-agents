"""Trích entities bằng REGEX (neo theo từ khoá) — chạy ở MỌI nhánh của Intent Classifier (kể cả degrade).

Mục đích: `order_id` luôn bắt được kể cả khi không có LLM (fix bug entities rỗng). LLM (schema + few-shot)
trích entities giàu hơn; merge `{**rule, **llm}` (LLM đè, regex bù). Giá trị entity luôn là CHUỖI.
"""

from __future__ import annotations

import re

# order_id: neo theo từ khoá "đơn/đơn hàng/order/mã/mã đơn/#", cho phép ≤8 ký tự KHÔNG-số ở giữa, giá trị ≥3 chữ số.
_ORDER_ID_RE = re.compile(
    r"(?:đơn(?:\s*hàng)?|order|mã(?:\s*đơn)?|#)\D{0,8}(\d{3,})", re.IGNORECASE
)
# size: neo theo từ khoá "size".
_SIZE_RE = re.compile(r"\bsize\s*([SMLX]{1,3}|\d{2,3})\b", re.IGNORECASE)
# height/weight: neo theo đơn vị. Height hỗ trợ "1m60"/"1.6m"/"160cm".
_HEIGHT_RE = re.compile(r"(\d{2,3}\s*cm|\d[.,]?\d*\s*m(?:\s*\d{1,2})?)", re.IGNORECASE)
_WEIGHT_RE = re.compile(r"(\d{2,3})\s*kg\b", re.IGNORECASE)


def extract_entities_rule(text: str) -> dict[str, str]:
    """Trích entities theo regex neo từ khoá. Trả dict giá trị CHUỖI (chỉ key bắt được)."""
    entities: dict[str, str] = {}

    m = _ORDER_ID_RE.search(text)
    if m:
        entities["order_id"] = m.group(1)

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
