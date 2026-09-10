"use client";

import { useLayoutEffect, useRef, useState } from "react";
import { MAX_MESSAGE_CHARS } from "shared-types";
import { effectiveLength, isSendKey, showCharCounter } from "@/lib/chatInput";

// ~5 dòng (15px × leading 1.5) + padding dọc → vượt thì ô tự cuộn thay vì nở tiếp.
const MAX_INPUT_HEIGHT_PX = 128;

// Máy cảm ứng (con trỏ chính "thô"): bàn phím ảo không có Shift+Enter → Enter để xuống dòng (UX-01.1).
const isCoarsePointer = () =>
  typeof window !== "undefined" && window.matchMedia?.("(pointer: coarse)").matches === true;

// Ô nhập màn khách (design): hộp trắng bo 14px + nút "Gửi" olive + dòng ghi chú dưới.
// Nhiều dòng (UX-01.1): textarea tự nở tới ~5 dòng; Enter gửi, Shift+Enter xuống dòng (máy cảm ứng: Enter xuống
// dòng, gửi bằng nút), KHÔNG gửi khi bộ gõ đang ghép chữ; dán văn bản giữ nguyên xuống dòng. Trần MAX_MESSAGE_CHARS
// (UX-01.2) = đúng trần backend cắt ở biên WS, đếm như backend (sau NFKC) → chữ khách thấy chính là chữ hệ thống
// nhận; gần trần thì hiện bộ đếm, vượt trần thì không gửi.
export function MessageInput({
  disabled,
  placeholder,
  onSend,
}: {
  disabled: boolean;
  placeholder: string;
  /** true = tin đã vào danh sách (đang gửi / có "Gửi lại") → được xoá ô; false → giữ nguyên chữ. */
  onSend: (text: string) => boolean;
}) {
  const [text, setText] = useState("");
  const ref = useRef<HTMLTextAreaElement>(null);

  // Auto-grow: co về một dòng rồi nở theo nội dung, tới trần thì cuộn trong ô.
  useLayoutEffect(() => {
    const el = ref.current;
    if (!el) return;
    el.style.height = "auto";
    const full = el.scrollHeight;
    el.style.height = `${Math.min(full, MAX_INPUT_HEIGHT_PX)}px`;
    el.style.overflowY = full > MAX_INPUT_HEIGHT_PX ? "auto" : "hidden";
  }, [text]);

  const length = effectiveLength(text);
  const overLimit = length > MAX_MESSAGE_CHARS;

  function submit() {
    // Chặn NGAY trong submit (không chỉ nhờ nút bị khoá): mất kết nối thì chữ PHẢI còn nguyên trong ô (UX-02.2);
    // vượt trần (sau NFKC) thì server sẽ cắt → không gửi, để khách tự rút gọn.
    if (disabled || overLimit) return;
    const t = text.trim();
    if (!t) return;
    if (onSend(t)) setText("");
  }

  const showCounter = showCharCounter(length, MAX_MESSAGE_CHARS);
  return (
    <div className="flex-none px-1 pb-[22px]">
      <form
        onSubmit={(e) => {
          e.preventDefault();
          submit();
        }}
        className="flex items-end gap-2.5 rounded-[14px] border border-line bg-white py-2 pl-[18px] pr-2 shadow-soft focus-within:border-line-olive"
      >
        <textarea
          ref={ref}
          rows={1}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => {
            if (isSendKey(e.nativeEvent, isCoarsePointer())) {
              e.preventDefault();
              submit();
            }
          }}
          maxLength={MAX_MESSAGE_CHARS}
          disabled={disabled}
          placeholder={placeholder}
          aria-label="Nội dung tin nhắn"
          className="min-w-0 flex-1 resize-none border-none bg-transparent py-[9px] text-[15px] leading-[1.5] text-ink outline-none placeholder:text-dim disabled:cursor-not-allowed"
        />
        {showCounter && (
          <span
            aria-live="polite"
            className={`flex-none pb-[11px] text-[11px] ${
              length >= MAX_MESSAGE_CHARS ? "text-terracotta" : "text-dim"
            }`}
          >
            {length}/{MAX_MESSAGE_CHARS}
          </span>
        )}
        <button
          type="submit"
          disabled={disabled || !text.trim() || overLimit}
          className="rounded-[9px] bg-olive px-5 py-2.5 text-sm font-semibold text-white hover:bg-olive-dark disabled:opacity-50"
        >
          Gửi
        </button>
      </form>
      <p className="mt-[11px] text-center text-[11.5px] text-dimmer">
        Trợ lý AI trả lời dựa trên tài liệu chính thức của shop · phản hồi tự động ≤ 5 giây
      </p>
    </div>
  );
}
