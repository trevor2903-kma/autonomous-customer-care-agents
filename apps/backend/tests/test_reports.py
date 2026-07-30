"""Tổng hợp báo cáo (slice obs P2) — hàm THUẦN trên TurnView. Offline, KHÔNG DB/network."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from app.models.audit_log import AuditLog
from app.models.enums import TurnOutcome
from app.services import report_service as rs

NOW = datetime(2026, 7, 30, 10, 0, tzinfo=UTC)


def _turn(outcome: str, *, intent="shipping", ms=1200, conf=0.8, fallback=False,
          blocking=(), created=NOW) -> rs.TurnView:
    return rs.TurnView(
        turn_id=uuid.uuid4(), conversation_id=uuid.uuid4(), created_at=created,
        customer_text="x", intent=intent, outcome=outcome,
        agent_action="human_handoff" if outcome == TurnOutcome.QUEUED_FOR_HUMAN else "auto_reply",
        priority="low", severity="low", duration_ms=ms, confidence=conf,
        flags=[], blocking_flags=list(blocking), fallback=fallback,
    )


# ── Phân vị ──────────────────────────────────────────────────────────────────
def test_percentile_nearest_rank_returns_a_real_measurement() -> None:
    values = [100, 200, 300, 400, 5000]
    assert rs.percentile(values, 50) == 300
    assert rs.percentile(values, 95) == 5000  # p95 phải chạm được đuôi, không bị nội suy làm mềm
    assert rs.percentile(values, 100) == 5000
    assert rs.percentile([], 50) is None
    assert rs.percentile([42], 95) == 42


# ── KPI tổng ─────────────────────────────────────────────────────────────────
def test_summary_outcome_percentages() -> None:
    turns = [
        _turn(TurnOutcome.SENT), _turn(TurnOutcome.SENT),
        _turn(TurnOutcome.HELD_FOR_APPROVAL),
        _turn(TurnOutcome.QUEUED_FOR_HUMAN, blocking=["out_of_domain"]),
    ]
    s = rs.summarize(turns)
    assert s["turns"] == 4
    assert (s["auto_reply_pct"], s["draft_pct"], s["handoff_pct"]) == (50.0, 25.0, 25.0)
    assert s["outcomes"]["sent"] == 2


def test_summary_nfr_and_percentiles() -> None:
    # 4 lượt <= 5s, 1 lượt 9s -> 80% dat NFR-1; p95 phai loi ra duoc lượt cham.
    turns = [_turn(TurnOutcome.SENT, ms=ms) for ms in (900, 1200, 2000, 4800, 9000)]
    lat = rs.summarize(turns)["latency"]
    assert lat["within_nfr_pct"] == 80.0
    assert lat["nfr_threshold_ms"] == 5000
    assert lat["p50_ms"] == 2000
    assert lat["p95_ms"] == 9000
    assert lat["avg_ms"] == round((900 + 1200 + 2000 + 4800 + 9000) / 5)
    assert lat["measured"] == 5


def test_summary_escalation_reasons_counted_by_blocking_flag() -> None:
    # Bóc tách theo CỜ CHẶN thật: một lượt có 2 cờ thì tính cho CẢ HAI (cờ mới là thứ định tuyến).
    turns = [
        _turn(TurnOutcome.QUEUED_FOR_HUMAN, blocking=["low_retrieval_score"]),
        _turn(TurnOutcome.QUEUED_FOR_HUMAN, blocking=["low_retrieval_score", "multi_intent"]),
        _turn(TurnOutcome.QUEUED_FOR_HUMAN, blocking=["out_of_domain"]),
        _turn(TurnOutcome.SENT),  # không escalate -> KHÔNG được tính vào mẫu
    ]
    reasons = {r["flag"]: r for r in rs.summarize(turns)["escalation_reasons"]}
    assert reasons["low_retrieval_score"]["count"] == 2
    assert reasons["low_retrieval_score"]["pct"] == 66.7  # mẫu = 3 lượt escalate, KHÔNG phải 4
    assert reasons["multi_intent"]["count"] == 1
    assert list(reasons)[0] == "low_retrieval_score"  # nhiều nhất lên đầu


def test_summary_fallback_pct_is_agent4_not_agent3() -> None:
    turns = [_turn(TurnOutcome.SENT, fallback=True), _turn(TurnOutcome.SENT), _turn(TurnOutcome.SENT),
             _turn(TurnOutcome.SENT)]
    s = rs.summarize(turns)
    assert s["fallback_pct"] == 25.0
    assert s["handoff_pct"] == 0.0  # fallback (Agent 4) KHÁC chuyển người (Agent 3)


def test_summary_empty_is_zero_not_crash() -> None:
    s = rs.summarize([])
    assert s["turns"] == 0 and s["auto_reply_pct"] == 0.0
    assert s["latency"]["p95_ms"] is None and s["latency"]["within_nfr_pct"] == 0.0


# ── Theo intent ──────────────────────────────────────────────────────────────
def test_by_intent_rows_sorted_by_volume() -> None:
    turns = [
        _turn(TurnOutcome.SENT, intent="shipping", ms=1000, conf=0.9),
        _turn(TurnOutcome.SENT, intent="shipping", ms=3000, conf=0.7),
        _turn(TurnOutcome.QUEUED_FOR_HUMAN, intent="other", ms=2000, conf=0.4),
    ]
    rows = rs.summarize_by_intent(turns)
    assert [r["intent"] for r in rows] == ["shipping", "other"]
    ship = rows[0]
    assert ship["turns"] == 2 and ship["auto_pct"] == 100.0
    assert ship["avg_latency_ms"] == 2000
    assert ship["avg_confidence"] == 0.8
    assert rows[1]["handoff_pct"] == 100.0


def test_by_intent_groups_missing_intent() -> None:
    rows = rs.summarize_by_intent([_turn(TurnOutcome.ERROR, intent=None)])
    assert rows[0]["intent"] == "(không rõ)"


# ── Gộp dòng audit thành lượt ────────────────────────────────────────────────
def _row(node, **kw) -> AuditLog:
    return AuditLog(
        turn_id=kw.pop("turn_id", uuid.uuid4()), conversation_id=uuid.uuid4(), node=node,
        created_at=kw.pop("created_at", NOW), uncertainty_flags=kw.pop("flags", []),
        detail=kw.pop("detail", {}), **kw,
    )


def test_build_turn_view_joins_decision_and_response_into_delivery() -> None:
    tid = uuid.uuid4()
    rows = [
        _row("customer", turn_id=tid, detail={"customer_text": "vé xem phim"}),
        _row("decision", turn_id=tid, action="human_handoff",
             escalation_reason="blocking_flags=['out_of_domain']",
             detail={"blocking_flags": ["out_of_domain"]}),
        _row("response", turn_id=tid, action="human_handoff", flags=["hallucination_risk"]),
        _row("delivery", turn_id=tid, action=TurnOutcome.QUEUED_FOR_HUMAN, duration_ms=3801,
             confidence=0.41, flags=["out_of_domain"],
             detail={"intent": "other", "agent_action": "human_handoff", "customer_text": "vé xem phim",
                     "priority": "low", "severity": "low"}),
    ]
    v = rs.build_turn_view(rows)
    assert v is not None
    assert v.outcome == TurnOutcome.QUEUED_FOR_HUMAN and v.intent == "other"
    assert v.duration_ms == 3801 and v.customer_text == "vé xem phim"
    assert v.blocking_flags == ["out_of_domain"]  # từ dòng decision
    assert v.fallback is True  # từ dòng response
    assert v.short_id.startswith("trc_") and len(v.short_id) == 12


def test_incomplete_turn_is_dropped_not_counted() -> None:
    # Thiếu dòng delivery = lượt dở dang (tiến trình chết giữa chừng) -> đếm vào KPI là bịa kết cục.
    tid = uuid.uuid4()
    assert rs.build_turn_view([_row("customer", turn_id=tid), _row("intent", turn_id=tid)]) is None
    assert rs.group_turns([_row("customer", turn_id=tid)]) == []


def test_group_turns_sorts_newest_first_and_ignores_legacy_rows() -> None:
    old, new = uuid.uuid4(), uuid.uuid4()
    rows = [
        _row("delivery", turn_id=old, action=TurnOutcome.SENT, created_at=NOW - timedelta(hours=2), detail={}),
        _row("delivery", turn_id=new, action=TurnOutcome.SENT, created_at=NOW, detail={}),
        # Dòng CŨ do task nền REST ghi: không có turn_id -> phải bị loại khỏi mọi tỉ lệ.
        AuditLog(turn_id=None, node="pipeline", created_at=NOW, uncertainty_flags=[], detail={}),
    ]
    views = rs.group_turns(rows)
    assert [v.turn_id for v in views] == [new, old]


# ── Khoảng thời gian ─────────────────────────────────────────────────────────
def test_range_start_semantics() -> None:
    assert rs.range_start("all") is None
    assert rs.range_start("7d") < datetime.now(UTC)
    today = rs.range_start("today")
    # Nửa đêm THEO GIỜ SHOP (UTC+7) -> quy về UTC là 17:00 hôm trước, không phải 00:00 UTC.
    local = today + timedelta(hours=rs.settings.reports_tz_offset_hours)
    assert (local.hour, local.minute, local.second) == (0, 0, 0)
