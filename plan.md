# plan.md — Slice 11: Xác thực (Admin + Khách) · Mô hình hội thoại theo khách · Gate động · Kiện toàn màn Admin

> Repo: `github.com/trevor2903-kma/autonomous-customer-care-agents`
> BE: `apps/backend` (FastAPI + LangGraph, Alembic). FE: `apps/dashboard` (Next.js 14, Tailwind thuần + TanStack, **KHÔNG shadcn**).
> Nguyên tắc (CLAUDE.md): cấu hình đọc từ env, KHÔNG hardcode secret/URL/ngưỡng. Sửa **có phẫu thuật**, không đập lại kiến trúc.

---

## 0. Vì sao gộp 3 việc vào một slice (chúng bổ trợ nhau)

Ba việc bạn nêu **có chung một trục là xác thực (auth)**:

1. **Auth Admin + Khách** — nền móng. Admin cần JWT+RBAC để bảo vệ dashboard (thay `DEMO_ADMIN_ID`). Khách cần danh tính để (2) hoạt động.
2. **Mô hình hội thoại theo khách** — _phụ thuộc trực tiếp_ vào danh tính khách từ (1): phải biết "ca đang active của khách X" mới `tìm-ca-active-hoặc-mở-ca-mới`. Không có auth thì không làm được (WS hiện tạo conversation **mỗi kết nối** theo `sid` guest — comment trong code ghi thẳng _"tài khoản = slice 11"_).
3. **Gate động + kiện toàn nav (RAG vào trong, thêm tab Cấu hình Gate)** — đây là các tính năng **của Admin**, nằm _sau_ lớp auth admin ở (1). Chuyển toggle gate từ env → DB + endpoint admin, và tổ chức lại điều hướng màn admin.

→ Làm cùng slice để chỉ dựng hạ tầng auth **một lần**, rồi mọi thứ (mô hình hội thoại, bảo vệ gate/RAG) gắn lên đó. Slice **lớn** nhưng chia **7 pha (P0–P6)**; Claude Code chạy **tuần tự, commit từng pha**, có thể dừng/nghỉ giữa chừng.

---

## 1. Bất biến kiến trúc (KHÔNG được phá)

- Pipeline 4 agent cố định, **không Supervisor**. Grounding: không bịa → chuyển người. **Agent 4 là egress DUY NHẤT của luồng tự động** (tin admin = egress người, qua hub — vẫn tách biệt).
- **1 worker**; hub pub/sub **in-process** (không Redis). Không đổi ở slice này.
- **Agent 3 tất định** (không LLM). **Escalation an toàn theo blocking flags LUÔN bật, KHÔNG toggle được** — Gate chỉ chỉnh _mức độ tự động cho ca AI tự tin_, **không** ghi đè escalation an toàn (đúng như intro trong design: "Ca có cờ bất định luôn được chuyển nhân viên").
- **Bộ nhớ theo ca** (`_load_history` theo `conversation_id`) — giữ nguyên. Ca đã đóng KHÔNG vào ngữ cảnh ca mới.
- Không blend confidence (route theo flags). Giữ nguyên slice này; slider ngưỡng confidence chỉ **read-only** (KHÔNG đổi hành vi Agent 2 — xem P3).

---

## 2. Design tokens (nhúng sẵn — Claude Code KHÔNG đọc được file upload)

> **Trước khi làm FE:** copy file design vào repo để tham chiếu: `apps/dashboard/docs/design/ThriftYourStyle_CSKH.dc.html`. Các token dưới là bản tóm tắt đủ để dựng, khớp `globals.css` hiện có.

**Font (đã thay cho tiếng Việt):** heading/brand = **Playfair Display**; body/UI = **Be Vietnam Pro** (design gốc dùng Instrument Serif/Sans — không có subset tiếng Việt). Màn login dùng đúng bộ này.

**Bảng màu (thrift ấm):** nền `#FBFAF7`; listpane `#FDFCFA`; card `#FFFFFF`; chữ `#211F1B`/`#57534A`/`#8E887B`/`#B0A99B`/`#C4BEB1`; viền `#E7E2D8`/`#F0EDE6`/`#DDE1D0`/`#E0DBCF`; **olive chính `#6B7A4F`**, hover `#5A6743`; xanh nhạt `#EEF0E6` (avatar AI/chip tri thức), viền xanh `#DDE1D0`; bong bóng khách `#211F1B` + chữ `#F7F5F0`; bong bóng AI trắng + `#E7E2D8`; nhân viên (NV) xám-xanh `#42536B`/`#5A6B84`/`#E8ECF3`/`#D4DAE6`; handoff/hệ thống terracotta `#F6E7DF`/`#EAD4C7`/`#8A4E33`; badge cảnh báo/đếm `#B25B3C`; amber "duyệt/cần làm rõ" `#B98534`/`#F7EFDD`; chấm online `#5B7A5B`.

**Bo góc / bóng:** card 11–14px, nút 6–9px, bong bóng 16px (đuôi 5px), pill 6–7px. Bóng `0 2px 8–10px rgba(33,31,27,.03–.04)`.

**Toggle switch (dùng ở Gate):** hệ thống 48×27px, per-intent 44×25px; bo 13–14; **BẬT** nền olive `#6B7A4F` núm phải; **TẮT** nền `#DAD5C8` núm trái; núm trắng 21/19px.

---

## 3. Mô hình dữ liệu mới (P0)

### 3.1 Bảng `user` (chung admin + khách, RBAC theo role)

| cột           | kiểu                     | ghi chú                                                |
| ------------- | ------------------------ | ------------------------------------------------------ |
| id            | UUID PK                  |                                                        |
| email         | citext/str UNIQUE        | định danh đăng nhập                                    |
| password_hash | str                      | bcrypt (passlib)                                       |
| role          | enum `admin`\|`customer` | RBAC                                                   |
| display_name  | str                      | tên hiển thị (admin UI: "Ngọc Trần"; khách: tên khách) |
| created_at    | ts                       |                                                        |

- Seed **1 admin** (email/mật khẩu lấy từ env, KHÔNG hardcode — **stop-point**).

### 3.2 `conversation` — thêm liên kết khách

- Thêm `customer_id UUID FK → user(id) NULL` (NULL cho guest/legacy). Giữ `customer_identifier` (string) để hiển thị (điền email hoặc display_name).

### 3.3 `gate_config` (DB thay env) — khớp UI design

Một bản ghi cấu hình toàn cục (singleton) + bảng luật per-intent:

**`gate_config`** (1 dòng):
| cột | kiểu | mặc định (seed từ env hiện tại) |
|---|---|---|
| id | int PK (=1) | |
| auto_reply_enabled | bool | `true` (master) |
| auto_resolve_enabled | bool | `true` (vì `auto_resolve_minutes` đang có) |
| auto_resolve_minutes | int | `30` |
| retrieval_threshold | float | `0.35` (chỉ để **hiển thị read-only** slice này; Agent 2 vẫn đọc env — xem P3) |

**`gate_intent_rule`** (10 dòng, PK=intent):
| intent | label | nhạy cảm (tag) | send_directly (mặc định) |
|---|---|---|---|
| product_price | Giá sản phẩm | – | **true** (Gửi thẳng) |
| product_information | Thông tin sản phẩm | – | true |
| size_consulting | Tư vấn size | – | true |
| shipping | Vận chuyển | – | true |
| order_status | Trạng thái đơn | – | true |
| promotion | Khuyến mãi | – | true |
| refund | Hoàn tiền | ✓ | **false** (Duyệt nháp) |
| exchange | Đổi hàng | ✓ | false |
| complaint | Khiếu nại | ✓ | false |
| other | Khác | – | false |

> **Ý nghĩa `send_directly`:** `true` = "Gửi thẳng"; `false` = "Duyệt nháp" (giữ nháp `PENDING_APPROVAL`). Đây là bản tổng quát hoá của `sensitive_intents` cũ (intent nhạy cảm = `send_directly=false`). Cột `nhạy cảm` chỉ để hiển thị tag, không chi phối logic.

- **Migration Alembic**: tạo `user`, `gate_config`, `gate_intent_rule`; thêm cột `conversation.customer_id`. Kèm **data migration seed** `gate_config` + 10 `gate_intent_rule` theo bảng trên. (Admin seed nằm ở script riêng/stop-point, không nhét secret vào migration.)

---

## 4. Ánh xạ ngữ nghĩa Gate (giữ nhất quán với câu chuyện an toàn)

**Gate động chỉ chi phối nhánh auto_reply (status `REPLIED`).** Escalation an toàn của Agent 3 (blocking flags → `human_handoff`) **không đổi, không toggle**.

`gate_holds(status_out, intent)` (đọc DB thay env):

```
if status_out != REPLIED: return False
cfg = get_gate_config()          # cache nhẹ, đọc DB
if not cfg.auto_reply_enabled:   # master TẮT → giữ nháp TẤT CẢ auto_reply
    return True
return not rule(intent).send_directly   # per-intent: giữ nếu không "gửi thẳng"
```

Tương thích logic cũ:

- `auto_reply_review=True` + tập nhạy cảm ≈ `auto_reply_enabled=True` + (intent nhạy cảm có `send_directly=false`).
- `auto_reply_review=False` (gửi hết) ≈ mọi intent `send_directly=true`.
- **Năng lực mới:** master TẮT = giữ nháp toàn bộ (chế độ chặt hơn mà toggle hệ thống của design mở ra).

`auto_resolve`: đọc `auto_resolve_enabled` + `auto_resolve_minutes` từ DB.

**Slider "Ngưỡng confidence chuyển người" (0.70) — HOÃN slice này (chỉ read-only):**

- Slider này _bản chất khác_ hai toggle trên: nó chỉnh **độ nhạy escalation an toàn**, ánh xạ vào `retrieval_threshold` mà **Agent 2** dùng để đặt cờ `low_retrieval_score` (Agent 3 coi là blocking → `human_handoff`). Vì là thay đổi _hành vi Agent 2_ (cần test kỹ trên KB), **hoãn wiring sang slice sau (P3-b)**.
- **Slice này:** slider **CHỈ read-only** — hiển thị `gate_config.retrieval_threshold` (đọc qua `GET /admin/gate-config`), **KHÔNG cho chỉnh**. `PUT /admin/gate-config` **KHÔNG nhận** `retrieval_threshold`. **Agent 2 GIỮ NGUYÊN đọc env** (không đọc DB). Ghi chú UI: "điều chỉnh ở phiên bản sau".
- Ghi rõ trong báo cáo: slider = tinh chỉnh escalation an toàn, **không phải** "van giám sát" của auto_reply; hiện chỉ hiển thị.

---

## 5. Các pha (P0–P6) — Claude Code chạy tuần tự, commit từng pha

### P0 — Data model + migration `feat(auth): P0 data model + migrations`

- **In:** models `User`/`GateConfig`/`GateIntentRule`; cột `conversation.customer_id`; migration Alembic + seed gate; script seed admin (đọc env). Thêm deps `passlib[bcrypt]` + `python-jose[cryptography]` (hoặc `pyjwt`) vào `pyproject.toml`.
- **Out:** logic auth/route (P1+).
- **Verify:** `alembic upgrade head` chạy sạch; bảng + seed 10 intent rule + gate_config tồn tại; `alembic downgrade -1` OK.
- **Stop-point:** báo user (a) `.env` thêm `JWT_SECRET`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`; (b) chạy migration + script seed admin.

### P1 — Auth backend `feat(auth): P1 jwt login/rbac + protect admin + ws token`

- **In:**
  - `core/security.py`: hash/verify mật khẩu (passlib bcrypt), issue/verify JWT (sub=user_id, role, exp). `core/config.py` thêm `jwt_secret`, `jwt_expire_minutes`.
  - `POST /api/auth/register` (role=customer), `POST /api/auth/login` (trả JWT + role + display_name), `GET /api/auth/me`.
  - Dependency `get_current_user` (Bearer) + `require_admin` (RBAC role=admin).
  - Bảo vệ toàn bộ `/api/admin/*` bằng `require_admin`; **thay `DEMO_ADMIN_ID`** bằng `current_user.id` (takeover/assign dùng admin đã đăng nhập).
  - **JWT-over-WS**: `/ws/chat?token=` (khách) + `/ws/admin/{id}?token=` (admin) — xác thực khi `accept()`, sai/không đúng role → đóng (code 4401). (Browser không set được header WS → buộc dùng query-param.)
- **Out:** mô hình hội thoại (P2), gate DB (P3).
- **Verify:** login admin/khách trả token; `/api/admin/escalations` không token → 401, có token admin → 200, token khách → 403; WS thiếu/sai token → đóng.

### P2 — Mô hình hội thoại theo khách `feat(chat): P2 per-customer find-active-or-open-case`

- **In:**
  - `conversation_service`: `get_active_conversation_for_customer(customer_id)` (status ∉ {RESOLVED, CLOSED}) + `open_case_for_customer(customer_id, display)` (conversation mới `ACTIVE_AI`, gắn `customer_id` + `customer_identifier`).
  - **Sửa `ws/chat.py`**: lấy `customer_id` từ token (thay `sid` guest) → **tìm-ca-active-hoặc-mở-ca-mới** → route theo status (`should_run_ai` giữ nguyên). Bỏ `create_conversation` mỗi kết nối.
    - Ca active `ACTIVE_AI` → agent chạy pipeline. Ca đang người xử lý (IN_HUMAN_QUEUE/HUMAN_HANDLING/PENDING_APPROVAL) → route admin (AI tạm dừng). Khi ca đóng giữa các lượt → tin kế tiếp **mở ca mới** (agent chạy lại từ đầu — AI-first).
  - `GET /api/me/thread`: trả **mạch ghép** (mọi conversation của khách đã đăng nhập, message xếp theo `created_at` xuyên ca, ca cũ trước → ca mới sau) cho UX "một đoạn liền mạch". Admin **không đổi** (vẫn thấy các ca riêng biệt).
- **Bất biến:** bộ nhớ agent vẫn **theo ca** (`_load_history` theo `conversation_id`) — ca cũ không vào ngữ cảnh ca mới.
- **Verify:** khách A đăng nhập, chat → 1 conversation `ACTIVE_AI`; admin đóng ca (RESOLVED) → khách A nhắn tiếp → **conversation MỚI** `ACTIVE_AI`, agent chạy lại; `GET /me/thread` trả cả 2 ca ghép liền.

### P3 — Gate động (DB) `feat(gate): P3 db-backed gate config + admin toggle`

- **In:**
  - `gate_service`: `get_gate_config()` (đọc `gate_config` + `gate_intent_rule`, cache nhẹ theo request/ttl), `update_gate_config(...)`.
  - **Refactor `gate_holds`** (ở `ws/chat.py`) đọc DB theo §4 (master + per-intent). Auto-resolve đọc `auto_resolve_enabled`/`minutes` từ DB.
  - `GET /api/admin/gate-config` + `PUT /api/admin/gate-config` (`require_admin`): trả/cập nhật toggle hệ thống + bảng per-intent.
  - **Giữ nguyên** escalation an toàn Agent 3 (blocking flags) — KHÔNG đọc gate, KHÔNG toggle.
  - **`GET /admin/gate-config` trả kèm `retrieval_threshold`** (chỉ để FE hiển thị read-only). **`PUT` KHÔNG nhận `retrieval_threshold`.**
  - **P3-b (HOÃN sang slice sau — KHÔNG làm bây giờ):** wiring slider → **Agent 2** đọc `gate_config.retrieval_threshold` thay hằng env + mở cho chỉnh. Slice này **Agent 2 GIỮ NGUYÊN** đọc env; slider FE read-only.
- **Verify:** PUT tắt `auto_reply_enabled` → mọi auto_reply (kể cả intent `send_directly=true`) chuyển `PENDING_APPROVAL`; bật lại + set `refund.send_directly=true` → refund auto_reply gửi thẳng; blocking-flag case vẫn `human_handoff` bất kể gate.

### P4 — FE Auth: màn login + điều hướng + gắn token `feat(fe-auth): P4 login screens + redirect + token plumbing`

- **In:**
  - **Màn `/login`** (design KHÔNG có → thiết kế mới theo §2): card giữa (max ~420px), brand ("T" vuông serif tối + "ThriftYourStyle" serif), heading serif, ô email + mật khẩu (trắng, viền `#E7E2D8`, bo 10–12), nút "Đăng nhập" olive `#6B7A4F`; link "Tạo tài khoản" (khách). Cho phép 2 chế độ: **Khách** (đăng nhập/đăng ký) + **Admin** (đăng nhập) — dạng tab hoặc 2 link. Footer nhẹ. Bám palette ấm.
  - `AuthContext`/hook: lưu JWT (in-memory + cookie/localStorage tuỳ chuẩn dự án), `login/register/logout`, `me`.
  - **`lib/api.ts`**: gắn `Authorization: Bearer` cho mọi fetch; helper WS URL kèm `?token=` cho `/ws/chat` và `adminWsUrl(id)`.
  - **Guard**: `/admin/*` yêu cầu role admin; `/chat` yêu cầu khách đăng nhập; thiếu token → redirect `/login`. Sau login: admin → `/admin`, khách → `/chat`. Nút Đăng xuất.
  - Thay cái toggle harness "Khách/Admin" ở TopBar (chỉ để demo) bằng trạng thái đăng nhập thực (hiện tên + Đăng xuất).
- **Out:** không đụng logic pipeline.
- **Verify:** đăng nhập admin → vào `/admin`; đăng nhập/đăng ký khách → vào `/chat`; vào thẳng `/admin` khi chưa đăng nhập → về `/login`; WS gửi kèm token OK.

### P5 — FE Admin: RAG vào nav + tab Cấu hình Gate `feat(fe-admin): P5 rag-in-nav + gate config tab`

- **In:**
  - **Chuyển RAG** từ route riêng `apps/dashboard/app/rag/page.tsx` **vào cụm nav** trong `components/shell/AdminShell.tsx` như một module. **Thứ tự nav (5):** `Hội thoại / Hàng đợi chuyển tiếp (count) / Duyệt nháp (count) / Quản lý tri thức / Cấu hình Gate`. Item active: nền `#F4F2EC` + ô vuông olive `#6B7A4F`; inactive: trong suốt + ô vuông `#DAD5C8`.
  - **Tab "Cấu hình Gate"** (module mới) theo design:
    - Tiêu đề serif 27 "Cấu hình Gate" + intro: _"Gate chỉ điều chỉnh mức độ tự động cho ca AI tự tin. Ca có cờ bất định luôn được chuyển nhân viên — an toàn không bị gate ghi đè."_
    - 2 hàng toggle hệ thống (card, label + mô tả + switch 48×27): **Auto-reply (toàn hệ thống)**, **Auto-resolve**.
    - Bảng **"Auto-reply theo intent / category"** (10 dòng, §3.3): label + intent (mono) + tag "nhạy cảm" (terracotta `#B25B3C`/`#F6E7DF`) nếu có + switch 44×25 với nhãn **"Gửi thẳng"** (olive) / **"Duyệt nháp"** (amber `#B98534`).
    - Card slider **"Ngưỡng confidence chuyển người"** — **READ-ONLY** (không kéo được, không PUT): giá trị mono `#6B7A4F` lấy từ `gate_config.retrieval_threshold`, track `#EFEBE2` fill olive (disabled), ghi chú "Dưới ngưỡng → Decision Engine đặt action = human_handoff · điều chỉnh ở phiên bản sau."
  - Nối GET/PUT `/api/admin/gate-config` (TanStack query + mutation; optimistic tuỳ chọn).
- **Out:** không đổi backend.
- **Verify:** nav 5 mục đúng thứ tự, RAG mở trong khung admin (không còn route ngoài); tab Gate hiển thị đúng seed (6 ON, refund/exchange/complaint/other OFF); bật/tắt toggle → PUT thành công → reload giữ trạng thái.

### P6 — FE Khách: mạch ghép + kiểm thử đầu-cuối `feat(fe-chat): P6 stitched thread + e2e`

- **In:**
  - **`/chat`**: nạp `GET /api/me/thread` (mạch ghép của khách đã đăng nhập) render **một đoạn liền mạch**; tin mới gửi qua WS `?token=` vào ca active. Header hiển thị `custStatus` theo ca active.
  - Kiểm thử đầu-cuối: đăng nhập khách → chat (AI trả lời) → tình huống escalate → đăng nhập admin → nhận ca (takeover) → trả lời → đóng ca → khách quay lại nhắn tiếp → **ca mới, AI chạy lại từ đầu**; mạch khách vẫn thấy liền.
- **Verify:** kịch bản đầu-cuối chạy trơn trên 1 worker; khách thấy 1 thread liền, admin thấy các ca riêng.

---

## 6. Ghi chú cho Claude Code

- Đọc `apps/backend/CLAUDE.md` trước. Cấu hình từ env; **KHÔNG hardcode** secret/URL/ngưỡng.
- **Copy file design** vào `apps/dashboard/docs/design/ThriftYourStyle_CSKH.dc.html` để tham chiếu (token đã tóm tắt ở §2; design KHÔNG có màn login → thiết kế mới theo §4/P4).
- FE: **Tailwind thuần + TanStack, KHÔNG shadcn**. Sửa có phẫu thuật.
- **Không phá bất biến §1**: pipeline cố định/không Supervisor; Agent 4 egress duy nhất luồng auto; grounding không bịa→handoff; 1 worker + hub in-process; Agent 3 tất định; escalation an toàn luôn bật & KHÔNG toggle; bộ nhớ theo ca; không blend confidence.
- **Gate = van cho auto_reply**, KHÔNG phải escalation an toàn (§4). Slider = độ nhạy escalation → **HOÃN slice này, chỉ read-only** (Agent 2 giữ env, PUT không nhận `retrieval_threshold`).
- Commit **từng pha** với prefix ở tiêu đề mỗi pha. Có thể dừng/nghỉ giữa các pha.
- **Stop-point bắt buộc** (dừng, hỏi user): (a) trước migration/seed (P0) để user set `.env` `JWT_SECRET`/`ADMIN_EMAIL`/`ADMIN_PASSWORD` và chạy `alembic upgrade head` + seed admin; (b) khi cần biến môi trường mới cho FE (`NEXT_PUBLIC_*`) nếu phát sinh.
- Sau mỗi pha: chạy **Verify** tương ứng, tóm tắt thay đổi ngắn gọn.

---

## 7. Phạm vi & không-phạm-vi

- **Trong:** auth admin+khách (JWT+RBAC, login+điều hướng, token-qua-WS); mô hình hội thoại theo khách (find-active-or-open-case + mạch ghép `/me/thread`); gate động DB + toggle admin; RAG vào nav + tab Cấu hình Gate; màn login mới.
- **Ngoài (slice sau):** **P3-b** — wiring slider ngưỡng confidence (Agent 2 đọc `gate_config.retrieval_threshold` + mở cho chỉnh; slice này chỉ read-only); ngữ cảnh **xuyên ca** cho agent (khách quen/đơn cũ) — cross-conversation memory (§22/17); tích hợp đơn hàng (16); observability Langfuse (12); anti-injection (13); deploy nhiều worker (khi lên Redis pub/sub + durable checkpointer 09b); dashboard giám sát/KPI (10b/c).
