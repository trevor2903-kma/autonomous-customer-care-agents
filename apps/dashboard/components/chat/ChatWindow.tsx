"use client";

import { useEffect, useRef } from "react";

export type ChatMessage = {
  id: number;
  from: "you" | "system" | "ai" | "admin";
  text: string;
  time: string;
  /** Nguồn tri thức Agent 2 dùng để trả lời (chip "Căn cứ tri thức"). */
  sources?: string[];
};

// Bong bóng theo design: khách (nền đậm, phải) · AI (trắng + avatar olive) · nhân viên (avatar steel) ·
// hệ thống/chuyển người (căn giữa, terracotta).
export function ChatWindow({
  messages,
  typing = false,
  waiting = false,
}: {
  messages: ChatMessage[];
  typing?: boolean;
  waiting?: boolean;
}) {
  const endRef = useRef<HTMLDivElement>(null);
  // Luôn cuộn tới tin mới nhất (kể cả khi đang hiện "đang trả lời…").
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages.length, typing, waiting]);

  return (
    <div className="flex flex-1 flex-col gap-5 overflow-y-auto px-1 pb-[22px] pt-3">
      {messages.length === 0 && !typing && (
        <p className="pt-6 text-center text-sm text-dim">
          Hỏi shop về sản phẩm, size, đổi trả, vận chuyển…
        </p>
      )}

      {messages.map((m) => {
        if (m.from === "you") {
          return (
            <div key={m.id} className="flex flex-col items-end gap-[5px]">
              <div className="max-w-[80%] rounded-[16px_16px_5px_16px] bg-ink px-4 py-3 text-[15px] leading-[1.55] text-ink-paper">
                {m.text}
              </div>
              <span className="pr-1 text-[11px] text-dim">{m.time}</span>
            </div>
          );
        }

        if (m.from === "system") {
          return (
            <div key={m.id} className="flex justify-center">
              <div className="max-w-[82%] rounded-[11px] border border-terracotta-line bg-terracotta-soft px-[18px] py-2.5 text-center text-[13px] leading-[1.55] text-terracotta-ink">
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
            <div className="flex max-w-[80%] flex-col gap-[7px]">
              {isAdmin && <span className="text-xs font-semibold text-steel">Nhân viên hỗ trợ</span>}
              <div
                className={`rounded-[5px_16px_16px_16px] border bg-white px-4 py-3 text-[15px] leading-[1.6] text-ink ${
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
                      className="rounded-md border border-line-olive bg-olive-soft px-2 py-0.5 font-mono text-[11.5px] text-olive-dark"
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

      <div ref={endRef} />
    </div>
  );
}
