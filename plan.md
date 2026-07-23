# plan.md — Refactor RAG/Knowledge: KB có cấu trúc · Taxonomy mới · Retrieve theo intent · Facts layer · Đo threshold

> Repo: `github.com/trevor2903-kma/autonomous-customer-care-agents`
> BE `apps/backend` (FastAPI + LangGraph + Alembic). Scripts ở **gốc repo** `scripts/`. `.env` ở **gốc repo**.
> Nguyên tắc (CLAUDE.md): cấu hình từ env, **KHÔNG hardcode** secret/URL/ngưỡng. Sửa **có phẫu thuật**.

---

## 0. Mục tiêu & bối cảnh

Hoàn thiện **phần lõi tri thức** theo mô hình học từ bot V2 (Avada), gắn thẳng vào pipeline 4-agent cố định
(không thay kiến trúc). Đồng thời **sửa 2 lỗi phân loại** đang gặp (chào hỏi → `out_of_domain`; hỏi chính sách
đổi/trả → `refund` bị bắt duyệt). Shop là **thời trang hàng mới** (kiểu Uniqlo).

**Trạng thái nền hiện tại (đã đọc code):**

- **Nạp**: `/rag/upload` file → `rag_service.ingest_document` → `chunk_text` cắt câu ~800/overlap 120 → Qdrant
  payload **trơn** `{text, source, chunk_index}`. `search()` = `query_points` (Distance.COSINE, top_k, **không** filter/score_threshold). `reset_collection` = delete + recreate.
- **Agent 2** (`knowledge.py`): retrieve bằng **`state["input"]` thô**; `rag_contexts=[{text,source,score}]`;
  `retrieval_confidence = hits[0].score`; cờ `low_retrieval_score` nếu `< retrieval_threshold` (0.35). `intent` **không** dùng cho retrieve.
- **Agent 1** (`intent.py`): prompt Quy tắc 1 map **chào hỏi → `other`** và **hỏi chính sách đổi/trả → `refund`**; `intent==other` → cờ `out_of_domain`.
- **Agent 3** (`decision.py`): escalation **theo cờ** (`BLOCKING_FLAGS` 6 cờ), **không blend điểm**; bảng `_PRIORITY_SEVERITY` theo intent.
- **Agent 4** (`response.py`): `_system_prompt` ngắn, **không facts**; grounded thuần `rag_contexts`; rỗng → FALLBACK.
- **Gate** (`gate_service.py`): `holds_auto_reply` đọc `gate_config` (master `auto_reply_enabled` + `send_directly_for(intent)`); **`send_directly_for` trả `False` cho intent KHÔNG có luật** → giữ nháp. `gate_intent_rule` seed 10 intent (migration `c3f1a9d47b28`).
- Canonical KB mới → **`apps/backend/knowledge/`** (bộ starter đã tạo). `fixtures/knowledge/` (PDF cũ) **không được tham chiếu ở đâu** → xoá.

---

## 1. Bất biến kiến trúc (KHÔNG phá)

- Pipeline 4-agent cố định, **không Supervisor**. **Agent 4 là egress DUY NHẤT của luồng tự động**.
- **Grounding**: chỉ nói từ tri thức được cấp (giờ = `facts.md` luôn-bật **+** `rag_contexts`); không đủ → FALLBACK/handoff. **Grounding cả HÀNH ĐỘNG** (không hứa hoàn tiền/tra đơn khi chưa có năng lực → escalate).
- **Agent 3 tất định, theo cờ, KHÔNG blend điểm**. Escalation an toàn (BLOCKING_FLAGS) **không** đổi logic.
- **Một ngưỡng số duy nhất** liên quan escalation = `retrieval_threshold` ở **Agent 2** (điểm cosine top-1 → cờ `low_retrieval_score`). Agent 3 chỉ đọc cờ.
- **Reset-and-reingest**: `knowledge/` là nguồn chân lý; Qdrant là bản phái sinh, dựng lại từ repo. Upload UI = ad-hoc **non-canonical**.
- 1 worker; hub in-process; không đụng ở slice này.

---

## 2. Thiết kế cốt lõi (chốt trước khi code)

### 2.1 Tập intent MỚI (14) — khớp 1-1 ở 4 NƠI

`enums.Intent` (nguồn chuẩn) → `taxonomy.py` (mô tả/ví dụ) → **seed `gate_intent_rule`** (migration) → **frontmatter `intent:`** trong `knowledge/**/*.md`.

| Nhóm          | intent                                                                                                                                          | nhạy cảm              | `send_directly` (gate) | priority/severity                                              |
| ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | --------------------- | ---------------------- | -------------------------------------------------------------- |
| Thông tin     | product_price, product_information, size_consulting, shipping, order_status, promotion, **payment**, **return_exchange_policy**, **membership** | không                 | **true** (gửi thẳng)   | low/low (order_status = medium/low)                            |
| Chào hỏi      | **greeting**                                                                                                                                    | không                 | true                   | low/low                                                        |
| Giao dịch     | refund, exchange, complaint                                                                                                                     | **có**                | **false** (duyệt nháp) | refund high/medium · exchange medium/low · complaint high/high |
| Ngoài phạm vi | other                                                                                                                                           | — (→ `out_of_domain`) | —                      | low/low                                                        |

> **4 intent MỚI**: `greeting`, `return_exchange_policy`, `payment`, `membership`.
> **⚠️ GOTCHA bắt buộc**: mọi intent mới PHẢI có dòng `gate_intent_rule` (`send_directly=true`) — vì `send_directly_for` trả `False` cho intent **không có luật** → thiếu là bị **bắt duyệt oan**.

### 2.2 Sửa 2 lỗi ở Agent 1 (`taxonomy.py` + `intent.py`)

- **Chào hỏi/cảm ơn → `greeting`** (KHÔNG còn `other` → hết cờ `out_of_domain` → hết escalate).
- **HỎI chính sách/thời hạn đổi–trả–hoàn → `return_exchange_policy`** (thông tin, không nhạy cảm). Giữ `refund`/`exchange`/`complaint` cho **yêu cầu thực trên đơn cụ thể**.
- `other` = _thật sự ngoài phạm vi_ (vé xem phim…) mới `out_of_domain`.

### 2.3 Schema KB + payload

- Canonical: `apps/backend/knowledge/{faq,case,reference}/*.md` (+ `facts.md`, + `promotion/` cho KM định kỳ). Bộ starter đã có.
- **Thư mục = `type`** (ingest suy `type` từ tên thư mục). Frontmatter: faq `intent/title/questions`; case thêm `applies_when` + thân có `## Bot Diagnostic Flow`; reference `intent?/title`; facts chỉ `title`.
- **Payload mới mỗi chunk**: `{text, source, chunk_index, type, intent, title}`.

### 2.4 Chunking mới

- **Chunk theo section (`##`)**; **giữ `## Bot Diagnostic Flow` nguyên một chunk** (đừng cắt câu). Sentence-window cũ = **fallback** khi một section quá dài (> ngưỡng ký tự).
- **Query-expansion**: với faq/case có `questions[]`, upsert **thêm một point mỗi câu hỏi** — `vector = embed(câu hỏi)`, `payload.text = thân trả lời`. ID ổn định (vd `uuid5(source#type#i#q{j})`) để reset/reingest idempotent.

### 2.5 Retrieve theo intent (Agent 2)

- `search(query, top_k, intent=None)`: khi có `intent` (≠ `other`) → thử `query_filter` theo `payload.intent`; nếu **ít kết quả / điểm thấp / rỗng** → chạy lượt **không filter** rồi **gộp-khử-trùng** theo score, giữ top_k. Không hard-fail khi filter rỗng.
- `knowledge_node` truyền `state["intent"]`; `rag_contexts` mang thêm **`type`, `title`**.

### 2.6 Facts layer (Agent 4)

- Nạp `apps/backend/knowledge/facts.md` **lúc khởi động** (đọc 1 lần, cache) → ghép **luôn** vào `_system_prompt` (khối "SỰ THẬT CỬA HÀNG"). Facts là tri thức được cấp → không phá phanh grounding.
- **Dung hoà phanh**: giữ phanh cứng (rag_contexts rỗng → FALLBACK). Để câu cơ bản (phí ship…) vẫn trả lời được, **dựa vào coverage KB + query-expansion** (đưa các sự thật lõi vào `reference/faq` để retrieve không trượt), KHÔNG nới phanh. Ghi quyết định này vào báo cáo.

### 2.7 Ngưỡng `retrieval_threshold`

- **Cơ chế giữ nguyên** (cosine top-1 → cờ). **Đo lại giá trị** trên KB mới (§ P6). Lưu ý query-expansion đẩy điểm faq cao → ngưỡng canh chủ yếu cho hit _thân_ reference/case.

---

## 3. Các pha (P0–P7) — Claude Code chạy tuần tự, commit từng pha

### P0 — Dọn & đặt chỗ `chore(kb): P0 setup knowledge dir + remove fixtures`

- **In:** xoá `fixtures/` (`git rm -r fixtures` — đã xác nhận không code nào tham chiếu); copy bộ KB starter vào **`apps/backend/knowledge/`** (faq/case/reference/facts.md/README/promotion). Thêm dep **`python-frontmatter`** vào `apps/backend/pyproject.toml`.
- **Out:** logic ingest/agent.
- **Verify:** `apps/backend/knowledge/` có cây file; `fixtures/` đã biến mất; `uv sync` cài được frontmatter.

### P1 — Taxonomy mới đầu-cuối (sửa 2 lỗi + đồng bộ intent) `feat(intent): P1 new taxonomy + fix greeting/policy routing`

- **In:**
  - `enums.Intent`: thêm `greeting`, `return_exchange_policy`, `payment`, `membership` + mục `INTENT_CATEGORY`.
  - `taxonomy.py`: mô tả/ví dụ 4 intent mới; **sửa Quy tắc 1** (§2.2): chào hỏi→`greeting`, hỏi-chính-sách→`return_exchange_policy`.
  - `decision.py` `_PRIORITY_SEVERITY`: thêm 4 dòng mới (theo bảng §2.1 — mặc định low/low).
  - **Migration Alembic mới**: thêm 4 dòng `gate_intent_rule` (`send_directly=true`) cho intent mới. **⚠️ GOTCHA §2.1**.
  - Frontmatter KB **đã** dùng đúng các intent này (starter set) — chỉ cần khớp.
- **Out:** ingestion/retrieval (P2+).
- **Verify:** classify "xin chào" → `greeting`, **không** cờ `out_of_domain`; "xin chính sách trả hàng" → `return_exchange_policy`; `gate_intent_rule` có đủ 14 intent; `send_directly_for("greeting")=true`.
- **Stop-point:** báo user chạy `alembic upgrade head`.

### P2 — Ingestion refactor (frontmatter + chunk-theo-section + query-expansion) `feat(rag): P2 structured ingest from repo + query expansion`

- **In:**
  - `rag_service`: parse frontmatter (suy `type` từ thư mục); **chunk theo `##`** (giữ Bot Diagnostic Flow nguyên khối; fallback sentence-window cho section dài); **query-expansion** (§2.4); payload mới `{text,source,chunk_index,type,intent,title}`; ID ổn định.
  - **`scripts/ingest_kb.py`** (theo pattern `seed_admin.py`: `sys.path.insert(apps/backend)` + `load_dotenv(.env gốc)`): duyệt `apps/backend/knowledge/` → **`reset_collection` → upsert**; **bỏ qua `facts.md`** (Agent 4 nạp riêng); in số doc/chunk. Thêm **Makefile target** `ingest-kb`.
- **Out:** UI/console (P3), retrieve theo intent (P4).
- **Verify:** `make ingest-kb` chạy sạch; Qdrant có point với payload đủ `type/intent/title`; một câu hỏi FAQ khớp điểm cao (query-expansion); case doc giữ nguyên khối flow.
- **Stop-point:** báo user cần `.env` (QDRANT + OPENAI) và chạy `make ingest-kb`.

### P3 — Console tài liệu (persist + đổi vai `/rag/*`) `feat(rag): P3 knowledge_document persist + rag endpoints re-role`

- **In:**
  - Persist **`knowledge_document`** (source/title/type/intent/format/status/chunks/indexed_at) khi ingest (repo) + khi upload ad-hoc. Migration nếu bảng chưa có/đủ cột.
  - **Đổi vai endpoint**: `GET /rag/documents` (từ `knowledge_document`) cho bảng UI; `POST /rag/reindex` (chạy ingest-from-repo); giữ `POST /rag/reset`; `POST /rag/upload` = **ad-hoc**, `source=upload`, đánh dấu **non-canonical**.
  - FE `apps/dashboard` (nếu làm luôn): bảng "Tài liệu" đọc `/rag/documents`; nút Re-index/Xóa/Upload theo vai mới; badge "tạm thời/non-canonical" cho doc upload.
- **Out:** không đụng pipeline.
- **Verify:** ingest → bảng liệt kê doc repo với chunks/status thật; upload ad-hoc → hiện badge non-canonical; reindex-from-repo chạy.

### P4 — Agent 2 retrieve theo intent `feat(rag): P4 intent-aware retrieval + typed contexts`

- **In:** `search(query, top_k, intent=None)` (§2.5, filter + fallback gộp); `knowledge_node` truyền `state["intent"]`; `rag_contexts` mang `type`, `title`. Cơ chế cờ **giữ nguyên**.
- **Out:** đo threshold (P6).
- **Verify:** truy vấn intent cụ thể ưu tiên đúng chunk cùng intent; intent lạ/không match không bị rỗng (fallback hoạt động).

### P5 — Agent 4 facts + greeting + bám flow + grounding hành động `feat(rag): P5 facts layer + flow-following + action grounding`

- **In:**
  - Nạp `knowledge/facts.md` lúc khởi động → khối facts luôn-bật trong `_system_prompt` (§2.6).
  - `greeting` → **câu chào mẫu** (bỏ qua nhánh grounding RAG).
  - `_context_block` gắn nhãn loại (`[Quy trình xử lý]` cho `type=case`, `[Tra cứu]` cho reference) + luật **bám diagnostic flow từng bước**.
  - Luật **grounding hành động** (không hứa hoàn tiền/tra đơn khi chưa có năng lực → escalate). (Tuỳ chọn: luật văn phong.)
- **Out:** đo threshold.
- **Verify:** hỏi phí ship → trả từ facts kể cả retrieve mỏng; case "đơn giao chậm" → bot **hỏi mã đơn trước** (bám flow); "xin chào" → chào mẫu, không escalate; không có câu "đã hoàn tiền cho bạn".

### P6 — Đo & đặt `retrieval_threshold` `chore(rag): P6 measure retrieval threshold on new KB`

- **In:**
  - Dựng 2 tập truy vấn (trả-lời-được / không-trả-lời-được), mỗi tập ~20–40 câu (có thể để trong `apps/backend/tests/` hoặc `scripts/`).
  - Script đo (tận dụng `verify_intent.py` pattern): chạy retrieval, thu **điểm cosine top-1** mỗi câu → in phân bố / phân vị → gợi ý ngưỡng nằm trong "khe".
  - Đặt `retrieval_threshold` mới (env). Ghi **phương pháp + số liệu** vào `docs/` (cho Chương 4).
- **Out:** —
- **Verify:** tập trả-lời-được phần lớn ≥ ngưỡng; tập không-trả-lời-được phần lớn < ngưỡng; ít `low_retrieval_score` oan.

### P7 — Kiểm thử & đo tổng `test(rag): P7 e2e verify + inspector chunks/scores`

- **In:**
  - Kiểm chứng **2 lỗi đã sửa** (greeting auto-reply; return_exchange_policy auto-reply, không duyệt nháp).
  - **Mở rộng Pipeline Inspector** (`/api/agents/pipeline` + AnalyzePanel): hiện _chunk retrieve + điểm số_ của Agent 2 (`type/title/source/score`).
  - Ghi **số liệu trước/sau** (hit-rate, escalation rate) vào `docs/`.
- **Verify:** kịch bản đầu-cuối chạy; Inspector hiện chunk+score.

---

## 4. Ghi chú cho Claude Code

- Đọc `apps/backend/CLAUDE.md`. Cấu hình từ **`.env` gốc repo**; **KHÔNG hardcode**.
- **Scripts ở gốc `scripts/`**, theo pattern `seed_admin.py`: `_REPO_ROOT=parents[1]` · `load_dotenv(_REPO_ROOT/.env)` · `sys.path.insert(_REPO_ROOT/'apps'/'backend')` · chạy `cd apps/backend && uv run python ../../scripts/<x>.py`.
- **KHÔNG phá bất biến §1**: pipeline cố định/egress Agent 4 duy nhất; grounding (facts+RAG, không bịa→handoff, grounding hành động); Agent 3 theo-cờ-không-blend; một ngưỡng số ở Agent 2; Reset-and-reingest; 1 worker/hub in-process.
- **Đồng bộ intent 4 nơi** (§2.1) — và **GOTCHA gate_intent_rule** cho intent mới (thiếu = duyệt oan).
- FE: **Tailwind thuần + TanStack, KHÔNG shadcn**. Sửa có phẫu thuật.
- Commit **từng pha** với prefix ở tiêu đề. Có thể dừng/nghỉ giữa các pha.
- **Stop-point bắt buộc:** (P1) chạy `alembic upgrade head`; (P2) `.env` QDRANT+OPENAI + `make ingest-kb`; (P3) migration `knowledge_document` nếu cần; (P6) chạy script đo threshold rồi đặt giá trị vào `.env`.

## 5. Phạm vi & không-phạm-vi

- **Trong:** dọn fixtures + KB vào repo; taxonomy mới (sửa 2 lỗi) + đồng bộ intent; ingest-from-repo (frontmatter + chunk-theo-section + query-expansion + payload); console `knowledge_document` + đổi vai `/rag/*`; Agent 2 intent-aware; Agent 4 facts + bám flow + grounding hành động; đo threshold; Inspector chunk+score.
- **Ngoài (sau):** sàn điểm từng-context (lọc nhiễu); corrections-pipeline/learning-loop (15, trụ cột 4); observability (12); anti-injection (13); deploy (14); ngữ cảnh xuyên-ca (17).
