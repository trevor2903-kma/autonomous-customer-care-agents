// Nhãn tiếng Việt cho định danh kỹ thuật của backend (slice obs P4/P5).
// GIỮ NGUYÊN dạng mono các định danh thật (khóa intent, `trc_…`, tên `.md`) — chỉ dịch phần MÔ TẢ.

export const OUTCOME_LABEL: Record<string, string> = {
  sent: "Gửi thẳng",
  held_for_approval: "Giữ nháp chờ duyệt",
  queued_for_human: "Chuyển nhân viên",
  error: "Lỗi hệ thống",
};

// Tông màu theo kết cục (bảng màu design §2).
export const OUTCOME_TONE: Record<string, { text: string; bg: string; border: string }> = {
  sent: { text: "text-olive-dark", bg: "bg-olive-soft", border: "border-line-olive" },
  held_for_approval: { text: "text-gold", bg: "bg-gold-soft", border: "border-gold/30" },
  queued_for_human: { text: "text-terracotta", bg: "bg-terracotta-soft", border: "border-terracotta-line" },
  error: { text: "text-terracotta-ink", bg: "bg-terracotta-soft", border: "border-terracotta-line" },
};

// Quyết định của Agent 3 (khác kết cục giao — một ca auto_reply vẫn có thể bị gate giữ nháp).
export const ACTION_LABEL: Record<string, string> = {
  auto_reply: "Tự động trả lời",
  human_handoff: "Chuyển nhân viên",
};

// Bước trong nhật ký kiểm toán → tên tác tử hiển thị.
export const NODE_LABEL: Record<string, string> = {
  customer: "Tin nhắn khách",
  intent: "Agent 1 · Phân loại ý định",
  knowledge: "Agent 2 · Truy hồi tri thức",
  decision: "Agent 3 · Ra quyết định",
  response: "Agent 4 · Soạn phản hồi",
  delivery: "Hệ thống gửi",
};

export const NODE_SHORT: Record<string, string> = {
  customer: "Tin nhắn khách",
  intent: "Phân loại ý định",
  knowledge: "Truy hồi tri thức",
  decision: "Ra quyết định",
  response: "Soạn phản hồi",
  delivery: "Hệ thống gửi",
};

// Hành động ghi trong audit_log → câu mô tả cho người đọc.
export const AUDIT_ACTION_LABEL: Record<string, string> = {
  message_received: "Nhận tin nhắn mới, tạo lượt xử lý",
  classify: "Phân loại ý định và bóc tách thực thể",
  retrieve: "Tìm kiếm vector trên kho tri thức",
  auto_reply: "Đối chiếu cờ bất định → tự động trả lời",
  human_handoff: "Đối chiếu cờ bất định → chuyển nhân viên",
  response: "Soạn phản hồi bám tri thức",
  sent: "Gửi thẳng phản hồi cho khách",
  held_for_approval: "Giữ nháp chờ nhân viên duyệt",
  queued_for_human: "Đưa vào hàng đợi nhân viên",
  error: "Lượt xử lý gặp lỗi",
};

// Cờ bất định → giải thích ngắn (dùng ở phần bóc tách lý do chuyển người).
export const FLAG_LABEL: Record<string, string> = {
  low_retrieval_score: "Điểm truy hồi thấp",
  no_relevant_knowledge: "Không có tri thức liên quan",
  out_of_domain: "Ngoài phạm vi shop",
  multi_intent: "Khách hỏi nhiều việc",
  llm_unavailable: "Không gọi được mô hình",
  search_error: "Lỗi truy hồi",
  ambiguous_intent: "Ý định mơ hồ",
  hallucination_risk: "Thiếu căn cứ để trả lời",
};

export const KB_TYPE_LABEL: Record<string, string> = {
  faq: "Hỏi đáp",
  case: "Quy trình xử lý",
  reference: "Tra cứu",
  promotion: "Khuyến mãi",
  upload: "Tải lên",
};

export const SEVERITY_LABEL: Record<string, string> = {
  high: "cao",
  medium: "trung bình",
  low: "thấp",
};

export const PRIORITY_LABEL: Record<string, string> = {
  high: "cao",
  medium: "trung bình",
  low: "thấp",
};

export function parseBlockingFlags(reason?: string | null): string[] {
  const m = reason?.match(/\[(.*)\]/);
  if (!m) return [];
  return m[1]
    .split(",")
    .map((s) => s.trim().replace(/^['"]|['"]$/g, ""))
    .filter(Boolean);
}

export function formatEscalationReason(reason?: string | null): string {
  if (!reason) return "—";
  const flags = parseBlockingFlags(reason);
  if (flags.length > 0) {
    const translated = flags.map((f) => FLAG_LABEL[f] ?? f).join(", ");
    return `Cờ chặn: ${translated}`;
  }
  return reason;
}

export function fmtMs(ms: number | null | undefined): string {
  if (ms === null || ms === undefined) return "—";
  return ms < 1000 ? `${ms}ms` : `${(ms / 1000).toFixed(2)}s`;
}

export function fmtTime(iso: string): string {
  const d = new Date(iso);
  const today = new Date();
  const sameDay = d.toDateString() === today.toDateString();
  const hhmm = d.toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" });
  return sameDay ? `Hôm nay ${hhmm}` : `${d.toLocaleDateString("vi-VN")} ${hhmm}`;
}

export function fmtClock(iso: string): string {
  return new Date(iso).toLocaleTimeString("vi-VN", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}
