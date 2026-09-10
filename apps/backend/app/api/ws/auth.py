"""Auth JWT-over-WebSocket (slice 11 P1).

Browser KHÔNG set được header Authorization cho WS → truyền JWT qua query-param `?token=`.
Xác thực SAU `accept()` (để gửi được close-frame có mã): sai/thiếu token hoặc sai role → đóng 4401.

Role đọc từ DB, KHÔNG từ claim trong token (audit v2, SEC-XC.3) — cùng luật với `deps.require_admin`: admin bị
hạ quyền / user bị xoá thì token cũ (còn hạn `jwt_expire_minutes`) không mở được WS nữa. DB lỗi → đóng (fail closed).
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import WebSocket

from ...core.database import AsyncSessionLocal
from ...core.logging import get_logger
from ...core.security import decode_access_token
from ...models import User

log = get_logger("ws.auth")

WS_AUTH_CLOSE_CODE = 4401  # tự-định-nghĩa (4000–4999): xác thực WS thất bại


async def _db_role(sub: Any) -> str | None:
    """Role HIỆN TẠI trong DB của user `sub` (session ngắn). `sub` hỏng / user không còn → None; DB lỗi → raise."""
    try:
        user_id = uuid.UUID(str(sub))
    except (ValueError, TypeError):
        return None
    async with AsyncSessionLocal() as s:
        user = await s.get(User, user_id)
        return user.role if user is not None else None


async def authenticate_websocket(websocket: WebSocket, required_role: str) -> dict[str, Any] | None:
    """Trả payload JWT nếu hợp lệ & role TRONG DB đúng; ngược lại đóng WS (4401) + trả None. Gọi SAU accept()."""
    token = websocket.query_params.get("token")
    payload = decode_access_token(token) if token else None
    role: str | None = None
    if payload is not None:
        try:
            role = await _db_role(payload.get("sub"))
        except Exception as exc:  # noqa: BLE001 — không xác minh được quyền → KHÔNG cho vào (fail closed).
            log.warning("ws auth: đọc role từ DB lỗi (đóng kết nối): %s", exc)
    if role is None or role != required_role:
        await websocket.close(code=WS_AUTH_CLOSE_CODE)
        return None
    return payload
