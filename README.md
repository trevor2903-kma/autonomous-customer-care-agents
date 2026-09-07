# Autonomous Customer Support System — Multi-Agent AI

Hệ thống **Chăm sóc Khách hàng Tự trị (CSKH)** cho một shop thời trang online, xây trên **pipeline cố định 4 agent**
(`intent → knowledge → decision → response`) + `human_handoff` có điều kiện. **KHÔNG có Supervisor** — một lựa chọn
có chủ đích: ưu tiên **dự đoán được · kiểm toán được · an toàn nội dung** hơn là tính linh hoạt của điều phối động.

Đồ án tốt nghiệp — Học viện Kỹ thuật Mật mã.

> Nguồn chân lý nghiệp vụ: [`PRD.md`](./PRD.md) · Quy ước code: [`CLAUDE.md`](./CLAUDE.md) · Kiến trúc: [`docs/architecture.md`](./docs/architecture.md)

---

## 1. Tổng quan

Khách hàng chat với trợ lý AI; mỗi tin đi qua **pipeline 4 agent tất định**. Hệ tự trả lời khi đủ tự tin và
có căn cứ, và **chuyển tiếp cho nhân viên** một cách *tất định* (theo cờ, không phải theo "cảm tính" của LLM) khi
gặp giới hạn. Admin theo dõi, tiếp quản, duyệt nháp và giám sát qua một dashboard riêng.

**4 trụ cột thiết kế**
1. **Luồng cố định, kiểm toán được** — 4 agent chạy theo thứ tự bất biến; mọi bước ghi vào `audit_log`.
2. **Tự trị có giới hạn** — hệ tự xử phần lớn, nhưng hành động nhạy cảm (hoàn tiền/đổi/khiếu nại) qua cổng duyệt.
3. **An toàn qua grounding** — Agent 4 chỉ nói từ tri thức được cấp (facts + RAG + dữ liệu đơn); không bịa *có*,
   không suy diễn *không có* từ chỗ tài liệu im lặng; không hứa hành động hệ không làm được.
4. **Cải thiện bán tự động** — tri thức là canonical trong repo, nạp lại theo cơ chế reset-and-reingest.

## 2. Tính năng chính

- **Pipeline 4 agent**
  - *Agent 1 — Intent Classifier*: phân loại **15 nhóm ý định** + trích xuất thực thể (mã đơn, size…).
  - *Agent 2 — Knowledge/RAG*: truy hồi **theo intent** trên kho tri thức có cấu trúc + **tra cứu đơn hàng** (scoped theo khách).
  - *Agent 3 — Decision Engine*: **tất định** — định tuyến theo tập cờ chặn (`BLOCKING_FLAGS`), gán ưu tiên/mức độ; **không** dùng LLM, **không** trộn điểm tin cậy.
  - *Agent 4 — Response Generator*: sinh phản hồi **có căn cứ** (facts luôn-bật + RAG + đơn), là **egress duy nhất** của luồng tự động.
- **RAG có cấu trúc**: KB `.md` trong repo (frontmatter, chunk theo section, query-expansion), nạp vào Qdrant qua `ingest_kb`; ngưỡng truy hồi **được đo** bằng script (không phải nút UI).
- **Human-in-the-loop**: hàng đợi chuyển tiếp · tiếp quản (takeover) · duyệt nháp phản hồi · cấu hình gate động theo từng intent.
- **Tra cứu đơn hàng**: lookup **giới hạn theo khách đã đăng nhập** (không lộ đơn của người khác); đơn không thấy → báo "kiểm tra lại mã", không escalate ngay.
- **Xác thực & phân quyền**: JWT + RBAC (admin / khách), JWT-over-WebSocket cho chat.
- **Realtime**: WebSocket + pub/sub **in-process** (1 worker) — cập nhật tin & trạng thái tức thì cho cả khách lẫn admin.
- **Quan sát (Observability)**: `audit_log` per-agent (kèm thời gian từng bước) + Langfuse (trace LLM) + tab **Báo cáo** (KPI: tỉ lệ tự trả lời, lý do escalate, độ trễ p50/p95, đối chiếu NFR-1 ≤ 5s).
- **Bảo mật (chống prompt-injection)**: chuẩn hoá + giới hạn đầu vào; delimit tin khách/RAG là *dữ liệu*; luật chống lộ prompt / đổi vai; sanitize tài liệu upload.
- **Tự đóng hội thoại**: khi khách bất hoạt → **nhắc nhẹ (canned)** → nếu vẫn im → tự đóng, qua một vòng lặp nền.
- **Giao diện**: dashboard admin (Next.js) + màn chat khách dạng **PWA** (cài được lên màn hình chính).

## 3. Kiến trúc

```
                       ┌───────────────────────────── pipeline (LangGraph) ─────────────────────────────┐
  Khách ──WS──▶  Agent 1        ▶   Agent 2         ▶   Agent 3            ▶   Agent 4
                Intent            Knowledge/RAG         Decision (tất định)     Response (grounded)
                (ý định+          (+ tra cứu đơn)       cờ chặn? → định tuyến    = egress DUY NHẤT
                 thực thể)                                                       │
                                                                                ├─▶ auto_reply ──▶ Khách
                                                                                └─▶ human_handoff ─▶ Hàng đợi ─▶ Admin
       audit_log ◀── mỗi agent ghi (intent/cờ/điểm/hành động/độ trễ) ──────────────────────────────────┘
```

- **Định tuyến = cờ, không phải chữ.** Escalation do Agent 3 quyết theo `BLOCKING_FLAGS`; Agent 4 không tự chuyển được.
- **Grounding hai chiều** ở Agent 4 + **phanh cứng** (không có tri thức → phản hồi dự phòng, không gọi LLM).
- Chi tiết: [`docs/architecture.md`](./docs/architecture.md), [`docs/rag-refactor-results.md`](./docs/rag-refactor-results.md), [`docs/retrieval-threshold.md`](./docs/retrieval-threshold.md).

## 4. Công nghệ

| Lớp | Công nghệ |
| --- | --- |
| Backend | Python 3.12 · FastAPI · **LangGraph** · SQLAlchemy 2 (async) · Alembic · Pydantic v2 + pydantic-settings · `uv` |
| LLM / Embedding | OpenAI (`gpt-4o-mini` + `text-embedding-3-small`) |
| Realtime | WebSocket + **pub/sub in-process** (1 worker) |
| Vector store | **Qdrant Cloud** (cosine) |
| CSDL | **Neon** (Postgres, async) |
| Cache | **Upstash** (Redis) |
| Observability | **Langfuse** (trace LLM, degrade-safe) + `audit_log` (Postgres) |
| Frontend | Next.js 14 · React 18 · **Tailwind CSS (thuần)** · TanStack Query · TypeScript · PWA |
| Monorepo | pnpm workspaces (`apps/*`, `packages/*`) + backend Python riêng |

## 5. Cấu trúc thư mục

```
.
├── apps/
│   ├── backend/            # FastAPI + LangGraph + Alembic
│   │   ├── app/
│   │   │   ├── agents/     # pipeline + nodes (intent/knowledge/decision/response)
│   │   │   ├── api/        # routes/ (REST) + ws/ (WebSocket chat & admin)
│   │   │   ├── core/       # config, database, security, tracing…
│   │   │   ├── models/     # SQLAlchemy: user, conversation, message, order, gate_config, audit_log…
│   │   │   ├── schemas/    # Pydantic
│   │   │   ├── services/   # conversation, gate, order, escalation, report…
│   │   │   ├── tasks/      # tác vụ nền (vòng lặp tự đóng hội thoại)
│   │   │   └── tools/
│   │   ├── knowledge/      # KB canonical: faq/ · case/ · reference/ · facts.md
│   │   └── alembic/        # migrations
│   └── dashboard/          # Next.js (dashboard admin + chat khách PWA)
├── packages/shared-types/  # type dùng chung
├── scripts/                # seed / ingest / đo ngưỡng / kiểm tra kết nối (chạy độc lập)
├── docs/                   # architecture, kết quả RAG, ngưỡng truy hồi, design
├── PRD.md · CLAUDE.md · Makefile · README.md
```

> `.env` đặt ở **gốc repo** (config đọc qua pydantic-settings). Scripts cũng ở **gốc `scripts/`**.

## 6. Bắt đầu

### Yêu cầu
- Python **3.12**, [`uv`](https://docs.astral.sh/uv/), Node.js + **pnpm**
- Tài khoản: Neon (Postgres) · Upstash (Redis) · Qdrant Cloud · OpenAI API key

### Các bước
```bash
# 1) Clone
git clone https://github.com/trevor2903-kma/autonomous-customer-care-agents.git
cd autonomous-customer-care-agents

# 2) Tạo .env ở GỐC repo (điền URL/khoá của bạn — xem §7)
cp apps/backend/.env.example .env    # rồi mở .env điền giá trị

# 3) Cài phụ thuộc
make install                          # backend (uv) + dashboard (pnpm)

# 4) Migrate DB
make migrate                          # alembic upgrade head

# 5) Tạo tài khoản admin
cd apps/backend && uv run python ../../scripts/seed_admin.py && cd ../..

# 6) Nạp kho tri thức vào Qdrant
make ingest-kb

# (tuỳ chọn) kiểm tra kết nối & tạo đơn hàng mẫu để test
make check-conn
cd apps/backend && uv run python ../../scripts/seed_orders.py && cd ../..

# 7) Chạy (2 terminal)
make dev-backend                      # http://localhost:8000
make dev-dashboard                    # http://localhost:3000
```

## 7. Biến môi trường (`.env` ở gốc repo)

| Nhóm | Biến |
| --- | --- |
| LLM | `LLM_API_KEY`, `ENABLE_LLM` |
| Postgres (Neon) | `DATABASE_URL`, `DATABASE_SSL` |
| Qdrant | `QDRANT_URL`, `QDRANT_API_KEY`, `QDRANT_COLLECTION` |
| Redis (Upstash) | `REDIS_URL` (hoặc `UPSTASH_REDIS_REST_URL` + `UPSTASH_REDIS_REST_TOKEN`) |
| Xác thực | `JWT_SECRET`, `JWT_EXPIRE_MINUTES` |
| Langfuse (tuỳ chọn) | `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST` |
| Tinh chỉnh (có mặc định) | `RETRIEVAL_THRESHOLD` (0.40) · `AUTO_RESOLVE_MINUTES` · `SWEEP_INTERVAL_SECONDS` · `MAX_MESSAGE_CHARS` · `NFR_LATENCY_MS` · `HISTORY_WINDOW` … |

Danh sách đầy đủ + mô tả xem `apps/backend/.env.example` và `app/core/config.py`.

## 8. Lệnh Make

| Lệnh | Việc |
| --- | --- |
| `make install` | Cài backend (uv) + dashboard (pnpm) |
| `make dev-backend` | Chạy FastAPI (uvicorn) |
| `make dev-dashboard` | Chạy Next.js dashboard |
| `make migrate` | `alembic upgrade head` |
| `make makemigration` | Tạo migration mới |
| `make ingest-kb` | Reset + nạp lại kho tri thức vào Qdrant |
| `make check-conn` | Kiểm tra kết nối Postgres/Redis/Qdrant/OpenAI |
| `make health` | Health check backend |
| `make test` | Chạy test (offline) |
| `make build` | Build production dashboard |
| `make local-infra-up/down` | Hạ tầng local qua docker-compose (tuỳ chọn) |

## 9. Scripts (`scripts/`, chạy từ `apps/backend`)

| Script | Việc |
| --- | --- |
| `seed_admin.py` | Tạo tài khoản admin |
| `seed_orders.py` | Tạo đơn hàng mẫu đa dạng (đủ mọi trạng thái) cho các khách trong DB |
| `ingest_kb.py` | Nạp KB `.md` → Qdrant (reset-and-reingest) |
| `measure_threshold.py` | Đo ngưỡng truy hồi trên tập đánh giá → gợi ý `RETRIEVAL_THRESHOLD` |
| `verify_intent.py` | Kiểm tra phân loại intent (live) |
| `check_connections.py` | Kiểm tra kết nối hạ tầng |
| `gen_favicon.py` | Sinh favicon/PWA icon từ nhãn thương hiệu |

Mẫu chạy: `cd apps/backend && uv run python ../../scripts/<tên>.py`

## 10. Kiểm thử

```bash
make test        # bộ test backend, chạy offline (không cần key)
```

## 11. Tài liệu

- [`PRD.md`](./PRD.md) — yêu cầu nghiệp vụ (nguồn chân lý)
- [`CLAUDE.md`](./CLAUDE.md) — quy ước code
- [`docs/architecture.md`](./docs/architecture.md) — kiến trúc hệ thống
- [`docs/rag-refactor-results.md`](./docs/rag-refactor-results.md) — kết quả tinh chỉnh RAG
- [`docs/retrieval-threshold.md`](./docs/retrieval-threshold.md) — phương pháp & kết quả đo ngưỡng truy hồi
