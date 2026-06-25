# PLAN — Scaffold Monorepo: HỆ THỐNG CHĂM SÓC KHÁCH HÀNG TỰ TRỊ (Shop Quần áo)

> Nguồn chân lý của hệ thống là **`PRD.md`**.
>
> **Phạm vi:** CHỈ dựng nền móng — monorepo, môi trường, skeleton **chạy được**. Node agent là **stub**,
> UI là **placeholder**. KHÔNG triển khai logic nghiệp vụ thật. Mục tiêu: khung sạch để cắm logic theo PRD.
>
> **Kiến trúc (theo PRD §5–§8):** pipeline cố định `intent → knowledge → decision → response` + human_handoff
> có điều kiện, KHÔNG có Supervisor. Hạ tầng managed-first (Neon · Upstash · Qdrant); giữ docker-compose.local.yml dự phòng.

---

## 1. Pipeline & thứ tự (khớp PRD §7–§8)

`intent → knowledge → decision → [gate] → response`, cộng `human_handoff` có điều kiện. Ở scaffold, 5 node
là **stub**: `intent`, `knowledge`, `decision`, `response`, `human_handoff`. Node ra quyết định là `decision`
(sau nó là định tuyến auto_reply/human_handoff). Chi tiết nghiệp vụ: xem PRD, KHÔNG lặp lại ở đây.

---

## 2. In / Out scope (scaffold)

**In scope:**

- Monorepo pnpm workspaces + backend Python.
- Kết nối Neon · Upstash Redis · Qdrant Cloud; `/api/health` ping thật cả 3.
- Skeleton FastAPI: REST + **WebSocket echo** (chứng minh transport realtime; chưa wiring AI).
- Skeleton LangGraph: `ConversationState` (chừa sẵn confidence/uncertainty/escalation + trường CSKH:
  intent/entities/rag_contexts/action/draft_reply/awaiting_customer), 5 node stub, `policy.py` route theo
  confidence/cờ, endpoint demo chạy **cả 2 nhánh** (`response` / `human_handoff`).
- Async skeleton bằng FastAPI BackgroundTasks.
- Dashboard Next.js (trạng thái service + agent-trace placeholder + conversation-list placeholder) + cổng chat
  khách placeholder (Header/ChatWindow/Input nối WebSocket echo) + Mobile Expo (trạng thái backend).
- `shared-types`; migration Alembic tạo bảng tối thiểu (conversation, message, knowledge_document, audit_log)
  — đủ rộng theo PRD §20.
- `.env.example`, `.gitignore`, `README.md`, `Makefile`, `docker-compose.local.yml`.
- Sao chép `PRD.md` và `CLAUDE.md` vào repo (đặt ở gốc).

**Out of scope (chỉ CHỪA CHỖ — theo PRD §22):** logic phân loại intent / RAG (embed+truy hồi) / decision /
gate / human_handoff định tuyến / vòng học thật; LLM trong pipeline (`ENABLE_LLM=false`); wiring AI vào
WebSocket; Redis pub/sub thật; tích hợp đơn hàng/push; auth đầy đủ.

---

## 3. Tech Stack & Phiên bản

| Thành phần            | Lựa chọn                                           | Phiên bản / Ghi chú                      |
| --------------------- | -------------------------------------------------- | ---------------------------------------- |
| Monorepo (JS)         | pnpm workspaces                                    | pnpm 9.x                                 |
| Node.js               | LTS                                                | 20.x / 22.x                              |
| Python                | CPython                                            | 3.12.x                                   |
| Python pkg manager    | uv (fallback venv+pip)                             | latest                                   |
| Backend               | FastAPI + uvicorn[standard]                        | 0.115.x / 0.30.x                         |
| Realtime              | WebSocket (FastAPI) + Redis pub/sub                | pub/sub là TODO (scaffold: echo)         |
| Agent orchestration   | LangGraph                                          | 0.2.x                                    |
| LLM SDK               | (cấu hình được: OpenAI/Anthropic/Gemini)           | chưa bật                                 |
| ORM / Migration       | SQLAlchemy 2.0.x / Alembic 1.13.x                  | async                                    |
| DB driver             | asyncpg                                            | 0.29.x (Neon cần SSL)                    |
| Validation            | Pydantic 2.9.x / pydantic-settings 2.5.x           |                                          |
| PostgreSQL            | Neon (managed)                                     | free: 0.5GB, 100 CU-hrs/tháng            |
| Redis                 | Upstash (managed)                                  | free: 500K lệnh/tháng; session + pub/sub |
| Vector DB             | Qdrant Cloud (managed)                             | free: 1GB; embedding tri thức (RAG)      |
| Async jobs (scaffold) | FastAPI BackgroundTasks                            | không broker                             |
| Frontend              | Next.js 14 · Tailwind · shadcn/ui · TanStack Query |                                          |
| Mobile                | React Native / Expo                                | SDK 51+                                  |
| Container (dự phòng)  | Docker + Compose v2                                | chỉ cho docker-compose.local.yml         |

---

## 4. Prerequisites

```bash
node --version              # >= 20
corepack enable && corepack prepare pnpm@latest --activate
python3 --version           # 3.12.x
# uv:  curl -LsSf https://astral.sh/uv/install.sh | sh
uv --version
# (tùy chọn) docker --version
```

---

## 5. TRƯỚC KHI BẮT ĐẦU — tài khoản managed (việc của con người)

Claude Code tạo `.env.example` + checklist rồi **DỪNG chờ** `.env` được điền.

| Dịch vụ                  | Đăng ký                    | Cần lấy               |
| ------------------------ | -------------------------- | --------------------- |
| Neon                     | https://neon.tech          | Connection string     |
| Upstash Redis            | https://upstash.com        | `rediss://` URL (TLS) |
| Qdrant Cloud             | https://cloud.qdrant.io    | Cluster URL + API key |
| Langfuse (optional, sau) | https://cloud.langfuse.com | Public + Secret key   |

---

## 6. Cấu trúc Monorepo

```
autonomous-customer-support-system/
├── PRD.md                        # NGUỒN CHÂN LÝ (giữ ở gốc)
├── CLAUDE.md                     # quy ước code (Claude Code tự đọc)
├── plan.md                       # file này — bỏ sau scaffold
├── README.md, Makefile, .gitignore, .env.example
├── docker-compose.local.yml      # dự phòng
├── package.json, pnpm-workspace.yaml
├── apps/
│   ├── backend/                  # FastAPI · LangGraph
│   │   ├── pyproject.toml, Dockerfile, .env.example, alembic.ini, alembic/
│   │   └── app/
│   │       ├── main.py
│   │       ├── core/{config.py, database.py, redis_client.py, qdrant_client.py, logging.py}
│   │       ├── api/{deps.py, routes/{health.py, conversations.py, agents.py}, ws/{chat.py}}
│   │       ├── agents/{state.py, graph.py, policy.py, nodes/{intent,knowledge,decision,response,human_handoff}.py}
│   │       ├── models/{base.py, conversation.py, message.py, knowledge_document.py, audit_log.py}
│   │       ├── schemas/{conversation.py, message.py, agent.py}
│   │       ├── services/{conversation_service.py, audit_service.py}
│   │       ├── tools/            # placeholder (PRD §7 — phase sau: RAG retriever, order lookup)
│   │       └── tasks/{background.py}
│   ├── dashboard/                # Next.js 14 — dashboard Admin + cổng chat khách (placeholder)
│   └── mobile/                   # Expo — Admin xử lý nhanh (placeholder)
├── packages/shared-types/
└── docs/architecture.md          # tóm tắt kiến trúc + trỏ PRD
```

---

## 7. Kế hoạch theo Phase

> Sau MỖI phase: chạy "Verify", hiển thị output, `git commit` (`feat(scaffold): phase N - ...`), tiếp tục nếu không lỗi.

**Phase 0 — Khởi tạo.** `git init`, `.gitignore`, prerequisites, README, pnpm-workspace, root package.json,
Makefile (`dev-backend`, `dev-dashboard`, `dev-mobile`, `migrate`, `health`, `test`, `local-infra-up/down`).
Đặt sẵn `PRD.md` + `CLAUDE.md` ở gốc.
**Verify:** `pnpm -v`, `python3 --version`, `uv --version` OK; git sạch.

**Phase 1 — Kết nối managed.** Tạo `.env.example` + checklist §5. **DỪNG** chờ `.env`. Tạo docker-compose.local.yml dự phòng.
**Verify:** script kiểm tra kết nối 3 dịch vụ.

**Phase 2 — Backend + Health + WebSocket khung.** `uv init`; `config.py` (gồm `CONFIDENCE_THRESHOLD=0.6`,
`AUTO_RESOLVE_MINUTES=30`, `CONTEXT_WINDOW_MESSAGES=10` — đọc env, ghi chú "tinh chỉnh ở Chương 4");
`database.py` (Neon SSL qua `connect_args={"ssl": True}`, KHÔNG `sslmode=`); redis/qdrant client; `main.py`;
`health.py` ping thật; `ws/chat.py` **WebSocket echo** (accept + echo, chưa wiring pipeline).
**Verify:** `/api/health` trả `ok` cho api + 3 dịch vụ; kết nối WebSocket echo được.

**Phase 3 — Models + Migration.** `conversation` (id, customer_identifier, status, current_intent, entities
JSONB, confidence, uncertainty_flags JSONB, escalation_reason, assigned_admin_id, created_at, updated_at,
last_message_at); `message` (id, conversation_id, sender, content, intent, confidence, created_at);
`knowledge_document` (id, title, source_type, file_ref, metadata JSONB, status, embedding_ref, created_at,
indexed_at); `audit_log` (id, conversation_id, message_id, node, action, confidence, uncertainty_flags JSONB,
escalation_reason, detail JSONB, created_at). Alembic async + migration đầu. Service + `conversations.py`
(POST tạo hội thoại + gửi message / GET).
**Verify:** `make migrate`; POST/GET conversation; 4 bảng tồn tại.

**Phase 4 — Skeleton LangGraph.** `state.py` `ConversationState`: `conversation_id, input, scratchpad,
messages(append-only), status, result, error` + **chừa sẵn** `confidence, uncertainty_flags, escalation_reason,
require_human_handoff` + **trường CSKH** `intent, entities, rag_contexts, action, draft_reply,
awaiting_customer`. 5 node stub set giá trị stub (`confidence=1.0`, `uncertainty_flags=[]`, `action="auto_reply"`);
`decision` là node quyết định; `human_handoff` set `require_human_handoff=True` + `escalation_reason`.
`policy.py` `should_handoff(state)`. `graph.py`: `intent → knowledge → decision → [should_handoff] →
(response | human_handoff)`; trong scaffold giữ tuyến tính đơn giản, conditional sau decision route
`response`(đại diện nhánh tự động) vs `human_handoff`. Checkpointer `MemorySaver` (TODO: Redis/Postgres cho
suspend/resume — PRD §10). `agents.py` `run-demo` có cờ ép nhánh → chạy **cả 2 nhánh**. TODO rõ:
`# TODO (PRD §9/§10): gate, human_handoff định tuyến, suspend/resume, wiring WebSocket↔graph`.
**Verify:** `make test` (graph compile + 2 nhánh); `run-demo` trả trace đúng nhánh + confidence.

**Phase 5 — Async (BackgroundTasks).** `tasks/background.py` `process_message(conversation_id, message_id)` →
log + audit + (tùy chọn) graph. TODO: Redis pub/sub phát realtime + suspend/resume (PRD §10).
**Verify:** POST message → task nền ghi audit_log.

**Phase 6 — Frontend & Mobile & shared-types.** `shared-types`: `Conversation, Message, AgentTraceStep(node,
confidence, branch), HealthStatus, ConversationStatus(enum theo PRD §15)`. Dashboard `/`: ServiceStatus +
AgentTracePanel (Run demo + toggle ép handoff) + ConversationList placeholder. Cổng chat khách: Header +
ChatWindow + Input nối WebSocket echo (hiển thị "connected" + echo). Mobile StatusScreen. `docs/architecture.md`
(tóm tắt + trỏ PRD).
**Verify:** dashboard localhost:3000 (3 service xanh + Run demo 2 nhánh); chat khách echo được; Expo OK;
`pnpm -r build` pass.

---

## 8. Definition of Done

- [ ] `.env` có managed HOẶC trỏ local.
- [ ] `/api/health` trả `ok` (api + 3 dịch vụ); WebSocket echo kết nối được.
- [ ] `make migrate`; bảng conversation/message/knowledge_document/audit_log tồn tại (đủ cột theo PRD §20).
- [ ] `ConversationState` chừa sẵn confidence/uncertainty_flags/escalation_reason/require_human_handoff +
      trường CSKH (intent/entities/rag_contexts/action/draft_reply/awaiting_customer).
- [ ] `run-demo` chạy **cả 2 nhánh** (`response` / `human_handoff`), trace có nhánh + confidence.
- [ ] `make test` xanh; BackgroundTask ghi audit_log.
- [ ] dashboard + cổng chat khách + mobile chạy; `pnpm -r build` pass; `shared-types` dùng chung
      (gồm `ConversationStatus` enum theo PRD §15).
- [ ] Chỉ `.env.example` commit; `.env` gitignore.
- [ ] `PRD.md`, `CLAUDE.md` ở gốc repo; `docs/architecture.md` trỏ PRD.

---

## 9. Lưu ý cho Claude Code

- Async-first; cấu hình từ env; không hardcode secret. Mỗi phase 1 commit.
- **Chừa chỗ, không build logic thật** (theo PRD): State có sẵn các trường; `should_handoff` route được;
  demo 2 nhánh; audit_log đủ cột. Logic gate/RAG/intent/decision/human_handoff định tuyến/vòng học/ wiring
  WebSocket↔graph → stub + TODO trỏ PRD.
- Async/queue: BackgroundTasks (KHÔNG worker polling Redis — phá free tier Upstash). Realtime: WebSocket echo
  ở scaffold; pub/sub là TODO.
- **Response Generator là điểm phát ngôn DUY NHẤT** tới khách — đừng rải tin nhắn ở node khác (kể cả khi wiring sau).
- `conversation.status` theo tập canonical PRD §15.
- Phase 1: DỪNG chờ `.env` trước khi verify kết nối.
- Mọi quyết định nghiệp vụ → tra `PRD.md`, KHÔNG suy diễn. Plan này chỉ lo dựng khung.
- Kết thúc: in cây thư mục, lệnh chạy, checklist DoD.
