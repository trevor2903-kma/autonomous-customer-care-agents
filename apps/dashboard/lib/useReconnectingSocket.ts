"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { probeSession } from "@/lib/api";
import {
  AUTH_PROBE_TIMEOUT_MS,
  HEARTBEAT_MS,
  STALE_AFTER_MS,
  WS_AUTH_CLOSE_CODE,
  backoffDelay,
  parseFrame,
  stopAfterAuthClose,
  type Frame,
} from "@/lib/realtime";

// Socket tự nối lại DÙNG CHUNG (FE-01.2) cho chat khách, màn ca admin và inbox admin.
// - Rớt → nối lại khi còn mounted, backoff 1 s → 2 s → 4 s → 8 s → trần 15 s.
// - Heartbeat `{"type":"ping"}` mỗi 25 s; 60 s không nhận được frame nào (pong hay frame bất kỳ) = half-open
//   (TCP chết nhưng trình duyệt chưa bắn `close`) → bỏ socket NGAY và nối lại, không chờ close handshake.
// - Đóng 4401 → hỏi lại `/api/auth/me`: chỉ khi hết phiên thật (401 / sai vai) mới KHÔNG nối lại (để vòng đăng nhập
//   hiện có lo). Backend cũng đóng 4401 khi DB lỗi lúc đọc role → khi đó nối lại như mọi lần rớt khác.
// - Handler luôn là bản MỚI NHẤT (ref) → không gắn trùng listener qua các lần re-render; unmount = đóng sạch.

/** "offline" = đã dừng hẳn (hết phiên thật sau đóng 4401 / không có token) — khác "reconnecting" (đang thử lại). */
export type ConnState = "connecting" | "online" | "reconnecting" | "offline";

export type SocketHandlers = {
  /** Vai socket này đòi (khớp `required_role` backend) — đóng 4401 mà `/api/auth/me` báo vai khác → dừng hẳn. */
  authRole?: string;
  /** Mọi frame JSON hợp lệ, trừ `pong` (hook tự nuốt). */
  onFrame: (frame: Frame) => void;
  /** Socket mở. `isReconnect` = không phải lần mở đầu tiên → caller đối soát lại (nạp lại lịch sử…). */
  onOpen?: (isReconnect: boolean) => void;
  /** Socket vừa rớt (trước khi thử lại) — vd gỡ "đang trả lời…" để không kẹt. */
  onDown?: () => void;
};

export function useReconnectingSocket(url: string | null, handlers: SocketHandlers) {
  const [state, setState] = useState<ConnState>("connecting");
  const handlersRef = useRef(handlers);
  handlersRef.current = handlers;
  const wsRef = useRef<WebSocket | null>(null);
  const forceRef = useRef<() => void>(() => {});

  useEffect(() => {
    if (!url) {
      setState("offline");
      return;
    }
    let disposed = false;
    let attempt = 0;
    let everOpened = false;
    let lastSeen = 0;
    let retryTimer: ReturnType<typeof setTimeout> | undefined;
    let beatTimer: ReturnType<typeof setInterval> | undefined;
    setState("connecting");

    const stopBeat = () => {
      if (beatTimer !== undefined) clearInterval(beatTimer);
      beatTimer = undefined;
    };

    // Gỡ handler RỒI mới close: socket đã bỏ không được bắn onclose/onmessage vào state hiện tại.
    const discard = (ws: WebSocket) => {
      ws.onopen = null;
      ws.onmessage = null;
      ws.onclose = null;
      ws.onerror = null;
      try {
        ws.close();
      } catch {
        /* đã đóng */
      }
    };

    const armRetry = () => {
      if (retryTimer !== undefined) clearTimeout(retryTimer);
      retryTimer = setTimeout(connect, backoffDelay(attempt));
      attempt += 1;
    };

    const scheduleReconnect = () => {
      if (disposed) return;
      setState("reconnecting");
      handlersRef.current.onDown?.();
      armRetry();
    };

    // Bỏ socket ĐANG MỞ (nghi half-open) rồi nối lại. Chưa có socket (đang chờ nối lại) hoặc socket còn CONNECTING
    // (lần nối lại đang dở) → không làm gì: hẹn giờ ack sót lại của socket cũ không được giết lần nối lại đó.
    const forceReconnect = () => {
      const ws = wsRef.current;
      if (!ws || disposed || ws.readyState !== WebSocket.OPEN) return;
      wsRef.current = null;
      stopBeat();
      discard(ws);
      scheduleReconnect();
    };

    function connect() {
      if (disposed) return;
      retryTimer = undefined;
      let ws: WebSocket;
      try {
        ws = new WebSocket(url as string);
      } catch {
        scheduleReconnect();
        return;
      }
      wsRef.current = ws;
      ws.onopen = () => {
        lastSeen = Date.now();
        setState("online");
        const isReconnect = everOpened;
        everOpened = true;
        stopBeat();
        beatTimer = setInterval(() => {
          if (Date.now() - lastSeen > STALE_AFTER_MS) {
            forceReconnect();
            return;
          }
          try {
            ws.send(JSON.stringify({ type: "ping" }));
          } catch {
            /* onclose sẽ lo */
          }
        }, HEARTBEAT_MS);
        handlersRef.current.onOpen?.(isReconnect);
      };
      ws.onmessage = (ev: MessageEvent) => {
        lastSeen = Date.now();
        attempt = 0; // nhận được frame = kết nối dùng được thật → reset backoff
        const frame = parseFrame(ev.data);
        if (!frame || frame.type === "pong") return;
        handlersRef.current.onFrame(frame);
      };
      ws.onclose = (ev: CloseEvent) => {
        stopBeat();
        if (wsRef.current === ws) wsRef.current = null;
        if (disposed) return;
        if (ev.code === WS_AUTH_CLOSE_CODE) {
          // 4401 chưa chắc là hết phiên (backend đóng 4401 cả khi DB lỗi lúc đọc role): hỏi REST rồi mới quyết —
          // hết phiên thật → dừng hẳn; còn lại nối lại với backoff như mọi lần rớt.
          setState("reconnecting");
          handlersRef.current.onDown?.();
          void probeSession(AUTH_PROBE_TIMEOUT_MS).then((me) => {
            if (disposed) return;
            if (stopAfterAuthClose(me, handlersRef.current.authRole)) setState("offline");
            else armRetry();
          });
          return;
        }
        scheduleReconnect();
      };
    }

    forceRef.current = forceReconnect;
    connect();
    return () => {
      disposed = true;
      stopBeat();
      if (retryTimer !== undefined) clearTimeout(retryTimer);
      const ws = wsRef.current;
      wsRef.current = null;
      if (ws) discard(ws);
      forceRef.current = () => {};
    };
  }, [url]);

  /** Gửi một frame JSON. false = socket chưa/không mở (caller đánh dấu tin "chưa gửi được"). */
  const send = useCallback((payload: object): boolean => {
    const ws = wsRef.current;
    if (!ws || ws.readyState !== WebSocket.OPEN) return false;
    try {
      ws.send(JSON.stringify(payload));
      return true;
    } catch {
      return false;
    }
  }, []);

  /** Bỏ socket hiện tại và nối lại ngay (vd quá hạn ack → nghi half-open). */
  const reconnect = useCallback(() => forceRef.current(), []);

  return { state, send, reconnect };
}
