"use client";

import Link from "next/link";
import { useEffect, useMemo, useRef, useState } from "react";
import { useQueryClient, useQuery } from "@tanstack/react-query";
import type { AdminConversation } from "shared-types";
import {
  adminWsUrl,
  approveDraft,
  getAdminConversation,
  getToken,
  rejectDraft,
  resolveConversation,
  takeoverConversation,
} from "@/lib/api";
import { useAuth } from "@/lib/auth";
import {
  type AdminMsg,
  appendUnique,
  markFailed,
  markSending,
  markSent,
  mergeAdminMessages,
} from "@/lib/messageMerge";
import { ACK_TIMEOUT_MS, type Frame, asString, convStateOf, newClientMsgId } from "@/lib/realtime";
import { useReconnectingSocket } from "@/lib/useReconnectingSocket";
import { ApprovalPanel } from "@/components/admin/ApprovalPanel";
import { EscalationCardPanel } from "@/components/admin/EscalationCardPanel";
import { StatusPill } from "@/components/admin/StatusPill";
import { ConfirmModal } from "@/components/ConfirmModal";

function CloseCaseIcon() {
  return (
    <svg
      width="14"
      height="14"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
    >
      <circle cx="12" cy="12" r="9" />
      <line x1="9" y1="9" x2="15" y2="15" />
      <line x1="15" y1="9" x2="9" y2="15" />
    </svg>
  );
}

// Màn chi tiết admin (08b/08c/08a): EscalationCard + lịch sử + tiếp quản TƯỜNG MINH + trả lời + duyệt nháp.
// MỞ = CHỈ XEM (fix 08c): ca vẫn nằm trong hàng đợi cho tới khi bấm "Tiếp quản".
//
// Làm tươi (FE-01.1 / FE-01.3): hội thoại nạp lại mỗi lần mở trang và mỗi lần socket (nối lại) mở; tin realtime
// ghép theo message_id nên không mất, không trùng. Frame `status` (ca đổi trạng thái khi đang mở) → pill +
// EscalationCard / ApprovalPanel theo ngay. "Đang xử lý" chỉ khi CHÍNH mình giữ ca (assigned_admin_id).

const hhmm = (iso?: string) =>
  new Date(iso ?? Date.now()).toLocaleTimeString("vi-VN", {
    hour: "2-digit",
    minute: "2-digit",
  });

function initials(s?: string | null): string {
  const t = (s ?? "").replace(/[^a-zA-Z0-9]/g, "");
  return (t.slice(0, 2) || "KH").toUpperCase();
}

// Server từ chối tin admin vì ca không (còn) do mình giữ (contract §4.2 `error/not_assigned`).
const NOT_ASSIGNED_NOTICE =
  "Tin chưa được gửi: bạn không còn giữ ca này (chưa tiếp quản, ca đã đổi trạng thái hoặc nhân viên khác đã nhận).";

function Bubble({
  msg,
  canRetry,
  onRetry,
}: {
  msg: AdminMsg;
  canRetry: boolean;
  onRetry: (m: AdminMsg) => void;
}) {
  const { sender, content } = msg;
  const time = hhmm(msg.at);
  if (sender === "system") {
    return (
      <div className="flex justify-center">
        <div className="whitespace-pre-wrap break-words rounded-[9px] border border-terracotta-line bg-terracotta-soft px-3.5 py-[7px] text-xs text-terracotta-ink">
          {content}
        </div>
      </div>
    );
  }
  const isCustomer = sender === "customer";
  const isAdmin = sender === "admin";
  const label = isCustomer ? "Khách" : isAdmin ? "Bạn (CSKH)" : "Trợ lý AI";
  return (
    <div
      className={`flex flex-col gap-[5px] ${isCustomer ? "items-start" : "items-end"}`}
    >
      <span
        className={`px-0.5 text-[11.5px] ${isCustomer ? "text-dim" : isAdmin ? "text-steel" : "text-olive-dark"}`}
      >
        {label} · {time}
      </span>
      <div
        className={`max-w-[72%] whitespace-pre-wrap break-words px-[15px] py-[11px] text-[14.5px] leading-[1.55] ${
          msg.sendState === "sending" ? "opacity-70 " : ""
        }${
          isCustomer
            ? "rounded-[5px_15px_15px_15px] border border-line bg-white text-ink"
            : isAdmin
              ? "rounded-[15px_15px_5px_15px] border border-steel-line bg-steel-soft text-ink"
              : "rounded-[15px_15px_5px_15px] border border-line-olive bg-olive-soft text-ink"
        }`}
      >
        {content}
      </div>
      {msg.sendState === "sending" && (
        <span className="px-0.5 text-[11px] text-dim">Đang gửi…</span>
      )}
      {msg.sendState === "failed" && (
        <span className="flex items-center gap-1 px-0.5 text-[11.5px] text-terracotta">
          Chưa gửi được ·
          <button
            type="button"
            onClick={() => onRetry(msg)}
            disabled={!canRetry}
            className="font-semibold hover:underline disabled:opacity-50"
          >
            Gửi lại
          </button>
        </span>
      )}
    </div>
  );
}

export default function AdminConversationPage({
  params,
}: {
  params: { conversationId: string };
}) {
  const id = params.conversationId;
  const qc = useQueryClient();
  const { user } = useAuth();
  const [live, setLive] = useState<AdminMsg[]>([]);
  // Trạng thái / người giữ ca theo socket (system lúc (nối lại) mở, frame status) hoặc theo body của hành động
  // vừa thành công — mới hơn bản REST. `wsAssigned === undefined` = chưa biết → dùng số liệu REST.
  const [wsStatus, setWsStatus] = useState<string | null>(null);
  const [wsAssigned, setWsAssigned] = useState<string | null | undefined>(undefined);
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const [replyError, setReplyError] = useState<string | null>(null);
  const [confirmCloseOpen, setConfirmCloseOpen] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);
  // Hẹn giờ ack theo client_msg_id; `genRef` = thế hệ socket (+1 mỗi lần mở) — xem app/chat/page.tsx.
  const ackTimers = useRef(new Map<string, ReturnType<typeof setTimeout>>());
  const genRef = useRef(0);
  const seqRef = useRef(0);
  const wsUrl = useMemo(() => {
    const token = getToken();
    return token ? adminWsUrl(id, token) : null;
  }, [id]);

  const {
    data: conv,
    isLoading,
    isError,
    error,
  } = useQuery<AdminConversation, Error>({
    queryKey: ["admin-conv", id],
    queryFn: () => getAdminConversation(id),
    // KHÔNG staleTime Infinity (FE-01.1): mở lại ca phải nạp lại, tin đến lúc không xem mới không mất.
    refetchOnMount: "always",
    refetchOnWindowFocus: false,
  });

  const status = wsStatus ?? conv?.status ?? null;
  const assigned = wsAssigned !== undefined ? wsAssigned : (conv?.assigned_admin_id ?? null);
  const closed = status === "RESOLVED" || status === "CLOSED";
  const humanHandling = status === "HUMAN_HANDLING";
  // "Đang xử lý" chỉ khi CHÍNH mình giữ ca; nhân viên khác giữ → chỉ xem (không trả lời / tiếp quản / đóng).
  const isHandling = humanHandling && !!user && assigned === user.id;
  const heldByOther = humanHandling && !!assigned && assigned !== user?.id;
  const isPending = status === "PENDING_APPROVAL";

  function refresh() {
    qc.invalidateQueries({ queryKey: ["admin-conv", id] });
    qc.invalidateQueries({ queryKey: ["conversations"] });
    qc.invalidateQueries({ queryKey: ["escalations"] });
  }

  const clearAck = (cid: string) => {
    const t = ackTimers.current.get(cid);
    if (t !== undefined) clearTimeout(t);
    ackTimers.current.delete(cid);
  };

  useEffect(() => {
    const timers = ackTimers.current;
    return () => timers.forEach((t) => clearTimeout(t));
  }, []);

  function onFrame(f: Frame) {
    switch (f.type) {
      case "system": {
        // Mỗi lần socket (nối lại) mở: trạng thái + người giữ ca TẠI THỜI ĐIỂM đó. Server đọc lỗi (status null) →
        // người giữ ca "chưa biết" → dùng số liệu REST, không coi là "không ai giữ" (FE-03.2).
        const s = convStateOf(f);
        setWsStatus(s.status);
        setWsAssigned(s.assigned);
        break;
      }
      case "status": {
        // FE-01.3: ca đổi trạng thái khi đang mở → pill + EscalationCard / ApprovalPanel theo ngay (nạp lại card).
        const s = convStateOf(f);
        setWsStatus(s.status);
        setWsAssigned(s.assigned);
        refresh();
        break;
      }
      case "message": {
        const messageId = asString(f.message_id);
        const item: AdminMsg = {
          key: messageId ?? `live-${seqRef.current++}`,
          sender: asString(f.from) ?? "ai",
          content: asString(f.content) ?? "",
          at: new Date().toISOString(),
          messageId,
        };
        setLive((p) => appendUnique(p, item));
        break;
      }
      case "ack": {
        const cid = asString(f.client_msg_id);
        if (cid) {
          clearAck(cid);
          setLive((p) => markSent(p, cid, asString(f.message_id)));
        }
        break;
      }
      case "error": {
        const cid = asString(f.client_msg_id);
        if (cid) {
          clearAck(cid);
          setLive((p) => markFailed(p, cid));
        }
        if (f.code === "not_assigned") {
          setReplyError(NOT_ASSIGNED_NOTICE);
          // Server là chuẩn: bỏ trạng thái socket có thể đã cũ (như nhánh lỗi của `act`) để số liệu vừa nạp lại quyết
          // định — không thì ô trả lời vẫn mở và tin nào cũng bị từ chối lại (FE-03.2).
          setWsStatus(null);
          setWsAssigned(undefined);
          refresh(); // nạp lại trạng thái / người giữ ca thật
        }
        break;
      }
    }
  }

  const socket = useReconnectingSocket(wsUrl, {
    authRole: "admin",
    onFrame,
    // Mỗi lần (nối lại) mở: nạp lại hội thoại — tin đến lúc rớt / lúc không xem không bị mất (FE-01.1).
    onOpen: () => {
      genRef.current += 1;
      qc.invalidateQueries({ queryKey: ["admin-conv", id] });
    },
  });
  const online = socket.state === "online";

  const messages = useMemo(
    () => mergeAdminMessages(conv?.messages ?? [], live),
    [conv?.messages, live],
  );

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages.length]);

  async function act(fn: () => Promise<AdminConversation>) {
    setBusy(true);
    setActionError(null);
    try {
      const res = await fn();
      // Áp trạng thái CHỈ SAU khi server nhận — lấy từ chính body trả về (không đoán trước).
      setWsStatus(res.status);
      setWsAssigned(res.assigned_admin_id ?? null);
    } catch (e) {
      // FE-03: 409 (ca đã đổi trạng thái / nhân viên khác đang giữ) → hiện đúng lý do backend rồi nạp lại ca;
      // bỏ trạng thái socket có thể đã cũ để số liệu vừa nạp lại quyết định.
      setActionError(e instanceof Error ? e.message : "Thao tác không thành công.");
      setWsStatus(null);
      setWsAssigned(undefined);
    } finally {
      setBusy(false);
      refresh();
    }
  }

  // Gửi (hoặc gửi lại — CÙNG client_msg_id) một tin admin rồi chờ ack.
  function transmit(cid: string, text: string) {
    clearAck(cid);
    setLive((p) => markSending(p, cid));
    if (!socket.send({ type: "message", content: text, client_msg_id: cid })) {
      setLive((p) => markFailed(p, cid));
      return;
    }
    const gen = genRef.current;
    ackTimers.current.set(
      cid,
      setTimeout(() => {
        ackTimers.current.delete(cid);
        setLive((p) => markFailed(p, cid));
        // Socket đã nhận tin vẫn là socket hiện tại mà không ack → nghi half-open: bỏ và nối lại.
        if (gen === genRef.current) socket.reconnect();
      }, ACK_TIMEOUT_MS),
    );
  }

  function sendReply() {
    const text = draft.trim();
    // Không giữ ca / mất kết nối → return TRƯỚC khi xoá draft: chữ admin đang soạn không bị mất.
    if (!text || !isHandling || !online) return;
    const cid = newClientMsgId();
    setReplyError(null);
    setLive((p) => [
      ...p,
      {
        key: cid,
        sender: "admin",
        content: text,
        at: new Date().toISOString(),
        clientMsgId: cid,
        sendState: "sending",
      },
    ]);
    setDraft("");
    transmit(cid, text);
  }

  function retry(m: AdminMsg) {
    if (!m.clientMsgId || !isHandling || !online) return;
    setReplyError(null);
    transmit(m.clientMsgId, m.content);
  }

  const replyPlaceholder = heldByOther
    ? "Ca đang do nhân viên khác xử lý"
    : !isHandling
      ? "Tiếp quản để trả lời khách"
      : online
        ? "Nhập trả lời gửi tới khách…"
        : "Mất kết nối — đang kết nối lại…";

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
            <div className="truncate text-xs text-faint">
              khách · {id.slice(0, 8)}
            </div>
          </div>
        </div>
        <div className="flex flex-none items-center gap-2">
          <StatusPill status={status} size="md" />
          {/* Hành động phá huỷ/thoát → tông cảnh báo (design §2), khác nút xây dựng (olive). */}
          {!closed && (
            <button
              onClick={() => setConfirmCloseOpen(true)}
              disabled={busy || heldByOther}
              title="Đóng ca hội thoại này"
              className="inline-flex items-center gap-[7px] whitespace-nowrap rounded-[8px] border border-terracotta-btn-line bg-terracotta-btn px-[13px] py-[7px] text-[12.5px] font-semibold text-terracotta transition-colors hover:border-terracotta-btn-line-hover hover:bg-terracotta-btn-hover disabled:opacity-50 mob:hidden"
            >
              <CloseCaseIcon />
              Đóng ca
            </button>
          )}
        </div>
      </header>

      {/* Mất kết nối (FE-01.2): admin phải biết là đang KHÔNG nhận tin khách, thay vì tưởng khách im lặng. */}
      {(socket.state === "reconnecting" || socket.state === "offline") && (
        <div
          role="status"
          className="flex flex-none items-center gap-2 border-b border-terracotta-line bg-terracotta-soft px-[26px] py-1.5 text-xs text-terracotta-ink mob:px-4"
        >
          <span
            className={`h-1.5 w-1.5 flex-none rounded-full bg-terracotta ${
              socket.state === "reconnecting" ? "animate-blink" : ""
            }`}
          />
          {socket.state === "offline"
            ? "Phiên đăng nhập đã hết hạn — vui lòng đăng nhập lại."
            : "Mất kết nối — đang kết nối lại… Tin mới sẽ hiện khi kết nối lại."}
        </div>
      )}

      <div className="flex flex-1 flex-col gap-4 overflow-y-auto bg-panel px-[26px] py-6 mob:px-4">
        {isLoading && <p className="text-sm text-dim">Đang tải hội thoại…</p>}
        {isError && (
          <p className="text-sm text-terracotta">Lỗi: {error.message}</p>
        )}

        {conv?.escalation_card &&
          (status === "IN_HUMAN_QUEUE" || isPending) && (
            <EscalationCardPanel
              card={conv.escalation_card}
              identifier={conv.customer_identifier}
            />
          )}

        {isPending && conv?.escalation_card?.suggested_reply && (
          <ApprovalPanel
            draft={conv.escalation_card.suggested_reply}
            busy={busy}
            onApprove={(content, shown) => act(() => approveDraft(id, content, shown))}
            onReject={(shown) => act(() => rejectDraft(id, shown))}
          />
        )}

        <div className="flex flex-col gap-[18px]">
          {messages.map((m) => (
            <Bubble key={m.key} msg={m} canRetry={isHandling && online} onRetry={retry} />
          ))}
          <div ref={endRef} />
        </div>
      </div>

      <footer className="flex-none border-t border-line bg-white px-[26px] py-3.5 mob:px-4">
        {actionError && (
          <p role="alert" className="mb-2.5 text-[12.5px] leading-[1.5] text-terracotta">
            {actionError}
          </p>
        )}
        <div className="mb-2.5 flex flex-wrap items-center gap-2.5">
          {isHandling ? (
            <div className="flex flex-1 items-center gap-2 rounded-lg border border-steel-line bg-steel-soft px-3 py-[7px] text-xs text-steel">
              <span className="h-1.5 w-1.5 flex-none rounded-full bg-steel" />
              AI đã tạm dừng cho hội thoại này — bạn đang trực tiếp trả lời
              khách.
            </div>
          ) : (
            <>
              <button
                onClick={() => act(() => takeoverConversation(id))}
                disabled={busy || closed || heldByOther}
                className="rounded-[9px] bg-olive px-[18px] py-2.5 text-sm font-semibold text-white hover:bg-olive-dark disabled:opacity-50"
              >
                Tiếp quản
              </button>
              {heldByOther ? (
                <div className="flex flex-1 items-center gap-2 rounded-lg border border-steel-line bg-steel-soft px-3 py-[7px] text-xs text-steel">
                  <span className="h-1.5 w-1.5 flex-none rounded-full bg-steel" />
                  Ca đang do nhân viên khác xử lý — bạn chỉ xem, không trả lời hay đóng ca được.
                </div>
              ) : (
                <span className="flex-1 text-xs text-faint">
                  Đang ở chế độ xem — ca vẫn nằm trong hàng đợi cho tới khi bạn
                  tiếp quản.
                </span>
              )}
            </>
          )}
          {/* Mobile: "Đóng ca" chuyển xuống đây vì header hẹp (tên khách bị cắt nếu nhồi thêm nút). */}
          {!closed && (
            <button
              onClick={() => setConfirmCloseOpen(true)}
              disabled={busy || heldByOther}
              className="hidden items-center gap-[7px] whitespace-nowrap rounded-[8px] border border-terracotta-btn-line bg-terracotta-btn px-[13px] py-2 text-[12.5px] font-semibold text-terracotta disabled:opacity-50 mob:inline-flex"
            >
              <CloseCaseIcon />
              Đóng ca
            </button>
          )}
        </div>

        {replyError && (
          <p role="alert" className="mb-2 text-[12.5px] leading-[1.5] text-terracotta">
            {replyError}
          </p>
        )}
        <div className="flex items-center gap-2.5 rounded-[12px] border border-line bg-cream-soft py-[7px] pl-4 pr-[7px]">
          <input
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") sendReply();
            }}
            disabled={!isHandling}
            placeholder={replyPlaceholder}
            aria-label="Nội dung trả lời khách"
            className="flex-1 border-none bg-transparent text-[14.5px] text-ink outline-none placeholder:text-dim disabled:cursor-not-allowed"
          />
          <button
            onClick={sendReply}
            disabled={!isHandling || !online || !draft.trim()}
            className="rounded-[8px] bg-ink px-[18px] py-[9px] text-[13.5px] font-semibold text-ink-paper hover:bg-ink-2 disabled:opacity-50"
          >
            Gửi
          </button>
        </div>
      </footer>

      {/* Modal xác nhận đóng ca */}
      <ConfirmModal
        isOpen={confirmCloseOpen}
        onClose={() => setConfirmCloseOpen(false)}
        onConfirm={() => {
          setConfirmCloseOpen(false);
          act(() => resolveConversation(id));
        }}
        title="Xác nhận đóng ca"
        message={
          <>
            Bạn có chắc chắn muốn đóng ca hội thoại của khách hàng{" "}
            <span className="font-semibold text-ink">
              {conv?.customer_identifier || `Khách ${id.slice(0, 6)}`}
            </span>
            ? Ca sẽ được chuyển sang trạng thái đã xử lý (Resolved) và AI/CSKH
            kết thúc phiên này.
          </>
        }
        confirmText="Đồng ý đóng ca"
        cancelText="Hủy"
        variant="danger"
        isLoading={busy}
      />
    </div>
  );
}
