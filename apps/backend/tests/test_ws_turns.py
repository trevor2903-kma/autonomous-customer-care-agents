"""Audit v2 — WS khách: một lượt = ghi TRƯỚC khi báo khách, CAS status, tuần tự theo khách, ack/pong/rate-limit,
chống gửi lại, lỗi pipeline → hàng đợi [error]. Offline hoàn toàn (DB/pipeline/hub giả, socket giả).

GRAPH-02.1 (handoff mất khi khách đóng tab), GRAPH-02.2 (pipeline đè takeover/đóng ca), GRAPH-02.3 (2 tab chạy song
song / đẻ 2 ca), IDEM-XC.1 + FE-01.4 (ack, gửi lại), SEC-XC.2 (trần tin), PERF-01.3/PERF-01.5 (timings, message_id).
"""

from __future__ import annotations

import asyncio
import json
import uuid
from types import SimpleNamespace
from typing import Any

import pytest

from app.api.ws import chat
from app.api.ws.hub import INBOX_KEY, ConnectionHub
from app.core.rate_limit import SlidingWindowLimiter
from app.models.enums import ConversationStatus as S
from app.models.enums import TurnOutcome
from app.services import audit_service, conversation_service
from tests.test_state_support import FakeStore, FakeWebSocket, drain, install_service_fakes, until

REPLY = "Dạ phí ship về Đà Nẵng là 30.000đ ạ."
NOTICE = "Yêu cầu của bạn đã được chuyển tới nhân viên hỗ trợ."


def _final(
    status: str,
    *,
    reply: str = REPLY,
    intent: str = "shipping",
    reason: str | None = None,
    priority: str = "low",
) -> dict[str, Any]:
    return {
        "status": status,
        "intent": intent,
        "result": {"reply": reply},
        "priority": priority,
        "severity": "low",
        "escalation_reason": reason,
        "entities": {},
        "rag_contexts": [],
        "uncertainty_flags": [],
        "trace": [],
    }


class _Pipeline:
    """run_pipeline giả: ghi lại lời gọi; `gate` chặn giữa chừng (mô phỏng pipeline 3-6 s); `error` = pipeline ném."""

    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []
        self.gate: asyncio.Event | None = None
        self.final: dict[str, Any] = _final(S.REPLIED)
        self.error: Exception | None = None

    async def __call__(
        self,
        *,
        input_text: str,
        history: list[dict[str, str]] | None,
        turn_id: str,
        customer_id: str | None,
        prior_status: str | None,
        prior_intent: str | None,
    ) -> dict[str, Any]:
        self.calls.append(
            {"input": input_text, "history": history, "prior_status": prior_status, "prior_intent": prior_intent}
        )
        if self.gate is not None:
            await self.gate.wait()
        if self.error is not None:
            raise self.error
        return dict(self.final)


class _SnapWS(FakeWebSocket):
    """Chụp trạng thái "DB" ĐÚNG lúc frame kết quả được gửi → chứng minh ghi TRƯỚC, báo khách SAU."""

    def __init__(self, store: FakeStore, *, name: str = "tab") -> None:
        super().__init__(store, name=name)
        self.snaps: dict[str, dict[str, Any]] = {}

    async def send_json(self, payload: dict[str, Any]) -> None:
        await super().send_json(payload)
        if payload.get("type") in ("reply", "handoff", "pending", "status") and self.store is not None:
            convs = list(self.store.convs.values())
            self.snaps[payload["type"]] = {
                "statuses": [c["status"] for c in convs],
                "cards": [c["escalation_card"] for c in convs],
                "ai": [m.id for m in self.store.messages if m.sender == "ai"],
            }


@pytest.fixture
async def env(monkeypatch: pytest.MonkeyPatch) -> Any:
    store = FakeStore()
    install_service_fakes(monkeypatch, store)
    hub = ConnectionHub()
    monkeypatch.setattr(chat, "hub", hub)
    monkeypatch.setattr(chat, "AsyncSessionLocal", store.session)

    async def auth(websocket: Any, role: str) -> dict[str, Any]:
        return {"sub": websocket.query_params.get("token"), "role": role}

    async def display(customer_id: uuid.UUID) -> str:
        return "Khách test"

    async def no_hold(status_out: str | None, intent: str | None) -> bool:
        return False

    audits: list[dict[str, Any]] = []

    async def record_turn(**kwargs: Any) -> int:
        audits.append(kwargs)
        return 1

    pipe = _Pipeline()
    monkeypatch.setattr(chat, "authenticate_websocket", auth)
    monkeypatch.setattr(chat, "_load_customer_display", display)
    monkeypatch.setattr(chat, "gate_holds", no_hold)
    monkeypatch.setattr(audit_service, "record_turn", record_turn)
    monkeypatch.setattr(chat, "run_pipeline", pipe)
    monkeypatch.setattr(chat, "_chat_limiter", SlidingWindowLimiter(1000, 60))
    chat._recent_client_ids.clear()
    yield SimpleNamespace(store=store, hub=hub, audits=audits, pipe=pipe)
    if pipe.gate is not None:
        pipe.gate.set()
    await asyncio.wait_for(asyncio.gather(*list(chat._turn_tasks), return_exceptions=True), 2)
    chat._recent_client_ids.clear()


def _msg(content: str, cid: str | None = None) -> str:
    return json.dumps({"type": "message", "content": content, "client_msg_id": cid})


async def _open(env: Any, customer: uuid.UUID, *, name: str = "tab", snap: bool = False) -> tuple[Any, Any]:
    ws = _SnapWS(env.store, name=name) if snap else FakeWebSocket(env.store, name=name)
    ws.query_params = {"token": str(customer)}
    task = asyncio.create_task(chat.chat_ws(ws))  # type: ignore[arg-type]
    await until(lambda: bool(ws.frames("system")))
    return ws, task


async def _settle(*pairs: tuple[Any, Any]) -> None:
    """Rớt các socket rồi chờ mọi task lượt xong."""
    for ws, task in pairs:
        ws.drop()
        await asyncio.wait_for(task, 2)
    await asyncio.wait_for(asyncio.gather(*list(chat._turn_tasks), return_exceptions=True), 2)


def _customer_convs(store: FakeStore, customer: uuid.UUID) -> list[dict[str, Any]]:
    return [c for c in store.convs.values() if c["customer_id"] == customer]


# ── Luồng chuẩn: ack → typing → reply (đã commit) + liên kết audit ───────────
async def test_reply_is_committed_before_the_frame_and_linked_everywhere(env: Any) -> None:
    customer = uuid.uuid4()
    cid = env.store.add_conv(customer_id=customer, status=S.REPLIED)
    ws, task = await _open(env, customer, snap=True)

    ws.push(_msg("ship về Đà Nẵng bao nhiêu", "c-1"))
    await until(lambda: bool(ws.frames("reply")))
    ai = env.store.msgs(cid, "ai")
    customer_msgs = env.store.msgs(cid, "customer")
    assert ws.sent[1:4] == [
        {"type": "ack", "client_msg_id": "c-1", "message_id": None, "duplicate": False},
        {"type": "typing"},
        {"type": "reply", "content": REPLY, "message_id": str(ai[0].id)},
    ]
    assert ws.snaps["reply"]["ai"] == [ai[0].id]  # tin AI đã COMMIT trước khi frame rời server
    assert customer_msgs[0].client_msg_id == "c-1"
    await _settle((ws, task))

    audit = env.audits[0]
    assert audit["message_id"] == customer_msgs[0].id  # PERF-01.5
    assert audit["outcome"] == TurnOutcome.SENT
    assert set(audit["delivery_detail"]["timings"]) == {
        "queue_ms", "pre_pipeline_ms", "pipeline_ms", "persist_ms", "send_ms", "fanout_ms"
    }


async def test_handoff_status_card_and_notice_land_in_one_commit_before_the_frame(env: Any) -> None:
    customer = uuid.uuid4()
    cid = env.store.add_conv(customer_id=customer, status=S.REPLIED)
    env.pipe.final = _final(
        S.IN_HUMAN_QUEUE, reply=NOTICE, intent="complaint",
        reason="blocking_flags=['low_retrieval_score']", priority="high",
    )
    ws, task = await _open(env, customer, snap=True)
    ws.push(_msg("áo bị rách, shop xử lý sao", "h-1"))
    await until(lambda: bool(ws.frames("handoff")))

    snap = ws.snaps["handoff"]
    assert snap["statuses"] == [S.IN_HUMAN_QUEUE] and snap["cards"][0]["summary"] == "áo bị rách, shop xử lý sao"
    assert len(snap["ai"]) == 1  # khách chỉ được báo "đã chuyển" khi ca ĐÃ nằm trong hàng đợi admin
    conv = env.store.convs[cid]
    assert (conv["priority"], conv["escalation_reason"]) == ("high", "blocking_flags=['low_retrieval_score']")
    assert ws.frames("handoff") == [{"type": "handoff", "content": NOTICE, "message_id": str(snap["ai"][0])}]
    await _settle((ws, task))
    assert env.audits[0]["outcome"] == TurnOutcome.QUEUED_FOR_HUMAN


async def test_escalating_turn_publishes_status_to_admin_and_inbox_not_to_its_own_socket(env: Any) -> None:
    customer = uuid.uuid4()
    cid = env.store.add_conv(customer_id=customer, status=S.REPLIED)
    env.pipe.final = _final(S.IN_HUMAN_QUEUE, reply=NOTICE, intent="complaint", priority="high")
    admin_q = env.hub.register(str(cid))  # admin đang mở ca để theo dõi (FE-01.3)
    inbox_q = env.hub.register(INBOX_KEY)
    ws, task = await _open(env, customer)
    ws.push(_msg("áo bị rách, shop xử lý sao", "s-1"))
    await until(lambda: bool(ws.frames("handoff")))
    await _settle((ws, task))

    frames = drain(admin_q)
    assert [f["type"] for f in frames] == ["message", "message", "status"]
    assert frames[-1] == {"type": "status", "status": "IN_HUMAN_QUEUE", "assigned_admin_id": None}
    assert [(e["event"], e["status"]) for e in drain(inbox_q)] == [
        ("message", None), ("message", None), ("status", "IN_HUMAN_QUEUE")
    ]
    assert ws.frames("status") == [] and ws.frames("message") == []  # socket gốc đã nhận frame handoff trực tiếp


async def test_gate_hold_persists_pending_card_without_sending_the_draft(
    env: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def hold(status_out: str | None, intent: str | None) -> bool:
        return True

    monkeypatch.setattr(chat, "gate_holds", hold)
    customer = uuid.uuid4()
    cid = env.store.add_conv(customer_id=customer, status=S.REPLIED)
    env.pipe.final = _final(S.REPLIED, reply="Nháp hoàn tiền", intent="refund")
    ws, task = await _open(env, customer, snap=True)
    ws.push(_msg("hoàn tiền đơn 123456 giúp em", "p-1"))
    await until(lambda: bool(ws.frames("pending")))

    assert ws.frames("pending") == [{"type": "pending"}]  # KHÔNG nội dung (sole-egress)
    assert ws.snaps["pending"]["statuses"] == [S.PENDING_APPROVAL]
    assert ws.snaps["pending"]["cards"][0]["suggested_reply"] == "Nháp hoàn tiền"
    assert env.store.msgs(cid, "ai") == []  # nháp chưa duyệt KHÔNG thành tin nhắn
    await _settle((ws, task))
    assert env.audits[0]["outcome"] == TurnOutcome.HELD_FOR_APPROVAL


async def test_awaiting_customer_keeps_the_original_intent(env: Any) -> None:
    customer = uuid.uuid4()
    cid = env.store.add_conv(customer_id=customer, status=S.REPLIED)
    env.pipe.final = _final(S.AWAITING_CUSTOMER, reply="Cho em xin mã đơn ạ.", intent="refund")
    ws, task = await _open(env, customer)
    ws.push(_msg("em muốn hoàn tiền", "a-1"))
    await until(lambda: bool(ws.frames("reply")))
    await _settle((ws, task))
    assert (env.store.convs[cid]["status"], env.store.convs[cid]["current_intent"]) == (S.AWAITING_CUSTOMER, "refund")


async def test_pipeline_exception_goes_to_human_queue_with_error_card(env: Any) -> None:
    customer = uuid.uuid4()
    cid = env.store.add_conv(customer_id=customer, status=S.REPLIED)
    env.pipe.error = RuntimeError("boom")
    ws, task = await _open(env, customer)
    ws.push(_msg("đơn của em đâu", "e-1"))
    await until(lambda: bool(ws.frames("handoff")))
    await _settle((ws, task))

    conv = env.store.convs[cid]
    ai = env.store.msgs(cid, "ai")
    assert ws.frames("handoff") == [{"type": "handoff", "content": chat._ERROR_REPLY, "message_id": str(ai[0].id)}]
    assert conv["status"] == S.IN_HUMAN_QUEUE  # PRD §15: lỗi kỹ thuật → hàng đợi người, gắn nhãn [error]
    assert conv["escalation_reason"].startswith("[error]") and conv["priority"] == "high"
    card = conv["escalation_card"]
    assert card["summary"] == "đơn của em đâu" and card["escalation_reason"].startswith("[error]")
    assert card["priority"] == "high"
    assert env.audits[0]["outcome"] == TurnOutcome.ERROR


# ── CAS: admin tiếp quản / đóng ca trong lúc pipeline chạy (GRAPH-02.2) ──────
@pytest.mark.parametrize("status_now", [S.HUMAN_HANDLING, S.RESOLVED])
async def test_status_change_mid_pipeline_discards_the_turn(env: Any, status_now: str) -> None:
    customer, admin = uuid.uuid4(), uuid.uuid4()
    cid = env.store.add_conv(customer_id=customer, status=S.REPLIED)
    env.pipe.gate = asyncio.Event()
    ws, task = await _open(env, customer)
    ws.push(_msg("size M còn không", "x-1"))
    await until(lambda: len(env.pipe.calls) == 1)

    # Admin bấm Tiếp quản / Đóng ca (đã commit) trong lúc pipeline còn chạy.
    env.store.convs[cid]["status"] = status_now
    env.store.convs[cid]["assigned_admin_id"] = admin if status_now == S.HUMAN_HANDLING else None
    env.pipe.gate.set()
    await until(lambda: bool(ws.frames("status")))
    await _settle((ws, task))

    holder = str(admin) if status_now == S.HUMAN_HANDLING else None
    assert ws.frames("status") == [{"type": "status", "status": status_now, "assigned_admin_id": holder}]
    assert ws.frames("reply") == [] and ws.frames("handoff") == []  # AI KHÔNG nói chen vào ca người đang giữ
    assert env.store.msgs(cid, "ai") == [] and env.store.convs[cid]["status"] == status_now
    audit = env.audits[0]
    assert audit["outcome"] == TurnOutcome.QUEUED_FOR_HUMAN
    detail = audit["delivery_detail"]
    assert (detail["discarded"], detail["reason"], detail["status_now"]) == (True, "status_changed", status_now)


async def test_lost_cas_is_discarded_even_when_the_status_reread_fails(
    env: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    customer, admin = uuid.uuid4(), uuid.uuid4()
    cid = env.store.add_conv(customer_id=customer, status=S.REPLIED)
    env.pipe.gate = asyncio.Event()
    real = conversation_service.get_status_and_admin
    broken = {"on": False}

    async def reread_fails(session: Any, conversation_id: uuid.UUID, *, for_update: bool = False) -> Any:
        if broken["on"]:
            raise RuntimeError("Neon ngắt kết nối")
        return await real(session, conversation_id, for_update=for_update)

    monkeypatch.setattr(conversation_service, "get_status_and_admin", reread_fails)
    ws, task = await _open(env, customer)
    ws.push(_msg("size M còn không", "y-1"))
    await until(lambda: len(env.pipe.calls) == 1)
    env.store.convs[cid].update(status=S.HUMAN_HANDLING, assigned_admin_id=admin)  # admin vừa tiếp quản…
    broken["on"] = True  # …và lần đọc lại status sau khi CAS thua cũng lỗi
    admin_q = env.hub.register(str(cid))
    env.pipe.gate.set()
    await until(lambda: bool(ws.frames("status")))
    await _settle((ws, task))

    # CAS thua = lượt BỊ BỎ dù không biết status mới: AI KHÔNG nói chen vào ca admin đã nhận (GRAPH-02.2).
    assert ws.frames("status") == [{"type": "status", "status": None, "assigned_admin_id": None}]
    assert ws.frames("reply") == [] and env.store.msgs(cid, "ai") == [] and drain(admin_q) == []
    assert env.audits[0]["delivery_detail"]["discarded"] is True


# ── Lượt sống sót khi socket chết giữa chừng (GRAPH-02.1) ────────────────────
async def test_turn_completes_and_persists_after_the_socket_closes_mid_turn(env: Any) -> None:
    customer = uuid.uuid4()
    cid = env.store.add_conv(customer_id=customer, status=S.REPLIED)
    env.pipe.gate = asyncio.Event()
    ws, task = await _open(env, customer, name="old")
    ws.push(_msg("đơn 716449 tới đâu rồi", "k-1"))
    await until(lambda: len(env.pipe.calls) == 1)

    ws.drop()  # khách đóng tab giữa lượt → reader kết thúc, kết nối đóng
    await asyncio.wait_for(task, 2)
    ws2, task2 = await _open(env, customer, name="new")  # khách mở lại /chat
    env.pipe.gate.set()
    await asyncio.wait_for(asyncio.gather(*list(chat._turn_tasks)), 2)

    ai = env.store.msgs(cid, "ai")
    assert len(ai) == 1 and env.store.convs[cid]["status"] == S.REPLIED and len(env.audits) == 1
    # Trả lời tới socket MỚI qua hub (không mất), socket cũ không còn đăng ký (không rò queue).
    assert ws2.frames("message") == [
        {"type": "message", "from": "ai", "content": REPLY, "message_id": str(ai[0].id), "client_msg_id": None}
    ]
    assert env.hub.subscriber_count(str(cid)) == 1
    await _settle((ws2, task2))


# ── Tuần tự theo khách + chọn ca (GRAPH-02.3) ────────────────────────────────
async def test_two_concurrent_first_messages_of_one_customer_open_one_case(env: Any) -> None:
    customer = uuid.uuid4()
    a, ta = await _open(env, customer, name="a")
    b, tb = await _open(env, customer, name="b")
    a.push(_msg("chào shop", "a-1"))
    b.push(_msg("shop ơi", "b-1"))
    await until(lambda: bool(a.frames("reply")) and bool(b.frames("reply")))
    await _settle((a, ta), (b, tb))

    convs = _customer_convs(env.store, customer)
    assert len(convs) == 1  # KHÔNG đẻ hai ca cho một khách
    assert sorted(m.content for m in env.store.msgs(convs[0]["id"], "customer")) == ["chào shop", "shop ơi"]


async def test_turns_of_one_customer_run_one_at_a_time_in_arrival_order(env: Any) -> None:
    customer = uuid.uuid4()
    env.store.add_conv(customer_id=customer, status=S.REPLIED)
    env.pipe.gate = asyncio.Event()
    a, ta = await _open(env, customer, name="a")
    b, tb = await _open(env, customer, name="b")
    a.push(_msg("câu một", "1"))
    await until(lambda: len(env.pipe.calls) == 1)
    b.push(_msg("câu hai", "2"))
    await until(lambda: len(b.frames("ack")) == 1)
    await asyncio.sleep(0.05)
    assert len(env.pipe.calls) == 1  # lượt của tab b CHỜ lượt của tab a xong

    env.pipe.gate.set()
    await until(lambda: len(env.pipe.calls) == 2)
    second = env.pipe.calls[1]
    assert second["input"] == "câu hai"
    # Lịch sử của lượt sau đã có trọn lượt trước (không đọc chồng nhau).
    assert second["history"][-2:] == [{"sender": "customer", "content": "câu một"}, {"sender": "ai", "content": REPLY}]
    await _settle((a, ta), (b, tb))


async def test_socket_on_a_closed_case_moves_to_the_case_another_tab_opened(env: Any) -> None:
    customer = uuid.uuid4()
    old = env.store.add_conv(customer_id=customer, status=S.REPLIED)
    ws, task = await _open(env, customer)  # gắn vào ca `old`
    env.store.convs[old]["status"] = S.RESOLVED  # ca bị đóng…
    new = env.store.add_conv(customer_id=customer, status=S.REPLIED)  # …và tab khác đã mở ca mới
    ws.push(_msg("cho hỏi thêm", "n-1"))
    await until(lambda: bool(ws.frames("reply")))

    assert len(_customer_convs(env.store, customer)) == 2  # không đẻ ca thứ ba
    assert [m.content for m in env.store.msgs(new, "customer")] == ["cho hỏi thêm"]
    assert env.hub.subscriber_count(str(new)) == 1 and env.hub.subscriber_count(str(old)) == 0
    await _settle((ws, task))


async def test_case_closed_between_status_read_and_insert_moves_the_message_to_a_new_case(
    env: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    customer = uuid.uuid4()
    old = env.store.add_conv(customer_id=customer, status=S.REPLIED)
    real = chat._load_history
    closed = {"done": False}

    async def history_then_case_closes(conv_id: Any) -> Any:
        out = await real(conv_id)
        if not closed["done"]:  # admin resolve / auto-resolve commit ĐÚNG lúc này (lượt đã đọc status REPLIED)
            closed["done"] = True
            env.store.convs[old]["status"] = S.RESOLVED
        return out

    monkeypatch.setattr(chat, "_load_history", history_then_case_closes)
    ws, task = await _open(env, customer)
    ws.push(_msg("còn size M không shop", "q-1"))
    await until(lambda: bool(ws.frames("reply")))
    await _settle((ws, task))

    convs = _customer_convs(env.store, customer)
    new = next(c["id"] for c in convs if c["id"] != old)
    assert len(convs) == 2 and env.store.msgs(old) == []  # KHÔNG tin nào lọt vào ca đã đóng
    assert [m.content for m in env.store.msgs(new, "customer")] == ["còn size M không shop"]
    # Câu hỏi được trả lời trên ca MỚI (PRD §15), không bị bỏ âm thầm.
    assert env.store.convs[new]["status"] == S.REPLIED and ws.frames("status") == []


async def test_other_tab_sees_the_customer_message_and_the_ai_reply(env: Any) -> None:
    customer = uuid.uuid4()
    cid = env.store.add_conv(customer_id=customer, status=S.REPLIED)
    a, ta = await _open(env, customer, name="a")
    b, tb = await _open(env, customer, name="b")
    a.push(_msg("size L còn không", "t-1"))
    await until(lambda: len(b.frames("message")) == 2)
    customer_msg, ai_msg = env.store.msgs(cid, "customer")[0], env.store.msgs(cid, "ai")[0]
    assert b.frames("message") == [
        {"type": "message", "from": "customer", "content": "size L còn không", "message_id": str(customer_msg.id),
         "client_msg_id": "t-1"},
        {"type": "message", "from": "ai", "content": REPLY, "message_id": str(ai_msg.id), "client_msg_id": None},
    ]
    assert a.frames("message") == []  # socket gửi đã nhận frame trực tiếp → không nhận lại
    await _settle((a, ta), (b, tb))


# ── Nhận tin: ack / chống gửi lại / trần / ping (IDEM-XC.1, FE-01.4, SEC-XC.2) ──
async def test_duplicate_client_msg_id_is_acked_and_the_pipeline_runs_once(env: Any) -> None:
    customer = uuid.uuid4()
    cid = env.store.add_conv(customer_id=customer, status=S.REPLIED)
    ws, task = await _open(env, customer)
    ws.push(_msg("Kiểm tra đơn hàng của mình", "d-1"))
    ws.push(_msg("Kiểm tra đơn hàng của mình", "d-1"))  # bấm lại / gửi lại
    await until(lambda: len(ws.frames("ack")) == 2 and bool(ws.frames("reply")))
    await _settle((ws, task))

    assert [a["duplicate"] for a in ws.frames("ack")] == [False, True]
    assert len(env.pipe.calls) == 1 and len(env.store.msgs(cid, "customer")) == 1
    assert len(ws.frames("reply")) == 1


async def test_resend_after_registry_loss_is_caught_by_the_db_index(env: Any) -> None:
    customer = uuid.uuid4()
    cid = env.store.add_conv(customer_id=customer, status=S.REPLIED)
    ws, task = await _open(env, customer)
    ws.push(_msg("đổi size giúp em", "r-1"))
    await until(lambda: bool(ws.frames("reply")))
    chat._recent_client_ids.clear()  # như khi tiến trình vừa khởi động lại
    ws.push(_msg("đổi size giúp em", "r-1"))
    await until(lambda: len(ws.frames("ack")) == 3)
    await _settle((ws, task))

    assert [a["duplicate"] for a in ws.frames("ack")] == [False, False, True]
    assert len(env.pipe.calls) == 1 and len(env.store.msgs(cid, "customer")) == 1
    assert len(ws.frames("typing")) == 1


async def test_rate_limited_message_gets_error_frame_and_is_not_processed(
    env: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(chat, "_chat_limiter", SlidingWindowLimiter(1, 60))
    customer = uuid.uuid4()
    cid = env.store.add_conv(customer_id=customer, status=S.REPLIED)
    ws, task = await _open(env, customer)
    ws.push(_msg("tin một", "m-1"))
    ws.push(_msg("tin hai", "m-2"))
    await until(lambda: bool(ws.frames("error")) and bool(ws.frames("reply")))
    await _settle((ws, task))

    assert ws.frames("error") == [{"type": "error", "code": "rate_limited", "client_msg_id": "m-2"}]
    assert [a["client_msg_id"] for a in ws.frames("ack")] == ["m-1"]
    assert [m.content for m in env.store.msgs(cid, "customer")] == ["tin một"] and len(env.pipe.calls) == 1


async def test_resend_of_an_accepted_message_does_not_use_the_rate_budget(
    env: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Trần 2 tin: tin GỬI LẠI (id đã nhận) không tốn slot và không bị báo rate_limited — tin gốc ĐÃ lưu + trả lời.
    monkeypatch.setattr(chat, "_chat_limiter", SlidingWindowLimiter(2, 60))
    customer = uuid.uuid4()
    cid = env.store.add_conv(customer_id=customer, status=S.REPLIED)
    ws, task = await _open(env, customer)
    ws.push(_msg("tin một", "m-1"))
    ws.push(_msg("tin một", "m-1"))  # gửi lại (chưa thấy ack)
    ws.push(_msg("tin hai", "m-2"))
    await until(lambda: len(ws.frames("ack")) == 3 and len(ws.frames("reply")) == 2)
    await _settle((ws, task))

    assert ws.frames("error") == []
    assert [(a["client_msg_id"], a["duplicate"]) for a in ws.frames("ack")] == [
        ("m-1", False), ("m-1", True), ("m-2", False)
    ]
    assert [m.content for m in env.store.msgs(cid, "customer")] == ["tin một", "tin hai"] and len(env.pipe.calls) == 2


async def test_ping_is_answered_while_a_turn_is_running(env: Any) -> None:
    customer = uuid.uuid4()
    env.store.add_conv(customer_id=customer, status=S.REPLIED)
    env.pipe.gate = asyncio.Event()
    ws, task = await _open(env, customer)
    ws.push(_msg("câu hỏi dài", "p-1"))
    await until(lambda: len(env.pipe.calls) == 1)
    ws.push(json.dumps({"type": "ping"}))
    await until(lambda: bool(ws.frames("pong")))
    assert ws.frames("reply") == []  # lượt vẫn đang chạy — pong KHÔNG phải chờ nó

    env.pipe.gate.set()
    await until(lambda: bool(ws.frames("reply")))
    await _settle((ws, task))


async def test_legacy_raw_text_frame_is_a_message_without_client_id(env: Any) -> None:
    customer = uuid.uuid4()
    cid = env.store.add_conv(customer_id=customer, status=S.REPLIED)
    ws, task = await _open(env, customer)
    ws.push("chào shop")
    await until(lambda: bool(ws.frames("reply")))
    await _settle((ws, task))
    assert ws.frames("ack") == [{"type": "ack", "client_msg_id": None, "message_id": None, "duplicate": False}]
    assert [(m.content, m.client_msg_id) for m in env.store.msgs(cid, "customer")] == [("chào shop", None)]


# ── Status-gate giữ nguyên (08c) ─────────────────────────────────────────────
async def test_status_gated_message_reaches_admin_without_running_ai(env: Any) -> None:
    customer, admin = uuid.uuid4(), uuid.uuid4()
    cid = env.store.add_conv(customer_id=customer, status=S.HUMAN_HANDLING, assigned_admin_id=admin)
    admin_q = env.hub.register(str(cid))
    ws, task = await _open(env, customer)
    ws.push(_msg("anh ơi em gửi ảnh rồi", "g-1"))
    await until(lambda: len(env.store.msgs(cid, "customer")) == 1)
    await _settle((ws, task))

    saved = env.store.msgs(cid, "customer")[0]
    assert drain(admin_q) == [
        {"type": "message", "from": "customer", "content": "anh ơi em gửi ảnh rồi", "message_id": str(saved.id),
         "client_msg_id": "g-1"}
    ]
    assert env.pipe.calls == [] and ws.frames("typing") == [] and env.audits == []


# ── Nhánh degrade (DB chết lúc mở kết nối) vẫn nói giao thức v2 ───────────────
async def test_ai_only_degraded_path_speaks_protocol_v2(env: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    async def db_down(session: Any, customer_id: uuid.UUID) -> Any:
        raise RuntimeError("db down")

    monkeypatch.setattr(conversation_service, "get_active_conversation_for_customer", db_down)
    ws = FakeWebSocket(env.store, name="tab")
    ws.query_params = {"token": str(uuid.uuid4())}
    task = asyncio.create_task(chat.chat_ws(ws))  # type: ignore[arg-type]
    ws.push(json.dumps({"type": "ping"}))
    ws.push(_msg("alo", "z-1"))
    await until(lambda: bool(ws.frames("reply")))
    ws.drop()
    await asyncio.wait_for(task, 2)
    assert ws.sent == [
        {"type": "pong"},
        {"type": "ack", "client_msg_id": "z-1", "message_id": None, "duplicate": False},
        {"type": "typing"},
        {"type": "reply", "content": REPLY, "message_id": None},
    ]


async def test_ai_only_resend_does_not_use_the_rate_budget(env: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    async def db_down(session: Any, customer_id: uuid.UUID) -> Any:
        raise RuntimeError("db down")

    monkeypatch.setattr(conversation_service, "get_active_conversation_for_customer", db_down)
    monkeypatch.setattr(chat, "_chat_limiter", SlidingWindowLimiter(1, 60))
    ws = FakeWebSocket(env.store, name="tab")
    ws.query_params = {"token": str(uuid.uuid4())}
    task = asyncio.create_task(chat.chat_ws(ws))  # type: ignore[arg-type]
    ws.push(_msg("alo", "z-1"))
    ws.push(_msg("alo", "z-1"))  # gửi lại → ack duplicate, KHÔNG rate_limited
    await until(lambda: len(ws.frames("ack")) == 2)
    ws.drop()
    await asyncio.wait_for(task, 2)
    assert ws.frames("error") == [] and [a["duplicate"] for a in ws.frames("ack")] == [False, True]
    assert len(ws.frames("reply")) == 1


# ── Quyết định giao (hàm thuần) ──────────────────────────────────────────────
def test_plan_delivery_cas_uses_prior_status_or_the_ai_active_set() -> None:
    known = chat.plan_delivery(
        prior_status=S.REPLIED, status_out=S.REPLIED, final=_final(S.REPLIED), reply="x", customer_text="q", held=False
    )
    assert known.allowed_from == frozenset({S.REPLIED}) and known.frame == "reply"
    unknown = chat.plan_delivery(
        prior_status=None, status_out=S.REPLIED, final=_final(S.REPLIED), reply="x", customer_text="q", held=False
    )
    # Không đọc được status đầu lượt → chỉ ghi đè status AI-active: KHÔNG bao giờ đè ca người đang giữ / đã đóng.
    assert S.REPLIED in unknown.allowed_from and S.ACTIVE_AI in unknown.allowed_from
    for blocked in (S.HUMAN_HANDLING, S.IN_HUMAN_QUEUE, S.PENDING_APPROVAL, S.RESOLVED, S.CLOSED):
        assert blocked not in unknown.allowed_from
