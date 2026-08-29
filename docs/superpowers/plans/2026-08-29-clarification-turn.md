# Clarification Turn Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wire the `AWAITING_CUSTOMER` clarification turn: when an order-linked intent lacks the order code, the AI asks for it deterministically and resumes on the next customer message (DB history + status, no checkpointer).

**Architecture:** Decision Engine gains a third route `clarify` (after the safety-gate) that fires when `{order_status, refund, exchange}` is missing `order_id`; Response emits a fixed question and sets `AWAITING_CUSTOMER`; a loop-guard via `prior_status` escalates to human after one unanswered ask. Resume is just the next pipeline run with DB history — no durable checkpointer, no `interrupt()`, no reducer redesign.

**Tech Stack:** Python 3.12 · FastAPI · LangGraph · SQLAlchemy 2 async · pytest.

**Spec:** `docs/superpowers/specs/2026-08-29-clarification-turn-design.md`

## Global Constraints

- Async-first backend; Decision Engine stays TẤT ĐỊNH (no LLM/reasoning, route on flags/entities).
- Safety-gate ALWAYS wins over clarify: any flag ∈ `BLOCKING_FLAGS` → `human_handoff`, never clarify.
- Clarify question is a FIXED template emitted by Response (sole-egress), NO LLM call.
- Loop-guard: already asked (`prior_status == AWAITING_CUSTOMER`) and still missing → `human_handoff` (max 1, FR-ASYNC-2).
- Keep `MemorySaver` + per-turn `thread_id`; NO durable checkpointer, NO `interrupt()`, NO reducer-channel changes.
- NO new `ConversationStatus` (reuse `AWAITING_CUSTOMER`). `AgentAction` gains exactly one value: `CLARIFY = "clarify"`.
- Clarify entity map (MVP): `{order_status, refund, exchange} → order_id`, all reusing ONE question template keyed by field `order_id`.
- `make test` must stay OFFLINE-green.
- Commit per unit, prefix `feat(09b)/test(09b)`.

---

### Task 1: Decision Engine clarify route

Add the `CLARIFY` action, the state fields it needs, the deterministic clarify routing (after safety-gate), the PRD note, and update the one existing test that the change repurposes.

**Files:**
- Modify: `apps/backend/app/models/enums.py` (`AgentAction`, ~line 82-85)
- Modify: `apps/backend/app/agents/state.py` (add two TypedDict fields)
- Modify: `apps/backend/app/agents/nodes/decision.py` (map + routing)
- Modify: `apps/backend/PRD.md` (§7.3 note)
- Test: `apps/backend/tests/test_decision.py` (new tests + fix one existing)

**Interfaces:**
- Consumes: `ConversationState`, `ConversationStatus`, `AgentAction`, `Priority`, `Severity`.
- Produces (later tasks rely on these):
  - `AgentAction.CLARIFY == "clarify"`.
  - `ConversationState` has `prior_status: str | None` (input) and `clarify_field: str | None`.
  - `decision.CLARIFY_MISSING_ENTITY: dict[str, str] = {"order_status": "order_id", "refund": "order_id", "exchange": "order_id"}`.
  - `decision_node(state)` returns a dict that includes `"clarify_field": str | None`; sets `action="clarify"` + `clarify_field="order_id"` for the clarify case; `action="human_handoff"` + `escalation_reason="clarify_unresolved"` for the loop-guard case.

- [ ] **Step 1: Add the `CLARIFY` enum value**

In `apps/backend/app/models/enums.py`, `AgentAction`:

```python
class AgentAction(StrEnum):
    # Decision Engine output (PRD §7.3)
    AUTO_REPLY = "auto_reply"
    HUMAN_HANDOFF = "human_handoff"
    CLARIFY = "clarify"  # 09b/FR-ASYNC-2: thiếu entity bắt buộc → hỏi lại (AWAITING_CUSTOMER), tối đa 1 lần
```

- [ ] **Step 2: Add the two state fields**

In `apps/backend/app/agents/state.py`, inside `ConversationState`, near the CSKH fields (after `awaiting_customer`):

```python
    # 09b clarification (FR-ASYNC-2): status hội thoại TRƯỚC lượt này (input, chỉ-đọc) cho loop-guard "đã hỏi
    # 1 lần chưa"; None = ca/lượt mới. `clarify_field` = entity Decision yêu cầu Response hỏi (None nếu không clarify).
    prior_status: str | None
    clarify_field: str | None
```

- [ ] **Step 3: Write the failing decision tests**

In `apps/backend/tests/test_decision.py`, add these tests at the end, AND fix the existing `test_ambiguous_intent_alone_not_blocking` (which now needs an `order_id` so it stays a pure "ambiguous is not blocking" test rather than tripping the new clarify path):

```python
def test_clarify_when_order_status_missing_code() -> None:
    out = _decide(intent="order_status", uncertainty_flags=[], entities={})
    assert out["action"] == "clarify"
    assert out["clarify_field"] == "order_id"
    assert out["require_human_handoff"] is False


def test_clarify_covers_refund_and_exchange() -> None:
    for intent in ("refund", "exchange"):
        out = _decide(intent=intent, uncertainty_flags=[], entities={})
        assert out["action"] == "clarify", intent
        assert out["clarify_field"] == "order_id", intent


def test_no_clarify_when_code_present() -> None:
    out = _decide(intent="order_status", uncertainty_flags=[], entities={"order_id": "716449"})
    assert out["action"] == "auto_reply"
    assert out["clarify_field"] is None


def test_clarify_loop_guard_escalates_after_asking_once() -> None:
    # Đã hỏi (prior=AWAITING_CUSTOMER) mà vẫn thiếu mã → handoff (max 1, FR-ASYNC-2).
    out = _decide(intent="order_status", uncertainty_flags=[], entities={}, prior_status="AWAITING_CUSTOMER")
    assert out["action"] == "human_handoff"
    assert out["require_human_handoff"] is True
    assert out["escalation_reason"] == "clarify_unresolved"
    assert out["clarify_field"] is None


def test_blocking_flag_wins_over_clarify() -> None:
    # An toàn ưu tiên: cờ chặn + thiếu mã đồng thời → handoff (KHÔNG clarify).
    out = _decide(intent="order_status", uncertainty_flags=["human_requested"], entities={})
    assert out["action"] == "human_handoff"
    assert out["clarify_field"] is None
    assert "human_requested" in out["escalation_reason"]


def test_non_order_intent_missing_code_no_clarify() -> None:
    out = _decide(intent="product_price", uncertainty_flags=[], entities={})
    assert out["action"] == "auto_reply"
    assert out["clarify_field"] is None
```

And change the existing test (around line 82-86) to keep its original meaning:

```python
def test_ambiguous_intent_alone_not_blocking() -> None:
    # ambiguous_intent (nhãn mờ) NHƯNG grounding mạnh → auto_reply. Có order_id để KHÔNG kích clarify (09b).
    assert "ambiguous_intent" not in BLOCKING_FLAGS
    out = _decide(
        intent="refund",
        uncertainty_flags=["ambiguous_intent"],
        retrieval_confidence=0.65,
        entities={"order_id": "716449"},
    )
    assert out["action"] == "auto_reply"
```

- [ ] **Step 4: Run tests to verify they fail**

Run: `cd apps/backend && uv run pytest tests/test_decision.py -v`
Expected: the new tests FAIL (no `clarify` action / `clarify_field` key yet); `test_ambiguous_intent_alone_not_blocking` passes with its new entities.

- [ ] **Step 5: Implement the clarify routing in `decision.py`**

In `apps/backend/app/agents/nodes/decision.py`, add the map above `decision_node`:

```python
# Clarify (09b/FR-ASYNC-2): intent gắn-với-đơn thiếu mã → hỏi lại. Tất cả trỏ CÙNG field `order_id` (một câu hỏi).
CLARIFY_MISSING_ENTITY: dict[str, str] = {
    "order_status": "order_id",
    "refund": "order_id",
    "exchange": "order_id",
}
```

Replace the body of `decision_node` (from the `blocking` computation through the `action`/`escalation_reason`/`intent` lines) so clarify is evaluated AFTER the safety-gate. Full replacement of `decision_node`:

```python
def decision_node(state: ConversationState) -> dict[str, Any]:
    accumulated = list(state.get("uncertainty_flags") or [])  # cờ tích luỹ Agent 1+2 (reducer add)
    injected = list((state.get("scratchpad") or {}).get("injected_flags") or [])  # demo (run-demo)

    # Safety gate TẤT ĐỊNH (PRD §5 trụ cột 3): cờ ∈ BLOCKING_FLAGS → human_handoff. KHÔNG blend confidence.
    blocking = sorted((set(accumulated) | set(injected)) & BLOCKING_FLAGS)
    handoff = bool(blocking)
    escalation_reason = f"blocking_flags={blocking}" if handoff else None
    action = AgentAction.HUMAN_HANDOFF if handoff else AgentAction.AUTO_REPLY

    intent = state.get("intent") or "other"

    # Clarify (09b/FR-ASYNC-2): CHỈ khi safety-gate KHÔNG chặn. Thiếu entity bắt buộc → hỏi lại (tối đa 1 lần:
    # đã hỏi mà vẫn thiếu → handoff). An toàn LUÔN ưu tiên.
    clarify_field: str | None = None
    if not handoff:
        field = CLARIFY_MISSING_ENTITY.get(intent)
        missing = bool(field) and not str((state.get("entities") or {}).get(field) or "").strip()
        if missing:
            if state.get("prior_status") == ConversationStatus.AWAITING_CUSTOMER:
                action = AgentAction.HUMAN_HANDOFF
                handoff = True
                escalation_reason = "clarify_unresolved"
            else:
                action = AgentAction.CLARIFY
                clarify_field = field

    priority, severity = _PRIORITY_SEVERITY.get(intent, (Priority.LOW, Severity.LOW))

    return {
        "status": ConversationStatus.DECIDING,
        "action": action,
        "priority": str(priority),
        "severity": str(severity),
        "require_human_handoff": handoff,
        "escalation_reason": escalation_reason,
        "clarify_field": clarify_field,
        # Reducer `add`: CHỈ trả cờ MỚI (injected của demo) — cờ tích luỹ đã có sẵn, đừng trả lại (tránh nhân đôi).
        "uncertainty_flags": injected,
        "trace": [
            {
                "node": "decision",
                "confidence": state.get("intent_confidence"),
                "branch": str(action),
                "detail": {
                    "blocking_flags": blocking,
                    "clarify_field": clarify_field,
                    "priority": str(priority),
                    "severity": str(severity),
                    "intent_confidence": state.get("intent_confidence"),
                    "retrieval_confidence": state.get("retrieval_confidence"),
                },
            }
        ],
    }
```

- [ ] **Step 6: Run decision tests to verify they pass**

Run: `cd apps/backend && uv run pytest tests/test_decision.py -v`
Expected: PASS (all, including the new clarify tests and the amended ambiguous test).

- [ ] **Step 7: Add the PRD note (§7.3)**

In `apps/backend/PRD.md`, find the Decision Engine section (§7.3, where the output `auto_reply | human_handoff` is described) and add a short note (matching the surrounding Vietnamese style):

```
- **clarify (route thứ ba, §10 FR-ASYNC-2):** khi intent gắn-với-đơn (order_status/refund/exchange) THIẾU mã đơn
  và KHÔNG có cờ chặn → Decision route `clarify` → Response hỏi lại mã + hội thoại `AWAITING_CUSTOMER`. Hỏi TỐI ĐA
  1 lần: đã hỏi mà lượt sau vẫn thiếu → `human_handoff`. An toàn (BLOCKING_FLAGS) LUÔN ưu tiên trên clarify.
```

- [ ] **Step 8: Run the full offline suite**

Run: `cd apps/backend && uv run pytest -q`
Expected: all pass (no regression; `test_graph` still green because `run_pipeline` defaults `prior_status=None` and its inputs aren't order-linked).

- [ ] **Step 9: Commit**

```bash
git add apps/backend/app/models/enums.py apps/backend/app/agents/state.py apps/backend/app/agents/nodes/decision.py apps/backend/PRD.md apps/backend/tests/test_decision.py
git commit -m "feat(09b): Decision route clarify (thiếu mã đơn → AWAITING_CUSTOMER, max 1)"
```

---

### Task 2: Response clarify branch

Response emits the fixed clarification question and sets `AWAITING_CUSTOMER` when `action == clarify`. No LLM.

**Files:**
- Modify: `apps/backend/app/agents/nodes/response.py` (constant + branch in `response_node`)
- Test: `apps/backend/tests/test_response.py`

**Interfaces:**
- Consumes: `AgentAction.CLARIFY`, `state["clarify_field"]`, `ConversationStatus.AWAITING_CUSTOMER`, `FALLBACK_REPLY`.
- Produces: for `action==clarify` + `clarify_field=="order_id"`, `response_node` returns `result.reply == CLARIFY_QUESTION["order_id"]`, `status == "AWAITING_CUSTOMER"`, `result.branch == "clarify"`, `uncertainty_flags == []`, and does NOT call `generate_reply`.

- [ ] **Step 1: Write the failing test**

In `apps/backend/tests/test_response.py`, add after the handoff tests:

```python
async def test_response_node_clarify_asks_for_order_code(monkeypatch: pytest.MonkeyPatch) -> None:
    # 09b: action=clarify + clarify_field=order_id -> câu hỏi mã đơn + AWAITING_CUSTOMER, KHÔNG gọi LLM.
    async def boom(*a, **k):  # generate_reply KHÔNG được gọi ở nhánh clarify
        raise AssertionError("generate_reply must not be called for clarify")

    monkeypatch.setattr(resp, "generate_reply", boom)
    out = await resp.response_node({"action": "clarify", "clarify_field": "order_id"})
    assert out["status"] == "AWAITING_CUSTOMER"
    assert out["result"]["branch"] == "clarify"
    assert out["result"]["reply"] == resp.CLARIFY_QUESTION["order_id"]
    assert out["messages"] == [{"sender": "ai", "content": resp.CLARIFY_QUESTION["order_id"]}]
    assert out["uncertainty_flags"] == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd apps/backend && uv run pytest tests/test_response.py::test_response_node_clarify_asks_for_order_code -v`
Expected: FAIL (`CLARIFY_QUESTION` undefined / no clarify branch).

- [ ] **Step 3: Add the constant + branch in `response.py`**

Add the template near `HANDOFF_NOTICE` (after `HANDOFF_NOTICE_AFTER_HOURS`):

```python
# 09b clarification: câu hỏi CỐ ĐỊNH theo field thiếu (sole-egress, KHÔNG LLM). MVP chỉ order_id.
CLARIFY_QUESTION: dict[str, str] = {
    "order_id": "Dạ anh/chị cho em xin mã đơn hàng để em kiểm tra giúp ạ.",
}
```

In `response_node`, make the clarify branch the FIRST branch (actions are mutually exclusive):

```python
    action = state.get("action")
    if action == AgentAction.CLARIFY:
        # 09b: hỏi lại tất định + AWAITING_CUSTOMER. Nếu field lạ (map lệch, không nên xảy ra) → degrade an toàn.
        question = CLARIFY_QUESTION.get(state.get("clarify_field") or "")
        if question is not None:
            reply = question
            status = ConversationStatus.AWAITING_CUSTOMER
            branch = "clarify"
            flags: list[str] = []
        else:
            reply = FALLBACK_REPLY
            status = ConversationStatus.REPLIED
            branch = "response"
            flags = ["hallucination_risk"]
    elif action == AgentAction.HUMAN_HANDOFF:
        # 09c offline: trong giờ → notice thường; ngoài giờ → "nhân viên sẽ phản hồi sớm". AI không đổi hành vi
        # khác (ca vẫn IN_HUMAN_QUEUE + EscalationCard); chỉ câu thông báo tới khách khác.
        within = is_within_support_hours(datetime.now(timezone.utc))
        reply = HANDOFF_NOTICE if within else HANDOFF_NOTICE_AFTER_HOURS
        status = ConversationStatus.IN_HUMAN_QUEUE
        branch = "human_handoff"
        flags = []
    else:
        result = await generate_reply(
            query=state.get("input", ""),
            intent=state.get("intent"),
            entities=state.get("entities") or {},
            rag_contexts=state.get("rag_contexts") or [],
            history=state.get("history"),
            order_context=state.get("order_context"),
            order_not_found=state.get("order_not_found"),
        )
        reply = result["reply"]
        status = ConversationStatus.REPLIED
        branch = "response"
        flags = result["uncertainty_flags"]
```

(Note: the `flags: list[str]` annotation moves to the clarify branch since it is now the first assignment; keep exactly one annotated declaration.)

- [ ] **Step 4: Run response tests to verify they pass**

Run: `cd apps/backend && uv run pytest tests/test_response.py -v`
Expected: PASS (new clarify test + existing handoff/auto_reply tests unchanged).

- [ ] **Step 5: Run the full offline suite**

Run: `cd apps/backend && uv run pytest -q`
Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add apps/backend/app/agents/nodes/response.py apps/backend/tests/test_response.py
git commit -m "feat(09b): Response nhánh clarify (hỏi mã đơn + AWAITING_CUSTOMER, no LLM)"
```

---

### Task 3: Pipeline plumbing + integration

Thread `prior_status` from the WS boundary through `run_pipeline` → `_initial_state` so Decision's loop-guard sees the previous status; verify end-to-end.

**Files:**
- Modify: `apps/backend/app/agents/graph.py` (`_initial_state` + `run_pipeline`)
- Modify: `apps/backend/app/api/ws/chat.py` (`_run_pipeline_safe` + call-site)
- Test: `apps/backend/tests/test_graph.py`

**Interfaces:**
- Consumes: `AgentAction.CLARIFY`, decision/response clarify behavior (Tasks 1-2), `ConversationState.prior_status`/`clarify_field`.
- Produces: `run_pipeline(..., prior_status: str | None = None)`; `_initial_state` sets `prior_status` + `clarify_field=None`; WS passes the pre-turn status.

- [ ] **Step 1: Write the failing integration test**

In `apps/backend/tests/test_graph.py`, add a test that an order_status turn with no code ends in AWAITING_CUSTOMER with the clarify question (offline: Intent uses regex when LLM off, and the clarify branch needs no LLM). Force the intent deterministically by monkeypatching the intent node so the test is not LLM-dependent:

```python
import app.agents.graph as graph_mod


async def test_pipeline_clarifies_order_status_without_code(monkeypatch: pytest.MonkeyPatch) -> None:
    # Ép intent=order_status, entities rỗng (không mã) qua intent node -> pipeline phải hỏi mã + AWAITING_CUSTOMER.
    async def fake_intent(state):
        return {
            "status": "CLASSIFYING",
            "intent": "order_status",
            "entities": {},
            "intent_confidence": 0.9,
            "uncertainty_flags": [],
            "trace": [{"node": "intent", "confidence": 0.9, "branch": "intent"}],
        }

    monkeypatch.setattr(graph_mod, "graph", graph_mod.build_graph())  # graph mới cho test cô lập
    # Patch node đã compile khó; thay vào đó patch hàm intent_node trước khi build:
```

Because the compiled `graph` binds nodes at build time, patch at the node-module level and rebuild. Simpler and robust — call `run_pipeline` with a monkeypatched `intent_node` and a freshly built graph:

```python
async def test_pipeline_clarifies_order_status_without_code(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.agents.nodes import intent as intent_mod

    async def fake_intent(state):
        return {
            "status": "CLASSIFYING",
            "intent": "order_status",
            "entities": {},
            "intent_confidence": 0.9,
            "uncertainty_flags": [],
            "trace": [{"node": "intent", "confidence": 0.9, "branch": "intent"}],
        }

    monkeypatch.setattr(intent_mod, "intent_node", fake_intent)
    monkeypatch.setattr(graph_mod, "graph", graph_mod.build_graph())

    final = await graph_mod.run_pipeline(input_text="đơn của mình tới đâu rồi ạ")
    assert final["status"] == "AWAITING_CUSTOMER"
    assert final["result"]["reply"] == "Dạ anh/chị cho em xin mã đơn hàng để em kiểm tra giúp ạ."


async def test_pipeline_prior_awaiting_escalates_when_still_no_code(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.agents.nodes import intent as intent_mod

    async def fake_intent(state):
        return {
            "status": "CLASSIFYING",
            "intent": "order_status",
            "entities": {},
            "intent_confidence": 0.9,
            "uncertainty_flags": [],
            "trace": [{"node": "intent", "confidence": 0.9, "branch": "intent"}],
        }

    monkeypatch.setattr(intent_mod, "intent_node", fake_intent)
    monkeypatch.setattr(graph_mod, "graph", graph_mod.build_graph())

    final = await graph_mod.run_pipeline(input_text="vẫn đơn đó", prior_status="AWAITING_CUSTOMER")
    assert final["status"] == "IN_HUMAN_QUEUE"
```

Note: `build_graph()` wraps `intent_node` via `_observed(intent_node)` at build time, so patch `intent_mod.intent_node` BEFORE rebuilding `graph`. The knowledge node runs but returns empty order signals for no code (harmless); RAG retrieval is offline-safe (returns low/empty without network) — if it makes a network call in this env, also monkeypatch `graph_mod`'s knowledge to a stub returning `{"status":"RETRIEVING","rag_contexts":[],"retrieval_confidence":0.0,"order_context":None,"order_not_found":None,"uncertainty_flags":[],"trace":[{"node":"knowledge","confidence":0.0,"branch":"knowledge"}]}`. Prefer the intent-only patch first; add the knowledge stub only if the run hits the network.

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd apps/backend && uv run pytest tests/test_graph.py::test_pipeline_clarifies_order_status_without_code tests/test_graph.py::test_pipeline_prior_awaiting_escalates_when_still_no_code -v`
Expected: FAIL — `run_pipeline` doesn't accept `prior_status` yet / doesn't clarify.

- [ ] **Step 3: Thread `prior_status` through `graph.py`**

In `apps/backend/app/agents/graph.py`, add the param to `_initial_state` and set both new keys:

```python
def _initial_state(
    *,
    input_text: str,
    conversation_id: str,
    turn_id: str,
    force_handoff: bool,
    history: list[dict[str, Any]] | None,
    customer_id: str | None,
    prior_status: str | None,
) -> ConversationState:
    return {
        # ... existing keys unchanged ...
        "awaiting_customer": False,
        "prior_status": prior_status,
        "clarify_field": None,
    }
```

(Add `prior_status` + `clarify_field` to the returned dict alongside the existing keys; do not remove any existing key.)

And `run_pipeline`:

```python
async def run_pipeline(
    *,
    input_text: str,
    force_handoff: bool = False,
    conversation_id: str | None = None,
    history: list[dict[str, Any]] | None = None,
    turn_id: str | None = None,
    customer_id: str | None = None,
    prior_status: str | None = None,
) -> dict[str, Any]:
```

and pass `prior_status=prior_status` into the `_initial_state(...)` call.

- [ ] **Step 4: Pass `prior_status` from the WS boundary**

In `apps/backend/app/api/ws/chat.py`, add the param to `_run_pipeline_safe` and forward it:

```python
async def _run_pipeline_safe(
    msg: str,
    history: list[dict[str, str]] | None,
    turn_id: uuid.UUID,
    customer_id: uuid.UUID | None = None,
    prior_status: str | None = None,
) -> tuple[str | None, dict[str, Any] | None, str]:
    ...
    final = await run_pipeline(
        input_text=msg,
        history=history,
        turn_id=str(turn_id),
        customer_id=str(customer_id) if customer_id else None,
        prior_status=prior_status,
    )
    ...
```

At the call site in `_customer_reader` (where `status_out, final, reply = await _run_pipeline_safe(msg, history, turn_id, st.customer_id)`), pass the pre-turn `status` variable:

```python
            status_out, final, reply = await _run_pipeline_safe(
                msg, history, turn_id, st.customer_id, status
            )
```

(`status` here is the status loaded before this turn — `ACTIVE_AI` for a new/reopened case, or the persisted status such as `AWAITING_CUSTOMER` for an existing case. That is exactly the loop-guard input.)

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd apps/backend && uv run pytest tests/test_graph.py -v`
Expected: PASS (both new tests + existing graph tests).

- [ ] **Step 6: Run the full offline suite + import check**

Run: `cd apps/backend && uv run pytest -q` (expect all pass) and `uv run python -c "import app.main; print('import OK')"`.

- [ ] **Step 7: Verify LIVE end-to-end (WS)**

With backend running (:8001 for e2e; ENABLE_LLM as configured), over `/ws/chat` as an authenticated customer:
- Send "đơn của mình tới đâu rồi ạ" (no code) → expect a `reply` asking for the order code; the conversation persists `AWAITING_CUSTOMER`.
- Send a valid order code the customer owns → expect the order-status answer (resume works via history).
- (refund path) Send "mình muốn hoàn đơn" (no code) → expect the code question + `AWAITING_CUSTOMER`; then send the code → expect it to proceed into the sensitive/draft flow (PENDING_APPROVAL) as before.
Capture outcomes for the report.

- [ ] **Step 8: Commit**

```bash
git add apps/backend/app/agents/graph.py apps/backend/app/api/ws/chat.py apps/backend/tests/test_graph.py
git commit -m "feat(09b): thread prior_status vào pipeline + WS (loop-guard clarify) + e2e"
```

---

## Self-Review

**Spec coverage:**
- §2 D1 (clarify = 3rd Decision route after safety-gate) → Task 1. D2 (map order_status/refund/exchange→order_id) → Task 1. D3 (loop-guard via prior_status) → Task 1 (decision) + Task 3 (plumbing). D4 (Response fixed question, field-keyed) → Task 2. D5 (keep MemorySaver/thread_id, no checkpointer) → nothing added (constraint honored; no task touches graph checkpointer). D6 (refund/exchange clarify-first) → Task 1 map includes them.
- §3 state machine (reuse AWAITING_CUSTOMER; add AgentAction.CLARIFY) → Task 1 (enum) + Task 2 (status set). ✓
- §4.1 enum → Task 1. §4.2 state fields → Task 1. §4.3 decision → Task 1. §4.4 response → Task 2. §4.5 graph → Task 3. §4.6 ws → Task 3. §4.7 (gate/auto-resolve/WS-delivery/TurnOutcome unchanged) → no task, verified constant. ✓
- §5 edge cases → covered by Task 1 tests (blocking wins, prior-none first-ask, loop-guard, intent-not-in-map) + Task 2 fallback branch. ✓
- §6 tests: decision offline → Task 1; response offline → Task 2; graph offline + live → Task 3. ✓
- §7 safety invariants → Task 1 (safety-gate first; no LLM) + Task 2 (no LLM). ✓
- §8 PRD reconciliation → Task 1 Step 7. ✓
- §9 out-of-scope (checkpointer/interrupt/fuzzy-intent/multi-field) → no task touches them. ✓

**Placeholder scan:** no TBD/TODO; every code step has concrete content. Task 3 Step 1 gives a concrete monkeypatch strategy with a named fallback (knowledge stub) rather than a vague "handle network."

**Type consistency:** `AgentAction.CLARIFY == "clarify"` used identically in decision (`action`), response (branch check), and tests. `clarify_field` is `str | None` in state, decision output, and read by response. `prior_status: str | None` consistent across state / `_initial_state` / `run_pipeline` / `_run_pipeline_safe`. `CLARIFY_MISSING_ENTITY` (decision) and `CLARIFY_QUESTION` (response) both key on `"order_id"`. `escalation_reason == "clarify_unresolved"` consistent between decision impl and Task 1 test.

**Risk noted:** Task 3's offline pipeline test depends on the intent node being patchable pre-build and the knowledge node being offline-safe; the step gives an explicit fallback stub if RAG hits the network in the test env.
