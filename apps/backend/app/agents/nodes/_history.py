"""Định dạng lịch sử hội thoại (đầu vào chỉ-đọc) cho prompt Agent 1 + Agent 4 — bộ nhớ đa lượt (PRD §12).

Lịch sử chỉ để HIỂU NGỮ CẢNH (đại từ/tham chiếu "cái áo đó", "size L nữa") — KHÔNG thay `rag_contexts`
(phanh chống bịa của Agent 4 còn nguyên: câu trả lời vẫn grounded từ tri thức, KHÔNG từ lịch sử).
"""

from __future__ import annotations

from typing import Any


def format_history(history: list[dict[str, Any]] | None, limit: int = 6) -> str:
    """Block "Lịch sử hội thoại gần đây" (rỗng nếu không có lịch sử). Gán nhãn Khách/Shop theo sender."""
    if not history:
        return ""
    lines: list[str] = []
    for m in history[-limit:]:
        who = "Khách" if m.get("sender") == "customer" else "Shop"
        content = str(m.get("content", "")).strip()
        if content:
            lines.append(f"{who}: {content}")
    if not lines:
        return ""
    return "Lịch sử hội thoại gần đây (chỉ để hiểu ngữ cảnh, KHÔNG bịa thêm):\n" + "\n".join(lines) + "\n\n"
