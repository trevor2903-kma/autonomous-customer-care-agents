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

/** Nối lại (FE-01.4): tin mình gửi mà lịch sử vừa nạp CHƯA có — "đang gửi" LẪN "đã gửi". `ack` chỉ là biên nhận
 *  TRƯỚC khi lưu: server khởi động lại lúc lượt còn xếp hàng thì tin "đã gửi" mất mà UI vẫn báo đã gửi. Gửi lại cùng
 *  client_msg_id là an toàn (server còn nhớ id / unique index ở DB → `duplicate`, không chạy lại lượt). Tin "chưa gửi
 *  được" chờ khách bấm "Gửi lại". */
export function unconfirmedOwn(
  local: ChatMessage[],
  thread: ThreadMessage[],
): { cid: string; text: string }[] {
  const saved = new Set(thread.map((m) => m.client_msg_id).filter((c): c is string => !!c));
  const out: { cid: string; text: string }[] = [];
  for (const m of local) {
    const cid = m.clientMsgId;
    if (m.from !== "you" || !cid || saved.has(cid)) continue;
    if (m.sendState === "sending" || m.sendState === "sent") out.push({ cid, text: m.text });
  }
  return out;
}

/** Đánh dấu các tin vừa gửi lại lúc nối lại: lượt gốc (của socket CŨ) có thể vẫn lưu rồi phát lại tin qua hub
 *  (from:"customer") tới socket mới — xem `absorbOwnEcho`. */
export function markEchoPending(list: ChatMessage[], cids: ReadonlySet<string>): ChatMessage[] {
  return list.map((m) => (m.clientMsgId && cids.has(m.clientMsgId) ? { ...m, echoPending: true } : m));
}

/** Frame hub from:"customer" CÓ client_msg_id (FE-01.6): khớp CHÍNH XÁC bong bóng tab này đã gửi → gắn message_id,
 *  "đã gửi" (không thêm bong bóng thứ hai). null = không phải tin của tab này (tab/thiết bị khác) → thêm như thường. */
export function absorbOwnById(
  list: ChatMessage[],
  cid: string,
  messageId: string | null,
): ChatMessage[] | null {
  const i = list.findIndex((m) => m.clientMsgId === cid);
  if (i < 0) return null;
  const out = list.slice();
  out[i] = { ...list[i], messageId: messageId ?? list[i].messageId, echoPending: false, sendState: "sent" };
  return out;
}

// So nội dung như server thấy: backend chuẩn hoá tin khách (NFKC + gộp khoảng trắng — core/sanitize.py) rồi mới
// lưu/phát, nên chuẩn hoá tương tự ở cả hai phía.
const normText = (s: string) => s.normalize("NFKC").replace(/\s+/g, " ").trim();

/** Frame hub from:"customer" (FE-01.6). Khớp một bong bóng `echoPending` của tab này (chưa có message_id, cùng nội
 *  dung) → đó là tiếng vọng tin mình gửi trước lúc nối lại: gắn message_id vào CHÍNH bong bóng đó (đã lưu = đã gửi)
 *  thay vì thêm bong bóng "bạn" thứ hai. null = không khớp → tin gõ ở tab/thiết bị khác, thêm như thường. Chỉ xét
 *  bong bóng `echoPending` (không phải mọi tin chưa có message_id): tab khác bấm đúng câu gợi ý nhanh mình từng gửi
 *  vẫn phải hiện. */
export function absorbOwnEcho(
  list: ChatMessage[],
  text: string,
  messageId: string | null,
): ChatMessage[] | null {
  const want = normText(text);
  const i = list.findIndex((m) => m.echoPending && !m.messageId && normText(m.text) === want);
  if (i < 0) return null;
  const out = list.slice();
  out[i] = { ...list[i], messageId, echoPending: false, sendState: "sent" };
  return out;
}

/** Một dòng trong màn ca admin: bản đã lưu (REST) hoặc bản realtime / đang gửi. `at` = ISO thời điểm. */
export type AdminMsg = Trackable & { key: string; sender: string; content: string; at: string };

/** Admin (FE-01.1): tin đã lưu (REST — nạp lại mỗi lần mở trang và mỗi lần socket nhận `system`, tức đã gắn hub) +
 *  phần realtime CHƯA có trong đó. Chống trùng bằng message_id (frame hub, ack) và client_msg_id (tin admin gửi). */
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

/** Admin (FE-01.4): frame hub `message` → danh sách live mới. Frame mang client_msg_id của một bong bóng tab này đang
 *  theo dõi = tiếng vọng tin CHÍNH mình gửi (lưu xong SAU khi quá hạn ack đã ép nối lại → tới socket MỚI) → bong bóng
 *  đó "đã gửi" + message_id của frame, KHÔNG thêm bong bóng thứ hai (một bản "Chưa gửi được · Gửi lại" dễ làm admin gõ
 *  lại → khách nhận trùng). Không khớp (tin khách / AI, tin admin gõ ở tab khác) → thêm như thường, chống trùng theo
 *  message_id. */
export function absorbAdminEcho(list: AdminMsg[], item: AdminMsg, cid: string | null): AdminMsg[] {
  if (cid && list.some((m) => m.clientMsgId === cid)) return markSent(list, cid, item.messageId);
  return appendUnique(list, item);
}
