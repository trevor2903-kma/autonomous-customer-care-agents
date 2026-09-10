// Ghép tin THUẦN (không import runtime): chống trùng khi lịch sử REST gặp frame realtime + vòng đời gửi của
// tin có client_msg_id (protocol v2 — contract §4/§5). Test: node --test apps/dashboard/lib/*.test.mts.

import type { Message } from "shared-types";
import type { ChatMessage } from "@/components/chat/ChatWindow";
import type { ThreadMessage } from "@/lib/api";

/** Vòng đời một tin client tự gửi: đang gửi → đã gửi (có `ack`) → chưa gửi được (quá hạn / frame `error`). */
export type SendState = "sending" | "sent" | "failed";

/** Phần chung của một bong bóng client theo dõi được (khách hoặc admin). */
type Trackable = { messageId?: string | null; clientMsgId?: string; sendState?: SendState };

/** `ack` → "đã gửi" (+ message_id nếu server trả về). */
export function markSent<T extends Trackable>(list: T[], cid: string, messageId?: string | null): T[] {
  return list.map((m) =>
    m.clientMsgId === cid
      ? { ...m, sendState: "sent" as SendState, messageId: messageId ?? m.messageId }
      : m,
  );
}

/** Quá hạn ack / frame `error` → "chưa gửi được". Chỉ hạ từ "sending": ack đã tới trước thì vẫn là "đã gửi". */
export function markFailed<T extends Trackable>(list: T[], cid: string): T[] {
  return list.map((m) =>
    m.clientMsgId === cid && m.sendState === "sending" ? { ...m, sendState: "failed" as SendState } : m,
  );
}

/** Gửi lại (cùng client_msg_id) → về "sending"; tin đã "sent" giữ nguyên. */
export function markSending<T extends Trackable>(list: T[], cid: string): T[] {
  return list.map((m) =>
    m.clientMsgId === cid && m.sendState !== "sent" ? { ...m, sendState: "sending" as SendState } : m,
  );
}

/** Thêm tin realtime; bỏ qua nếu message_id đã hiện (frame lặp, hoặc tin đã có trong lịch sử). */
export function appendUnique<T extends Trackable>(list: T[], item: T): T[] {
  if (item.messageId && list.some((m) => m.messageId === item.messageId)) return list;
  return [...list, item];
}

/** Người gửi trong lịch sử → loại bong bóng phía khách. */
export function senderToFrom(sender: string): ChatMessage["from"] {
  if (sender === "customer") return "you";
  if (sender === "admin") return "admin";
  return "ai";
}

/** Khách (FE-01.2 / FE-01.4): ghép lịch sử `/me/thread` với danh sách đang hiển thị — dùng cả lúc nạp đầu lẫn
 *  sau mỗi lần nối lại.
 *  - lịch sử mới nạp đứng TRƯỚC và thay toàn bộ phần lịch sử cũ;
 *  - frame realtime đã có trong lịch sử (message_id) → bỏ bản realtime (không trùng);
 *  - tin mình gửi mà client_msg_id đã có trong lịch sử → chính bản lịch sử, tức "đã gửi";
 *  - còn lại (tin tới SAU lúc chụp lịch sử, tin đang gửi / chưa gửi được, thông báo tạm) giữ nguyên thứ tự ở
 *    cuối. Bong bóng đã hiện giữ nguyên `id` (key React) → không dựng lại cả danh sách. */
export function reconcileThread(
  local: ChatMessage[],
  thread: ThreadMessage[],
  nextId: () => number,
  timeOf: (iso: string) => string,
): ChatMessage[] {
  const ids = new Set(thread.map((m) => m.id));
  const cids = new Set(thread.map((m) => m.client_msg_id).filter((c): c is string => !!c));
  const keyByMsg = new Map<string, number>();
  const keyByCid = new Map<string, number>();
  for (const m of local) {
    if (m.messageId) keyByMsg.set(m.messageId, m.id);
    if (m.clientMsgId) keyByCid.set(m.clientMsgId, m.id);
  }
  const history: ChatMessage[] = thread.map((m) => ({
    id:
      keyByMsg.get(m.id) ??
      (m.client_msg_id ? keyByCid.get(m.client_msg_id) : undefined) ??
      nextId(),
    from: senderToFrom(m.sender),
    text: m.content,
    time: timeOf(m.created_at),
    messageId: m.id,
    fromHistory: true,
  }));
  const rest = local.filter(
    (m) =>
      !m.fromHistory &&
      !(m.messageId && ids.has(m.messageId)) &&
      !(m.clientMsgId && cids.has(m.clientMsgId)),
  );
  return [...history, ...rest];
}

/** Một dòng trong màn ca admin: bản đã lưu (REST) hoặc bản realtime / đang gửi. `at` = ISO thời điểm. */
export type AdminMsg = Trackable & { key: string; sender: string; content: string; at: string };

/** Admin (FE-01.1): tin đã lưu (REST — nạp lại mỗi lần mở trang và mỗi lần socket (nối lại) mở) + phần
 *  realtime CHƯA có trong đó. Chống trùng bằng message_id (frame hub, ack) và client_msg_id (tin admin gửi). */
export function mergeAdminMessages(fetched: Message[], live: AdminMsg[]): AdminMsg[] {
  const ids = new Set(fetched.map((m) => m.id));
  const cids = new Set(fetched.map((m) => m.client_msg_id).filter((c): c is string => !!c));
  return [
    ...fetched.map(
      (m): AdminMsg => ({
        key: m.id,
        sender: m.sender,
        content: m.content,
        at: m.created_at,
        messageId: m.id,
      }),
    ),
    ...live.filter(
      (m) => !(m.messageId && ids.has(m.messageId)) && !(m.clientMsgId && cids.has(m.clientMsgId)),
    ),
  ];
}
