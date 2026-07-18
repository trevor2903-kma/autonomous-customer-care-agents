"use client";

import { useEffect, useState } from "react";

// Khối duyệt nháp (08a, design "Nháp phản hồi gợi ý"): nháp Agent 4 hiện ra để admin đọc, SỬA TRỰC TIẾP rồi gửi.
// Chỉ 2 hành động: gửi (nội dung đang có trong ô) hoặc chuyển sang tự xử lý — "sửa & gửi" chính là sửa ô rồi bấm gửi,
// nên không tách thành nút riêng làm cùng một việc.
export function ApprovalPanel({
  draft,
  busy,
  onApprove,
  onReject,
}: {
  draft: string;
  busy: boolean;
  onApprove: (content: string) => void;
  onReject: () => void;
}) {
  const [text, setText] = useState(draft);
  useEffect(() => setText(draft), [draft]);

  return (
    <section className="rounded-[13px] border-[1.5px] border-olive bg-white px-5 py-[18px] shadow-draft">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <div className="text-xs font-semibold uppercase tracking-[0.8px] text-olive-dark">
          Nháp phản hồi gợi ý
        </div>
        <span className="text-[11.5px] text-faint">AI soạn từ RAG context · sửa trực tiếp trước khi gửi</span>
      </div>

      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={4}
        aria-label="Nháp phản hồi"
        className="min-h-[118px] w-full resize-y rounded-[10px] border border-line bg-panel px-[15px] py-[13px] text-[14.5px] leading-[1.6] text-ink outline-none focus:border-olive"
      />

      <div className="mt-3.5 flex flex-wrap items-center gap-2.5">
        <button
          onClick={() => onApprove(text)}
          disabled={busy || !text.trim()}
          className="rounded-[9px] bg-olive px-[22px] py-[11px] text-sm font-semibold text-white hover:bg-olive-dark disabled:opacity-50"
        >
          Duyệt &amp; gửi
        </button>
        <button
          onClick={onReject}
          disabled={busy}
          className="rounded-[9px] border border-line bg-transparent px-[18px] py-[11px] text-sm text-faint hover:bg-cream disabled:opacity-50"
        >
          Chuyển xử lý tay
        </button>
      </div>
    </section>
  );
}
