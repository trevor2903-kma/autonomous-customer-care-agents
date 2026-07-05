"""WebSocket chat — lát cắt RAG-intent: trả KẾT QUẢ PHÂN LOẠI (dev/verify signal).

QUAN TRỌNG (PRD §7.4 + CLAUDE.md): message `type=classification` là TÍN HIỆU DEV/VERIFY, KHÔNG phải câu
trả lời cuối cho khách. Response Generator vẫn là điểm phát ngôn DUY NHẤT — wiring câu trả lời thật (chạy
đủ pipeline + phát qua Response Generator) là việc SAU lát cắt này.

TODO (PRD §7.4, §8, §10):
  - Tin nhắn khách -> tạo Message -> chạy ĐỦ pipeline (BackgroundTasks) -> phát realtime qua Response Generator.
  - Phát tin tới client/Admin qua **Redis pub/sub** (FR-ASYNC-7), KHÔNG polling.
  - Khi hội thoại ở IN_HUMAN_QUEUE/HUMAN_HANDLING: định tuyến tin tới Admin, KHÔNG tới AI (FR-ASYNC-3).
"""

from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ...agents.nodes.intent import classify_intent
from ...core.logging import get_logger

router = APIRouter()
log = get_logger("ws.chat")


@router.websocket("/ws/chat")
async def chat_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    await websocket.send_json({"type": "system", "message": "connected (classification mode — RAG intent slice)"})
    log.info("WebSocket client connected (classification mode)")
    try:
        while True:
            data = await websocket.receive_text()
            # Lát cắt: chỉ phân loại intent (metadata), CHƯA sinh câu trả lời khách (Response Generator lo sau).
            result = await classify_intent(data)
            await websocket.send_json(
                {
                    "type": "classification",
                    "intent": result["intent"],
                    "confidence": result["confidence"],
                    "entities": result["entities"],
                }
            )
    except WebSocketDisconnect:
        log.info("WebSocket client disconnected")
