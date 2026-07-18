"use client";

import Link from "next/link";
import { usePathname, useSearchParams } from "next/navigation";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import type { Escalation } from "shared-types";
import { getEscalations } from "@/lib/api";

// Vỏ admin (design): sidebar 250px + vùng module. ≤820px sidebar thành drawer off-canvas + scrim + hamburger.
// Nav trỏ vào CÙNG danh sách hội thoại với bộ lọc khác nhau (10a) — không dựng module rời.

type NavItem = { key: string; label: string; href: string; count?: "queue" | "approval" };

const NAV: NavItem[] = [
  { key: "all", label: "Hội thoại", href: "/admin" },
  { key: "queue", label: "Hàng đợi chuyển tiếp", href: "/admin?filter=queue", count: "queue" },
  { key: "approval", label: "Duyệt nháp", href: "/admin?filter=approval", count: "approval" },
  { key: "rag", label: "Kho tri thức", href: "/rag" },
];

export function AdminShell({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useState(false);
  const pathname = usePathname();
  const filter = useSearchParams().get("filter") ?? "all";

  const { data: escalations } = useQuery<Escalation[], Error>({
    queryKey: ["escalations"],
    queryFn: getEscalations,
    refetchInterval: 10000, // badge hàng đợi — dashboard, không phải đường realtime của khách
  });
  const counts = {
    queue: (escalations ?? []).filter((e) => e.status === "IN_HUMAN_QUEUE").length,
    approval: (escalations ?? []).filter((e) => e.status === "PENDING_APPROVAL").length,
  };

  const activeKey = pathname.startsWith("/rag") ? "rag" : filter;
  const moduleTitle = NAV.find((n) => n.key === activeKey)?.label ?? "Hội thoại";

  return (
    <div className="flex min-h-0 flex-1 overflow-hidden">
      {open && (
        <div
          onClick={() => setOpen(false)}
          className="fixed inset-0 z-[65] hidden bg-[rgba(20,18,15,0.34)] mob:block"
          aria-hidden
        />
      )}

      <aside
        className={`flex w-[250px] flex-none flex-col border-r border-line bg-white px-3.5 py-5 mob:fixed mob:inset-y-0 mob:left-0 mob:z-[70] mob:shadow-drawer mob:transition-transform mob:duration-[260ms] ${
          open ? "mob:translate-x-0" : "mob:-translate-x-full"
        }`}
      >
        <div className="px-2.5 pb-[18px] pt-1">
          <div className="font-serif text-[19px] text-ink">ThriftYourStyle</div>
          <div className="mt-0.5 text-[11px] uppercase tracking-[1.5px] text-dim">Bảng điều hành CSKH</div>
        </div>

        <nav className="flex flex-col gap-[3px]">
          {NAV.map((n) => {
            const active = n.key === activeKey;
            const count = n.count ? counts[n.count] : 0;
            return (
              <Link
                key={n.key}
                href={n.href}
                onClick={() => setOpen(false)}
                className={`flex items-center gap-[11px] rounded-[9px] px-3 py-2.5 text-sm ${
                  active ? "bg-cream font-semibold text-ink" : "font-medium text-muted hover:bg-cream/60"
                }`}
              >
                <span
                  className={`h-2 w-2 flex-none rounded-[2px] ${active ? "bg-olive" : "bg-[#DAD5C8]"}`}
                />
                <span className="flex-1">{n.label}</span>
                {n.count && count > 0 && (
                  <span
                    className={`inline-flex h-[19px] min-w-[19px] items-center justify-center rounded-[10px] px-[5px] text-[11px] font-semibold ${
                      active ? "bg-terracotta text-white" : "bg-[#EFEBE2] text-faint"
                    }`}
                  >
                    {count}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>

        <div className="mt-auto flex items-center gap-[11px] border-t border-line-soft pt-3.5">
          <span className="flex h-[34px] w-[34px] items-center justify-center rounded-[9px] border border-steel-line bg-steel-soft text-xs font-semibold text-steel">
            NG
          </span>
          <div className="flex-1">
            <div className="text-[13.5px] font-semibold text-ink">Ngọc Trần</div>
            <div className="flex items-center gap-1.5">
              <span className="h-1.5 w-1.5 rounded-full bg-sage" />
              <span className="text-[11.5px] text-faint">Đang trực tuyến</span>
            </div>
          </div>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col overflow-hidden">
        <div className="hidden flex-none items-center gap-3 border-b border-line bg-white px-4 py-[11px] mob:flex">
          <button
            onClick={() => setOpen(true)}
            aria-label="Mở menu điều hướng"
            className="flex h-[38px] w-[38px] flex-none flex-col items-center justify-center gap-1 rounded-[9px] border border-line bg-white"
          >
            <span className="h-0.5 w-4 rounded-sm bg-ink-2" />
            <span className="h-0.5 w-4 rounded-sm bg-ink-2" />
            <span className="h-0.5 w-4 rounded-sm bg-ink-2" />
          </button>
          <span className="font-serif text-xl text-ink">{moduleTitle}</span>
        </div>
        {children}
      </div>
    </div>
  );
}
