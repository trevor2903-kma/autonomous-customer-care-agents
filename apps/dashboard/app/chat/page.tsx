"use client";

import { useEffect, useRef, useState } from "react";
import { ChatHeader } from "@/components/chat/ChatHeader";
import { ChatWindow, type ChatMessage } from "@/components/chat/ChatWindow";
import { MessageInput } from "@/components/chat/MessageInput";
import { QuickReplies } from "@/components/chat/QuickReplies";
import { CUST_PLACEHOLDER, type CustStatus } from "@/components/chat/custStatus";
import { WS_URL } from "@/lib/api";

// Cổng chat khách (PRD §6, §16). Câu trả lời tự động CHỈ đến từ Response Generator (§7.4);
// tin nhân viên tới qua hub sau khi admin tiếp quản.
//
// Thông báo chuyển người là tin do BE phát (HANDOFF_NOTICE / câu xin lỗi khi pipeline lỗi) — cả hai đều
// mang nghĩa "đang chờ người". Nhận diện theo cụm chung để hiển thị dạng system + trạng thái chờ.
const HANDOFF_HINT = "nhân viên hỗ trợ";

const now = () => new Date().toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" });

export default function ChatPage() {
  const [connected, setConnected] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [typing, setTyping] = useState(false);
  const [status, setStatus] = useState<CustStatus>("ai");
  const wsRef = useRef<WebSocket | null>(null);
  const idRef = useRef(0);

  const push = (m: Omit<ChatMessage, "id" | "time">) =>
    setMessages((prev) => [...prev, { ...m, id: idRef.current++, time: now() }]);

  useEffect(() => {
    const ws = new WebSocket(WS_URL);
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
          setTyping(false);
          const text = String(data.content);
          const handoff = text.toLowerCase().includes(HANDOFF_HINT);
          push({ from: handoff ? "system" : "ai", text });
          setStatus(handoff ? "waiting" : "ai");
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
    <main className="flex min-h-0 w-full flex-1 justify-center overflow-hidden">
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
