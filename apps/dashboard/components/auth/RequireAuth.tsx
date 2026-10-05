"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuth } from "@/lib/auth";
import { loginUrl } from "@/lib/authRedirect";

// Guard client (slice 11 P4). Thiếu đăng nhập → /login; sai role → về trang đúng vai của mình.
// role bỏ trống = chỉ cần đăng nhập (bất kỳ vai).
export function RequireAuth({
  role,
  children,
}: {
  role?: "admin" | "customer";
  children: React.ReactNode;
}) {
  const { user, loading, signedOut } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (loading) return;
    if (!user) {
      // Mang theo trang đang mở (`?next=`) → đăng nhập (lại) xong quay về đúng chỗ, kể cả khi hết phiên giữa chừng.
      // Chủ động đăng xuất → KHÔNG mang: đăng nhập lại luôn về trang mặc định.
      router.replace(signedOut ? "/login" : loginUrl(window.location.pathname + window.location.search));
    } else if (role && user.role !== role) {
      // Đăng nhập nhưng sai vai → đưa về trang đúng vai (admin→/admin, khách→/chat).
      router.replace(user.role === "admin" ? "/admin" : "/chat");
    }
  }, [loading, user, signedOut, role, router]);

  if (loading || !user || (role && user.role !== role)) {
    return (
      <div className="flex flex-1 items-center justify-center py-20 text-sm text-dim">
        Đang tải…
      </div>
    );
  }
  return <>{children}</>;
}
