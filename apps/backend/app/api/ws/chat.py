"""WebSocket chat — cổng chat khách chạy ĐỦ pipeline (PRD §6, §8, §16).

Mỗi tin nhắn khách → gửi `{"type":"typing"}` (UX) → chạy `run_pipeline` (intent → knowledge →
decision(pass-through) → response) → gửi `{"type":"reply", content}` (câu trả lời do RESPONSE GENERATOR sinh —
điểm phát ngôn DUY NHẤT, PRD §7.4). Lỗi pipeline → câu xin lỗi, KHÔNG rớt kết nối.

Phạm vi slice happy-case (xem plan): 1 khách/1 kết nối → gửi thẳng qua WS. **KHÔNG** Redis pub/sub (dành cho
multi-client/Admin ở HITL phase sau, FR-ASYNC-7). Single-turn: mỗi tin chạy pipeline độc lập (bộ nhớ đa lượt —
ROADMAP 09a). Persist hội thoại/message = TUỲ CHỌN (Phase 4).

TODO (PRD §7.4, §10): persist Message + audit; khi hội thoại ở IN_HUMAN_QUEUE/HUMAN_HANDLING → định tuyến tin
tới Admin, KHÔNG tới AI (FR-ASYNC-3); phát realtime qua Redis pub/sub.
"""

from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ...agents.graph import run_pipeline
from ...core.logging import get_logger

router = APIRouter()
log = get_logger("ws.chat")

# Câu xin lỗi khi pipeline lỗi bất ngờ — KHÔNG rớt WS (phanh cuối, đừng để khách thấy stacktrace).
_ERROR_REPLY = (
    "Dạ hệ thống đang gặp trục trặc tạm thời, em xin phép chuyển yêu cầu tới nhân viên hỗ trợ ạ. "
    "Mong anh/chị thông cảm."
)


@router.websocket("/ws/chat")
async def chat_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    conn_id = str(uuid4())  # NHÃN kết nối cho log (KHÔNG dùng làm thread_id — xem dưới).
    await websocket.send_json({"type": "system", "message": "connected"})
    log.info("WebSocket client connected (conn_id=%s)", conn_id)
    try:
        while True:
            msg = await websocket.receive_text()
            await websocket.send_json({"type": "typing"})  # UX: hiện "đang trả lời…"
            try:
                # Single-turn: MỖI tin chạy pipeline ĐỘC LẬP -> thread_id mới (run_pipeline tự sinh uuid).
                # KHÔNG tái dùng 1 thread_id/kết nối: graph có MemorySaver checkpointer nên reduce-channel
                # (messages/trace/uncertainty_flags, PRD §5) sẽ TÍCH LUỸ + rò cờ qua các lượt. Bộ nhớ đa
                # lượt (dùng thread_id ổn định) là ROADMAP 09a.
                final = await run_pipeline(input_text=msg)
                reply = (final.get("result") or {}).get("reply") or _ERROR_REPLY
            except Exception as exc:  # noqa: BLE001 — lỗi pipeline → xin lỗi, KHÔNG rớt kết nối.
                log.warning("pipeline failed on WS message -> apology: %s", exc)
                reply = _ERROR_REPLY
            await websocket.send_json({"type": "reply", "content": reply})
    except WebSocketDisconnect:
        log.info("WebSocket client disconnected (conn_id=%s)", conn_id)
