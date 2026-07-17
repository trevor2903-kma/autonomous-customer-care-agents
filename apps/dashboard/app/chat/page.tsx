"use client";

import { useEffect, useRef, useState } from "react";
import { ChatWindow, type ChatMessage } from "@/components/chat/ChatWindow";
import { Header } from "@/components/chat/Header";
import { MessageInput } from "@/components/chat/MessageInput";
import { WS_URL } from "@/lib/api";

// Cổng chat khách (PRD §6, §16): Header · ChatWindow · MessageInput nối WebSocket.
// Mỗi tin khách chạy ĐỦ pipeline ở backend; câu trả lời tới khách CHỈ đến từ Response Generator (PRD §7.4).
export default function ChatPage() {
  const [connected, setConnected] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [typing, setTyping] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const idRef = useRef(0);

  const push = (m: Omit<ChatMessage, "id">) =>
    setMessages((prev) => [...prev, { ...m, id: idRef.current++ }]);

  useEffect(() => {
    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;
    ws.onopen = () => setConnected(true);
    ws.onclose = () => {
      setConnected(false);
      setTyping(false); // rớt kết nối giữa typing→reply -> gỡ indicator "đang trả lời…" (không kẹt)
    };
    ws.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data);
        if (data.type === "system") {
          push({ from: "system", text: String(data.message) });
        } else if (data.type === "typing") {
          setTyping(true); // hiện "đang trả lời…"
        } else if (data.type === "reply") {
          setTyping(false);
          push({ from: "ai", text: String(data.content) });
        } else if (data.type === "message") {
          // Tin từ nhân viên (admin đã tiếp quản) — realtime qua hub. Gỡ typing nếu còn.
          setTyping(false);
          push({ from: data.from === "admin" ? "admin" : "ai", text: String(data.content) });
        }
      } catch {
        // Bỏ qua frame không phải JSON hợp lệ.
      }
    };
    return () => ws.close();
  }, []);

  function send(text: string) {
    push({ from: "you", text });
    wsRef.current?.send(text);
  }

  return (
    <main className="mx-auto flex h-screen max-w-2xl flex-col border-x border-neutral-200 bg-neutral-50">
      <Header connected={connected} />
      <ChatWindow messages={messages} typing={typing} />
      <MessageInput disabled={!connected} onSend={send} />
    </main>
  );
}
