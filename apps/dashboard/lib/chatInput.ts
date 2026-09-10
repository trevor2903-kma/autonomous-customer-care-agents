// Luật phím + bộ đếm của ô nhập khách (THUẦN — test node --test apps/dashboard/lib/*.test.mts).

type KeyLike = { key: string; shiftKey: boolean; isComposing?: boolean; keyCode?: number };

/** Enter gửi, Shift+Enter xuống dòng (UX-01.1); KHÔNG gửi khi bộ gõ (IME) đang ghép chữ — Enter lúc đó là để
 *  chốt chữ. Safari bắn keydown kết thúc ghép với isComposing=false nhưng keyCode 229 → chặn cả hai. */
export function isSendKey(e: KeyLike): boolean {
  return e.key === "Enter" && !e.shiftKey && !e.isComposing && e.keyCode !== 229;
}

/** Bộ đếm ký tự chỉ hiện khi đã dùng ≥ 90% trần (UX-01.2). */
export function showCharCounter(length: number, max: number): boolean {
  return length >= Math.floor(max * 0.9);
}
