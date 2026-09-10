// Chạy: node --test apps/dashboard/lib/*.test.mts (Node ≥ 23.6 tự bỏ type TS — không cần thêm dependency).
import test from "node:test";
import assert from "node:assert/strict";
import { CUST_TURN_IDLE, custStatusFrom, custTurnAfter } from "../components/chat/custStatus.ts";

const turn = (over: Partial<typeof CUST_TURN_IDLE> = {}) => ({ ...CUST_TURN_IDLE, ...over });
// Áp lần lượt các frame (như chuỗi frame server gửi xuống một socket khách).
const run = (start: typeof CUST_TURN_IDLE, ...frames: Record<string, unknown>[]) =>
  frames.reduce(custTurnAfter, start);

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

test("UX-02.3: frame status RESOLVED khi đang chờ nhân viên + typing → về 'ai', gỡ typing", () => {
  const out = custTurnAfter(turn({ status: "waiting", typing: true }), {
    type: "status",
    status: "RESOLVED",
    assigned_admin_id: null,
  });
  assert.deepEqual(out, { status: "ai", typing: false, inFlight: 0 });
});

test("UX-02.3: nháp vừa duyệt tới khách (message from ai) khi đang 'review' → về 'ai'; đang chờ nhân viên thì giữ", () => {
  const ai = { type: "message", from: "ai", content: "Dạ…", message_id: "m1" };
  assert.equal(custTurnAfter(turn({ status: "review" }), ai).status, "ai");
  assert.equal(custTurnAfter(turn({ status: "waiting" }), ai).status, "waiting");
  assert.equal(custTurnAfter(turn({ status: "review", typing: true }), ai).typing, false);
});

test("UX-02.3: lượt bị huỷ vì admin tiếp quản giữa chừng (CAS → frame status) → gỡ typing, hết lượt đang chạy", () => {
  const out = run(
    turn({ inFlight: 1 }),
    { type: "ack", client_msg_id: "c1", message_id: null, duplicate: false },
    { type: "typing" },
    { type: "status", status: "HUMAN_HANDLING", assigned_admin_id: "a1" },
  );
  assert.deepEqual(out, { status: "human", typing: false, inFlight: 0 });
});

test("IDEM-XC.1: gợi ý nhanh vẫn khoá trong khe ack→typing (ack tới trước typing vài vòng DB); mở lại khi có trả lời", () => {
  const acked = custTurnAfter(turn({ inFlight: 1 }), {
    type: "ack",
    client_msg_id: "c1",
    message_id: null,
    duplicate: false,
  });
  assert.equal(acked.inFlight, 1, "đã ack nhưng lượt chưa xong → vẫn khoá");
  assert.equal(acked.typing, false);
  assert.deepEqual(run(acked, { type: "typing" }, { type: "reply", content: "x", message_id: "m1" }), {
    status: "ai",
    typing: false,
    inFlight: 0,
  });
});

test("IDEM-XC.1: tin xếp hàng sau lượt đang chạy → trả lời của lượt đầu chưa mở khoá", () => {
  const out = custTurnAfter(turn({ inFlight: 2, typing: true }), { type: "reply", content: "x", message_id: "m1" });
  assert.equal(out.inFlight, 1);
});

test("IDEM-XC.1: không có lượt nào chạy → ack là xong (ca do người xử lý / tin trùng / bị rate limit)", () => {
  const ack = { type: "ack", client_msg_id: "c1", message_id: null, duplicate: false };
  assert.equal(custTurnAfter(turn({ status: "waiting", inFlight: 1 }), ack).inFlight, 0, "status-gate: không typing");
  assert.equal(custTurnAfter(turn({ inFlight: 1 }), { ...ack, duplicate: true }).inFlight, 0);
  assert.equal(
    custTurnAfter(turn({ inFlight: 1 }), { type: "error", code: "rate_limited", client_msg_id: "c1" }).inFlight,
    0,
  );
});

test("IDEM-XC.1: ca sang tay người (handoff / pending / tin nhân viên) → lượt xếp hàng phía sau bị status-gate", () => {
  assert.deepEqual(custTurnAfter(turn({ inFlight: 2, typing: true }), { type: "handoff", content: "x" }), {
    status: "waiting",
    typing: false,
    inFlight: 0,
  });
  assert.deepEqual(custTurnAfter(turn({ inFlight: 2 }), { type: "pending" }), {
    status: "review",
    typing: false,
    inFlight: 0,
  });
  assert.deepEqual(custTurnAfter(turn({ inFlight: 2 }), { type: "message", from: "admin", content: "x" }), {
    status: "human",
    typing: false,
    inFlight: 0,
  });
});

test("lượt không bao giờ âm; frame không liên quan trả nguyên trạng thái", () => {
  assert.equal(custTurnAfter(turn(), { type: "reply", content: "x" }).inFlight, 0);
  const t = turn({ inFlight: 1, typing: true });
  assert.equal(custTurnAfter(t, { type: "message", from: "customer", content: "tab khác" }), t);
  assert.equal(custTurnAfter(t, { type: "system", message: "connected" }), t);
});
