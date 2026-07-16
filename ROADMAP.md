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
- **05 — Agent 3 · Decision Engine** (§7.3). **Deterministic** policy: routes on FLAGS (`BLOCKING_FLAGS`), **NOT**
  confidence-blending; `RETRIEVAL_THRESHOLD` split from `confidence_threshold`; priority/severity by intent;
  sole-egress (Response Generator emits reply + `HANDOFF_NOTICE`); pass-through removed. **Calibration** (learned
  live): `ambiguous_intent` is informational (grounding-gated, not a blocker), `out_of_domain` fires for
  `intent=other`. FR unit tests + live e2e (KB → auto_reply; out-of-domain/nonsense → handoff; complaint → high).
- **09a (core) — Conversation persistence + multi-turn memory** (§12). Guest conversation + messages → Postgres
  (short sessions); `history_window` recent turns from DB fed into Agent 1 + Agent 4 prompts (reply still grounded
  in `rag_contexts`, **not** history). **`thread_id` stays per-message ON PURPOSE** — memory comes from the **DB**,
  not the checkpointer (stable per-conversation `thread_id` + durable checkpointer = 09b).
- **FE Pipeline Inspector** (§17). `/rag` panel calls `/api/agents/pipeline` (single-shot, no persist) → observe
  ALL 4 agents for a test query, incl. Agent 3 `action/priority/severity/escalation_reason`.

> **Autonomous core reached:** the pipeline now **decides + escalates on real traffic** (not just the happy path):
> KB-answerable → grounded auto-reply; out-of-domain / no-grounding → `human_handoff` + IN_HUMAN_QUEUE. Conversations
> persist and the agent understands multi-turn context. Concurrency works (async + per-`thread_id`) on **1 uvicorn
> worker** (deliberate — see notes). Remaining for full HITL: the human SIDE of handoff (08b/08c) + gates (08a).

---

## ⚠️ CURRENT DEBT (known-temporary — pay before the thesis is "complete")

- ~~**05 — Agent 3 pass-through**~~ → **PAID.** Agent 3 is now deterministic and escalates on real traffic
  (autonomous decisions + safety, PRD §5 pillars 1 & 3, are demonstrated — not just the happy path).
- ~~**Conversation memory (single-turn)**~~ → **PAID.** Multi-turn memory from DB (09a-core above).
- **Handoff has no human SIDE yet.** Agent 3 routes to `human_handoff` and Response Generator sends the notice,
  but there is **no EscalationCard, no admin queue, no admin takeover** (08b/08c) and **no gate / PENDING_APPROVAL**
  (08a). A customer is *told* "chuyển nhân viên" but no admin actually receives/handles the case yet. → next gap.
- **Agent 2 retrieval not contextualized for follow-ups.** History feeds Agent 1 + Agent 4, but Agent 2 retrieves
  on the RAW follow-up query → a very vague follow-up ("thế đi tỉnh thì sao?") retrieves weakly → handoff (fails
  **safe**). Query-contextualization for Agent 2 = future enhancement.
- **`MemorySaver` in-memory + `thread_id`-per-message** (correct for memory-from-DB). Durable checkpointer + stable
  per-conversation `thread_id` = 09b (needed for suspend/resume + running >1 worker).

---

## ✅ PHASE 1 — Autonomous pipeline + live chat — **DONE (incl. 05)**

> The decision is real: the pipeline routes auto-reply vs escalate on real traffic. Milestone reached — the
> autonomous core *decides + escalates*, not just the happy path.

- **05 — Agent 3 · Decision Engine — DONE.** Deterministic, flag-based (NOT confidence-blend): any flag in
  `BLOCKING_FLAGS` (incl. `no_relevant_knowledge` / `low_retrieval_score` / `out_of_domain`) → `human_handoff` +
  `escalation_reason` (pillar 3); priority/severity by intent; separate `RETRIEVAL_THRESHOLD`. Agent 4 stays pure
  response. Insight applied: `intent_confidence` (LLM) vs `retrieval_confidence` (cosine) are different scales →
  do NOT `min()` them; route on flags. Both branches tested on real messages.

---

## 🟡 PHASE 2 — Human-in-the-loop (gates + escalation + admin handling) — **← NEXT**

> Escalation is now real (05 produces real `human_handoff` + conversations persist), but nobody on the human side
> receives it yet. HITL is the safety story — this is the next gap to close.

- **08b — human_handoff + EscalationCard + admin queue** (§11) **← NEXT.** Escalation case + card (summary + intent
  + context + reason + suggested draft); admin queue UI + badge/push. *(Unblocked: Agent 3 emits real handoffs and
  conversations are persisted to attach the card to.)*
- **08a — Gates** (§9). auto-reply gate (system-wide + per category); three-way delivery: direct /
  PENDING_APPROVAL / IN_HUMAN_QUEUE. Invariant FR-GATE-2. `GateConfig` + admin toggle.
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
- [x] 06 Agent 4 (grounded + brake) · 07a integration · 07b realtime chat · 07c chat UI
- [x] **05 Agent 3 · Decision Engine (deterministic, flag-based)** · **09a-core memory (multi-turn from DB)** · FE pipeline inspector
- [ ] **08b human_handoff + EscalationCard + admin queue ← NEXT** · 08a gates · 08c admin chat + draft approval
- [ ] 09b suspend/resume + durable checkpointer · 09c auto-resolve + offline
- [ ] 10a conversation list · 10b system/agent monitoring · 10c analytics + audit log
- [ ] 11 auth (admin RBAC; optional customer login) · 12 observability · 13 anti-injection · UI redesign · 14 deploy
- [ ] 15 learning loop · 16 order-system integration (mock orders + scoped tool) · 17 others
