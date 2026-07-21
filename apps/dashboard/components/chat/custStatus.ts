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
