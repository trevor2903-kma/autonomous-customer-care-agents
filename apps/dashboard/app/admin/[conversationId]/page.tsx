"use client";

import Link from "next/link";
import { useEffect, useMemo, useRef, useState } from "react";
import { useQueryClient, useQuery } from "@tanstack/react-query";
import type { AdminConversation } from "shared-types";
import {
  adminWsUrl,
  approveDraft,
  getAdminConversation,
  rejectDraft,
  resolveConversation,
  takeoverConversation,
} from "@/lib/api";
import { ApprovalPanel } from "@/components/admin/ApprovalPanel";
import { EscalationCardPanel } from "@/components/admin/EscalationCardPanel";
import { StatusPill } from "@/components/admin/StatusPill";

// Màn chi tiết admin (08b/08c/08a): EscalationCard + lịch sử + tiếp quản TƯỜNG MINH + trả lời + duyệt nháp.
// MỞ = CHỈ XEM (fix 08c): ca vẫn nằm trong hàng đợi cho tới khi bấm "Tiếp quản".

type Msg = { sender: string; content: string; time: string };

const hhmm = (iso?: string) =>
  new Date(iso ?? Date.now()).toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" });

function initials(s?: string | null): string {
  const t = (s ?? "").replace(/[^a-zA-Z0-9]/g, "");
  return (t.slice(0, 2) || "KH").toUpperCase();
}

function Bubble({ sender, content, time }: Msg) {
  if (sender === "system") {
    return (
      <div className="flex justify-center">
        <div className="rounded-[9px] border border-terracotta-line bg-terracotta-soft px-3.5 py-[7px] text-xs text-terracotta-ink">
          {content}
        </div>
      </div>
    );
  }
  const isCustomer = sender === "customer";
  const isAdmin = sender === "admin";
  const label = isCustomer ? "Khách" : isAdmin ? "Bạn (CSKH)" : "Trợ lý AI";
  return (
    <div className={`flex flex-col gap-[5px] ${isCustomer ? "items-start" : "items-end"}`}>
      <span
        className={`px-0.5 text-[11.5px] ${isCustomer ? "text-dim" : isAdmin ? "text-steel" : "text-olive-dark"}`}
      >
        {label} · {time}
      </span>
      <div
        className={`max-w-[72%] px-[15px] py-[11px] text-[14.5px] leading-[1.55] ${
          isCustomer
            ? "rounded-[5px_15px_15px_15px] border border-line bg-white text-ink"
            : isAdmin
              ? "rounded-[15px_15px_5px_15px] border border-steel-line bg-steel-soft text-ink"
              : "rounded-[15px_15px_5px_15px] border border-line-olive bg-olive-soft text-ink"
        }`}
      >
        {content}
      </div>
    </div>
  );
}

export default function AdminConversationPage({ params }: { params: { conversationId: string } }) {
  const id = params.conversationId;
  const qc = useQueryClient();
  const [live, setLive] = useState<Msg[]>([]);
  const [wsStatus, setWsStatus] = useState<string | null>(null);
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const endRef = useRef<HTMLDivElement>(null);

  const { data: conv, isLoading, isError, error } = useQuery<AdminConversation, Error>({
    queryKey: ["admin-conv", id],
    queryFn: () => getAdminConversation(id),
    staleTime: Infinity, // lịch sử nạp 1 lần, tin mới đến qua WS (tránh trùng)
    refetchOnWindowFocus: false,
  });

  const status = wsStatus ?? conv?.status ?? null;
  const isHandling = status === "HUMAN_HANDLING";
  const isPending = status === "PENDING_APPROVAL";

  useEffect(() => {
    const ws = new WebSocket(adminWsUrl(id));
    wsRef.current = ws;
    ws.onmessage = (ev) => {
      try {
        const d = JSON.parse(ev.data);
        if (d.type === "system") setWsStatus(d.status ?? null);
        else if (d.type === "message")
          setLive((p) => [...p, { sender: d.from, content: String(d.content), time: hhmm() }]);
      } catch {
        /* bỏ qua frame không hợp lệ */
      }
    };
    return () => ws.close();
  }, [id]);

  const messages: Msg[] = useMemo(
    () => [
      ...(conv?.messages ?? []).map((m) => ({
        sender: m.sender,
        content: m.content,
        time: hhmm(m.created_at),
      })),
      ...live,
    ],
    [conv?.messages, live],
  );

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages.length]);

  async function act(fn: () => Promise<unknown>, next?: string) {
    setBusy(true);
    try {
      await fn();
      if (next) setWsStatus(next);
      qc.invalidateQueries({ queryKey: ["conversations"] });
      qc.invalidateQueries({ queryKey: ["escalations"] });
    } finally {
      setBusy(false);
    }
  }

  function sendReply() {
    const text = draft.trim();
    if (!text || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;
    wsRef.current.send(text);
    setLive((p) => [...p, { sender: "admin", content: text, time: hhmm() }]);
    setDraft("");
  }

  return (
    <div className="flex min-h-0 flex-1 flex-col overflow-hidden">
      <header className="flex flex-none items-center justify-between gap-4 border-b border-line bg-white px-[26px] py-4 mob:px-4">
        <div className="flex min-w-0 items-center gap-3">
          <Link
            href="/admin"
            className="hidden h-9 w-9 flex-none items-center justify-center rounded-[9px] border border-line bg-white text-lg text-ink-2 mob:flex"
            aria-label="Quay lại danh sách"
          >
            ‹
          </Link>
          <span className="flex h-[38px] w-[38px] flex-none items-center justify-center rounded-[10px] border border-line bg-cream text-[13px] font-semibold text-muted">
            {initials(conv?.customer_identifier)}
          </span>
          <div className="min-w-0">
            <div className="truncate text-[15px] font-semibold text-ink">
              {conv?.customer_identifier || `Khách ${id.slice(0, 6)}`}
            </div>
            <div className="truncate text-xs text-faint">khách · {id.slice(0, 8)}</div>
          </div>
        </div>
        <div className="flex flex-none items-center gap-2">
          <StatusPill status={status} size="md" />
          {status !== "RESOLVED" && (
            <button
              onClick={() => act(() => resolveConversation(id), "RESOLVED")}
              disabled={busy}
              className="whitespace-nowrap rounded-[8px] border border-line bg-white px-3 py-1.5 text-[13px] text-muted hover:bg-cream disabled:opacity-50 mob:hidden"
            >
              Đóng ca
            </button>
          )}
        </div>
      </header>

      <div className="flex flex-1 flex-col gap-4 overflow-y-auto bg-panel px-[26px] py-6 mob:px-4">
        {isLoading && <p className="text-sm text-dim">Đang tải hội thoại…</p>}
        {isError && <p className="text-sm text-terracotta">Lỗi: {error.message}</p>}

        {conv?.escalation_card && (status === "IN_HUMAN_QUEUE" || isPending) && (
          <EscalationCardPanel card={conv.escalation_card} identifier={conv.customer_identifier} />
        )}

        {isPending && conv?.escalation_card?.suggested_reply && (
          <ApprovalPanel
            draft={conv.escalation_card.suggested_reply}
            busy={busy}
            onApprove={(content) => act(() => approveDraft(id, content), "REPLIED")}
            onReject={() => act(() => rejectDraft(id), "IN_HUMAN_QUEUE")}
          />
        )}

        <div className="flex flex-col gap-[18px]">
          {messages.map((m, i) => (
            <Bubble key={i} {...m} />
          ))}
          <div ref={endRef} />
        </div>
      </div>

      <footer className="flex-none border-t border-line bg-white px-[26px] py-3.5 mob:px-4">
        <div className="mb-2.5 flex flex-wrap items-center gap-2.5">
          {isHandling ? (
            <div className="flex flex-1 items-center gap-2 rounded-lg border border-steel-line bg-steel-soft px-3 py-[7px] text-xs text-steel">
              <span className="h-1.5 w-1.5 flex-none rounded-full bg-steel" />
              AI đã tạm dừng cho hội thoại này — bạn đang trực tiếp trả lời khách.
            </div>
          ) : (
            <>
              <button
                onClick={() => act(() => takeoverConversation(id), "HUMAN_HANDLING")}
                disabled={busy || status === "RESOLVED"}
                className="rounded-[9px] bg-olive px-[18px] py-2.5 text-sm font-semibold text-white hover:bg-olive-dark disabled:opacity-50"
              >
                Tiếp quản
              </button>
              <span className="flex-1 text-xs text-faint">
                Đang ở chế độ xem — ca vẫn nằm trong hàng đợi cho tới khi bạn tiếp quản.
              </span>
            </>
          )}
          {/* Mobile: "Đóng ca" chuyển xuống đây vì header hẹp (tên khách bị cắt nếu nhồi thêm nút). */}
          {status !== "RESOLVED" && (
            <button
              onClick={() => act(() => resolveConversation(id), "RESOLVED")}
              disabled={busy}
              className="hidden whitespace-nowrap rounded-[8px] border border-line bg-white px-3 py-2 text-[13px] text-muted disabled:opacity-50 mob:inline-flex"
            >
              Đóng ca
            </button>
          )}
        </div>

        <div className="flex items-center gap-2.5 rounded-[12px] border border-line bg-cream-soft py-[7px] pl-4 pr-[7px]">
          <input
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") sendReply();
            }}
            disabled={!isHandling}
            placeholder={isHandling ? "Nhập trả lời gửi tới khách…" : "Tiếp quản để trả lời khách"}
            aria-label="Nội dung trả lời khách"
            className="flex-1 border-none bg-transparent text-[14.5px] text-ink outline-none placeholder:text-dim disabled:cursor-not-allowed"
          />
          <button
            onClick={sendReply}
            disabled={!isHandling || !draft.trim()}
            className="rounded-[8px] bg-ink px-[18px] py-[9px] text-[13.5px] font-semibold text-ink-paper hover:bg-ink-2 disabled:opacity-50"
          >
            Gửi
          </button>
        </div>
      </footer>
    </div>
  );
}
