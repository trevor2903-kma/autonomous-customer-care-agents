# Thiết kế: Auto-resolve hội thoại theo thời gian im lặng (một phần slice 09c)

- **Ngày:** 2026-08-28
- **Trạng thái:** Đã duyệt hướng thiết kế, chờ review spec → lập plan
- **Nguồn chân lý:** PRD §9 (gate auto-resolve), §10 (async), §15 (state machine), ROADMAP 09c
- **Phạm vi:** CHỈ tính năng tự đóng ca do khách im lặng. KHÔNG gộp 09b (durable checkpointer / `thread_id` ổn định), KHÔNG gộp offline-handling FR-ASYNC-4.

---

## 1. Vấn đề & mục tiêu

Vòng đời hội thoại (PRD §15) chưa khép kín: ca ở `REPLIED`/`AWAITING_CUSTOMER` mà khách bỏ đi sẽ nằm mở vô hạn → hàng đợi admin phình, KPI báo cáo nhiễu, khách không có tín hiệu đóng.

**Mục tiêu:** một tiến trình nền tự động, sau khi khách im lặng đủ lâu, **nhắc một lần** rồi **đóng ca** (`RESOLVED`) — chỉ với các ca đang ở phía AI, tôn trọng gate `auto-resolve` của Admin.

**Tiêu chí thành công (kiểm chứng được):**
- Ca `REPLIED`/`AWAITING_CUSTOMER` im lặng ≥ T1 (khi gate ON) → nhận **đúng 1** tin nhắc, `auto_resolve_reminded_at` được set.
- Ca đã nhắc, im lặng thêm ≥ T2 → chuyển `RESOLVED`.
- Khách trả lời bất kỳ lúc nào → thoát tiến trình đóng, `auto_resolve_reminded_at` reset về NULL.
- Ca `IN_HUMAN_QUEUE` / `PENDING_APPROVAL` / `HUMAN_HANDLING` / các trạng thái đang trong pipeline → **không bao giờ** bị đụng (FR-ASYNC-4).
- Gate `auto_resolve_enabled=false` → sweep no-op hoàn toàn.
- `make test` vẫn OFFLINE-xanh (logic quyết định thuần, không I/O).

---

## 2. Quyết định thiết kế đã chốt

| # | Quyết định | Lý do |
|---|---|---|
| D1 | **Periodic sweep** trên Postgres (asyncio task trong FastAPI lifespan), KHÔNG polling Redis | 1 worker; bền vững qua restart (state ở DB); không đụng free-tier Upstash (NFR-9) |
| D2 | Hai ngưỡng: **T1 = `auto_resolve_minutes`** (im lặng→nhắc), **T2 = `auto_resolve_grace_minutes`** (nhắc→đóng, cột MỚI) | Khách "bận một lát" có cơ hội quay lại sau khi được nhắc — Hướng A chống mất context |
| D3 | **Hướng A** cho vấn đề mất ngữ cảnh: đặt ngưỡng đủ dài, KHÔNG kế thừa bộ nhớ xuyên ca | Giữ bất biến "bộ nhớ agent theo ca" (§1); auto-resolve chỉ dọn ca **đã bỏ hẳn** |
| D4 | Tin nhắc + tin đóng là **template cố định**, KHÔNG gọi LLM; phát qua **đúng đường của pipeline** (persist message sender=`ai` + `hub.publish`) | Tôn trọng sole-egress; nhẹ; giống cách `HANDOFF_NOTICE` đi |
| D5 | Chỉ auto-resolve trạng thái **`REPLIED`** và **`AWAITING_CUSTOMER`** | Đây là các trạng thái mà bên phải hành động là KHÁCH; im lặng = khách bỏ đi |
| D6 | KHÔNG gộp 09b (checkpointer/thread_id) | Auto-resolve chỉ đọc `last_message_at` + đổi `status`, không cần checkpointer; tách scope |

---

## 3. Máy trạng thái (bổ sung PRD §15, không thêm status mới)

```
REPLIED / AWAITING_CUSTOMER  (khách im lặng, đồng hồ = last_message_at)
   │
   │  gate auto_resolve ON · reminded_at IS NULL · now - last_message_at ≥ T1
   ▼
[GỬI TIN NHẮC]  → set auto_resolve_reminded_at = now   (status GIỮ NGUYÊN)
   │
   │  reminded_at IS NOT NULL · không có tin khách sau reminded_at · now - reminded_at ≥ T2
   ▼
RESOLVED  (+ tuỳ chọn: 1 tin thông báo đã tạm đóng)

Bất kỳ lúc nào khách gửi tin  →  last_message_at cập nhật + reminded_at = NULL  →  thoát vòng đóng
```

**Không thêm `ConversationStatus` mới** — chỉ thêm một cột mốc thời gian. Đây là bất biến: enum canonical PRD §15 không đổi.

---

## 4. Thay đổi dữ liệu (Alembic migration)

### 4.1 `conversation`
- **+ `auto_resolve_reminded_at`** `TIMESTAMP WITH TIME ZONE NULL` — mốc đã gửi tin nhắc. NULL = chưa nhắc.

### 4.2 `gate_config`
- **+ `auto_resolve_grace_minutes`** `INTEGER NOT NULL DEFAULT 15` — T2, thời gian chờ sau khi nhắc trước khi đóng.

(`auto_resolve_minutes` và `auto_resolve_enabled` đã có sẵn — tái dùng làm T1 và cờ bật/tắt.)

---

## 5. Thành phần & giao diện

### 5.1 `services/auto_resolve.py` (MỚI) — lõi tất định + sweep

**Hàm thuần (offline-testable), KHÔNG I/O:**

```python
class IdleAction(StrEnum):
    NOOP = "noop"
    REMIND = "remind"
    RESOLVE = "resolve"

def classify_idle(
    *, status: str, last_message_at: datetime | None,
    reminded_at: datetime | None, now: datetime,
    t1_minutes: int, t2_minutes: int,
) -> IdleAction:
    """Quyết định cho MỘT ca. Tất định, không đọc gate/DB (call-site đã lọc gate ON)."""
```

Luật:
- `status` ∉ {REPLIED, AWAITING_CUSTOMER} → `NOOP` (chốt an toàn kép, dù SQL đã lọc).
- `last_message_at` là None → `NOOP`.
- `reminded_at` is None và `now - last_message_at ≥ T1` → `REMIND`.
- `reminded_at` not None và `last_message_at ≤ reminded_at` và `now - reminded_at ≥ T2` → `RESOLVE`.
- còn lại → `NOOP`.

**Coroutine sweep (I/O, guarded):**

```python
async def run_sweep_once(now: datetime) -> SweepResult:
    """1 vòng: đọc gate (nếu OFF → no-op); 1 query lọc ứng viên; với mỗi ca classify → remind/resolve."""

async def sweep_loop(stop: asyncio.Event) -> None:
    """Lặp: run_sweep_once(now) rồi asyncio.wait(stop, timeout=sweep_interval_seconds). Nuốt lỗi mỗi vòng."""
```

- Query ứng viên: `status IN ('REPLIED','AWAITING_CUSTOMER') AND last_message_at < now - (min(T1,T2 tính từ reminded) )`. Thực dụng: lọc thô `status IN (...)` + `last_message_at < now - T1_seconds OR auto_resolve_reminded_at IS NOT NULL`, rồi `classify_idle` quyết định từng ca (tránh nhồi hết logic vào SQL).
- `now` **truyền vào** (không gọi `datetime.now()` bên trong hàm thuần) để test tất định.

### 5.2 `services/conversation_service.py` — 2 helper nhỏ
- **`send_auto_message(session, conv_id, content)`** — persist message `sender=ai` **KHÔNG bump `last_message_at`** (để đồng hồ im-lặng của khách không bị reset bởi tin của hệ thống). Tách khỏi `_append_message` bằng cờ `bump_activity: bool = True`.
- **`mark_reminded` / `resolve_by_auto`** — set `auto_resolve_reminded_at` / đổi `status=RESOLVED`. (Có thể tái dùng `set_status`.)
- **Reset khi khách nhắn:** trong `add_message`, khi `sender=customer` → set `auto_resolve_reminded_at = NULL`. (Đây là điểm "khách quay lại thì thoát vòng đóng".)

### 5.3 Phát tin (sole-egress)
Sweep gọi `send_auto_message` (persist) **và** `hub.publish(conv_key, {"type":"message","from":"ai","content": <template>})`. Khách còn kết nối → `_hub_listener` đẩy xuống socket; khách offline → nhận qua `GET /me/thread` khi quay lại. Admin đang mở ca → thấy realtime. Không mở đường gửi mới.

Template (cấu hình được sau; hardcode tiếng Việt lịch sự ở phase này):
- Nhắc: *"Anh/chị còn cần em hỗ trợ thêm gì không ạ? Nếu không, em xin phép tạm đóng cuộc trò chuyện này ạ."*
- (Tuỳ chọn) Đóng: *"Em xin phép tạm đóng cuộc trò chuyện. Anh/chị cần hỗ trợ thì nhắn lại bất cứ lúc nào ạ."*

### 5.4 `main.py` lifespan
- Khởi động: tạo `stop = asyncio.Event()`, `task = asyncio.create_task(auto_resolve.sweep_loop(stop))`.
- Tắt: `stop.set()`, `await task` (có timeout/shield nhẹ). Guarded — lỗi sweep KHÔNG làm sập app.

### 5.5 `core/config.py`
- **+ `sweep_interval_seconds: int = 60`** (env-configurable, NFR-10).

### 5.6 `gate_service.py` + admin route + dashboard gate UI
- `GateSnapshot` + `_load_snapshot` + `update_gate_config`: thêm `auto_resolve_grace_minutes`.
- Route admin gate: nhận `auto_resolve_grace_minutes`.
- UI gate (`admin/gate`): thêm ô nhập "phút chờ sau khi nhắc".
- `shared-types`: đồng bộ field mới (nếu type gate được share).

---

## 6. Ranh giới an toàn (bất biến)

- **KHÔNG** auto-resolve `IN_HUMAN_QUEUE`, `PENDING_APPROVAL`, `HUMAN_HANDLING`, `NEW/CLASSIFYING/RETRIEVING/DECIDING/RESPONDING/ACTIVE_AI` — SQL lọc + `classify_idle` chốt lần hai.
- **KHÔNG** gọi LLM trong sweep.
- **KHÔNG** đụng Redis pub/sub đa-worker (hub in-process, 1 worker — như hiện tại).
- **KHÔNG** thêm status mới vào PRD §15.
- Gate OFF → no-op tuyệt đối.

---

## 7. Kiểm thử

**Offline (`make test`, không I/O) — `tests/test_auto_resolve.py`:**
- `classify_idle` mọi nhánh: chưa tới T1 → NOOP; ≥T1 chưa nhắc → REMIND; đã nhắc chưa tới T2 → NOOP; đã nhắc ≥T2 → RESOLVE; khách nhắn sau reminded (`last_message_at > reminded_at`) → NOOP; status bị loại trừ → NOOP; `last_message_at=None` → NOOP.

**Live/DB (e2e, KB đã nạp):**
- Seed ca `REPLIED` với `last_message_at` quá hạn T1 → `run_sweep_once` → assert có message nhắc + `reminded_at` set + status vẫn REPLIED.
- Đẩy thời gian qua T2 → `run_sweep_once` → assert `status=RESOLVED`.
- Seed ca `IN_HUMAN_QUEUE` quá hạn → assert KHÔNG đổi.
- Gate `auto_resolve_enabled=false` → assert no-op.
- Khách gửi tin sau khi đã nhắc → assert `reminded_at` reset NULL, không bị đóng.

---

## 8. Ngoài phạm vi (ghi rõ để không trôi)

- 09b: durable checkpointer + `thread_id` ổn định.
- FR-ASYNC-4: offline/ngoài giờ, "nhân viên sẽ phản hồi sớm" cho ca chờ người.
- Kế thừa/tóm tắt ngữ cảnh xuyên ca (Hướng B/C đã loại).
- Redis pub/sub đa-worker.
- Template tin nhắc cấu hình được qua UI (phase này hardcode).
