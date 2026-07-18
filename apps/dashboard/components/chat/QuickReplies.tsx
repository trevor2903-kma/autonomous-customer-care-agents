"use client";

// Gợi ý câu hỏi nhanh (design: pill dưới header). Đây là quick-reply THẬT — bấm là gửi câu hỏi,
// khác với pill trong file mockup (vốn chỉ để chuyển kịch bản demo).
const QUICK_REPLIES = [
  "Chính sách đổi trả thế nào?",
  "Phí ship và thời gian giao?",
  "Tư vấn giúp mình chọn size",
  "Kiểm tra đơn hàng của mình",
];

export function QuickReplies({
  disabled,
  onPick,
}: {
  disabled: boolean;
  onPick: (text: string) => void;
}) {
  return (
    <div className="flex flex-wrap gap-2">
      {QUICK_REPLIES.map((q) => (
        <button
          key={q}
          onClick={() => onPick(q)}
          disabled={disabled}
          className="whitespace-nowrap rounded-lg border border-line bg-white px-[13px] py-1.5 text-[12.5px] text-muted hover:border-line-olive hover:text-ink disabled:opacity-50"
        >
          {q}
        </button>
      ))}
    </div>
  );
}
