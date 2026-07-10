# PLAN — Tách vai đúng PRD: Agent 1 (taxonomy trong prompt) + Agent 2 (Knowledge Agent) + dọn state contract

> **Bản chất:** kịch bản ONE-SHOT, xong thì bỏ. Nguồn chân lý vẫn là **`PRD.md`** (§7.1 Intent Classifier —
> output SẠCH, KHÔNG retrieval; §7.2 Knowledge Agent — retrieval; §13 RAG; §5 trụ cột 3 — grounding).
>
> **Vì sao có plan này:** hiện Agent 1 đang **làm hộ việc retrieval của Agent 2** (`classify_intent` gọi
> `rag_service.search`, output rò rỉ `rag_contexts` + cờ `low_retrieval_score`) — lệch vai so với PRD. Plan
> này **tách vai**:
>
> - **Agent 1** phân loại từ message + **taxonomy cố định trong prompt** (KHÔNG retrieval). Output sạch
>   `{intent, category, entities, confidence, uncertainty_flags}`.
> - **Agent 2 (Knowledge Agent)** đảm nhiệm retrieval từ **kho tri thức** (chính sách/FAQ/sản phẩm) → contexts.
> - **Qdrant đổi vai:** từ "kho intent" → **kho tri thức để TRẢ LỜI** (Agent 2 truy hồi). Intents-guide KHÔNG
>   còn upload (taxonomy đã vào prompt).
> - Dọn **state contract**: cờ tích luỹ, tách per-stage confidence.
>
> Chỉ Agent 1 + Agent 2 có logic thật; Decision/Response/human_handoff vẫn stub (chỉ chỉnh Decision tối thiểu do contract).

---

## 0. Quyết định kiến trúc

- **Agent 1 (§7.1):** LLM phân loại từ message + **taxonomy few-shot cố định** (mô tả + ví dụ mỗi intent). BỎ
  `rag_service.search`. Output **BỎ `rag_contexts`**; cờ ∈ `{ambiguous_intent, multi_intent, out_of_domain}`
  (BỎ `low_retrieval_score`); `confidence` = độ tự tin LLM (không phải điểm cosine). Giữ entities (LLM ⊕ regex).
- **Agent 2 (§7.2):** `retrieve_knowledge(query)` gọi `rag_service.search` trên **kho tri thức** → `rag_contexts`
  (text+source+score) + `retrieval_confidence` + cờ `no_relevant_knowledge`/`low_retrieval_score`.
- **State contract (Layer 1 lite):** `uncertainty_flags` **TÍCH LUỸ** (reducer `add`); thêm `intent_confidence`
  - `retrieval_confidence`; `rag_contexts` **do Agent 2 ghi** (Agent 1 không ghi nữa). Decision đọc cờ tích luỹ
  - `min(intent_confidence, retrieval_confidence)`.
- **Corpus:** upload **`knowledge_base_shop_quan_ao.pdf`** (chính sách/FAQ/sản phẩm) — KHÁC intents-guide.
- Degrade an toàn (cả 2 agent) khi offline → `make test` vẫn offline OK; Response Generator vẫn là điểm phát ngôn duy nhất.

---

## 1. In / Out scope

**In scope:** dọn state contract; **refactor Agent 1** (taxonomy prompt, bỏ retrieval, output sạch); **xây Agent 2**
(retrieve từ kho tri thức); endpoint verify `POST /api/agents/analyze`; upload kho tri thức + verify e2e.
**Out of scope:** Decision/Response/human_handoff logic thật (chỉ chỉnh Decision tối thiểu do reducer); gate/
PENDING_APPROVAL; phản hồi khách thật; multi-provider; RAG management nâng cao. Intents-guide KHÔNG upload nữa.

---

## 2. Kế hoạch theo Phase

> Sau MỖI phase: chạy "Verify", cho tôi xem output, `git commit` (`refactor(agents): phase N - ...`), tóm tắt 1 dòng, tiếp nếu không lỗi.

### Phase 0 — Dọn state contract (cờ tích luỹ + per-stage confidence)

- `app/agents/state.py`: đổi `uncertainty_flags: list[str]` → **`Annotated[list[str], add]`** (tích luỹ như
  `trace`); thêm `intent_confidence: float`, `retrieval_confidence: float`.
- `app/agents/nodes/decision.py` (chỉnh tối thiểu do reducer — nếu không sẽ NHÂN ĐÔI cờ):
  - Đọc cờ tích luỹ để route (giữ nguyên logic an toàn).
  - **Chỉ emit cờ MỚI** cho `uncertainty_flags` (tức `injected` từ scratchpad), KHÔNG trả lại cả danh sách cũ.
  - `confidence` để check ngưỡng = `min(state.get("intent_confidence",1.0), state.get("retrieval_confidence",1.0))`.
- `should_handoff` (policy.py) KHÔNG đổi (vẫn đọc `require_human_handoff`).

**Verify:** `make test` xanh; chạy `run-demo` 2 nhánh — nhánh handoff vẫn đúng, cờ KHÔNG bị nhân đôi. Commit:
`refactor(agents): phase 0 - state contract (accumulate flags + per-stage confidence)`.

### Phase 1 — Refactor Agent 1 SẠCH (§7.1): taxonomy trong prompt, bỏ retrieval

- Tạo `app/agents/nodes/taxonomy.py`: hằng `TAXONOMY` = 10 intent, mỗi intent `{description, examples:[...3-4 câu]}`
  (lấy nội dung từ intents-guide) + `entity schema` theo intent; hàm `render_taxonomy() -> str` để nhúng vào prompt.
- `app/agents/nodes/intent.py`:
  - **BỎ** `from ...services import rag_service` và mọi lời gọi `search` / `_rag_contexts` / cờ `low_retrieval_score`.
  - `_system_prompt()` dùng `render_taxonomy()` (đầy đủ mô tả + ví dụ) — KHÔNG cần ngữ cảnh RAG nữa.
  - `classify_intent(text) -> {intent, category, entities, confidence, uncertainty_flags}` (**BỎ rag_contexts**):
    LLM phân loại từ message; validate intent ∈ `Intent` (lệch → other + `out_of_domain`); cờ khác:
    `ambiguous_intent`/`multi_intent` do LLM báo (nếu mơ hồ/nhiều ý); `confidence` = LLM; `category` = `INTENT_CATEGORY`;
    entities = `{**extract_entities_rule(text), **llm_entities}`. Degrade: thiếu key/LLM lỗi → `intent="unknown"`,
    `confidence=0.0`, cờ `["llm_unavailable"]`, entities = regex (KHÔNG network, KHÔNG ném lỗi).
  - `intent_node(state)`: ghi `intent, entities, intent_confidence(=confidence), uncertainty_flags` + `trace`.
    **KHÔNG ghi `rag_contexts`, KHÔNG ghi `confidence` chung.**
- `app/schemas/agent.py` `ClassifyResult`: **BỎ trường `rag_contexts`**.

**Verify:** `curl -X POST .../api/agents/classify -d '{"message":"Đơn hàng 6578 của tôi sắp giao tới nơi chưa?"}'`
→ `intent=order_status`, `category=after_sale`, `entities.order_id="6578"`, `uncertainty_flags` KHÔNG có
`low_retrieval_score`, **KHÔNG có `rag_contexts`**. `make test` xanh. Commit:
`refactor(agents): phase 1 - Agent 1 clean (taxonomy prompt, no retrieval, no rag_contexts)`.

### Phase 2 — Xây Agent 2 (Knowledge Agent, §7.2)

- `app/agents/nodes/knowledge.py` (viết thật, tách hàm thuần tái dùng):
  - `retrieve_knowledge(query: str, top_k: int = 4) -> {rag_contexts, retrieval_confidence, uncertainty_flags}`:
    - Thiếu `llm_api_key` (embeddings cần) / Qdrant lỗi / collection trống / `not hits` → degrade:
      `rag_contexts=[]`, `retrieval_confidence=0.0`, `uncertainty_flags=["no_relevant_knowledge"]` (KHÔNG ném lỗi).
    - Có hits: `hits = await rag_service.search(query, top_k)` → `rag_contexts=[{text, source, score}]`;
      `retrieval_confidence = float(hits[0]["score"])`; cờ `low_retrieval_score` nếu `hits[0].score < CONFIDENCE_THRESHOLD`.
  - `knowledge_node(state)`: `query = state.get("input","")` → `retrieve_knowledge(query)` → ghi `rag_contexts`,
    `retrieval_confidence`, `uncertainty_flags` (reducer tích luỹ) + `trace` (`node="knowledge"`, contexts count) +
    `status=RETRIEVING`.
- Grounding (PRD §5 trụ cột 3, FR-PIPE-5): cờ `no_relevant_knowledge` sẽ khiến Decision Engine (sau này)
  chuyển `human_handoff` — Agent 2 chỉ phát cờ, KHÔNG tự quyết.

**Verify:** unit — sau khi upload kho tri thức, `retrieve_knowledge("chính sách đổi trả trong bao nhiêu ngày?")`
→ `rag_contexts` có nguồn `knowledge_base_shop_quan_ao.pdf`, `retrieval_confidence>0`; `retrieve_knowledge("bla bla xyz")`
→ `no_relevant_knowledge`. `make test` xanh. Commit: `feat(agents): phase 2 - Knowledge Agent (RAG retrieval)`.

### Phase 3 — Endpoint verify Agent 1 + Agent 2

- `app/api/routes/agents.py`: `POST /analyze` (body `{message}`) → `intent = await classify_intent(msg)`;
  `know = await retrieve_knowledge(msg)` → trả `{intent, category, entities, intent_confidence(=intent.confidence),
retrieval_confidence, uncertainty_flags: intent.flags + know.flags, rag_contexts}`. (schema `AnalyzeResult`.)
  Cho thấy rõ tách vai: Agent 1 → intent/entities; Agent 2 → rag_contexts; cờ gộp.

**Verify:** `curl -X POST .../api/agents/analyze -d '{"message":"phí ship đi tỉnh bao nhiêu?"}'` → intent=shipping +
`rag_contexts` (Agent 2) có đoạn về phí ship. Commit: `feat(agents): phase 3 - /api/agents/analyze (intent + knowledge)`.

### Phase 4 — Upload kho tri thức + verify e2e

- **RESET** collection (`POST /api/rag/reset`) rồi **upload `knowledge_base_shop_quan_ao.pdf`** (KHÔNG upload
  intents-guide nữa — taxonomy đã ở prompt Agent 1).
- Chạy `/api/agents/analyze` vài câu chính sách/sản phẩm; kiểm intent (Agent 1) + rag_contexts hợp lý (Agent 2).

**Verify:** analyze "đổi trả trong bao lâu?" → intent=refund + context đổi trả; "size M nặng bao nhiêu kg?" →
intent=size_consulting + context bảng size; "asdf zxcv" → intent=other/unknown + `no_relevant_knowledge`. `make test` xanh.
Commit: `chore(agents): phase 4 - upload knowledge base + e2e verify`.

---

## 3. Definition of Done

- [ ] `make test` xanh; `run-demo` 2 nhánh đúng, `uncertainty_flags` **tích luỹ, không nhân đôi**.
- [ ] **Agent 1 sạch:** `/api/agents/classify` trả `{intent, category, entities, confidence, uncertainty_flags}`
      — **KHÔNG `rag_contexts`**, KHÔNG `low_retrieval_score`; taxonomy ở prompt (không gọi Qdrant). order_id vẫn đúng.
- [ ] **Agent 2 thật:** `retrieve_knowledge`/`knowledge_node` trả `rag_contexts` + `retrieval_confidence` + cờ
      `no_relevant_knowledge`/`low_retrieval_score`; degrade offline không ném lỗi.
- [ ] State: `rag_contexts` do **Agent 2** ghi; `intent_confidence`/`retrieval_confidence` tách riêng; cờ tích luỹ tới Decision.
- [ ] `/api/agents/analyze` cho thấy đúng tách vai; upload **kho tri thức** (không phải intents-guide) + e2e đạt.

---

## 4. Ghi chú cho Claude Code

- **Vai:** retrieval + `rag_contexts` + `low_retrieval_score`/`no_relevant_knowledge` thuộc **Agent 2**; intent +
  entities + `ambiguous/multi/out_of_domain` thuộc **Agent 1**. Đừng để Agent 1 gọi `rag_service` nữa.
- **Reducer:** khi `uncertainty_flags` thành `Annotated[..., add]`, MỌI node chỉ được trả **cờ MỚI của nó** (đừng
  trả lại cờ đã có) — nếu không sẽ nhân đôi. Đây là lý do phải chỉnh `decision_node`.
- **Taxonomy trong prompt** (module `taxonomy.py`), đầy đủ mô tả + ví dụ để bù cho việc bỏ retrieval; giữ entity
  schema + few-shot (gồm order_id "6578").
- **`search()` vẫn ở tầng service** — Agent 2 gọi; Agent 1 không. Degrade an toàn cả hai (offline → `make test` xanh).
- **Qdrant giờ chứa KHO TRI THỨC** (chính sách/FAQ/sản phẩm), không phải intent. Nhớ reset + upload lại (Phase 4).
- "Sửa có phẫu thuật"; async-first; config từ env. Response Generator vẫn là điểm phát ngôn duy nhất — `/classify`
  và `/analyze` chỉ trả metadata.
- Sau bước này (layer sau): Decision Engine thật (priority/severity + gate), Response Generator (grounded từ
  rag_contexts của Agent 2), suspend/resume — theo `docs/DEVELOPMENT.md`.
