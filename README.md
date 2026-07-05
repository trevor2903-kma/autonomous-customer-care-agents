# Autonomous Customer Support System (Shop Quần áo)

Hệ thống **Chăm sóc Khách hàng Tự trị** dùng **Multi-Agent AI** — pipeline cố định 4 agent
(`intent → knowledge → decision → response`) + `human_handoff` có điều kiện. **KHÔNG có Supervisor** (lựa chọn
có chủ đích: ưu tiên dự đoán được + kiểm toán + an toàn nội dung).

> **Nguồn chân lý nghiệp vụ: [`PRD.md`](./PRD.md).** Quy ước code: [`CLAUDE.md`](./CLAUDE.md).
> Kiến trúc tóm tắt: [`docs/architecture.md`](./docs/architecture.md).

## Trạng thái: SCAFFOLD

Đây là **khung chạy được** — node agent là **stub**, UI là **placeholder**. KHÔNG có logic nghiệp vụ thật
(không LLM, không RAG thật, không gate, không định tuyến human_handoff thật). Chỗ kiến trúc cho 4 trụ cột
(PRD §5) và xử lý bất đồng bộ/chuyển tiếp (PRD §10) đã được chừa sẵn bằng trường state + `policy.should_handoff`
+ TODO trỏ PRD.

## Kiến trúc & Stack

| Lớp | Công nghệ |
| --- | --- |
| Backend | Python 3.12 · FastAPI · LangGraph · SQLAlchemy 2 (async) · Alembic · Pydantic v2 · `uv` |
| Realtime | WebSocket (chat) + Redis pub/sub (scaffold: echo; pub/sub là TODO) |
| Hạ tầng | Neon (Postgres) · Upstash (Redis) · Qdrant Cloud — dự phòng `docker-compose.local.yml` |
| Async | FastAPI BackgroundTasks (KHÔNG worker polling) |
| Frontend | Next.js 14 · Tailwind · shadcn/ui · TanStack Query |
| Điện thoại (PWA) | Chính web (Next.js) cài lên màn hình chính (Add to Home Screen) — không codebase mobile riêng |
| Monorepo | pnpm workspaces (`apps/*`, `packages/*`) + backend Python riêng |

## Cấu trúc thư mục

```
.
├── PRD.md                      # NGUỒN CHÂN LÝ (nghiệp vụ)
├── CLAUDE.md                   # quy ước code
├── docs/architecture.md        # tóm tắt kiến trúc → trỏ PRD
├── apps/
│   ├── backend/                # FastAPI · LangGraph (uv)
│   └── dashboard/              # Next.js — Admin dashboard + cổng chat khách (PWA cài được)
└── packages/shared-types/      # type dùng chung (ConversationStatus theo PRD §15)
```

## Yêu cầu môi trường

- Node ≥ 20, pnpm ≥ 9 (`corepack enable`)
- Python 3.12 + [`uv`](https://docs.astral.sh/uv/) (uv tự quản Python 3.12)
- (tùy chọn) Docker — chỉ cho `docker-compose.local.yml`

## Bắt đầu nhanh

```bash
# 1) Điền secret (xem checklist trong .env.example)
cp .env.example .env            # rồi điền Neon / Upstash / Qdrant

# 2) Cài deps
make install                    # = uv sync (backend) + pnpm install (workspace)

# 3) Kiểm tra kết nối 3 dịch vụ managed (Phase 1)
make check-conn

# 4) Migrate DB
make migrate

# 5) Chạy (mỗi lệnh một terminal)
make dev-backend                # FastAPI :8000  (/api/health, /ws/chat)
make dev-dashboard              # Next.js :3000 (web là PWA — Add to Home Screen để cài lên điện thoại)
```

> **PWA:** dashboard là web app **cài được** — trên điện thoại/desktop dùng **Add to Home Screen / Install app**
> (service worker chỉ bật ở production; cài được cần HTTPS ở production, localhost dev thì OK). Một codebase web
> duy nhất, responsive; không codebase mobile riêng.
> Dev backend phải đang chạy để dashboard gọi `/api/health` (CORS dev cho mọi cổng localhost).

Không có tài khoản managed? Chạy local:

```bash
make local-infra-up             # Postgres + Redis + Qdrant qua docker-compose.local.yml
# rồi trỏ .env vào localhost (xem .env.example phần "LOCAL")
```

## Lệnh hữu ích

| Lệnh | Việc |
| --- | --- |
| `make health` | `curl /api/health` (api + Neon + Upstash + Qdrant) |
| `make test` | pytest backend (graph compile + chạy 2 nhánh) |
| `make migrate` / `make makemigration m="..."` | Alembic upgrade / autogenerate |
| `make build` | `pnpm -r build` |

## Tài liệu

- **`PRD.md`** — nghiệp vụ, luồng, agent, state machine (§15), mô hình dữ liệu (§20). Mọi câu hỏi "hệ thống
  nên làm gì" → tra đây.
- **`CLAUDE.md`** — quy ước code (async-first, secret trong `.env`, Response Generator là điểm phát ngôn DUY NHẤT…).
- **`plan.md`** — kịch bản scaffold (dùng xong bỏ, KHÔNG phải nguồn chân lý).
