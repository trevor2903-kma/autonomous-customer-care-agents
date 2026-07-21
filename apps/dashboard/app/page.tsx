"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuth } from "@/lib/auth";

// Trang gốc: điều hướng theo vai (slice 11 P4). Chưa đăng nhập → /login; admin → /admin; khách → /chat.
export default function HomePage() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (loading) return;
    router.replace(!user ? "/login" : user.role === "admin" ? "/admin" : "/chat");
  }, [loading, user, router]);

  return (
    <div className="flex min-h-[calc(100vh_-_53px)] items-center justify-center text-sm text-dim">
      Đang chuyển hướng…
    </div>
  );
}
