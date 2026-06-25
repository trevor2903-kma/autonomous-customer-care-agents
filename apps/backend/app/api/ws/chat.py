"""WebSocket chat — SCAFFOLD: chỉ ECHO (chứng minh transport realtime).

CHƯA wiring AI pipeline / Redis pub/sub (đúng phạm vi scaffold — plan §2).

TODO (PRD §7.4, §8, §10):
  - Tin nhắn khách -> tạo Message -> chạy pipeline (BackgroundTasks) -> phát realtime.
  - Phát tin tới client/Admin qua **Redis pub/sub** (FR-ASYNC-7), KHÔNG polling.
  - Mọi phát ngôn tới khách CHỈ đến từ **Response Generator** — điểm phát ngôn DUY NHẤT (PRD §7.4).
    KHÔNG gửi tin cho khách rải rác ở node/handler khác.
  - Khi hội thoại ở IN_HUMAN_QUEUE/HUMAN_HANDLING: định tuyến tin tới Admin, KHÔNG tới AI (FR-ASYNC-3).
"""

from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ...core.logging import get_logger

router = APIRouter()
log = get_logger("ws.chat")


@router.websocket("/ws/chat")
async def chat_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    await websocket.send_json({"type": "system", "message": "connected (echo mode — scaffold)"})
    log.info("WebSocket client connected (echo mode)")
    try:
        while True:
            data = await websocket.receive_text()
            # Scaffold: echo nguyên văn. Phase sau thay bằng pipeline + pub/sub.
            await websocket.send_json({"type": "echo", "message": data})
    except WebSocketDisconnect:
        log.info("WebSocket client disconnected")
