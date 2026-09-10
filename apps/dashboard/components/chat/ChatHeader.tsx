import Image from "next/image";
import type { ConnState } from "@/lib/useReconnectingSocket";
import { CUST_STATUS, type CustStatus } from "./custStatus";

// Header màn khách (design): avatar "T" olive + tên trợ lý (serif) + chấm trạng thái.
// KHÔNG có link sang admin — khách và bảng điều hành là hai URL tách biệt.
// Không online (FE-01.2) → dòng trạng thái đổi sang báo kết nối, KHÔNG còn chấm xanh "đang trò chuyện".
const CONN_LINE: Partial<Record<ConnState, { label: string; dot: string; text: string }>> = {
  connecting: { label: "Đang kết nối…", dot: "bg-dim", text: "text-faint" },
  reconnecting: {
    label: "Mất kết nối — đang kết nối lại…",
    dot: "bg-terracotta animate-blink",
    text: "text-terracotta",
  },
  offline: {
    label: "Phiên đăng nhập đã hết hạn — vui lòng đăng nhập lại",
    dot: "bg-terracotta",
    text: "text-terracotta",
  },
};

export function ChatHeader({ status, conn = "online" }: { status: CustStatus; conn?: ConnState }) {
  const s = CUST_STATUS[status];
  const line = CONN_LINE[conn] ?? { label: s.label, dot: s.dot, text: "text-faint" };
  return (
    <div className="flex items-center gap-[13px]">
      <Image
        src="/icon-192.png"
        alt="ThriftYourStyle"
        width={40}
        height={40}
        className="h-10 w-10 flex-none rounded-[11px] object-cover"
      />
      <div>
        <div className="font-serif text-[22px] leading-[1.1] text-ink">Trợ lý ThriftYourStyle</div>
        <div className="mt-[3px] flex items-center gap-[7px]" role="status" aria-live="polite">
          <span className={`h-[7px] w-[7px] flex-none rounded-full ${line.dot}`} />
          <span className={`text-[13px] ${line.text}`}>{line.label}</span>
        </div>
      </div>
    </div>
  );
}
