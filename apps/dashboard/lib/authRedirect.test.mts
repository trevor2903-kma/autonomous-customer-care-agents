// Chạy: node --test apps/dashboard/lib/*.test.mts (Node ≥ 23.6 tự bỏ type TS — không cần thêm dependency).
import test from "node:test";
import assert from "node:assert/strict";
import { afterLoginPath, loginUrl } from "./authRedirect.ts";

test("loginUrl mang theo trang đang mở (kèm query), mã hoá an toàn", () => {
  assert.equal(loginUrl("/admin/abc-123"), "/login?next=%2Fadmin%2Fabc-123");
  assert.equal(loginUrl("/admin?filter=queue"), "/login?next=%2Fadmin%3Ffilter%3Dqueue");
  assert.equal(loginUrl("/chat"), "/login?next=%2Fchat");
});

test("loginUrl: trang gốc / chính /login → không mang next (không lồng next=/login…)", () => {
  assert.equal(loginUrl("/"), "/login");
  assert.equal(loginUrl("/login"), "/login");
  assert.equal(loginUrl("/login?next=%2Fadmin"), "/login");
});

test("afterLoginPath: next thuộc khu vực của vai → quay lại đúng trang đó", () => {
  assert.equal(afterLoginPath("/admin/abc-123", "admin"), "/admin/abc-123");
  assert.equal(afterLoginPath("/admin?filter=queue", "admin"), "/admin?filter=queue");
  assert.equal(afterLoginPath("/admin", "admin"), "/admin");
  assert.equal(afterLoginPath("/chat", "customer"), "/chat");
});

test("afterLoginPath: next của vai KHÁC → trang mặc định của vai mình", () => {
  assert.equal(afterLoginPath("/admin/abc-123", "customer"), "/chat");
  assert.equal(afterLoginPath("/chat", "admin"), "/admin");
});

test("afterLoginPath: thiếu next / link ngoài / tiền tố giả → trang mặc định (chống open redirect)", () => {
  assert.equal(afterLoginPath(null, "admin"), "/admin");
  assert.equal(afterLoginPath("", "admin"), "/admin");
  assert.equal(afterLoginPath("//evil.com/admin", "admin"), "/admin");
  assert.equal(afterLoginPath("https://evil.com/admin", "admin"), "/admin");
  assert.equal(afterLoginPath("/administrator", "admin"), "/admin");
  assert.equal(afterLoginPath("/chatroom", "customer"), "/chat");
});
