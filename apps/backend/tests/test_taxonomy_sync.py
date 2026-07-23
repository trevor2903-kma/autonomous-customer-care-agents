"""Tập intent phải ĐỒNG BỘ ở mọi nơi tiêu thụ nó (plan §2.1). Offline, KHÔNG network/DB.

Thiếu đồng bộ = lỗi im lặng: intent không có luật gate → `send_directly_for` trả False → duyệt nháp OAN;
intent không có trong `_PRIORITY_SEVERITY` → tụt về low/low âm thầm. Test này bắt ngay khi thêm intent mới.
Riêng seed `gate_intent_rule` nằm ở DB (migration) — ở đây canh gián tiếp qua `_INTENT_ORDER`.
"""

from __future__ import annotations

from pathlib import Path

import frontmatter

from app.agents.nodes.decision import _PRIORITY_SEVERITY
from app.agents.nodes.taxonomy import TAXONOMY
from app.models.enums import INTENT_CATEGORY, Intent
from app.services.gate_service import _INTENT_ORDER

_ALL = {i.value for i in Intent}
_KNOWLEDGE_DIR = Path(__file__).resolve().parents[1] / "knowledge"


def test_taxonomy_covers_every_intent() -> None:
    # Prompt Agent 1 phải mô tả ĐỦ tập đóng — thiếu ⇒ LLM không bao giờ chọn được intent đó.
    assert set(TAXONOMY) == _ALL


def test_category_map_covers_every_intent() -> None:
    assert {i.value for i in INTENT_CATEGORY} == _ALL


def test_priority_severity_covers_every_intent() -> None:
    assert set(_PRIORITY_SEVERITY) == _ALL


def test_gate_intent_order_covers_every_intent() -> None:
    # ⚠️ GOTCHA: intent mới PHẢI có dòng gate_intent_rule (migration) — `_INTENT_ORDER` là bản sao trong code.
    assert set(_INTENT_ORDER) == _ALL
    assert len(_INTENT_ORDER) == len(set(_INTENT_ORDER))


def test_knowledge_frontmatter_intents_are_valid() -> None:
    # Frontmatter KB là nơi thứ 4 — intent lạ ⇒ chunk không bao giờ khớp filter theo intent (P4).
    for md in sorted(_KNOWLEDGE_DIR.rglob("*.md")):
        intent = frontmatter.load(md).get("intent")
        assert intent is None or intent in _ALL, f"{md.name}: intent {intent!r} ngoài enum Intent"
