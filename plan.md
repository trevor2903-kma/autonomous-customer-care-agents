# PLAN — Nạp tài liệu thật (PDF/Word) + UI Admin + Intent Classifier (intent + ENTITIES) theo RAG

> **Bản chất:** kịch bản ONE-SHOT, xong thì bỏ. Nguồn chân lý vẫn là **`PRD.md`** (§7.1 Intent Classifier —
> output có **intent + entities**; §7.2 Knowledge Agent; §13 RAG; §17 Module 1 RAG Management). Repo đã scaffold
>
> - đã có bản intent classifier seed-based; plan này **thay** phần xử lý tài liệu bằng nạp file thật, thêm UI,
>   và **sửa luôn bug entities rỗng**.
>
> **Gộp 2 việc:** (A) admin **upload file thật (PDF/Word/txt/md)** → **trích văn bản → chunking TỔNG QUÁT →
> embed vào Qdrant**, kèm **UI Quản lý tri thức**; (B) **Intent Classifier trích ĐÚNG entities** (vd
> `order_id`) thay vì trả `{}`. CHƯA cần lưu trữ tài liệu lâu dài (chỉ đẩy vector lên Qdrant).

---

## 0. Quyết định kiến trúc (đọc trước — thay code seed hiện tại)

- **Chunking TỔNG QUÁT** (recursive theo đoạn/câu + overlap), KHÔNG theo heading `##`. **Thay** `chunk_by_heading`
  hiện có (chỉ hợp file seed cấu trúc sẵn).
- **Payload chunk GENERIC** `{text, source, chunk_index}` — **bỏ** nhãn `intent`/`category` trên chunk (payload
  seed cũ). ⚠️ Payload đổi → **sau khi deploy phải `POST /api/rag/reset` rồi upload lại** (vector cũ không tương thích).
- **Intent do LLM quyết** từ chunk truy hồi + tập `Intent` enum đóng. Vì chunk generic không mang nhãn nên **đường
  similarity-top-1-nhãn không dùng được nữa** → **LLM bắt buộc cho intent**. Không LLM / offline / LLM lỗi →
  **degrade `intent=unknown`** (+ cờ), nhưng **entities vẫn được trích bằng regex** (xem dưới). `make test` vẫn offline OK.
- **Entities** (fix bug rỗng): kết hợp **LLM (schema + few-shot)** ⊕ **regex** (`order_id`, neo theo từ khoá) →
  merge `entities = {**regex, **llm}`. Regex chạy ở **mọi nhánh** (kể cả degrade) → `order_id` luôn bắt được.
- **`category`** lấy từ **map tĩnh `INTENT_CATEGORY`** (chunk generic không mang category).
- Truy hồi (`search`) giữ ở **tầng service** để Knowledge Agent (PRD §7.2) tái dùng.

---

## 1. In / Out scope

**In scope — Backend:** deps `openai`/`python-multipart`/`pypdf`/`python-docx`; embeddings + bootstrap collection;
**trích đa định dạng (.pdf/.docx/.txt/.md) + chunking tổng quát + ingest (payload generic)**; route
`POST /api/rag/upload` + `/info` + `/reset`; enums `Intent`/`Category` + `INTENT_CATEGORY`; **Intent Classifier
LLM (intent) + ENTITIES (LLM schema/few-shot ⊕ regex)**; `POST /api/agents/classify` + WS.

**In scope — Frontend:** trang **Quản lý tri thức (RAG)** `app/rag/page.tsx` (upload file, xem số chunk + nguồn,
reset) + **widget test phân loại** hiển thị intent/category/confidence/cờ/**entities**/nguồn.

**Out of scope (giữ nguyên / layer sau):** KHÔNG chạy đủ pipeline 4 agent (chỉ Agent 1); Knowledge/Decision/
Response/human_handoff GIỮ stub. KHÔNG persist tài liệu xuống Postgres (bảng `knowledge_document` để yên).
KHÔNG OCR PDF scan; KHÔNG multi-provider (chỉ OpenAI); KHÔNG re-index/versioning nâng cao; KHÔNG shadcn.
KHÔNG gửi câu trả lời cho khách (chỉ metadata phân loại; Response Generator vẫn là điểm phát ngôn DUY NHẤT).

---

## 2. Tài liệu test & Dependencies

- Test: `tai_lieu_intents_shop_quan_ao.pdf` (guide 10 intent, PRD §7.1, văn xuôi + ví dụ) — upload qua UI/curl.
- `apps/backend/pyproject.toml` thêm: `openai>=1.40,<2` (đã có), `python-multipart>=0.0.9` (đã có),
  `pypdf>=5,<6`, `python-docx>=1.1,<2` → `cd apps/backend && uv sync`.
- `.env` (gốc repo): `ENABLE_LLM=true`, `LLM_PROVIDER=openai`, `LLM_API_KEY=<openai key>`, `LLM_MODEL=gpt-4o-mini`,
  `EMBEDDING_MODEL=text-embedding-3-small`, `QDRANT_URL/QDRANT_API_KEY/QDRANT_COLLECTION` (đã có).
- Frontend: không dep mới (FormData native + TanStack có sẵn).

**Verify:** `uv run python -c "import openai, multipart, pypdf, docx; print('deps ok')"`; `make health` ok.

---

## 3. Kế hoạch theo Phase

> Sau MỖI phase: chạy "Verify", cho tôi xem output, `git commit` (`feat(rag): phase N - ...`), tóm tắt 1 dòng, tiếp nếu không lỗi.

### Phase 0 — Deps + config

Như mục 2. Commit: `feat(rag): phase 0 - deps (pypdf/python-docx) + env LLM/RAG`. **Verify:** import ok; health ok.

### Phase 1 — Embeddings + bootstrap collection

- `app/core/embeddings.py`: `embed_text`/`embed_texts` (`AsyncOpenAI(api_key=settings.llm_api_key)` +
  `settings.embedding_model`) + `embedding_dim()` (probe, cache; 1536).
- `app/services/rag_service.py`: `ensure_collection()` (COSINE, size=`embedding_dim()`), idempotent.

**Verify:** collection tồn tại, vector size 1536. Commit: `feat(rag): phase 1 - embeddings + qdrant collection`.

### Phase 2 — Trích đa định dạng + chunking TỔNG QUÁT + ingest (thay chunk_by_heading)

- `app/services/extract.py`: `extract_text(filename, data: bytes) -> str` — `.pdf`→`pypdf.PdfReader(BytesIO)`;
  `.docx`→`docx.Document(BytesIO)` (nối `paragraph.text`); `.txt`/`.md`→`decode("utf-8", errors="ignore")`;
  đuôi khác→`ValueError`.
- `rag_service.py`:
  - **XOÁ** `chunk_by_heading`; thêm `chunk_text(text, size=800, overlap=120) -> list[str]` (chuẩn hoá khoảng
    trắng → tách `\n\n` → gộp cửa sổ ~`size` ký tự, ~`overlap` chồng lấn, ưu tiên ranh giới câu). KHÔNG theo heading.
  - `ingest_document(text, source) -> int`: `ensure_collection()` → `chunk_text` → `embed_texts` → `upsert`
    (id `uuid5(source#i)`; **payload `{text, source, chunk_index:i}`**). Trả số chunk.
  - `collection_info() -> {collection, points_count, sources[]}` (sources: `scroll` gom distinct `payload.source`);
    `reset_collection()` (drop + `ensure_collection`).

**Verify:** unit — `extract_text` đọc PDF ra chữ tiếng Việt; `chunk_text` ra N>1 chunk (payload generic). Commit:
`feat(rag): phase 2 - multi-format extract + generic chunking + ingest`.

### Phase 3 — Route upload

- `app/api/routes/rag.py` (`prefix="/rag"`): `POST /upload` (`UploadFile`, chỉ .pdf/.docx/.txt/.md else 415;
  `extract_text` → rỗng thì 422; `ingest_document` → `{source, chunks, collection}`); `GET /info`; `POST /reset`.
- `app/main.py`: `include_router(rag.router, prefix="/api")`.

**Verify:** `curl -F "file=@tai_lieu_intents_shop_quan_ao.pdf" .../api/rag/upload` → `chunks>0`; `/api/rag/info`
→ `points_count` + `sources` có tên file. Commit: `feat(rag): phase 3 - /api/rag/upload (pdf/docx/txt/md) + info + reset`.

### Phase 4 — Enums + Intent Classifier (LLM cho intent) + ENTITIES (fix bug rỗng)

- `app/models/enums.py`: `Intent(StrEnum)` (product_price, product_information, size_consulting, shipping,
  order_status, refund, exchange, complaint, promotion, other); `Category(StrEnum)` (pre_sale, after_sale,
  general); `INTENT_CATEGORY: dict[Intent, Category]` (price/info/size/promotion→pre_sale; order_status/refund/
  exchange/complaint→after_sale; shipping/other→general).
- `rag_service.search(query, top_k=4) -> [{text, source, score, chunk_index}]` (payload generic; **bỏ** intent/category).
- **Entities helper** `extract_entities_rule(text) -> dict` (trong `intent.py` hoặc `nodes/_entities.py`):
  - `order_id`: regex **neo theo từ khoá** (unicode, ignorecase):
    `r"(?:đơn(?:\s*hàng)?|order|mã(?:\s*đơn)?|#)\D{0,8}(\d{3,})"` → `{"order_id": "<số>"}` (giá trị **chuỗi**).
  - (tuỳ chọn) `size`: `r"\bsize\s*([SMLX]{1,3}|\d{2,3})\b"`; `height`/`weight`: `r"(\d[.,]?\d*\s*m|\d{2,3}\s*cm)"`,
    `r"(\d{2,3})\s*kg"`. Cẩn thận không nhặt nhầm (neo từ khoá + giữ chuỗi).
- Viết lại `app/agents/nodes/intent.py`:
  - `classify_intent(text)`:
    1. `rule = extract_entities_rule(text)` (tính sớm — dùng cho MỌI nhánh).
    2. Thiếu `llm_api_key` → degrade: `intent="unknown", category=None, entities=rule, confidence=0.0,
uncertainty_flags=["llm_unavailable"], rag_contexts=[]` (không network).
    3. `hits = await search(text)`; lỗi → degrade `["search_error"]` + `entities=rule`; `not hits` → degrade
       `["no_relevant_knowledge"]` + `entities=rule` + `rag_contexts=[]`.
    4. `ENABLE_LLM=true`: gọi LLM (`AsyncOpenAI`, `settings.llm_model`, `response_format=json_object`, temp 0) với
       (a) **nhãn hợp lệ = `Intent` enum**, (b) **schema entity theo intent** + **few-shot** (xem dưới), (c) các
       đoạn `hits[].text` làm ngữ cảnh, (d) câu khách. Output JSON `{intent, entities, confidence}`.
       - Validate `intent ∈ Intent`; lệch → `"other"` + cờ `out_of_domain`.
       - `entities = {**rule, **(llm.entities if dict else {})}` (LLM đè trùng key; regex bù key thiếu).
       - `category = INTENT_CATEGORY.get(intent)`; `rag_contexts = [{source, score} for hits]`;
         cờ `low_retrieval_score` nếu `hits[0].score < CONFIDENCE_THRESHOLD`, `ambiguous_intent` nếu 2 điểm đầu sát nhau.
       - LLM lỗi (exception) → degrade `intent="unknown"` + cờ **`llm_unavailable`** + `entities=rule` +
         `rag_contexts=[{source,score}]` (đừng ném lỗi; đừng im lặng — cờ để chẩn đoán).
    5. `ENABLE_LLM=false` → degrade `intent="unknown"` + cờ `["llm_unavailable"]` + `entities=rule` +
       `rag_contexts=[{source,score}]` (chunk generic không phân loại được nếu không LLM).
  - `intent_node(state)` giữ chữ ký; ghi state + `trace`. Chỉ Agent 1 có logic thật; node khác GIỮ stub.
  - **make test phải xanh** (mọi nhánh degrade KHÔNG network, KHÔNG ném lỗi).
- **Prompt LLM (entity schema + few-shot):** yêu cầu chỉ chọn intent ∈ enum; trích entities theo schema:
  order_status/refund/exchange/complaint→`order_id`; product_price/product_information→`product_name`,`color`;
  size_consulting→`height`,`weight`,`size`; shipping→`destination`(+option `order_id`); promotion→`promo_code`;
  other→{}. Giá trị **chuỗi**; `order_id` chỉ chữ số; không bịa key ngoài schema. Few-shot gồm:
  - `"Đơn hàng 6578 của tôi sắp giao tới nơi chưa?"` → `{"intent":"order_status","entities":{"order_id":"6578"}}`
  - `"Mình cao 1m60 nặng 50kg mặc size gì?"` → `{"intent":"size_consulting","entities":{"height":"1m60","weight":"50kg"}}`

**Verify:** `classify_intent("Đơn hàng 6578 của tôi sắp giao tới nơi chưa?")` → `intent=order_status`,
`category=after_sale`, `entities.order_id=="6578"`; `make test` xanh. Commit:
`feat(rag): phase 4 - enums + LLM intent + entity extraction (schema+few-shot+regex)`.

### Phase 5 — Điểm test backend: classify + WS

- `app/api/routes/agents.py`: `POST /classify` (body `{message}`) → `classify_intent` → trả
  `{intent, category, entities, confidence, uncertainty_flags, rag_contexts:[{source,score}]}`.
- `app/api/ws/chat.py`: text khách → `classify_intent` → gửi `{"type":"classification", intent, category,
confidence, entities}` (thay echo). Tín hiệu dev/verify, KHÔNG phải câu trả lời khách (PRD §7.4).

**Verify:** `curl -X POST .../api/agents/classify -d '{"message":"Đơn hàng 6578 của tôi sắp giao tới nơi chưa?"}'`
→ `entities.order_id="6578"`; WS trả `type=classification`. Commit: `feat(rag): phase 5 - /api/agents/classify + ws`.

### Phase 6 — UI Admin: trang Quản lý tri thức (RAG)

- `packages/shared-types` (theo pattern export sẵn): `RagUploadResult{source,chunks,collection}`;
  `RagInfo{collection,points_count,sources:string[]}`; `IntentClassification{intent, category:string|null,
entities:Record<string,unknown>, confidence, uncertainty_flags:string[], rag_contexts:{source:string;score:number}[]}`.
- `apps/dashboard/lib/api.ts`: `uploadKnowledgeDoc(file)` (FormData → `POST /api/rag/upload`, KHÔNG tự set
  Content-Type), `getRagInfo()`, `resetRag()`, `classifyMessage(message)`.
- `components/rag/UploadPanel.tsx` (theo `ServiceStatus.tsx`: `"use client"` + TanStack + Tailwind thuần): input
  `accept=".pdf,.docx,.txt,.md"`; nút Upload (mutation, loading, kết quả `{source,chunks}`); hiện `getRagInfo()`
  (points_count + sources), invalidate sau upload; nút Reset (confirm).
- `components/rag/ClassifyTester.tsx`: ô nhập câu khách → nút "Phân loại" (`classifyMessage`) → hiện `intent`,
  `category`, `confidence`, `uncertainty_flags`, **`entities` (nổi bật)**, và `rag_contexts` (source + score).
- `app/rag/page.tsx`: layout như `app/page.tsx` (header + link "← Dashboard"), render `<UploadPanel/>` + `<ClassifyTester/>`.
- `app/page.tsx`: thêm link header **"Quản lý tri thức (RAG) →"** trỏ `/rag`.

**Verify:** `make dev-backend` + `make dev-dashboard` → `/rag`: upload PDF → thấy `chunks=N` + nguồn;
ClassifyTester câu "Đơn hàng 6578…" → intent=order_status + **entities.order_id=6578**. `pnpm -r build` pass.
Commit: `feat(rag): phase 6 - admin RAG upload UI + classify tester (hiện entities)`.

### Phase 7 — Verify tổng (e2e) + migration

- **RESET rồi upload lại** (payload đổi so với bản seed): `POST /api/rag/reset` → upload PDF (UI/curl).
- Chạy bộ câu (order_status/size/product/promotion/complaint) qua `/api/agents/classify`; kiểm intent + entities.

**Verify:** e2e đạt (đặc biệt `order_id=6578`); `make test` xanh; `pnpm -r build` pass. Commit:
`feat(rag): phase 7 - e2e verify + reset/re-ingest`.

---

## 4. Definition of Done

- [ ] `uv sync` với openai/python-multipart/pypdf/python-docx; `/api/health` ok.
- [ ] Upload `tai_lieu_intents_shop_quan_ao.pdf` (UI **và** curl) → `chunks>0`; `/api/rag/info` → `points_count` + `sources` có tên file. Trích được **PDF + Word + txt/md**; chunking **tổng quát**; payload **generic**.
- [ ] `POST /api/agents/classify` với `"Đơn hàng 6578 của tôi sắp giao tới nơi chưa?"` → `intent=order_status`,
      `category=after_sale`, **`entities.order_id="6578"`** (đúng qua LLM; và regex bù nếu LLM off/lỗi).
- [ ] Với `ENABLE_LLM=true`: entities đa dạng đúng schema (order_id/size/height/weight/product_name…).
- [ ] LLM off/lỗi → cờ `llm_unavailable`, KHÔNG mất `order_id` (regex). `make test` xanh.
- [ ] Trang `/rag` upload + hiện chunk/nguồn + reset; ClassifyTester hiện **entities**. `pnpm -r build` pass.
- [ ] Chỉ Agent 1 có logic thật; KHÔNG persist Postgres; Response Generator vẫn là điểm phát ngôn duy nhất.

---

## 5. Ghi chú cho Claude Code

- **Thay** `chunk_by_heading` → `chunk_text` **tổng quát**; payload **generic** `{text, source, chunk_index}`;
  `search` trả `{text, source, score, chunk_index}` (bỏ intent/category). Sau deploy: **reset + upload lại**.
- **LLM bắt buộc cho intent** (chunk generic không có nhãn); không LLM → degrade `unknown` + cờ `llm_unavailable`.
  Embeddings KHÔNG bị gate bởi `ENABLE_LLM` (retrieval vẫn chạy).
- **Entities:** LLM (schema + few-shot) ⊕ **regex order_id** (neo từ khoá, giá trị chuỗi) → merge
  `{**rule, **llm}`. Regex chạy MỌI nhánh (kể cả degrade) → order_id luôn bắt. `category` từ `INTENT_CATEGORY` map.
- **Giữ `make test` offline:** mọi nhánh degrade KHÔNG network, KHÔNG ném lỗi; LLM lỗi → cờ, đừng im lặng.
- **`search()` ở tầng service** (Knowledge Agent PRD §7.2 tái dùng) — đừng nhét truy hồi cứng vào node.
- PDF scan (không text layer) ngoài phạm vi → route 422, ĐỪNG OCR.
- UI theo **pattern sẵn có** (Tailwind thuần + TanStack + `lib/api.ts`) — KHÔNG thêm shadcn. "Sửa có phẫu thuật".
- Async-first; config từ env; KHÔNG hardcode key/URL/model/ngưỡng.
- Response Generator vẫn là điểm phát ngôn DUY NHẤT — lát cắt chỉ trả metadata phân loại (WS `type=classification`
  là tín hiệu dev, KHÔNG phải câu trả lời khách).
- Sau bước này (layer sau): tách Knowledge Agent, chạy đủ pipeline, gate/PENDING_APPROVAL, phản hồi khách thật,
  RAG management đầy đủ — theo `docs/DEVELOPMENT.md` (Layer 1→4).
