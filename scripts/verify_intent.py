"""Verify lát cắt RAG-intent — chạy classify_intent trên bộ câu test rồi in accuracy.

Câu test dùng GIỌNG KHÁC ví dụ trong seed (tránh "học vẹt"). Ngưỡng ~80% là SANITY cho lát cắt verify,
KHÔNG phải KPI PRD (§19).

Chạy (cần .env cấu hình QDRANT+LLM và collection 'knowledge' đã nạp seed qua POST /api/rag/upload):
    cd apps/backend && uv run python ../../scripts/verify_intent.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Cho `import app...` chạy khi gọi script từ gốc repo (app cài editable trong apps/backend/.venv).
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps" / "backend"))

from app.agents.nodes.intent import classify_intent  # noqa: E402
from app.core.embeddings import close_openai  # noqa: E402
from app.core.qdrant_client import close_qdrant  # noqa: E402

# (câu khách — giọng khác seed, intent kỳ vọng)
CASES: list[tuple[str, str]] = [
    ("cái quần jean này nhiêu xu vậy shop", "product_price"),
    ("đầm này vải có nóng không ạ", "product_information"),
    ("em 1m65 58kg thì lấy size nào vừa", "size_consulting"),
    ("gửi ra Hà Nội mất bao lâu shop ơi", "shipping"),
    ("kiện hàng mã AB12 giờ nằm ở đâu rồi", "order_status"),
    ("hàng lỗi muốn trả lại lấy tiền về", "refund"),
    ("cho đổi qua màu đen được hông shop", "exchange"),
    ("nhân viên trả lời trống không, thái độ quá tệ", "complaint"),
    ("đang có đợt sale nào hong shop", "promotion"),
    ("cửa hàng mình mấy giờ đóng cửa vậy", "other"),
    ("freeship cho đơn từ mấy trăm k vậy ạ", "shipping"),
    ("tư vấn giúp em chọn size áo khoác với", "size_consulting"),
]

THRESHOLD = 0.8  # sanity cho lát cắt verify (KHÔNG phải KPI PRD)


async def main() -> int:
    correct = 0
    print(f"{'EXPECTED':<20}{'PREDICTED':<20}{'RESULT':<8}CONF  FLAGS")
    print("-" * 78)
    for message, expected in CASES:
        r = await classify_intent(message)
        ok = r["intent"] == expected
        correct += int(ok)
        print(
            f"{expected:<20}{r['intent']:<20}{('OK' if ok else 'WRONG'):<8}"
            f"{r['confidence']:.2f}  {r['uncertainty_flags']}"
        )

    await close_openai()
    await close_qdrant()

    total = len(CASES)
    acc = correct / total
    print("-" * 78)
    print(f"accuracy: {correct}/{total} = {acc:.0%}  (ngưỡng sanity >= {THRESHOLD:.0%})")
    passed = acc >= THRESHOLD
    print("RESULT:", "PASS" if passed else "FAIL")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
