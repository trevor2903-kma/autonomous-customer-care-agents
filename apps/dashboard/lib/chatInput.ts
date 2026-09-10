// Luật phím + bộ đếm của ô nhập khách (THUẦN — test node --test apps/dashboard/lib/*.test.mts).

type KeyLike = { key: string; shiftKey: boolean; isComposing?: boolean; keyCode?: number };

/** Enter gửi, Shift+Enter xuống dòng (UX-01.1); KHÔNG gửi khi bộ gõ (IME) đang ghép chữ — Enter lúc đó là để
 *  chốt chữ. Safari bắn keydown kết thúc ghép với isComposing=false nhưng keyCode 229 → chặn cả hai.
 *  Máy cảm ứng (`coarse` — bàn phím ảo không có Shift+Enter) → Enter LUÔN xuống dòng, gửi bằng nút "Gửi". */
export function isSendKey(e: KeyLike, coarse = false): boolean {
  return !coarse && e.key === "Enter" && !e.shiftKey && !e.isComposing && e.keyCode !== 229;
}

/** Độ dài như backend đếm (UX-01.2): Lớp A chuẩn hoá NFKC TRƯỚC khi cắt ở `max_message_chars` (core/sanitize.py),
 *  mà NFKC có thể làm chữ DÀI ra ("…" → "...", "½" → "1⁄2"; iOS tự đổi "..." thành "…"). Đếm theo bản đã chuẩn
 *  hoá thì tin lọt trần ở FE không bị server cắt âm thầm. */
export function effectiveLength(text: string): number {
  return text.normalize("NFKC").length;
}

/** Bộ đếm ký tự chỉ hiện khi đã dùng ≥ 90% trần (UX-01.2). */
export function showCharCounter(length: number, max: number): boolean {
  return length >= Math.floor(max * 0.9);
}
