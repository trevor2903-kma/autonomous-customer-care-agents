"use client";

import { useEffect, useRef, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { ChatHeader } from "@/components/chat/ChatHeader";
import { ChatWindow, type ChatMessage } from "@/components/chat/ChatWindow";
import { MessageInput } from "@/components/chat/MessageInput";
import { QuickReplies } from "@/components/chat/QuickReplies";
import { CUST_PLACEHOLDER, custStatusFrom, type CustStatus } from "@/components/chat/custStatus";
import { RequireAuth } from "@/components/auth/RequireAuth";
import { chatWsUrl, getMyThread, getToken } from "@/lib/api";

// Cổng chat khách (PRD §6, §16). Câu trả lời tự động CHỈ đến từ Response Generator (§7.4);
// tin nhân viên tới qua hub sau khi admin tiếp quản.
//
// "Đang chờ nhân viên" bám TÍN HIỆU THẬT (`type:"handoff"` = Agent 3 đã chuyển người), KHÔNG dò chữ trong
// câu trả lời: một câu auto_reply có nhắc "nhân viên hỗ trợ" KHÔNG có nghĩa ca đã được chuyển — dò chữ làm
// khách thấy "đang chờ nhân viên" trong khi AI vẫn đang trả lời bình thường.
const now = () => new Date().toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" });

// Map tin trong mạch ghép (lịch sử) → bong bóng khách. Trạng thái lúc nạp lại lấy từ `thread.active_status`.
function threadFrom(sender: string): ChatMessage["from"] {
  if (sender === "customer") return "you";
  if (sender === "admin") return "admin";
  return "ai";
}
const timeOf = (iso: string) =>
  new Date(iso).toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" });

function ChatInner() {
  const [connected, setConnected] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [typing, setTyping] = useState(false);
  const [status, setStatus] = useState<CustStatus>("ai");
  const wsRef = useRef<WebSocket | null>(null);
  const idRef = useRef(0);
  const seededRef = useRef(false);

  const push = (m: Omit<ChatMessage, "id" | "time">) =>
    setMessages((prev) => [...prev, { ...m, id: idRef.current++, time: now() }]);

  // Mạch ghép của khách (P2/P6): nạp lịch sử xuyên ca MỘT LẦN → render một đoạn liền mạch.
  const { data: thread } = useQuery({
    queryKey: ["me-thread"],
    queryFn: getMyThread,
    refetchOnWindowFocus: false,
  });

  useEffect(() => {
    if (!thread || seededRef.current) return;
    seededRef.current = true;
    const seeded: ChatMessage[] = thread.messages.map((m) => ({
      id: idRef.current++,
      from: threadFrom(m.sender),
      text: m.content,
      time: timeOf(m.created_at),
    }));
    // Ghép lịch sử TRƯỚC tin realtime lỡ tới trong lúc tải (giữ thứ tự: cũ → mới).
    setMessages((live) => [...seeded, ...live]);
    setStatus(custStatusFrom(thread.active_status));
  }, [thread]);

  useEffect(() => {
    const token = getToken();
    if (!token) return;
    const ws = new WebSocket(chatWsUrl(token));
    wsRef.current = ws;
    ws.onopen = () => setConnected(true);
    ws.onclose = () => {
      setConnected(false);
      setTyping(false); // rớt kết nối giữa typing→reply → không kẹt "đang trả lời…"
    };
    ws.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data);
        if (data.type === "typing") {
          setTyping(true);
        } else if (data.type === "reply") {
          // Trả lời tự động — LUÔN là bong bóng AI, kể cả khi câu chữ có nhắc tới nhân viên.
          setTyping(false);
          push({ from: "ai", text: String(data.content) });
          setStatus("ai");
        } else if (data.type === "handoff") {
          // Agent 3 đã chuyển người THẬT (ca vào hàng đợi, AI dừng cho hội thoại này).
          setTyping(false);
          push({ from: "system", text: String(data.content) });
          setStatus("waiting");
        } else if (data.type === "pending") {
          // Ca nhạy cảm: nháp đang chờ nhân viên duyệt (08a) — gỡ typing, đổi trạng thái, KHÔNG kẹt chờ.
          setTyping(false);
          setStatus("review");
        } else if (data.type === "message") {
          setTyping(false);
          const isAdmin = data.from === "admin";
          push({ from: isAdmin ? "admin" : "ai", text: String(data.content) });
          if (isAdmin) setStatus("human");
        }
      } catch {
        // Bỏ qua frame không phải JSON hợp lệ.
      }
    };
    return () => ws.close();
  }, []);

  function send(text: string) {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;
    push({ from: "you", text });
    wsRef.current.send(text);
  }

  return (
    // Khoá chiều cao dưới top bar 53px → vùng tin nhắn tự cuộn, ô nhập luôn nằm đáy màn.
    <main className="flex flex-1 min-h-0 w-full justify-center overflow-hidden">
      <div className="flex w-full max-w-[840px] flex-1 flex-col overflow-hidden px-6 mob:px-3.5">
        <div className="flex flex-none flex-col gap-3.5 px-1 pb-4 pt-[22px]">
          <ChatHeader status={status} />
          <QuickReplies disabled={!connected} onPick={send} />
        </div>

        <ChatWindow messages={messages} typing={typing} waiting={status === "waiting"} />

        <MessageInput
          disabled={!connected}
          placeholder={CUST_PLACEHOLDER[status]}
          onSend={send}
        />
      </div>
    </main>
  );
}

export default function ChatPage() {
  return (
    <RequireAuth role="customer">
      <ChatInner />
    </RequireAuth>
  );
}
