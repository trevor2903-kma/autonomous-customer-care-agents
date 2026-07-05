# PRD — Hệ thống Chăm sóc Khách hàng Tự trị sử dụng Multi-Agent AI (Shop Quần áo)

> **Tài liệu này là NGUỒN CHÂN LÝ của hệ thống.** Mọi quyết định triển khai phải đối chiếu với PRD này.
> Khi code và PRD mâu thuẫn → PRD đúng (hoặc cập nhật PRD trước rồi mới sửa code). Khi không chắc "hệ thống
> nên hành xử thế nào" → mở PRD, KHÔNG suy diễn.
>
> Hệ thống này dùng **kiến trúc điều khiển đa tác tử** (pipeline 4 agent cố định, KHÔNG Supervisor, gate cấu hình, 
> human-in-the-loop, kiểm toán đầy đủ);

---

## 1. Giới thiệu

### 1.1 Mục đích

Xây dựng hệ thống tự động hóa chăm sóc khách hàng cho shop quần áo, trong đó bốn AI Agent chuyên biệt phối
hợp trong một pipeline cố định để tiếp nhận, hiểu, tra cứu tri thức và trả lời câu hỏi của khách hàng; con
người (nhân viên CSKH / Admin) chỉ can thiệp ở các trường hợp quan trọng hoặc khi hệ thống không đủ tự tin.

Các vấn đề hiện tại mà hệ thống giải quyết:

- Số lượng câu hỏi lặp lại lớn (giá, size, vận chuyển, đổi trả…).
- Thời gian phản hồi chậm, phụ thuộc nhiều vào nhân viên trực.
- Khó theo dõi hiệu suất xử lý yêu cầu và chất lượng trả lời.
- Khó quản lý tài liệu hướng dẫn, chính sách và kiến thức nghiệp vụ một cách nhất quán.

### 1.2 Tầm nhìn

Giảm tải cho nhân viên CSKH và rút ngắn thời gian phản hồi, đồng thời giữ trách nhiệm giải trình thông qua
nhật ký kiểm toán và cơ chế chuyển tiếp/duyệt của con người. Hệ thống tự động nhưng **trong tầm kiểm soát**:
ưu tiên tính dự đoán được, khả năng kiểm toán và an toàn nội dung (không trả lời sai chính sách) hơn là tự
trị tối đa.

### 1.3 Bối cảnh sản phẩm

Web đóng vai trò kép: **cổng chat công khai** cho khách hàng VÀ **bảng điều hành đầy đủ** cho Admin (danh
sách hội thoại, chat trực tiếp, quản lý RAG, giám sát, kiểm toán). Trên điện thoại, chính web này (dạng
**PWA cài được lên màn hình chính**) cho Admin xử lý nhanh hội thoại được chuyển tiếp khi di chuyển. Backend
chạy pipeline đa tác tử thời gian thực (mục tiêu phản hồi tự động ≤ 5 giây).

---

## 2. Mục tiêu & Phi mục tiêu

### 2.1 Mục tiêu

- **M1.** Tự động phân loại ý định (intent) và trích xuất thực thể (entity) từ tin nhắn khách hàng.
- **M2.** Tự động tra cứu tri thức liên quan (RAG) từ chính sách/FAQ/thông tin sản phẩm để trả lời có căn cứ.
- **M3.** Tự động đánh giá rủi ro và ra quyết định: trả lời tự động hay chuyển nhân viên (human handoff).
- **M4.** Tự động sinh phản hồi cuối cùng cho khách — sau khi qua cổng kiểm soát (gate).
- **M5.** Cung cấp dashboard giám sát hệ thống/agent thời gian thực + hàng đợi chuyển tiếp cho Admin.
- **M6.** Bảo đảm tính kiểm soát: nhật ký kiểm toán đầy đủ, human-in-the-loop, gate cấu hình được, quản lý RAG.

**Mục tiêu kinh doanh (đo bằng KPI §19):** tự động xử lý ≥ 70% yêu cầu; thời gian phản hồi tự động < 5 giây;
giảm tải nhân viên CSKH; chuẩn hóa quy trình xử lý yêu cầu.

### 2.2 Phi mục tiêu (Phase 1 — không làm)

- Không có bộ nhớ dài hạn xuyên hội thoại (cross-conversation memory) — mỗi hội thoại có memory riêng (§12).
- Không hồ sơ khách hàng (customer profile memory), không gợi ý sản phẩm (recommendation engine).
- Không marketing automation, không tích hợp mạng xã hội, không voice/image search.
- Không phải hệ multi-agent tự trị hoàn toàn (**KHÔNG có Supervisor Agent** điều phối động).
- Không tích hợp hệ thống đơn hàng thật ở Phase 1 (order lookup là tool chừa chỗ — Phase 2).
- Chỉ kênh chat văn bản (web); không kênh thoại/video.

---

## 3. Thuật ngữ

- **Intent:** ý định của khách hàng trong một tin nhắn (vd `refund`, `shipping`, `size_consulting`).
- **Entity:** thực thể trích xuất từ tin nhắn (vd `order_id`, `product_name`, `size`).
- **Conversation (Hội thoại):** một phiên trò chuyện giữa một khách hàng và hệ thống; có memory riêng (§12).
  Trạng thái vòng đời do §15 quy định.
- **Ticket / Request:** một yêu cầu/vấn đề cụ thể bên trong hội thoại — **đơn vị nghiệp vụ chạy qua pipeline**.
  Phase 1: mỗi hội thoại có một ticket "đang mở" tại một thời điểm.
- **Message:** một tin nhắn (của khách / AI / admin) trong hội thoại.
- **Agent:** một bước xử lý chuyên biệt trong pipeline (intent classifier, knowledge agent, decision engine,
  response generator).
- **Pipeline:** chuỗi agent cố định xử lý một tin nhắn: `intent → knowledge → decision → response`.
- **HITL / human_handoff:** điểm chuyển hội thoại cho Admin xử lý, kích hoạt có điều kiện.
- **Gate:** cổng cấu hình do Admin bật/tắt, kiểm soát hành động tự động (auto-reply, auto-resolve).
- **confidence:** độ tự tin của agent với kết quả của nó (0..1).
- **uncertainty_flags:** cờ **an toàn/bất định** (vd `ambiguous_intent`, `no_relevant_knowledge`,
  `hallucination_risk`) — khi có cờ → Decision Engine đặt `action=human_handoff` (xem §7.3, §9).
- **escalation_reason:** lý do một hội thoại bị chuyển sang human_handoff.
- **EscalationCard:** thẻ ngữ cảnh đính kèm mỗi ca human_handoff (tóm tắt + intent + ngữ cảnh + lý do + nháp).
- **RAG (Retrieval-Augmented Generation):** sinh phản hồi dựa trên tri thức truy hồi từ vector DB.
- **Session memory:** bộ nhớ ngắn hạn của một hội thoại (lịch sử + ticket hiện tại).
- **Grounding:** phản hồi tự động phải dựa trên tri thức truy hồi được, không bịa (anti-hallucination).

---

## 4. Vai trò & Phân quyền

| Vai trò                    | Đăng nhập                       | Quyền                                                                                                                                                                                  |
| -------------------------- | ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Khách hàng (Customer)**  | Tùy chọn (guest hoặc tài khoản) | Tạo hội thoại mới; chat với AI; nhận phản hồi tự động; chờ phản hồi từ nhân viên nếu được chuyển tiếp; xem lịch sử hội thoại của mình.                                                  |
| **Admin (Nhân viên CSKH)** | Bắt buộc                        | Xem danh sách hội thoại + bộ lọc; chat trực tiếp với khách; nhận & xử lý hàng đợi chuyển tiếp (EscalationCard); duyệt nháp phản hồi; upload/quản lý tài liệu RAG; bật/tắt gate; giám sát hệ thống/agent; xem analytics & audit log. |

> Khách hàng có thể dùng chế độ guest (chỉ cần định danh phiên) hoặc đăng nhập để theo dõi lịch sử. Phase 1
> giữ rào cản thấp; phân quyền chi tiết hơn (vd nhiều cấp admin) để phase sau.

---

## 5. Triết lý thiết kế (4 trụ cột)

Đây là phần cốt lõi quyết định mọi lựa chọn kỹ thuật.

1. **Luồng cố định để dự đoán & kiểm toán.** Thứ tự agent và nhánh rẽ do graph quy định trước
   (`intent → knowledge → decision → response`), không do agent quyết runtime. **KHÔNG có Supervisor Agent**
   — đây là lựa chọn có chủ đích, đổi quyền tự trị tầng điều phối lấy độ tin cậy + khả năng kiểm toán + chi
   phí thấp.
2. **Tự trị CÓ GIỚI HẠN ở tầng agent.** Bên trong mỗi node, agent tự quyết dùng tool nào (function calling)
   — vd Knowledge Agent chọn nguồn tri thức và số đoạn truy hồi; Intent Classifier hỏi lại tối đa 1 lần khi
   mơ hồ — nhưng bị giới hạn số bước để giữ dự đoán được. Pipeline cố định ở tầng điều phối.
3. **An toàn trước case lạ.** Mỗi agent trả kèm `confidence` + `uncertainty_flags`; dưới ngưỡng → tự chuyển
   `human_handoff`. Đặc thù CSKH: **không có tri thức thì chuyển người, KHÔNG bịa câu trả lời** (grounding).
   "Không chắc thì chuyển nhân viên" là hành vi đúng, không phải thất bại.
4. **Cải thiện dần bán tự động có người duyệt.** Hệ thống phát hiện mẫu từ `audit_log` (intent hay bị chuyển
   tiếp, chủ đề confidence thấp, câu hỏi không có tri thức tương ứng) → *đề xuất* bổ sung FAQ / chỉnh prompt /
   thêm câu trả lời mẫu → Admin duyệt mới áp dụng. Agent KHÔNG tự đổi control flow hay tự sửa tri thức.

> Đánh đổi cốt lõi: quyền tự trị ở tầng điều phối ĐỔI LẤY độ tin cậy/khả năng kiểm toán + an toàn nội dung
> (không trả lời sai chính sách) + chi phí thấp.

---

## 6. Kiến trúc tổng thể

- **Web khách (Next.js):** giao diện chat (mô phỏng ChatGPT): Header · Chat Window · Message Input. Kết nối
  realtime qua WebSocket.
- **Web Admin (Next.js):** dashboard đầy đủ — danh sách hội thoại + chat trực tiếp; hàng đợi chuyển tiếp;
  quản lý RAG; giám sát hệ thống/agent; analytics; audit log; bật/tắt gate.
- **Trên điện thoại (PWA):** chính Web Admin ở trên, cài lên màn hình chính — Admin xem danh sách hội thoại +
  duyệt/nhận ca chuyển tiếp nhanh. Một app web duy nhất, responsive; KHÔNG có codebase mobile riêng.
- **Backend (FastAPI + LangGraph):** API Gateway + WebSocket; pipeline đa tác tử; session memory; chuyển tiếp
  con người (human handoff). Mục tiêu phản hồi tự động ≤ 5 giây.
- **Hạ tầng managed:** PostgreSQL (Neon) lưu hội thoại/ticket/audit; Redis (Upstash) cho session memory ngắn
  hạn + **pub/sub** phát realtime (event-driven, KHÔNG polling); Qdrant Cloud cho embedding tri thức (RAG).
- **Observability:** Langfuse (giám sát chi phí token/độ trễ/tỉ lệ lỗi — phase sau).

Luồng tổng thể (phía khách):

```
Khách → Chat UI → API Gateway + WebSocket → Session Memory → Pipeline 4 Agent
      → (Gate) → Phản hồi tự động   HOẶC   Human Handoff → Admin → Phản hồi
```

Luồng tổng thể (phía Admin): Dashboard → Danh sách hội thoại · Hàng đợi chuyển tiếp · Quản lý RAG · Giám sát
· Audit Log.

---

## 7. Bốn Agent

Mỗi agent nêu: **Đầu vào · Việc · confidence/cờ · Tool tự trị (phase sau)**. Schema I/O giữ định dạng JSON
để code bám theo.

### 7.1 Agent 1 — Intent Classifier

- **Đầu vào:** tin nhắn khách + lịch sử hội thoại.
- **Việc:** phân loại `intent` + `category`, trích `entities` → JSON. Là bước chuẩn hóa đầu vào pipeline.
- **confidence/cờ:** `ambiguous_intent` (không rõ ý), `multi_intent` (nhiều ý trong một tin nhắn),
  `out_of_domain` (ngoài phạm vi shop); confidence thấp khi tin nhắn mơ hồ/thiếu ngữ cảnh.
- **Tool tự trị (phase sau):** hỏi lại **tối đa 1 lần** để làm rõ ý (clarification) khi mơ hồ; tra cứu entity.

```text
# Example Intents
product_price · product_information · size_consulting · shipping · order_status
refund · exchange · complaint · promotion · other
```

```json
// Input
{ "message": "Áo này còn size M không shop?", "history": [] }
// Output
{ "intent": "product_information", "category": "pre_sale",
  "entities": { "product_name": "áo", "size": "M" },
  "confidence": 0.88, "uncertainty_flags": [] }
```

### 7.2 Agent 2 — Knowledge Agent (RAG)

- **Đầu vào:** intent + entities (+ câu hỏi gốc của khách).
- **Việc:** truy hồi tri thức liên quan từ Qdrant (chính sách đổi trả/vận chuyển, FAQ, hướng dẫn mua hàng,
  thông tin sản phẩm, tài liệu nội bộ) → danh sách `contexts` + `confidence` (điểm truy hồi). Chi tiết nạp &
  truy hồi: §13.
- **confidence/cờ:** `no_relevant_knowledge` (không tìm thấy đoạn phù hợp), `low_retrieval_score` (điểm thấp),
  `stale_knowledge` (tài liệu cần re-index — phase sau).
- **Tool tự trị (phase sau):** chọn nguồn truy vấn, số lượng chunk, re-rank, lọc theo metadata.

```json
// Input
{ "intent": "refund", "entities": { "order_id": "1234" } }
// Output
{ "contexts": [ { "source": "chinh_sach_doi_tra.pdf", "text": "..." } ],
  "confidence": 0.93, "uncertainty_flags": [] }
```

### 7.3 Agent 3 — Decision Engine — **node ra quyết định**

- **Đầu vào:** intent + RAG context + lịch sử hội thoại + confidence tổng hợp (từ Agent 1 & 2).
- **Việc:** đánh giá `priority` và `severity`; quyết định `action` = `auto_reply` **hoặc** `human_handoff`;
  sinh `reason` và `escalation_reason` (khi handoff). Đây là **node ra quyết định** của pipeline 
  và là nơi hội tụ tín hiệu an toàn của §5 trụ cột 3.
- **Quy tắc an toàn (bất biến):** nếu có **bất kỳ** `uncertainty_flag` nào (vd `ambiguous_intent`,
  `no_relevant_knowledge`, `low_retrieval_score`, `frustrated_customer`, `hallucination_risk`,
  `out_of_domain`, hoặc confidence < ngưỡng) → `action = human_handoff`. Đây là quyết định **an toàn**, độc
  lập với gate (§9).
- **Tính nhạy cảm (sensitivity) ≠ bất định:** intent nhạy cảm (`refund`/`complaint`/`exchange`) KHÔNG tự
  động là cờ bất định. Nếu ca tự tin & có tri thức, `action` vẫn có thể là `auto_reply`; việc **gửi thẳng hay
  cần Admin duyệt nháp** do **gate auto-reply theo category** quyết định (§9). Mục tiêu: ca nhạy cảm nhưng rõ
  ràng vẫn được xử lý nhanh (Admin chỉ duyệt một nháp tốt) thay vì luôn xử lý lại từ đầu.
- **Tool tự trị (phase sau):** công cụ đánh giá rủi ro; tra trạng thái đơn (order lookup — Phase 2).

```json
// Input: Intent + RAG Context + History + Confidence
// Output
{ "priority": "medium", "severity": "low",
  "action": "auto_reply", "reason": "Có đủ tri thức chính sách đổi trả, không có cờ bất định",
  "escalation_reason": null, "confidence": 0.9, "uncertainty_flags": [] }
```

```text
action:   auto_reply | human_handoff
priority: low | medium | high
severity: low | medium | high
```

### 7.4 Agent 4 — Response Generator

- **Đầu vào:** output Decision Engine (+ RAG context khi `auto_reply`).
- **Việc:** nếu `auto_reply` → sinh phản hồi cuối cùng **dựa trên RAG context** (grounded, tránh bịa); nếu
  `human_handoff` → trả khách thông báo "Yêu cầu của bạn đã được chuyển tới nhân viên hỗ trợ." và tạo
  **EscalationCard** (§11). Là **điểm phát ngôn DUY NHẤT** tới khách — mọi tin nhắn AI gửi đi đều qua đây
- **confidence/cờ:** `hallucination_risk` khi context yếu → có thể từ chối sinh và chuyển `human_handoff`.
- **Tool tự trị (phase sau):** chọn template/giọng điệu, chèn thông tin đơn hàng, định dạng phản hồi.

```text
# Rules
Nếu action == auto_reply   => sinh phản hồi (grounded theo RAG context); gửi theo gate (§9).
Nếu action == human_handoff => "Yêu cầu của bạn đã được chuyển tới nhân viên hỗ trợ." + tạo EscalationCard.
Nếu context không đủ để trả lời chắc chắn => KHÔNG bịa; chuyển human_handoff.
```

---

## 8. Luồng nghiệp vụ end-to-end

### 8.1 Thiết lập (Admin)

1. Admin đăng nhập, upload tài liệu tri thức (PDF/DOCX/TXT/MD). Hệ thống chunk → embedding → lưu Qdrant (§13).
2. Admin cấu hình: bộ intent/category, ngưỡng confidence, gate (§9), câu trả lời mẫu, mốc auto-resolve.

### 8.2 Khách mở hội thoại (web công khai)

3. Khách mở chat (guest hoặc đăng nhập), gửi tin nhắn. Hệ thống tạo `Conversation` (status `ACTIVE_AI`),
   khởi tạo session memory. Mỗi hội thoại độc lập, xử lý song song với hội thoại khác.

### 8.3 Pipeline (mỗi tin nhắn khách)

4. `intent`: phân loại + trích entity. (mơ hồ → có thể hỏi lại 1 lần → `AWAITING_CUSTOMER`)
5. `knowledge`: truy hồi RAG context.
6. `decision`: đánh giá + quyết định `action`. Định tuyến (§9):
   - `action = human_handoff` (có cờ bất định / context yếu) → **luôn** `IN_HUMAN_QUEUE` (gate no-op).
   - `action = auto_reply` + gate auto-reply **BẬT** cho category → `response` gửi thẳng → `REPLIED`.
   - `action = auto_reply` + gate auto-reply **TẮT** cho category (vd nhạy cảm) → nháp vào hàng đợi Admin
     duyệt → `PENDING_APPROVAL`.
7. `response`: thực thi phát ngôn cuối (trả lời / thông báo chuyển tiếp).

### 8.4 human_handoff (xem §11)

8. Hội thoại vào hàng đợi chuyển tiếp **kèm EscalationCard** (tóm tắt + intent + ngữ cảnh + lý do + nháp gợi ý).
   Admin nhận ca → AI tạm dừng cho hội thoại đó → Admin chat trực tiếp với khách (`HUMAN_HANDLING`).

### 8.5 Kết thúc

9. Vấn đề được giải quyết → ticket `RESOLVED`/`CLOSED`. Auto-resolve (nếu BẬT) tự đóng khi khách im lặng quá
   ngưỡng; nếu TẮT, Admin xác nhận đóng. Analytics & audit cập nhật.

Tóm tắt hai luồng:

```
# Auto Reply Flow
Khách → Agent1 → Agent2 → Agent3 → (gate) → Agent4 → Khách

# Human Escalation Flow
Khách → Agent1 → Agent2 → Agent3 → Human Queue → Admin → Khách
```

---

## 9. Gate cấu hình

Gate cho phép Admin chọn **mức độ tự động** mà hệ thống được phép thực hiện, mà không đụng vào logic an toàn.

| Gate              | Vị trí                                          | BẬT (ON)                             | TẮT (OFF)                                                 |
| ----------------- | ----------------------------------------------- | ------------------------------------ | -------------------------------------------------------- |
| **auto-reply**    | sau Decision Engine, ca `action=auto_reply`     | gửi thẳng phản hồi AI cho khách      | nháp → Admin duyệt trước khi gửi (`PENDING_APPROVAL`)    |
| **auto-resolve**  | sau khi đã phản hồi, khách im lặng ≥ ngưỡng     | tự đánh dấu `RESOLVED`/đóng hội thoại | giữ mở / Admin xác nhận đóng                             |

**Ba kết cục giao phản hồi (graduated response):**

| Kết cục                         | Khi nào                                                              | Ai gửi cho khách            |
| ------------------------------- | ------------------------------------------------------------------- | --------------------------- |
| **Gửi thẳng**                   | `auto_reply` · không cờ bất định · gate auto-reply ON cho category  | AI (Response Generator)     |
| **Duyệt nháp** (`PENDING_APPROVAL`) | `auto_reply` · không cờ bất định · gate auto-reply OFF cho category | Admin (duyệt/sửa nháp tốt)  |
| **Chuyển người** (`IN_HUMAN_QUEUE`) | `human_handoff` (có cờ bất định / context yếu)                  | Admin (xử lý từ đầu + EscalationCard) |

- **FR-GATE-1:** Gate là cấu hình của Admin, lưu trong DB; đặt được mức **toàn hệ thống** HOẶC **theo từng
  intent/category** (vd auto-reply ON cho `product_information`/`shipping`; OFF cho `refund`/`complaint`).
- **FR-GATE-2 (BẤT BIẾN):** Gate CHỈ can thiệp ca Decision Engine ra `auto_reply` (tự tin & an toàn). Ca
  `human_handoff` (do `uncertainty_flags` hoặc confidence < ngưỡng) → gate **no-op**, LUÔN `IN_HUMAN_QUEUE`,
  bất kể gate. (An toàn không bao giờ bị gate ghi đè.)
- **FR-GATE-3 (mặc định):** `auto-reply` mặc định **BẬT** (giá trị cốt lõi của CSKH: trả lời nhanh ca tự tin,
  rủi ro mỗi tin nhắn thấp) **nhưng** mặc định **TẮT cho nhóm nhạy cảm** (`refund`, `complaint`, `exchange`)
  → các ca này dù tự tin vẫn qua **Duyệt nháp**. `auto-resolve` mặc định **TẮT** (để Admin xác nhận đóng giai
  đoạn đầu).

---

## 10. Xử lý bất đồng bộ & chuyển tiếp con người

Nguyên lý: pipeline mỗi tin nhắn phải **nhanh** (≤ 5s) và **không giữ tài nguyên để đợi con người**. Khi cần
con người, hội thoại được tạm dừng auto-mode và chuyển quyền cho Admin; khi cần thêm thông tin từ khách,
hội thoại chờ lượt trả lời tiếp theo.

- **FR-ASYNC-1 (đường nhanh mỗi tin nhắn):** mỗi tin nhắn khách chạy pipeline đồng bộ, mục tiêu P95 ≤ 5s,
  ghi `audit_log` cho từng node. Session memory ở Redis (ngắn hạn, theo hội thoại).
- **FR-ASYNC-2 (lượt làm rõ — clarification):** Khi Intent/Decision cần thêm thông tin → Response Generator
  hỏi lại (tối đa 1 lần/lượt) → hội thoại sang `AWAITING_CUSTOMER`. Tin nhắn kế tiếp của khách **resume**
  pipeline với ngữ cảnh đã lưu.
- **FR-ASYNC-3 (chuyển tiếp = tạm dừng AI):** Khi `human_handoff` → hội thoại vào `IN_HUMAN_QUEUE`, **auto-pipeline
  tạm dừng cho hội thoại đó**; Admin được thông báo (push + badge dashboard). Tin nhắn khách trong giai đoạn
  này định tuyến tới Admin, KHÔNG tới AI. (Kỹ thuật: LangGraph `interrupt` + checkpointer giữ state hội thoại.)
- **FR-ASYNC-4 (ngoài giờ / không có Admin):** nếu không Admin nào online → giữ ca trong hàng đợi, gửi khách
  thông báo "nhân viên sẽ phản hồi sớm", thông báo Admin. **KHÔNG auto-đóng** ca chờ người.
- **FR-ASYNC-5 (trả lại AI — tùy chọn, phase sau):** Admin có thể trả hội thoại về chế độ AI sau khi xử lý
  xong; pipeline resume cho các tin nhắn tiếp theo.
- **FR-ASYNC-6 (bền vững):** state hội thoại đủ để resume sau khi service khởi động lại (checkpointer). Phase
  1 dùng Redis/short-term cho session; cân nhắc checkpointer Postgres khi cần bền vững dài hơn.
- **FR-ASYNC-7 (realtime, không polling):** phát tin nhắn tới client/Admin bằng WebSocket + Redis pub/sub
  (event-driven), KHÔNG worker polling (giữ free-tier Upstash).

---

## 11. human_handoff + EscalationCard

- **FR-ESC-1:** Mọi ca vào `human_handoff` phải kèm **EscalationCard** để Admin xử lý nhanh, KHÔNG chỉ đánh
  dấu "cần hỗ trợ".
- **EscalationCard gồm:** thông tin khách (id/định danh, tên nếu có); **tóm tắt hội thoại** (khách muốn gì);
  `intent` + `entities` phát hiện; **RAG context** đã truy hồi (nếu có); output Decision Engine (`priority`,
  `severity`); `escalation_reason` cụ thể (vd "không có tri thức phù hợp", "khách bức xúc", "confidence
  0.41 < ngưỡng", "ngoài phạm vi shop"); **nháp phản hồi gợi ý** (Admin sửa & gửi được); nút Nhận ca / Đóng
  + ô ghi chú; link mở **toàn bộ transcript** + agent trace.
- **FR-ESC-2 (web):** thẻ đầy đủ + transcript + trace; Admin chat trực tiếp với khách trong cùng màn hình.
- **FR-ESC-3 (trên điện thoại — PWA):** bản rút gọn responsive của EscalationCard (tóm tắt + intent + lý do +
  nháp + nút Nhận) để xử lý nhanh. Thông báo: badge số ca chờ hiển thị trong app. (Web push đẩy thật xuyên nền
  tảng: xem §22.)
- **FR-ESC-4 (xử lý):** Admin Nhận ca → `HUMAN_HANDLING` (AI tạm dừng) → chat với khách → Đóng → `RESOLVED`.
  Với ca `PENDING_APPROVAL` (gate auto-reply OFF): Admin **duyệt** nháp → gửi nguyên văn; hoặc **sửa & gửi**
  (ghi log là admin-edited); hoặc chuyển sang tự xử lý.
- **FR-ESC-5:** mọi quyết định/hành động của Admin ghi vào `audit_log` (ai, lúc nào, nhận/duyệt/sửa/đóng,
  ghi chú).

---

## 12. Bộ nhớ hội thoại (Conversation Memory)

**Phase 1:** mỗi hội thoại có memory riêng; **không chia sẻ dữ liệu giữa các hội thoại** (cross-conversation
memory để Phase 2). Lưu ngắn hạn ở Redis (truy cập nhanh trong lượt), sao lưu bền ở Postgres (bảng
`conversation`/`message`, §20).

```json
{
  "conversation_id": "",
  "customer_id": "",
  "messages": [],
  "current_ticket": "",
  "created_at": "",
  "updated_at": ""
}
```

- Memory cung cấp **lịch sử hội thoại** cho Intent Classifier (ngữ cảnh) và Decision Engine (đã hỏi gì, đã
  trả gì), và giữ `current_ticket` (intent + entities + trạng thái đang xử lý).
- Giới hạn cửa sổ ngữ cảnh (số tin nhắn gần nhất) cấu hình được (NFR-10).

---

## 13. RAG: nạp & truy hồi tri thức

```
Document Upload → Chunking → Embedding → Vector Database (Qdrant) → Retriever → Agent 2 (Knowledge Agent)
```

- **Nguồn tri thức:** chính sách đổi trả · chính sách vận chuyển · FAQ · hướng dẫn mua hàng · thông tin sản
  phẩm · tài liệu nội bộ.
- **Định dạng hỗ trợ:** PDF · DOCX · TXT · MD.
- **Vector DB:** Qdrant (khuyến nghị; Pinecone là lựa chọn thay thế). Embedding: `text-embedding-3-small`
  (hoặc model tương đương của LLM provider được chọn).
- **Quản lý (Admin Dashboard Module 1, §17):** upload · xóa · chỉnh metadata · re-index.
- **Liên quan grounding:** nếu Retriever không trả đoạn đủ liên quan → Knowledge Agent gắn `no_relevant_knowledge`
  → Decision Engine `human_handoff` (§7.3). KHÔNG để Response Generator bịa.

---

## 14. Yêu cầu chức năng (FR)

### 14.1 Admin

- **FR-ADMIN-CONV-1:** xem danh sách hội thoại + tìm kiếm + lọc theo trạng thái (đang AI / chờ duyệt / chờ
  nhận / đang xử lý / đã đóng); hiển thị tin nhắn mới nhất, thời gian cập nhật, trạng thái.
- **FR-ADMIN-CHAT-1:** mở một hội thoại, xem đủ tin nhắn (khách/AI/admin), chat trực tiếp với khách.
- **FR-ADMIN-QUEUE-1:** hàng đợi chuyển tiếp với EscalationCard; nhận ca / đóng ca.
- **FR-ADMIN-APPROVE-1:** hàng đợi duyệt nháp (khi gate auto-reply OFF); duyệt / sửa & gửi.
- **FR-ADMIN-RAG-1:** upload/xóa tài liệu RAG; chỉnh metadata; re-index (§13).
- **FR-ADMIN-GATE-1:** bật/tắt gate (toàn hệ thống và/hoặc theo intent/category).
- **FR-ADMIN-MON-1:** giám sát hệ thống (status, CPU, RAM, active users, active conversations, avg response time).
- **FR-ADMIN-MON-2:** giám sát agent (tên, status, latency, accuracy, confidence, escalation rate).
- **FR-ADMIN-ANALYTICS-1:** analytics (tổng hội thoại, auto-reply rate, escalation rate, satisfaction,
  resolution time; mẫu case lạ — vòng học, phase sau).
- **FR-ADMIN-AUDIT-1:** xem audit log (timestamp, conversation id, agent, action, result).

### 14.2 Khách hàng

- **FR-CUST-1:** tạo hội thoại mới (guest hoặc đăng nhập).
- **FR-CUST-2:** gửi tin nhắn và nhận phản hồi tự động (realtime qua WebSocket).
- **FR-CUST-3:** khi được chuyển tiếp → nhận thông báo và chờ phản hồi từ nhân viên.
- **FR-CUST-4:** xem lịch sử hội thoại của mình (nếu đăng nhập).

### 14.3 Pipeline / Agent

- **FR-PIPE-1:** mỗi hội thoại một state độc lập; nhiều hội thoại xử lý song song.
- **FR-PIPE-2:** thứ tự cố định `intent → knowledge → decision → response` + `human_handoff` có điều kiện.
- **FR-PIPE-3:** mỗi agent ghi `confidence` + `uncertainty_flags` vào state; routing dựa trên đó (§9, §10).
- **FR-PIPE-4:** mọi bước agent ghi `audit_log`.
- **FR-PIPE-5 (grounding):** phản hồi `auto_reply` phải dựa trên RAG context; khi `no_relevant_knowledge`/
  `hallucination_risk` → KHÔNG bịa, chuyển `human_handoff`.

### 14.4 RAG / Tri thức

- **FR-RAG-1:** nạp tài liệu (PDF/DOCX/TXT/MD) → chunk → embedding → lưu Qdrant.
- **FR-RAG-2:** truy hồi theo intent/entities; trả `contexts` + điểm truy hồi.
- **FR-RAG-3:** re-index khi tài liệu thay đổi; quản lý metadata; xóa tài liệu.

### 14.5 Thông báo

- **FR-NOTI-1:** realtime tới khách (phản hồi AI / tin nhắn admin) qua WebSocket.
- **FR-NOTI-2:** thông báo tới Admin khi có ca chuyển tiếp / chờ duyệt — badge (số ca chờ) trên dashboard/PWA,
  realtime qua WebSocket. (Web push đẩy thật xuyên nền tảng: §22.)

---

## 15. Vòng đời hội thoại (state machine)

`conversation.status` (canonical — dùng thống nhất ở backend, shared-types, dashboard):

```
NEW · ACTIVE_AI · CLASSIFYING · RETRIEVING · DECIDING · RESPONDING · REPLIED
AWAITING_CUSTOMER · PENDING_APPROVAL · IN_HUMAN_QUEUE · HUMAN_HANDLING · RESOLVED · CLOSED
```

```
NEW  (hội thoại tạo)
  │  khách gửi tin nhắn
  ▼
CLASSIFYING (Agent1) → RETRIEVING (Agent2) → DECIDING (Agent3) → định tuyến:
      auto_reply · an toàn · auto-reply ON    → RESPONDING (Agent4) → REPLIED
      auto_reply · an toàn · auto-reply OFF   → PENDING_APPROVAL
      cần làm rõ (clarify)                    → RESPONDING(hỏi lại) → AWAITING_CUSTOMER
      human_handoff (cờ bất định / context yếu) → IN_HUMAN_QUEUE
REPLIED:
      khách trả lời tiếp            → CLASSIFYING        (vòng lặp hội thoại)
      im lặng ≥ T · auto-resolve ON → RESOLVED
      im lặng ≥ T · auto-resolve OFF→ (giữ mở / Admin đóng)
AWAITING_CUSTOMER:
      khách trả lời  → CLASSIFYING
      timeout        → (tùy chọn) nhắc / RESOLVED
PENDING_APPROVAL (Admin duyệt nháp):
      duyệt          → RESPONDING → REPLIED
      sửa & gửi      → REPLIED [admin-edited]
      tự xử lý       → HUMAN_HANDLING
IN_HUMAN_QUEUE:
      Admin nhận     → HUMAN_HANDLING
HUMAN_HANDLING (Admin chat; AI tạm dừng):
      Admin đóng     → RESOLVED
      trả lại AI     → CLASSIFYING            (tùy chọn, phase sau)
RESOLVED / CLOSED  (kết thúc)
```

**Ba rổ dashboard:** đang xử lý (`NEW`, `ACTIVE_AI`, `CLASSIFYING..RESPONDING`, `AWAITING_CUSTOMER`); chờ
Admin (`PENDING_APPROVAL`, `IN_HUMAN_QUEUE`, `HUMAN_HANDLING`); kết thúc (`RESOLVED`, `CLOSED`). Lỗi kỹ thuật
→ chuyển `IN_HUMAN_QUEUE` nhưng gắn nhãn `[error]` để phân biệt với "ca cần người thật sự".

> **Conversation vs Ticket:** state machine trên là cấp **hội thoại**. `ticket.status` (cấp yêu cầu) thô hơn:
> `open` → `escalated` → `resolved`/`closed`. Phase 1 mỗi hội thoại một ticket đang mở.

---

## 16. Web vs Điện thoại (PWA)

| Chức năng                                    | Web Admin | Điện thoại (PWA) | Web khách |
| -------------------------------------------- | --------- | ---------------- | --------- |
| Chat với AI                                  | —         | —                | ✅        |
| Xem lịch sử hội thoại của mình               | —         | —                | ✅        |
| Xem danh sách hội thoại + lọc                | ✅        | ✅ (xem)         | —         |
| Chat trực tiếp với khách (human handling)    | ✅        | ✅               | —         |
| Duyệt nháp (PENDING_APPROVAL)                | ✅        | ✅ rút gọn       | —         |
| Nhận chuyển tiếp + EscalationCard            | ✅ đầy đủ | ✅ rút gọn       | —         |
| Quản lý RAG (upload/index)                   | ✅        | ❌               | —         |
| Giám sát hệ thống (System Monitoring)        | ✅        | ❌               | —         |
| Giám sát agent (Agent Monitoring)            | ✅        | ❌               | —         |
| Analytics                                    | ✅        | ❌               | —         |
| Audit log                                    | ✅        | ❌               | —         |
| Bật/tắt gate                                 | ✅        | ❌               | —         |

**Layout web khách:** Header · Chat Window · Message Input (mô phỏng ChatGPT).
**Layout web Admin chat:** trái = Conversation List (search · tin mới nhất · cập nhật · status); phải = Chat
Window (tin khách / AI / admin).
**Trên điện thoại (PWA):** Conversation List → Chat Screen (rút gọn), cài lên màn hình chính; badge số ca chờ.

> Chỉ một app web (Next.js), responsive; cột "Điện thoại (PWA)" là ưu tiên hiển thị + duyệt nhanh trên màn
> hình nhỏ, KHÔNG phải app riêng. Web push đẩy thật: §22.

---

## 17. Admin Dashboard (5 module)

- **Module 1 — RAG Management:** upload/xóa tài liệu; chỉnh metadata; re-index. (§13)
- **Module 2 — System Monitoring:** System Status · CPU · RAM · Active Users · Active Conversations · Average
  Response Time.
- **Module 3 — Agent Monitoring:** mỗi agent (Intent Classifier, Knowledge Agent, Decision Engine, Response
  Generator) hiển thị: Status · Latency · Accuracy · Confidence · Escalation Rate.
- **Module 4 — Analytics:** Total Conversations · Auto Reply Rate · Human Escalation Rate · Average Satisfaction
  · Average Resolution Time.
- **Module 5 — Audit Log:** Timestamp · Conversation ID · Agent · Action · Result. (vd `09:15:31 · Agent1 ·
  intent=refund`)

---

## 18. Yêu cầu phi chức năng (NFR)

- **NFR-1 (thời gian phản hồi):** phản hồi tự động P95 ≤ 5 giây.
- **NFR-2 (đồng thời):** ≥ 100 người dùng đồng thời; nhiều hội thoại song song; một hội thoại chuyển tiếp
  không làm nghẽn hội thoại khác.
- **NFR-3 (khả dụng):** uptime ≥ 99%.
- **NFR-4 (kiểm toán):** 100% hành động agent và quyết định Admin ghi `audit_log` đầy đủ, truy vết được.
- **NFR-5 (bảo mật):** JWT authentication; Role-Based Access Control; HTTPS/WSS.
- **NFR-6 (an toàn dữ liệu):** hội thoại chứa dữ liệu cá nhân khách; demo dùng dữ liệu tổng hợp/ẩn danh; có
  phương án chạy local khi cần.
- **NFR-7 (chống lạm dụng):** chống prompt injection từ tin nhắn khách và nội dung tài liệu RAG (phase sau).
- **NFR-8 (observability):** giám sát chi phí token, độ trễ, tỉ lệ lỗi (Langfuse — phase sau).
- **NFR-9 (chi phí):** ưu tiên dịch vụ managed free-tier; lường trần free-tier khi test tải.
- **NFR-10 (cấu hình):** ngưỡng confidence, gate, intent/category, mốc auto-resolve, cửa sổ ngữ cảnh, câu trả
  lời mẫu — cấu hình được.
- **NFR-11 (grounding/an toàn nội dung):** phản hồi tự động phải dựa trên tri thức; cấm trả lời sai/bịa chính
  sách; context yếu → chuyển người.

---

## 19. KPIs

| KPI                       | Mục tiêu     |
| ------------------------- | ------------ |
| Auto Reply Rate           | ≥ 70%        |
| Average Response Time     | < 5 giây     |
| Escalation Rate           | < 30%        |
| Customer Satisfaction     | ≥ 4.5 / 5    |
| Resolution Rate           | (theo dõi)   |
| Average Resolution Time   | (theo dõi)   |

---

## 20. Mô hình dữ liệu (thực thể chính)

> `conversation.status` dùng tập giá trị canonical ở §15. JSONB cho các trường mở rộng.

- **AdminUser:** id, email, password_hash, role, status (online/offline), created_at.
- **Customer:** id, identifier/email, name, is_guest, created_at.
- **Conversation:** id, customer_id, status, current_intent, current_ticket_id, assigned_admin_id,
  confidence, uncertainty_flags (JSONB), escalation_reason, created_at, updated_at, last_message_at.
- **Message:** id, conversation_id, sender (customer/ai/admin), content, intent, confidence, created_at.
- **Ticket (Request):** id, conversation_id, intent, category, entities (JSONB), priority, severity, status
  (open/escalated/resolved/closed), escalation_reason, resolved_at, timestamps.
- **KnowledgeDocument:** id, title, source_type, file_ref, metadata (JSONB), status (indexed/pending),
  embedding_ref (Qdrant), uploaded_by, created_at, indexed_at.
- **EscalationCase:** id, conversation_id, escalation_card (JSONB: summary, intent, rag_context, decision,
  reason, suggested_reply), assigned_admin, admin_action, admin_note, resolved_at.
- **GateConfig:** id, scope (global/per-category), category, auto_reply (bool), auto_resolve (bool),
  updated_by, updated_at.
- **AuditLog:** id, conversation_id, message_id, node, action, confidence, uncertainty_flags (JSONB),
  escalation_reason, detail (JSONB), created_at.
- **Vector (Qdrant):** embedding các chunk tri thức phục vụ truy hồi.

---

## 21. Tech stack đề xuất

> backend **FastAPI (Python) + LangGraph**, vì LangGraph
> (multi-agent, checkpointer, `interrupt`/suspend-resume) trưởng thành nhất trên Python và dùng chung tooling
> với repo còn lại. Bản draft từng nêu Fastify (Node) + RabbitMQ — xem ghi chú cuối mục.

| Lớp                  | Lựa chọn                                                        |
| -------------------- | -------------------------------------------------------------- |
| Frontend (Web)       | Next.js 14 · TailwindCSS · shadcn/ui · TanStack Query           |
| Điện thoại (PWA)     | Web PWA (Next.js) cài lên màn hình chính — không app riêng      |
| Backend              | **FastAPI (Python 3.12)** _(draft: Fastify/Node)_              |
| API / Realtime       | REST API + WebSocket                                           |
| Agent framework      | LangGraph                                                      |
| LLM provider         | OpenAI / Claude / Gemini (cấu hình được)                        |
| Embeddings           | text-embedding-3-small (hoặc tương đương)                      |
| Database             | PostgreSQL (Neon managed)                                      |
| Vector DB            | Qdrant (Cloud)                                                 |
| Cache / Session      | Redis (Upstash) — session ngắn hạn + pub/sub realtime          |
| Async (scaffold)     | FastAPI BackgroundTasks (KHÔNG broker polling)                  |
| Observability        | Langfuse (phase sau)                                          |

> **Ghi chú queue/realtime:**
>  CSKH realtime dùng **WebSocket** cho chat và **Redis pub/sub** (event-driven) để phát tin nhắn tới nhiều client/Admin —

---

## 22. Ngoài phạm vi / Tương lai

- **Phase 2:** Cross-conversation memory; Customer Profile memory; Recommendation system; tích hợp hệ thống
  đơn hàng (order lookup là tool thật); marketing automation; vòng học bán tự động đầy đủ (gom mẫu từ
  audit_log → đề xuất bổ sung FAQ/prompt → Admin duyệt — §5 trụ cột 4, thiết kế đã chừa chỗ).
- **Phase 3:** Voice assistant; tích hợp mạng xã hội; đa ngôn ngữ nâng cao.
- **Thông báo (push):** Web push notification xuyên nền tảng cho Admin (đặc biệt trên iOS, vốn hạn chế PWA
  push) — thay cho push native của app mobile cũ (đã bỏ). Phase 1 dùng badge in-app + realtime WebSocket.

---

## 23. Giả định & Câu hỏi mở

- **Giả định:** khách dùng kênh chat web; tri thức (chính sách/FAQ/sản phẩm) được Admin cung cấp dưới dạng
  tài liệu nạp được; mỗi hội thoại gắn một khách và một ticket đang mở.
- **Mở:** ngưỡng confidence cụ thể cho từng intent (tinh chỉnh thực nghiệm — Chương 4); mốc auto-resolve tối
  ưu; nhóm intent nào mặc định TẮT auto-reply (hiện đề xuất: refund/complaint/exchange); 
  có nên cho Admin trả hội thoại về AI (FR-ASYNC-5) ở Phase 1 hay để phase sau.

---

## 24. Source of Truth

Mọi thay đổi về: kiến trúc hệ thống · business logic · AI agents · database · UI · dashboard · API · workflow
— đều phải được **cập nhật vào PRD.md trước khi triển khai code**.

**PRD.md là tài liệu nguồn duy nhất (Single Source of Truth) của toàn bộ dự án CSKH.**
