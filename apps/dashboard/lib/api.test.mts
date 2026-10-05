// Chạy: node --test apps/dashboard/lib/*.test.mts (Node ≥ 23.6 tự bỏ type TS — không cần thêm dependency).
import test, { afterEach } from "node:test";
import assert from "node:assert/strict";
import { getAdminConversation, login, onSessionExpired } from "./api.ts";

const realFetch = globalThis.fetch;

/** fetch giả: mỗi path trả status cố định; ghi lại các path đã gọi. */
function fakeFetch(statusFor: (path: string) => number): string[] {
  const calls: string[] = [];
  globalThis.fetch = (async (input: RequestInfo | URL) => {
    const path = new URL(String(input)).pathname;
    calls.push(path);
    const status = statusFor(path);
    return new Response(status === 200 ? JSON.stringify({ id: "c1" }) : JSON.stringify({ detail: "x" }), { status });
  }) as typeof fetch;
  return calls;
}

/** "Treo" = chưa settle sau một nhịp timer (fetch giả resolve ngay nên mọi nhánh khác đã xong). */
async function isPending(p: Promise<unknown>): Promise<boolean> {
  const PENDING = Symbol("pending");
  const winner = await Promise.race([p.catch(() => "rejected"), new Promise((r) => setTimeout(() => r(PENDING), 20))]);
  return winner === PENDING;
}

afterEach(() => {
  globalThis.fetch = realFetch;
  onSessionExpired(null);
});

test("401 + refresh hỏng khi ĐANG đăng nhập → gọi handler, nơi gọi KHÔNG nhận lỗi 401 (về /login)", async () => {
  fakeFetch(() => 401);
  let fired = 0;
  onSessionExpired(() => {
    fired++;
    return true;
  });
  assert.equal(await isPending(getAdminConversation("c1")), true);
  assert.equal(fired, 1);
});

test("401 + refresh hỏng khi CHƯA đăng nhập (handler trả false) → nơi gọi nhận lỗi như cũ", async () => {
  fakeFetch(() => 401);
  onSessionExpired(() => false);
  await assert.rejects(getAdminConversation("c1"), /admin conversation 401/);
});

test("401 nhưng refresh thành công → thử lại, trả dữ liệu, KHÔNG coi là hết phiên", async () => {
  let first = true;
  const calls = fakeFetch((path) => {
    if (path === "/api/auth/refresh") return 200;
    if (first) {
      first = false;
      return 401;
    }
    return 200;
  });
  let fired = 0;
  onSessionExpired(() => {
    fired++;
    return true;
  });
  assert.deepEqual(await getAdminConversation("c1"), { id: "c1" });
  assert.equal(fired, 0);
  assert.deepEqual(calls, ["/api/admin/conversations/c1", "/api/auth/refresh", "/api/admin/conversations/c1"]);
});

test("401 ở route đăng nhập (sai mật khẩu) → KHÔNG refresh, KHÔNG điều hướng — hiện lỗi đăng nhập", async () => {
  const calls = fakeFetch(() => 401);
  let fired = 0;
  onSessionExpired(() => {
    fired++;
    return true;
  });
  await assert.rejects(login("a@b.c", "sai"), /x/);
  assert.equal(fired, 0);
  assert.deepEqual(calls, ["/api/auth/login"]);
});
