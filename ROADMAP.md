# ROADMAP — Autonomous Customer Support System (map of implementation slices)

> **Living map** to stay oriented — remaining work split into thin slices, ordered, with rationale.
> **Not a contract:** slices may split/reorder as we learn (the Agent-1-doing-retrieval role-bleed taught us).
> Source of truth is still **`PRD.md`** (Vietnamese). Each slice = its own one-shot plan when its turn comes.
>
> Throughout: thin slices, backend then UI right after, verify each slice, filter every idea through the PRD.
> Architecture (PRD §5): fixed 4-agent pipeline `intent → knowledge → decision → response` + human_handoff,
> **no Supervisor**; safety via confidence/uncertainty_flags + grounding; gates + HITL under human control.

---

## ✅ DONE

- Scaffold (7 phases) · PWA migration (dropped React Native; dashboard is a PWA).
- **01 — Agent 1 · Intent Classifier** (§7.1). LLM classifies 10 intents (**taxonomy in prompt**, not RAG),
  extracts entities (LLM schema + regex), clean output (no retrieval). `/api/agents/classify`.
- **02 — RAG ingestion + admin UI** (§13, §17 Module 1). Upload PDF/Word/txt/md → extract → generic chunking →
  embed to Qdrant. "Quản lý tri thức (RAG)" page (upload/list/reset). `/api/rag/upload|info|reset`.
- **03 — Agent 2 · Knowledge Agent** (§7.2). Retrieval → `rag_contexts` + `retrieval_confidence` + flags.
  Role separation (retrieval out of Agent 1) + state-contract cleanup (accumulate flags, per-stage confidence).
  `/api/agents/analyze`.
- **04 — Role-split dashboard UI.** `AnalyzePanel` (Agent 1 | Agent 2), Agent-1 tester, copy aligned.
- **06 — Agent 4 · Response Generator** (§7.4). Grounded reply from `rag_contexts`; **anti-hallucination brake**
  (empty/weak context or no LLM key → polite fallback + `hallucination_risk`, never fabricate); degrade-safe.
  Sole egress to the customer. ⚠️ *Ships alongside a temporary Agent-3 pass-through — see debt below.*
- **07a — Pipeline integration.** Graph runs all 4 nodes end-to-end (`intent → knowledge → decision → response`).
- **07b — Realtime chat backend (minimal).** WebSocket `/ws/chat` runs the full pipeline per message and returns
  `{type:"reply"}` (+ `typing`). *Single-turn: a fresh `thread_id` per message — no cross-turn memory yet; no
  Redis pub/sub yet (single client is fine).*
- **07c — Customer chat UI** (§16). `/chat` renders AI replies + typing indicator over WebSocket.

> **Baseline reached:** the **happy path is live and demoable** — a customer chats at `/chat`, and the agent
> auto-answers grounded in the uploaded knowledge base (or politely defers when it lacks knowledge). Concurrency
> already works (async + per-`thread_id` isolation), on **1 uvicorn worker** (deliberate — see notes).

---

## ⚠️ CURRENT DEBT (known-temporary — pay before the thesis is "complete")

- **05 — Agent 3 · Decision Engine is a PASS-THROUGH.** Real traffic always → `auto_reply`; it does **not** yet
  assess priority/severity or decide `auto_reply` vs `human_handoff` on confidence/flags/grounding. The
  **human_handoff / escalation path only fires on demo-injected flags**, not real traffic. → The thesis's core
  claim (**autonomous decisions + human-in-the-loop safety**, PRD §5 pillars 1 & 3) is **not demonstrated on
  real traffic yet** — only the happy path is. Agent 4's grounding brake gives *basic* safety, but it is not a
  substitute for Agent 3. **This is the single most important gap.**
- **Conversation memory not done** (single-turn). Multi-turn context = slice 09a.

---

## 🟡 PHASE 1 — Autonomous pipeline + live chat — **almost done; 05 remains**

> Only piece left: make the **decision** real so the pipeline actually routes (auto-reply vs escalate).

- **05 — Agent 3 · Decision Engine ← THE NEXT THING (per PRD + roadmap).** Aggregate confidence (careful:
  `intent_confidence` is LLM-reported, `retrieval_confidence` is cosine — different scales; consider a separate
  `retrieval_threshold`); compute priority/severity; decide `auto_reply` vs `human_handoff` + `escalation_reason`.
  **Safety invariant**: any uncertainty flag / low grounding / `no_relevant_knowledge` → `human_handoff`
  (pillar 3). Replace the pass-through; keep Agent 4 as pure response. Backend + test both branches on real messages.
  → **Milestone:** the autonomous core is *real* (decides + escalates), not just the happy path.

---

## 🔵 PHASE 2 — Human-in-the-loop (gates + escalation + admin handling)

> Now escalation matters (05 produces real `human_handoff`). HITL is the safety story.

- **08a — Gates** (§9). auto-reply gate (system-wide + per category); three-way delivery: direct /
  PENDING_APPROVAL / IN_HUMAN_QUEUE. Invariant FR-GATE-2. `GateConfig` + admin toggle.
- **08b — human_handoff + EscalationCard + admin queue** (§11). Escalation case + card; admin queue UI + badge/push.
- **08c — Admin chat / takeover + draft approval** (§11). Admin takes a conversation (AI pauses), admin ↔ customer
  live; PENDING_APPROVAL (approve / edit & send); audit admin actions.
  → **Milestone:** full HITL — escalate → admin handles → customer served.

---

## 🔵 PHASE 3 — Async robustness (memory + suspend/resume + auto-resolve)

- **09a — Conversation memory** (§12). Session memory (Redis short-term + Postgres) + context window; replaces the
  current single-turn `thread_id`-per-message with a stable per-conversation `thread_id`. Feeds Agent 1 + Agent 3.
- **09b — Suspend/resume** (§10). Clarification turn (`AWAITING_CUSTOMER`); human-handoff pause via `interrupt` +
  **durable checkpointer** (Redis/Postgres, replacing `MemorySaver`, FR-ASYNC-6). *(This — plus running >1 worker
  — is the real trigger to drop MemorySaver; not "many concurrent chats", which 1 async worker already handles.)*
- **09c — Auto-resolve + offline handling** (§9/§10). auto-resolve gate + inactivity timer; after-hours → queue +
  "nhân viên sẽ phản hồi sớm"; never auto-close a waiting case.
  → **Milestone:** robust, resumable conversation lifecycle.

---

## 🔵 PHASE 4 — Admin dashboard (full operational view)

- **10a — Conversation list + filters** (§17). Status buckets; open a conversation (customer/AI/admin).
- **10b — System + Agent monitoring** (§17 Modules 2–3). Latency, accuracy, confidence, escalation rate.
- **10c — Analytics + Audit log** (§17 Modules 4–5). Auto-reply/escalation/CSAT/resolution; audit viewer.
  → **Milestone:** full admin operations + KPI visibility (§19).

---

## 🔵 PHASE 5 — Auth + hardening + deploy

- **11 — Auth** (§18 NFR-5; §4). JWT + RBAC for admin routes/pages. **Customer stays guest/low-barrier in
  Phase 1 per PRD §4** — a lightweight customer login (email → `customer_id`) is optional and only needed for
  per-customer history / personal data. *(Can move earlier — see the reprioritization note below.)*
- **12 — Observability** (NFR-8). Langfuse: token cost, latency, LLM error rates.
- **13 — Anti-prompt-injection** (NFR-7). Sanitize customer messages AND RAG doc content before the LLM.
- **UI redesign.** End-phase visual pass, incremental, no-backend-touched, plain Tailwind.
- **14 — Deploy.** Backend → Render/Railway; frontend → Vercel; cloud infra; env secrets; personal-data care (NFR-6).
  → **Milestone:** running on the internet, demo-able remotely.

---

## ⚪ PHASE 6 — Future / optional (PRD §22, pillar 4)

- **15 — Semi-auto improvement loop** (pillar 4). audit_log patterns → propose FAQ/prompt/canned → admin approves.
- **16 — Order-system integration** (**PRD §22 Phase 2**). Mock orders (`order_id, customer_id, status, …`) +
  an **order-lookup tool scoped to the authenticated customer** (authorization: only your own orders — else no
  personal-data leak) → Agent answers "đơn 1234 của tôi…" grounded on **order data + KB policy**. Depends on
  customer identity (11). Pillar-2 tool use. *(Strong demo; but a Phase-2 feature — see note below.)*
- **17 — Others:** cross-conversation memory · customer profile · recommendation · marketing · voice · social · multilingual.

---

## 🧭 Reprioritization considered (2026-07) — customer auth + order-context + browser concurrency demo

Weighed pulling **customer auth (part of 11) + order-context (16)** forward to enable a personalized
multi-customer demo. Decision, filtered through the PRD:

- **Browser concurrency check = do it TODAY, no slice needed.** Open `/chat` in a normal window **and an
  incognito window** (separate sessions!) and chat simultaneously → you already see two pipelines interleave
  (async + per-`thread_id`). This needs no auth and no new code. *(Two tabs in the same browser share one
  session → would look like one customer — use incognito / two browsers.)*
- **Customer auth + order-context are PRD Phase-2/optional, not Phase-1.** PRD §4 keeps customer login
  optional/low-barrier in Phase 1; PRD §22 lists order integration under **Phase 2**. Pulling them forward now
  means **building a Phase-2 feature while the Phase-1 core (Agent 3) is still faked**.
- **Recommendation: do 05 (Agent 3) FIRST**, then optionally auth + order-context. Rationale: Agent 3 is the
  thesis's heart (autonomous decisions + escalation) and is currently a pass-through — highest value, and the
  marked NEXT. Auth+order-context are a compelling *feature demo*, but secondary to making the *core* real.
- If a personalized demo is a hard near-term need, auth-first is defensible (auth is a genuine prerequisite for
  order-context and independent of Agent 3) — **but commit to paying the Agent-3 debt right after**; don't let
  the pass-through become permanent.

---

## Sequencing notes & flex points

- **Core before features:** make the pipeline *decide + escalate* (05) real before layering personalization
  (auth/orders). The happy path already works; the safety half doesn't.
- **Grounding is the safety crux:** Response Generator must never fabricate — weak/no knowledge → handoff. (Done
  in Agent 4; Agent 3 will add confidence/priority-based routing on top.)
- **1 worker for now:** async + `thread_id` already give concurrency; add semaphore/timeout/DB-pool caps only when
  load actually warrants. Drop `MemorySaver` only at 09b (durable suspend/resume) or when running >1 worker.
- **Auth late by default; movable:** guest is fine for the happy path (PRD §4). Move up only if a personalized/
  secured demo needs it — and it becomes a prerequisite for order-context (16).
- **UI polish is its own end-phase**, not per-slice.
- **Minimum viable thesis:** full Phase 1 (incl. **05**) + basic HITL (08a/08b) + auth (11) + deploy (14); scope
  Async (Phase 3) down if time is short — state the reduction in the report.
- **Don't spawn slices outside this roadmap** — filter new ideas through the PRD first.

---

## Quick status (update per slice)

- [x] Scaffold · PWA · 01 Agent 1 · 02 RAG + UI · 03 Agent 2 + role split · 04 role-split UI
- [x] 06 Agent 4 (grounded + brake) · 07a integration · 07b realtime chat (minimal, single-turn) · 07c chat UI
- [ ] **05 Agent 3 · Decision Engine ← NEXT (core; currently a temporary pass-through)**
- [ ] 08a gates · 08b human_handoff + EscalationCard + queue · 08c admin chat + draft approval
- [ ] 09a conversation memory (multi-turn) · 09b suspend/resume + durable checkpointer · 09c auto-resolve + offline
- [ ] 10a conversation list · 10b system/agent monitoring · 10c analytics + audit log
- [ ] 11 auth (admin RBAC; optional customer login) · 12 observability · 13 anti-injection · UI redesign · 14 deploy
- [ ] 15 learning loop · 16 order-system integration (mock orders + scoped tool) · 17 others
