import type { Frame } from "@/lib/realtime";

// Trạng thái hiển thị cho khách (design: custStatus — chấm màu + nhãn).
// Suy từ tín hiệu WS mà khách NHẬN ĐƯỢC, không lộ trạng thái nội bộ của hệ thống.
export type CustStatus = "ai" | "review" | "waiting" | "human";

export const CUST_STATUS: Record<CustStatus, { label: string; dot: string }> = {
  ai: { label: "Đang trò chuyện với Trợ lý AI", dot: "bg-olive" },
  review: { label: "Nhân viên đang kiểm tra phản hồi", dot: "bg-gold" },
  waiting: { label: "Đang chờ nhân viên hỗ trợ", dot: "bg-terracotta" },
  human: { label: "Nhân viên đang hỗ trợ bạn", dot: "bg-steel-2" },
};

// Ô nhập đổi lời nhắc theo trạng thái (design: custInputPlaceholder).
export const CUST_PLACEHOLDER: Record<CustStatus, string> = {
  ai: "Nhập tin nhắn…",
  review: "Nhập tin nhắn…",
  waiting: "Nhân viên sẽ phản hồi sớm…",
  human: "Nhập tin nhắn…",
};

// Trạng thái hiển thị ban đầu suy từ status ca ĐANG MỞ (active_status của /me/thread — slice 11 P6).
export function custStatusFrom(status: string | null | undefined): CustStatus {
  switch (status) {
    case "PENDING_APPROVAL":
      return "review";
    case "IN_HUMAN_QUEUE":
      return "waiting";
    case "HUMAN_HANDLING":
      return "human";
    default:
      return "ai"; // ACTIVE_AI / REPLIED / null … → đang với AI
  }
}

/** Trạng thái lượt phía khách: header (`status`), "đang trả lời…" (`typing`) và số tin đã gửi mà lượt CHƯA xong
 *  (`inFlight`). `inFlight > 0` → khoá gợi ý nhanh (IDEM-XC.1): server `ack` NGAY lúc nhận tin nhưng `typing` chỉ tới
 *  sau vài vòng DB (lâu hơn khi Neon vừa ngủ dậy) — khoá theo typing thôi thì cú bấm thứ hai lọt vào khe ack→typing và
 *  đẻ lượt trùng ("Kiểm tra đơn hàng" còn dính loop-guard clarify → chuyển người oan). */
export type CustTurn = { status: CustStatus; typing: boolean; inFlight: number };

export const CUST_TURN_IDLE: CustTurn = { status: "ai", typing: false, inFlight: 0 };

const settled = (n: number) => Math.max(0, n - 1);

/** Áp MỘT frame server (protocol v2 — contract §4.1) lên trạng thái lượt; frame không liên quan → trả nguyên `t`.
 *  Thuần — test: lib/custStatus.test.mts. */
export function custTurnAfter(t: CustTurn, f: Frame): CustTurn {
  switch (f.type) {
    case "ack":
      // Tin trùng → server không chạy lại lượt. Ca đang do người xử lý (review/waiting/human) → status-gate: không có
      // typing/trả lời nào theo sau → lượt coi như xong ngay khi server nhận tin.
      return f.duplicate === true || t.status !== "ai" ? { ...t, inFlight: settled(t.inFlight) } : t;
    case "error":
      return { ...t, inFlight: settled(t.inFlight) }; // tin bị từ chối (rate_limited) → không có lượt nào
    case "typing":
      return t.typing ? t : { ...t, typing: true };
    case "reply":
      // Trả lời tự động — hội thoại vẫn với AI.
      return { status: "ai", typing: false, inFlight: settled(t.inFlight) };
    case "handoff":
      // Ca vào tay người → lượt còn xếp hàng phía sau đều bị status-gate (không typing / trả lời) → hết lượt chạy.
      return { status: "waiting", typing: false, inFlight: 0 };
    case "pending":
      // Nháp chờ duyệt (08a): gỡ typing, đổi trạng thái, KHÔNG kẹt chờ.
      return { status: "review", typing: false, inFlight: 0 };
    case "status": {
      // Trạng thái ca đổi do người khác (admin tiếp quản/đóng/duyệt/từ chối, tự đóng, tab khác) HOẶC lượt của chính
      // tab này bị huỷ (CAS) → không còn reply nào theo sau: gỡ typing (UX-02.3).
      const status = custStatusFrom(typeof f.status === "string" ? f.status : null);
      return { status, typing: false, inFlight: status === "ai" ? settled(t.inFlight) : 0 };
    }
    case "message":
      if (f.from === "customer") return t; // tin của chính khách ở tab khác — không đổi lượt của tab này
      if (f.from === "admin") return { status: "human", typing: false, inFlight: 0 };
      // AI qua hub: nháp vừa duyệt tới khách → hết "đang kiểm tra" (UX-02.3); trả lời của lượt mà socket cũ đã rớt.
      return {
        status: t.status === "review" ? "ai" : t.status,
        typing: false,
        inFlight: settled(t.inFlight),
      };
    default:
      return t;
  }
}
