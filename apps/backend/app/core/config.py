"""Cấu hình ứng dụng — đọc từ `.env` ở GỐC REPO qua pydantic-settings.

Quy ước (CLAUDE.md): cấu hình đọc từ env, KHÔNG hardcode secret/URL/ngưỡng.
"""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# config.py = apps/backend/app/core/config.py -> parents[4] = gốc repo
_REPO_ROOT = Path(__file__).resolve().parents[4]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_REPO_ROOT / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ───────────────────────────────────────────────────────────────────
    env: str = "development"
    log_level: str = "INFO"
    # Scaffold: KHÔNG gọi LLM trong pipeline (PRD §22 / CLAUDE.md). Giữ false.
    enable_llm: bool = False
    backend_cors_origins: str = "http://localhost:3000"

    # ── Ngưỡng cấu hình được (PRD §18 NFR-10) ─────────────────────────────────
    # TODO: tinh chỉnh thực nghiệm ở Chương 4 (ngưỡng theo từng intent — PRD §23).
    confidence_threshold: float = 0.6
    auto_resolve_minutes: int = 30
    context_window_messages: int = 10
    # Intent Classifier (PRD §7.1): 2 ứng viên RAG đầu chênh score < margin -> cờ ambiguous_intent.
    intent_ambiguous_margin: float = 0.05

    # ── Postgres (Neon) ───────────────────────────────────────────────────────
    # SSL bật qua connect_args={"ssl": ...} (CLAUDE.md). URL KHÔNG mang '?sslmode='.
    database_url: str
    database_ssl: bool = True  # local docker không TLS -> đặt DATABASE_SSL=false

    # ── Redis (Upstash) ───────────────────────────────────────────────────────
    redis_url: str
    upstash_redis_rest_url: str | None = None
    upstash_redis_rest_token: str | None = None

    # ── Qdrant (Vector DB / RAG) ──────────────────────────────────────────────
    qdrant_url: str
    qdrant_api_key: str | None = None
    qdrant_collection: str = "knowledge"

    # ── Langfuse (observability — phase sau) ──────────────────────────────────
    langfuse_public_key: str | None = None
    langfuse_secret_key: str | None = None
    langfuse_base_url: str | None = None

    # ── LLM provider (cấu hình được — CHƯA bật ở scaffold) ────────────────────
    llm_provider: str = "openai"
    llm_api_key: str | None = None
    llm_model: str | None = None
    embedding_model: str = "text-embedding-3-small"

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.backend_cors_origins.split(",") if o.strip()]

    @property
    def cors_origin_regex(self) -> str | None:
        # Dev: cho phép mọi cổng localhost/127.0.0.1 (dashboard :3000, ...).
        # Prod: None -> chỉ dùng allow-list cors_origins (chặt chẽ).
        if self.env == "development":
            return r"https?://(localhost|127\.0\.0\.1)(:\d+)?"
        return None


settings = Settings()  # type: ignore[call-arg]
