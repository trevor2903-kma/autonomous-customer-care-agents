// Chạy: node --test apps/dashboard/lib/*.test.mts (Node ≥ 23.6 tự bỏ type TS — không cần thêm dependency).
import test from "node:test";
import assert from "node:assert/strict";
import { isSendKey, showCharCounter } from "./chatInput.ts";

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

test("bộ đếm ký tự chỉ hiện khi đã dùng ≥ 90% trần (UX-01.2)", () => {
  assert.equal(showCharCounter(0, 2000), false);
  assert.equal(showCharCounter(1799, 2000), false);
  assert.equal(showCharCounter(1800, 2000), true);
  assert.equal(showCharCounter(2000, 2000), true);
});
