# BIG PLAN — Agent 3 (slice 05) + Lưu trữ & Bộ nhớ đa lượt (slice 09a) + FE Pipeline Inspector

> **Bản chất:** kịch bản ONE-SHOT gộp 2 slice + phần FE để test. Nguồn chân lý vẫn là **`PRD.md`** (§7.3 Decision
> Engine; §12 Conversation Memory; §5 trụ cột 1 dự đoán/kiểm toán + trụ cột 3 an toàn; NFR-10 context window;
> §9/§11 — **để dành 08a/08b/08c**; durable checkpointer/suspend-resume — **để dành 09b**).
>
> **Ba mục tiêu:**
>
> - **A · Agent 3 (05):** khôi phục Decision Engine THẬT (policy TẤT ĐỊNH) — bỏ pass-through; quyết `auto_reply`
>   vs `human_handoff` + `priority`/`severity`/`escalation_reason`.
> - **B · Persistence + Memory (09a):** LƯU conversation + message vào Postgres; **bộ nhớ đa lượt** (nạp lịch sử
>   từ DB vào pipeline để hiểu ngữ cảnh).
> - **C · FE Pipeline Inspector:** mở rộng panel ở `/rag` để **quan sát đủ 4 agent** cho một câu test (thấy quyết
>   định Agent 3 + câu trả lời Agent 4) — công cụ test + minh chứng minh bạch cho ĐATN.
>
> **Ranh giới (đọc kỹ):** Agent 3 **CHỈ ra quyết định + gắn cờ**; pipeline **chạy tới cuối rồi THOÁT** (KHÔNG
> suspend/resume, KHÔNG hàng đợi admin, KHÔNG duyệt nháp — 09b/08a-c). **Response Generator là điểm phát ngôn DUY
> NHẤT** (phát cả câu trả lời lẫn thông báo handoff, luôn grounded từ `rag_contexts`). Bộ nhớ lấy từ **DB, KHÔNG
> từ checkpointer**.

---

## 0. Quyết định kiến trúc (gộp)

- **KHÔNG blend confidence.** `intent_confidence` (LLM tự khai) vs `retrieval_confidence` (cosine) là **hai thang
  khác nhau** → đừng `min` rồi so một ngưỡng. Mỗi thang có ngưỡng riêng; **Agent 3 quyết trên CỜ**; giữ cả hai
  confidence cho priority + audit.
- **Agent 3 = LUẬT tất định — KHÔNG LLM cho phần an toàn; KHÔNG reasoning model** (thừa + hại NFR-1 latency). LLM
  sentiment (nếu cần) = non-reasoning nhẹ, **để sau**.
- **Sole egress:** graph `decision → response`; `response_node` branch theo `action`. `human_handoff` node đầy đủ
  (EscalationCard + queue) = 08b — GIỮ file, đừng dựng ở đây.
- **Tách `db_conversation_id` (persist) ≠ `thread_id` (checkpointer).** GIỮ `thread_id` sinh MỚI mỗi lượt
  (MemorySaver in-memory sẽ tích luỹ reduce-channel nếu tái dùng) → **bộ nhớ từ DB**. Durable checkpointer = 09b.
- **`history` là ĐẦU VÀO chỉ-đọc** (khác `messages` output). Lịch sử chỉ để _hiểu ngữ cảnh_, KHÔNG thay `rag_contexts`.
- **Guest, không auth:** `customer_identifier` = query `?sid=` hoặc uuid sinh theo kết nối. Tài khoản = slice 11.

---

## 1. In / Out scope

**In:** tách `RETRIEVAL_THRESHOLD`; Agent 3 policy tất định + enums/state; sole-egress routing; persist
conversation/message; multi-turn memory; endpoint + panel FE inspector đủ 4 agent; test FR + persist + e2e.
**Out (để sau):** suspend/resume + durable checkpointer (09b); gate §9 / PENDING_APPROVAL (08a); human_handoff đầy
đủ + EscalationCard + admin queue + takeover (08b/08c); pub/sub multi-client; màn danh sách hội thoại (10a); auth
tài khoản (11); FE reload-lịch-sử-khi-reconnect.

---

## 2. Kế hoạch theo Phase

> Sau MỖI phase: chạy "Verify", cho tôi xem output, `git commit`, tóm tắt 1 dòng, tiếp nếu không lỗi.

### === PHẦN A · AGENT 3 (slice 05) ===

### Phase 0 — Tách `RETRIEVAL_THRESHOLD` (sửa "hai thang một ngưỡng")

- `app/core/config.py`: thêm `retrieval_threshold: float = 0.35` (env `RETRIEVAL_THRESHOLD`); GIỮ
  `confidence_threshold`. Ghi chú: _"ngưỡng cosine — PHẢI đo trên KB (Chương 4); 0.35 là mặc định tạm"_.
- `app/agents/nodes/knowledge.py`: `low_retrieval_score` dùng **`settings.retrieval_threshold`** (thay `confidence_threshold`).
- (Tùy chọn) `scripts/measure_retrieval_threshold.py`: đo phân bố cosine top-1 trên KB (câu có/không đáp án).

**Verify:** với KB đã nạp, `retrieve_knowledge("phí ship đi tỉnh?")` → KHÔNG `low_retrieval_score` oan;
`retrieve_knowledge("asdf")` → `no_relevant_knowledge`. `make test` xanh. Commit:
`feat(agent3): phase 0 - tách RETRIEVAL_THRESHOLD khỏi confidence_threshold`.

### Phase 1 — Agent 3 policy TẤT ĐỊNH (bỏ pass-through)

- `app/models/enums.py`: thêm `Priority(low/medium/high)`, `Severity(low/medium/high)`.
- `app/agents/state.py`: thêm `priority: str | None`, `severity: str | None`.
- Hằng **`BLOCKING_FLAGS`** (tập ĐÓNG cờ có mặt tại decision, từ Agent 1+2):
  `{"ambiguous_intent","multi_intent","out_of_domain","no_relevant_knowledge","low_retrieval_score","llm_unavailable","search_error"}`.
  _(KHÔNG gồm `hallucination_risk` — Agent 4 phát SAU; giữ là phanh dự phòng cuối ở Agent 4.)_
- Viết lại `app/agents/nodes/decision.py` (bỏ pass-through):
  - Đọc cờ tích luỹ `uncertainty_flags` + `intent` + `intent_confidence` + `retrieval_confidence` + `scratchpad.injected_flags`.
  - **Safety gate (luật cứng, KHÔNG blend):** `blocking = (set(flags)|set(injected)) & BLOCKING_FLAGS`. ≠ ∅ →
    `action=HUMAN_HANDOFF`, `require_human_handoff=True`, `escalation_reason=f"blocking_flags={sorted(blocking)}"`;
    ngược lại → `AUTO_REPLY`.
  - **Bảng priority/severity theo intent:** complaint→high/high; refund→high/medium; exchange→medium/low;
    order*status→medium/low; product*\*/size/shipping/promotion→low/low; other/unknown→low/low.
  - **KHÔNG** `min(confidence)`; ghi cả hai confidence + `blocking` vào `trace` (audit + Agent Monitoring).
  - `uncertainty_flags` (reducer add): CHỈ trả cờ MỚI (thường rỗng) — tránh nhân đôi. `status=DECIDING`.
  - **TODO rõ:** gate §9 (nhạy cảm → PENDING_APPROVAL) = 08a; LLM sentiment `frustrated_customer` = sau.
  - Demo: `run-demo force_handoff` tiêm `ambiguous_intent` ∈ BLOCKING → handoff tự nhiên (test 2 nhánh xanh).

**Verify:** unit `decision_node` (không cần network): `no_relevant_knowledge` → human_handoff + reason;
`intent=complaint` không cờ → auto_reply + priority=high/severity=high; product_price sạch cờ → auto_reply low/low.
`make test` xanh. Commit: `feat(agent3): phase 1 - deterministic policy (safety gate + priority/severity), bỏ pass-through`.

### Phase 2 — Định tuyến SOLE-EGRESS (Response Generator phát cả trả lời lẫn thông báo handoff)

> Hiện `response_node` chưa branch theo `action`; graph route sang `human_handoff` (ghi `result.notice`, không
> `result.reply`) → WS `final["result"]["reply"]` sẽ vỡ ở ca handoff. Sửa:

- `app/agents/graph.py`: route `decision → response` (bỏ conditional `should_handoff`→human_handoff cho slice
  này); `response → END`. **GIỮ** `human_handoff.py` + `policy.should_handoff` (ghi chú để dành 08b re-wire thành
  side-effect: EscalationCard + admin queue + suspend/resume).
- `app/agents/nodes/response.py` — `response_node` branch theo `state["action"]`:
  - `auto_reply` → `generate_reply(...)` grounded → `status=REPLIED`, `result.reply=<trả lời>`.
  - `human_handoff` → KHÔNG gọi LLM; `reply=HANDOFF_NOTICE` ("Yêu cầu của bạn đã được chuyển tới nhân viên hỗ
    trợ.") → `status=IN_HUMAN_QUEUE`, `result.reply=HANDOFF_NOTICE`, ghi `messages` (sender=ai).
  - Cả hai set `result.reply` → **WS không phải sửa**. Response Generator là node DUY NHẤT ghi `messages`/`result.reply`.

**Verify:** `run_pipeline("phí ship đi tỉnh?")` → auto_reply + reply grounded + REPLIED. `run_pipeline("asdf")` →
no_relevant_knowledge → handoff → reply=HANDOFF_NOTICE + IN_HUMAN_QUEUE. run-demo 2 nhánh. `make test` xanh.
Commit: `feat(agent3): phase 2 - sole-egress routing (Response Generator phát trả lời + handoff notice)`.

### === PHẦN B · LƯU TRỮ + BỘ NHỚ ĐA LƯỢT (slice 09a) ===

### Phase 3 — Persist conversation + message (WS lưu Postgres)

- `app/agents/state.py`: thêm `history: list[dict[str, Any]]` (đầu vào chỉ-đọc — KHÔNG reducer).
- `app/agents/graph.py`: `run_pipeline(..., history=None)` → `_initial_state` đặt `history=history or []`. GIỮ việc
  sinh `thread_id` mỗi lượt.
- `app/api/ws/chat.py` (bỏ TODO persist): connect → `sid` từ `websocket.query_params` hoặc `uuid4` →
  `async with AsyncSessionLocal() as s: conv = await create_conversation(s, customer_identifier=sid)` → giữ
  `db_conversation_id`. Mỗi tin: lưu message khách (session ngắn) → `run_pipeline` → lưu message AI + cập nhật
  `conversation.status` theo `final["result"]`.

**Verify:** `/chat` gửi 1 câu → DB có 1 conversation + 2 message (customer+ai), `customer_identifier` set.
`make test` xanh. Commit: `feat(memory): phase 3 - persist conversation + messages qua WS`.

### Phase 4 — Bộ nhớ đa lượt (nạp lịch sử từ DB vào pipeline)

- `app/services/conversation_service.py`: `get_recent_messages(session, conversation_id, limit)` → N `{sender,content}` gần nhất.
- `app/core/config.py`: `history_window: int = 8` (env `HISTORY_WINDOW`; NFR-10).
- `app/api/ws/chat.py`: TRƯỚC `run_pipeline`, nạp `history` (các lượt trước) → truyền `run_pipeline(input_text, history=...)`.
- `app/agents/nodes/intent.py`: `classify_intent(text, history=None)` — thêm lịch sử gần nhất vào prompt.
- `app/agents/nodes/response.py`: `generate_reply(..., history=None)` — thêm lịch sử vào prompt (hiểu đại từ/tham
  chiếu; vẫn grounded từ `rag_contexts`).

**Verify:** `/chat`: "áo này còn size M không shop?" → "thế còn size L?" → hiểu **size L của cùng cái áo** (không
hỏi lại). `make test` xanh. Commit: `feat(memory): phase 4 - multi-turn memory (history từ DB vào Agent 1 + Agent 4)`.

### === PHẦN C · FE PIPELINE INSPECTOR + VERIFY ===

### Phase 5 — FE Pipeline Inspector (quan sát đủ 4 agent cho một câu test)

- Backend: `app/api/routes/agents.py` thêm `POST /pipeline` (body `{message}`) → `final = await run_pipeline(input_text=message)`
  → trả `{intent, category, entities, intent_confidence, retrieval_confidence, rag_contexts, action, priority,
severity, escalation_reason, uncertainty_flags, reply}` (rút từ final state). (schema `PipelineResult`.)
- `packages/shared-types`: thêm `PipelineResult`.
- `apps/dashboard/lib/api.ts`: `runPipeline(message): Promise<PipelineResult>`.
- `apps/dashboard/components/rag/AnalyzePanel.tsx` (mở rộng — hoặc thêm `PipelinePanel.tsx`, theo pattern sẵn có
  Tailwind + TanStack): dùng `runPipeline` → render **4 khối**:
  - **Agent 1 · Intent**: intent, category, entities, intent_confidence.
  - **Agent 2 · Knowledge**: retrieval_confidence + rag_contexts (source·score·snippet).
  - **Agent 3 · Decision**: `action` (badge auto_reply/human_handoff), `priority`, `severity`, `escalation_reason`,
    và cờ chặn (highlight). ← đây là chỗ _test Agent 3 trên FE_.
  - **Agent 4 · Response**: `reply` (câu trả lời grounded hoặc thông báo handoff).
- (Tùy chọn) `apps/dashboard/app/chat/page.tsx`: phân biệt bong bóng thông báo handoff (badge/màu khác) để demo dễ thấy.

**Verify:** `/rag` inspector: "shop cho đổi trả trong bao lâu?" → Agent 3 `auto_reply` + Agent 4 câu trả lời
grounded; "thời tiết hôm nay?" → Agent 3 `human_handoff` (out_of_domain/no_relevant_knowledge) + priority/severity

- Agent 4 thông báo chuyển người. `pnpm -r build` pass. Commit:
  `feat(ui): phase 5 - pipeline inspector đủ 4 agent (test Agent 3 + Agent 4 trên FE)`.

### Phase 6 — Test FR + e2e verify (bỏ hẳn pass-through)

- Test đơn vị `decision_node` (cờ→action; intent→priority/severity); persist (đúng sender); `get_recent_messages`
  cap `history_window`; golden e2e (KB→auto_reply grounded; no-knowledge→handoff notice; complaint→priority high).
- Không còn `pass_through` trong trace; `run-demo` 2 nhánh; `make test` xanh; `pnpm -r build` pass.

**Verify:** `make test` xanh; `/chat` đa lượt + định tuyến đúng; `/rag` inspector hiển thị quyết định. Commit:
`test(pipeline): phase 6 - FR tests + e2e verify`.

---

## 3. Definition of Done

- [ ] `RETRIEVAL_THRESHOLD` tách riêng; Agent 2 dùng nó; ngưỡng đo trên KB (không escalate oan vì 0.6).
- [ ] Agent 3 **tất định**: route bằng **cờ** (BLOCKING_FLAGS), **KHÔNG blend confidence**; có priority/severity;
      **không LLM/reasoning**; pass-through đã bỏ; run-demo 2 nhánh đúng.
- [ ] **Response Generator là điểm phát ngôn DUY NHẤT** — phát cả trả lời grounded lẫn handoff notice; status đúng
      (REPLIED / IN_HUMAN_QUEUE); WS không phải sửa.
- [ ] Hội thoại + message **lưu Postgres** (guest sid); **đa lượt hiểu ngữ cảnh**; chỉ nạp N tin (`history_window`);
      bộ nhớ từ **DB** (thread_id vẫn sinh mỗi lượt).
- [ ] **FE inspector `/rag`** hiển thị đủ 4 agent — thấy `action`/`priority`/`severity`/`escalation_reason` của
      Agent 3 + câu trả lời Agent 4. `/chat` vẫn test được định tuyến + đa lượt.
- [ ] `make test` xanh; `pnpm -r build` pass. Agent 3 CHỈ quyết định + gắn cờ; pipeline chạy hết rồi thoát.

---

## 4. Ghi chú cho Claude Code

- **KHÔNG blend confidence — route trên CỜ.** Agent 2 phát `low_retrieval_score` bằng `RETRIEVAL_THRESHOLD`; Agent
  3 đọc cờ; giữ cả hai confidence cho priority + audit. **Agent 3 tất định — KHÔNG LLM/reasoning cho an toàn.**
- **`BLOCKING_FLAGS` là tập ĐÓNG** cờ tại decision (Agent 1+2); `hallucination_risk` KHÔNG thuộc (Agent 4 phát sau).
- **Response Generator là điểm phát ngôn DUY NHẤT** — branch theo `action`; `human_handoff` node đầy đủ = 08b, GIỮ
  file, đừng dựng.
- **Tách `db_conversation_id` (persist) ≠ `thread_id` (checkpointer);** GIỮ thread_id sinh mỗi lượt; **bộ nhớ từ
  DB**. `history` là đầu vào chỉ-đọc; lịch sử KHÔNG thay `rag_contexts` (phanh chống bịa còn nguyên).
- **Session DB NGẮN** (`async with AsyncSessionLocal()` mỗi thao tác) — Neon free giới hạn connection.
- **FE inspector** dùng `run_pipeline` (không persist — là công cụ dev); nó test Agent 3/Agent 4 **single-shot**
  (KHÔNG test đa lượt — đa lượt test qua `/chat`). Theo pattern UI sẵn có (Tailwind + TanStack), KHÔNG shadcn.
- **Ranh giới tuyệt đối:** Agent 3 chỉ quyết định + gắn cờ; pipeline chạy hết rồi thoát. "Chờ admin" (đóng băng
  state rồi đánh thức) = 09b, KHÔNG làm ở đây. Async-first; config từ env; "sửa có phẫu thuật".
- **Slice này mở khóa HITL:** kế tiếp 08b (human_handoff + EscalationCard + admin queue — nay có hội thoại
  persisted) → 08c (admin chat/takeover, cần pub/sub) → 08a (gate §9) → 09b (durable checkpointer + suspend/resume).
