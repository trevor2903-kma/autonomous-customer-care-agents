export type ChatMessage = {
  id: number;
  from: "you" | "system" | "ai";
  text: string;
};

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
          className={
            m.from === "you" ? "flex justify-end" : "flex justify-start"
          }
        >
          <span
            className={`max-w-[75%] rounded-2xl px-3 py-2 text-sm ${
              m.from === "you"
                ? "bg-neutral-900 text-white"
                : m.from === "system"
                  ? "bg-amber-50 text-amber-700"
                  : "bg-white text-neutral-800 border border-neutral-200"
            }`}
          >
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
