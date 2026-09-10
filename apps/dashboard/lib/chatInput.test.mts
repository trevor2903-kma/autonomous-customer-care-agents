// Chạy: node --test apps/dashboard/lib/*.test.mts (Node ≥ 23.6 tự bỏ type TS — không cần thêm dependency).
import test from "node:test";
import assert from "node:assert/strict";
import { effectiveLength, isSendKey, showCharCounter } from "./chatInput.ts";

test("Enter gửi, Shift+Enter xuống dòng, phím khác không gửi (UX-01.1)", () => {
  assert.equal(isSendKey({ key: "Enter", shiftKey: false }), true);
  assert.equal(isSendKey({ key: "Enter", shiftKey: true }), false);
  assert.equal(isSendKey({ key: "a", shiftKey: false }), false);
});

test("không gửi khi bộ gõ IME đang ghép chữ (isComposing, hoặc keyCode 229 của Safari)", () => {
  assert.equal(isSendKey({ key: "Enter", shiftKey: false, isComposing: true }), false);
  assert.equal(isSendKey({ key: "Enter", shiftKey: false, isComposing: false, keyCode: 229 }), false);
  assert.equal(isSendKey({ key: "Enter", shiftKey: false, isComposing: false, keyCode: 13 }), true);
});

test("máy cảm ứng: Enter xuống dòng (bàn phím ảo không có Shift+Enter), gửi bằng nút (UX-01.1)", () => {
  assert.equal(isSendKey({ key: "Enter", shiftKey: false, keyCode: 13 }, true), false);
  assert.equal(isSendKey({ key: "Enter", shiftKey: false, keyCode: 13 }, false), true);
});

test("độ dài đếm như backend (sau NFKC): '…' → '...' nên tin lọt trần ở FE không bị server cắt (UX-01.2)", () => {
  assert.equal(effectiveLength("abc"), 3);
  assert.equal(effectiveLength("…"), 3);
  const pasted = "…".repeat(700);
  assert.equal(pasted.length, 700, "ô nhập (maxLength) đếm 700");
  assert.ok(effectiveLength(pasted) > 2000, "backend đếm 2100 → vượt trần");
});

test("bộ đếm ký tự chỉ hiện khi đã dùng ≥ 90% trần (UX-01.2)", () => {
  assert.equal(showCharCounter(0, 2000), false);
  assert.equal(showCharCounter(1799, 2000), false);
  assert.equal(showCharCounter(1800, 2000), true);
  assert.equal(showCharCounter(2000, 2000), true);
});
