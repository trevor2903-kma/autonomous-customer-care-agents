// Chạy: node --test apps/dashboard/lib/*.test.mts (Node ≥ 23.6 tự bỏ type TS — không cần thêm dependency).
import test from "node:test";
import assert from "node:assert/strict";
import { dayKey, dayLabel, startsNewDay } from "./dayDivider.ts";

// Mốc "bây giờ" cố định (giờ máy) để nhãn hôm nay/hôm qua không phụ thuộc lúc chạy test.
const now = new Date(2026, 8, 14, 22, 9); // T2 14/09/2026
const at = (y: number, m: number, d: number, h = 12, min = 0) =>
  new Date(y, m - 1, d, h, min).toISOString();

test("nhãn chip: hôm nay / hôm qua gọi theo tên, ngày cũ hơn ghi thứ + ngày/tháng/năm", () => {
  assert.equal(dayLabel(at(2026, 9, 14, 8, 30), now), "Hôm nay");
  assert.equal(dayLabel(at(2026, 9, 13, 23, 59), now), "Hôm qua");
  assert.equal(dayLabel(at(2026, 9, 11), now), "T6 11/09/2026");
  assert.equal(dayLabel(at(2026, 9, 13), new Date(2026, 8, 13)), "Hôm nay");
});

test("chủ nhật ghi 'CN', thứ bảy ghi 'T7'", () => {
  assert.equal(dayLabel(at(2026, 9, 6), now), "CN 06/09/2026"); // 06/09/2026 là chủ nhật
  assert.equal(dayLabel(at(2026, 9, 5), now), "T7 05/09/2026");
});

test("cùng ngày (khác giờ) KHÔNG mở ngày mới; tin đầu danh sách luôn có chip", () => {
  assert.equal(startsNewDay(at(2026, 9, 14, 22, 9), at(2026, 9, 14, 0, 1)), false);
  assert.equal(startsNewDay(at(2026, 9, 14), at(2026, 9, 13, 23, 59)), true);
  assert.equal(startsNewDay(at(2026, 9, 14), undefined), true);
});

test("chuỗi thời gian hỏng/thiếu → không nhãn, không chip (thà thiếu còn hơn ghi sai ngày)", () => {
  assert.equal(dayKey("không phải ngày"), "");
  assert.equal(dayLabel("không phải ngày", now), "");
  assert.equal(dayLabel(undefined, now), "");
  assert.equal(startsNewDay("không phải ngày", at(2026, 9, 14)), false);
  assert.equal(startsNewDay(undefined, undefined), false);
});
