# PLAN — Cập nhật UI dashboard theo tách vai (Agent 1 sạch + Agent 2 Knowledge Agent)

> **Bản chất:** kịch bản ONE-SHOT, **chỉ FRONTEND** (dashboard). Backend đã áp tách vai (`/api/agents/classify`
> sạch — KHÔNG `rag_contexts`; endpoint mới `/api/agents/analyze` = Agent 1 + Agent 2). Nguồn chân lý: `PRD.md`
> §7.1 (Agent 1), §7.2 (Agent 2), §17 (Module 1 RAG Management). KHÔNG đụng backend.
>
> **Vì sao cần plan này (UI đang LỆCH & vỡ):**
>
> - `ClassifyTester` render `r.rag_contexts` nhưng `/classify` KHÔNG còn trả → **crash runtime** khi bấm "Phân loại".
> - Type `IntentClassification` (shared-types) còn `rag_contexts` → khi sửa cho khớp backend sẽ **fail `pnpm build`**
>   nếu không sửa `ClassifyTester` cùng lúc.
> - Copy vẫn coi tài liệu upload là "corpus phân loại intent"; thực tế giờ là **kho tri thức để Agent 2 trả lời**.
>
> **Mục tiêu:** đồng bộ UI với tách vai — Agent 1 sạch (intent/entities, không retrieval); Agent 2 (truy hồi);
> dùng `/analyze` để **hiện rõ cả hai agent**; sửa copy (upload = kho tri thức cho Agent 2).

---

## 0. Schema backend (để dựng type TS cho khớp — KHÔNG đổi backend)

- `ClassifyResult` (Agent 1): `{intent, category, entities, confidence, uncertainty_flags}` — **không** `rag_contexts`.
- `AnalyzeResult` (Agent 1 + Agent 2): `{intent, category, entities, intent_confidence, retrieval_confidence,
uncertainty_flags (gộp), rag_contexts}` với `rag_contexts = [{text, source, score}]` (Agent 2).

---

## 1. In / Out scope

**In scope:** `packages/shared-types`; `apps/dashboard/lib/api.ts`; `components/rag/*`; `app/rag/page.tsx`; copy.
**Out of scope:** backend (giữ nguyên); trang khác ngoài `/rag`; thêm thư viện UI mới (KHÔNG shadcn — theo pattern
Tailwind thuần + TanStack sẵn có).

---

## 2. Kế hoạch theo Phase

> Mỗi phase để `pnpm -r build` XANH trước khi commit (`feat(ui): phase N - ...`).

### Phase 0 — Đồng bộ type + API + sửa ClassifyTester (giữ build xanh)

Làm CÙNG lúc để không để build vỡ giữa chừng:

- `packages/shared-types/src/index.ts`:
  - `IntentClassification`: **BỎ trường `rag_contexts`** (khớp `ClassifyResult`) → còn `{intent, category:string|null,
entities:Record<string,unknown>, confidence:number, uncertainty_flags:string[]}`.
  - Thêm `AnalyzeResult { intent:string; category:string|null; entities:Record<string,unknown>;
intent_confidence:number; retrieval_confidence:number; uncertainty_flags:string[];
rag_contexts:{ text?:string; source:string; score:number }[] }`.
- `apps/dashboard/lib/api.ts`: thêm `analyzeMessage(message:string):Promise<AnalyzeResult>` (POST
  `/api/agents/analyze`). GIỮ `classifyMessage` (→ `/classify`, Agent 1).
- `apps/dashboard/components/rag/ClassifyTester.tsx`: **BỎ block** `{r.rag_contexts.length > 0 && (…Nguồn RAG…)}`
  (Agent 1 không còn rag_contexts). Đổi tiêu đề → **"Test Agent 1 · Intent Classifier"**; thêm 1 dòng chú thích
  nhỏ: "Agent 1 sạch — không truy hồi (retrieval là việc của Agent 2, §7.2)".

**Verify:** `pnpm -r build` xanh; mở `/rag`, panel Agent 1: câu "Đơn hàng 6578…" → `intent=order_status` +
`entities order_id=6578`, **KHÔNG còn mục "Nguồn RAG"**, không crash. Commit: `feat(ui): phase 0 - types + api + Agent1 tester clean`.

### Phase 1 — Thêm AnalyzePanel (Agent 1 → Agent 2, dùng /analyze)

- `apps/dashboard/components/rag/AnalyzePanel.tsx` (theo pattern `ClassifyTester`: `"use client"`, TanStack
  mutation, Tailwind thuần, tái dùng `Badge`): input câu khách → `analyzeMessage` → render **hai mục tách bạch**:
  - **"Agent 1 · Intent Classifier":** `intent` (badge), `category`, `entities` (chips k=v), `intent_confidence`.
  - **"Agent 2 · Knowledge Agent":** `retrieval_confidence`; danh sách `rag_contexts` (mỗi mục: `source` · `score`
    (3 số) · snippet `text` ~120 ký tự). Rỗng → "— không truy hồi được tri thức —".
  - Cuối: `uncertainty_flags` (gộp) dạng badge; tô nổi `no_relevant_knowledge`/`low_retrieval_score` (amber).
- `app/rag/page.tsx`: render thêm `<AnalyzePanel />` (dưới `ClassifyTester`).

**Verify:** `/rag` → AnalyzePanel: "phí ship đi tỉnh bao nhiêu?" → Agent 1 `intent=shipping`; Agent 2 `rag_contexts`
có nguồn `knowledge_base_shop_quan_ao.pdf` + snippet về phí ship. "asdf zxcv" → cờ `no_relevant_knowledge`. Commit:
`feat(ui): phase 1 - AnalyzePanel (Agent 1 + Agent 2 via /analyze)`.

### Phase 2 — Copy cho khớp vai trò

- `app/rag/page.tsx` subtitle → **"Kho tri thức cho Agent 2 (chính sách/FAQ/sản phẩm) → embed Qdrant · test
  Agent 1 (intent) & Agent 2 (truy hồi)"**.
- `components/rag/UploadPanel.tsx`: thêm dòng phụ đề dưới tiêu đề: "Tài liệu **Agent 2** truy hồi để trả lời
  (không phải tài liệu phân loại intent)".

**Verify:** trang đọc mạch lạc, phản ánh đúng tách vai; `pnpm -r build` pass. Commit: `feat(ui): phase 2 - copy khớp vai trò Agent 2`.

---

## 3. Definition of Done

- [ ] `pnpm -r build` xanh; không còn tham chiếu `rag_contexts` trong luồng `/classify` (Agent 1).
- [ ] Panel **Agent 1** chạy không crash; hiện intent/category/entities/confidence/cờ; "Đơn hàng 6578…" ra order_id=6578.
- [ ] **AnalyzePanel** hiện rõ **hai mục** Agent 1 (intent/entities) và Agent 2 (rag_contexts + retrieval_confidence);
      cờ gộp; "phí ship đi tỉnh?" → shipping + context KB; câu vô nghĩa → `no_relevant_knowledge`.
- [ ] Copy trang + UploadPanel phản ánh: upload = **kho tri thức cho Agent 2** (không phải corpus phân loại).
- [ ] KHÔNG đụng backend; theo pattern UI sẵn có (Tailwind thuần + TanStack); KHÔNG thêm thư viện UI.

---

## 4. Ghi chú cho Claude Code

- **Thứ tự Phase 0 quan trọng:** đổi type `IntentClassification` + sửa `ClassifyTester` phải cùng phase, nếu
  không `pnpm build` vỡ (ClassifyTester đọc field vừa bị xoá).
- Type TS phải **khớp schema backend** đã ghi ở mục 0 (đọc `app/schemas/agent.py` nếu cần).
- **AnalyzePanel là chỗ thể hiện tách vai** — trình bày Agent 1 và Agent 2 thành hai khối riêng, rõ nhãn.
- "Sửa có phẫu thuật": chỉ đụng các file trong scope; theo style component sẵn có (`ServiceStatus`/`ClassifyTester`).
- Đây là **metadata phân loại/truy hồi để dev xem** — KHÔNG phải câu trả lời cuối cho khách (Response Generator lo,
  §7.4). Đừng render như "câu trả lời gửi khách".
- Sau bước này (layer sau): khi có Response Generator, thêm panel xem **draft_reply** (câu trả lời grounded từ
  `rag_contexts` của Agent 2) — theo `docs/DEVELOPMENT.md`.
