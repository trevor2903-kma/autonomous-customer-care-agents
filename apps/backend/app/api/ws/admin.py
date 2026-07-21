"""WebSocket admin (HITL 08c) — /ws/admin/{conversation_id}: theo dõi + trả lời khách trực tiếp (qua hub).

MỞ KẾT NỐI = CHỈ XEM (fix 08c): chỉ đọc status, KHÔNG đổi trạng thái. Tiếp quản là hành động tường minh
`POST /api/admin/conversations/{id}/takeover` — nhờ vậy xem một ca không làm nó rời hàng đợi.

Hai task:
- `_admin_reader`: tin admin → lưu (sender=ADMIN) + `hub.publish` sang khách.
- `_hub_listener`: tin khách (từ hub, status-gate ở WS khách route lên) → đẩy xuống socket admin.

Tin admin là egress-NGƯỜI (TÁCH khỏi Response Generator = egress tự động, PRD §7.4). Lịch sử hội thoại admin nạp
qua REST `GET /api/admin/conversations/{id}` — WS chỉ lo tin realtime MỚI. Admin auth thật = slice 11.
"""

from __future__ import annotations

import asyncio
import uuid
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ...core.database import AsyncSessionLocal
from ...core.logging import get_logger
from ...models.enums import MessageSender, UserRole
from ...services import conversation_service
from .auth import authenticate_websocket
from .hub import hub

router = APIRouter()
log = get_logger("ws.admin")


async def _current_status(conv_id: uuid.UUID) -> str | None:
    """CHỈ ĐỌC status (fix 08c) — mở kết nối admin KHÔNG đổi trạng thái hội thoại.

    Tiếp quản là hành động tường minh: `POST /api/admin/conversations/{id}/takeover`. Nhờ vậy admin xem một ca
    trong hàng đợi mà ca đó KHÔNG bị rời hàng đợi / gán nhầm người xử lý.
    """
    try:
        async with AsyncSessionLocal() as s:
            return await conversation_service.get_status(s, conv_id)
    except Exception as exc:  # noqa: BLE001 — đọc status lỗi → vẫn cho admin mở (chỉ log).
        log.warning("read status failed (conv=%s): %s", conv_id, exc)
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
    auth = await authenticate_websocket(websocket, UserRole.ADMIN)  # JWT ?token= (P1)
    if auth is None:
        return  # helper đã đóng 4401 (thiếu/sai token hoặc không phải admin)
    status = await _current_status(conversation_id)  # CHỈ XEM — không đổi status (fix 08c)
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
