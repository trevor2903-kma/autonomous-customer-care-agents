"use client";

import { useState } from "react";

// Ô nhập màn khách (design): hộp trắng bo 14px + nút "Gửi" olive + dòng ghi chú dưới.
export function MessageInput({
  disabled,
  placeholder,
  onSend,
}: {
  disabled: boolean;
  placeholder: string;
  onSend: (text: string) => void;
}) {
  const [text, setText] = useState("");

  function submit(e: React.FormEvent) {
    e.preventDefault();
    const t = text.trim();
    if (!t) return;
    onSend(t);
    setText("");
  }

  return (
    <div className="flex-none px-1 pb-[22px]">
      <form
        onSubmit={submit}
        className="flex items-center gap-2.5 rounded-[14px] border border-line bg-white py-2 pl-[18px] pr-2 shadow-soft focus-within:border-line-olive"
      >
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder={placeholder}
          aria-label="Nội dung tin nhắn"
          className="flex-1 border-none bg-transparent text-[15px] text-ink outline-none placeholder:text-dim"
        />
        <button
          type="submit"
          disabled={disabled || !text.trim()}
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
