"""Nạp KB canonical (`apps/backend/knowledge/`) vào Qdrant — **Reset-and-reingest** (plan §1, P2).

Repo là NGUỒN CHÂN LÝ; Qdrant là bản phái sinh → mỗi lần chạy là drop collection rồi nạp lại toàn bộ.
Sửa file `.md` xong chạy lại là bot áp dụng bản mới. `facts.md` KHÔNG vào Qdrant (Agent 4 nạp riêng).

Ghi luôn sổ `knowledge_document` (Postgres) để console `/admin/knowledge` liệt kê đúng — cùng đường
nạp với `POST /rag/reindex`.

Chạy (cần .env gốc repo: QDRANT_URL/QDRANT_API_KEY + LLM_API_KEY + DATABASE_URL):
    cd apps/backend && uv run python ../../scripts/ingest_kb.py
    hoặc: make ingest-kb
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv

_REPO_ROOT = Path(__file__).resolve().parents[1]
# Nạp .env gốc repo vào os.environ (như scripts/seed_admin.py) — os.getenv KHÔNG tự đọc .env.
load_dotenv(_REPO_ROOT / ".env")

# Cho `import app...` chạy khi gọi script từ gốc repo (app cài editable trong apps/backend/.venv).
sys.path.insert(0, str(_REPO_ROOT / "apps" / "backend"))

from app.core.database import engine  # noqa: E402
from app.core.embeddings import close_openai  # noqa: E402
from app.core.qdrant_client import close_qdrant  # noqa: E402
from app.services import knowledge_service, rag_service  # noqa: E402


async def main() -> int:
    docs = rag_service.load_kb_documents()
    if not docs:
        print(f"FAIL: không thấy tài liệu nào trong {rag_service.KNOWLEDGE_DIR}")
        return 1

    print(f"KB: {rag_service.KNOWLEDGE_DIR}")
    print(f"{'SOURCE':<40}{'TYPE':<12}{'INTENT':<24}{'Q':>3}{'POINTS':>8}")
    print("-" * 87)

    try:
        report = await knowledge_service.reindex_from_repo()
    finally:
        await close_openai()
        await close_qdrant()
        await engine.dispose()

    for d in report["per_document"]:
        print(f"{d['source']:<40}{d['type']:<12}{str(d['intent']):<24}{d['questions']:>3}{d['points']:>8}")

    print("-" * 87)
    print(
        f"collection '{report['collection']}': {report['documents']} tài liệu -> {report['points']} point"
        " (đã ghi sổ knowledge_document)"
    )
    missing = [d["source"] for d in report["per_document"] if not d["intent"]]
    if missing:
        print(f"CẢNH BÁO: thiếu frontmatter `intent:` -> Agent 2 không lọc theo intent được: {missing}")
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
