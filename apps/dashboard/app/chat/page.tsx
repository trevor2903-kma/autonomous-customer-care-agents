"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { ChatHeader } from "@/components/chat/ChatHeader";
import { ChatWindow, type ChatMessage } from "@/components/chat/ChatWindow";
import { MessageInput } from "@/components/chat/MessageInput";
import { QuickReplies } from "@/components/chat/QuickReplies";
import {
  CUST_PLACEHOLDER,
  CUST_TURN_IDLE,
  type CustTurn,
  custStatusFrom,
  custTurnAfter,
} from "@/components/chat/custStatus";
import { RequireAuth } from "@/components/auth/RequireAuth";
import { type CustomerThread, chatWsUrl, getMyThread, getToken } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import {
  absorbOwnById,
  absorbOwnEcho,
  appendUnique,
  markEchoPending,
  markFailed,
  markSending,
  markSent,
  reconcileThread,
  unconfirmedOwn,
} from "@/lib/messageMerge";
import { ACK_TIMEOUT_MS, TURN_STALL_MS, type Frame, asString, newClientMsgId } from "@/lib/realtime";
import { useReconnectingSocket } from "@/lib/useReconnectingSocket";

// Cổng chat khách (PRD §6, §16). Câu trả lời tự động CHỈ đến từ Response Generator (§7.4);
// tin nhân viên tới qua hub sau khi admin tiếp quản.
//
// "Đang chờ nhân viên" bám TÍN HIỆU THẬT (`type:"handoff"` = Agent 3 đã chuyển người), KHÔNG dò chữ trong
// câu trả lời: một câu auto_reply có nhắc "nhân viên hỗ trợ" KHÔNG có nghĩa ca đã được chuyển — dò chữ làm
// khách thấy "đang chờ nhân viên" trong khi AI vẫn đang trả lời bình thường.
//
// Bền kết nối (protocol v2 — contract §4.1): socket tự nối lại; mỗi tin mang `client_msg_id` với vòng đời
// đang gửi → đã gửi (ack) → chưa gửi được (quá 10 s / frame error) + "Gửi lại" cùng id. Mỗi lần server báo `system`
// (socket đã gắn hub — cả lần nối đầu) → nạp lại /me/thread rồi ghép theo message_id / client_msg_id: không mất tin,
// không trùng tin.
const now = () => new Date().toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" });
const timeOf = (iso: string) =>
  new Date(iso).toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" });

// Server từ chối vì gửi quá nhanh (`error/rate_limited`) — thông báo TẠM phía khách, không lưu DB.
const RATE_LIMIT_NOTICE = "Bạn đang gửi hơi nhanh — vui lòng đợi giây lát rồi bấm “Gửi lại”.";

// URL socket kèm token HIỆN TẠI trong localStorage — dựng lại ở MỖI lần nối (`resolveUrl`, FE-01.2): sau 4401 mà phiên
// vẫn còn (đăng nhập lại ở tab khác) lần thử lại dùng token mới.
function currentChatWsUrl(): string | null {
  const token = getToken();
  return token ? chatWsUrl(token) : null;
}

function ChatInner() {
  const { user } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  // Header (status) + "đang trả lời…" (typing) + số tin mà lượt CHƯA xong (inFlight) — suy từ frame server qua
  // `custTurnAfter` (thuần, có test).
  const [turn, setTurn] = useState<CustTurn>(CUST_TURN_IDLE);
  const { status, typing } = turn;
  const idRef = useRef(0);
  const seededRef = useRef(false);
  const messagesRef = useRef(messages);
  messagesRef.current = messages;
  // Hẹn giờ ack theo client_msg_id. `genRef` = thế hệ socket (+1 mỗi lần mở): quá hạn ack của tin gửi trên
  // socket CŨ chỉ đánh dấu "chưa gửi được", KHÔNG ép nối lại socket MỚI.
  const ackTimers = useRef(new Map<string, ReturnType<typeof setTimeout>>());
  const genRef = useRef(0);
  const wsUrl = useMemo(currentChatWsUrl, []);

  const nextId = () => idRef.current++;
  const push = (m: Omit<ChatMessage, "id" | "time">) => {
    const item: ChatMessage = { ...m, id: nextId(), time: now() };
    setMessages((prev) => appendUnique(prev, item));
  };

  // Mạch ghép của khách (P2/P6): lịch sử xuyên ca → render một đoạn liền mạch.
  const { data: thread, refetch } = useQuery({
    queryKey: ["me-thread", user?.id],
    queryFn: getMyThread,
    refetchOnWindowFocus: false,
  });

  // Ghép lịch sử TRƯỚC tin realtime lỡ tới trong lúc tải (giữ thứ tự: cũ → mới), chống trùng theo id.
  function applyThread(t: CustomerThread) {
    seededRef.current = true;
    setMessages((prev) => reconcileThread(prev, t.messages, nextId, timeOf));
    setTurn((s) => ({ ...s, status: custStatusFrom(t.active_status) }));
  }

  useEffect(() => {
    if (!thread || seededRef.current) return;
    applyThread(thread);
  }, [thread]);

  // Khoá gợi ý nhanh không được kẹt: tin đã gửi mà quá TURN_STALL_MS không có tiến triển nào (typing / kết quả).
  useEffect(() => {
    if (turn.inFlight === 0 || turn.typing) return;
    const timer = setTimeout(() => setTurn((s) => ({ ...s, inFlight: 0 })), TURN_STALL_MS);
    return () => clearTimeout(timer);
  }, [turn]);

  const clearAck = (cid: string) => {
    const t = ackTimers.current.get(cid);
    if (t !== undefined) clearTimeout(t);
    ackTimers.current.delete(cid);
  };

  useEffect(() => {
    const timers = ackTimers.current;
    return () => timers.forEach((t) => clearTimeout(t));
  }, []);

  // Gửi (hoặc gửi lại — CÙNG client_msg_id) một tin rồi chờ ack.
  function transmit(cid: string, text: string) {
    clearAck(cid);
    setMessages((prev) => markSending(prev, cid));
    if (!socket.send({ type: "message", content: text, client_msg_id: cid })) {
      setMessages((prev) => markFailed(prev, cid));
      return;
    }
    setTurn((s) => ({ ...s, inFlight: s.inFlight + 1 })); // lượt của tin này chưa xong → khoá gợi ý nhanh
    const gen = genRef.current;
    ackTimers.current.set(
      cid,
      setTimeout(() => {
        ackTimers.current.delete(cid);
        setMessages((prev) => markFailed(prev, cid));
        // Socket đã nhận tin vẫn là socket hiện tại mà không ack → nghi half-open: bỏ và nối lại.
        if (gen === genRef.current) socket.reconnect();
      }, ACK_TIMEOUT_MS),
    );
  }

  function notice(text: string) {
    const item: ChatMessage = { id: nextId(), from: "system", text, time: now() };
    setMessages((prev) => {
      const last = prev[prev.length - 1];
      return last?.from === "system" && last.text === text ? prev : [...prev, item];
    });
  }

  function onFrame(f: Frame) {
    const cid = asString(f.client_msg_id);
    const text = asString(f.content) ?? "";
    const messageId = asString(f.message_id);
    // Header / "đang trả lời…" / lượt đang chạy: MỘT reducer thuần cho mọi frame (UX-02.3, IDEM-XC.1) — `typing`,
    // `pending`, `status` chỉ đổi trạng thái đó, không có bong bóng.
    setTurn((s) => custTurnAfter(s, f));
    switch (f.type) {
      case "system":
        // Server gửi `system` SAU khi đã gắn socket vào hub → đối soát TỪ ĐÂY, không phải lúc bắt tay (`onOpen`): sự
        // kiện phát trước mốc này đã nằm trong /me/thread, sau mốc này tới qua socket — không lọt khe (FE-01.2). Chạy ở
        // MỌI lần nối, kể cả lần đầu (tải lại trang giữa lượt).
        reconcile();
        break;
      case "ack":
        if (cid) {
          clearAck(cid);
          setMessages((prev) => markSent(prev, cid));
        }
        break;
      case "error":
        // Server từ chối tin (không lưu, không xử lý) → bong bóng đó "chưa gửi được".
        if (cid) {
          clearAck(cid);
          setMessages((prev) => markFailed(prev, cid));
        }
        if (f.code === "rate_limited") notice(RATE_LIMIT_NOTICE);
        break;
      case "reply":
        // Trả lời tự động — LUÔN là bong bóng AI, kể cả khi câu chữ có nhắc tới nhân viên.
        push({ from: "ai", text, messageId });
        break;
      case "handoff":
        // Agent 3 đã chuyển người THẬT (ca vào hàng đợi, AI dừng cho hội thoại này).
        push({ from: "system", text, messageId });
        break;
      case "status":
        // status null = server không đọc lại được trạng thái → nạp lại mạch để lấy status thật (reducer giữ nguyên).
        if (typeof f.status !== "string") void refetch().then(({ data }) => data && applyThread(data));
        break;
      case "message":
        if (f.from === "customer") {
          // Tin của CHÍNH khách. Backend kèm client_msg_id → khớp CHÍNH XÁC bong bóng tab này đã gửi (tiếng vọng tin
          // gửi trước lúc nối lại) → gắn message_id vào bong bóng đó; không khớp = tin gõ ở tab/thiết bị khác (FE-01.6)
          // → bong bóng "bạn", KHÔNG phải AI. Frame thiếu client_msg_id (server cũ) mới khớp theo nội dung.
          const item: ChatMessage = { id: nextId(), from: "you", text, time: now(), messageId };
          if (cid) clearAck(cid);
          setMessages(
            (prev) =>
              (cid ? absorbOwnById(prev, cid, messageId) : absorbOwnEcho(prev, text, messageId)) ??
              appendUnique(prev, item),
          );
        } else {
          // Nhân viên, hoặc AI qua hub: nháp vừa được duyệt, tin nhắc/đóng tự động, trả lời của lượt mà socket cũ
          // đã rớt.
          push({ from: f.from === "admin" ? "admin" : "ai", text, messageId });
        }
        break;
    }
  }

  function onOpen() {
    genRef.current += 1; // thế hệ socket; đối soát chờ frame `system` (server đã gắn hub) — xem `reconcile`
  }

  // Đối soát khi server báo `system`: nạp lại mạch từ DB rồi dựng lại danh sách — tin mình đã lưu thành "đã gửi"; tin
  // chưa thấy trong lịch sử ("đang gửi" LẪN "đã gửi" — ack chỉ là biên nhận trước khi lưu) gửi lại MỘT lần cùng
  // client_msg_id (server không chạy lại lượt) và chờ tiếng vọng qua hub; tin "chưa gửi được" chờ khách bấm.
  function reconcile() {
    void refetch().then(({ data }) => {
      if (!data) return;
      const resend = unconfirmedOwn(messagesRef.current, data.messages);
      applyThread(data);
      setMessages((prev) => markEchoPending(prev, new Set(resend.map((r) => r.cid))));
      for (const r of resend) transmit(r.cid, r.text);
    });
  }

  const socket = useReconnectingSocket(wsUrl, {
    authRole: "customer",
    resolveUrl: currentChatWsUrl,
    onFrame,
    onOpen,
    // Rớt kết nối giữa typing→reply → không kẹt "đang trả lời…"; lượt đang chạy tính lại từ các tin gửi lại.
    onDown: () => setTurn((s) => ({ ...s, typing: false, inFlight: 0 })),
  });
  const online = socket.state === "online";
  // Lượt đang chạy (tin đã gửi mà lượt chưa xong — kể cả khe ack→typing / đang trả lời / tin chưa có ack) → khoá gợi
  // ý nhanh: bấm liên tiếp không đẻ lượt trùng (IDEM-XC.1).
  const busy = typing || turn.inFlight > 0 || messages.some((m) => m.sendState === "sending");

  /** true = tin đã vào danh sách (đang gửi / chưa gửi được có "Gửi lại") → ô nhập được phép xoá chữ. */
  function send(text: string): boolean {
    if (!online) return false;
    const cid = newClientMsgId();
    const item: ChatMessage = {
      id: nextId(),
      from: "you",
      text,
      time: now(),
      clientMsgId: cid,
      sendState: "sending",
    };
    setMessages((prev) => [...prev, item]);
    transmit(cid, text);
    return true;
  }

  function retry(cid: string, text: string) {
    if (online) transmit(cid, text);
  }

  return (
    // Khoá chiều cao dưới top bar 53px → vùng tin nhắn tự cuộn, ô nhập luôn nằm đáy màn.
    <main className="flex flex-1 min-h-0 w-full justify-center overflow-hidden">
      <div className="flex w-full max-w-[840px] flex-1 flex-col overflow-hidden px-6 mob:px-3.5">
        <div className="flex flex-none flex-col gap-3.5 px-1 pb-4 pt-[22px]">
          <ChatHeader status={status} conn={socket.state} />
          <QuickReplies disabled={!online || busy} onPick={send} />
        </div>

        <ChatWindow
          messages={messages}
          typing={typing}
          waiting={status === "waiting"}
          onRetry={retry}
          canRetry={online}
        />

        <MessageInput
          disabled={!online}
          placeholder={CUST_PLACEHOLDER[status]}
          onSend={send}
        />
      </div>
    </main>
  );
}

export default function ChatPage() {
  const { user } = useAuth();
  return (
    <RequireAuth role="customer">
      {user && <ChatInner key={user.id} />}
    </RequireAuth>
  );
}
