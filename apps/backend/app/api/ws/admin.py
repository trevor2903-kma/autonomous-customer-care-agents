"""WebSocket admin (HITL 08c).

- `/ws/admin/{conversation_id}`: theo dõi + trả lời khách trực tiếp (qua hub).
- `/ws/admin-inbox` (audit v2, FE-01.5 — thay polling 10s): mọi tin mới + mọi đổi status của MỌI ca →
  `{"type":"inbox","conversation_id","event","status"}`; FE gom (~800 ms) rồi làm tươi danh sách/hàng đợi.

MỞ KẾT NỐI = CHỈ XEM (fix 08c): chỉ đọc status, KHÔNG đổi trạng thái. Tiếp quản là hành động tường minh
`POST /api/admin/conversations/{id}/takeover` — nhờ vậy xem một ca không làm nó rời hàng đợi.

CHỈ admin ĐANG GIỮ ca mới gửi được tin (audit v2, FE-03.2 / GRAPH-02.4): mỗi tin đọc lại DB — ca phải
HUMAN_HANDLING và `assigned_admin_id` = admin của socket (JWT `sub`); ngược lại → `error/not_assigned`, KHÔNG
lưu, KHÔNG phát.

Hai task mỗi kết nối ca:
- `_admin_reader`: frame admin (giao thức v2: message / ping / chữ thô legacy) → lưu (sender=ADMIN) + phát sang
  khách qua hub → `ack` kèm `message_id`.
- `_hub_listener`: frame từ hub (tin khách, trả lời AI, `status`) → đẩy xuống socket admin.

Tin admin là egress-NGƯỜI (TÁCH khỏi Response Generator = egress tự động, PRD §7.4). Lịch sử hội thoại admin nạp
qua REST `GET /api/admin/conversations/{id}` — WS chỉ lo tin realtime MỚI.
"""

from __future__ import annotations

import asyncio
import uuid
from typing import Any, Literal

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.exc import IntegrityError

from ...core.database import AsyncSessionLocal
from ...core.logging import get_logger
from ...models.enums import ConversationStatus, MessageSender, UserRole
from ...models.message import CLIENT_MSG_ID_INDEX
from ...services import conversation_service
from .auth import WS_AUTH_CLOSE_CODE, authenticate_websocket
from .hub import INBOX_KEY, hub, parse_client_frame

router = APIRouter()
log = get_logger("ws.admin")

_SendResult = Literal["ok", "duplicate", "not_assigned", "error"]


def _sid(value: Any) -> str | None:
    return str(value) if value is not None else None


async def _current_state(conv_id: uuid.UUID) -> tuple[str | None, uuid.UUID | None]:
    """CHỈ ĐỌC `(status, người giữ)` (fix 08c) — mở kết nối admin KHÔNG đổi trạng thái hội thoại.

    Tiếp quản là hành động tường minh: `POST /api/admin/conversations/{id}/takeover`. Nhờ vậy admin xem một ca
    trong hàng đợi mà ca đó KHÔNG bị rời hàng đợi / gán nhầm người xử lý.
    """
    try:
        async with AsyncSessionLocal() as s:
            state = await conversation_service.get_status_and_admin(s, conv_id)
    except Exception as exc:  # noqa: BLE001 — đọc status lỗi → vẫn cho admin mở (chỉ log).
        log.warning("read status failed (conv=%s): %s", conv_id, exc)
        return None, None
    return state if state is not None else (None, None)


async def _persist_admin_message(
    conv_id: uuid.UUID, admin_id: uuid.UUID, content: str, client_msg_id: str | None
) -> tuple[_SendResult, uuid.UUID | None]:
    """Lưu tin admin NẾU admin này đang giữ ca (đọc tươi, session NGẮN).

    → `("ok", id)` | `("not_assigned", None)` | `("duplicate", None)` (client_msg_id đã lưu = gửi lại) |
    `("error", None)` (DB lỗi). Kiểm "đang giữ ca" bằng SELECT … FOR UPDATE, khoá giữ tới commit: một lần đổi status
    (kể cả resolve của CHÍNH admin này từ tab/PWA khác) phải CHỜ tin được lưu → không có tin admin nằm trong ca đã đóng.
    """
    try:
        async with AsyncSessionLocal() as s:
            state = await conversation_service.get_status_and_admin(s, conv_id, for_update=True)
            if state is None or state[0] != ConversationStatus.HUMAN_HANDLING or state[1] != admin_id:
                return "not_assigned", None
            message = await conversation_service.insert_message(
                s, conv_id, sender=MessageSender.ADMIN, content=content, client_msg_id=client_msg_id
            )
            await s.commit()
            return "ok", message.id
    except IntegrityError as exc:
        if CLIENT_MSG_ID_INDEX in str(exc):
            return "duplicate", None
        log.warning("persist admin message failed: %s", exc)
        return "error", None
    except Exception as exc:  # noqa: BLE001
        log.warning("persist admin message failed: %s", exc)
        return "error", None


async def _admin_reader(
    websocket: WebSocket,
    conv_id: uuid.UUID,
    conv_key: str,
    self_queue: asyncio.Queue[dict[str, Any]],
    admin_id: uuid.UUID,
) -> None:
    """Frame admin → (đang giữ ca?) lưu + phát sang khách qua hub → `ack`; không giữ ca → `error/not_assigned`."""
    try:
        while True:
            frame = parse_client_frame(await websocket.receive_text())
            if frame.kind == "ping":
                await websocket.send_json({"type": "pong"})
                continue
            result, message_id = await _persist_admin_message(
                conv_id, admin_id, frame.content, frame.client_msg_id
            )
            if result == "not_assigned":
                await websocket.send_json(
                    {"type": "error", "code": "not_assigned", "client_msg_id": frame.client_msg_id}
                )
                continue
            if result == "error":
                continue  # DB lỗi: KHÔNG ack → client quá hạn chờ ack, đánh dấu gửi lỗi để admin gửi lại.
            if result == "ok":
                await hub.notify_message(
                    conv_key,
                    sender=MessageSender.ADMIN,
                    content=frame.content,
                    message_id=message_id,
                    client_msg_id=frame.client_msg_id,
                    exclude=self_queue,
                )
            await websocket.send_json(
                {
                    "type": "ack",
                    "client_msg_id": frame.client_msg_id,
                    "message_id": _sid(message_id),
                    "duplicate": result == "duplicate",
                }
            )
    except WebSocketDisconnect:
        log.info("admin WS disconnected (conv=%s)", conv_id)


async def _hub_listener(websocket: WebSocket, queue: asyncio.Queue[dict[str, Any]]) -> None:
    """Nhận payload từ hub (tin khách/AI, status, sự kiện inbox) → đẩy xuống socket admin."""
    while True:
        payload = await queue.get()
        await websocket.send_json(payload)


async def _inbox_reader(websocket: WebSocket) -> None:
    """Kênh inbox chỉ nhận `ping` (heartbeat) → `pong`; frame khác bỏ qua."""
    try:
        while True:
            if parse_client_frame(await websocket.receive_text()).kind == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        log.info("admin inbox WS disconnected")


async def _run_until_first_done(*tasks: asyncio.Task[None]) -> None:
    """Một task xong (rớt kết nối) → huỷ task còn lại."""
    _, pending = await asyncio.wait(set(tasks), return_when=asyncio.FIRST_COMPLETED)
    for task in pending:
        task.cancel()
    await asyncio.gather(*pending, return_exceptions=True)


# Khai báo TRƯỚC route ca cho rõ ý: `/ws/admin/{conversation_id}` (có "/" sau "admin") không khớp được
# `/ws/admin-inbox`, nên route ca không bao giờ nuốt kênh inbox.
@router.websocket("/ws/admin-inbox")
async def admin_inbox_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    if await authenticate_websocket(websocket, UserRole.ADMIN) is None:
        return  # helper đã đóng 4401
    queue = hub.register(INBOX_KEY)
    log.info("admin inbox WS connected")
    reader = asyncio.create_task(_inbox_reader(websocket))
    listener = asyncio.create_task(_hub_listener(websocket, queue))
    try:
        await _run_until_first_done(reader, listener)
    finally:
        hub.unregister(INBOX_KEY, queue)
        log.info("admin inbox WS closed")


@router.websocket("/ws/admin/{conversation_id}")
async def admin_ws(websocket: WebSocket, conversation_id: uuid.UUID) -> None:
    await websocket.accept()
    auth = await authenticate_websocket(websocket, UserRole.ADMIN)  # JWT ?token= (P1)
    if auth is None:
        return  # helper đã đóng 4401 (thiếu/sai token hoặc không phải admin)
    try:
        admin_id = uuid.UUID(str(auth.get("sub")))
    except (ValueError, TypeError):
        await websocket.close(code=WS_AUTH_CLOSE_CODE)
        return
    conv_key = str(conversation_id)
    # Đăng ký hub TRƯỚC khi đọc snapshot (FE-01.3): sự kiện phát giữa lúc đọc status và lúc gửi frame connect nằm sẵn
    # trong queue, tới socket ngay sau frame connect — không lỡ. Frame status tới sau snapshot vô hại (FE lấy bản mới).
    queue = hub.register(conv_key)
    try:
        status, holder = await _current_state(conversation_id)  # CHỈ XEM — không đổi status (fix 08c)
        await websocket.send_json(
            {"type": "system", "message": "admin connected", "status": status, "assigned_admin_id": _sid(holder)}
        )
        log.info("admin WS connected (conv=%s status=%s)", conversation_id, status)
        reader = asyncio.create_task(_admin_reader(websocket, conversation_id, conv_key, queue, admin_id))
        listener = asyncio.create_task(_hub_listener(websocket, queue))
        await _run_until_first_done(reader, listener)
    finally:
        hub.unregister(conv_key, queue)
        log.info("admin WS closed (conv=%s)", conversation_id)
