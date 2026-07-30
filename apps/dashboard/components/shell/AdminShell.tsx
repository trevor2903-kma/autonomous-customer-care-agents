"use client";

import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import type { Escalation } from "shared-types";
import { getEscalations } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { ConversationListPane } from "@/components/admin/ConversationListPane";

// Vỏ admin (design): sidebar 250px + vùng module. ≤820px sidebar thành drawer off-canvas + scrim + hamburger.
// Hai chế độ vùng chính: (1) hội thoại master-detail (danh sách + chi tiết); (2) module full-width
// (Tri thức, Gate, Báo cáo).
//
// THU GỌN (P5): trên desktop (≥821px) sidebar rút còn rail 78px chỉ-icon — ẩn nhãn/đếm/tên thương hiệu/
// thông tin người dùng. Ở mobile KHÔNG có chế độ này (đã là drawer), nên nút thu gọn bị ẩn dưới 820px.

type NavItem = { key: string; label: string; href: string; count?: "queue" | "approval" };

const NAV: NavItem[] = [
  { key: "all", label: "Hội thoại", href: "/admin" },
  { key: "queue", label: "Hàng đợi chuyển tiếp", href: "/admin?filter=queue", count: "queue" },
  { key: "approval", label: "Duyệt nháp", href: "/admin?filter=approval", count: "approval" },
  { key: "knowledge", label: "Quản lý tri thức", href: "/admin/knowledge" },
  { key: "gate", label: "Cấu hình Gate", href: "/admin/gate" },
  { key: "reports", label: "Báo cáo", href: "/admin/reports" },
];

const COLLAPSE_KEY = "tys_side_collapsed";

function initials(name: string): string {
  const parts = name.trim().split(/\s+/);
  const two = (parts[0]?.[0] ?? "") + (parts[1]?.[0] ?? parts[0]?.[1] ?? "");
  return two.toUpperCase() || "AD";
}

function ChevronIcon({ flipped }: { flipped: boolean }) {
  return (
    <svg
      width="15"
      height="15"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={flipped ? "rotate-180" : ""}
      aria-hidden
    >
      <polyline points="15 18 9 12 15 6" />
    </svg>
  );
}

function LogoutIcon() {
  return (
    <svg
      width="17"
      height="17"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
    >
      <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
      <polyline points="16 17 21 12 16 7" />
      <line x1="21" y1="12" x2="9" y2="12" />
    </svg>
  );
}

export function AdminShell({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useState(false);
  const [collapsed, setCollapsed] = useState(false);
  const pathname = usePathname();
  const filter = useSearchParams().get("filter") ?? "all";
  const { user, logout } = useAuth();
  const router = useRouter();

  // Nhớ trạng thái thu gọn. Đọc trong effect (không phải lúc khởi tạo state) để HTML server và client
  // khớp nhau ở lượt render đầu — đọc localStorage khi render sẽ gây hydration mismatch.
  useEffect(() => {
    setCollapsed(window.localStorage.getItem(COLLAPSE_KEY) === "1");
  }, []);

  function toggleSide() {
    setCollapsed((prev) => {
      const next = !prev;
      window.localStorage.setItem(COLLAPSE_KEY, next ? "1" : "0");
      return next;
    });
  }

  function onLogout() {
    logout();
    router.replace("/login");
  }

  const { data: escalations } = useQuery<Escalation[], Error>({
    queryKey: ["escalations"],
    queryFn: getEscalations,
    refetchInterval: 10000, // badge hàng đợi — dashboard, không phải đường realtime của khách
  });
  const counts = {
    queue: (escalations ?? []).filter((e) => e.status === "IN_HUMAN_QUEUE").length,
    approval: (escalations ?? []).filter((e) => e.status === "PENDING_APPROVAL").length,
  };

  // Route TĨNH của module thắng route động /admin/[conversationId] — thêm module mới phải khai ở đây,
  // nếu không nó bị coi là một hội thoại và rơi vào bố cục master-detail.
  const isKnowledge = pathname.startsWith("/admin/knowledge");
  const isGate = pathname.startsWith("/admin/gate");
  const isReports = pathname.startsWith("/admin/reports");
  const isModule = isKnowledge || isGate || isReports;
  const activeKey = isReports ? "reports" : isGate ? "gate" : isKnowledge ? "knowledge" : filter;
  const moduleTitle = NAV.find((n) => n.key === activeKey)?.label ?? "Hội thoại";

  // Master-detail theo ROUTE (chỉ khi KHÔNG phải module): /admin = danh sách, /admin/{id} = chi tiết.
  const isDetail = !isModule && /^\/admin\/[^/]+$/.test(pathname);
  const selectedId = isDetail ? pathname.split("/")[2] : null;

  const displayName = user?.display_name || user?.email || "Quản trị viên";
  // `desk:` = ≥821px. Chế độ rail chỉ tồn tại trên desktop; mobile giữ nguyên drawer 250px.
  const rail = collapsed ? "desk:w-[78px] desk:px-2" : "";
  const hideWhenRail = collapsed ? "desk:hidden" : "";

  return (
    <div className="flex h-[calc(100vh_-_53px)] min-h-0 overflow-hidden">
      {open && (
        <div
          onClick={() => setOpen(false)}
          className="fixed inset-0 z-[65] hidden bg-[rgba(20,18,15,0.34)] mob:block"
          aria-hidden
        />
      )}

      <aside
        className={`flex w-[250px] flex-none flex-col border-r border-line bg-white px-3.5 py-5 transition-[width] duration-200 mob:fixed mob:inset-y-0 mob:left-0 mob:z-[70] mob:shadow-drawer mob:transition-transform mob:duration-[260ms] ${rail} ${
          open ? "mob:translate-x-0" : "mob:-translate-x-full"
        }`}
      >
        <div
          className={`flex items-center gap-2 pb-[18px] pt-1 ${collapsed ? "desk:flex-col desk:gap-3 desk:px-0" : "px-2.5"}`}
        >
          {/* Ô "T": vừa là dấu thương hiệu ở chế độ rail, vừa là nút bật/tắt thu gọn (design). */}
          <button
            onClick={toggleSide}
            title={collapsed ? "Mở rộng thanh bên" : "Thu gọn thanh bên"}
            aria-label={collapsed ? "Mở rộng thanh bên" : "Thu gọn thanh bên"}
            className={`hidden h-[34px] w-[34px] flex-none items-center justify-center rounded-[9px] bg-ink font-serif text-[17px] text-ink-paper ${
              collapsed ? "desk:flex" : ""
            }`}
          >
            T
          </button>
          <div className={`min-w-0 flex-1 ${hideWhenRail}`}>
            <div className="truncate font-serif text-[19px] text-ink">ThriftYourStyle</div>
            <div className="mt-0.5 text-[11px] uppercase tracking-[1.5px] text-dim">
              Bảng điều hành CSKH
            </div>
          </div>
          <button
            onClick={toggleSide}
            title={collapsed ? "Mở rộng thanh bên" : "Thu gọn thanh bên"}
            aria-label={collapsed ? "Mở rộng thanh bên" : "Thu gọn thanh bên"}
            aria-expanded={!collapsed}
            className="flex h-[30px] w-[30px] flex-none items-center justify-center rounded-[8px] border border-line text-dim transition-colors hover:bg-cream hover:text-muted mob:hidden"
          >
            <ChevronIcon flipped={collapsed} />
          </button>
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
                title={collapsed ? n.label : undefined}
                className={`flex items-center gap-[11px] rounded-[9px] px-3 py-2.5 text-sm ${
                  collapsed ? "desk:justify-center desk:gap-0 desk:px-0" : ""
                } ${active ? "bg-cream font-semibold text-ink" : "font-medium text-muted hover:bg-cream/60"}`}
              >
                <span className="relative flex-none">
                  <span
                    className={`block h-2 w-2 rounded-[2px] ${active ? "bg-olive" : "bg-[#DAD5C8]"}`}
                  />
                  {/* Ở chế độ rail nhãn + số đếm bị ẩn → chấm đỏ giữ lại tín hiệu "có việc chờ". */}
                  {n.count && count > 0 && collapsed && (
                    <span className="absolute -right-1 -top-1 hidden h-2 w-2 rounded-full border-[1.5px] border-white bg-terracotta desk:block" />
                  )}
                </span>
                <span className={`flex-1 ${hideWhenRail}`}>{n.label}</span>
                {n.count && count > 0 && (
                  <span
                    className={`inline-flex h-[19px] min-w-[19px] items-center justify-center rounded-[10px] px-[5px] text-[11px] font-semibold ${hideWhenRail} ${
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

        <div
          className={`mt-auto flex items-center gap-[11px] border-t border-line-soft pt-3.5 ${
            collapsed ? "desk:flex-col desk:gap-3" : ""
          }`}
        >
          <span className="flex h-[34px] w-[34px] flex-none items-center justify-center rounded-[9px] border border-steel-line bg-steel-soft text-xs font-semibold text-steel">
            {initials(displayName)}
          </span>
          <div className={`min-w-0 flex-1 ${hideWhenRail}`}>
            <div className="truncate text-[13.5px] font-semibold text-ink">{displayName}</div>
            <div className="flex items-center gap-1.5">
              <span className="h-1.5 w-1.5 rounded-full bg-sage" />
              <span className="text-[11.5px] text-faint">Đang trực tuyến</span>
            </div>
          </div>
          {/* Hành động THOÁT → tông cảnh báo (design §2), icon-only 34×34 cạnh "Đang trực tuyến". */}
          <button
            onClick={onLogout}
            title="Đăng xuất"
            aria-label="Đăng xuất"
            className="flex h-[34px] w-[34px] flex-none items-center justify-center rounded-[9px] border border-terracotta-btn-line bg-terracotta-btn text-terracotta transition-colors hover:border-terracotta-btn-line-hover hover:bg-terracotta-btn-hover"
          >
            <LogoutIcon />
          </button>
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

        {isModule ? (
          // Module full-width (Tri thức / Gate / Báo cáo) — tự cuộn bên trong.
          <div className="min-h-0 flex-1 overflow-y-auto">{children}</div>
        ) : (
          <div className="flex min-h-0 flex-1 overflow-hidden">
            <ConversationListPane
              filter={filter}
              selectedId={selectedId}
              className={isDetail ? "mob:hidden" : ""}
            />
            <div
              className={`flex min-w-0 flex-1 flex-col overflow-hidden ${isDetail ? "" : "mob:hidden"}`}
            >
              {children}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
