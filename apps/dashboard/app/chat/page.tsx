"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { ChatHeader } from "@/components/chat/ChatHeader";
import { ChatWindow, type ChatMessage } from "@/components/chat/ChatWindow";
import { MessageInput } from "@/components/chat/MessageInput";
import { QuickReplies } from "@/components/chat/QuickReplies";
import { CUST_PLACEHOLDER, custStatusFrom, type CustStatus } from "@/components/chat/custStatus";
import { RequireAuth } from "@/components/auth/RequireAuth";
import { type CustomerThread, chatWsUrl, getMyThread, getToken } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { appendUnique, markFailed, markSending, markSent, reconcileThread } from "@/lib/messageMerge";
import { ACK_TIMEOUT_MS, type Frame, asString, newClientMsgId } from "@/lib/realtime";
import { useReconnectingSocket } from "@/lib/useReconnectingSocket";

// Cổng chat khách (PRD §6, §16). Câu trả lời tự động CHỈ đến từ Response Generator (§7.4);
// tin nhân viên tới qua hub sau khi admin tiếp quản.
//
// "Đang chờ nhân viên" bám TÍN HIỆU THẬT (`type:"handoff"` = Agent 3 đã chuyển người), KHÔNG dò chữ trong
// câu trả lời: một câu auto_reply có nhắc "nhân viên hỗ trợ" KHÔNG có nghĩa ca đã được chuyển — dò chữ làm
// khách thấy "đang chờ nhân viên" trong khi AI vẫn đang trả lời bình thường.
//
// Bền kết nối (protocol v2 — contract §4.1): socket tự nối lại; mỗi tin mang `client_msg_id` với vòng đời
// đang gửi → đã gửi (ack) → chưa gửi được (quá 10 s / frame error) + "Gửi lại" cùng id. Nối lại → nạp lại
// /me/thread rồi ghép theo message_id / client_msg_id: không mất tin, không trùng tin.
const now = () => new Date().toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" });
const timeOf = (iso: string) =>
  new Date(iso).toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" });

// Server từ chối vì gửi quá nhanh (`error/rate_limited`) — thông báo TẠM phía khách, không lưu DB.
const RATE_LIMIT_NOTICE = "Bạn đang gửi hơi nhanh — vui lòng đợi giây lát rồi bấm “Gửi lại”.";

function ChatInner() {
  const { user } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [typing, setTyping] = useState(false);
  const [status, setStatus] = useState<CustStatus>("ai");
  const idRef = useRef(0);
  const seededRef = useRef(false);
  const messagesRef = useRef(messages);
  messagesRef.current = messages;
  // Hẹn giờ ack theo client_msg_id. `genRef` = thế hệ socket (+1 mỗi lần mở): quá hạn ack của tin gửi trên
  // socket CŨ chỉ đánh dấu "chưa gửi được", KHÔNG ép nối lại socket MỚI.
  const ackTimers = useRef(new Map<string, ReturnType<typeof setTimeout>>());
  const genRef = useRef(0);
  const wsUrl = useMemo(() => {
    const token = getToken();
    return token ? chatWsUrl(token) : null;
  }, []);

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
    setStatus(custStatusFrom(t.active_status));
  }

  useEffect(() => {
    if (!thread || seededRef.current) return;
    applyThread(thread);
  }, [thread]);

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
    switch (f.type) {
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
      case "typing":
        setTyping(true);
        break;
      case "reply":
        // Trả lời tự động — LUÔN là bong bóng AI, kể cả khi câu chữ có nhắc tới nhân viên.
        setTyping(false);
        push({ from: "ai", text, messageId });
        setStatus("ai");
        break;
      case "handoff":
        // Agent 3 đã chuyển người THẬT (ca vào hàng đợi, AI dừng cho hội thoại này).
        setTyping(false);
        push({ from: "system", text, messageId });
        setStatus("waiting");
        break;
      case "pending":
        // Ca nhạy cảm: nháp đang chờ nhân viên duyệt (08a) — gỡ typing, đổi trạng thái, KHÔNG kẹt chờ.
        setTyping(false);
        setStatus("review");
        break;
      case "status":
        // Trạng thái ca đổi do người khác (admin tiếp quản/đóng/duyệt/từ chối, tự đóng, tab khác) HOẶC lượt
        // của chính tab này bị huỷ vì trạng thái đổi giữa chừng → không còn reply nào theo sau: gỡ typing.
        setTyping(false);
        setStatus(custStatusFrom(asString(f.status)));
        break;
      case "message":
        if (f.from === "customer") {
          // Tin của CHÍNH khách gõ ở tab/thiết bị khác (FE-01.6) → bong bóng "bạn", KHÔNG phải AI.
          push({ from: "you", text, messageId });
        } else if (f.from === "admin") {
          setTyping(false);
          push({ from: "admin", text, messageId });
          setStatus("human");
        } else {
          // AI qua hub: nháp vừa được duyệt, tin nhắc/đóng tự động, trả lời của lượt mà socket cũ đã rớt.
          setTyping(false);
          push({ from: "ai", text, messageId });
          setStatus((s) => (s === "review" ? "ai" : s)); // nháp đã tới khách → hết "đang kiểm tra" (UX-02.3)
        }
        break;
    }
  }

  function onOpen(isReconnect: boolean) {
    genRef.current += 1;
    if (!isReconnect) return;
    // Nối lại: nạp lại mạch từ DB rồi dựng lại danh sách — tin mình đã lưu thành "đã gửi", tin còn "đang gửi"
    // gửi lại MỘT lần (cùng client_msg_id → server không chạy lại lượt), tin "chưa gửi được" chờ khách bấm.
    void refetch().then(({ data }) => {
      if (!data) return;
      const saved = new Set(data.messages.map((m) => m.client_msg_id).filter(Boolean));
      applyThread(data);
      for (const m of messagesRef.current) {
        if (m.from === "you" && m.sendState === "sending" && m.clientMsgId && !saved.has(m.clientMsgId)) {
          transmit(m.clientMsgId, m.text);
        }
      }
    });
  }

  const socket = useReconnectingSocket(wsUrl, {
    onFrame,
    onOpen,
    onDown: () => setTyping(false), // rớt kết nối giữa typing→reply → không kẹt "đang trả lời…"
  });
  const online = socket.state === "online";
  // Lượt đang chạy (đang trả lời / tin chưa có ack) → khoá gợi ý nhanh: bấm liên tiếp không đẻ lượt trùng.
  const busy = typing || messages.some((m) => m.sendState === "sending");

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
