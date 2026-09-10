"""Cấu hình ứng dụng — đọc từ `.env` ở GỐC REPO qua pydantic-settings.

Quy ước (CLAUDE.md): cấu hình đọc từ env, KHÔNG hardcode secret/URL/ngưỡng.
"""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

def _find_env_files() -> tuple[str, ...]:
    """Tìm tất cả các file .env khả dĩ từ thư mục hiện tại ngược lên root."""
    files: list[str] = [".env"]
    curr = Path(__file__).resolve().parent
    for p in [curr, *curr.parents]:
        env_file = p / ".env"
        if env_file.is_file():
            files.append(str(env_file))
    return tuple(dict.fromkeys(files))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_find_env_files(),
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
    # Ngưỡng COSINE của Agent 2 (retrieval) — thang KHÁC intent_confidence (LLM tự khai), đừng gộp chung.
    # 0.40 = ĐO trên KB thật (32 câu trả-lời-được / 25 câu không) — `scripts/measure_threshold.py`,
    # phương pháp + số liệu ở `docs/retrieval-threshold.md`. Hai phân bố CHỒNG NHAU nên ngưỡng này chỉnh
    # theo RECALL (escalate oan 3%), KHÔNG cố chặn câu ngoài KB — việc đó do `out_of_domain` (Agent 1) +
    # grounding (Agent 4) lo. Đo lại mỗi khi KB đổi đáng kể.
    retrieval_threshold: float = 0.40
    # Bộ nhớ đa lượt (PRD §12, NFR-10): số tin gần nhất nạp từ DB vào prompt (Agent 1 + Agent 4).
    history_window: int = 8
    # Nhịp quét auto-resolve (09c). Hai NGƯỠNG T1/T2 nằm ở bảng `gate_config` (Admin chỉnh runtime), KHÔNG ở đây.
    sweep_interval_seconds: int = 60
    # Trần số ca một vòng sweep nạp (pre-filter theo thời gian + LIMIT) — không nạp mọi ca REPLIED mỗi vòng.
    sweep_batch_limit: int = 500
    # Giờ hỗ trợ (09c offline): ngoài khung [start, end), handoff báo khách "nhân viên sẽ phản hồi sớm".
    # AI VẪN auto-reply 24/7 (facts.md); chỉ nhánh human_handoff đổi câu.
    support_hours_start: int = 9
    support_hours_end: int = 21
    support_timezone: str = "Asia/Ho_Chi_Minh"

    # ── Báo cáo / observability (slice obs) ───────────────────────────────────
    # Ngưỡng độ trễ NFR-1 (ms): tab Báo cáo tính "% lượt ≤ ngưỡng".
    nfr_latency_ms: int = 5000
    # Lệch giờ để quy "hôm nay" (VN = UTC+7). Dùng offset thay tên vùng: zoneinfo trên Windows cần
    # thêm gói `tzdata`, không đáng cho một mốc nửa đêm.
    reports_tz_offset_hours: int = 7

    # ── Chống prompt-injection (slice 13, NFR-7 — Lớp A) ──────────────────────
    # Cap độ dài tin nhắn khách tại biên WS: tin dài bị CẮT BỚT (không rớt kết nối). Đủ rộng cho
    # câu hỏi thật, đủ hẹp để chặn "tường văn bản" nhồi chỉ dẫn vào prompt.
    max_message_chars: int = 2000

    # ── Giới hạn tần suất (audit v2, SEC-XC.2) — IN-PROCESS như hub (1 worker) ──
    # Mỗi con số = số lần tối đa trong `rate_limit_window_seconds`; 0 = tắt. Đa-worker → chuyển sang Redis.
    rate_limit_window_seconds: int = 60
    login_rate_per_ip: int = 10
    login_rate_per_email: int = 5
    register_rate_per_ip: int = 5
    # Tin nhắn khách qua /ws/chat (theo customer_id, cộng dồn mọi tab) — mỗi tin là 2 lời gọi LLM + 1 embedding.
    chat_rate_per_customer: int = 20

    # ── Auth (slice 11 — JWT + RBAC + httpOnly cookies) ──────────────────────
    # Secret ký JWT (HS256) — BẮT BUỘC, đọc env JWT_SECRET (KHÔNG hardcode secret).
    jwt_secret: str
    jwt_expire_minutes: int = 10080  # tương thích cũ — mặc định 7 ngày
    jwt_access_expire_minutes: int = 30  # access token hết hạn sau 30 phút
    jwt_refresh_expire_days: int = 7  # refresh token hết hạn sau 7 ngày
    cookie_secure: bool = False  # dev: False (HTTP), prod: True (HTTPS)
    cookie_samesite: str = "lax"  # "lax", "strict", hoặc "none"
    cookie_domain: str | None = None

    # ── Postgres (Neon) ───────────────────────────────────────────────────────
    # SSL bật qua connect_args={"ssl": ...} (CLAUDE.md). URL KHÔNG mang '?sslmode='.
    database_url: str
    database_ssl: bool = True  # local docker không TLS -> đặt DATABASE_SSL=false

    # ── Redis (Upstash) ───────────────────────────────────────────────────────
    redis_url: str

    # ── Qdrant (Vector DB / RAG) ──────────────────────────────────────────────
    qdrant_url: str
    qdrant_api_key: str | None = None
    qdrant_collection: str = "knowledge"

    # ── Langfuse (observability — phase sau) ──────────────────────────────────
    langfuse_public_key: str | None = None
    langfuse_secret_key: str | None = None
    langfuse_base_url: str | None = None

    # ── LLM (OpenAI SDK — `core/embeddings.get_openai`) ───────────────────────
    llm_api_key: str | None = None
    llm_model: str | None = None
    embedding_model: str = "text-embedding-3-small"
    # Timeout + số lần retry của client OpenAI dùng chung (audit v2, PERF-01.1). Mặc định SDK là 600s × 3 lần:
    # một lời gọi treo làm treo chat của khách tới nửa giờ. Hết giờ → node tự degrade (cờ chặn / fallback).
    llm_timeout_seconds: float = 20.0
    llm_max_retries: int = 1

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.backend_cors_origins.split(",") if o.strip()]

    @property
    def cors_origin_regex(self) -> str | None:
        # Dev: cho phép mọi nguồn (localhost, IP mạng LAN 192.168.*, 10.*, 172.*, tunnel...)
        # Prod: None -> chỉ dùng allow-list cors_origins (chặt chẽ).
        if self.env == "development":
            return r"https?://.*"
        return None


settings = Settings()  # type: ignore[call-arg]
