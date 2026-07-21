"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";

// Top bar dùng chung (design: hbar 53px, trắng, viền dưới). Phải: trạng thái đăng nhập THỰC + Đăng xuất
// (thay toggle harness demo — slice 11 P4). KHÔNG chứa nav admin (khách và admin là hai URL riêng).
export function TopBar() {
  const { user, logout } = useAuth();
  const router = useRouter();

  function onLogout() {
    logout();
    router.replace("/login");
  }

  return (
    <header className="sticky top-0 z-50 flex h-[53px] flex-none items-center justify-between border-b border-line bg-white px-[22px] mob:px-3.5">
      <Link href="/" className="flex min-w-0 items-center gap-3">
        <span className="flex h-[26px] w-[26px] flex-none items-center justify-center rounded-[7px] bg-ink font-serif text-base text-ink-paper">
          T
        </span>
        <span className="font-serif text-xl tracking-[0.2px] text-ink mob:text-[17px]">ThriftYourStyle</span>
      </Link>

      {user ? (
        <div className="flex items-center gap-3">
          <div className="flex flex-col items-end leading-tight mob:hidden">
            <span className="text-[13px] font-semibold text-ink">{user.display_name || user.email}</span>
            <span className="text-[11px] text-faint">
              {user.role === "admin" ? "Quản trị viên" : "Khách hàng"}
            </span>
          </div>
          <button
            onClick={onLogout}
            className="rounded-[7px] border border-line px-3 py-1.5 text-[12.5px] text-muted hover:bg-cream"
          >
            Đăng xuất
          </button>
        </div>
      ) : (
        <Link href="/login" className="text-[12.5px] text-dim hover:text-muted mob:hidden">
          Đăng nhập
        </Link>
      )}
    </header>
  );
}
