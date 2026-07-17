"""WebSocket admin (HITL 08c) — /ws/admin/{conversation_id}: tiếp quản + trả lời khách trực tiếp (qua hub).

Admin connect → TAKEOVER: `set status HUMAN_HANDLING + assigned_admin_id` (demo admin). Hai task:
- `_admin_reader`: tin admin → lưu (sender=ADMIN) + `hub.publish` sang khách.
- `_hub_listener`: tin khách (từ hub, status-gate ở WS khách route lên) → đẩy xuống socket admin.

Tin admin là egress-NGƯỜI (TÁCH khỏi Response Generator = egress tự động, PRD §7.4). Lịch sử hội thoại admin nạp
qua REST `GET /api/admin/conversations/{id}` (Phase 1) — WS chỉ lo tin realtime MỚI. Admin auth thật = slice 11.
"""

from __future__ import annotations

import asyncio
import uuid
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ...core.database import AsyncSessionLocal
from ...core.logging import get_logger
from ...models.enums import ConversationStatus, MessageSender
from ...services import conversation_service
from .hub import hub

router = APIRouter()
log = get_logger("ws.admin")

# Demo admin (id cố định) — admin auth/RBAC thật = slice 11.
DEMO_ADMIN_ID = uuid.UUID("00000000-0000-0000-0000-0000000000ad")


async def _takeover(conv_id: uuid.UUID) -> str | None:
    """Tiếp quản khi admin mở kết nối: IN_HUMAN_QUEUE → HUMAN_HANDLING + gán admin. PENDING_APPROVAL GIỮ NGUYÊN
    (đang chờ DUYỆT nháp, không phải tiếp quản chat — approve/reject mới chuyển trạng thái). Trả status hiện tại."""
    try:
        async with AsyncSessionLocal() as s:
            current = await conversation_service.get_status(s, conv_id)
            if current == ConversationStatus.IN_HUMAN_QUEUE:
                conv = await conversation_service.assign_admin(
                    s, conv_id, DEMO_ADMIN_ID, status=ConversationStatus.HUMAN_HANDLING
                )
                return conv.status if conv else current
            return current
    except Exception as exc:  # noqa: BLE001 — takeover lỗi → vẫn cho admin chat (chỉ log).
        log.warning("takeover failed (conv=%s): %s", conv_id, exc)
        return None


async def _persist_admin_message(conv_id: uuid.UUID, content: str) -> None:
    try:
        async with AsyncSessionLocal() as s:
            await conversation_service.add_message(
                s, conv_id, content=content, sender=MessageSender.ADMIN
            )
    except Exception as exc:  # noqa: BLE001
        log.warning("persist admin message failed (bỏ qua): %s", exc)


async def _admin_reader(
    websocket: WebSocket,
    conv_id: uuid.UUID,
    conv_key: str,
    self_queue: asyncio.Queue[dict[str, Any]],
) -> None:
    """Đọc tin admin → lưu (sender=ADMIN) + phát sang khách qua hub."""
    try:
        while True:
            content = await websocket.receive_text()
            await _persist_admin_message(conv_id, content)
            await hub.publish(
                conv_key, {"type": "message", "from": "admin", "content": content}, exclude=self_queue
            )
    except WebSocketDisconnect:
        log.info("admin WS disconnected (conv=%s)", conv_id)


async def _hub_listener(websocket: WebSocket, queue: asyncio.Queue[dict[str, Any]]) -> None:
    """Nhận payload (tin khách) từ hub → đẩy xuống socket admin."""
    while True:
        payload = await queue.get()
        await websocket.send_json(payload)


@router.websocket("/ws/admin/{conversation_id}")
async def admin_ws(websocket: WebSocket, conversation_id: uuid.UUID) -> None:
    await websocket.accept()
    status = await _takeover(conversation_id)  # tiếp quản ngay khi mở kết nối
    await websocket.send_json({"type": "system", "message": "admin connected", "status": status})
    log.info("admin WS connected (conv=%s status=%s)", conversation_id, status)

    conv_key = str(conversation_id)
    queue = hub.register(conv_key)
    reader = asyncio.create_task(_admin_reader(websocket, conversation_id, conv_key, queue))
    listener = asyncio.create_task(_hub_listener(websocket, queue))
    try:
        _, pending = await asyncio.wait({reader, listener}, return_when=asyncio.FIRST_COMPLETED)
        for task in pending:
            task.cancel()
        await asyncio.gather(*pending, return_exceptions=True)
    finally:
        hub.unregister(conv_key, queue)
        log.info("admin WS closed (conv=%s)", conversation_id)
