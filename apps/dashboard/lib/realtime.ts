// Tiện ích THUẦN cho realtime (protocol v2 — contract §4): hằng số nối lại / heartbeat / ack, sinh
// client_msg_id, đọc frame. KHÔNG import runtime nào → dùng chung cho hook trình duyệt lẫn test Node
// (`node --test apps/dashboard/lib/*.test.mts`).

/** Nối lại có backoff (FE-01.2): 1 s → 2 s → 4 s → 8 s → trần 15 s. */
export const RECONNECT_BASE_MS = 1000;
export const RECONNECT_MAX_MS = 15000;
/** Heartbeat `{"type":"ping"}` mỗi 25 s; 60 s không nhận được frame nào (kể cả pong) = socket half-open. */
export const HEARTBEAT_MS = 25000;
export const STALE_AFTER_MS = 60000;
/** Tin đã gửi mà quá 10 s chưa có `ack` → "Chưa gửi được" (FE-01.4). */
export const ACK_TIMEOUT_MS = 10000;
/** Mã đóng WS khi token hỏng / hết hạn / sai vai (backend `ws/auth.py`) — KHÔNG nối lại. */
export const WS_AUTH_CLOSE_CODE = 4401;

/** Trễ trước lần nối lại thứ `attempt` (đếm từ 0). */
export function backoffDelay(attempt: number): number {
  return Math.min(RECONNECT_BASE_MS * 2 ** Math.max(0, attempt), RECONNECT_MAX_MS);
}

type CryptoLike = {
  randomUUID?: () => string;
  getRandomValues?: (array: Uint8Array) => Uint8Array;
};

/** uuid v4 cho `client_msg_id` — tái dùng NGUYÊN VĂN khi gửi lại để server nhận ra tin trùng (IDEM-XC.1).
 *  `crypto.randomUUID` chỉ có trong secure context (HTTPS / localhost): PWA mở qua IP LAN bằng http thì
 *  KHÔNG có → tự dựng v4 từ getRandomValues (hoặc Math.random nếu cả cái đó cũng thiếu). */
export function newClientMsgId(
  c: CryptoLike | undefined = (globalThis as { crypto?: CryptoLike }).crypto,
): string {
  if (c?.randomUUID) return c.randomUUID();
  const b = new Uint8Array(16);
  if (c?.getRandomValues) c.getRandomValues(b);
  else for (let i = 0; i < b.length; i++) b[i] = Math.floor(Math.random() * 256);
  b[6] = (b[6] & 0x0f) | 0x40; // version 4
  b[8] = (b[8] & 0x3f) | 0x80; // variant RFC 4122
  const h = Array.from(b, (x) => x.toString(16).padStart(2, "0")).join("");
  return `${h.slice(0, 8)}-${h.slice(8, 12)}-${h.slice(12, 16)}-${h.slice(16, 20)}-${h.slice(20)}`;
}

/** Một frame JSON từ server (dữ liệu từ mạng → không tin kiểu, đọc field qua `asString`). */
export type Frame = Record<string, unknown>;

/** Frame hỏng / không phải object JSON → null (bỏ qua, KHÔNG làm sập màn chat). */
export function parseFrame(raw: unknown): Frame | null {
  if (typeof raw !== "string") return null;
  try {
    const v: unknown = JSON.parse(raw);
    return v !== null && typeof v === "object" && !Array.isArray(v) ? (v as Frame) : null;
  } catch {
    return null;
  }
}

export function asString(v: unknown): string | null {
  return typeof v === "string" ? v : null;
}
