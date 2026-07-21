import { Suspense } from "react";
import { RequireAuth } from "@/components/auth/RequireAuth";
import { AdminShell } from "@/components/shell/AdminShell";

// Guard admin (slice 11 P4): chỉ role=admin vào /admin/*; chưa đăng nhập → /login.
// Suspense: AdminShell đọc useSearchParams (bộ lọc nav) — Next yêu cầu ranh giới suspense khi prerender tĩnh.
export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <RequireAuth role="admin">
      <Suspense fallback={<div className="flex min-h-0 flex-1" />}>
        <AdminShell>{children}</AdminShell>
      </Suspense>
    </RequireAuth>
  );
}
