import { Suspense } from "react";
import { AdminShell } from "@/components/shell/AdminShell";

// Suspense: AdminShell đọc useSearchParams (bộ lọc nav) — Next yêu cầu ranh giới suspense khi prerender tĩnh.
export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <Suspense fallback={<div className="flex min-h-0 flex-1" />}>
      <AdminShell>{children}</AdminShell>
    </Suspense>
  );
}
