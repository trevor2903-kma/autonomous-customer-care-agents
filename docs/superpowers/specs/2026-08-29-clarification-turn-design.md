# Thiết kế: Lượt clarification (AWAITING_CUSTOMER) — slice 09b (phần A)

- **Ngày:** 2026-08-29
- **Trạng thái:** Chờ review spec → plan
- **Nguồn chân lý:** PRD §10 FR-ASYNC-2 (clarification), §7.3 (Decision Engine), §15 (state machine)
- **Phạm vi:** CHỈ lượt clarification trên mẫu **DB history + status** (giữ `MemorySaver` + `thread_id` mỗi lượt). KHÔNG durable checkpointer, KHÔNG `interrupt()`, KHÔNG redesign reducer channels (quyết định của user — hướng A).

---

## 1. Vấn đề & mục tiêu

PRD §10 FR-ASYNC-2: khi Intent/Decision cần thêm thông tin → Response hỏi lại (tối đa 1 lần/lượt) → `AWAITING_CUSTOMER`; lượt kế của khách resume pipeline. Trạng thái `AWAITING_CUSTOMER` (PRD §15, enum) hiện **chỉ là scaffold** — chưa node nào set.

Ca cụ thể: intent gắn-với-đơn (`order_status`/`refund`/`exchange`) mà **thiếu mã đơn (`order_id`)**. Hiện [knowledge.py:128](../../../apps/backend/app/agents/nodes/knowledge.py) CỐ Ý để Agent 4 (LLM) tự hỏi mã (auto_reply). Ta **nâng cấp** thành máy trạng thái tường minh: hỏi tất định + `AWAITING_CUSTOMER` + loop-guard.

**"Resume" KHÔNG cần checkpointer:** lượt kế chạy pipeline bình thường với `history` (đã có hỏi-đáp) — y hệt mọi lượt khác. Đây là bản chất của hướng A.

**Tiêu chí thành công (kiểm chứng):**
- `order_status`/`refund`/`exchange` + không `order_id` + chưa hỏi + không cờ chặn → Response phát câu hỏi tất định + status `AWAITING_CUSTOMER`, KHÔNG gọi LLM.
- Lượt kế khách đưa mã → Intent trích `order_id` → lookup → xử lý bình thường (`order_status` trả lời; `refund`/`exchange` vào luồng nhạy cảm/duyệt nháp).
- Đã hỏi 1 lần (`prior_status == AWAITING_CUSTOMER`) mà vẫn thiếu mã → `human_handoff` (max 1, không hỏi vòng — FR-ASYNC-2).
- Safety-gate ưu tiên trên clarify: có cờ ∈ `BLOCKING_FLAGS` → `human_handoff`, KHÔNG clarify.
- Gate (duyệt nháp) không đụng clarify (chỉ chặn status REPLIED); câu hỏi gửi thẳng.
- `make test` OFFLINE-xanh (decision/response thuần, không LLM ở nhánh clarify).

---

## 2. Quyết định thiết kế

| # | Quyết định | Lý do |
|---|---|---|
| D1 | Clarify là **route thứ ba của Decision** (`AgentAction.CLARIFY`), tất định, SAU safety-gate | Decision là node ra quyết định (PRD §7.3); an toàn luôn ưu tiên |
| D2 | Trigger = `intent ∈ CLARIFY_MISSING_ENTITY` AND field thiếu; MVP map `{order_status, refund, exchange} → order_id` | Ba intent này đều cần mã đơn để xử lý; cùng field, cùng câu hỏi (hướng a) |
| D3 | Loop-guard qua **`prior_status`** truyền vào pipeline: đã hỏi (`AWAITING_CUSTOMER`) + vẫn thiếu → handoff | "Tối đa 1 lần" (FR-ASYNC-2); không vòng vô tận; không cần checkpointer để nhớ "đã hỏi" |
| D4 | Câu hỏi tất định do **Response** phát (sole-egress), template keyed theo **field** (`order_id` → 1 câu) | Sole-egress; refund/exchange tái dùng đúng câu của order_status |
| D5 | Giữ `MemorySaver` + `thread_id` mỗi lượt; KHÔNG durable checkpointer/interrupt | Hướng A: resume = lượt kế với history; tránh reducer-accumulation |
| D6 | `refund`/`exchange` clarify-TRƯỚC rồi mới vào luồng nhạy cảm (khi đã có mã) | User chọn hướng a; gom mã giúp admin đỡ hỏi lại |

---

## 3. Máy trạng thái (bổ sung PRD §15 — dùng `AWAITING_CUSTOMER` có sẵn)

```
DECIDING → route (Agent 3):
    cờ ∈ BLOCKING_FLAGS                                   → human_handoff → IN_HUMAN_QUEUE
    intent∈map · thiếu field · CHƯA hỏi                   → clarify       → RESPONDING(hỏi) → AWAITING_CUSTOMER
    intent∈map · thiếu field · ĐÃ hỏi (prior=AWAITING)    → human_handoff → IN_HUMAN_QUEUE  (max 1)
    còn lại                                               → auto_reply    → (gate) REPLIED / PENDING_APPROVAL
AWAITING_CUSTOMER:
    khách nhắn tiếp → CLASSIFYING (pipeline chạy lại, history có hỏi-đáp)
    im lặng ≥ T   → auto-resolve nhắc/đóng (sweep coi AWAITING_CUSTOMER là sweepable — đã có)
```

KHÔNG thêm `ConversationStatus` mới. `AgentAction` thêm `CLARIFY` (đối chiếu PRD §7.3 — xem §8).

---

## 4. Thành phần & giao diện

### 4.1 `models/enums.py`
- `AgentAction.CLARIFY = "clarify"` (thêm giá trị thứ ba).

### 4.2 `agents/state.py` (ConversationState)
- **+ `prior_status: str | None`** — status hội thoại TRƯỚC lượt này (input, chỉ-đọc). None = lượt/ca mới.
- **+ `clarify_field: str | None`** — field cần hỏi (Decision → Response). None nếu không clarify.

### 4.3 `agents/nodes/decision.py`
```python
CLARIFY_MISSING_ENTITY: dict[str, str] = {
    "order_status": "order_id",
    "refund": "order_id",
    "exchange": "order_id",
}
```
Logic (SAU safety-gate `blocking`):
- Nếu `blocking` → giữ nguyên `human_handoff` (an toàn ưu tiên; KHÔNG clarify).
- Ngược lại, `field = CLARIFY_MISSING_ENTITY.get(intent)`; `missing = bool(field) and not (entities.get(field))`:
  - `missing` và `prior_status != AWAITING_CUSTOMER` → `action=CLARIFY`, `clarify_field=field`.
  - `missing` và `prior_status == AWAITING_CUSTOMER` → `action=HUMAN_HANDOFF`, `require_human_handoff=True`, `escalation_reason="clarify_unresolved"`.
  - else → `AUTO_REPLY` (như cũ).
- `priority/severity` theo intent như cũ. `clarify_field` trả trong dict node (None khi không clarify).

### 4.4 `agents/nodes/response.py`
```python
CLARIFY_QUESTION: dict[str, str] = {
    "order_id": "Dạ anh/chị cho em xin mã đơn hàng để em kiểm tra giúp ạ.",
}
```
Nhánh mới trong `response_node` (TRƯỚC nhánh handoff/auto_reply):
- `action == CLARIFY` → `reply = CLARIFY_QUESTION[state["clarify_field"]]`, `status = AWAITING_CUSTOMER`, `branch = "clarify"`, `flags = []`, KHÔNG gọi LLM. (Nếu `clarify_field` lạ/thiếu template → fallback an toàn: coi như auto_reply? KHÔNG — dùng câu hỏi order_id mặc định hoặc handoff. Spec: `clarify_field` luôn có template ở MVP; nếu KeyError → fallback `FALLBACK_REPLY` + status REPLIED để pipeline không rớt.)

### 4.5 `agents/graph.py`
- `_initial_state(...)`: thêm tham số `prior_status`, set `prior_status` + `clarify_field=None`.
- `run_pipeline(...)`: thêm tham số `prior_status: str | None = None`, truyền xuống `_initial_state`.

### 4.6 `api/ws/chat.py`
- `_run_pipeline_safe(...)` + call-site: truyền `prior_status` = biến `status` (status TRƯỚC lượt, đã load cho status-gate) vào `run_pipeline`. Ca mới → None.

### 4.7 Không đổi (đã kiểm)
- Gate: `holds_auto_reply` chỉ chặn status REPLIED → clarify (AWAITING_CUSTOMER) no-op, gửi thẳng.
- Auto-resolve: `AWAITING_CUSTOMER ∈ _SWEEPABLE` → khách bỏ đi được nhắc/đóng (nhất quán).
- WS delivery: clarify phát type `reply` (câu hỏi là reply); KHÔNG cần signal mới.
- TurnOutcome: status AWAITING_CUSTOMER → `_outcome_of` trả SENT (đã gửi 1 reply).
- `order_not_found` (mã sai): KHÔNG đụng — là luồng khác (có mã, tra không ra).

---

## 5. Edge cases

- **Khách đưa mã ở lượt clarify:** Intent trích `order_id` (regex⊕LLM) → `missing=False` → không clarify → knowledge lookup → xử lý bình thường. `refund`/`exchange` có mã → luồng nhạy cảm (gate/duyệt nháp).
- **prior_status là REPLIED/ACTIVE_AI/None (chưa từng hỏi):** clarify lần đầu OK.
- **prior_status là AWAITING_CUSTOMER nhưng intent lượt này KHÁC (không thuộc map):** không clarify, đi auto_reply/handoff theo intent mới. (Loop-guard chỉ chặn khi VẪN thiếu field của intent-in-map.)
- **Safety-gate + missing đồng thời** (vd `human_requested` + order_status không mã): blocking → handoff (an toàn thắng clarify).
- **`clarify_field` không có template:** fallback `FALLBACK_REPLY` + REPLIED (pipeline không rớt) — chỉ xảy ra nếu map decision/response lệch (bắt bằng test).

---

## 6. Kiểm thử

**Offline (`make test`):**
- `decision`: mỗi intent∈{order_status,refund,exchange} + không order_id + prior None → CLARIFY (+ clarify_field="order_id"); có order_id → không CLARIFY; prior=AWAITING_CUSTOMER + vẫn thiếu → HUMAN_HANDOFF (reason clarify_unresolved); blocking flag đồng thời → HUMAN_HANDOFF (không clarify); intent ngoài map (vd product_price) không mã → không CLARIFY.
- `response`: action=CLARIFY + clarify_field=order_id → reply == câu hỏi order_id, status AWAITING_CUSTOMER, KHÔNG gọi LLM, flags rỗng.
- `graph` (nếu khả thi offline): pipeline order_status không mã → final status AWAITING_CUSTOMER + reply là câu hỏi (Intent offline dùng regex; nhánh clarify không cần LLM).

**Live (e2e, KB nạp):** WS: hỏi "đơn của tôi tới đâu" (không mã) → nhận câu hỏi mã + ca AWAITING_CUSTOMER; gửi mã hợp lệ → nhận trạng thái đơn; (refund không mã → hỏi mã → đưa mã → vào duyệt nháp).

---

## 7. Ranh giới an toàn / bất biến
- Safety-gate LUÔN ưu tiên clarify (blocking → handoff).
- Clarify KHÔNG gọi LLM (template cố định, sole-egress).
- KHÔNG durable checkpointer/interrupt/reducer-redesign (hướng A).
- KHÔNG thêm `ConversationStatus`.
- Decision vẫn TẤT ĐỊNH (không blend confidence, không reasoning).

---

## 8. Đối chiếu PRD
PRD §7.3 hiện liệt kê Decision output = `auto_reply | human_handoff`. §10 FR-ASYNC-2 mô tả clarification. Spec này thêm `clarify` làm route thứ ba của Decision (đúng tinh thần FR-ASYNC-2). **Hành động:** cập nhật PRD §7.3 ghi nhận `clarify` (route thứ ba, tất định, điều kiện thiếu-entity) trước/khi code — đưa vào plan như một bước.

## 9. Ngoài phạm vi
- Durable checkpointer + stable thread_id + `interrupt()` (hướng B — KHÔNG làm).
- Clarify cho intent fuzzy (size_consulting cần nhiều số đo) — khó tất định, để sau.
- Clarify đa-field / nhiều lượt hỏi (>1) — FR-ASYNC-2 giới hạn 1 lần.
