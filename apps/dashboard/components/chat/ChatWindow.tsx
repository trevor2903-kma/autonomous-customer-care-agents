export type ChatMessage = {
  id: number;
  from: "you" | "system" | "ai" | "admin";
  text: string;
};

// Màu bong bóng theo người gửi. admin = nhân viên (egress-người, PRD §7.4) → nổi bật khác AI.
function bubbleClass(from: ChatMessage["from"]): string {
  if (from === "you") return "bg-neutral-900 text-white";
  if (from === "system") return "bg-amber-50 text-amber-700";
  if (from === "admin") return "bg-emerald-600 text-white";
  return "bg-white text-neutral-800 border border-neutral-200"; // ai
}

export function ChatWindow({
  messages,
  typing = false,
}: {
  messages: ChatMessage[];
  typing?: boolean;
}) {
  return (
    <div className="flex-1 space-y-2 overflow-y-auto p-4">
      {messages.length === 0 && !typing && (
        <p className="text-center text-sm text-neutral-400">
          Hỏi shop về sản phẩm, size, đổi trả, vận chuyển…
        </p>
      )}
      {messages.map((m) => (
        <div
          key={m.id}
          className={m.from === "you" ? "flex justify-end" : "flex flex-col items-start"}
        >
          {m.from === "admin" && (
            <span className="mb-0.5 text-[10px] font-medium text-emerald-700">Nhân viên hỗ trợ</span>
          )}
          <span className={`max-w-[75%] rounded-2xl px-3 py-2 text-sm ${bubbleClass(m.from)}`}>
            {m.text}
          </span>
        </div>
      ))}
      {typing && (
        <div className="flex justify-start">
          <span className="max-w-[75%] rounded-2xl border border-neutral-200 bg-white px-3 py-2 text-sm text-neutral-400">
            đang trả lời…
          </span>
        </div>
      )}
    </div>
  );
}
