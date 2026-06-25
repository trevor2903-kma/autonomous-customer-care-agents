# Backend — Autonomous Customer Support (scaffold)

FastAPI + LangGraph. Pipeline cố định `intent → knowledge → decision → response` + `human_handoff` (PRD §7–§8).
Giai đoạn này là **scaffold**: node agent là stub, KHÔNG LLM/RAG/gate thật.

## Chạy

```bash
uv sync                 # tạo .venv (Python 3.12) + cài deps + editable `app`
uv run uvicorn app.main:app --reload --port 8000
# hoặc từ gốc repo:  make dev-backend
```

- Health: `GET /api/health` — ping thật Neon + Upstash + Qdrant.
- WebSocket echo (scaffold): `ws://localhost:8000/ws/chat`.
- Docs: `GET /docs`.

Cấu hình đọc từ `.env` **ở gốc repo** (xem `app/core/config.py`). Không hardcode secret.
