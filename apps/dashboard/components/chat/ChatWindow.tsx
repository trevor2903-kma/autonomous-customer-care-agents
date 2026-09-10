"use client";

import { useEffect, useRef, useState } from "react";
import type { SendState } from "@/lib/messageMerge";

export type ChatMessage = {
  id: number;
  from: "you" | "system" | "ai" | "admin";
  text: string;
  time: string;
  /** Nguồn tri thức Agent 2 dùng để trả lời (chip "Căn cứ tri thức"). */
  sources?: string[];
  /** id tin đã lưu (message.id) — khoá chống trùng khi ghép lịch sử với frame realtime. */
  messageId?: string | null;
  /** Tin khách gửi từ CHÍNH tab này: uuid client sinh, dùng lại nguyên văn khi gửi lại (IDEM-XC.1). */
  clientMsgId?: string;
  /** Vòng đời gửi của tin có clientMsgId: đang gửi → đã gửi (ack) → chưa gửi được (FE-01.4 / UX-02.2). */
  sendState?: SendState;
  /** Bong bóng dựng từ /me/thread — bị thay toàn bộ ở lần ghép lịch sử kế tiếp. */
  fromHistory?: boolean;
  /** Tin mình gửi mà lúc nối lại chưa thấy trong lịch sử: server có thể phát lại nó qua hub (from:"customer") →
   *  nhận làm CHÍNH bong bóng này, không thêm bong bóng thứ hai (FE-01.6). */
  echoPending?: boolean;
};

// Còn cách đáy ≤ 80px coi như "đang ở đáy" → tin mới tự cuộn theo (UX-02.1).
const NEAR_BOTTOM_PX = 80;

// Bong bóng theo design: khách (nền đậm, phải) · AI (trắng + avatar olive) · nhân viên (avatar steel) ·
// hệ thống/chuyển người (căn giữa, terracotta). Chữ `whitespace-pre-wrap` giữ xuống dòng khách gõ, `break-words`
// bẻ chuỗi dài liền (URL, mã) để không tràn khỏi bong bóng (UX-01.3).
//
// Cuộn DÍNH ĐÁY (UX-02.1): chỉ tự cuộn khi đang ở gần đáy hoặc vừa gửi tin; đang đọc lịch sử phía trên thì hiện
// nút "Tin nhắn mới ↓" thay vì giật xuống. Lần nạp lịch sử đầu nhảy thẳng xuống đáy (không cuộn animation).
export function ChatWindow({
  messages,
  typing = false,
  waiting = false,
  onRetry,
  canRetry = true,
}: {
  messages: ChatMessage[];
  typing?: boolean;
  waiting?: boolean;
  /** "Gửi lại" một tin chưa gửi được — cùng client_msg_id (server nhận ra tin trùng, không chạy lại lượt). */
  onRetry?: (clientMsgId: string, text: string) => void;
  canRetry?: boolean;
}) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const stickRef = useRef(true); // đang "bám đáy" — chỉ tắt khi CHÍNH người dùng cuộn lên
  const lastTopRef = useRef(0);
  const prevCountRef = useRef(0);
  const [hasNew, setHasNew] = useState(false);

  const last = messages[messages.length - 1];
  const justSent = last?.from === "you" && last.sendState === "sending";

  function scrollToEnd(behavior: ScrollBehavior) {
    const el = scrollRef.current;
    if (!el) return;
    el.scrollTo({ top: el.scrollHeight, behavior });
    stickRef.current = true;
    setHasNew(false);
  }

  function onScroll() {
    const el = scrollRef.current;
    if (!el) return;
    if (el.scrollHeight - el.scrollTop - el.clientHeight <= NEAR_BOTTOM_PX) {
      stickRef.current = true;
      setHasNew(false);
    } else if (el.scrollTop < lastTopRef.current) {
      stickRef.current = false; // người dùng cuộn LÊN (cuộn tự động chỉ đi xuống)
    }
    lastTopRef.current = el.scrollTop;
  }

  useEffect(() => {
    const prev = prevCountRef.current;
    const count = messages.length;
    prevCountRef.current = count;
    if (prev === 0 && count > 0) {
      scrollToEnd("auto"); // nạp lịch sử đầu → nhảy thẳng, không cuộn qua cả lịch sử
      return;
    }
    if (stickRef.current || justSent) {
      // Cả khối mới (ghép lại lịch sử sau khi nối lại) → nhảy; một tin / "đang trả lời…" → cuộn mượt.
      scrollToEnd(count - prev > 1 ? "auto" : "smooth");
      return;
    }
    if (count > prev) setHasNew(true);
  }, [messages.length, typing, waiting, justSent]);

  return (
    <div className="relative flex min-h-0 flex-1 flex-col">
      <div
        ref={scrollRef}
        onScroll={onScroll}
        className="flex min-h-0 flex-1 flex-col gap-5 overflow-y-auto px-1 pb-[22px] pt-3"
      >
        {messages.length === 0 && !typing && (
          <p className="pt-6 text-center text-sm text-dim">
            Hỏi shop về sản phẩm, size, đổi trả, vận chuyển…
          </p>
        )}

        {messages.map((m) => {
          if (m.from === "you") {
            const cid = m.clientMsgId;
            return (
              <div key={m.id} className="flex flex-col items-end gap-[5px]">
                <div
                  className={`max-w-[80%] whitespace-pre-wrap break-words rounded-[16px_16px_5px_16px] bg-ink px-4 py-3 text-[15px] leading-[1.55] text-ink-paper ${
                    m.sendState === "sending" ? "opacity-70" : ""
                  }`}
                >
                  {m.text}
                </div>
                {m.sendState === "failed" && cid ? (
                  <span className="flex items-center gap-1 pr-1 text-[11.5px] text-terracotta">
                    Chưa gửi được ·
                    <button
                      type="button"
                      onClick={() => onRetry?.(cid, m.text)}
                      disabled={!canRetry}
                      className="font-semibold hover:underline disabled:opacity-50"
                    >
                      Gửi lại
                    </button>
                  </span>
                ) : (
                  <span className="pr-1 text-[11px] text-dim">
                    {m.sendState === "sending" ? "Đang gửi…" : m.time}
                  </span>
                )}
              </div>
            );
          }

          if (m.from === "system") {
            return (
              <div key={m.id} className="flex justify-center">
                <div className="max-w-[82%] whitespace-pre-wrap break-words rounded-[11px] border border-terracotta-line bg-terracotta-soft px-[18px] py-2.5 text-center text-[13px] leading-[1.55] text-terracotta-ink">
                  {m.text}
                </div>
              </div>
            );
          }

          const isAdmin = m.from === "admin";
          return (
            <div key={m.id} className="flex items-start gap-3">
              <span
                className={`flex h-[34px] w-[34px] flex-none items-center justify-center rounded-[9px] border text-xs font-semibold ${
                  isAdmin
                    ? "border-steel-line bg-steel-soft text-steel"
                    : "border-line-olive bg-olive-soft text-olive-dark"
                }`}
              >
                {isAdmin ? "NV" : "AI"}
              </span>
              <div className="flex min-w-0 max-w-[80%] flex-col gap-[7px]">
                {isAdmin && <span className="text-xs font-semibold text-steel">Nhân viên hỗ trợ</span>}
                <div
                  className={`whitespace-pre-wrap break-words rounded-[5px_16px_16px_16px] border bg-white px-4 py-3 text-[15px] leading-[1.6] text-ink ${
                    isAdmin ? "border-steel-line" : "border-line"
                  }`}
                >
                  {m.text}
                </div>
                {m.sources && m.sources.length > 0 && (
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-[11.5px] text-dim">Căn cứ tri thức</span>
                    {m.sources.map((s) => (
                      <span
                        key={s}
                        className="rounded-md border border-line-olive bg-olive-soft px-2 py-0.5 text-[11.5px] text-olive-dark"
                      >
                        {s}
                      </span>
                    ))}
                  </div>
                )}
                <span className="text-[11px] text-dim">{m.time}</span>
              </div>
            </div>
          );
        })}

        {typing && (
          <div className="flex items-center gap-3">
            <span className="flex h-[34px] w-[34px] flex-none items-center justify-center rounded-[9px] border border-line-olive bg-olive-soft text-xs font-semibold text-olive-dark">
              AI
            </span>
            <div className="flex gap-[5px] rounded-[5px_16px_16px_16px] border border-line bg-white px-[18px] py-3.5">
              <span className="h-[7px] w-[7px] rounded-full bg-dim animate-blink" />
              <span className="h-[7px] w-[7px] rounded-full bg-dim animate-blink [animation-delay:.2s]" />
              <span className="h-[7px] w-[7px] rounded-full bg-dim animate-blink [animation-delay:.4s]" />
            </div>
          </div>
        )}

        {waiting && (
          <div className="flex items-center justify-center gap-[9px] text-[13px] text-terracotta">
            <span className="h-[7px] w-[7px] rounded-full bg-terracotta animate-blink" />
            Đang kết nối với nhân viên hỗ trợ…
          </div>
        )}
      </div>

      {hasNew && (
        <button
          type="button"
          onClick={() => scrollToEnd("smooth")}
          className="absolute bottom-3 left-1/2 -translate-x-1/2 rounded-full border border-line-olive bg-white px-3.5 py-1.5 text-[12.5px] font-medium text-olive-dark shadow-card hover:bg-olive-soft"
        >
          Tin nhắn mới ↓
        </button>
      )}
    </div>
  );
}
