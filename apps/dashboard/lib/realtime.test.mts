// Chạy: node --test apps/dashboard/lib/*.test.mts (Node ≥ 23.6 tự bỏ type TS — không cần thêm dependency).
import test from "node:test";
import assert from "node:assert/strict";
import {
  INBOX_WINDOW_MS,
  RECONNECT_MAX_MS,
  asString,
  backoffDelay,
  convStateOf,
  createInboxBatcher,
  newClientMsgId,
  parseFrame,
  stopAfterAuthClose,
  type InboxRefresh,
} from "./realtime.ts";

const UUID_V4 = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/;

test("backoff nối lại 1s → 2s → 4s → 8s rồi chặn trần 15s (FE-01.2)", () => {
  assert.deepEqual(
    [0, 1, 2, 3, 4, 5, 20].map(backoffDelay),
    [1000, 2000, 4000, 8000, 15000, 15000, 15000],
  );
  assert.equal(backoffDelay(-3), 1000);
  assert.equal(backoffDelay(1e6), RECONNECT_MAX_MS);
});

test("client_msg_id: dùng crypto.randomUUID khi trình duyệt có", () => {
  assert.equal(newClientMsgId({ randomUUID: () => "from-crypto" }), "from-crypto");
});

test("client_msg_id: không có randomUUID (http qua IP LAN) → uuid v4 từ getRandomValues", () => {
  const id = newClientMsgId({
    getRandomValues: (a) => {
      a.fill(0xff);
      return a;
    },
  });
  assert.match(id, UUID_V4);
});

test("client_msg_id: không có crypto nào → vẫn là uuid v4 và không trùng", () => {
  const ids = Array.from({ length: 300 }, () => newClientMsgId({}));
  for (const id of ids) assert.match(id, UUID_V4);
  assert.equal(new Set(ids).size, ids.length);
});

test("parseFrame: chỉ nhận object JSON, frame hỏng → null (không làm sập màn chat)", () => {
  assert.deepEqual(parseFrame('{"type":"ack","client_msg_id":"c1"}'), {
    type: "ack",
    client_msg_id: "c1",
  });
  assert.equal(parseFrame("not json"), null);
  assert.equal(parseFrame("[1,2]"), null);
  assert.equal(parseFrame("null"), null);
  assert.equal(parseFrame(42), null);
});

test("asString: field frame không phải chuỗi → null", () => {
  assert.equal(asString("x"), "x");
  assert.equal(asString(null), null);
  assert.equal(asString(3), null);
});

test("FE-01.2: đóng 4401 chỉ dừng hẳn khi REST xác nhận hết phiên (401) hoặc vai trong DB đã khác", () => {
  assert.equal(stopAfterAuthClose(null, "customer"), true, "/me 401 → token hỏng / hết hạn");
  assert.equal(stopAfterAuthClose(undefined, "customer"), false, "DB lỗi (5xx) / mạng / quá hạn → nối lại");
  assert.equal(stopAfterAuthClose({ role: "customer" }, "customer"), false, "token còn dùng được → 4401 thoáng qua");
  assert.equal(stopAfterAuthClose({ role: "customer" }, "admin"), true, "admin đã bị hạ quyền");
  assert.equal(stopAfterAuthClose({ role: "admin" }), false);
});

test("FE-03.2: frame system/status — server đọc lỗi (status null) → người giữ ca 'chưa biết', không phải 'không ai'", () => {
  assert.deepEqual(convStateOf({ type: "system", status: null, assigned_admin_id: null }), {
    status: null,
    assigned: undefined,
  });
  assert.deepEqual(convStateOf({ type: "status", status: "HUMAN_HANDLING", assigned_admin_id: "a1" }), {
    status: "HUMAN_HANDLING",
    assigned: "a1",
  });
  assert.deepEqual(convStateOf({ type: "status", status: "IN_HUMAN_QUEUE", assigned_admin_id: null }), {
    status: "IN_HUMAN_QUEUE",
    assigned: null,
  });
  assert.deepEqual(convStateOf({ type: "system", status: "REPLIED" }), { status: "REPLIED", assigned: undefined });
});

test("FE-01.5: inbox làm tươi TỐI ĐA một lần mỗi cửa sổ 3 s — sự kiện dồn dập không nhân số lần nạp danh sách", (t) => {
  t.mock.timers.enable({ apis: ["setTimeout"] });
  const flushes: InboxRefresh[] = [];
  const b = createInboxBatcher((r) => flushes.push(r));
  // 30 sự kiện rải trong 2,97 s (khách nhắn liên tục + trả lời AI): sự kiện đầu mở cửa sổ, cả loạt gộp một lần.
  for (let i = 0; i < 30; i++) {
    b.push("message", "c1");
    t.mock.timers.tick(99);
  }
  assert.equal(flushes.length, 0, "cửa sổ 3 s chưa đóng");
  t.mock.timers.tick(INBOX_WINDOW_MS);
  assert.equal(flushes.length, 1);
  b.dispose();
});

test("FE-01.5: hàng đợi chuyển tiếp chỉ nạp lại khi cửa sổ có sự kiện status; tin mới chỉ nạp lại danh sách", (t) => {
  t.mock.timers.enable({ apis: ["setTimeout"] });
  const flushes: InboxRefresh[] = [];
  const b = createInboxBatcher((r) => flushes.push(r));
  b.push("message", "c1");
  b.push("message", "c2");
  t.mock.timers.tick(INBOX_WINDOW_MS);
  assert.deepEqual(flushes, [{ escalations: false, changed: [] }]);
  b.push("message", "c3");
  b.push("status", "c2");
  b.push("status", "c2");
  t.mock.timers.tick(INBOX_WINDOW_MS);
  assert.deepEqual(flushes[1], { escalations: true, changed: ["c2"] });
  assert.equal(flushes.length, 2);
  b.dispose();
});

test("FE-01.5: nối lại → nạp lại ĐỦ ngay (cả hàng đợi) và gộp luôn cửa sổ đang chờ; gỡ (unmount) → không nạp nữa", (t) => {
  t.mock.timers.enable({ apis: ["setTimeout"] });
  const flushes: InboxRefresh[] = [];
  const b = createInboxBatcher((r) => flushes.push(r));
  b.push("status", "c1");
  b.flushNow();
  assert.deepEqual(flushes, [{ escalations: true, changed: ["c1"] }]);
  b.flushNow();
  assert.deepEqual(flushes[1], { escalations: true, changed: [] }, "sự kiện lúc rớt đã lỡ → vẫn nạp lại hàng đợi");
  t.mock.timers.tick(INBOX_WINDOW_MS);
  assert.equal(flushes.length, 2, "cửa sổ đã gộp vào lần nạp ngay — không nạp thêm");
  b.push("message", "c1");
  b.dispose();
  t.mock.timers.tick(INBOX_WINDOW_MS);
  assert.equal(flushes.length, 2);
});
