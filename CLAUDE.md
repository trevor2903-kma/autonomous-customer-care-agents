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
scoped, chống prompt-injection 4 lớp, auto-resolve theo im lặng, lượt clarification (AWAITING_CUSTOMER), thông báo
ngoài giờ — tất cả live. Việc còn lại (durable checkpointer + interrupt, admin-presence offline, Redis pub/sub
đa-worker, deploy, vòng học) và
slice tiếp theo (**14 deploy**) → xem **`ROADMAP.md`**.

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
- **Agent 1** Intent Classifier — taxonomy trong prompt, KHÔNG retrieval; entities LLM⊕regex. `order_id` neo từ khoá
  + từ nối đóng; số tiền ("đơn giá 250000", "đơn trên 500k", "500.000đ") KHÔNG thành mã — cùng luật lọc cả entity LLM.
- **Agent 2** Knowledge Agent/RAG — truy hồi Qdrant → `rag_contexts` + `retrieval_confidence` + cờ (`search_error` =
  Qdrant/embedding hỏng ≠ `no_relevant_knowledge`). Tra đơn SCOPED cho `order_status`/`shipping`/`refund`/`exchange`/
  `complaint`: đơn tra được thì cờ grounding truy hồi KHÔNG chặn (dữ liệu đơn là grounding); shipping không ra đơn →
  trả lời chính sách; thiếu danh tính → `order_unresolved`. Lượt resume mã trơ truy hồi theo CÂU HỎI GỐC; mã hỏng chỉ
  đếm khi bot đã thật sự báo "không tìm thấy" (khớp đúng template). Route dev `/api/agents/analyze` = admin-only.
- **Agent 3** Decision Engine — **tất định**: route trên CỜ (`BLOCKING_FLAGS`), **KHÔNG blend confidence**;
  `RETRIEVAL_THRESHOLD` tách khỏi `confidence_threshold`; priority/severity theo intent. KHÔNG LLM/reasoning.
- **Agent 4** Response Generator — grounded từ facts.md + `rag_contexts` + `order_context`; phanh anti-hallucination:
  không nguồn / LLM lỗi → KHÔNG bịa, `hallucination_risk` → **chuyển người** (HANDOFF_NOTICE + `IN_HUMAN_QUEUE` +
  EscalationCard, FR-PIPE-5). "Không tìm thấy đơn" = template cố định → `AWAITING_CUSTOMER` (intent resume được) để
  khách gửi lại mã trơ. **Sole-egress:** phát câu trả lời, `HANDOFF_NOTICE` (+ biến thể ngoài giờ), câu hỏi clarify.
  Dòng blockquote (`>`) trong facts.md = ghi chú biên tập, KHÔNG vào prompt.
- **Persistence + bộ nhớ đa lượt:** lưu conversation + message (Postgres, ca theo `customer_id` từ JWT);
  `history` (history_window) từ DB vào prompt Agent 1 + Agent 4 — **bộ nhớ từ DB**, `thread_id` sinh MỖI lượt
  (KHÔNG từ checkpointer).
- **Realtime (giao thức v2, audit v2):** `/ws/chat`, `/ws/admin/{id}`, `/ws/admin-inbox` nói frame JSON (ack ·
  ping/pong · typing · reply · handoff · pending · message · status · error). Tin mang `client_msg_id` → chống trùng
  (registry in-process + unique index `message(conversation_id, client_msg_id)`), ack biên nhận ngay. Lượt khách TUẦN TỰ
  theo khách (asyncio.Lock, mọi tab), chạy trong task KHÔNG bị huỷ khi khách đóng tab; kết quả lượt ghi MỘT transaction
  (CAS status + tin AI + EscalationCard) **TRƯỚC** khi báo khách; thua CAS (admin vừa tiếp quản/đóng) → không gửi trả
  lời, gửi frame `status`; ghi hỏng cả sau 1 lần thử lại → KHÔNG gửi `handoff`/`pending` (khách nhận câu không hứa
  hẹn). Socket nối lúc chưa có ca được gắn vào ca do lượt tab khác mở (registry socket đang sống); frame tới khách
  không mang id nhân viên. Dashboard tự nối lại (backoff + heartbeat, URL dựng từ token hiện tại) rồi ghép lại lịch sử
  khi server báo `system` (đã gắn hub); inbox admin thay polling (gom 3 s; refetch 60 s chỉ là lưới an toàn).
  `ENABLE_LLM=true`.
- **HITL đầy đủ (08a/08b/08c):** EscalationCard + hàng đợi admin (`GET /admin/escalations`); gate §9 hai van
  (`/admin/gate-config` + `gate_service.holds_auto_reply`) với ba kết cục gửi thẳng / `PENDING_APPROVAL` /
  `IN_HUMAN_QUEUE`; admin takeover/resolve/approve/reject + chat admin↔khách qua hub in-process (status-gate:
  ca đang có người xử lý thì AI KHÔNG chạy). Mọi chuyển trạng thái (pipeline, admin, auto-resolve) là
  **compare-and-set** (`conversation_service.transition_status`, bảng chuyển PRD §15): sai trạng thái / ca do admin
  khác giữ → 409; duyệt/từ chối kèm `expected_draft` (chống ABA); WS admin chỉ người đang giữ ca gửi được; mọi hành
  động admin ghi `audit_log` (FR-ESC-5).
- **Auto-resolve theo im lặng (09c, phần inactivity):** `services/auto_resolve.py` — `classify_idle` THUẦN (NOOP/
  REMIND/RESOLVE) + `run_sweep_once`/`sweep_loop` (asyncio task trong lifespan, quét Postgres mỗi
  `sweep_interval_seconds`, KHÔNG polling Redis). CHỈ `REPLIED`/`AWAITING_CUSTOMER`; gate `auto_resolve` OFF →
  no-op. Hai ngưỡng T1 `auto_resolve_minutes` (→ 1 tin nhắc) + T2 `auto_resolve_grace_minutes` (→ `RESOLVED`);
  `conversation.auto_resolve_reminded_at` mốc đã nhắc, reset khi khách nhắn. Ghi bằng **guarded UPDATE**
  (`WHERE status IN sweepable [+ reminded_at guard] [+ REMIND: vẫn im lặng ≥ T1 trên chính row]`, chỉ hành động khi
  `rowcount==1`) → KHÔNG nhắc/đóng nhầm ca vừa bị admin takeover / khách nhắn lại (FR-ASYNC-4). Tin nhắc/đóng =
  template cố định chèn bằng `conversation_service.insert_message` (KHÔNG bump `last_message_at`) trong CÙNG transaction
  với CAS, commit rồi mới phát hub (sole-egress, KHÔNG LLM) — không còn "đã đánh dấu nhắc mà tin không tới". Session
  ngắn mỗi ca; pre-filter thời gian + `LIMIT` (`sweep_batch_limit`) để không nạp mọi ca `REPLIED` mỗi vòng.
- **Lượt clarification (09b, AWAITING_CUSTOMER):** Decision route thứ ba `clarify` (SAU safety-gate) khi intent
  gắn-với-đơn (`order_status`/`refund`/`exchange`) thiếu `order_id` (`CLARIFY_MISSING_ENTITY`) → Response phát câu hỏi
  CỐ ĐỊNH (`CLARIFY_QUESTION`, no LLM) + `AWAITING_CUSTOMER`. Loop-guard qua `state.prior_status` (WS truyền status
  TRƯỚC lượt): đã hỏi 1 lần vẫn thiếu → `human_handoff` (FR-ASYNC-2). Resume = lượt kế với DB history (KHÔNG
  checkpointer). Safety-gate LUÔN ưu tiên clarify; refund/exchange sau khi có mã vẫn qua gate/duyệt nháp.
  **Resume mã TRƠ:** khách đáp chỉ bằng con số → `intent.resume_order_code` + short-circuit TẤT ĐỊNH khôi phục
  intent GỐC (lấy từ `conversation.current_intent`, persist mỗi khi lượt kết thúc ở `AWAITING_CUSTOMER` — clarify HOẶC
  "không tìm thấy đơn" — qua `transition_status(current_intent=)`)
  + `order_id`, **KHÔNG gọi LLM** — vì LLM hay xếp số trơ thành `other` → `out_of_domain` → escalate oan.
  Chỉ nới trong ngữ cảnh resume (regex `order_id` thường vẫn neo TỪ KHOÁ, chống nhầm "giá 250000").
  `intent.py` import `CLARIFY_MISSING_ENTITY` từ `decision.py` để tập intent clarify có MỘT nguồn chân lý.
- **Ngoài giờ (09c offline, business-hours):** `services/business_hours.is_within_support_hours` (thuần,
  `support_hours_start/end` + `support_timezone` Asia/Ho_Chi_Minh, dep `tzdata`). `response_node` nhánh handoff NGOÀI
  giờ → `HANDOFF_NOTICE_AFTER_HOURS` ("nhân viên sẽ phản hồi sớm") thay `HANDOFF_NOTICE`; ca vẫn `IN_HUMAN_QUEUE` +
  EscalationCard. AI auto-reply 24/7 không đổi. **Chưa có:** admin-presence thật (nay chỉ theo giờ).
- **Auth (11):** JWT HS256 + RBAC; admin routes qua `require_admin`; mọi WS xác thực `?token=` và đọc role TỪ DB
  (token hỏng / sai role / user bị xoá → 4401; DB lỗi → 1011, client nối lại); WS admin đọc lại role MỖI tin (bị hạ
  quyền giữa chừng → `not_assigned`). Rate limit in-process (`core/rate_limit.py`): login theo IP + email, register
  theo IP (429 + `Retry-After`), tin `/ws/chat` theo khách; bcrypt chạy threadpool + hash giả khi email không tồn tại.
  `/api/health` không trả nguyên văn lỗi hạ tầng; lỗi SQL không in tham số ra log (`hide_parameters`).
- **Đơn hàng (16):** `order_service.lookup(order_code, customer_id)` — tra **SCOPED theo khách**; mã người khác
  và mã không tồn tại trả CÙNG một kết quả (không lộ sự tồn tại).
- **Tri thức (RAG):** reindex **blue/green qua ALIAS Qdrant** — tên phục vụ (`qdrant_collection`) là alias trỏ
  collection vật lý; dựng xong mới đổi alias nguyên tử (không gián đoạn; lần reindex ĐẦU chuyển collection thật → alias,
  gián đoạn < 1 s) rồi dọn bản mồ côi. Upload ad-hoc có phiên bản (upload lại = THAY; ghi sổ hỏng → gỡ đúng bản vừa
  ghi), bỏ `## Internal Note`, tên file chỉ lấy phần cuối, không đè dòng canonical. Khoá ghi in-process cho
  reindex/upload/xoá/reset; reset xoá sổ TRONG transaction rồi mới reset Qdrant (Qdrant hỏng → sổ không mất).
- **Observability:** mỗi lượt khách ghi 6 dòng `audit_log` (cùng `turn_id` + `message_id`; dòng `delivery` có
  `timings` tách pre-pipeline / pipeline / ghi DB / gửi socket / fan-out — số đo phía SERVER; dòng `knowledge` tách
  embed / Qdrant / tra đơn); dòng `decision` chỉ mang lý do CỦA Agent 3, lý do của LƯỢT (kể cả Agent 4 fallback) ở dòng
  `delivery`. Mỗi hành động admin ghi 1 dòng `node="admin"`. Tab **Báo cáo** (`/admin/reports`): trung vị/p95/p99,
  % ≤ NFR-1, lý do chuyển người. Langfuse **bổ trợ** (trace LLM), no-op khi thiếu key. Client OpenAI có timeout +
  `max_retries` từ env.
- **Chống prompt-injection (13, NFR-7):** `core/sanitize.py` — Lớp A chuẩn hoá + cap `max_message_chars` tại
  biên WS (cắt thô trước khi chuẩn hoá; frame WS ≤ 64 KiB qua uvicorn `--ws-max-size`); Lớp B `as_data_block` bọc tin
  khách `<tin_nhan_khach>` + chunk RAG `<tri_thuc>` (vô hiệu thẻ giả mạo, kể cả thẻ có thuộc tính) — áp cho CẢ lịch sử
  hội thoại (`neutralize_tags` + repr) và dòng entities trong prompt Agent 4; Lớp C 5 luật chống-injection trong system
  prompt Agent 1 + Agent 4; Lớp D sanitize upload RAG ad-hoc.
  **KHÔNG có cờ/detector injection** — phòng thủ là cấu trúc + 4 lớp, cố ý.

**KHÔNG (giữ ranh giới — CHƯA tới lượt, xem ROADMAP):**
- KHÔNG Supervisor / điều phối động — pipeline cố định (PRD §5). KHÔNG blend confidence cho an toàn. (Đây là
  quyết định kiến trúc VĨNH VIỄN, không phải "chưa tới lượt".)
- **durable checkpointer + `interrupt()`** (09b — nay vẫn `MemorySaver` in-memory, `graph.py`; **lượt clarification
  AWAITING_CUSTOMER ĐÃ XONG** trên DB+status, checkpointer chưa); **admin-presence offline** (09c — **offline theo giờ
  hỗ trợ ĐÃ XONG**, presence thật chưa); Redis pub/sub đa-worker (nay hub, khoá lượt theo khách, registry chống trùng,
  registry socket đang sống, rate limiter, khoá ghi RAG đều IN-PROCESS → GIỮ 1 uvicorn worker); deploy (14); vòng
  học (15).
- KHÔNG worker queue polling Redis — dùng BackgroundTasks/session ngắn (giữ free-tier).

**Slice tiếp theo:** **14 — Deploy** (backend → Render/Railway, FE → Vercel; hạ tầng cloud, secret theo env,
lưu ý dữ liệu cá nhân NFR-6). Code TODO trỏ số slice trong **`ROADMAP.md`**.

---

## Khi nghi ngờ

Thứ tự tra cứu: **PRD.md** (nghiệp vụ, hệ thống nên làm gì) → **ROADMAP.md** (slice nào, thứ tự, đã xong gì) →
**CLAUDE.md** (cách code) → hỏi người dùng. `plan.md` = kịch bản one-shot của slice ĐANG chạy; xong slice thì bỏ,
KHÔNG dùng làm tham chiếu lịch sử.
