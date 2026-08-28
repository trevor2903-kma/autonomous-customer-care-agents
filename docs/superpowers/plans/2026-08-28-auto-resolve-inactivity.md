# Auto-resolve Inactivity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tự động nhắc một lần rồi đóng (`RESOLVED`) các hội thoại phía-AI im lặng quá ngưỡng, tôn trọng gate `auto-resolve`.

**Architecture:** Một asyncio background task (periodic sweep) chạy trong FastAPI lifespan, mỗi `sweep_interval_seconds` quét Postgres tìm ca `REPLIED`/`AWAITING_CUSTOMER` im lặng; một hàm thuần `classify_idle` quyết định NOOP/REMIND/RESOLVE theo hai ngưỡng T1 (`auto_resolve_minutes`) và T2 (`auto_resolve_grace_minutes`). Tin nhắc/đóng là template cố định, phát qua đường persist-message + `hub.publish` sẵn có (sole-egress). Không polling Redis, không LLM, không checkpointer.

**Tech Stack:** Python 3.12 · FastAPI · SQLAlchemy 2 async · Alembic · Pydantic v2 · pytest. Frontend: Next.js 14 · Tailwind · TanStack Query.

**Spec:** `docs/superpowers/specs/2026-08-28-auto-resolve-inactivity-design.md`

## Global Constraints

- Async-first backend; không trộn sync I/O trong route/service.
- Cấu hình đọc từ env qua pydantic-settings; KHÔNG hardcode ngưỡng/URL/secret.
- KHÔNG thêm `ConversationStatus` mới (enum canonical PRD §15 bất biến).
- Response tới khách CHỈ phát qua đường của pipeline (persist `sender=ai` + `hub.publish`); KHÔNG mở đường gửi mới rải rác.
- Sweep CHỈ đụng `REPLIED` và `AWAITING_CUSTOMER`; tuyệt đối không đụng `IN_HUMAN_QUEUE`/`PENDING_APPROVAL`/`HUMAN_HANDLING`/các trạng thái pipeline (FR-ASYNC-4).
- Gate `auto_resolve_enabled=false` → sweep no-op tuyệt đối.
- `make test` phải OFFLINE-xanh (mock/không I/O). Việc chạm DB verify LIVE riêng.
- Neon cần `connect_args={"ssl": True}`; KHÔNG `?sslmode=`.
- Commit mỗi đơn vị công việc, prefix `feat(09c)/test(09c)`.

---

### Task 1: Hàm thuần `classify_idle` + `IdleAction`

Lõi quyết định tất định, không I/O — nền cho toàn bộ sweep. TDD hoàn toàn offline.

**Files:**
- Create: `apps/backend/app/services/auto_resolve.py`
- Test: `apps/backend/tests/test_auto_resolve.py`

**Interfaces:**
- Consumes: `app.models.enums.ConversationStatus`
- Produces:
  - `class IdleAction(StrEnum)` với `NOOP="noop"`, `REMIND="remind"`, `RESOLVE="resolve"`
  - `def classify_idle(*, status: str, last_message_at: datetime | None, reminded_at: datetime | None, now: datetime, t1_minutes: int, t2_minutes: int) -> IdleAction`

- [ ] **Step 1: Viết test thất bại**

Tạo `apps/backend/tests/test_auto_resolve.py`:

```python
"""Auto-resolve (09c) — classify_idle thuần, tất định, offline (không DB/LLM)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.models.enums import ConversationStatus
from app.services.auto_resolve import IdleAction, classify_idle

NOW = datetime(2026, 8, 28, 12, 0, 0, tzinfo=timezone.utc)


def _ago(minutes: int) -> datetime:
    return NOW - timedelta(minutes=minutes)


def test_noop_before_t1() -> None:
    # im lặng 10' < T1=30 → chưa làm gì
    assert (
        classify_idle(
            status=ConversationStatus.REPLIED,
            last_message_at=_ago(10),
            reminded_at=None,
            now=NOW,
            t1_minutes=30,
            t2_minutes=15,
        )
        == IdleAction.NOOP
    )


def test_remind_after_t1_not_yet_reminded() -> None:
    assert (
        classify_idle(
            status=ConversationStatus.REPLIED,
            last_message_at=_ago(31),
            reminded_at=None,
            now=NOW,
            t1_minutes=30,
            t2_minutes=15,
        )
        == IdleAction.REMIND
    )


def test_awaiting_customer_also_reminded() -> None:
    assert (
        classify_idle(
            status=ConversationStatus.AWAITING_CUSTOMER,
            last_message_at=_ago(31),
            reminded_at=None,
            now=NOW,
            t1_minutes=30,
            t2_minutes=15,
        )
        == IdleAction.REMIND
    )


def test_noop_after_remind_before_t2() -> None:
    # đã nhắc 10' trước, T2=15 → chờ tiếp
    assert (
        classify_idle(
            status=ConversationStatus.REPLIED,
            last_message_at=_ago(45),
            reminded_at=_ago(10),
            now=NOW,
            t1_minutes=30,
            t2_minutes=15,
        )
        == IdleAction.NOOP
    )


def test_resolve_after_remind_past_t2() -> None:
    assert (
        classify_idle(
            status=ConversationStatus.REPLIED,
            last_message_at=_ago(50),
            reminded_at=_ago(16),
            now=NOW,
            t1_minutes=30,
            t2_minutes=15,
        )
        == IdleAction.RESOLVE
    )


def test_customer_replied_after_remind_is_noop() -> None:
    # khách nhắn SAU khi đã nhắc (last_message_at > reminded_at) → thoát vòng đóng
    assert (
        classify_idle(
            status=ConversationStatus.REPLIED,
            last_message_at=_ago(2),
            reminded_at=_ago(16),
            now=NOW,
            t1_minutes=30,
            t2_minutes=15,
        )
        == IdleAction.NOOP
    )


def test_excluded_status_never_acts() -> None:
    for status in (
        ConversationStatus.IN_HUMAN_QUEUE,
        ConversationStatus.PENDING_APPROVAL,
        ConversationStatus.HUMAN_HANDLING,
        ConversationStatus.ACTIVE_AI,
    ):
        assert (
            classify_idle(
                status=status,
                last_message_at=_ago(999),
                reminded_at=None,
                now=NOW,
                t1_minutes=30,
                t2_minutes=15,
            )
            == IdleAction.NOOP
        )


def test_none_last_message_is_noop() -> None:
    assert (
        classify_idle(
            status=ConversationStatus.REPLIED,
            last_message_at=None,
            reminded_at=None,
            now=NOW,
            t1_minutes=30,
            t2_minutes=15,
        )
        == IdleAction.NOOP
    )
```

- [ ] **Step 2: Chạy test để xác nhận FAIL**

Run: `cd apps/backend && uv run pytest tests/test_auto_resolve.py -v`
Expected: FAIL — `ModuleNotFoundError: app.services.auto_resolve` / `ImportError`.

- [ ] **Step 3: Viết implementation tối thiểu**

Tạo `apps/backend/app/services/auto_resolve.py`:

```python
"""Auto-resolve (09c) — tự nhắc rồi đóng ca phía-AI im lặng quá ngưỡng.

Lõi `classify_idle` THUẦN (offline-testable): route trên trạng thái + hai mốc thời gian.
Sweep (I/O) thêm ở task sau. Chỉ REPLIED/AWAITING_CUSTOMER; các trạng thái khác NOOP.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from enum import StrEnum

from ..models.enums import ConversationStatus

# Trạng thái phía-AI, bên phải hành động là KHÁCH → im lặng = khách bỏ đi (spec §5, D5).
_SWEEPABLE = frozenset({ConversationStatus.REPLIED, ConversationStatus.AWAITING_CUSTOMER})


class IdleAction(StrEnum):
    NOOP = "noop"
    REMIND = "remind"
    RESOLVE = "resolve"


def classify_idle(
    *,
    status: str,
    last_message_at: datetime | None,
    reminded_at: datetime | None,
    now: datetime,
    t1_minutes: int,
    t2_minutes: int,
) -> IdleAction:
    """Quyết định cho MỘT ca. Tất định, không đọc gate/DB (call-site đã lọc gate ON).

    - status ngoài {REPLIED, AWAITING_CUSTOMER} → NOOP (chốt an toàn kép).
    - chưa nhắc & im lặng ≥ T1 → REMIND.
    - đã nhắc & khách chưa nhắn lại (last_message_at ≤ reminded_at) & quá T2 kể từ khi nhắc → RESOLVE.
    """
    if status not in _SWEEPABLE or last_message_at is None:
        return IdleAction.NOOP
    if reminded_at is None:
        if now - last_message_at >= timedelta(minutes=t1_minutes):
            return IdleAction.REMIND
        return IdleAction.NOOP
    # đã nhắc: khách nhắn lại sau khi nhắc → thoát vòng đóng
    if last_message_at > reminded_at:
        return IdleAction.NOOP
    if now - reminded_at >= timedelta(minutes=t2_minutes):
        return IdleAction.RESOLVE
    return IdleAction.NOOP
```

- [ ] **Step 4: Chạy test để xác nhận PASS**

Run: `cd apps/backend && uv run pytest tests/test_auto_resolve.py -v`
Expected: PASS (8 test).

- [ ] **Step 5: Commit**

```bash
git add apps/backend/app/services/auto_resolve.py apps/backend/tests/test_auto_resolve.py
git commit -m "feat(09c): classify_idle thuần cho auto-resolve (NOOP/REMIND/RESOLVE)"
```

---

### Task 2: Cột DB + migration

Thêm mốc `auto_resolve_reminded_at` trên `conversation` và ngưỡng T2 `auto_resolve_grace_minutes` trên `gate_config`.

**Files:**
- Modify: `apps/backend/app/models/conversation.py` (thêm cột sau `last_message_at`, dòng ~49-51)
- Modify: `apps/backend/app/models/gate_config.py` (thêm cột sau `auto_resolve_minutes`, dòng ~24)
- Create: `apps/backend/alembic/versions/<rev>_auto_resolve_cols.py`

**Interfaces:**
- Produces:
  - `Conversation.auto_resolve_reminded_at: Mapped[datetime | None]`
  - `GateConfig.auto_resolve_grace_minutes: Mapped[int]` (default 15)

- [ ] **Step 1: Thêm cột vào model `Conversation`**

Trong `apps/backend/app/models/conversation.py`, ngay sau khối `last_message_at` (dòng 49-51), thêm:

```python
    # Auto-resolve (09c): mốc đã gửi tin nhắc. NULL = chưa nhắc. Set khi REMIND, reset khi khách nhắn lại.
    auto_resolve_reminded_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
```

- [ ] **Step 2: Thêm cột vào model `GateConfig`**

Trong `apps/backend/app/models/gate_config.py`, sau dòng `auto_resolve_minutes` (dòng 24), thêm:

```python
    auto_resolve_grace_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=15)
```

- [ ] **Step 3: Sinh migration**

Run: `cd apps/backend && uv run alembic revision -m "auto_resolve cols"`
Sửa file `upgrade()`/`downgrade()` vừa sinh trong `apps/backend/alembic/versions/` thành:

```python
def upgrade() -> None:
    op.add_column(
        "conversation",
        sa.Column("auto_resolve_reminded_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "gate_config",
        sa.Column(
            "auto_resolve_grace_minutes", sa.Integer(), nullable=False, server_default="15"
        ),
    )


def downgrade() -> None:
    op.drop_column("gate_config", "auto_resolve_grace_minutes")
    op.drop_column("conversation", "auto_resolve_reminded_at")
```

Đặt `down_revision` = revision head hiện tại (kiểm tra bằng `uv run alembic heads`).

- [ ] **Step 4: Áp migration lên DB (LIVE)**

Run: `cd apps/backend && uv run alembic upgrade head`
Expected: chạy không lỗi; `uv run alembic current` trỏ revision mới.
Kiểm tra cột: kết nối DB, xác nhận `conversation.auto_resolve_reminded_at` và `gate_config.auto_resolve_grace_minutes` tồn tại.

- [ ] **Step 5: Commit**

```bash
git add apps/backend/app/models/conversation.py apps/backend/app/models/gate_config.py apps/backend/alembic/versions/
git commit -m "feat(09c): cột auto_resolve_reminded_at + auto_resolve_grace_minutes (migration)"
```

---

### Task 3: Config + gate snapshot/route mang T2 và sweep_interval

Đưa `auto_resolve_grace_minutes` xuyên qua `GateSnapshot`/`update_gate_config`/admin route, và thêm `sweep_interval_seconds` vào settings.

**Files:**
- Modify: `apps/backend/app/core/config.py:48-49` (thêm setting)
- Modify: `apps/backend/app/services/gate_service.py` (GateSnapshot field + _load_snapshot + update_gate_config)
- Modify: `apps/backend/app/api/routes/admin.py` (GateConfigOut/In + _gate_out + update route, quanh dòng 164-193)
- Modify: `apps/backend/tests/test_gate.py:13-19` (cập nhật `_snap` helper cho field mới)

**Interfaces:**
- Consumes: `GateSnapshot` (Task hiện tại mở rộng)
- Produces:
  - `GateSnapshot.auto_resolve_grace_minutes: int`
  - `settings.sweep_interval_seconds: int`
  - `update_gate_config(..., auto_resolve_grace_minutes: int | None = None)`

- [ ] **Step 1: Cập nhật `_snap` trong test_gate.py để phản ánh field mới (giữ test cũ xanh)**

Trong `apps/backend/tests/test_gate.py`, hàm `_snap` (dòng 13-19), thêm tham số + field:

```python
def _snap(
    *,
    auto_reply_enabled: bool = True,
    rules: list[GateIntentRuleView] | None = None,
) -> GateSnapshot:
    return GateSnapshot(
        auto_reply_enabled=auto_reply_enabled,
        auto_resolve_enabled=True,
        auto_resolve_minutes=30,
        auto_resolve_grace_minutes=15,
        rules=tuple(rules or ()),
    )
```

- [ ] **Step 2: Chạy test_gate để xác nhận FAIL**

Run: `cd apps/backend && uv run pytest tests/test_gate.py -v`
Expected: FAIL — `GateSnapshot.__init__() got an unexpected keyword argument 'auto_resolve_grace_minutes'` (frozen dataclass chưa có field).

- [ ] **Step 3: Thêm field vào `GateSnapshot` + đọc từ DB + cho update**

Trong `apps/backend/app/services/gate_service.py`:

`GateSnapshot` (sau `auto_resolve_minutes: int`):
```python
    auto_resolve_grace_minutes: int
```

`_load_snapshot` — khối `return GateSnapshot(...)`, thêm:
```python
        auto_resolve_grace_minutes=cfg.auto_resolve_grace_minutes,
```

`update_gate_config` — thêm tham số vào chữ ký:
```python
    auto_resolve_grace_minutes: int | None = None,
```
và trong khối cập nhật `cfg`:
```python
        if auto_resolve_grace_minutes is not None:
            cfg.auto_resolve_grace_minutes = auto_resolve_grace_minutes
```

- [ ] **Step 4: Chạy test_gate để xác nhận PASS**

Run: `cd apps/backend && uv run pytest tests/test_gate.py -v`
Expected: PASS.

- [ ] **Step 5: Thêm setting `sweep_interval_seconds`**

Trong `apps/backend/app/core/config.py`, cạnh `auto_resolve_minutes` (dòng 49), thêm:
```python
    sweep_interval_seconds: int = 60
```

- [ ] **Step 6: Đưa field mới ra admin API**

Trong `apps/backend/app/api/routes/admin.py`:
- Schema `GateConfigOut` và `GateConfigIn` (nơi khai báo `auto_resolve_minutes`): thêm `auto_resolve_grace_minutes: int` (Out) và `auto_resolve_grace_minutes: int | None = None` (In, giữ optional như các field khác của payload).
- `_gate_out` (dòng ~165): thêm `auto_resolve_grace_minutes=snap.auto_resolve_grace_minutes,`.
- Route update (dòng ~187): thêm `auto_resolve_grace_minutes=payload.auto_resolve_grace_minutes,`.

- [ ] **Step 7: Chạy toàn bộ test offline**

Run: `cd apps/backend && uv run pytest -q`
Expected: PASS toàn bộ (không hồi quy).

- [ ] **Step 8: Commit**

```bash
git add apps/backend/app/core/config.py apps/backend/app/services/gate_service.py apps/backend/app/api/routes/admin.py apps/backend/tests/test_gate.py
git commit -m "feat(09c): auto_resolve_grace_minutes qua gate snapshot/route + sweep_interval_seconds"
```

---

### Task 4: Helper phát tin không-reset đồng hồ + reset khi khách nhắn

Thêm cách persist tin hệ thống (`sender=ai`) **không** bump `last_message_at`, và reset `auto_resolve_reminded_at` khi khách gửi tin.

**Files:**
- Modify: `apps/backend/app/services/conversation_service.py` (`_append_message` dòng 21-34; `add_message` dòng 55-67; thêm `send_auto_message`)

**Interfaces:**
- Consumes: `Conversation`, `MessageSender`
- Produces:
  - `_append_message(..., bump_activity: bool = True)` — khi `False`, KHÔNG cập nhật `last_message_at`
  - `async def send_auto_message(session, conversation_id, *, content) -> Conversation | None` — persist `sender=ai`, không bump activity
  - `add_message`: khi `sender == customer` → set `conversation.auto_resolve_reminded_at = None`

- [ ] **Step 1: Cho `_append_message` tuỳ chọn không bump activity**

Trong `apps/backend/app/services/conversation_service.py`, sửa `_append_message` (dòng 21-34):

```python
def _append_message(
    conversation: Conversation,
    *,
    sender: str,
    content: str,
    intent: str | None = None,
    confidence: float | None = None,
    bump_activity: bool = True,
) -> Message:
    # Append qua relationship: vừa set FK vừa cập nhật collection trong bộ nhớ (back_populates).
    msg = Message(sender=sender, content=content, intent=intent, confidence=confidence)
    conversation.messages.append(msg)
    # Tin hệ thống auto-resolve (nhắc/đóng) KHÔNG được reset đồng hồ im-lặng của KHÁCH (bump_activity=False).
    if bump_activity:
        conversation.last_message_at = datetime.now(timezone.utc)
    return msg
```

- [ ] **Step 2: Reset reminded_at khi KHÁCH nhắn trong `add_message`**

Sửa `add_message` (dòng 55-67), sau `_append_message(...)`:

```python
async def add_message(
    session: AsyncSession,
    conversation_id: uuid.UUID,
    *,
    content: str,
    sender: str = MessageSender.CUSTOMER,
) -> Conversation | None:
    conversation = await get_conversation(session, conversation_id)  # selectinload messages
    if conversation is None:
        return None
    _append_message(conversation, sender=sender, content=content)
    # Khách nhắn lại → thoát vòng auto-resolve (09c): xoá mốc đã-nhắc.
    if sender == MessageSender.CUSTOMER:
        conversation.auto_resolve_reminded_at = None
    await session.commit()
    return await get_conversation(session, conversation_id)
```

- [ ] **Step 3: Thêm `send_auto_message`**

Thêm hàm mới (đặt gần `add_message`):

```python
async def send_auto_message(
    session: AsyncSession, conversation_id: uuid.UUID, *, content: str
) -> Conversation | None:
    """Persist tin hệ thống auto-resolve (sender=ai) KHÔNG bump last_message_at (09c).

    Đồng hồ im-lặng của khách phải giữ nguyên để grace/đóng đo đúng. Broadcast hub do call-site lo."""
    conversation = await get_conversation(session, conversation_id)
    if conversation is None:
        return None
    _append_message(conversation, sender=MessageSender.AI, content=content, bump_activity=False)
    await session.commit()
    return await get_conversation(session, conversation_id)
```

- [ ] **Step 4: Verify LIVE (DB)**

Chạy backend dev (:8000 do người dùng chạy sẵn, hoặc :8001 cho e2e). Bằng một script/psql nhỏ hoặc REPL:
- Tạo ca, `add_message(sender=customer)` → ghi nhận `last_message_at = t0`, `reminded_at = NULL`.
- `send_auto_message(...)` → có message `sender=ai`; `last_message_at` VẪN `t0` (không đổi).
- `add_message(sender=customer)` sau khi set `reminded_at` thủ công → `reminded_at` trở về `NULL`.
Expected: đúng cả ba.

- [ ] **Step 5: Commit**

```bash
git add apps/backend/app/services/conversation_service.py
git commit -m "feat(09c): send_auto_message (no bump activity) + reset reminded_at khi khách nhắn"
```

---

### Task 5: Sweep coroutine + wiring lifespan

Vòng quét thật: đọc gate, lọc ứng viên, với mỗi ca `classify_idle` → nhắc/đóng; chạy nền trong lifespan.

**Files:**
- Modify: `apps/backend/app/services/auto_resolve.py` (thêm `run_sweep_once`, `sweep_loop`, template + broadcast)
- Modify: `apps/backend/app/main.py` (lifespan: start/stop task)
- Test: `apps/backend/tests/test_auto_resolve.py` (thêm test guard gate-off, offline với fake)

**Interfaces:**
- Consumes: `classify_idle`, `IdleAction`, `gate_service.get_gate_config`, `conversation_service.send_auto_message`/`set_status`, `hub.publish`, `settings.sweep_interval_seconds`
- Produces:
  - `async def run_sweep_once(now: datetime) -> int` (trả số ca đã hành động)
  - `async def sweep_loop(stop: asyncio.Event) -> None`
  - `REMIND_TEMPLATE: str`, `RESOLVE_TEMPLATE: str`

- [ ] **Step 1: Thêm test guard gate-off (offline)**

Thêm vào `apps/backend/tests/test_auto_resolve.py`:

```python
import asyncio
from unittest.mock import AsyncMock, patch


def test_run_sweep_once_noop_when_gate_off() -> None:
    """Gate auto_resolve OFF → sweep không truy vấn ca, trả 0 (spec §6)."""

    class _Snap:
        auto_resolve_enabled = False
        auto_resolve_minutes = 30
        auto_resolve_grace_minutes = 15

    async def _run() -> int:
        with patch(
            "app.services.auto_resolve.gate_service.get_gate_config",
            new=AsyncMock(return_value=_Snap()),
        ):
            from app.services.auto_resolve import run_sweep_once

            return await run_sweep_once(NOW)

    assert asyncio.run(_run()) == 0
```

- [ ] **Step 2: Chạy test để xác nhận FAIL**

Run: `cd apps/backend && uv run pytest tests/test_auto_resolve.py::test_run_sweep_once_noop_when_gate_off -v`
Expected: FAIL — `run_sweep_once` chưa tồn tại.

- [ ] **Step 3: Implement sweep trong `auto_resolve.py`**

Thêm vào cuối `apps/backend/app/services/auto_resolve.py`:

```python
import asyncio
from datetime import timezone

from sqlalchemy import select

from ..api.ws.hub import hub
from ..core.config import settings
from ..core.database import AsyncSessionLocal
from ..core.logging import get_logger
from ..models.conversation import Conversation
from ..services import conversation_service, gate_service

log = get_logger("auto_resolve")

REMIND_TEMPLATE = (
    "Anh/chị còn cần em hỗ trợ thêm gì không ạ? "
    "Nếu không, em xin phép tạm đóng cuộc trò chuyện này ạ."
)
RESOLVE_TEMPLATE = (
    "Em xin phép tạm đóng cuộc trò chuyện. "
    "Anh/chị cần hỗ trợ thì nhắn lại bất cứ lúc nào ạ."
)


async def _broadcast_ai(conv_id, content: str) -> None:
    """Dội tin hệ thống lên hub (admin/khách đang mở thấy realtime). Guarded — hub lỗi KHÔNG chặn sweep."""
    try:
        await hub.publish(str(conv_id), {"type": "message", "from": "ai", "content": content})
    except Exception as exc:  # noqa: BLE001
        log.warning("auto-resolve broadcast failed (bỏ qua): %s", exc)


async def run_sweep_once(now: datetime) -> int:
    """Một vòng quét. Gate OFF → 0. Lọc thô status phía-AI, rồi classify_idle từng ca."""
    try:
        snap = await gate_service.get_gate_config()
    except Exception as exc:  # noqa: BLE001 — không đọc được gate → an toàn: không đóng gì.
        log.warning("auto-resolve read gate failed (skip vòng): %s", exc)
        return 0
    if not snap.auto_resolve_enabled:
        return 0

    acted = 0
    async with AsyncSessionLocal() as s:
        rows = list(
            (
                await s.execute(
                    select(Conversation).where(
                        Conversation.status.in_(tuple(_SWEEPABLE))
                    )
                )
            )
            .scalars()
            .all()
        )
        for conv in rows:
            action = classify_idle(
                status=conv.status,
                last_message_at=conv.last_message_at,
                reminded_at=conv.auto_resolve_reminded_at,
                now=now,
                t1_minutes=snap.auto_resolve_minutes,
                t2_minutes=snap.auto_resolve_grace_minutes,
            )
            if action is IdleAction.REMIND:
                conv.auto_resolve_reminded_at = now
                await s.commit()
                await conversation_service.send_auto_message(s, conv.id, content=REMIND_TEMPLATE)
                await _broadcast_ai(conv.id, REMIND_TEMPLATE)
                acted += 1
            elif action is IdleAction.RESOLVE:
                conv.status = ConversationStatus.RESOLVED
                await s.commit()
                await conversation_service.send_auto_message(s, conv.id, content=RESOLVE_TEMPLATE)
                await _broadcast_ai(conv.id, RESOLVE_TEMPLATE)
                acted += 1
    if acted:
        log.info("auto-resolve sweep: %d ca đã xử lý", acted)
    return acted


async def sweep_loop(stop: asyncio.Event) -> None:
    """Lặp mỗi sweep_interval_seconds tới khi stop set. Nuốt lỗi mỗi vòng (đừng để task chết)."""
    log.info("auto-resolve sweep loop bắt đầu (mỗi %ds)", settings.sweep_interval_seconds)
    while not stop.is_set():
        try:
            await run_sweep_once(datetime.now(timezone.utc))
        except Exception as exc:  # noqa: BLE001
            log.warning("auto-resolve sweep vòng lỗi (bỏ qua): %s", exc)
        try:
            await asyncio.wait_for(stop.wait(), timeout=settings.sweep_interval_seconds)
        except asyncio.TimeoutError:
            pass
    log.info("auto-resolve sweep loop dừng")
```

Lưu ý import: gộp `import asyncio` và `from datetime import ... timezone` lên đầu file cùng các import hiện có (tránh import giữa file). Giữ code sạch theo style repo.

- [ ] **Step 4: Chạy test guard để xác nhận PASS**

Run: `cd apps/backend && uv run pytest tests/test_auto_resolve.py -v`
Expected: PASS toàn bộ (9 test).

- [ ] **Step 5: Wire vào lifespan `main.py`**

Trong `apps/backend/app/main.py`, `lifespan`:

Thêm import đầu file: `import asyncio` và `from .services import auto_resolve`.

Trong `lifespan`, trước `yield`:
```python
    stop_sweep = asyncio.Event()
    sweep_task = asyncio.create_task(auto_resolve.sweep_loop(stop_sweep))
```
Sau `yield` (đầu khối teardown):
```python
    stop_sweep.set()
    sweep_task.cancel()
    try:
        await sweep_task
    except asyncio.CancelledError:
        pass
```

- [ ] **Step 6: Verify LIVE end-to-end**

Chạy backend (:8001 cho e2e). Đặt tạm ngưỡng nhỏ để test nhanh: qua admin gate API set `auto_resolve_minutes=1`, `auto_resolve_grace_minutes=1`, `auto_resolve_enabled=true`; `SWEEP_INTERVAL_SECONDS=10` trong env.
- Seed/tạo ca `REPLIED` với `last_message_at` cách đây >1 phút (chat một lượt AI, hoặc chỉnh DB) → chờ 1 vòng sweep → xác nhận có tin nhắc + `auto_resolve_reminded_at` set + status vẫn `REPLIED`.
- Chờ thêm >1 phút → xác nhận `status=RESOLVED` + tin đóng.
- Seed ca `IN_HUMAN_QUEUE` quá hạn → xác nhận KHÔNG đổi.
- Set `auto_resolve_enabled=false` → xác nhận sweep không đóng gì.
- Trong lúc chờ grace, khách nhắn lại (WS) → xác nhận `reminded_at` reset NULL, ca không bị đóng.

- [ ] **Step 7: Commit**

```bash
git add apps/backend/app/services/auto_resolve.py apps/backend/app/main.py apps/backend/tests/test_auto_resolve.py
git commit -m "feat(09c): sweep run_sweep_once + sweep_loop + wiring lifespan"
```

---

### Task 6: Ô cấu hình grace trên dashboard gate

Cho Admin nhập "phút chờ sau khi nhắc" (T2) trên trang gate.

**Files:**
- Modify: `apps/dashboard/app/admin/gate/page.tsx` (khối auto-resolve, quanh dòng 58-59, 135-137)
- Modify: `apps/dashboard/lib/api.ts` (type `GateConfig` — thêm `auto_resolve_grace_minutes`; nếu có type patch, thêm optional)
- Modify (nếu dùng): `packages/shared-types` gate type — đồng bộ field mới

**Interfaces:**
- Consumes: `GateConfig` từ `GET /api/admin/gate-config` (nay có `auto_resolve_grace_minutes`)
- Produces: mutation gửi `{ auto_resolve_grace_minutes: number }` tới `PUT/PATCH /api/admin/gate-config`

- [ ] **Step 1: Thêm field vào type `GateConfig`**

Trong `apps/dashboard/lib/api.ts`, type `GateConfig` (nơi có `auto_resolve_minutes: number`), thêm:
```typescript
  auto_resolve_grace_minutes: number;
```
Trong hàm `applyPatch` (dòng ~58-59), thêm dòng tương tự các field auto_resolve:
```typescript
  if (patch.auto_resolve_grace_minutes !== undefined) next.auto_resolve_grace_minutes = patch.auto_resolve_grace_minutes;
```

- [ ] **Step 2: Thêm ô nhập số phút grace vào UI**

Trong `apps/dashboard/app/admin/gate/page.tsx`, cạnh khối toggle auto-resolve (dòng ~135-137), thêm một input số (theo pattern các control Tailwind thuần sẵn có trong file), ví dụ:

```tsx
<div className="mt-2 flex items-center gap-2">
  <label className="text-sm text-gray-600">Phút chờ sau khi nhắc trước khi đóng</label>
  <input
    type="number"
    min={1}
    value={cfg.auto_resolve_grace_minutes}
    onChange={(e) =>
      mutation.mutate({ auto_resolve_grace_minutes: Number(e.target.value) })
    }
    className="w-20 rounded border px-2 py-1 text-sm"
  />
</div>
```

(Bám đúng class/spacing của các input khác trong file — KHÔNG thêm thư viện UI.)

- [ ] **Step 3: Verify LIVE (UI)**

Chạy dashboard (:3000 người dùng, hoặc :3001 e2e). Mở `/admin/gate`:
- Ô "phút chờ" hiển thị giá trị hiện tại (mặc định 15).
- Đổi giá trị → reload trang → giá trị được lưu (persist qua API).
- Backend `GET /api/admin/gate-config` trả `auto_resolve_grace_minutes` đúng.

- [ ] **Step 4: Commit**

```bash
git add apps/dashboard/app/admin/gate/page.tsx apps/dashboard/lib/api.ts packages/shared-types
git commit -m "feat(09c): ô cấu hình auto_resolve_grace_minutes trên trang gate"
```

---

## Self-Review

**Spec coverage:**
- §2 D1 periodic sweep → Task 5. D2 hai ngưỡng → Task 2 (cột) + Task 3 (config) + Task 1/5 (dùng). D3 Hướng A → ngưỡng cấu hình (Task 3/6), không kế thừa context (không có task nào làm — đúng). D4 template qua egress → Task 4 (send_auto_message) + Task 5 (broadcast). D5 chỉ REPLIED/AWAITING_CUSTOMER → Task 1 `_SWEEPABLE` + Task 5 SQL filter. D6 không gộp 09b → không có task.
- §3 state machine (không thêm status) → Task 1/5 dùng RESOLVED sẵn có. ✓
- §4 migration (2 cột) → Task 2. ✓
- §5.1 auto_resolve.py → Task 1 + 5. §5.2 conversation_service helpers → Task 4. §5.3 sole-egress broadcast → Task 5. §5.4 lifespan → Task 5. §5.5 config → Task 3. §5.6 gate/route/UI → Task 3 + 6. ✓
- §6 ranh giới → Task 1 (chốt kép), Task 5 (gate-off guard). ✓
- §7 test offline (classify_idle) → Task 1; gate-off → Task 5; live e2e → Task 5 Step 6. ✓
- §8 ngoài phạm vi → không task nào chạm. ✓

**Placeholder scan:** không có TBD/TODO; mọi step code có nội dung thật.

**Type consistency:** `classify_idle` chữ ký nhất quán Task 1↔5; `IdleAction` (NOOP/REMIND/RESOLVE) nhất quán; `send_auto_message(session, conversation_id, *, content)` nhất quán Task 4↔5; `auto_resolve_grace_minutes` nhất quán model/snapshot/route/UI; `auto_resolve_reminded_at` nhất quán model/service/sweep.

**Rủi ro đã lường:** `_SWEEPABLE` là `frozenset` của `ConversationStatus` (StrEnum) — `Conversation.status.in_(tuple(_SWEEPABLE))` so khớp giá trị chuỗi (cột `status` là String) ✓. Circular import: `auto_resolve` import `api.ws.hub` + `services.conversation_service`; đặt import trong module-level cuối file/đầu file, nếu gặp vòng thì chuyển `hub`/`conversation_service` sang import trong hàm (ghi rõ ở Task 5 Step 3 nếu cần).
