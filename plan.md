# BIG PLAN — Fix 08c + Slice 10a (Conversation List) + UI Redesign (ThriftYourStyle)

> **Bản chất:** kịch bản ONE-SHOT LỚN — chạy phase-by-phase, có thể dừng/tiếp. Ba việc: **(A) fix bug 08c**
> (takeover-on-view) + polish `{type:pending}`; **(B) slice 10a** (danh sách hội thoại + bộ lọc); **(C) redesign
> UI** cho khách + admin theo bản **ThriftYourStyle**, có responsive/mobile. Nguồn chân lý: `PRD.md` + **file
> design** `ThriftYourStyle_CSKH.dc.html`.
>
> **QUAN TRỌNG:** đặt file design vào repo (vd `docs/design/ThriftYourStyle.dc.html`) để Claude Code **đọc trực
> tiếp lấy chi tiết pixel** (màu/spacing/bố cục từng màn). Bảng token dưới đây là bản tóm tắt để bám nhanh.
>
> Ràng buộc UI: **Tailwind thuần + TanStack Query, KHÔNG shadcn**. Giữ **khách `/chat`** và **admin `/admin`** là
> hai URL riêng (toggle Khách/Admin trong design chỉ là công cụ mockup — khách KHÔNG thấy admin).

---

## 0. DESIGN SYSTEM (tóm tắt — chi tiết xem file HTML)

**Fonts (Google Fonts):** `Instrument Serif` (display/heading/brand, có italic) · `Instrument Sans` (400/500/600, body/UI).

**Màu (tông kem · olive · terracotta):**

- Nền: page `#FBFAF7` · panel/list `#FDFCFA` · card/white `#FFFFFF`.
- Chữ: `#211F1B` (chính) · `#57534A` (phụ) · `#8E887B` (mờ) · `#B0A99B` · `#C4BEB1`.
- Viền: `#E7E2D8` (mặc định) · `#DDE1D0` (xanh nhạt) · `#F0EDE6` (nhạt).
- **Primary olive:** `#6B7A4F` (nút Gửi/link) · hover `#5A6743` · soft `#EEF0E6` (avatar AI, chip tri thức) · border `#DDE1D0`.
- Bong bóng khách: nền `#211F1B`, chữ `#F7F5F0`. Bong bóng AI: nền `#FFFFFF`, viền `#E7E2D8`.
- Nhân viên (NV): chữ `#42536B`/`#5A6B84`, nền `#E8ECF3`, viền `#D4DAE6`.
- Thông báo chuyển người / system: nền `#F6E7DF`, viền `#EAD4C7`, chữ `#8A4E33` (căn giữa).
- Badge đếm/alert: `#B25B3C`. "Cần làm rõ"/amber: chữ `#B98534`, nền `#F7EFDD`. Chấm online: `#5B7A5B`.

**Map status → {nhãn, màu, nền}** (dùng cho pill khắp admin + custStatus):
| status | nhãn | color | soft |
|---|---|---|---|
| ACTIVE_AI | AI đang xử lý | #6B7A4F | #EEF0E6 |
| REPLIED | Đã trả lời | #5B7A5B | #E8EFE6 |
| PENDING_APPROVAL | Chờ duyệt nháp | #B98534 | #F7EFDD |
| IN_HUMAN_QUEUE | Chờ nhận ca | #B25B3C | #F6E7DF |
| HUMAN_HANDLING | Nhân viên đang xử lý | #5A6B84 | #E8ECF3 |
| RESOLVED | Đã đóng | #8E887B | #F0EDE6 |

**Bo góc:** card 11–14px · nút 6–9px · bong bóng 16px (góc "đuôi" 5px: khách `16px 16px 5px 16px`, AI/NV
`5px 16px 16px 16px`) · pill 6–7px · badge 10px. **Shadow:** `0 2px 8–10px rgba(33,31,27,.03–.04)`.

**Bố cục:** top bar 53px (trắng, viền dưới `#E7E2D8`). Admin: sidebar 250px + listpane 340px + detailpane (flex).
**Responsive ≤820px:** sidebar → **drawer** (translateX + scrim + hamburger topbar `mtopbar`); listpane full-width;
detailpane ẩn (điều hướng master-detail).

---

## 1. Kế hoạch theo Phase

> Mỗi phase: `pnpm -r build` (và `make test` nếu chạm BE) XANH → `git commit` → tóm tắt 1 dòng → tiếp nếu không lỗi.

### Phase 0 — Nền design (fonts + tokens)

- `apps/dashboard/app/layout.tsx`: nạp **Instrument Serif + Instrument Sans** (next/font/google hoặc `<link>`).
- `apps/dashboard/app/globals.css`: khai báo **CSS variables** cho toàn bộ token màu ở trên (vd `--bg-page`,
  `--primary`, `--text-muted`, …) + font families; tiện ích nhỏ (bong bóng, pill, shadow) nếu cần. (Có thể map vào
  `tailwind.config` theme, hoặc dùng CSS vars trực tiếp — tuỳ pattern hiện có.)

**Verify:** app build; trang bất kỳ đổi font/nền sang tông ThriftYourStyle. Commit: `feat(ui): phase 0 - design tokens (Instrument fonts + bảng màu ThriftYourStyle)`.

### Phase 1 — App shell (top bar + admin sidebar + responsive)

- **Top bar** (dùng chung): brand "T" (ô vuông `#211F1B`, chữ serif) + "ThriftYourStyle" (serif) + tag "Demo" +
  bên phải "Pipeline 4 agent · HITL". (Khách và admin dùng biến thể phù hợp; KHÔNG lộ nav admin cho khách.)
- **Admin layout** (`apps/dashboard/app/admin/layout.tsx` hoặc shell component): **sidebar 250px** (brand + "Bảng
  điều hành CSKH" + nav: **Hội thoại** / **Chuyển nhân viên** (badge đếm IN_HUMAN_QUEUE) / **Duyệt nháp** (badge
  PENDING_APPROVAL) / **Kho tri thức (RAG)** + user profile "NG · Đang trực tuyến") + **responsive drawer** (≤820px:
  off-canvas + scrim + `mtopbar` hamburger + module title).

**Verify:** `/admin` có sidebar đúng style; thu nhỏ <820px → sidebar thành drawer mở/đóng bằng hamburger.
Commit: `feat(ui): phase 1 - app shell (top bar + admin sidebar + drawer responsive)`.

### Phase 2 — Redesign màn khách `/chat` (+ polish pending)

- `apps/dashboard/app/chat/page.tsx` + `components/chat/*`: dựng lại theo design —
  - Header: avatar "T" + "Trợ lý ThriftYourStyle" (serif) + **custStatus** (chấm màu + nhãn theo trạng thái:
    "Đang trò chuyện với Trợ lý AI"/#6B7A4F, "Đang chờ nhân viên hỗ trợ"/#B25B3C, "… (CSKH) đang hỗ trợ bạn"/#5A6B84).
  - **Quick-reply chips** (pill đậm primary / pill trắng). Bong bóng: **khách** (nền đậm, phải), **AI** (trắng +
    avatar "AI", trái) kèm chip **"Căn cứ tri thức"** (nguồn, monospace) + tag **"Cần làm rõ · hỏi lại 1 lần"** (amber);
    **NV** (avatar "NV" xanh-xám); **thông báo chuyển người/system** (căn giữa, terracotta). **Typing** 3 chấm nhấp nháy.
  - Ô nhập trắng bo tròn + nút **"Gửi"** olive. Footer: "Trợ lý AI trả lời dựa trên tài liệu chính thức của shop ·
    phản hồi tự động ≤ 5 giây".
  - **Polish (fix):** xử lý `{type:"pending"}` — gỡ typing + hiện trạng thái "Trợ lý AI cần thêm thông tin"/chờ duyệt
    (đúng lúc ca vào PENDING_APPROVAL), KHÔNG kẹt "đang trả lời…".

**Verify:** `/chat` đúng giao diện design; chat happy case + ca chuyển người + (nếu test) ca pending hiển thị đúng.
`pnpm -r build` pass. Commit: `feat(ui): phase 2 - redesign màn khách + xử lý pending`.

### Phase 3 — Backend: 10a (list + filter) + FIX bug 08c

- **10a:** `app/api/routes/admin.py` — `GET /admin/conversations?status=<optional>&limit=` → dùng
  `conversation_service.list_conversations` (thêm tham số lọc theo status/nhóm nếu chưa có). Trả `{id, customer_identifier,
status, current_intent, last_message_at, preview}` (preview = tin cuối). Schema + `lib/api.ts:getConversations(filter)`.
- **FIX 08c:** `app/api/ws/admin.py` — **BỎ `_takeover()` khỏi lúc connect** (mở kết nối = chỉ xem, KHÔNG đổi
  status). Thêm **tiếp quản tường minh**: `POST /admin/conversations/{id}/takeover` (IN_HUMAN_QUEUE → HUMAN_HANDLING
  - assigned_admin) **hoặc** WS `{type:"takeover"}` trong `_admin_reader`. `lib/api.ts:takeover(id)`.

**Verify:** mở admin WS KHÔNG còn tự đổi status (ca vẫn ở IN_HUMAN_QUEUE trong hàng đợi); `GET /admin/conversations?status=`
lọc đúng. `make test` xanh. Commit: `feat(hitl): phase 3 - conversation list endpoint (10a) + fix takeover-on-view (08c)`.

### Phase 4 — Admin: Danh sách hội thoại (10a) theo design

- `apps/dashboard/app/admin/page.tsx` (hoặc module "Hội thoại"): **listpane** —
  - Tiêu đề "Hội thoại" (serif 24px) + ô **search** "Tìm theo tên khách, mã đơn…".
  - **Filter chips** (pill đậm active / trắng inactive): vd **Tất cả · Đang xử lý (AI) · Cần xử lý · Đã đóng**
    (map nhóm: active=[ACTIVE_AI,REPLIED,AWAITING_CUSTOMER]; cần-xử-lý=[IN_HUMAN_QUEUE,PENDING_APPROVAL,HUMAN_HANDLING];
    đóng=[RESOLVED,CLOSED]).
  - **Conversation cards:** tên/định danh khách + time + **preview** (ellipsis 1 dòng) + **status pill** (chấm màu +
    nhãn theo bảng map). Chọn card → mở detail (Phase 5). Dùng `getConversations(filter)` (TanStack).

**Verify:** `/admin` hiện danh sách tất cả hội thoại + lọc theo chip + pill đúng màu. `pnpm -r build` pass.
Commit: `feat(ui): phase 4 - danh sách hội thoại + bộ lọc (10a) theo design`.

### Phase 5 — Admin: Detail (tiếp quản + hàng đợi + duyệt nháp) theo design + hoàn tất fix

- `apps/dashboard/app/admin/[conversationId]/page.tsx` (detailpane) — theo design:
  - **Lịch sử** hội thoại (khách/AI/NV/system, đúng bong bóng + màu) qua `getAdminConversation(id)` (đọc-only) + WS
    `/ws/admin/{id}` cho tin realtime mới.
  - **EscalationCard** (khi IN_HUMAN_QUEUE): tên + định danh (mono) + pill **"Ưu tiên {priority}"** (màu) + **"Mức độ
    {severity}"** (xám) + hộp **lý do** (terracotta) + **intent** + **flags** + **"Nháp phản hồi gợi ý"** (nếu có).
  - **Điều khiển (fix 08c):** nút **"Tiếp quản"** tường minh → `takeover(id)` (IN_HUMAN_QUEUE→HUMAN_HANDLING); ô trả
    lời + nút **Gửi** (bật sau khi tiếp quản, hoặc gửi tự tiếp quản); nút **"Đóng ca"** → `resolve(id)`.
  - **Duyệt nháp (PENDING_APPROVAL):** khối "Duyệt nháp phản hồi" (serif) + "Căn cứ" (nguồn) + nút **"Duyệt & gửi"**
    (olive) / **"Sửa & gửi"** (trắng, textarea) / **"Chuyển xử lý tay"** → `approveDraft`/`rejectDraft`.

**Verify:** mở một ca IN_HUMAN_QUEUE **chỉ xem** (không tự rời hàng đợi) → bấm **Tiếp quản** → chat realtime với khách →
**Đóng ca**; ca PENDING_APPROVAL → duyệt/sửa/gửi. `pnpm -r build` + `make test` pass. Commit:
`feat(ui): phase 5 - detail admin (tiếp quản + EscalationCard + duyệt nháp) + explicit takeover`.

### Phase 6 — Responsive/mobile + e2e verify

- ≤820px: sidebar → drawer (scrim + hamburger); top bar gọn (ẩn tag + phải); listpane full-width; **detailpane ẩn**
  → chọn hội thoại mới hiện detail (nút "‹ Hàng đợi"/"‹ Danh sách" quay lại). Màn khách `/chat` co gọn đúng design.
- **e2e:** (1) khách happy case; (2) escalate → hàng đợi → **xem không rời queue** → Tiếp quản → chat realtime →
  Đóng ca; (3) refund → PENDING_APPROVAL → duyệt/gửi; (4) danh sách + lọc; (5) toàn bộ trên mobile.

**Verify:** `make test` + `pnpm -r build` pass; các flow chạy trên cả desktop + mobile. Commit: `feat(ui): phase 6 - responsive mobile + e2e verify`.

---

## 2. Definition of Done

- [ ] **Fix 08c:** mở hội thoại = **chỉ xem** (không tự đổi status/rời hàng đợi); tiếp quản là **nút tường minh**;
      khách xử lý `{type:pending}` đúng.
- [ ] **10a:** `/admin` có **danh sách tất cả hội thoại** + search + **bộ lọc theo trạng thái** + status pill đúng màu.
- [ ] **Redesign:** khách `/chat` + admin (sidebar/list/detail) đúng hệ thị giác ThriftYourStyle (fonts, màu, bong
      bóng, EscalationCard, duyệt nháp); **responsive mobile** (drawer + master-detail).
- [ ] Giữ khách/admin tách URL; Tailwind thuần + TanStack, KHÔNG shadcn. `make test` + `pnpm -r build` XANH.

---

## 3. Ghi chú cho Claude Code

- **Đọc file design trong repo** (`docs/design/ThriftYourStyle.dc.html`) để lấy pixel/màu/bố cục chính xác từng màn;
  bảng token ở Phase 0 là tóm tắt. Design dùng inline style + `{{ }}`/`<sc-if>` (mockup) — **dịch sang Tailwind
  thuần**, KHÔNG bê nguyên template.
- **Tách khách/admin:** `/chat` (khách) và `/admin` (admin) là URL riêng; toggle Khách/Admin trong design chỉ để
  demo — KHÔNG cho khách vào admin.
- **Fix 08c là bắt buộc:** bỏ `_takeover` on-connect; thêm takeover tường minh. Xem là đọc-only (ca escalate vốn đã
  IN_HUMAN_QUEUE nên AI đã bị status-gate tạm dừng — xem không cần đổi status).
- **10a** dùng `list_conversations` (đã có) + tham số lọc; status pill dùng bảng map ở Phase 0.
- **Không đổi logic BE khác** (pipeline/gate/hub giữ nguyên) — chỉ thêm endpoint list + takeover + sửa on-connect.
  Async-first; session DB ngắn; "sửa có phẫu thuật".
- **Rebrand "ThriftYourStyle"** ở UI (brand/label). (Tuỳ chọn, không bắt buộc ở slice này: đổi nội dung KB/intents
  cho khớp tên shop — báo tôi nếu muốn làm.)
- **Big plan** — chạy phase-by-phase, commit từng phase, dừng hỏi khi lỗi/mơ hồ. Sau đây (ROADMAP): persist
  audit_log → 10b/c monitoring/analytics (KPI) → 09b async → 11 auth → 14 deploy.
