"""FastAPI app — entrypoint (scaffold).

Pipeline cố định + WebSocket. Giai đoạn scaffold: chỉ health + WS echo; route hội thoại/agent
được thêm ở Phase 3/4.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import conversations, health
from .api.ws import chat
from .core.config import settings
from .core.logging import configure_logging, get_logger
from .core.qdrant_client import close_qdrant
from .core.redis_client import close_redis

configure_logging()
log = get_logger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Backend startup — ENV=%s ENABLE_LLM=%s", settings.env, settings.enable_llm)
    yield
    await close_redis()
    await close_qdrant()
    log.info("Backend shutdown — closed redis/qdrant clients")


app = FastAPI(
    title="Autonomous Customer Support — Backend (scaffold)",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(conversations.router, prefix="/api")
app.include_router(chat.router)


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "service": "autonomous-customer-support backend",
        "status": "scaffold",
        "docs": "/docs",
    }
