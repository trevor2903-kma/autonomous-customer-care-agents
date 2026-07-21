"""Auth JWT-over-WebSocket (slice 11 P1).

Browser KHÔNG set được header Authorization cho WS → truyền JWT qua query-param `?token=`.
Xác thực SAU `accept()` (để gửi được close-frame có mã): sai/thiếu token hoặc sai role → đóng 4401.
"""

from __future__ import annotations

from typing import Any

from fastapi import WebSocket

from ...core.security import decode_access_token

WS_AUTH_CLOSE_CODE = 4401  # tự-định-nghĩa (4000–4999): xác thực WS thất bại


async def authenticate_websocket(websocket: WebSocket, required_role: str) -> dict[str, Any] | None:
    """Trả payload JWT nếu hợp lệ & đúng role; ngược lại đóng WS (4401) + trả None. Gọi SAU accept()."""
    token = websocket.query_params.get("token")
    payload = decode_access_token(token) if token else None
    if payload is None or payload.get("role") != required_role:
        await websocket.close(code=WS_AUTH_CLOSE_CODE)
        return None
    return payload
