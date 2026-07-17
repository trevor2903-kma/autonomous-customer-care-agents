# BIG PLAN — HITL Admin: Escalation Queue (08b) + Takeover & Live Reply (08c) + Gates & Draft Approval (08a) + FE Admin

> **Bản chất:** kịch bản ONE-SHOT LỚN (3 slice + FE admin), chạy phase-by-phase — Claude Code có thể dừng/tiếp
> giữa các phase. Nguồn chân lý: **`PRD.md`** (§11 EscalationCard/takeover; §9 gate/PENDING_APPROVAL; §10 realtime
> FR-ASYNC-7; §17 dashboard). Sau khi xong = **vòng HITL trọn vẹn, demo được**.
>
> **Mục tiêu:** hội thoại escalate → **admin thấy trong hàng đợi kèm EscalationCard** (08b) → **admin tiếp quản,
> trả lời khách trực tiếp** (08c) → và **ca nhạy cảm: AI soạn nháp, admin duyệt trước khi gửi** (08a). Kèm **FE admin**.
>
> **Quyết định kiến trúc (đọc kỹ):**
>
> - **Pub/sub TRONG-PROCESS** (1 worker) qua một `hub` nhỏ (dict `conversation_id → set WS`), **event-driven, KHÔNG
>   polling**. Redis pub/sub (PRD §10) là bản nâng cấp **đa-worker** — swap sau, không làm ở đây. Giữ 1 worker.
> - **Takeover ≠ suspend/resume.** Dùng **status-gate**: khi hội thoại đang có người xử lý (IN_HUMAN_QUEUE/
>   HUMAN_HANDLING/PENDING_APPROVAL) thì **AI KHÔNG chạy** — tin khách route sang admin. KHÔNG cần LangGraph
>   interrupt/checkpointer (đó là 09b).
> - **EscalationCard dựng từ final state** (không cần re-wire graph): WS/service gom intent/entities/rag_context/
>   reason/priority/severity (+ nháp cho ca PENDING_APPROVAL) → lưu lên conversation.
> - **Gate:** `auto_reply` + category **nhạy cảm** → **PENDING_APPROVAL** (giữ nháp Agent 4 chờ admin duyệt).
>   `human_handoff` LUÔN escalate (bất biến FR-GATE-2). Response Generator vẫn là egress TỰ ĐỘNG duy nhất; tin
>   admin là egress-người riêng (qua hub).
> - **Admin identity tối giản:** chưa có admin auth (slice 11) → dùng một "demo admin" (id cố định / query param).

---

## 0. In / Out scope

**In:** cột conversation (priority/severity/escalation_card) + migration; endpoint + UI hàng đợi escalation;
pub/sub in-process + status-gating + admin WS + takeover; UI admin chat/takeover; gate config + PENDING_APPROVAL +
duyệt/sửa/gửi nháp + UI; e2e + test.
**Out (để sau):** Redis pub/sub đa-worker; durable checkpointer + suspend/resume + AWAITING_CUSTOMER (09b);
auto-resolve/offline (09c); admin auth/RBAC thật (11); danh sách TẤT CẢ hội thoại (10a — queue này chỉ escalation);
monitoring/analytics (10b/c); push/badge notification thật (nay chỉ hiện trong queue khi refresh).

---

## 1. Kế hoạch theo Phase

> Mỗi phase để `make test` (backend) / `pnpm -r build` (frontend) XANH rồi `git commit`, tóm tắt 1 dòng, tiếp nếu không lỗi.

### === PHẦN A · 08b — HÀNG ĐỢI ESCALATION + ESCALATIONCARD ===

### Phase 0 — Model + service (lưu card/priority/severity)

- `app/models/conversation.py`: thêm `priority: str | None`, `severity: str | None`, `escalation_card: dict|None`
  (JSONB, nullable). Tạo **migration Alembic**.
- `app/services/escalation_service.py` (mới): `build_escalation_card(final_state, trigger_message) -> dict`
  (summary = tin khách kích hoạt + intent; intent/entities/rag_context (top nguồn); escalation_reason; priority;
  severity; `suggested_reply` = nháp — rỗng cho handoff, có cho PENDING_APPROVAL); `persist_escalation(session,
conv_id, card, priority, severity, reason)`; `list_escalations(session, statuses, limit)` (lọc theo status, **sắp
  giảm dần theo priority** high→low rồi `last_message_at`).

**Verify:** unit `build_escalation_card` từ một final-state mẫu → card đủ trường; `list_escalations` sắp đúng thứ tự.
`make test` xanh. Commit: `feat(hitl): phase 0 - conversation escalation cols + escalation_service`.

### Phase 1 — WS lưu card khi handoff + endpoint queue

- `app/api/ws/chat.py`: sau `run_pipeline`, nếu `status == IN_HUMAN_QUEUE` → `build_escalation_card` +
  `persist_escalation` (card + priority + severity + reason từ final state).
- `app/api/routes/admin.py` (mới, prefix `/admin`): `GET /escalations` → `list_escalations([IN_HUMAN_QUEUE,
PENDING_APPROVAL])` → danh sách `{conversation_id, customer_identifier, status, priority, severity,
escalation_reason, escalation_card, last_message_at}`. `GET /conversations/{id}` → hội thoại + messages (cho UI).
- `packages/shared-types`: `Escalation`, `AdminConversation` (+ message). `apps/dashboard/lib/api.ts`:
  `getEscalations()`, `getAdminConversation(id)`.

**Verify:** `/chat` hỏi câu vô nghĩa → escalate → `GET /api/admin/escalations` có ca đó, đúng priority/card.
`make test` xanh; `pnpm -r build` pass. Commit: `feat(hitl): phase 1 - persist card + GET /api/admin/escalations`.

### Phase 2 — FE trang hàng đợi admin

- `apps/dashboard/app/admin/page.tsx`: trang **Hàng đợi** — `getEscalations()` (TanStack, refetch nút/định kỳ),
  **danh sách sắp theo priority** (badge màu theo priority/severity), mỗi mục hiện tóm tắt EscalationCard (intent,
  reason, tin khách). Chọn một mục → mở hội thoại (Phần B). Link "Admin" ở trang chủ.

**Verify:** mở `/admin` → thấy ca escalate, ưu tiên cao lên trước, card hiển thị. `pnpm -r build` pass. Commit:
`feat(ui): phase 2 - trang hàng đợi escalation admin`.

### === PHẦN B · 08c — TIẾP QUẢN + TRẢ LỜI TRỰC TIẾP (pub/sub in-process + status-gate) ===

### Phase 3 — Pub/sub hub + status-gating cho WS khách

- `app/api/ws/hub.py` (mới): `ConnectionHub` — `register(conv_id, ws)`/`unregister`; `publish(conv_id, payload,
exclude=ws)` gửi tới các WS khác cùng hội thoại (mỗi kết nối một `asyncio.Queue`). In-process, không Redis.
- `app/api/ws/chat.py` refactor (WS khách): đăng ký hub theo `db_conversation_id`; chạy **HAI task**
  `asyncio.gather`: (a) `_reader` đọc tin khách; (b) `_hub_listener` đọc từ hub → đẩy xuống socket khách.
  - `_reader`: **status-gate** — nạp `conversation.status`; nếu ∈ {IN_HUMAN_QUEUE, HUMAN_HANDLING,
    PENDING_APPROVAL} → **KHÔNG chạy AI**: lưu tin khách + `hub.publish(conv_id, {type:"message", from:"customer",
content})` (admin thấy). Ngược lại (ACTIVE_AI/REPLIED…) → chạy pipeline như cũ + trả lời + lưu.
  - `_hub_listener`: nhận payload (tin admin) → `websocket.send_json({type:"message", from:"admin", content})`.

**Verify:** khi status IN_HUMAN_QUEUE, gửi tin ở `/chat` → KHÔNG có reply AI (được publish lên hub thay vì chạy
pipeline). `make test` xanh. Commit: `feat(hitl): phase 3 - in-process pub/sub hub + status-gate WS khách`.

### Phase 4 — Admin WS + tiếp quản

- `app/api/ws/admin.py` (mới): `/ws/admin/{conversation_id}` — admin connect → gửi lịch sử hiện có; đăng ký hub
  theo conv_id; hai task tương tự (reader tin admin ↔ hub listener tin khách).
  - Takeover: khi admin connect (hoặc gửi `{type:"takeover"}`) → `set_status(HUMAN_HANDLING)` + `assigned_admin_id`
    (demo admin).
  - `_reader` admin: tin admin → lưu (sender=ADMIN) + `hub.publish(conv_id, {from:"admin", content})` (→ khách).
  - `_hub_listener`: tin khách (từ hub) → đẩy xuống socket admin.
- (Tùy chọn) `POST /api/admin/conversations/{id}/resolve` → `set_status(RESOLVED)`.

**Verify:** kịch bản: khách escalate → admin mở `/ws/admin/{id}`, takeover → gửi tin → **khách nhận tin admin
trực tiếp**; khách gửi lại → **admin nhận**. `make test` xanh. Commit: `feat(hitl): phase 4 - admin WS + takeover + live 2 chiều`.

### Phase 5 — FE màn admin tiếp quản

- `apps/dashboard/app/admin/[conversationId]/page.tsx` (hoặc panel trong `/admin`): mở hội thoại → hiện **lịch sử
  đầy đủ** (customer/ai/admin, phân biệt màu) + **EscalationCard** (context để admin nắm nhanh); kết nối
  `ws://.../ws/admin/{id}`; nút **"Tiếp quản"** → HUMAN_HANDLING; ô nhập → gửi tin (tới khách trực tiếp); nhận tin
  khách realtime. Tái dùng pattern chat sẵn có.

**Verify:** mở hai cửa sổ (khách `/chat` + admin `/admin/{id}`) → chat qua lại realtime sau khi admin tiếp quản.
`pnpm -r build` pass. Commit: `feat(ui): phase 5 - màn admin tiếp quản + chat realtime`.

### === PHẦN C · 08a — GATE + DUYỆT NHÁP (PENDING_APPROVAL) ===

### Phase 6 — Gate config + giữ nháp + duyệt/sửa/gửi

- `app/core/config.py`: `sensitive_intents` (mặc định `{refund, complaint, exchange}`) + `auto_reply_review: bool
= True` (env). (Tùy chọn: 1 dòng DB `GateConfig` + toggle — nếu không, dùng config.)
- `app/api/ws/chat.py` (nhánh AI-active, sau pipeline): nếu `action == auto_reply` **và** category/intent ∈
  sensitive **và** `auto_reply_review` → **KHÔNG gửi thẳng**: `set_status(PENDING_APPROVAL)` + `build/persist card`
  với `suggested_reply = <nháp Agent 4>` (vào hàng đợi). Ngược lại gửi như cũ. `human_handoff` LUÔN escalate (bất biến).
- `app/api/routes/admin.py`: `POST /conversations/{id}/approve` (body `{content?}`) → gửi `content` (nháp đã duyệt/
  sửa) tới khách qua `hub.publish` + lưu (sender=AI) + `set_status(REPLIED)`. `POST /conversations/{id}/reject` →
  chuyển `IN_HUMAN_QUEUE` (admin tự xử lý).

**Verify:** hỏi câu `refund` KB trả lời được → **KHÔNG gửi thẳng**, vào PENDING_APPROVAL với nháp; `approve` →
khách nhận nháp. `make test` xanh. Commit: `feat(hitl): phase 6 - gate sensitive → PENDING_APPROVAL + duyệt/sửa/gửi nháp`.

### Phase 7 — FE duyệt nháp

- `apps/dashboard/app/admin/[conversationId]/page.tsx`: nếu status `PENDING_APPROVAL` → hiện **nháp AI** + nút
  **Duyệt & gửi** / **Sửa & gửi** (textarea) / **Từ chối** (→ tiếp quản). (Tùy chọn) toggle gate ở trang admin.

**Verify:** ca PENDING_APPROVAL trên `/admin` → admin duyệt/sửa/gửi → khách nhận. `pnpm -r build` pass. Commit:
`feat(ui): phase 7 - duyệt/sửa/gửi nháp (PENDING_APPROVAL)`.

### Phase 8 — Test + e2e verify (vòng HITL trọn vẹn)

- Test: `build_escalation_card`/`list_escalations`; gate → PENDING_APPROVAL đúng; status-gate (human-handling →
  không chạy AI). e2e tay: (1) câu vô nghĩa → escalate → queue → admin takeover → chat realtime; (2) câu refund →
  PENDING_APPROVAL → admin duyệt/gửi.

**Verify:** `make test` xanh; `pnpm -r build` pass; hai kịch bản demo chạy. Commit: `test(hitl): phase 8 - e2e HITL loop`.

---

## 2. Definition of Done

- [ ] Escalate → conversation có priority/severity/escalation_card; `GET /api/admin/escalations` liệt kê **sắp theo priority**.
- [ ] `/admin`: hàng đợi hiện ca escalate + PENDING_APPROVAL (ưu tiên cao trước) + EscalationCard.
- [ ] **Admin tiếp quản + chat realtime 2 chiều** với khách (pub/sub in-process); khi có người xử lý, **AI KHÔNG chạy** (status-gate).
- [ ] Ca nhạy cảm (refund/complaint/exchange) → **PENDING_APPROVAL**, AI soạn nháp, admin **duyệt/sửa/gửi**; handoff luôn escalate.
- [ ] Response Generator vẫn là egress tự động duy nhất; tin admin qua hub. `make test` xanh; `pnpm -r build` pass.
- [ ] 1 worker; KHÔNG suspend/resume, KHÔNG Redis pub/sub, KHÔNG admin auth (đã note để dành 09b/11).

---

## 3. Ghi chú cho Claude Code

- **Pub/sub IN-PROCESS** (`hub.py`, 1 worker) — event-driven, KHÔNG polling; đằng sau interface nhỏ để sau swap
  Redis (đa-worker, PRD §10). ĐỪNG dựng Redis pub/sub ở đây.
- **WS khách + admin cần HAI task** (`asyncio.gather`: reader socket + hub listener) để nhận realtime từ phía kia;
  `hub.publish(..., exclude=self)` để không tự nghe lại tin mình.
- **Status-gate, KHÔNG suspend/resume:** human-handling → AI không chạy (chỉ định tuyến). LangGraph interrupt +
  durable checkpointer = 09b.
- **EscalationCard dựng từ final state** (không re-wire graph). `human_handoff.py` node cứ để nguyên (không dùng
  trong graph) — hoặc bỏ; KHÔNG bắt buộc.
- **Gate chỉ đổi DELIVERY** (auto_reply nhạy cảm → PENDING_APPROVAL giữ nháp); **handoff LUÔN escalate** (FR-GATE-2).
  Response Generator vẫn là egress tự động duy nhất.
- **Admin identity tối giản** (demo admin id) — admin auth/RBAC thật = slice 11. Guest khách = 11.
- Session DB NGẮN (Neon free); async-first; config từ env; UI theo pattern sẵn có (Tailwind + TanStack, KHÔNG shadcn);
  "sửa có phẫu thuật". Migration Alembic cho cột mới.
- **Đây là big plan** — chạy phase-by-phase, commit từng phase, dừng hỏi khi lỗi/mơ hồ. Sau đây (ROADMAP): 10a
  danh sách hội thoại → 10b/c monitoring/analytics → 11 auth → 09b suspend/resume + Redis pub/sub khi scale.
