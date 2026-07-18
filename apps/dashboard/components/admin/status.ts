// Map trạng thái → nhãn + màu (design). Dùng chung cho pill ở danh sách, header detail, hàng đợi.
export type StatusMeta = { label: string; color: string; soft: string };

const NEUTRAL: StatusMeta = { label: "—", color: "#8E887B", soft: "#F0EDE6" };

export const STATUS_META: Record<string, StatusMeta> = {
  NEW: { label: "Mới", color: "#8E887B", soft: "#F0EDE6" },
  ACTIVE_AI: { label: "AI đang xử lý", color: "#6B7A4F", soft: "#EEF0E6" },
  REPLIED: { label: "Đã trả lời", color: "#5B7A5B", soft: "#E8EFE6" },
  AWAITING_CUSTOMER: { label: "Chờ khách phản hồi", color: "#8E887B", soft: "#F0EDE6" },
  PENDING_APPROVAL: { label: "Chờ duyệt nháp", color: "#B98534", soft: "#F7EFDD" },
  IN_HUMAN_QUEUE: { label: "Chờ nhận ca", color: "#B25B3C", soft: "#F6E7DF" },
  HUMAN_HANDLING: { label: "Nhân viên đang xử lý", color: "#5A6B84", soft: "#E8ECF3" },
  RESOLVED: { label: "Đã đóng", color: "#8E887B", soft: "#F0EDE6" },
  CLOSED: { label: "Đã đóng", color: "#8E887B", soft: "#F0EDE6" },
};

export function statusMeta(status?: string | null): StatusMeta {
  if (!status) return NEUTRAL;
  return STATUS_META[status] ?? { ...NEUTRAL, label: status };
}

// Bộ lọc danh sách (10a). `key` cũng là giá trị ?filter= dùng chung với nav sidebar.
export type FilterKey = "all" | "active" | "queue" | "approval" | "handling" | "done";

export const FILTERS: { key: FilterKey; label: string; statuses: string[] }[] = [
  { key: "all", label: "Tất cả", statuses: [] },
  { key: "active", label: "Đang xử lý (AI)", statuses: ["NEW", "ACTIVE_AI", "REPLIED", "AWAITING_CUSTOMER"] },
  { key: "queue", label: "Chờ nhận ca", statuses: ["IN_HUMAN_QUEUE"] },
  { key: "approval", label: "Chờ duyệt nháp", statuses: ["PENDING_APPROVAL"] },
  { key: "handling", label: "Đang tiếp quản", statuses: ["HUMAN_HANDLING"] },
  { key: "done", label: "Đã đóng", statuses: ["RESOLVED", "CLOSED"] },
];

export function filterByKey(key: string): (typeof FILTERS)[number] {
  return FILTERS.find((f) => f.key === key) ?? FILTERS[0];
}
