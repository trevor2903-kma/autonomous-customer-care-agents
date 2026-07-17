"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import type { AdminConversation, EscalationCard } from "shared-types";
import { API_BASE, adminWsUrl, approveDraft, getAdminConversation, rejectDraft } from "@/lib/api";
import { Badge } from "@/components/rag/ClassifyTester";

// Màn admin tiếp quản (08c, PRD §11/§17): lịch sử (REST) + EscalationCard + chat realtime 2 chiều với khách (WS).
// Takeover TỰ ĐỘNG khi mở kết nối WS (→ HUMAN_HANDLING). Tin admin = egress-người (TÁCH khỏi Response Generator).

type LiveMsg = { sender: "customer" | "ai" | "admin"; content: string };

function CardPanel({ card }: { card: EscalationCard }) {
  return (
    <aside className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm">
      <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-amber-700">EscalationCard</div>
      <div className="flex flex-wrap gap-2">
        {card.intent && <Badge label={`intent: ${card.intent}`} tone="blue" />}
        {card.priority && <Badge label={`priority: ${card.priority}`} tone="amber" />}
        {card.severity && <Badge label={`severity: ${card.severity}`} />}
      </div>
      <p className="mt-2">
        <span className="text-neutral-500">Tin khách: </span>
        {card.summary || "—"}
      </p>
      {card.escalation_reason && (
        <p className="mt-1 text-xs text-amber-700">
          Lý do: <code>{card.escalation_reason}</code>
        </p>
      )}
      {card.rag_context.length > 0 && (
        <div className="mt-2">
          <div className="text-xs font-semibold uppercase tracking-wide text-neutral-500">Nguồn tri thức</div>
          <ul className="mt-1 space-y-1">
            {card.rag_context.map((c, i) => (
              <li key={i} className="text-xs text-neutral-600">
                <code>{c.source}</code> · {c.snippet}
              </li>
            ))}
          </ul>
        </div>
      )}
    </aside>
  );
}

function Bubble({ sender, content }: LiveMsg) {
  const align = sender === "admin" ? "items-end" : "items-start";
  const color =
    sender === "admin"
      ? "bg-emerald-600 text-white"
      : sender === "ai"
        ? "bg-blue-50 text-blue-900 border border-blue-100"
        : "bg-white text-neutral-800 border border-neutral-200";
  const label = sender === "admin" ? "Bạn (admin)" : sender === "ai" ? "AI" : "Khách";
  return (
    <div className={`flex flex-col ${align}`}>
      <span className="mb-0.5 text-[10px] text-neutral-400">{label}</span>
      <span className={`max-w-[75%] rounded-2xl px-3 py-2 text-sm ${color}`}>{content}</span>
    </div>
  );
}

export default function AdminConversationPage({ params }: { params: { conversationId: string } }) {
  const id = params.conversationId;
  const { data: conv, isLoading, isError, error } = useQuery<AdminConversation, Error>({
    queryKey: ["admin-conv", id],
    queryFn: () => getAdminConversation(id),
    staleTime: Infinity, // lịch sử nạp 1 lần; tin mới đến qua WS (tránh trùng)
    refetchOnWindowFocus: false,
  });
  const [live, setLive] = useState<LiveMsg[]>([]);
  const [connected, setConnected] = useState(false);
  const [status, setStatus] = useState<string | null>(null);
  const [draft, setDraft] = useState("");
  const [draftEdit, setDraftEdit] = useState(""); // nháp AI để duyệt/sửa (PENDING_APPROVAL)
  const wsRef = useRef<WebSocket | null>(null);
  const effectiveStatus = status ?? conv?.status ?? null;

  useEffect(() => {
    const ws = new WebSocket(adminWsUrl(id));
    wsRef.current = ws;
    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onmessage = (ev) => {
      try {
        const d = JSON.parse(ev.data);
        if (d.type === "system") setStatus(d.status ?? null);
        else if (d.type === "message") setLive((p) => [...p, { sender: d.from, content: String(d.content) }]);
      } catch {
        /* bỏ qua frame không hợp lệ */
      }
    };
    return () => ws.close();
  }, [id]);

  useEffect(() => {
    const sr = conv?.escalation_card?.suggested_reply;
    if (sr) setDraftEdit(sr); // seed textarea duyệt bằng nháp Agent 4
  }, [conv?.escalation_card?.suggested_reply]);

  async function onApprove() {
    await approveDraft(id, draftEdit.trim() || undefined);
    setStatus("REPLIED"); // nháp đã duyệt → khách nhận qua hub (hub_listener tự append)
  }

  async function onReject() {
    await rejectDraft(id);
    setStatus("IN_HUMAN_QUEUE"); // từ chối → admin tự tiếp quản/chat
  }

  function send() {
    const text = draft.trim();
    if (!text || !wsRef.current) return;
    wsRef.current.send(text);
    setLive((p) => [...p, { sender: "admin", content: text }]); // optimistic (server KHÔNG echo lại)
    setDraft("");
  }

  async function resolve() {
    await fetch(`${API_BASE}/api/admin/conversations/${id}/resolve`, { method: "POST" });
    setStatus("RESOLVED");
  }

  return (
    <main className="mx-auto max-w-3xl px-6 py-8">
      <header className="mb-4 flex flex-wrap items-center justify-between gap-2">
        <div>
          <h1 className="text-xl font-semibold">Tiếp quản hội thoại</h1>
          <p className="text-xs text-neutral-500">
            {connected ? "● đã kết nối" : "○ mất kết nối"} · trạng thái: {status ?? conv?.status ?? "…"}
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={resolve}
            className="rounded-md border border-neutral-300 px-3 py-1.5 text-sm hover:bg-neutral-100"
          >
            Đóng ca
          </button>
          <Link
            href="/admin"
            className="rounded-md border border-neutral-300 px-3 py-1.5 text-sm hover:bg-neutral-100"
          >
            ← Hàng đợi
          </Link>
        </div>
      </header>

      {isLoading && <p className="text-sm text-neutral-400">Đang tải hội thoại…</p>}
      {isError && <p className="text-sm text-red-500">Lỗi: {error.message}</p>}

      {conv?.escalation_card && (
        <div className="mb-4">
          <CardPanel card={conv.escalation_card} />
        </div>
      )}

      {effectiveStatus === "PENDING_APPROVAL" && (
        <div className="mb-4 rounded-lg border border-emerald-300 bg-emerald-50 p-4">
          <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-emerald-700">
            Nháp AI chờ duyệt (ca nhạy cảm)
          </div>
          <textarea
            value={draftEdit}
            onChange={(e) => setDraftEdit(e.target.value)}
            rows={3}
            className="w-full rounded-md border border-emerald-200 bg-white px-3 py-2 text-sm"
          />
          <div className="mt-2 flex flex-wrap gap-2">
            <button
              onClick={onApprove}
              disabled={!draftEdit.trim()}
              className="rounded-md bg-emerald-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-emerald-700 disabled:opacity-50"
            >
              Duyệt &amp; gửi
            </button>
            <button
              onClick={onReject}
              className="rounded-md border border-neutral-300 px-3 py-1.5 text-sm hover:bg-neutral-100"
            >
              Từ chối (tự xử lý)
            </button>
          </div>
        </div>
      )}

      <div className="flex h-[60vh] flex-col rounded-lg border border-neutral-200 bg-neutral-50">
        <div className="flex-1 space-y-2 overflow-y-auto p-4">
          {conv?.messages.map((m) => (
            <Bubble key={m.id} sender={m.sender as LiveMsg["sender"]} content={m.content} />
          ))}
          {live.map((m, i) => (
            <Bubble key={`live-${i}`} sender={m.sender} content={m.content} />
          ))}
        </div>
        <div className="flex gap-2 border-t border-neutral-200 p-3">
          <input
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") send();
            }}
            placeholder="Nhập tin trả lời khách…"
            disabled={!connected}
            className="min-w-0 flex-1 rounded-md border border-neutral-300 px-3 py-2 text-sm disabled:bg-neutral-100"
          />
          <button
            onClick={send}
            disabled={!connected || !draft.trim()}
            className="rounded-md bg-neutral-900 px-4 py-2 text-sm font-medium text-white hover:bg-neutral-700 disabled:opacity-50"
          >
            Gửi
          </button>
        </div>
      </div>
    </main>
  );
}
