// Chạy: node --test apps/dashboard/lib/*.test.mts (Node ≥ 23.6 tự bỏ type TS — không cần thêm dependency).
import test from "node:test";
import assert from "node:assert/strict";
import {
  absorbOwnEcho,
  appendUnique,
  markEchoPending,
  markFailed,
  markSending,
  markSent,
  mergeAdminMessages,
  reconcileThread,
  senderToFrom,
  unconfirmedOwn,
} from "./messageMerge.ts";

function ids() {
  let n = 100;
  return () => n++;
}
const timeOf = (iso: string) => iso.slice(11, 16);
const th = (id: string, sender: string, content: string, client_msg_id: string | null = null) => ({
  id,
  conversation_id: "conv-1",
  sender,
  content,
  created_at: "2026-09-10T10:00:00Z",
  client_msg_id,
});

test("nạp đầu: lịch sử đứng TRƯỚC frame lỡ tới lúc tải; frame đã có trong lịch sử không bị nhân đôi", () => {
  const local = [
    { id: 1, from: "ai" as const, text: "trả lời 2", time: "t", messageId: "m2" },
    { id: 2, from: "ai" as const, text: "trả lời 3", time: "t", messageId: "m3" },
  ];
  const out = reconcileThread(local, [th("m1", "customer", "hỏi"), th("m2", "ai", "trả lời 2")], ids(), timeOf);
  assert.deepEqual(
    out.map((m) => m.text),
    ["hỏi", "trả lời 2", "trả lời 3"],
  );
  assert.equal(out[1].id, 1, "bong bóng đã hiện giữ nguyên key React");
  assert.equal(out[1].fromHistory, true);
});

test("nối lại: tin mình đã lưu thành bản lịch sử (đã gửi); tin đang gửi / chưa gửi được giữ ở cuối, đúng thứ tự", () => {
  const local = [
    { id: 1, from: "ai" as const, text: "cũ", time: "t", messageId: "m1", fromHistory: true },
    { id: 2, from: "you" as const, text: "a", time: "t", clientMsgId: "c1", sendState: "sending" as const },
    { id: 3, from: "you" as const, text: "b", time: "t", clientMsgId: "c2", sendState: "failed" as const },
    { id: 4, from: "you" as const, text: "c", time: "t", clientMsgId: "c3", sendState: "sending" as const },
  ];
  const out = reconcileThread(local, [th("m1", "ai", "cũ"), th("m4", "customer", "a", "c1")], ids(), timeOf);
  assert.deepEqual(
    out.map((m) => [m.text, m.sendState ?? null]),
    [
      ["cũ", null],
      ["a", null],
      ["b", "failed"],
      ["c", "sending"],
    ],
  );
  assert.equal(out[1].id, 2, "tin vừa được lưu giữ key của bong bóng đang gửi");
  assert.equal(out[1].messageId, "m4");
});

test("ghép lại nhiều lần với cùng lịch sử là idempotent (không nạp lịch sử hai lần)", () => {
  const thread = [th("m1", "customer", "hỏi"), th("m2", "admin", "chào bạn")];
  const once = reconcileThread([], thread, ids(), timeOf);
  const twice = reconcileThread(once, thread, ids(), timeOf);
  assert.deepEqual(twice, once);
  assert.deepEqual(
    twice.map((m) => m.from),
    ["you", "admin"],
  );
});

test("thông báo tạm (không message_id, vd rate_limited) được giữ sau khi ghép", () => {
  const local = [{ id: 7, from: "system" as const, text: "gửi hơi nhanh", time: "t" }];
  const out = reconcileThread(local, [th("m1", "customer", "hỏi")], ids(), timeOf);
  assert.deepEqual(
    out.map((m) => m.text),
    ["hỏi", "gửi hơi nhanh"],
  );
});

test("vòng đời gửi: ack → sent (+message_id); quá hạn chỉ hạ tin đang gửi; gửi lại về sending", () => {
  const base = [
    { key: "a", clientMsgId: "c1", sendState: "sending" as const },
    { key: "b", clientMsgId: "c2", sendState: "sent" as const, messageId: "m2" },
  ];
  const acked = markSent(base, "c1", "m1");
  assert.equal(acked[0].sendState, "sent");
  assert.equal(acked[0].messageId, "m1");
  assert.equal(markSent(base, "c2").at(1)?.messageId, "m2", "ack không kèm message_id giữ id cũ");

  assert.equal(markFailed(base, "c1")[0].sendState, "failed");
  assert.equal(markFailed(base, "c2")[1].sendState, "sent", "ack tới trước quá hạn → vẫn đã gửi");

  const failed = markFailed(base, "c1");
  assert.equal(markSending(failed, "c1")[0].sendState, "sending");
  assert.equal(markSending(base, "c2")[1].sendState, "sent");
});

test("appendUnique: frame lặp cùng message_id không thêm lần hai; tin không có id luôn được thêm", () => {
  const list = [{ key: "1", messageId: "m1" }];
  assert.equal(appendUnique(list, { key: "2", messageId: "m1" }), list);
  assert.equal(appendUnique(list, { key: "3", messageId: "m9" }).length, 2);
  assert.equal(appendUnique(list, { key: "4", messageId: null }).length, 2);
});

test("admin: tin realtime/ack đã có trong bản REST vừa nạp lại → không trùng; phần chưa lưu giữ lại", () => {
  const fetched = [
    { id: "m1", sender: "customer", content: "hỏi", created_at: "2026-09-10T10:00:00Z" },
    { id: "m2", sender: "admin", content: "đáp", created_at: "2026-09-10T10:01:00Z", client_msg_id: "c2" },
  ];
  const live = [
    { key: "m1", sender: "customer", content: "hỏi", at: "x", messageId: "m1" },
    { key: "c2", sender: "admin", content: "đáp", at: "x", clientMsgId: "c2", sendState: "sending" as const },
    { key: "m3", sender: "ai", content: "mới", at: "x", messageId: "m3" },
    { key: "c4", sender: "admin", content: "lỗi", at: "x", clientMsgId: "c4", sendState: "failed" as const },
  ];
  const out = mergeAdminMessages(fetched, live);
  assert.deepEqual(
    out.map((m) => m.content),
    ["hỏi", "đáp", "mới", "lỗi"],
  );
  assert.equal(out[1].sendState, undefined, "tin admin đã lưu hiện bằng bản REST (đã gửi)");
});

const you = (id: number, text: string, cid: string, sendState: "sending" | "sent" | "failed") => ({
  id,
  from: "you" as const,
  text,
  time: "t",
  clientMsgId: cid,
  sendState,
});

test("FE-01.4: nối lại → gửi lại tin 'đang gửi' LẪN 'đã gửi' mà lịch sử chưa có; tin đã lưu / chưa gửi được thì không", () => {
  const local = [
    you(1, "đã lưu", "c1", "sent"),
    you(2, "đã ack nhưng chưa lưu", "c2", "sent"),
    you(3, "chưa ack", "c3", "sending"),
    you(4, "lỗi", "c4", "failed"),
    { id: 5, from: "ai" as const, text: "trả lời", time: "t", messageId: "m9" },
  ];
  assert.deepEqual(unconfirmedOwn(local, [th("m1", "customer", "đã lưu", "c1")]), [
    { cid: "c2", text: "đã ack nhưng chưa lưu" },
    { cid: "c3", text: "chưa ack" },
  ]);
});

test("FE-01.6: tiếng vọng tin mình gửi trước lúc nối lại (from customer qua hub) gắn vào CHÍNH bong bóng đó", () => {
  const list = markEchoPending([you(1, "Kiểm tra   đơn hàng…", "c1", "sent")], new Set(["c1"]));
  assert.equal(list[0].echoPending, true);
  // Server lưu/phát bản đã chuẩn hoá (NFKC: "…" → "...", gộp khoảng trắng).
  const out = absorbOwnEcho(list, "Kiểm tra đơn hàng...", "m1");
  assert.ok(out);
  assert.equal(out.length, 1, "không thêm bong bóng 'bạn' thứ hai");
  assert.equal(out[0].messageId, "m1");
  assert.equal(out[0].echoPending, false);
  assert.equal(absorbOwnEcho(out, "Kiểm tra đơn hàng...", "m2"), null, "đã nhận rồi → tin trùng chữ sau là tin mới");
});

test("FE-01.6: tab khác gửi đúng câu mình từng gửi (bong bóng KHÔNG chờ tiếng vọng) → không nuốt, thêm như thường", () => {
  const list = [you(1, "Kiểm tra đơn hàng của mình", "c1", "sent")];
  assert.equal(absorbOwnEcho(list, "Kiểm tra đơn hàng của mình", "m7"), null);
  assert.equal(absorbOwnEcho(markEchoPending(list, new Set(["c1"])), "câu khác", "m8"), null);
});

test("FE-01.6: tin gửi lại bị hết hạn ack ('chưa gửi được') mà tiếng vọng tới → đã lưu, tức 'đã gửi'", () => {
  const list = markEchoPending([you(1, "a", "c1", "failed")], new Set(["c1"]));
  assert.equal(absorbOwnEcho(list, "a", "m1")?.[0].sendState, "sent");
});

test("senderToFrom: khách → you, admin → admin, còn lại → ai", () => {
  assert.equal(senderToFrom("customer"), "you");
  assert.equal(senderToFrom("admin"), "admin");
  assert.equal(senderToFrom("ai"), "ai");
});
