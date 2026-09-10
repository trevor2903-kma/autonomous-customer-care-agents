"""Audit v2 — route HITL admin: bảng chuyển + CAS + 409 + audit CÙNG transaction + phát SAU commit. Offline.

FE-03.1 (duyệt trùng / gửi nháp đã từ chối / hồi sinh ca đã đóng), FE-03.2 + GRAPH-02.4 (cướp ca), FE-03.3
(kéo ngược ca đang có người xử lý), DATA-01.1 (hành động admin không có audit).
"""

from __future__ import annotations

import uuid
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi import HTTPException

from app.api.routes import admin as routes
from app.api.ws.hub import INBOX_KEY, ConnectionHub
from app.models.enums import ConversationStatus as S
from app.schemas.admin import ApproveRequest
from app.schemas.gate import GateConfigUpdate
from app.services import conversation_service, gate_service
from tests.test_state_support import FakeStore, drain, install_service_fakes

DRAFT = "Dạ shop hỗ trợ đổi trong 7 ngày kể từ khi nhận hàng ạ."


class _LoggingHub(ConnectionHub):
    """Hub ghi mỗi lần phát vào nhật ký store → kiểm được 'phát SAU commit'."""

    def __init__(self, store: FakeStore) -> None:
        super().__init__()
        self._store = store

    async def publish(self, conversation_id: str, payload: dict[str, Any], *, exclude: Any = None) -> None:
        self._store.log.append(f"publish:{payload.get('type')}")
        await super().publish(conversation_id, payload, exclude=exclude)


@pytest.fixture
def store(monkeypatch: pytest.MonkeyPatch) -> FakeStore:
    st = FakeStore()
    install_service_fakes(monkeypatch, st)
    st.hub = _LoggingHub(st)  # type: ignore[attr-defined]
    monkeypatch.setattr(routes, "hub", st.hub)  # type: ignore[attr-defined]
    return st


def _admin() -> SimpleNamespace:
    return SimpleNamespace(id=uuid.uuid4())


async def _approve(store: FakeStore, cid: uuid.UUID, admin: Any = None, content: str | None = None) -> Any:
    return await routes.approve_draft(
        cid, ApproveRequest(content=content), session=store.session(), admin=admin or _admin()
    )


async def _act(store: FakeStore, verb: str, cid: uuid.UUID, admin: Any) -> Any:
    fn = {
        "takeover": routes.takeover_conversation,
        "resolve": routes.resolve_conversation,
        "reject": routes.reject_draft,
    }[verb]
    return await fn(cid, session=store.session(), admin=admin)


async def _code(coro: Any) -> int:
    with pytest.raises(HTTPException) as exc:
        await coro
    return exc.value.status_code


# ── Bảng chuyển (hàm thuần) ──────────────────────────────────────────────────
def test_transition_table_matches_contract() -> None:
    me, other = uuid.uuid4(), uuid.uuid4()
    c = routes.transition_conflict
    assert c("approve", S.PENDING_APPROVAL, None, me) is None
    assert c("reject", S.PENDING_APPROVAL, None, me) is None
    for status in (S.REPLIED, S.IN_HUMAN_QUEUE, S.HUMAN_HANDLING, S.RESOLVED, S.CLOSED):
        assert c("approve", status, None, me) == routes.CONFLICT_NOT_PENDING
        assert c("reject", status, None, me) == routes.CONFLICT_NOT_PENDING
    for verb in ("takeover", "resolve"):
        for status in (S.ACTIVE_AI, S.REPLIED, S.AWAITING_CUSTOMER, S.PENDING_APPROVAL, S.IN_HUMAN_QUEUE):
            assert c(verb, status, None, me) is None
        assert c(verb, S.HUMAN_HANDLING, me, me) is None  # chính mình → idempotent
        assert c(verb, S.HUMAN_HANDLING, None, me) is None  # không ai giữ (dữ liệu cũ) → không kẹt ca
        assert c(verb, S.HUMAN_HANDLING, other, me) == routes.CONFLICT_HELD
        assert c(verb, S.RESOLVED, None, me) == routes.CONFLICT_CLOSED
        assert c(verb, S.CLOSED, None, me) == routes.CONFLICT_CLOSED


# ── Duyệt nháp (FE-03.1) ─────────────────────────────────────────────────────
async def test_approve_twice_second_is_409_and_customer_gets_one_message(store: FakeStore) -> None:
    cid = store.add_conv(status=S.PENDING_APPROVAL, card={"suggested_reply": DRAFT})
    customer_q = store.hub.register(str(cid))  # type: ignore[attr-defined]

    await _approve(store, cid)
    assert await _code(_approve(store, cid)) == 409  # admin thứ hai bấm trên màn cũ

    assert [m.content for m in store.msgs(cid, "ai")] == [DRAFT]  # lưu MỘT lần
    frames = drain(customer_q)
    assert [f["type"] for f in frames] == ["message", "status"]  # khách nhận MỘT tin (không trùng)
    assert frames[0]["message_id"] == str(store.msgs(cid, "ai")[0].id)
    assert frames[1] == {"type": "status", "status": "REPLIED", "assigned_admin_id": None}
    assert store.convs[cid]["status"] == S.REPLIED


async def test_approve_after_reject_is_409_and_nothing_sent(store: FakeStore) -> None:
    cid = store.add_conv(status=S.PENDING_APPROVAL, card={"suggested_reply": DRAFT})
    await _act(store, "reject", cid, _admin())
    customer_q = store.hub.register(str(cid))  # type: ignore[attr-defined]

    assert await _code(_approve(store, cid)) == 409
    assert store.msgs(cid) == [] and drain(customer_q) == []  # nháp đã bị từ chối KHÔNG tới khách
    assert store.convs[cid]["status"] == S.IN_HUMAN_QUEUE


@pytest.mark.parametrize("status", [S.HUMAN_HANDLING, S.RESOLVED])
async def test_approve_never_overwrites_takeover_or_resurrects_closed_case(
    store: FakeStore, status: str
) -> None:
    holder = uuid.uuid4() if status == S.HUMAN_HANDLING else None
    cid = store.add_conv(status=status, assigned_admin_id=holder, card={"suggested_reply": DRAFT})
    assert await _code(_approve(store, cid)) == 409
    assert store.convs[cid]["status"] == status and store.msgs(cid) == []


async def test_approve_commits_before_publishing(store: FakeStore) -> None:
    cid = store.add_conv(status=S.PENDING_APPROVAL, card={"suggested_reply": DRAFT})
    await _approve(store, cid)
    first_publish = next(i for i, e in enumerate(store.log) if e.startswith("publish:"))
    assert store.log.index("commit") < first_publish


async def test_approve_empty_draft_is_still_400(store: FakeStore) -> None:
    cid = store.add_conv(status=S.PENDING_APPROVAL, card={"suggested_reply": ""})
    assert await _code(_approve(store, cid)) == 400  # hành vi cũ giữ nguyên: không bao giờ gửi tin rỗng


# ── Tiếp quản / đóng ca / từ chối (FE-03.2, GRAPH-02.4, FE-03.3) ─────────────
async def test_takeover_by_second_admin_is_409_same_admin_is_200(store: FakeStore) -> None:
    a, b = _admin(), _admin()
    cid = store.add_conv(status=S.IN_HUMAN_QUEUE)
    conv = await _act(store, "takeover", cid, a)
    assert conv.status == S.HUMAN_HANDLING and conv.assigned_admin_id == a.id

    assert await _code(_act(store, "takeover", cid, b)) == 409  # KHÔNG cướp ca âm thầm
    assert store.convs[cid]["assigned_admin_id"] == a.id

    again = await _act(store, "takeover", cid, a)  # chính A bấm lại → idempotent
    assert again.assigned_admin_id == a.id


async def test_resolve_of_another_admins_case_is_409(store: FakeStore) -> None:
    a, b = _admin(), _admin()
    cid = store.add_conv(status=S.HUMAN_HANDLING, assigned_admin_id=a.id)
    assert await _code(_act(store, "resolve", cid, b)) == 409
    assert store.convs[cid]["status"] == S.HUMAN_HANDLING

    customer_q = store.hub.register(str(cid))  # type: ignore[attr-defined]
    await _act(store, "resolve", cid, a)
    # UX-02.3: resolve PHÁT frame status → khách rời "đang chờ nhân viên" ngay.
    assert drain(customer_q) == [{"type": "status", "status": "RESOLVED", "assigned_admin_id": str(a.id)}]
    assert await _code(_act(store, "resolve", cid, a)) == 409  # đã đóng


async def test_reject_never_pulls_a_handled_case_back_to_queue(store: FakeStore) -> None:
    a = _admin()
    cid = store.add_conv(status=S.HUMAN_HANDLING, assigned_admin_id=a.id)
    assert await _code(_act(store, "reject", cid, _admin())) == 409
    assert store.convs[cid]["status"] == S.HUMAN_HANDLING


async def test_lost_cas_race_is_409_changed(store: FakeStore, monkeypatch: pytest.MonkeyPatch) -> None:
    # Đọc thấy IN_HUMAN_QUEUE nhưng admin khác đã tiếp quản trước khi UPDATE chạy → CAS thua → 409.
    a, b = _admin(), _admin()
    cid = store.add_conv(status=S.HUMAN_HANDLING, assigned_admin_id=a.id)
    real = conversation_service.get_status_and_admin
    calls = {"n": 0}

    async def stale_first(session: Any, conversation_id: uuid.UUID) -> Any:
        calls["n"] += 1
        return (S.IN_HUMAN_QUEUE, None) if calls["n"] == 1 else await real(session, conversation_id)

    monkeypatch.setattr(conversation_service, "get_status_and_admin", stale_first)
    with pytest.raises(HTTPException) as exc:
        await _act(store, "takeover", cid, b)
    assert exc.value.status_code == 409 and exc.value.detail == routes.CONFLICT_CHANGED
    assert store.convs[cid]["assigned_admin_id"] == a.id and store.admin_audit() == []


@pytest.mark.parametrize("verb", ["takeover", "resolve", "reject"])
async def test_missing_conversation_is_404(store: FakeStore, verb: str) -> None:
    assert await _code(_act(store, verb, uuid.uuid4(), _admin())) == 404
    assert await _code(_approve(store, uuid.uuid4())) == 404


# ── Audit hành động admin (DATA-01.1) ────────────────────────────────────────
@pytest.mark.parametrize(
    ("verb", "start", "end"),
    [
        ("takeover", S.IN_HUMAN_QUEUE, S.HUMAN_HANDLING),
        ("resolve", S.REPLIED, S.RESOLVED),
        ("reject", S.PENDING_APPROVAL, S.IN_HUMAN_QUEUE),
    ],
)
async def test_admin_action_writes_exactly_one_audit_row(
    store: FakeStore, verb: str, start: str, end: str
) -> None:
    a = _admin()
    cid = store.add_conv(status=start)
    await _act(store, verb, cid, a)
    rows = store.admin_audit()
    assert len(rows) == 1
    row = rows[0]
    assert (row.node, row.action, row.conversation_id, row.turn_id) == ("admin", verb, cid, None)
    assert row.detail == {"admin_id": str(a.id), "from_status": start, "to_status": end}


async def test_approve_audit_row_flags_edit_without_copying_content(store: FakeStore) -> None:
    a = _admin()
    same = store.add_conv(status=S.PENDING_APPROVAL, card={"suggested_reply": DRAFT})
    edited = store.add_conv(status=S.PENDING_APPROVAL, card={"suggested_reply": DRAFT})
    await _approve(store, same, a)
    await _approve(store, edited, a, content="Dạ shop đổi trong 7 ngày, anh/chị mang hoá đơn giúp em ạ.")
    by_conv = {r.conversation_id: r for r in store.admin_audit()}
    assert by_conv[same].detail == {
        "admin_id": str(a.id), "from_status": "PENDING_APPROVAL", "to_status": "REPLIED", "edited": False
    }
    assert by_conv[edited].detail["edited"] is True
    assert all(DRAFT not in str(r.detail) for r in store.admin_audit())  # KHÔNG chép nội dung nháp


async def test_refused_action_writes_no_audit_and_publishes_nothing(store: FakeStore) -> None:
    cid = store.add_conv(status=S.HUMAN_HANDLING, assigned_admin_id=uuid.uuid4())
    inbox_q = store.hub.register(INBOX_KEY)  # type: ignore[attr-defined]
    assert await _code(_act(store, "takeover", cid, _admin())) == 409
    assert store.admin_audit() == [] and drain(inbox_q) == []


async def test_gate_update_writes_one_audit_row(store: FakeStore, monkeypatch: pytest.MonkeyPatch) -> None:
    snap = gate_service.GateSnapshot(
        auto_reply_enabled=False,
        auto_resolve_enabled=True,
        auto_resolve_minutes=30,
        auto_resolve_grace_minutes=15,
        rules=(),
    )

    async def fake_update(**kwargs: Any) -> gate_service.GateSnapshot:
        return snap

    monkeypatch.setattr(gate_service, "update_gate_config", fake_update)
    a = _admin()
    out = await routes.update_gate_config(
        GateConfigUpdate(auto_reply_enabled=False), session=store.session(), admin=a
    )
    assert out.auto_reply_enabled is False
    rows = store.admin_audit()
    assert len(rows) == 1 and rows[0].action == "gate_update" and rows[0].conversation_id is None
    assert rows[0].detail == {"admin_id": str(a.id), "changes": {"auto_reply_enabled": False}}
