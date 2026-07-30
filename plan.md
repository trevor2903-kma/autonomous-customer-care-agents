# plan.md — Observability + Tab Báo cáo · Vá absence-assertion · Kiện toàn UI

> Repo: `github.com/trevor2903-kma/autonomous-customer-care-agents`
> BE `apps/backend` (FastAPI + LangGraph + Alembic). Scripts + `.env` ở **gốc repo**. FE `apps/dashboard`
> (Next.js 14, Tailwind thuần + TanStack, **KHÔNG shadcn**). Nguyên tắc: cấu hình từ env, **KHÔNG hardcode**; sửa **có phẫu thuật**.

---

## 0. Mục tiêu & bối cảnh (grounded từ code)

Một slice quanh **observability + báo cáo**, kèm vá grounding nhỏ và kiện toàn UI. Trạng thái nền:

- **`audit_log` model + `audit_service` ĐÃ có** (cột `node/action/confidence/uncertainty_flags/escalation_reason/detail`),
  nhưng **chỉ task stub** ghi; **pipeline WS thật CHƯA ghi**; **THIẾU cột thời gian** và **THIẾU khóa gom một lượt**; **chưa có API đọc**; **chưa có tab**.
- **Langfuse**: config có placeholder (`langfuse_public_key/secret_key/base_url`), **code chưa nối**.
- **Công cụ dev cần gỡ**: "Test Agent 1" (`/classify`) + "Pipeline Inspector" (`/pipeline`) — endpoint trong
  `app/api/routes/agents.py` + component `apps/dashboard/components/rag/AnalyzePanel.tsx` (đang nhúng trong màn Quản lý tri thức).
- **Nav hiện tại** (`components/shell/AdminShell.tsx`): Hội thoại · Hàng đợi chuyển tiếp · Duyệt nháp · Quản lý tri thức · Cấu hình Gate.
- Đăng xuất **đã có** ở TopBar (slice 11) — lần này thêm **màu hành động** cho nó + "Đóng ca".

---

## 1. Bất biến kiến trúc (KHÔNG phá)

- Pipeline 4-agent cố định/không Supervisor; **Agent 4 egress DUY NHẤT luồng tự động**; grounding (facts+RAG, không bịa→handoff, grounding hành động); Agent 3 tất định theo cờ; 1 worker + hub in-process. Slice này **chỉ QUAN SÁT**, không đổi logic quyết định.
- **`audit_log` là NGUỒN của tab Báo cáo** (dữ liệu mình kiểm soát). **Langfuse là bổ trợ** (observability cấp LLM, có dashboard riêng) — **KHÔNG dựng tab trên Langfuse API**; chỉ link sang.
- Observability **không được làm chậm/rớt pipeline**: ghi audit_log + Langfuse phải **degrade an toàn** (lỗi ghi log KHÔNG làm hỏng lượt trả lời khách). Thiếu key Langfuse → no-op.

---

## 2. Design tokens (nhúng — Claude Code bám file HTML trong repo cho chi tiết)

> **Copy bản HTML mới nhất của bạn vào** `apps/dashboard/docs/design/ThriftYourStyle_CSKH.dc.html` để Claude Code
> đọc chi tiết redesign (Claude Code KHÔNG đọc được thư mục upload; bản trên uploads là bản cũ). Token dưới đã xác nhận qua bảng màu.

**Bảng màu (thrift ấm):** nền `#FBFAF7` · listpane `#FDFCFA` · card `#FFFFFF` · nav-active `#F4F2EC`;
chữ `#211F1B`/`#332F29`/`#57534A`/`#8E887B`/`#B0A99B`/`#C4BEB1`; viền `#E7E2D8`/`#F0EDE6`/`#DDE1D0`;
**olive `#6B7A4F`** hover `#5A6743`, xanh nhạt `#EEF0E6`, viền xanh `#DDE1D0`;
**terracotta (nguy hiểm/thoát) `#B25B3C`** + đậm `#8A4E33` + nền nhạt `#F6E7DF`/`#EAD4C7`;
amber `#B98534`/`#F7EFDD`; NV xám-xanh `#42536B`/`#5A6B84`/`#E8ECF3`/`#D4DAE6`; chấm online `#5B7A5B`;
toggle off `#DAD5C8` · track slider `#EFEBE2`. Font: Playfair Display (heading/brand) + Be Vietnam Pro (body).

**Ngữ nghĩa MÀU HÀNH ĐỘNG (đo chính xác từ HTML mới):**

- **Hành động phá huỷ/thoát** (Đăng xuất, Đóng ca, Xoá) → chữ/icon `#B25B3C` · nền `#FDF3EF` · viền `#E8C4B6`.
- **Hành động xây dựng** (Nhận ca, Gửi, Duyệt & gửi) → nền olive `#6B7A4F` · chữ trắng · không viền.
- PWA `theme-color = #F9F7E7`.

---

## 3. Mô hình dữ liệu bổ sung (P1)

`audit_log` thêm 2 cột (migration Alembic):
| cột | kiểu | ghi chú |
|---|---|---|
| `turn_id` | UUID, index | **khóa gom một lượt** — mọi bước agent của cùng lượt khách chia sẻ 1 `turn_id` (sinh khi pipeline bắt đầu). Hiển thị dạng ngắn (`trc_…`) trong UI. |
| `duration_ms` | int, null | thời gian chạy của **bước** (node) đó, ms. |

> Vì sao cần: drill-down 4-agent cần gom 4 dòng theo `turn_id`; và tổng hợp "% auto theo intent" phải nối dòng
> `intent` với dòng `decision`/`response` của **cùng lượt** → không có khóa gom thì không tính được. `duration_ms`
> nuôi cả timeline per-agent lẫn KPI độ trễ (p50/p95, NFR-1 ≤5s).

Có thể lưu thêm vào `detail` (JSONB) các trường phục vụ UI mà không cần cột riêng: `intent`, `retrieval_confidence`,
`priority`, `severity`, `rag_sources` (list `{source,type,title,score}`), `reply_len`, `customer_text`.

---

## 4. Các pha (P0–P5) — Claude Code chạy tuần tự, commit từng pha. Slice LỚN.

### P0 — Vá absence-assertion (Agent 4) `fix(agent): P0 no absence-assertion from KB silence`

- **In:** thêm luật vào `_system_prompt` của `response.py`: _"Nếu nguồn (SỰ THẬT CỬA HÀNG + ĐOẠN TRI THỨC) KHÔNG nhắc tới một điều, TUYỆT ĐỐI đừng khẳng định điều đó KHÔNG tồn tại (vd 'shop không giao đi X', 'không có chi nhánh ở Y'). Hãy nói chưa có thông tin và sẽ chuyển nhân viên."_ Cấm suy diễn _không có_ từ chỗ nguồn im lặng (song song với cấm bịa _có_ đã có).
- **Out:** không đụng gì khác.
- **Verify (live):** câu "shop có giao đi Mỹ không" khi KB im lặng → bot **không** khẳng định "không giao", mà nói chưa có thông tin/chuyển nhân viên. Câu có trong KB vẫn trả lời bình thường.

### P1 — Ghi audit_log ở pipeline THẬT + thời gian + khóa gom `feat(obs): P1 persist audit_log in ws pipeline + timing + turn_id`

- **In:**
  - Migration: thêm `turn_id` (index) + `duration_ms` vào `audit_log`.
  - **Sinh `turn_id`** khi pipeline bắt đầu một lượt (trong `run_pipeline`/WS); gắn vào state.
  - **Đo thời gian từng node** (bọc mỗi node bằng timer — hoặc middleware LangGraph) → `duration_ms`.
  - Ghi **một dòng `audit_log`/node/lượt** qua `audit_service` **trong luồng WS THẬT** (mỗi lượt khách), gồm cả 2 sự kiện bao quanh nếu muốn ("nhận tin" / "đã gửi"). Điền `detail` (intent, retrieval_confidence, rag_sources[{source,type,title,score}], priority/severity, reply_len, customer_text).
  - **Degrade an toàn**: ghi log lỗi → chỉ log warning, KHÔNG làm rớt lượt trả lời.
- **Out:** API đọc (P2).
- **Verify:** chat thật 1 lượt → xuất hiện các dòng audit_log cùng `turn_id`, có `duration_ms`, `detail` đủ; pipeline không chậm/rớt.
- **Stop-point:** báo user chạy `alembic upgrade head`.

### P2 — API đọc + tổng hợp (KPI · theo-intent · lý-do-escalate · p95/NFR-1) `feat(obs): P2 reports read API + aggregation`

- **In (đều `require_admin`, prefix gợi ý `/admin/reports`):**
  - `GET /summary?range=today|7d|all` → KPI: %auto_reply · %duyệt_nháp · %handoff · %fallback; độ trễ **avg · p50 · p95** end-to-end; **%lượt ≤ 5s (NFR-1)**; **bóc tách lý-do-escalate** (đếm theo `escalation_reason`/blocking flags: low_retrieval_score X% · out_of_domain Y% · multi_intent Z%…).
  - `GET /by-intent?range=` → mỗi intent: số lượt · %auto vs handoff · độ trễ TB · confidence TB.
  - `GET /turns?range=&result=all|auto|handoff|draft` → **danh sách lượt gần đây** (turn_id ngắn, thời gian, hội thoại/khách, câu khách, intent, action, tổng độ trễ, cờ). Có phân trang.
  - `GET /turns/{turn_id}` → **drill-down 4 agent**: từng node (intent+confidence+entities+cờ · rag_sources[{source,type,title,score}]+retrieval_confidence · action+priority/severity+escalation_reason · branch+reply+hallucination_risk) + `duration_ms` từng bước + tổng.
- **Tổng hợp end-to-end/lượt**: gom `audit_log` theo `turn_id`; tổng độ trễ = tổng `duration_ms` các node (hoặc mốc thời gian đầu-cuối).
- **Out:** Langfuse (P3), FE (P4).
- **Verify:** sau vài lượt chat thật, `/summary` trả số khớp; `/by-intent` có dòng theo intent; `/turns/{id}` dựng lại đúng 4 bước với `.md` source (KHÔNG phải PDF).

### P3 — Nối Langfuse (bổ trợ, cấp LLM) `feat(obs): P3 langfuse tracing for llm calls`

- **In:**
  - Thêm SDK Langfuse; **instrument các lời gọi LLM/embedding** (Agent 1 classify, Agent 4 generate, embeddings) → trace + latency + token/cost lên Langfuse. Gắn `turn_id`/`conversation_id` làm trace id/metadata để đối chiếu với audit_log.
  - **Thiếu key Langfuse → no-op hoàn toàn** (không lỗi, không chậm).
  - **KHÔNG** dựng dữ liệu tab từ Langfuse — tab vẫn đọc `audit_log` (P2).
- **Out:** —
- **Verify:** có key → trace hiện trên dashboard Langfuse (kèm token/latency); không key → app chạy y như cũ.
- **Stop-point:** nếu cần biến `.env` Langfuse → báo user (đã có comment trong `.env.example`).

### P4 — Tab "Báo cáo" (FE) + gỡ 2 panel dev `feat(fe-obs): P4 reports tab + remove dev inspector`

- **In:**
  - **Nav thêm "Báo cáo" ở CUỐI** (`AdminShell.tsx`): Hội thoại · Hàng đợi chuyển tiếp · Duyệt nháp · Quản lý tri thức · Cấu hình Gate · **Báo cáo**.
  - **Bố cục tab** (theo mockup + phần đã chốt):
    1. **Bộ lọc khoảng thời gian** (Hôm nay / 7 ngày / Tất cả) — điều khiển toàn tab.
    2. **3 thẻ KPI**: _Tự động trả lời %_ (x/y tin) · _Chuyển nhân viên %_ **+ dòng top lý do** (thay "chủ yếu do độ tin cậy thấp" bằng số thật) · _Độ trễ_ — **trung vị + p95 + "% ≤ 5s (NFR-1)"**.
    3. **Bảng phân tích theo intent**: intent · số lượt · %auto vs chuyển-người · độ trễ TB.
    4. **Danh sách lượt gần đây + lọc theo kết quả** (Tất cả/auto/handoff/duyệt) — thay 3 ví dụ ghim cứng; degrade mượt khi loại nào chưa có.
    5. Chọn một lượt → **hàng thẻ 4 tác tử** (như mockup: nhãn tác tử + tóm tắt + số phụ + **ms**; thẻ Agent 2 hiện **source `.md` + type/title + score**, KHÔNG phải PDF) + **timeline ms**.
    6. **Bảng "Nhật ký kiểm toán" per-step** (mốc thời gian · tác tử · hành động · kết quả) — gồm cả sự kiện "Tin nhắn khách"/"Hệ thống gửi" bao quanh.
    7. _(tuỳ chọn)_ nút **"Xem trace LLM chi tiết"** → link Langfuse.
  - Nối các endpoint P2 (TanStack query).
  - **GỠ**: component "Test Agent 1" + "Pipeline Inspector" (`AnalyzePanel.tsx`) khỏi màn Quản lý tri thức; gỡ endpoint dev `/classify`, `/pipeline` trong `agents.py` nếu không còn dùng (giữ `/analyze`,`/run-demo` nếu test khác cần — kiểm tra tham chiếu trước khi xoá).
- **Out:** UI polish (P5).
- **Verify:** nav 6 mục, Báo cáo ở cuối; tab hiện KPI + theo-intent + lý-do-escalate + p95/NFR-1 + danh sách lượt + drill-down 4 agent (source `.md`); màn Quản lý tri thức không còn 2 panel dev.

### P5 — Kiện toàn UI (theo HTML mới của bạn) `feat(fe): P5 sidebar-collapse + action-colors + knowledge redesign + favicon + full-vi`

> Bám `docs/design/ThriftYourStyle_CSKH.dc.html` (bạn copy vào repo) cho chi tiết; token + số liệu ở §2.

- **In:**
  1. **Màu hành động** (đo từ HTML): Đăng xuất/Đóng ca/Xoá → chữ/icon `#B25B3C` · nền `#FDF3EF` · viền `#E8C4B6`; hành động xây dựng (Nhận ca, Gửi, Duyệt) giữ nền olive `#6B7A4F` chữ trắng. Cụ thể: **nút Đăng xuất** = icon-only 34×34, bo 9px, đặt ở khối user trong sidebar (cạnh "Đang trực tuyến"); **nút Đóng ca** = icon + chữ "Đóng ca", bo 8px, hiện ở header hội thoại khi `conv.canClose`.
  2. **Thu gọn / mở rộng sidebar** (logic mới): handler `toggleSide` bật/tắt class `.side-collapsed` trên `.admin-side`. **Mở rộng** ~250px (đủ label + count + brand + user-meta); **thu gọn = 78px chỉ-icon** — ẩn `.nav-label`/`.nav-count`/`.brand-full`/`.user-meta`, `.nav-btn` căn giữa (`padding-left:0`). **Trigger**: ô "T" (`.brand-logo`) + nút chevron riêng (`.side-collapse-btn`, 30×30) cạnh brand. **Mobile ≤820px**: ẩn `.side-collapse-btn` (giữ drawer off-canvas hiện có), không dùng chế độ 78px. Nên nhớ trạng thái collapse (localStorage/cookie).
  3. **Redesign màn "Quản lý tri thức"** theo HTML mới (bảng tài liệu + vùng upload ad-hoc); **giữ chức năng** từ RAG refactor: `GET /rag/documents`, reindex-from-repo, upload non-canonical, badge tạm thời.
  4. **Favicon (web + PWA)** từ nhãn "T" (ô `#211F1B` + chữ serif kem): PNG **16/32/48/256** + **apple-touch 512** + `<meta theme-color="#F9F7E7">` + manifest PWA (icon 192/512). Ảnh gốc là asset design (href UUID, không lấy được) → **tự sinh** từ nhãn "T". Cập nhật `app/layout.tsx` metadata/icons + manifest.
  5. **Chuẩn hoá TOÀN tiếng Việt**: nhãn UI còn tiếng Anh (vd `auto_reply`/`human_handoff` hiển thị cho admin → "Tự động trả lời"/"Chuyển nhân viên"; "Pipeline", "Send/Submit"…) → tiếng Việt. **Giữ nguyên** định danh kỹ thuật mono (khóa intent `product_price`, `turn_id`/`trc_…`, tên `.md`).
- **Out:** —
- **Verify:** Đăng xuất/Đóng ca hiện tông cảnh báo (`#B25B3C`/`#FDF3EF`/`#E8C4B6`); **thu gọn sidebar → rail 78px chỉ-icon, mở lại đầy đủ**; mobile không có nút thu gọn (drawer vẫn chạy); màn tri thức khớp HTML; favicon hiện trên tab + khi cài PWA (theme `#F9F7E7`); không còn nhãn tiếng Anh trong UI (trừ định danh kỹ thuật mono).

---

## 5. Ghi chú cho Claude Code

- Đọc `apps/backend/CLAUDE.md`. Cấu hình từ **`.env` gốc repo**; **KHÔNG hardcode**.
- **Scripts gốc `scripts/`** theo pattern `seed_admin.py` (`sys.path.insert(apps/backend)` + `load_dotenv(.env gốc)`).
- **KHÔNG phá bất biến §1**: slice này **chỉ quan sát**, không đổi logic 4 agent (trừ P0 = luật prompt Agent 4). Ghi log **degrade an toàn**, không làm rớt/chậm lượt trả lời.
- **`audit_log` nuôi tab; Langfuse chỉ bổ trợ + link** — đừng dựng tab trên Langfuse.
- FE: **Tailwind thuần + TanStack, KHÔNG shadcn**. Bám `docs/design/ThriftYourStyle_CSKH.dc.html` (user copy vào) cho P4/P5; token §2. Sửa có phẫu thuật.
- **Trước khi xoá** `/classify`,`/pipeline` (P4): grep tham chiếu, xoá cả FE lẫn BE cho sạch.
- Commit **từng pha** với prefix ở tiêu đề. Dừng/nghỉ giữa pha được.
- **Stop-point:** (P1) `alembic upgrade head`; (P3) biến `.env` Langfuse nếu bật; (bất kỳ) chạm bất biến §1 hoặc xoá/viết lại nhiều file → dừng hỏi trước.

## 6. Phạm vi & không-phạm-vi

- **Trong:** vá absence-assertion; ghi audit_log ở pipeline thật + `duration_ms` + `turn_id`; API tổng hợp (KPI · theo-intent · lý-do-escalate · p95/NFR-1 · danh sách lượt · drill-down); Langfuse (bổ trợ + link); tab Báo cáo (cuối nav) + gỡ 2 panel dev; kiện toàn UI (màu hành động + redesign tri thức + favicon + toàn tiếng Việt).
- **Ngoài (sau):** **phân bố `retrieval_confidence` trên traffic thật** trong tab Báo cáo (#5 — hoãn theo yêu cầu); QA verdict per reply; corrections-pipeline (15); anti-injection (13); deploy (14); sàn điểm từng-context.
