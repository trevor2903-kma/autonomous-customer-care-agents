// Chạy: node --test apps/dashboard/lib/*.test.mts (Node ≥ 23.6 tự bỏ type TS — không cần thêm dependency).
import test from "node:test";
import assert from "node:assert/strict";
import {
  RECONNECT_MAX_MS,
  asString,
  backoffDelay,
  newClientMsgId,
  parseFrame,
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
