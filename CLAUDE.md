# CLAUDE.md

Hướng dẫn cho Claude Code khi làm việc trong repo này. Đọc mỗi session.

## tài liệu (đọc kỹ)

- **`PRD.md` = NGUỒN CHÂN LÝ của hệ thống.** Mọi quyết định nghiệp vụ, luồng, agent, trạng thái, yêu cầu —
  tra `PRD.md`. Khi code mâu thuẫn với PRD → PRD đúng (hoặc cập nhật PRD trước rồi mới sửa code). Khi không
  chắc "hệ thống nên hành xử thế nào" → mở PRD, KHÔNG suy diễn.

---

## Project là gì (tóm tắt — chi tiết ở PRD)

**Hệ thống chăm sóc khách hàng tự trị sử dụng Multi-Agent AI** cho shop quần áo. Tự động hóa trả lời câu hỏi
khách hàng (giá, size, vận chuyển, đổi trả…); nhân viên CSKH (Admin) chỉ can thiệp ở ca quan trọng hoặc khi
hệ thống không đủ tự tin.

Pipeline cố định (PRD §7–§8): `intent → knowledge → decision → response` + `human_handoff` có điều kiện.

- `intent` (Intent Classifier): tin nhắn khách → intent + category + entities (JSON).
- `knowledge` (Knowledge Agent, RAG): truy hồi tri thức liên quan từ Qdrant → contexts + confidence.
- `decision` (Decision Engine): đánh giá priority/severity; quyết định `auto_reply` vs `human_handoff`. **Node
  ra quyết định.** Có cờ bất định/context yếu → `human_handoff` (an toàn).
- `response` (Response Generator): sinh phản hồi **grounded theo RAG context** (auto_reply) hoặc thông báo
  chuyển tiếp + tạo **EscalationCard** (human_handoff). **Điểm phát ngôn DUY NHẤT** tới khách.
- `human_handoff`: kích hoạt có điều kiện; luôn kèm **EscalationCard** (tóm tắt + intent + ngữ cảnh + lý do +
  nháp gợi ý); Admin nhận ca → chat trực tiếp với khách (AI tạm dừng cho hội thoại đó).

Hai **gate** cấu hình (PRD §9): `auto-reply`, `auto-resolve` — Admin bật/tắt (toàn hệ thống hoặc theo
intent/category). Gate CHỈ can thiệp ca **tự tin & an toàn**; ca bất định LUÔN `human_handoff` (gate no-op).
Ba kết cục giao phản hồi: **gửi thẳng** / **duyệt nháp** (`PENDING_APPROVAL`) / **chuyển người**
(`IN_HUMAN_QUEUE`).

Kiến trúc đã chốt: **pipeline cố định, KHÔNG Supervisor** — có chủ đích, ưu tiên dự đoán được + kiểm toán +
an toàn nội dung (không trả lời sai chính sách) (PRD §5, 4 trụ cột).

Giai đoạn hiện tại: **lõi tự trị + HITL đầy đủ đã chạy live.** Agent 1 (intent), Agent 2 (RAG), Agent 3
(Decision Engine tất định), Agent 4 (Response grounded) đều thật; lưu hội thoại + bộ nhớ đa lượt (Postgres);
chat khách `/chat`, dashboard admin (hàng đợi, takeover, duyệt nháp, gate, báo cáo), auth JWT + RBAC, tra đơn
scoped, chống prompt-injection 4 lớp — tất cả live. Việc còn lại (suspend/resume + durable checkpointer,
auto-resolve, Redis pub/sub đa-worker, deploy, vòng học) và slice tiếp theo (**14 deploy**) → xem **`ROADMAP.md`**.

---

## Stack

- **Backend:** Python 3.12 · FastAPI · LangGraph · SQLAlchemy 2 (async) · Alembic · Pydantic v2. Gói: `uv`.
- **Realtime:** WebSocket (chat) + Redis pub/sub (phát tin nhắn tới client/Admin) — **event-driven, KHÔNG polling**.
- **Hạ tầng (managed-first):** Neon (Postgres) · Upstash Redis · Qdrant Cloud. Dự phòng: `docker-compose.local.yml`.
- **Async:** FastAPI BackgroundTasks (KHÔNG worker polling — phá free tier Upstash). human_handoff/clarification
  dùng suspend/resume (LangGraph interrupt + checkpointer — phase sau).
- **Frontend:** Next.js 14 · **Tailwind thuần (KHÔNG shadcn/thư viện UI)** · TanStack Query. Theo pattern
  component sẵn có (`DocumentsPanel`, `admin/gate/page.tsx`, `components/reports/*`).
- **Điện thoại (PWA):** chính web dashboard cài được lên màn hình chính cho Admin (Add to Home Screen) — một
  codebase web duy nhất, responsive; KHÔNG codebase mobile riêng.
- **AI:** LLM provider cấu hình được (OpenAI/Claude/Gemini); embeddings `text-embedding-3-small`. **Đã bật**
  (`ENABLE_LLM=true`): LLM chạy ở Agent 1 (intent) + Agent 4 (response); embeddings cho RAG (Agent 2).
- **Monorepo:** pnpm workspaces; dùng chung ở `packages/shared-types`.

---

## Quy ước code (BẮT BUỘC)

- **Async-first** ở backend: async engine/session/route. Không trộn sync I/O.
- **Cấu hình đọc từ env** qua pydantic-settings. KHÔNG hardcode secret/URL/ngưỡng.
- **Type đầy đủ:** type hints (Python), không `any` tùy tiện (TS).
- **Secret chỉ trong `.env`** (gitignore). Chỉ commit `.env.example`.
- **Commit mỗi đơn vị công việc:** message rõ ràng, prefix theo slice (`feat(agent3)/feat(memory)/feat(ui)/
  test(pipeline): ...`).
- **Neon cần SSL:** `connect_args={"ssl": True}` trong `create_async_engine`. KHÔNG `?sslmode=` (asyncpg không hiểu).
- **Response Generator là điểm phát ngôn DUY NHẤT** tới khách hàng — đừng gửi tin nhắn cho khách rải rác ở
  node khác.
- **Trạng thái hội thoại** dùng tập canonical ở PRD §15 (`conversation.status`) — thống nhất backend +
  shared-types + dashboard.
- **Realtime KHÔNG polling:** dùng WebSocket + Redis pub/sub (giữ free-tier Upstash).

---

## Bốn nguyên tắc làm việc

_(Chắt từ quan sát của Andrej Karpathy về lỗi LLM hay mắc khi code. Thiên về cẩn trọng hơn tốc độ.)_

### 1. Nghĩ trước khi code — đừng giả định, đừng giấu chỗ khó hiểu

- Nêu rõ giả định; không chắc thì **hỏi**. Nhiều cách hiểu → **trình bày lựa chọn**, đừng tự chọn im lặng.
- Có cách đơn giản hơn → **nói ra**. Điều gì không rõ → **dừng**, gọi tên, hỏi.
- Project này: nghiệp vụ chưa rõ → mở **PRD**; PRD chưa đủ → hỏi, ĐỪNG suy diễn.

### 2. Đơn giản trước — code tối thiểu giải quyết vấn đề

- Không tính năng ngoài yêu cầu. Không trừu tượng cho code dùng một lần. Không "linh hoạt" không ai yêu cầu.
- 200 dòng mà 50 là đủ → viết lại. "Kỹ sư senior có nói cái này phức tạp quá mức không?"
- ĐỪNG thêm agent/tính năng ngoài slice hiện tại "cho xịn" — lọc mọi ý tưởng qua PRD + ROADMAP trước (vd phần
  an toàn của Agent 3 dùng LUẬT tất định, KHÔNG LLM/reasoning).

### 3. Sửa có phẫu thuật — chỉ động vào cái buộc phải động

- Đừng "cải thiện" code/comment/format xung quanh. Đừng refactor cái không hỏng. Theo style sẵn có.
- Thấy dead code không liên quan → nói ra, đừng xóa. Dọn phần _do bạn_ tạo thừa.
- Mỗi dòng thay đổi truy được về yêu cầu (hoặc một mục PRD).

### 4. Thực thi theo mục tiêu — định nghĩa tiêu chí thành công rồi lặp đến khi xác minh

- Biến task thành mục tiêu kiểm chứng. Mỗi phase của plan.md có bước **Verify** — chạy (`make test` + e2e live),
  cho người dùng xem, mới commit.
- Logic nghiệp vụ: mỗi yêu cầu PRD (FR-xxx) là tiêu chí; viết test phản ánh FR rồi làm cho pass. Chạm LLM/DB →
  verify LIVE (KB đã nạp); giữ `make test` OFFLINE-xanh (mock LLM/retrieval/DB).

---

## Trạng thái hiện tại & ranh giới

**Đã THẬT (đừng coi là stub):**
- **Agent 1** Intent Classifier — taxonomy trong prompt, KHÔNG retrieval; entities LLM⊕regex.
- **Agent 2** Knowledge Agent/RAG (`/api/agents/analyze`) — truy hồi Qdrant → `rag_contexts` + `retrieval_confidence` + cờ.
- **Agent 3** Decision Engine — **tất định**: route trên CỜ (`BLOCKING_FLAGS`), **KHÔNG blend confidence**;
  `RETRIEVAL_THRESHOLD` tách khỏi `confidence_threshold`; priority/severity theo intent. KHÔNG LLM/reasoning.
- **Agent 4** Response Generator — grounded từ `rag_contexts` + phanh anti-hallucination (không tri thức → fallback +
  `hallucination_risk`). **Sole-egress:** phát cả câu trả lời lẫn `HANDOFF_NOTICE`.
- **Persistence + bộ nhớ đa lượt:** lưu conversation + message (Postgres, ca theo `customer_id` từ JWT);
  `history` (history_window) từ DB vào prompt Agent 1 + Agent 4 — **bộ nhớ từ DB**, `thread_id` sinh MỖI lượt
  (KHÔNG từ checkpointer).
- **Realtime:** `/ws/chat` chạy đủ pipeline (typing → reply). `ENABLE_LLM=true`.
- **HITL đầy đủ (08a/08b/08c):** EscalationCard + hàng đợi admin (`GET /admin/escalations`); gate §9 hai van
  (`/admin/gate-config` + `gate_service.holds_auto_reply`) với ba kết cục gửi thẳng / `PENDING_APPROVAL` /
  `IN_HUMAN_QUEUE`; admin takeover/resolve/approve/reject + chat admin↔khách qua hub in-process (status-gate:
  ca đang có người xử lý thì AI KHÔNG chạy).
- **Auth (11):** JWT HS256 + RBAC; admin routes qua `require_admin`, `/ws/chat` xác thực `?token=` (role customer).
- **Đơn hàng (16):** `order_service.lookup(order_code, customer_id)` — tra **SCOPED theo khách**; mã người khác
  và mã không tồn tại trả CÙNG một kết quả (không lộ sự tồn tại).
- **Observability:** mỗi lượt khách ghi 6 dòng `audit_log` (cùng `turn_id` + `duration_ms`); tab **Báo cáo**
  (`/admin/reports`) tổng hợp từ đó. Langfuse **bổ trợ** (trace LLM), no-op khi thiếu key.
- **Chống prompt-injection (13, NFR-7):** `core/sanitize.py` — Lớp A chuẩn hoá + cap `max_message_chars` tại
  biên WS; Lớp B `as_data_block` bọc tin khách `<tin_nhan_khach>` + chunk RAG `<tri_thuc>` (vô hiệu thẻ giả
  mạo); Lớp C 5 luật chống-injection trong system prompt Agent 1 + Agent 4; Lớp D sanitize upload RAG ad-hoc.
  **KHÔNG có cờ/detector injection** — phòng thủ là cấu trúc + 4 lớp, cố ý.

**KHÔNG (giữ ranh giới — CHƯA tới lượt, xem ROADMAP):**
- KHÔNG Supervisor / điều phối động — pipeline cố định (PRD §5). KHÔNG blend confidence cho an toàn. (Đây là
  quyết định kiến trúc VĨNH VIỄN, không phải "chưa tới lượt".)
- suspend/resume + **durable checkpointer** (09b — nay vẫn `MemorySaver` in-memory, `graph.py`); auto-resolve +
  xử lý ngoài giờ (09c); Redis pub/sub đa-worker (nay hub IN-PROCESS, 1 worker); deploy (14); vòng học (15).
- KHÔNG worker queue polling Redis — dùng BackgroundTasks/session ngắn (giữ free-tier).

**Slice tiếp theo:** **14 — Deploy** (backend → Render/Railway, FE → Vercel; hạ tầng cloud, secret theo env,
lưu ý dữ liệu cá nhân NFR-6). Code TODO trỏ số slice trong **`ROADMAP.md`**.

---

## Khi nghi ngờ

Thứ tự tra cứu: **PRD.md** (nghiệp vụ, hệ thống nên làm gì) → **ROADMAP.md** (slice nào, thứ tự, đã xong gì) →
**CLAUDE.md** (cách code) → hỏi người dùng. `plan.md` = kịch bản one-shot của slice ĐANG chạy; xong slice thì bỏ,
KHÔNG dùng làm tham chiếu lịch sử.
