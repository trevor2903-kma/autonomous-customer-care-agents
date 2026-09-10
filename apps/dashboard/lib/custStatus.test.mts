// Chạy: node --test apps/dashboard/lib/*.test.mts (Node ≥ 23.6 tự bỏ type TS — không cần thêm dependency).
import test from "node:test";
import assert from "node:assert/strict";
import { custStatusFrom } from "../components/chat/custStatus.ts";

test("frame status → trạng thái khách (UX-02.3): đóng ca / trả lời xong về 'ai', không kẹt spinner chờ", () => {
  assert.equal(custStatusFrom("RESOLVED"), "ai");
  assert.equal(custStatusFrom("CLOSED"), "ai");
  assert.equal(custStatusFrom("REPLIED"), "ai");
  assert.equal(custStatusFrom("AWAITING_CUSTOMER"), "ai");
  assert.equal(custStatusFrom(null), "ai");
});

test("frame status → trạng thái khách: hàng đợi / duyệt nháp / nhân viên đang xử lý", () => {
  assert.equal(custStatusFrom("IN_HUMAN_QUEUE"), "waiting");
  assert.equal(custStatusFrom("PENDING_APPROVAL"), "review");
  assert.equal(custStatusFrom("HUMAN_HANDLING"), "human");
});
