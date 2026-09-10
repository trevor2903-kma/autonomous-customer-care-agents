"""Định dạng lịch sử hội thoại (đầu vào chỉ-đọc) cho prompt Agent 1 + Agent 4 — bộ nhớ đa lượt (PRD §12).

Lịch sử chỉ để HIỂU NGỮ CẢNH (đại từ/tham chiếu "cái áo đó", "size L nữa") — KHÔNG thay `rag_contexts`
(phanh chống bịa của Agent 4 còn nguyên: câu trả lời vẫn grounded từ tri thức, KHÔNG từ lịch sử).
"""

from __future__ import annotations

from typing import Any

from ...core.sanitize import neutralize_tags


def format_history(history: list[dict[str, Any]] | None, limit: int = 6) -> str:
    """Block "Lịch sử hội thoại gần đây" (rỗng nếu không có lịch sử). Gán nhãn Khách/Shop theo sender.

    `limit` = cửa sổ tin đưa vào prompt — production TRUYỀN `settings.history_window` (env, NFR-10) để khớp
    số tin đã nạp từ DB; default 6 chỉ là fallback/test.

    Lớp B (RAG-02.1): lời khách lượt TRƯỚC cũng KHÔNG TIN CẬY như lượt hiện tại → mỗi dòng đi qua
    `neutralize_tags` rồi `repr()` (MỘT dòng, trong ngoặc) như câu khách hiện tại: không mở/đóng được thẻ
    `<tri_thuc>`/`<tin_nhan_khach>`, không giả được cấu trúc prompt nhiều dòng (vd tiêu đề "ĐOẠN TRI THỨC:").
    """
    if not history:
        return ""
    lines: list[str] = []
    for m in history[-limit:]:
        who = "Khách" if m.get("sender") == "customer" else "Shop"
        content = str(m.get("content", "")).strip()
        if content:
            lines.append(f"{who}: {neutralize_tags(content)!r}")
    if not lines:
        return ""
    return "Lịch sử hội thoại gần đây (chỉ để hiểu ngữ cảnh, KHÔNG bịa thêm):\n" + "\n".join(lines) + "\n\n"
