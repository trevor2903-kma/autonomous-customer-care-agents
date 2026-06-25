"use client";

import { useEffect, useRef, useState } from "react";
import { ChatWindow, type ChatMessage } from "@/components/chat/ChatWindow";
import { Header } from "@/components/chat/Header";
import { MessageInput } from "@/components/chat/MessageInput";
import { WS_URL } from "@/lib/api";

// Cổng chat khách (PRD §6, §16): Header · ChatWindow · MessageInput nối WebSocket.
// SCAFFOLD: chỉ echo — CHƯA wiring AI pipeline. Phản hồi tới khách (khi wiring) sẽ CHỈ đến từ
// Response Generator (PRD §7.4).
export default function ChatPage() {
  const [connected, setConnected] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const wsRef = useRef<WebSocket | null>(null);
  const idRef = useRef(0);

  const push = (m: Omit<ChatMessage, "id">) =>
    setMessages((prev) => [...prev, { ...m, id: idRef.current++ }]);

  useEffect(() => {
    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;
    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data);
        push({ from: data.type === "system" ? "system" : "echo", text: String(data.message) });
      } catch {
        push({ from: "echo", text: String(ev.data) });
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
      <ChatWindow messages={messages} />
      <MessageInput disabled={!connected} onSend={send} />
    </main>
  );
}
