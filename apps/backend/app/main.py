"""FastAPI app — entrypoint (scaffold).

Pipeline cố định + WebSocket. Giai đoạn scaffold: chỉ health + WS echo; route hội thoại/agent
được thêm ở Phase 3/4.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .agents.nodes.response import load_facts
from .api.routes import admin, agents, auth, conversations, health, me, rag, reports
from .api.ws import admin as admin_ws
from .api.ws import chat
from .core import tracing
from .core.config import settings
from .core.embeddings import close_openai
from .core.logging import configure_logging, get_logger
from .core.qdrant_client import close_qdrant
from .core.redis_client import close_redis

configure_logging()
log = get_logger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Backend startup — ENV=%s ENABLE_LLM=%s", settings.env, settings.enable_llm)
    # Nạp facts.md 1 lần lúc khởi động (plan §2.6) — sau đó Agent 4 dùng bản cache, không đọc đĩa mỗi lượt.
    log.info("Facts cửa hàng: %d ký tự (knowledge/facts.md)", len(load_facts()))
    log.info("Langfuse (observability cấp LLM): %s", "BẬT" if tracing.enabled() else "tắt (thiếu key)")
    yield
    tracing.flush()  # đẩy nốt sự kiện còn trong hàng đợi; no-op nếu tracing tắt
    await close_redis()
    await close_qdrant()
    await close_openai()
    log.info("Backend shutdown — closed redis/qdrant/openai clients")


app = FastAPI(
    title="Autonomous Customer Support — Backend (scaffold)",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=settings.cors_origin_regex,  # dev: mọi cổng localhost (dashboard, ...)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(me.router, prefix="/api")
app.include_router(conversations.router, prefix="/api")
app.include_router(agents.router, prefix="/api")
app.include_router(rag.router, prefix="/api")
# reports TRƯỚC admin: cả hai cùng gốc /api/admin — router cụ thể hơn (/admin/reports/*) phải đăng ký
# trước để không bị route động của admin nuốt mất.
app.include_router(reports.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(chat.router)
app.include_router(admin_ws.router)


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "service": "autonomous-customer-support backend",
        "status": "scaffold",
        "docs": "/docs",
    }
