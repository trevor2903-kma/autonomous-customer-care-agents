// Chip ngăn cách theo ngày trong box chat (kiểu Zalo): giữa hai tin khác NGÀY chèn một chip căn giữa
// ("Hôm nay" · "Hôm qua" · "T6 11/09/2026"); bong bóng vẫn chỉ hiện giờ. Thuần, không import runtime —
// test: node --test apps/dashboard/lib/*.test.mts.

const WEEKDAY = ["CN", "T2", "T3", "T4", "T5", "T6", "T7"];
const pad = (n: number) => String(n).padStart(2, "0");

const keyOf = (d: Date) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;

/** Khoá ngày theo GIỜ MÁY người xem: "2026-09-11". Hai tin cùng khoá = cùng ngày → không chèn chip.
 *  Chuỗi thời gian hỏng/thiếu → "" (không chèn chip, không hiện nhãn sai). */
export function dayKey(iso: string | null | undefined): string {
  if (!iso) return "";
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? "" : keyOf(d);
}

/** Nhãn chip: hôm nay/hôm qua gọi theo tên, còn lại "T6 11/09/2026". `now` truyền được để test. */
export function dayLabel(iso: string | null | undefined, now: Date = new Date()): string {
  if (!iso) return "";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "";
  const key = keyOf(d);
  if (key === keyOf(now)) return "Hôm nay";
  const yesterday = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 1);
  if (key === keyOf(yesterday)) return "Hôm qua";
  return `${WEEKDAY[d.getDay()]} ${pad(d.getDate())}/${pad(d.getMonth() + 1)}/${d.getFullYear()}`;
}

/** Tin `iso` có mở một ngày MỚI so với tin liền trước (`prevIso`) không → có chèn chip trước nó không.
 *  Tin đầu danh sách (prevIso rỗng) LUÔN có chip, như Zalo. */
export function startsNewDay(iso: string | null | undefined, prevIso: string | null | undefined): boolean {
  const key = dayKey(iso);
  return key !== "" && key !== dayKey(prevIso);
}
