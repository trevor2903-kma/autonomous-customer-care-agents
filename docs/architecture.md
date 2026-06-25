# Kiến trúc (tóm tắt) — Autonomous Customer Support System

> Đây là **tóm tắt kỹ thuật**. Nguồn chân lý nghiệp vụ là **[`../PRD.md`](../PRD.md)**. Khi mâu thuẫn → PRD đúng.
> Trạng thái hiện tại: **SCAFFOLD** (khung chạy được; node agent là stub; UI placeholder; KHÔNG logic thật).

## 1. Bốn trụ cột (PRD §5)

1. **Luồng cố định để dự đoán & kiểm toán** — `intent → knowledge → decision → response` + `human_handoff`
   có điều kiện; **KHÔNG Supervisor**. Thứ tự/nhánh do graph quy định trước.
2. **Tự trị CÓ GIỚI HẠN ở tầng agent** — node tự chọn tool (phase sau), bị giới hạn bước. Điều phối cố định.
3. **An toàn trước case lạ** — mỗi agent trả `confidence` + `uncertainty_flags`; dưới ngưỡng / không tri thức
   → `human_handoff` (KHÔNG bịa — grounding).
4. **Cải thiện dần có người duyệt** — phát hiện mẫu từ `audit_log` → *đề xuất*; Admin duyệt mới áp dụng (phase sau).

## 2. Pipeline (PRD §7–§8)

```
intent (Intent Classifier) → knowledge (Knowledge Agent/RAG) → decision (Decision Engine)
   └─ should_handoff? ─┬─ response (Response Generator)  → REPLIED        # nhánh tự động
                       └─ human_handoff (EscalationCard) → IN_HUMAN_QUEUE  # chuyển người
```

- **Decision Engine** = node ra quyết định (auto_reply | human_handoff). Quy tắc an toàn bất biến: có
  `uncertainty_flag` bất kỳ hoặc `confidence < ngưỡng` → human_handoff (độc lập gate §9).
- **Response Generator** = **điểm phát ngôn DUY NHẤT** tới khách (PRD §7.4). Không gửi tin cho khách rải rác ở node khác.
- Code: [`apps/backend/app/agents/`](../apps/backend/app/agents/) — `state.py`, `nodes/`, `policy.py`, `graph.py`.

## 3. Trạng thái hội thoại (PRD §15)

Tập canonical dùng chung backend (`app/models/enums.py`) + shared-types (`ConversationStatus`) + dashboard:
`NEW · ACTIVE_AI · CLASSIFYING · RETRIEVING · DECIDING · RESPONDING · REPLIED · AWAITING_CUSTOMER ·
PENDING_APPROVAL · IN_HUMAN_QUEUE · HUMAN_HANDLING · RESOLVED · CLOSED`.

## 4. Thành phần & hạ tầng (PRD §6, §21)

| Thành phần | Vai trò | Code |
| --- | --- | --- |
| Backend (FastAPI + LangGraph) | API + WebSocket + pipeline | [`apps/backend`](../apps/backend) |
| Web (Next.js) | Admin dashboard `/` + cổng chat khách `/chat` | [`apps/dashboard`](../apps/dashboard) |
| Mobile (Expo) | Admin xử lý nhanh (trạng thái backend) | [`apps/mobile`](../apps/mobile) |
| shared-types | type dùng chung (ConversationStatus, Conversation, AgentTraceStep, HealthStatus) | [`packages/shared-types`](../packages/shared-types) |
| Neon (Postgres) | hội thoại/tin nhắn/audit | `app/models`, `alembic/` |
| Upstash (Redis) | session ngắn hạn + **pub/sub** realtime (pub/sub: TODO) | `app/core/redis_client.py` |
| Qdrant Cloud | vector DB cho RAG (embed/truy hồi: phase sau) | `app/core/qdrant_client.py` |

## 5. Xử lý bất đồng bộ & realtime (PRD §10)

- Đường nhanh mỗi tin nhắn (P95 ≤ 5s) — FastAPI **BackgroundTasks** (KHÔNG worker polling Redis).
  Code: [`app/tasks/background.py`](../apps/backend/app/tasks/background.py) — ghi `audit_log` mỗi bước (FR-PIPE-4).
- Realtime: **WebSocket + Redis pub/sub** (event-driven, KHÔNG polling). Scaffold: WebSocket **echo**; pub/sub là TODO.
- human_handoff = tạm dừng AI cho hội thoại (LangGraph `interrupt` + checkpointer) — **TODO** (scaffold dùng `MemorySaver`).

## 6. Ranh giới scaffold (TODO trỏ PRD)

Chưa làm (chỉ chừa chỗ): LLM trong pipeline (`ENABLE_LLM=false`) · intent thật · RAG embed/truy hồi · logic
gate (§9) · human_handoff định tuyến/EscalationCard đầy đủ (§11) · suspend/resume (§10) · wiring AI↔WebSocket ·
Redis pub/sub · vòng học (§5 trụ cột 4). Xem `# TODO (PRD …)` trong code.
