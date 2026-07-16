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

Giai đoạn hiện tại: **pipeline THẬT, happy-path + lõi tự trị đã chạy live.** Agent 1 (intent), Agent 2 (RAG),
Agent 3 (Decision Engine tất định), Agent 4 (Response grounded) đều thật; lưu hội thoại + bộ nhớ đa lượt
(Postgres); cổng chat khách `/chat` + FE pipeline inspector `/rag` chạy live. Việc còn lại (HITL đầy đủ, gate,
suspend/resume, auth, deploy…) và slice tiếp theo (**08b**) → xem **`ROADMAP.md`**.

---

## Stack

- **Backend:** Python 3.12 · FastAPI · LangGraph · SQLAlchemy 2 (async) · Alembic · Pydantic v2. Gói: `uv`.
- **Realtime:** WebSocket (chat) + Redis pub/sub (phát tin nhắn tới client/Admin) — **event-driven, KHÔNG polling**.
- **Hạ tầng (managed-first):** Neon (Postgres) · Upstash Redis · Qdrant Cloud. Dự phòng: `docker-compose.local.yml`.
- **Async:** FastAPI BackgroundTasks (KHÔNG worker polling — phá free tier Upstash). human_handoff/clarification
  dùng suspend/resume (LangGraph interrupt + checkpointer — phase sau).
- **Frontend:** Next.js 14 · **Tailwind thuần (KHÔNG shadcn/thư viện UI)** · TanStack Query. Theo pattern
  component sẵn có (`ServiceStatus`, `AnalyzePanel`…), tái dùng `Badge`.
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
- **Agent 1** Intent Classifier (`/api/agents/classify`) — taxonomy trong prompt, KHÔNG retrieval; entities LLM⊕regex.
- **Agent 2** Knowledge Agent/RAG (`/api/agents/analyze`) — truy hồi Qdrant → `rag_contexts` + `retrieval_confidence` + cờ.
- **Agent 3** Decision Engine — **tất định**: route trên CỜ (`BLOCKING_FLAGS`), **KHÔNG blend confidence**;
  `RETRIEVAL_THRESHOLD` tách khỏi `confidence_threshold`; priority/severity theo intent. KHÔNG LLM/reasoning.
- **Agent 4** Response Generator — grounded từ `rag_contexts` + phanh anti-hallucination (không tri thức → fallback +
  `hallucination_risk`). **Sole-egress:** phát cả câu trả lời lẫn `HANDOFF_NOTICE`.
- **Persistence + bộ nhớ đa lượt:** lưu conversation + message (Postgres, guest sid); `history` (history_window) từ DB
  vào prompt Agent 1 + Agent 4 — **bộ nhớ từ DB**, `thread_id` sinh MỖI lượt (KHÔNG từ checkpointer).
- **Realtime:** `/ws/chat` chạy đủ pipeline (typing → reply). **FE inspector `/rag`** xem đủ 4 agent. `ENABLE_LLM=true`.

**KHÔNG (giữ ranh giới — CHƯA tới lượt, xem ROADMAP):**
- KHÔNG Supervisor / điều phối động — pipeline cố định (PRD §5). KHÔNG blend confidence cho an toàn.
- `human_handoff` node đầy đủ (EscalationCard + hàng đợi Admin, 08b), gate §9 / PENDING_APPROVAL (08a), admin
  takeover (08c), suspend/resume + **durable checkpointer** (09b — nay vẫn `MemorySaver` in-memory), Redis pub/sub
  multi-client, tích hợp đơn hàng (16), vòng học (15) — **giữ file/`policy.should_handoff` cho 08b, đừng dựng sớm.**
- KHÔNG worker queue polling Redis — dùng BackgroundTasks/session ngắn (giữ free-tier).

**Slice tiếp theo:** **08b** (human_handoff + EscalationCard + hàng đợi Admin) — nay đã có hội thoại persisted để gắn.
Code TODO trỏ số slice trong **`ROADMAP.md`**.

---

## Khi nghi ngờ

Thứ tự tra cứu: **PRD.md** (nghiệp vụ, hệ thống nên làm gì) → **ROADMAP.md** (slice nào, thứ tự, đã xong gì) →
**CLAUDE.md** (cách code) → hỏi người dùng. `plan.md` = kịch bản one-shot của slice ĐANG chạy; xong slice thì bỏ,
KHÔNG dùng làm tham chiếu lịch sử.
