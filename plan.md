# plan.md — Sửa 4 lỗi trước slice 13: markdown · real-time admin · tích hợp đơn hàng · tín hiệu handoff

> Repo: `github.com/trevor2903-kma/autonomous-customer-care-agents`. BE `apps/backend` (FastAPI+LangGraph+Alembic).
> Scripts + `.env` ở **gốc repo**. FE `apps/dashboard` (Next.js, Tailwind thuần + TanStack, **KHÔNG shadcn**).
> Nguyên tắc: cấu hình từ env, **KHÔNG hardcode**; sửa **có phẫu thuật**.

---

## 0. Bối cảnh & gốc lỗi (grounded từ code, tip `564f1f8`)

Bốn lỗi, nhưng **P2+P3 cùng một gốc**: _escalation đang bị suy ra từ CHỮ trong câu trả lời, không phải từ QUYẾT ĐỊNH của Agent 3._

- **Lỗi markdown**: `_system_prompt` (`response.py`) **chưa cấm markdown** → GPT-4o-mini phát `**...**` (thói quen + tài liệu KB `.md` có sẵn `**bold**`). Khung chat render văn bản thuần → hiện `**` nguyên xi. _Nội dung vẫn grounded đúng — chỉ rò định dạng._
- **Real-time admin**: `ws/chat.py` nhánh **AI thường** persist tin khách + gửi reply vào socket khách, nhưng **KHÔNG `hub.publish`** lên channel (chỉ nhánh HUMAN_HANDLING publish). FE admin `app/admin/[conversationId]/page.tsx` **đã** xử lý `type:"message"` → chỉ thiếu backend publish.
- **Tín hiệu handoff GIẢ**: FE khách `app/chat/page.tsx` dòng 82–84 **dò CHỮ** `text.includes(HANDOFF_HINT)` → nếu reply chứa "chuyển nhân viên" thì set `waiting`. Nhưng đó là `type:"reply"` (auto_reply) — backend **chưa escalate**. → khách thấy "đang chờ nhân viên" (giả), admin thấy "AI đang xử lý" (thật), AI vẫn trả lời.
- **Order không escalate thật**: `order_status` **không** ∈ `BLOCKING_FLAGS`; Agent 2 truy hồi KB vận chuyển _thành công_ → không cờ chặn → auto_reply. Mà câu hỏi về **một đơn cụ thể không thể trả lời từ KB** (chưa có dữ liệu đơn). Case doc `knowledge/case/don-giao-cham.md` dòng 20 dặn "**chuyển nhân viên**" → Agent 4 nói ra, nhưng không có escalation thật. Entity `order_id` **đã** được taxonomy trích cho intent đơn hàng.

---

## 1. Bất biến kiến trúc (KHÔNG phá)

- Pipeline 4-agent cố định/không Supervisor; **Agent 4 egress DUY NHẤT luồng tự động**; Agent 3 tất định theo cờ; 1 worker + hub in-process.
- **Escalation là QUYẾT ĐỊNH của Agent 3 (theo cờ), KHÔNG phải chữ của Agent 4.** Mọi "cần người" phải thành **cờ** để Agent 3 xử → state đổi thật (`IN_HUMAN_QUEUE`), FE bám state, không bám chữ.
- **Grounding**: Agent 4 chỉ nói từ `facts.md` + `rag_contexts` (+ nay **dữ liệu đơn** khi có). Không bịa _có_, không suy diễn _không có_. **Grounding hành động**: chỉ hứa/khẳng định việc hệ thống LÀM ĐƯỢC.
- **Quyền riêng tư đơn hàng**: "đơn 1234 của TÔI" là dữ liệu cá nhân → lookup **CHỈ trong phạm vi khách đã đăng nhập** (slice 11 đã cấp danh tính qua JWT-over-WS). Không lộ đơn của người khác.

---

## 2. Thiết kế cốt lõi (P2 — tích hợp đơn hàng)

### 2.1 Model `order` + seed

`order`: `id` (UUID PK) · `order_code` (str, UNIQUE — mã "1234") · **`customer_id`** (UUID FK→user, chủ đơn) · `status` (enum `OrderStatus`) · `items_summary` (str) · `region` (str) · `ordered_at` · `shipped_at` (null) · `estimated_delivery` (null) · `tracking_code` (str, null) · `created_at`.
`OrderStatus` (StrEnum): `pending`/`processing`/`shipped`/`delivering`/`delivered`/`cancelled` + **map nhãn tiếng Việt** dùng khi dựng khối context (Agent 4 nói tiếng Việt).
**`scripts/seed_orders.py`** (pattern `seed_admin.py`): **truy vấn các khách đã có trong DB** (role=customer) và tạo **đơn đa dạng phủ ĐỦ mọi `OrderStatus`** cho mỗi khách (mỗi khách ~6–8 đơn rải khắp: `pending`/`processing`/`shipped`/`delivering`/`delivered`/`cancelled`), dữ liệu thật-như: `order_code` duy nhất (vd `TYS-<mã khách ngắn>-<i>`), `items_summary` biến hoá, `region` đa dạng (Hà Nội/Đà Nẵng/HCM/tỉnh), **ngày & mã vận đơn nhất quán với trạng thái** (`delivered`→có đủ ngày đặt/gửi/giao + tracking; `delivering`→có gửi + tracking, chưa giao; `pending`/`processing`→chỉ mới đặt, tracking null; `cancelled`→có ngày huỷ). **Idempotent**: bỏ qua `order_code` đã tồn tại (chạy lại an toàn; thêm khách mới rồi chạy lại thì seed cho khách mới). **KHÔNG cần env chỉ-định-khách** — tự lấy từ DB. Migration Alembic tạo bảng.

### 2.2 Tra cứu SCOPED

`order_service.lookup(order_code, customer_id) -> Order | None`: trả đơn **chỉ khi** tồn tại **VÀ** thuộc `customer_id`. `order_code` có nhưng thuộc người khác → trả `None` (không lộ sự tồn tại).

### 2.3 Gộp vào Agent 2 + luật "hỏi mã đơn một lần rồi escalate"

Truyền `customer_id` xuống pipeline: đổi chữ ký `run_pipeline(input_text, history, turn_id, customer_id)`; WS truyền `customer_id` (từ token) → vào `state`.
Trong `knowledge_node` (sau RAG), **khi intent là đơn hàng** (`order_status`; và `shipping` nếu có `order_id`):

- **Có `order_id` + lookup THẤY** (thuộc khách) → gắn khối **`order_context`** vào state (Agent 4 đọc): mã đơn · trạng thái (nhãn VI) · items · khu vực · ngày đặt/gửi · dự kiến giao · mã vận đơn. _(RAG vẫn chạy song song — đơn + chính sách bổ trợ nhau.)_
- **Có `order_id` nhưng KHÔNG thấy / không thuộc khách** → đặt cờ **`order_unresolved`** → escalate thật.
- **KHÔNG có `order_id`** → **KHÔNG escalate**; để Agent 4 **hỏi mã đơn** (auto_reply bình thường). Đây là bước "hỏi một lần".

### 2.4 Agent 3 — thêm cờ chặn

`BLOCKING_FLAGS` thêm **`order_unresolved`** (khách đưa mã nhưng bot không giải được → human_handoff). Logic decision **không đổi** khác. Cập nhật `_PRIORITY_SEVERITY` nếu cần (order_unresolved theo intent order_status = medium/low như hiện tại).

### 2.5 Agent 4 — dùng dữ liệu đơn + chỉnh grounding hành động

- Nếu state có `order_context` → Agent 4 **báo trạng thái đơn** dựa trên khối đó (grounded). Vẫn **KHÔNG** tự huỷ/hoàn/đổi đơn (chỉ báo trạng thái).
- Nếu không có `order_context` và intent đơn hàng thiếu mã → **hỏi mã đơn** (không hứa handoff — xem P3).

---

## 3. Các pha (P0–P3) — Claude Code chạy tuần tự, commit từng pha

### P0 — Cấm markdown ở Agent 4 `fix(agent): P0 plain-text replies (no markdown)`

- **In:** thêm luật `_system_prompt` (`response.py`): _"Trả lời bằng văn xuôi hội thoại thuần như nhân viên nhắn tin với khách; KHÔNG dùng markdown (`**`, `#`, `-`, `_`), KHÔNG in đậm/tiêu đề/gạch đầu dòng."_
- **Verify (live):** hỏi "chính sách đổi trả" → câu trả lời **không còn `**`\*\*, văn xuôi tự nhiên; nội dung vẫn đúng chính sách (30 ngày, còn tag…).

### P1 — Real-time màn admin (publish hub) `fix(chat): P1 publish customer+ai messages to hub`

- **In:** trong `ws/chat.py` nhánh AI thường, publish lên hub (`exclude=st.queue` để không dội lại khách):
  - Sau `_persist_message(CUSTOMER, msg)` → `hub.publish(st.conv_key, {"type":"message","from":"customer","content":msg}, exclude=st.queue)`.
  - Sau `send_json({"type":"reply",...})` → `hub.publish(st.conv_key, {"type":"message","from":"ai","content":reply}, exclude=st.queue)`.
  - Publish tin khách cả ở nhánh `pending`/`handoff` (để admin thấy câu hỏi). Publish **degrade an toàn**.
- **Out:** không đụng FE (đã xử lý `type:"message"`).
- **Verify:** admin mở một ca `ACTIVE_AI`, khách nhắn → **tin khách + reply AI hiện ngay** trong khung chat admin (không cần F5).

### P2 — Tích hợp đơn hàng (lookup scoped trong Agent 2 + escalate thật) `feat(order): P2 mock orders + scoped lookup in agent 2 + escalate-on-unresolved`

- **In:** (theo §2)
  - Model `order` + `OrderStatus` + migration; **`scripts/seed_orders.py`**.
  - `order_service.lookup(order_code, customer_id)` (scoped).
  - `run_pipeline(...)` + WS truyền **`customer_id`** vào state.
  - `knowledge_node`: gộp order lookup (§2.3) → `order_context` (thấy) / cờ `order_unresolved` (có mã, không thấy) / để Agent 4 hỏi mã (không mã).
  - `decision.py`: `BLOCKING_FLAGS` + `order_unresolved`.
  - `response.py`: dùng `order_context` báo trạng thái (grounded); không tự thao tác đơn.
- **Out:** tín hiệu handoff FE (P3).
- **Verify:** (khách đăng nhập có seed đơn) "đơn <MÃ_ĐÚNG> giao đến đâu" → bot **báo trạng thái thật** từ dữ liệu đơn; "đơn 9999" (không thuộc khách) → **escalate** (không bịa); "đơn của tôi giao đến đâu" (không mã) → bot **hỏi mã đơn** (không escalate).
- **Tự chạy (KHÔNG cần user thao tác):** Claude Code **commit migration TRƯỚC** (để đảo được: `alembic downgrade -1` + git revert), rồi tự chạy `alembic upgrade head` và `uv run python ../../scripts/seed_orders.py`, rồi **báo cáo** đã chạy gì + seed ra bao nhiêu đơn/khách. Seed idempotent nên chạy lại vô hại. (Chỉ dừng nếu DB không kết nối được hoặc migration/seed lỗi.)

### P3 — Tín hiệu handoff THẬT (bỏ dò-chữ + action-grounding) `fix(handoff): P3 real handoff signal + agent4 action-grounding`

- **In:**
  - **(Backend)** khi `status_out == IN_HUMAN_QUEUE`, WS gửi **`{"type":"handoff","content":<HANDOFF_NOTICE>}`** thay vì `{"type":"reply"}` (tín hiệu rõ ràng, không để FE đoán).
  - **(FE khách)** `app/chat/page.tsx`: **BỎ** `HANDOFF_HINT`/dò-chữ. Xác định `waiting` từ tín hiệu thật: nhận `type:"handoff"` → render system message + `setStatus("waiting")`; `type:"reply"` → luôn `"ai"`. (Reconnect vẫn lấy từ `thread.active_status`.)
  - **(Agent 4 action-grounding)** thêm luật `_system_prompt`: _"Bạn KHÔNG tự chuyển được cho nhân viên (hệ thống quyết). Khi đang trả lời tự động mà chưa đủ thông tin: HỎI thêm (vd mã đơn) hoặc nói thẳng chưa có thông tin — TUYỆT ĐỐI không hứa 'sẽ chuyển nhân viên'/'đang kết nối nhân viên'."_
  - **(KB, nhẹ)** rà bước "chuyển nhân viên" trong `knowledge/case/don-giao-cham.md`: escalation ca đơn nay đi qua cờ `order_unresolved` (P2) → viết lại bước đó thành hành động khách-thấy ("báo đang kiểm tra") thay vì lời hứa chuyển. _(Các case sensitive refund/exchange/complaint đã được gate giữ nháp cho admin duyệt — không đổi.)_
- **Out:** —
- **Verify:** khách hỏi đơn không giải được → escalate thật: **admin thấy "Chờ nhận ca"**, **AI DỪNG** (khách nhắn tiếp không được AI trả lời), khách thấy "đang chờ nhân viên" (thật, từ tín hiệu). Auto_reply thường → **không** còn câu "sẽ chuyển nhân viên" giả.

---

## 4. Ghi chú cho Claude Code

- Đọc `apps/backend/CLAUDE.md`. Cấu hình từ **`.env` gốc repo**; **KHÔNG hardcode**. Scripts gốc `scripts/` theo pattern `seed_admin.py` (`sys.path.insert(apps/backend)` + `load_dotenv(.env gốc)`).
- **KHÔNG phá bất biến §1**: escalation = cờ→Agent 3 (không phải chữ); Agent 4 egress duy nhất; grounding (facts+RAG+order, không bịa/không suy diễn vắng mặt, grounding hành động); lookup scoped theo khách; 1 worker + hub in-process.
- **P2+P3 cùng gốc** ("escalation phải THẬT") — làm liền mạch. Publish/log **degrade an toàn**, không làm rớt/chậm lượt.
- FE: Tailwind thuần + TanStack, KHÔNG shadcn. Sửa có phẫu thuật.
- Commit **từng pha** với prefix ở tiêu đề. Dừng/nghỉ giữa pha được.
- **Stop-point:** P2 **KHÔNG cần dừng** — Claude Code tự commit migration → `alembic upgrade head` → `seed_orders.py` → báo cáo (migration đảo được, seed idempotent). Chỉ dừng nếu chạm bất biến §1, DB không kết nối được, hoặc phải xoá/viết lại nhiều file.

## 5. Phạm vi & không-phạm-vi

- **Trong:** cấm markdown; real-time admin (publish hub); tích hợp đơn hàng mock (model+seed+lookup scoped trong Agent 2 + cờ `order_unresolved` escalate) + Agent 4 báo trạng thái đơn; tín hiệu handoff thật (backend `{type:handoff}` + FE bỏ dò-chữ + Agent 4 action-grounding + dọn case doc đơn).
- **Ngoài (sau):** thao tác đơn thật (huỷ/hoàn/đổi qua tool) — chỉ _tra cứu_ ở slice này; dùng 1 đơn active khi khách không đưa mã (enhancement); slice 13 anti-injection; 14 deploy; 15 corrections pipeline.
