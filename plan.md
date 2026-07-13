# PLAN — Happy-case pipeline (Agent 4 + Decision pass-through) + Cổng chat khách chạy thật

> **Bản chất:** kịch bản ONE-SHOT, xong thì bỏ. Nguồn chân lý vẫn là **`PRD.md`** (§7.4 Response Generator;
> §6/§16 chat & realtime; §5 trụ cột 3 + §14 FR-PIPE-5 grounding). Repo: Agent 1 + Agent 2 đã thật; Agent 3
> **TẠM bỏ**, Agent 4 làm thật.
>
> **Mục tiêu:** khách vào **cổng chat `/chat`**, hỏi một câu mà kho tri thức trả lời được → **agent tự trả lời
> grounded, không người can thiệp**. Mô phỏng & quan sát một happy case chạy trọn pipeline
> `intent → knowledge → decision(pass-through) → response`, và trả lời hiển thị ngay trên giao diện khách.
>
> **Quyết định TẠM (ghi rõ để không lệch vai):** bỏ Agent 3 = `decision_node` **pass-through** (traffic thật →
> luôn `auto_reply`). **Phanh an toàn chuyển vào Agent 4** (không có tri thức → không bịa → câu fallback). Khi
> làm Agent 3 (ROADMAP slice 05), khôi phục logic quyết định (priority/severity + flags/confidence → handoff)
> về đúng chỗ; Agent 4 quay lại chỉ lo sinh câu trả lời.

---

## 0. In / Out scope

**In scope:** Agent 4 (Response Generator, grounded + phanh anti-hallucination); Decision pass-through (giữ demo
nhánh handoff cho run-demo/test); wire WebSocket `/ws/chat` chạy ĐỦ pipeline và trả câu trả lời; cổng chat khách
`/chat` hiển thị câu trả lời AI.

**Out of scope (để slice/phase sau — theo ROADMAP):** Agent 3 thật (05); gate/PENDING_APPROVAL (§9); human_handoff
UI + EscalationCard + admin queue (Phase 2); **bộ nhớ hội thoại / context window đa lượt** (09a — giờ single-turn);
Redis pub/sub multi-client (chỉ 1 khách → gửi thẳng qua WS là đủ); persist hội thoại/audit đầy đủ (Phase 4 —
để tuỳ chọn, không bắt buộc cho demo).

---

## 1. Kế hoạch theo Phase

> Sau MỖI phase: chạy "Verify", cho tôi xem output, `git commit` (`feat(pipeline): phase N - ...`), tóm tắt 1 dòng, tiếp nếu không lỗi.

### Phase 0 — Agent 4 · Response Generator (§7.4, FR-PIPE-5)

- `app/agents/nodes/response.py` (viết thật, tách hàm thuần tái dùng):
  - `async generate_reply(query, intent, entities, rag_contexts) -> {reply, uncertainty_flags}`:
    - **Phanh grounding:** nếu `not rag_contexts` **hoặc** thiếu `settings.llm_api_key` → **KHÔNG gọi LLM bịa**;
      trả câu fallback lịch sự (vd "Dạ câu hỏi này em xin phép chuyển tới nhân viên hỗ trợ để trả lời chính xác
      hơn ạ.") + cờ `["hallucination_risk"]`.
    - Có `rag_contexts`: gọi LLM (`AsyncOpenAI`, `settings.llm_model`) với prompt: _soạn câu trả lời CSKH tiếng
      Việt, thân thiện, NGẮN GỌN, CHỈ dựa trên các đoạn tri thức được cung cấp (rag_contexts). KHÔNG bịa thông
      tin ngoài context. Nếu context không đủ để trả lời chắc chắn thì nói sẽ chuyển nhân viên, KHÔNG bịa._
      Truyền vào: `query`, `intent`, `entities`, và các đoạn `rag_contexts[].text` (kèm source). Cờ = [].
  - `async response_node(state)`: gọi `generate_reply` với `query=state["input"]`, `intent`, `entities`,
    `rag_contexts` từ state → ghi `draft_reply`, `messages:[{"sender":"ai","content":reply}]`,
    `result:{"branch":"response","action":state.get("action"),"reply":reply}`, `status=REPLIED`,
    `uncertainty_flags` (reducer add) + `trace`. **Node DUY NHẤT ghi tin nhắn AI** (PRD §7.4).

**Verify:** unit — `generate_reply("shop cho đổi trả trong bao lâu?", "refund", {}, [<đoạn đổi trả>])` → câu trả
lời có "7 ngày"; `generate_reply("x", "other", {}, [])` → fallback + `hallucination_risk`. `make test` xanh.
Commit: `feat(pipeline): phase 0 - Agent 4 Response Generator (grounded + anti-hallucination)`.

### Phase 1 — Decision pass-through (TẠM bỏ Agent 3)

- `app/agents/nodes/decision.py`: **TẠM** bỏ đánh giá real flags/confidence. Chỉ giữ nhánh demo:
  - `injected = (scratchpad or {}).get("injected_flags")`; `handoff = bool(injected)`;
    `action = HUMAN_HANDOFF if handoff else AUTO_REPLY`; `require_human_handoff = handoff`.
  - ⇒ traffic thật (không tiêm cờ) → **luôn `auto_reply`** (happy case); `run-demo force_handoff` (tiêm
    `ambiguous_intent`) → vẫn `human_handoff` (giữ test 2 nhánh xanh).
  - Ghi **TODO to** (PRD §7.3, ROADMAP 05): khôi phục priority/severity + quy tắc an toàn thật (accumulated
    flags / `min(intent_confidence, retrieval_confidence)` < ngưỡng → handoff). Grounding hiện do Agent 4 giữ.

**Verify:** `run_pipeline(input_text="phí ship đi tỉnh bao nhiêu?")` → `action=auto_reply`, đi nhánh `response`;
`run-demo` với `force_handoff=True` → `human_handoff`. `make test` xanh. Commit:
`feat(pipeline): phase 1 - decision pass-through (auto_reply) tạm bỏ Agent 3`.

### Phase 2 — Realtime: wire WebSocket `/ws/chat` chạy ĐỦ pipeline (§6, §8, §16)

- `app/api/ws/chat.py` (thay chế độ classification):
  - Khi client kết nối: tạo `conversation_id = str(uuid4())` (giữ trong scope WS); gửi
    `{"type":"system","message":"connected"}`.
  - Mỗi tin nhắn khách: gửi `{"type":"typing"}` (UX) → `final = await run_pipeline(input_text=msg,
conversation_id=conversation_id)` → `reply = final["result"]["reply"]` → gửi `{"type":"reply","content":reply}`.
  - Bọc try/except: lỗi pipeline → gửi `{"type":"reply","content":"<câu xin lỗi + chuyển nhân viên>"}`, KHÔNG
    rớt kết nối.
  - **KHÔNG cần Redis pub/sub** (1 khách/1 kết nối — gửi thẳng). Persist hội thoại/message = TUỲ CHỌN (để Phase 4).

**Verify:** dùng script/`wscat` gửi "shop cho đổi trả trong bao lâu?" → nhận `{"type":"typing"}` rồi
`{"type":"reply","content":"...7 ngày..."}`. Commit: `feat(pipeline): phase 2 - WS chạy full pipeline + trả reply`.

### Phase 3 — Cổng chat khách (FE) hiển thị câu trả lời AI (§16)

- `apps/dashboard/components/chat/ChatWindow.tsx`: đổi type `from: "you" | "system" | "ai"` (bỏ `"echo"`); render
  bong bóng `"ai"` (nền trắng viền); đổi empty-state copy → "Hỏi shop về sản phẩm, size, đổi trả, vận chuyển…".
- `apps/dashboard/app/chat/page.tsx`: trong `ws.onmessage` xử lý:
  - `data.type === "system"` → push `system`.
  - `data.type === "typing"` → set `typing=true` (hiện "đang trả lời…").
  - `data.type === "reply"` → `typing=false`, push `{from:"ai", text:data.content}`.
  - Giữ `send` gửi raw text như cũ. Bỏ nhánh `echo`.
- `apps/dashboard/components/chat/Header.tsx`: bỏ copy "echo — scaffold" → hiện "Đang hoạt động" khi connected.

**Verify:** `make dev-backend` + `make dev-dashboard`; mở `http://localhost:3000/chat`, hỏi "shop cho đổi trả
trong bao lâu?" → thấy "đang trả lời…" rồi bong bóng AI trả lời grounded. `pnpm -r build` pass. Commit:
`feat(pipeline): phase 3 - cổng chat khách hiển thị câu trả lời AI`.

### Phase 4 — Verify happy case end-to-end

- Đảm bảo kho tri thức đã nạp: `/api/rag/info` có `knowledge_base_shop_quan_ao.pdf` (nếu trống → upload lại qua `/rag`).
- Mở `/chat`, hỏi vài câu **KB trả lời được**: "đổi trả trong bao lâu?", "phí ship đi tỉnh?", "mình 1m60 50kg mặc
  size gì?", "có mã giảm giá cho khách mới không?" → agent tự trả lời grounded.
- Hỏi câu **ngoài KB**: "thời tiết hôm nay thế nào?" → câu fallback lịch sự (KHÔNG bịa).

**Verify:** happy case chạy trọn không cần người; câu ngoài KB → fallback; `make test` xanh; `pnpm -r build` pass.
Commit: `chore(pipeline): phase 4 - verify happy case e2e`.

---

## 2. Definition of Done

- [ ] `/chat`: khách hỏi câu KB trả lời được → **agent tự trả lời grounded** (nội dung bám kho tri thức), có
      indicator "đang trả lời…".
- [ ] Câu ngoài KB / không có tri thức → **fallback lịch sự, KHÔNG bịa** (cờ `hallucination_risk`).
- [ ] Pipeline chạy trọn `intent → knowledge → decision(auto_reply) → response`; Response Generator là điểm phát
      ngôn DUY NHẤT (chỉ node này ghi tin AI).
- [ ] `run-demo force_handoff` vẫn ra `human_handoff` (giữ 2 nhánh); `make test` xanh; `pnpm -r build` pass.
- [ ] Decision pass-through có **TODO rõ** khôi phục Agent 3 (ROADMAP 05); không có logic quyết định "vĩnh viễn"
      nằm trong Agent 4.

---

## 3. Ghi chú cho Claude Code

- **Bỏ Agent 3 là TẠM:** `decision_node` chỉ handoff khi có `injected_flags` (demo); traffic thật → `auto_reply`.
  KHÔNG xoá node/edges khỏi graph (để Agent 3 cắm lại). Ghi TODO trỏ PRD §7.3 + ROADMAP 05.
- **Agent 4 grounded, KHÔNG bịa:** trả lời CHỈ từ `rag_contexts`; rag_contexts rỗng / thiếu key → fallback +
  `hallucination_risk` (đây chính là phanh an toàn thay cho Agent 3 tạm thời). Response Generator = điểm phát
  ngôn DUY NHẤT — chỉ node này ghi `messages` (sender=ai).
- **Realtime:** 1 khách → gửi thẳng qua WS; **KHÔNG** thêm Redis pub/sub (đó là cho multi-client/admin ở HITL
  phase sau, FR-ASYNC-7).
- **Single-turn:** mỗi tin nhắn chạy pipeline độc lập; bộ nhớ hội thoại đa lượt (context window) là ROADMAP 09a.
- **Chọn câu demo KB trả lời được** (đổi trả/ship/size/khuyến mãi). Tránh câu cần dữ liệu ngoài như trạng thái
  đơn thật ("đơn 6578 tới đâu?") — chưa có tích hợp hệ thống đơn (tool Phase 2); Agent 4 chỉ trả được chính sách chung.
- Async-first; config từ env; "sửa có phẫu thuật"; FE theo pattern sẵn có. Cần `LLM_API_KEY` + kho tri thức đã upload.
- Sau slice này: Agent 3 thật (05) → chuyển quyết định về đúng chỗ; rồi HITL/gate (Phase 2), memory/async (Phase 3).
