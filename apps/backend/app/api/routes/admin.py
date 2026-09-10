"""Routes admin (HITL 08b/08c/08a) — hàng đợi escalation, xem hội thoại, hành động HITL cho màn admin.

Mọi hành động đổi trạng thái (takeover/resolve/approve/reject) theo BẢNG CHUYỂN `transition_conflict` (contract
§5, PRD §15) rồi ghi bằng CAS `conversation_service.transition_status` trên chính status vừa đọc (audit v2, FE-03 /
GRAPH-02): chuyển không hợp lệ, ca do admin KHÁC giữ, hoặc status đổi dưới chân → 409 (FE tải lại ca). Mỗi hành
động ghi đúng MỘT dòng `audit_log` (node "admin") CÙNG transaction với hành động (DATA-01.1); realtime (hub) chỉ
phát SAU commit.
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_session
from ...core.logging import get_logger
from ...models import User
from ...models.enums import ConversationStatus, MessageSender
from ...schemas.admin import (
    AdminConversationOut,
    ApproveRequest,
    ConversationListItem,
    EscalationOut,
    RejectRequest,
)
from ...schemas.gate import GateConfigOut, GateConfigUpdate, GateIntentRuleSchema
from ...services import audit_service, conversation_service, escalation_service, gate_service
from ..deps import require_admin
from ..ws.hub import hub

# Mọi route /api/admin/* yêu cầu admin đã đăng nhập (slice 11): thiếu token → 401, sai role → 403.
router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])
log = get_logger("admin")

# Hàng đợi = ca đang chờ người: escalate (IN_HUMAN_QUEUE) + chờ duyệt nháp (PENDING_APPROVAL, slice 08a).
_QUEUE_STATUSES = [ConversationStatus.IN_HUMAN_QUEUE, ConversationStatus.PENDING_APPROVAL]

# Ca "còn mở" — takeover/resolve chỉ đi từ đây (contract §5).
_OPEN_STATUSES = frozenset(ConversationStatus) - {ConversationStatus.RESOLVED, ConversationStatus.CLOSED}

# Lý do 409 (ngắn, tiếng Việt — FE hiện thẳng rồi tải lại ca).
CONFLICT_NOT_PENDING = "Nháp không còn chờ duyệt — ca đã được xử lý hoặc đã đổi trạng thái."
CONFLICT_HELD = "Ca đang do nhân viên khác xử lý."
CONFLICT_CLOSED = "Ca đã đóng."
CONFLICT_CHANGED = "Trạng thái ca vừa thay đổi — hãy tải lại."
CONFLICT_STALE_DRAFT = "Nháp đã đổi (khách vừa nhắn thêm) — hãy tải lại để xem nháp mới."


def transition_conflict(
    action: str, status: str | None, holder: uuid.UUID | None, admin_id: uuid.UUID
) -> str | None:
    """Bảng chuyển trạng thái của hành động admin. None = hợp lệ; ngược lại = lý do 409. Hàm THUẦN.

    - approve: PENDING_APPROVAL → REPLIED · reject: PENDING_APPROVAL → IN_HUMAN_QUEUE.
    - takeover: ca còn mở → HUMAN_HANDLING · resolve: ca còn mở → RESOLVED — TRỪ ca HUMAN_HANDLING do admin KHÁC
      giữ (chính admin đó tiếp quản lại = thành công, idempotent).
    """
    if action in ("approve", "reject"):
        return None if status == ConversationStatus.PENDING_APPROVAL else CONFLICT_NOT_PENDING
    if status not in _OPEN_STATUSES:
        return CONFLICT_CLOSED
    if status == ConversationStatus.HUMAN_HANDLING and holder is not None and holder != admin_id:
        return CONFLICT_HELD
    return None


async def _state_or_404(
    session: AsyncSession, conversation_id: uuid.UUID
) -> tuple[str, uuid.UUID | None]:
    state = await conversation_service.get_status_and_admin(session, conversation_id)
    if state is None:
        raise HTTPException(status_code=404, detail="conversation not found")
    return state


async def _transition(
    session: AsyncSession,
    conversation_id: uuid.UUID,
    admin_id: uuid.UUID,
    *,
    action: str,
    to: str,
    state: tuple[str, uuid.UUID | None],
    assign: bool = False,
    audit_extra: dict[str, Any] | None = None,
    expected_draft: str | None = None,
) -> None:
    """Bảng chuyển + CAS trên status VỪA ĐỌC + dòng audit, trong transaction của caller (caller commit).

    Không hợp lệ / thua CAS (status — hoặc nháp `expected_draft` — đổi giữa lúc đọc và ghi) → 409; ca biến mất giữa
    chừng → 404. Detail audit chỉ có id + status (+ cờ) — KHÔNG chép nội dung tin/nháp.
    """
    from_status, holder = state
    conflict = transition_conflict(action, from_status, holder, admin_id)
    if conflict is None:
        ok = await conversation_service.transition_status(
            session,
            conversation_id,
            to=to,
            allowed_from=(from_status,),
            assigned_admin_id=admin_id if assign else None,
            not_held_by_other_than=admin_id,
            expected_draft=expected_draft,
        )
        if ok:
            await audit_service.write_audit(
                session,
                conversation_id=conversation_id,
                node=audit_service.ADMIN_NODE,
                action=action,
                detail={
                    "admin_id": str(admin_id),
                    "from_status": str(from_status),
                    "to_status": str(to),
                    **(audit_extra or {}),
                },
            )
            return
        await session.rollback()
        if await conversation_service.get_status_and_admin(session, conversation_id) is None:
            raise HTTPException(status_code=404, detail="conversation not found")
        conflict = CONFLICT_CHANGED
    raise HTTPException(status_code=409, detail=conflict)


@router.get("/escalations", response_model=list[EscalationOut])
async def get_escalations(session: AsyncSession = Depends(get_session)) -> list[EscalationOut]:
    """Hàng đợi escalation, sắp priority cao → thấp rồi mới nhất (PRD §11/§17)."""
    convs = await escalation_service.list_escalations(session, _QUEUE_STATUSES)
    return [
        EscalationOut(
            conversation_id=c.id,
            customer_identifier=c.customer_identifier,
            status=c.status,
            priority=c.priority,
            severity=c.severity,
            escalation_reason=c.escalation_reason,
            escalation_card=c.escalation_card,
            last_message_at=c.last_message_at,
        )
        for c in convs
    ]


def _preview(messages: list) -> str | None:  # type: ignore[type-arg]
    """Tin KHÁCH gần nhất (fallback: tin cuối) — xem `get_conversations`."""
    for m in reversed(messages):
        if m.sender == MessageSender.CUSTOMER:
            return m.content
    return messages[-1].content if messages else None


@router.get("/conversations", response_model=list[ConversationListItem])
async def get_conversations(
    status: list[str] | None = Query(default=None, description="lọc theo status; lặp lại để lọc nhiều"),
    limit: int = Query(default=50, le=200),
    session: AsyncSession = Depends(get_session),
) -> list[ConversationListItem]:
    """Danh sách TẤT CẢ hội thoại (10a) + lọc theo nhóm status.

    `preview` ưu tiên tin KHÁCH gần nhất: tin cuối của ca escalate luôn là câu thông báo chuyển người giống
    hệt nhau → danh sách không đọc được. Câu hỏi của khách mới là thứ admin cần để phân loại.
    """
    convs = await conversation_service.list_conversations(session, statuses=status, limit=limit)
    return [
        ConversationListItem(
            id=c.id,
            customer_identifier=c.customer_identifier,
            status=c.status,
            # current_intent chưa được pipeline ghi xuống conversation → lấy tạm từ card của ca đã escalate.
            current_intent=c.current_intent or (c.escalation_card or {}).get("intent"),
            last_message_at=c.last_message_at,
            preview=_preview(c.messages),
        )
        for c in convs
    ]


@router.get("/conversations/{conversation_id}", response_model=AdminConversationOut)
async def get_admin_conversation(
    conversation_id: uuid.UUID, session: AsyncSession = Depends(get_session)
) -> AdminConversationOut:
    """Hội thoại đầy đủ (messages + EscalationCard) cho màn admin tiếp quản/duyệt nháp."""
    conv = await conversation_service.get_conversation(session, conversation_id)
    if conv is None:
        raise HTTPException(status_code=404, detail="conversation not found")
    return conv


@router.post("/conversations/{conversation_id}/takeover", response_model=AdminConversationOut)
async def takeover_conversation(
    conversation_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    admin: User = Depends(require_admin),
) -> AdminConversationOut:
    """Tiếp quản TƯỜNG MINH (fix 08c): chỉ đổi status khi admin BẤM NÚT — gán admin ĐÃ ĐĂNG NHẬP.

    Mở hội thoại để xem KHÔNG còn đổi status — ca escalate vẫn nằm trong hàng đợi cho tới khi có người nhận.
    Status + người giữ ghi trong CÙNG câu UPDATE có điều kiện: ca đã đóng / đang do admin KHÁC giữ → 409 (không
    cướp ca âm thầm — GRAPH-02.4); chính admin đó bấm lại → 200.
    """
    state = await _state_or_404(session, conversation_id)
    await _transition(
        session,
        conversation_id,
        admin.id,
        action="takeover",
        to=ConversationStatus.HUMAN_HANDLING,
        state=state,
        assign=True,
    )
    await session.commit()
    if state != (ConversationStatus.HUMAN_HANDLING, admin.id):
        await hub.notify_status(
            conversation_id, status=ConversationStatus.HUMAN_HANDLING, assigned_admin_id=admin.id
        )
    return await conversation_service.get_conversation(session, conversation_id)


@router.post("/conversations/{conversation_id}/resolve", response_model=AdminConversationOut)
async def resolve_conversation(
    conversation_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    admin: User = Depends(require_admin),
) -> AdminConversationOut:
    """Đóng ca sau khi admin xử lý xong → status RESOLVED (08c). Ca đã đóng / do admin KHÁC giữ → 409.

    Phát frame `status` sau commit → khách rời trạng thái "đang chờ"/"đang kiểm tra" ngay (UX-02.3)."""
    state = await _state_or_404(session, conversation_id)
    await _transition(
        session, conversation_id, admin.id, action="resolve", to=ConversationStatus.RESOLVED, state=state
    )
    await session.commit()
    await hub.notify_status(conversation_id, status=ConversationStatus.RESOLVED, assigned_admin_id=state[1])
    return await conversation_service.get_conversation(session, conversation_id)


@router.post("/conversations/{conversation_id}/approve", response_model=AdminConversationOut)
async def approve_draft(
    conversation_id: uuid.UUID,
    payload: ApproveRequest,
    session: AsyncSession = Depends(get_session),
    admin: User = Depends(require_admin),
) -> AdminConversationOut:
    """Duyệt nháp (08a): gửi nháp (đã duyệt/sửa) tới khách qua hub + lưu (sender=AI) + status REPLIED.
    Bỏ trống `content` → dùng `suggested_reply` trong EscalationCard.

    MỘT transaction: CAS PENDING_APPROVAL → REPLIED + chèn tin AI + dòng audit; commit rồi MỚI phát (FE-03.1). Ca
    không còn PENDING_APPROVAL (đã duyệt / đã từ chối / đã đóng / đang có người tiếp quản) → 409: không lưu, không
    gửi — hết gửi trùng, hết gửi nháp đã bị từ chối, hết hồi sinh ca đã đóng.
    """
    conv = await conversation_service.get_conversation(session, conversation_id)
    if conv is None:
        raise HTTPException(status_code=404, detail="conversation not found")
    draft = (conv.escalation_card or {}).get("suggested_reply") or ""
    content = (payload.content or "").strip() or draft
    if not content:
        raise HTTPException(status_code=400, detail="no draft to send")
    # ABA (FE-03.2): PENDING(D1) → REPLIED → PENDING(D2) vẫn qua bảng chuyển — nháp màn admin đã xem phải là nháp
    # HIỆN TẠI: kiểm ở đây (lý do rõ) và lại trong CAS (không đua giữa lúc đọc và lúc ghi).
    expected = payload.expected_draft or None
    if expected is not None and expected != draft:
        raise HTTPException(status_code=409, detail=CONFLICT_STALE_DRAFT)
    holder = conv.assigned_admin_id
    await _transition(
        session,
        conversation_id,
        admin.id,
        action="approve",
        to=ConversationStatus.REPLIED,
        state=(conv.status, holder),
        audit_extra={"edited": content.strip() != draft.strip()},
        expected_draft=expected,
    )
    message = await conversation_service.insert_message(
        session, conversation_id, sender=MessageSender.AI, content=content
    )
    await session.commit()
    # Nháp đã duyệt → khách nhận realtime (hub). Egress này do ADMIN kích hoạt (duyệt) — vẫn là câu của shop/AI.
    await hub.notify_message(conversation_id, sender=MessageSender.AI, content=content, message_id=message.id)
    await hub.notify_status(conversation_id, status=ConversationStatus.REPLIED, assigned_admin_id=holder)
    return await conversation_service.get_conversation(session, conversation_id)


@router.post("/conversations/{conversation_id}/reject", response_model=AdminConversationOut)
async def reject_draft(
    conversation_id: uuid.UUID,
    payload: RejectRequest | None = None,
    session: AsyncSession = Depends(get_session),
    admin: User = Depends(require_admin),
) -> AdminConversationOut:
    """Từ chối nháp (08a) → IN_HUMAN_QUEUE (admin tự tiếp quản xử lý). Chỉ từ PENDING_APPROVAL — không kéo ngược
    ca đang có người xử lý về hàng đợi (FE-03.3) → 409. Có `expected_draft` mà card đã sang nháp mới (ABA) → 409."""
    state = await _state_or_404(session, conversation_id)
    await _transition(
        session,
        conversation_id,
        admin.id,
        action="reject",
        to=ConversationStatus.IN_HUMAN_QUEUE,
        state=state,
        expected_draft=(payload.expected_draft if payload else None) or None,
    )
    await session.commit()
    await hub.notify_status(conversation_id, status=ConversationStatus.IN_HUMAN_QUEUE, assigned_admin_id=state[1])
    return await conversation_service.get_conversation(session, conversation_id)


# ── Gate động (P3) — cấu hình toggle hệ thống + per-intent (đọc/ghi DB) ────────
def _gate_out(snap: gate_service.GateSnapshot) -> GateConfigOut:
    return GateConfigOut(
        auto_reply_enabled=snap.auto_reply_enabled,
        auto_resolve_enabled=snap.auto_resolve_enabled,
        auto_resolve_minutes=snap.auto_resolve_minutes,
        auto_resolve_grace_minutes=snap.auto_resolve_grace_minutes,
        rules=[
            GateIntentRuleSchema(
                intent=r.intent, label=r.label, sensitive=r.sensitive, send_directly=r.send_directly
            )
            for r in snap.rules
        ],
    )


@router.get("/gate-config", response_model=GateConfigOut)
async def get_gate_config() -> GateConfigOut:
    """Cấu hình gate hiện tại (2 toggle + bảng per-intent)."""
    return _gate_out(await gate_service.get_gate_config())


@router.put("/gate-config", response_model=GateConfigOut)
async def update_gate_config(
    payload: GateConfigUpdate,
    session: AsyncSession = Depends(get_session),
    admin: User = Depends(require_admin),
) -> GateConfigOut:
    """Cập nhật toggle hệ thống + `send_directly` per-intent. Ghi MỘT dòng audit (node "admin", `gate_update`).

    `gate_service.update_gate_config` tự mở + commit session riêng nên dòng audit đi NGAY SAU trong session của
    request (không chung transaction được). Ghi audit lỗi chỉ log — cấu hình đã lưu, không trả lỗi cho admin.
    """
    snap = await gate_service.update_gate_config(
        auto_reply_enabled=payload.auto_reply_enabled,
        auto_resolve_enabled=payload.auto_resolve_enabled,
        auto_resolve_minutes=payload.auto_resolve_minutes,
        auto_resolve_grace_minutes=payload.auto_resolve_grace_minutes,
        rules=[(r.intent, r.send_directly) for r in payload.rules] if payload.rules else None,
    )
    try:
        await audit_service.write_audit(
            session,
            node=audit_service.ADMIN_NODE,
            action="gate_update",
            detail={"admin_id": str(admin.id), "changes": payload.model_dump(exclude_none=True)},
        )
        await session.commit()
    except Exception as exc:  # noqa: BLE001 — audit hỏng KHÔNG được làm hỏng cấu hình vừa lưu.
        log.warning("audit gate_update failed (bỏ qua): %s", exc)
    return _gate_out(snap)
