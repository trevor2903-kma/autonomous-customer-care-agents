# PLAN — Lát cắt dọc (walking skeleton): Upload → Embed (Qdrant) → Intent Classifier phân loại theo RAG

> **Bản chất file này:** kịch bản ONE-SHOT để verify hệ thống ở mức cơ bản nhất — MỘT lát cắt dọc chạy thật,
> KHÔNG phải toàn bộ hệ. Xong thì bỏ. Nguồn chân lý vẫn là **`PRD.md`** (đặc biệt §7.1 Intent Classifier,
> §13 RAG). Repo hiện tại đã scaffold xong; plan này CẮM logic thật vào đúng chỗ đã chừa.
>
> **Mục tiêu (đúng yêu cầu):** admin upload tài liệu → **embed vào Qdrant** → khi khách chat, **Agent 1
> (Intent Classifier) phân loại intent dựa trên tài liệu RAG đó**. CHƯA cần lưu trữ tài liệu lâu dài (chỉ đẩy
> vector lên Qdrant, KHÔNG persist document xuống Postgres).
>
> **Quyết định kiến trúc (ghi rõ để không lệch PRD):** lát cắt này cho Intent Classifier **tự truy hồi** để
> phân loại. Trong kiến trúc đầy đủ (PRD §7.2), truy hồi là việc của Knowledge Agent — nên hàm `search()`
> viết ở **tầng service** (`rag_service`) để Knowledge Agent tái dùng về sau, KHÔNG nhét cứng vào node intent.

---

## 0. In / Out scope

**In scope:**

- Thêm khả năng **embeddings** (OpenAI `text-embedding-3-small` — đã có trong `config.EMBEDDING_MODEL`).
- Bootstrap **collection Qdrant** (tên `settings.qdrant_collection` = `knowledge`).
- **RAG service**: chunk tài liệu → embed → upsert Qdrant; và `search(query, top_k)`.
- **Route upload**: `POST /api/rag/upload` (nhận file .md/.txt) → embed → Qdrant.
- **Intent Classifier thật** (thay stub): truy hồi top-k intent từ Qdrant → chọn intent (LLM nếu
  `ENABLE_LLM`, ngược lại similarity top-1) → set `intent/category/entities/confidence/uncertainty_flags`.
- **Điểm test**: `POST /api/agents/classify` (chạy RIÊNG bước intent) + WS `/ws/chat` trả kết quả phân loại.

**Out of scope (giữ nguyên scaffold / để layer sau):**

- KHÔNG chạy đủ pipeline 4 agent cho lát cắt này (chỉ Agent 1). Decision/Response/human_handoff vẫn stub.
- KHÔNG persist tài liệu xuống Postgres (bảng `knowledge_document` để yên); KHÔNG RAG management UI, re-index.
- KHÔNG PDF/DOCX (chỉ .md/.txt); KHÔNG multi-provider (chỉ OpenAI); KHÔNG tách Knowledge Agent (Layer sau).
- KHÔNG gửi phản hồi "trả lời khách" — lát cắt chỉ trả **metadata phân loại** (Response Generator vẫn là
  điểm phát ngôn DUY NHẤT tới khách; wiring câu trả lời thật là việc sau).

---

## 1. Tài liệu test (đã có sẵn để upload)

`intents_seed_vi.md` — mỗi mục `## <intent_id>` là MỘT chunk; payload `{intent, category, text, source}`.
Đặt vào repo tại `fixtures/knowledge/intents_seed_vi.md` (tạo thư mục `fixtures/knowledge/`).

---

## 2. Dependencies & cấu hình

- **`apps/backend/pyproject.toml`** — thêm vào `dependencies`:
  - `openai>=1.40,<2` (embeddings + chat cho bước chọn intent)
  - `python-multipart>=0.0.9` (FastAPI cần để nhận `UploadFile`)
  - Cài: `cd apps/backend && uv sync` (hoặc `uv add openai python-multipart`).
- **`.env`** (gốc repo) — điền/đặt:
  - `ENABLE_LLM=true` (bật bước chọn intent bằng LLM; xem Phase 3 để hiểu chế độ fallback)
  - `LLM_PROVIDER=openai`, `LLM_API_KEY=<openai key>`, `LLM_MODEL=gpt-4o-mini`
  - `EMBEDDING_MODEL=text-embedding-3-small` (đã mặc định)
  - `QDRANT_URL`, `QDRANT_API_KEY`, `QDRANT_COLLECTION=knowledge` (đã có)
  - _(Không muốn dùng OpenAI? Xem "Ghi chú" cuối file — phương án fastembed local, không cần key.)_

**Verify:** `cd apps/backend && uv run python -c "import openai, multipart; print('deps ok')"`; `make health`
vẫn trả `ok` cho api + 3 dịch vụ (Qdrant reachable).

---

## 3. Kế hoạch theo Phase

> Sau MỖI phase: chạy "Verify", hiển thị output, `git commit` (`feat(rag-intent): phase N - ...`), tiếp nếu không lỗi.

### Phase 0 — Deps + config

Như mục 2. Commit: `feat(rag-intent): phase 0 - deps openai/multipart + env RAG/LLM`.
**Verify:** import deps ok; `/api/health` ok.

### Phase 1 — Embeddings + bootstrap collection

- Tạo **`app/core/embeddings.py`**:
  - `async embed_texts(texts: list[str]) -> list[list[float]]` và `async embed_text(text) -> list[float]`,
    dùng `AsyncOpenAI(api_key=settings.llm_api_key)` + `settings.embedding_model`.
  - `embedding_dim()` — suy ra số chiều bằng cách embed 1 chuỗi "dim probe" (tránh hardcode; `text-embedding-3-small`
    = 1536). Cache lại.
- Trong **`app/services/rag_service.py`** (tạo mới): `async ensure_collection()` — nếu collection chưa có →
  `create_collection(name=settings.qdrant_collection, vectors_config=VectorParams(size=embedding_dim(),
distance=Distance.COSINE))`. Idempotent (đã có thì bỏ qua).
- Gọi `ensure_collection()` lười (khi upload/search lần đầu) hoặc trong lifespan `main.py` (tùy — lười là đủ).

**Verify:** script nhỏ gọi `ensure_collection()` rồi `get_qdrant().get_collection(...)` in ra `points_count=0`

- vector size = 1536. Commit: `feat(rag-intent): phase 1 - embeddings + qdrant collection bootstrap`.

### Phase 2 — RAG ingest + route upload

- **`app/services/rag_service.py`** thêm:
  - `chunk_by_heading(text) -> list[dict]`: tách theo dòng bắt đầu `"## "`; mỗi section → `{intent: <heading>,
category: <parse dòng "- category:"> | None, text: <cả section>}`.
  - `async ingest_document(text: str, source: str) -> int`: `ensure_collection()` → chunk → `embed_texts` →
    `upsert` các point (id ổn định theo `source#intent`, payload `{intent, category, text, source}`) → trả số chunk.
  - `async collection_info() -> dict` (points_count) và `async reset_collection()` (drop + `ensure_collection`).
- Tạo **`app/api/routes/rag.py`** (`APIRouter(prefix="/rag", tags=["rag"])`):
  - `POST /upload` — `file: UploadFile`; chỉ nhận `.md`/`.txt`; đọc bytes → `decode("utf-8")` →
    `ingest_document(text, source=file.filename)` → `{ "source", "chunks", "collection" }`.
  - `GET /info` → `collection_info()`. `POST /reset` → `reset_collection()` (tiện test lại nhiều lần).
- **`app/main.py`**: `app.include_router(rag.router, prefix="/api")`.

**Verify:** `curl -F "file=@fixtures/knowledge/intents_seed_vi.md" http://localhost:8000/api/rag/upload`
→ `{"chunks": 10, ...}`; `GET /api/rag/info` → `points_count: 10`. Commit:
`feat(rag-intent): phase 2 - rag ingest service + /api/rag/upload`.

### Phase 3 — Intent Classifier thật (thay stub)

- **`app/services/rag_service.py`** thêm `async search(query: str, top_k: int = 3) -> list[dict]`: `embed_text(query)`
  → `query_points(collection, query=vec, limit=top_k, with_payload=True)` → list `{intent, category, text, score}`.
- **(Khuyến nghị, Layer-1 lite)** thêm `Intent(StrEnum)` vào `app/models/enums.py` (tập đóng theo PRD §7.1:
  product_price, product_information, size_consulting, shipping, order_status, refund, exchange, complaint,
  promotion, other). Dùng để validate nhãn LLM trả về (chống trôi nhãn).
- Viết **`app/agents/nodes/intent.py`** thật, tách hàm thuần để tái dùng:
  - `async classify_intent(text: str) -> dict` trả `{intent, category, entities, confidence, uncertainty_flags,
rag_contexts}`:
    1. `hits = await rag_service.search(text, top_k=3)`.
    2. Nếu `not hits` **hoặc** `settings.llm_api_key` trống **hoặc** Qdrant/collection lỗi → **degrade an toàn**:
       trả `intent="unknown", confidence=0.0, uncertainty_flags=["no_relevant_knowledge"]` (KHÔNG gọi network —
       giữ `make test` chạy offline).
    3. **Chế độ chọn intent:**
       - `ENABLE_LLM=true`: gọi LLM (`AsyncOpenAI`, `settings.llm_model`) với prompt: "Cho các intent ứng viên
         sau (kèm mô tả/ví dụ từ RAG) và câu khách, chọn 1 intent, trích entities, và độ tự tin". Output JSON
         (`response_format=json_object`). Validate intent ∈ `Intent`. Cờ: `ambiguous_intent` nếu LLM lưỡng lự /
         2 ứng viên đầu điểm sát nhau; `out_of_domain` nếu LLM chọn `other` với điểm truy hồi thấp.
       - `ENABLE_LLM=false`: **similarity top-1** — `intent = hits[0].intent`, `confidence = hits[0].score`,
         `entities = {}`. Cờ theo ngưỡng: `low_retrieval_score`/`out_of_domain` nếu `score < CONFIDENCE_THRESHOLD`;
         `ambiguous_intent` nếu `|score[0]-score[1]|` nhỏ.
  - `async intent_node(state)`: gọi `classify_intent(state["input"])`, set các field vào state + `trace`
    (`node="intent"`, confidence, `detail={"top": [...]} `), `status=CLASSIFYING`. Giữ chữ ký node như cũ.
  - _Lưu ý:_ node vẫn phải hoạt động trong graph (`build_graph`) — chỉ Agent 1 có logic thật; knowledge/decision/
    response vẫn stub. `make test` phải xanh (nhờ degrade an toàn ở bước 2).

**Verify:** `cd apps/backend && uv run python -c "..."` gọi `classify_intent("áo này còn size M không shop?")`
→ intent hợp lý (`product_information`/`size_consulting`); `make test` xanh. Commit:
`feat(rag-intent): phase 3 - intent classifier RAG (search + LLM/similarity) + Intent enum`.

### Phase 4 — Điểm test: REST classify + wire WebSocket

- **`app/api/routes/agents.py`** thêm `POST /classify` (body `{ "message": str }`) → `classify_intent(message)`
  → trả `{intent, category, entities, confidence, uncertainty_flags, rag_contexts: [{intent, score}]}`. Chạy
  RIÊNG Agent 1 (KHÔNG chạy cả graph).
- **`app/api/ws/chat.py`**: khi nhận text của khách → `classify_intent(text)` → gửi lại
  `{"type": "classification", intent, confidence, entities}` (thay `echo`). Đây là **tín hiệu dev/verify**, KHÔNG
  phải câu trả lời cuối cho khách (Response Generator lo việc đó sau — PRD §7.4).

**Verify:** `curl -s -X POST /api/agents/classify -H 'Content-Type: application/json' -d '{"message":"đơn 1234 tới đâu rồi"}'`
→ `intent=order_status`; mở WS gửi câu bất kỳ → nhận `type=classification`. Commit:
`feat(rag-intent): phase 4 - /api/agents/classify + ws classification`.

### Phase 5 — Verify lát cắt (bộ câu test)

- Tạo **`scripts/verify_intent.py`**: danh sách ~10–12 câu khách (giọng KHÁC ví dụ trong seed để không "học vẹt")
  kèm intent kỳ vọng → gọi `classify_intent` (hoặc `/api/agents/classify`) → in `dự đoán vs kỳ vọng` + tỉ lệ đúng.
- Ngưỡng sanity (KHÔNG phải KPI PRD): ≥ ~8/10 đúng là đạt cho lát cắt verify.

**Verify:** chạy `uv run python scripts/verify_intent.py` → in bảng + accuracy ≥ ngưỡng. Commit:
`feat(rag-intent): phase 5 - verify script cho intent qua RAG`.

---

## 4. Definition of Done

- [ ] `uv sync` xong với `openai` + `python-multipart`; `/api/health` ok.
- [ ] `POST /api/rag/upload` với `intents_seed_vi.md` → `chunks = 10`; `GET /api/rag/info` → `points_count = 10`.
- [ ] `classify_intent()` phân loại đúng ≥ ~8/10 câu test (Phase 5), có `confidence` + `uncertainty_flags` + `rag_contexts`.
- [ ] `POST /api/agents/classify` trả intent đúng; WS `/ws/chat` trả `type=classification` khi khách chat.
- [ ] `make test` vẫn xanh (intent_node degrade an toàn khi offline; các node khác vẫn stub).
- [ ] KHÔNG persist tài liệu xuống Postgres; embeddings chỉ nằm ở Qdrant.
- [ ] Chỉ Agent 1 có logic thật; Response Generator vẫn là điểm phát ngôn duy nhất (lát cắt chỉ trả metadata).

---

## 5. Ghi chú cho Claude Code

- **Embeddings KHÔNG bị gate bởi `ENABLE_LLM`** — RAG cần embeddings để chạy. `ENABLE_LLM` chỉ gate **bước chọn
  intent bằng LLM** (bật → LLM chọn + trích entities; tắt → similarity top-1). Cả hai chế độ đều "phân loại theo RAG".
- **Giữ `make test` chạy offline:** mọi lệnh gọi network trong `intent_node` phải đi qua nhánh degrade an toàn
  khi thiếu key / Qdrant lỗi / collection trống → trả `unknown` + cờ, KHÔNG ném lỗi.
- **Async-first, config từ env** (CLAUDE.md): dùng `AsyncOpenAI`, `AsyncQdrantClient`; không hardcode key/URL/model.
- **`search()` ở tầng service** (`rag_service`) để Knowledge Agent (PRD §7.2) tái dùng — đừng nhét truy hồi cứng
  vào node intent.
- **Chống trôi nhãn:** validate intent LLM trả về ∈ `Intent` enum; nếu lệch → coi như `other` + `out_of_domain`.
- **Phương án không dùng OpenAI (tùy chọn):** thay `embeddings.py` bằng `fastembed` (qdrant-client hỗ trợ, chạy
  local, không cần API key) và bỏ bước LLM (chỉ similarity top-1). Đổi `EMBEDDING_MODEL` + `embedding_dim()` cho khớp.
- **Sau lát cắt này** (không làm ở đây): tách Knowledge Agent, chạy đủ pipeline, gate/PENDING_APPROVAL, phản hồi
  khách thật qua Response Generator, PDF/DOCX ingest, RAG management — theo `docs/DEVELOPMENT.md` (Layer 1→4).
