# plan.md — 3 tinh chỉnh: tạo hội thoại lười · đơn không thấy → báo (không escalate ngay) · dọn hiển thị ngưỡng

> Repo: `github.com/trevor2903-kma/autonomous-customer-care-agents`. BE `apps/backend` (FastAPI+LangGraph+Alembic).
> Scripts + `.env` ở **gốc repo**. FE `apps/dashboard` (Next.js, Tailwind thuần + TanStack, **KHÔNG shadcn**).
> Nguyên tắc: cấu hình từ env, **KHÔNG hardcode**; sửa **có phẫu thuật**. Slice nhỏ, 3 pha độc lập.

---

## 0. Bối cảnh (grounded từ code, tip hiện tại)

- **P0 (tạo hội thoại lười):** `ws/chat.py` (~dòng 381–399) tạo/tìm conversation **ngay khi `websocket.accept()`** (khách MỞ chat, chưa gửi tin) → sinh conversation `ACTIVE_AI` rỗng → card thừa, loãng danh sách. Đăng ký tài khoản KHÔNG tạo hội thoại; chỉ mở-chat mới tạo.
- **P1 (đơn không thấy):** `knowledge_node` order-lookup hiện: mã có + lookup `None` (không thấy/không thuộc khách) → cờ **`order_unresolved`** (blocking) → **escalate ngay**. Nhưng "không tìm thấy" là **câu trả lời được** (kết quả lookup chính là grounding) — phần lớn do khách **gõ nhầm mã**, escalate ngay là quá vội + phí nhân viên.
- **P2 (ngưỡng):** cột `gate_config.retrieval_threshold` = **0.35 (chết)** — pipeline KHÔNG đọc; Agent 2 dùng `settings.retrieval_threshold` = **0.40** (`config.py`). Slider hiển thị 0.35 (sai) và từng định "chỉnh được ở phiên bản sau". Bạn đã chọn: **gỡ slider + bỏ cột chết**. Ngưỡng là **giá trị ĐO** từ `measure_threshold.py`, không phải nút UI.

---

## 1. Bất biến kiến trúc (KHÔNG phá)

- Mô hình hội thoại **giữ nguyên**: một ca active/khách, ca cũ đóng → khách nhắn lại mở ca MỚI (AI-first). P0 chỉ **dời thời điểm tạo**, không tạo nhiều ca active song song.
- **Escalation = QUYẾT ĐỊNH của Agent 3 (theo cờ), không phải chữ.** P1 chỉ **thu hẹp điều kiện** bật cờ escalate cho ca đơn, không đổi cơ chế.
- **Grounding + quyền riêng tư đơn hàng giữ nguyên:** câu "không tìm thấy" grounded trên kết quả lookup; lookup **scoped theo khách**; **KHÔNG lộ** đơn thuộc người khác (luôn nói "trong tài khoản CỦA BẠN").
- Ngưỡng thật vẫn ở `config.retrieval_threshold` (đặt từ script). Ghi/log **degrade an toàn**.

---

## 2. Các pha (P0–P2) — Claude Code chạy tuần tự, commit từng pha

### P0 — Tạo hội thoại LƯỜI (chỉ khi có tin đầu) `fix(chat): P0 lazy-create conversation on first message`

- **In (`ws/chat.py`):**
  - Lúc **connect** (`accept()`): chỉ xác thực + `get_active_conversation_for_customer` (nếu có → nạp lịch sử để hiển thị). **BỎ `open_case_for_customer` ở đây.** Nếu chưa có ca active → giữ `conv = None`, **chưa tạo gì**.
  - Lúc **`receive_text` ĐẦU TIÊN**: nếu `conv is None` → **lúc này mới `open_case_for_customer`** → đăng ký hub queue theo ca mới → chạy pipeline. Nếu đã có ca → dùng ca đó.
  - Đảm bảo đăng ký hub queue (`hub.register(conv_key)`) diễn ra **sau khi có conv** (dời theo).
- **Out:** không đổi mô hình ca (P2 cũ: ca đóng → tin mới mở ca mới — giữ nguyên).
- **Verify:** khách mở `/chat` mà **không** nhắn → **không** sinh conversation, admin **không** thấy card rỗng "AI đang xử lý". Khách nhắn tin đầu → ca mới tạo + agent chạy. Khách có ca đang mở từ phiên trước → connect nạp đúng lịch sử.

### P1 — Đơn không thấy → BÁO (auto_reply), escalate SAU `fix(order): P1 order-not-found informs instead of escalating immediately`

- **In (`knowledge_node` + `response.py`):**
  - Order-lookup: mã có + lookup `None` (không thấy / không thuộc khách) → **KHÔNG** đặt `order_unresolved` nữa; đặt tín hiệu **`order_not_found`** (state, **KHÔNG** phải blocking flag) + kèm `order_code` để Agent 4 nhắc lại.
  - `response.py`: khi state có `order_not_found` → **auto_reply** câu **privacy-safe**: _"Mình không thấy đơn `<mã>` trong tài khoản của bạn. Bạn kiểm tra lại mã giúp mình nhé; nếu mã đúng mà vẫn không thấy, mình sẽ chuyển nhân viên kiểm tra giúp bạn."_ (KHÔNG lộ đơn của người khác — luôn "trong tài khoản của bạn"; KHÔNG hứa chuyển ngay — grounding hành động vẫn giữ.)
  - **Escalate SAU (giữ `order_unresolved`, nhưng chỉ khi khách thật sự cần người):** đặt `order_unresolved` (→ Agent 3 human_handoff) khi **một trong hai**: (i) khách **xin gặp/chuyển nhân viên rõ ràng**; (ii) đây là **lần thứ hai** vẫn không giải được trong CÙNG ca. Phát hiện (ii) qua **`history`** (truyền vào lookup) — đếm số lượt khách hỏi đơn với `order_id` không giải được trong ca; ≥2 → escalate. **KHÔNG dò chữ trong reply.**
    > Nếu (ii) khó làm gọn, ưu tiên làm (i) trước ("xin nhân viên → escalate"); (ii) là tinh chỉnh — ghi rõ nếu tạm bỏ.
  - Ba nhánh còn lại **giữ nguyên**: mã + thấy (thuộc khách) → `order_context` báo trạng thái; không mã → hỏi mã.
- **Out:** không đổi cơ chế Agent 3 (vẫn theo cờ).
- **Verify:** (khách A có seed đơn) hỏi **mã lạ/gõ nhầm** → bot **báo "không thấy, kiểm tra lại mã"** (auto_reply, KHÔNG escalate); khách A hỏi **mã của khách B** → **cùng câu "không thấy trong tài khoản của bạn"** (không lộ đơn B); sau đó khách **xin gặp nhân viên** → **escalate thật** (admin "Chờ nhận ca", AI dừng); mã đúng → báo trạng thái thật.

### P2 — Dọn hiển thị ngưỡng (gỡ slider + bỏ cột chết) `chore(gate): P2 remove threshold slider + drop dead gate_config column`

- **In:**
  - **(FE)** Gỡ **card/slider "Ngưỡng độ tin cậy tri thức"** khỏi màn Cấu hình Gate (`apps/dashboard`).
  - **(BE)** Bỏ `retrieval_threshold` khỏi: model `GateConfig`, `gate_service` (`GateSnapshot`/`send_directly_for`-adjacent), response API `GET /admin/gate-config` (bỏ trường trả về). **Migration Alembic** drop cột `gate_config.retrieval_threshold`.
  - Nguồn chân lý ngưỡng = **`config.retrieval_threshold`** (đặt từ `measure_threshold.py` → env/config). Không UI, không cột DB.
- **Out:** không đổi hành vi pipeline (Agent 2 vẫn đọc `config`, 0.40).
- **Verify:** màn Cấu hình Gate **không còn** slider ngưỡng; `GET /admin/gate-config` không trả `retrieval_threshold`; `alembic upgrade head` chạy sạch (+ `downgrade` OK); pipeline vẫn dùng 0.40 như cũ.
- **Tự chạy:** Claude Code commit migration TRƯỚC → `alembic upgrade head` → báo cáo (đảo được). Chỉ dừng nếu DB không kết nối được / migration lỗi.

---

## 3. Ghi chú cho Claude Code

- Đọc `apps/backend/CLAUDE.md`. Cấu hình từ **`.env` gốc repo**; **KHÔNG hardcode**.
- **KHÔNG phá bất biến §1**: mô hình một-ca-active (P0 chỉ dời thời điểm tạo); escalation = cờ→Agent 3 (P1 chỉ thu hẹp điều kiện); grounding + privacy đơn hàng (không lộ đơn người khác); ngưỡng thật ở `config`. Ghi/log degrade an toàn.
- **P1 — KHÔNG dò chữ**: phát hiện "cần người" bằng ý định/history, không match text reply (tránh đúng cái bug handoff cũ).
- FE: Tailwind thuần + TanStack, KHÔNG shadcn. Sửa có phẫu thuật.
- Commit **từng pha** với prefix ở tiêu đề. Dừng/nghỉ giữa pha được.
- **Stop-point:** P2 **tự chạy** migration (commit trước, đảo được). Chỉ dừng nếu chạm bất biến §1, DB không kết nối được, hoặc phải xoá/viết lại nhiều file.

## 4. Phạm vi & không-phạm-vi

- **Trong:** tạo hội thoại lười (chỉ khi có tin đầu); đơn không thấy → auto_reply báo (privacy-safe) + escalate-sau (xin nhân viên / lần 2); gỡ slider ngưỡng + bỏ cột `gate_config.retrieval_threshold`.
- **Ngoài (sau):** lọc/ẩn card hội thoại rỗng cũ đã tồn tại (nếu muốn dọn dữ liệu cũ — P0 chỉ chặn phát sinh MỚI); intent riêng "yêu cầu gặp nhân viên" (nếu (i) cần tổng quát hơn); đo ngưỡng trên traffic thật (phân bố `retrieval_confidence` ở tab Báo cáo — đã hoãn); slice 13 anti-injection; 14 deploy.
