"use client";

// Gợi ý câu hỏi nhanh (design: pill dưới header). Đây là quick-reply THẬT — bấm là gửi câu hỏi,
// khác với pill trong file mockup (vốn chỉ để chuyển kịch bản demo).
const QUICK_REPLIES = [
  { text: "Chính sách đổi trả thế nào?", mobHidden: true },
  { text: "Phí ship và thời gian giao?", mobHidden: true },
  { text: "Tư vấn giúp mình chọn size" },
  { text: "Kiểm tra đơn hàng của mình" },
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
          key={q.text}
          onClick={() => onPick(q.text)}
          disabled={disabled}
          className={`whitespace-nowrap rounded-lg border border-line bg-white px-[13px] py-1.5 text-[12.5px] text-muted hover:border-line-olive hover:text-ink disabled:opacity-50 ${
            q.mobHidden ? "mob:hidden" : ""
          }`}
        >
          {q.text}
        </button>
      ))}
    </div>
  );
}
