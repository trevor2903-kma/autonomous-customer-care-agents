"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import type { ConversationListItem } from "shared-types";
import { getConversations } from "@/lib/api";
import { FILTERS, filterByKey } from "./status";
import { StatusPill } from "./StatusPill";

// Listpane (design, 10a): tiêu đề + tìm kiếm + chip lọc + thẻ hội thoại (tên · thời gian · preview · pill).
// Chọn một thẻ → điều hướng /admin/{id} (detail hiện ở pane bên phải; trên mobile thay thế danh sách).

function shortTime(iso?: string | null): string {
  if (!iso) return "";
  const diffMin = Math.round((Date.now() - new Date(iso).getTime()) / 60000);
  if (diffMin < 1) return "vừa xong";
  if (diffMin < 60) return `${diffMin} phút`;
  const h = Math.round(diffMin / 60);
  if (h < 24) return `${h} giờ`;
  return `${Math.round(h / 24)} ngày`;
}

function label(c: ConversationListItem): string {
  return c.customer_identifier?.trim() || `Khách ${c.id.slice(0, 6)}`;
}

export function ConversationListPane({
  filter,
  selectedId,
  className = "",
}: {
  filter: string;
  selectedId: string | null;
  className?: string;
}) {
  const [term, setTerm] = useState("");
  const active = filterByKey(filter);

  const { data, isLoading, isError, error } = useQuery<ConversationListItem[], Error>({
    queryKey: ["conversations", active.key],
    queryFn: () => getConversations(active.statuses.length ? active.statuses : undefined, 100),
    refetchInterval: 10000,
  });

  const rows = useMemo(() => {
    const q = term.trim().toLowerCase();
    if (!q) return data ?? [];
    return (data ?? []).filter((c) =>
      [label(c), c.preview ?? "", c.current_intent ?? ""].join(" ").toLowerCase().includes(q),
    );
  }, [data, term]);

  return (
    <div
      className={`flex w-[340px] flex-none flex-col border-r border-line bg-panel mob:w-full mob:flex-1 mob:border-r-0 ${className}`}
    >
      <div className="px-5 pb-3.5 pt-5">
        <h1 className="font-serif text-2xl text-ink">Hội thoại</h1>

        <div className="mt-3.5 flex items-center gap-[9px] rounded-[10px] border border-line bg-white px-[13px] py-[9px]">
          <span className="h-3.5 w-3.5 flex-none rounded-full border-2 border-dimmer" aria-hidden />
          <input
            value={term}
            onChange={(e) => setTerm(e.target.value)}
            placeholder="Tìm theo tên khách, nội dung…"
            aria-label="Tìm hội thoại"
            className="flex-1 border-none bg-transparent text-[13.5px] text-ink outline-none placeholder:text-dim"
          />
        </div>

        <div className="mt-3 flex flex-wrap gap-[7px]">
          {FILTERS.map((f) => {
            const on = f.key === active.key;
            return (
              <Link
                key={f.key}
                href={f.key === "all" ? "/admin" : `/admin?filter=${f.key}`}
                className={`rounded-[7px] border px-[11px] py-[5px] text-xs ${
                  on ? "border-ink bg-ink text-ink-paper" : "border-line bg-white text-muted hover:border-dimmer"
                }`}
              >
                {f.label}
              </Link>
            );
          })}
        </div>
      </div>

      <div className="flex flex-1 flex-col gap-[5px] overflow-y-auto px-3 pb-4 pt-1">
        {isLoading && <p className="px-2 py-4 text-sm text-dim">Đang tải hội thoại…</p>}
        {isError && <p className="px-2 py-4 text-sm text-terracotta">Lỗi: {error.message}</p>}
        {!isLoading && !isError && rows.length === 0 && (
          <p className="px-2 py-6 text-sm text-dim">
            {term ? "Không có hội thoại khớp tìm kiếm." : "Chưa có hội thoại nào ở bộ lọc này."}
          </p>
        )}

        {rows.map((c) => {
          const on = c.id === selectedId;
          return (
            <Link
              key={c.id}
              href={`/admin/${c.id}`}
              className={`flex flex-col gap-1.5 rounded-[11px] border px-3.5 py-[13px] ${
                on ? "border-line-olive bg-white shadow-card" : "border-transparent hover:bg-cream"
              }`}
            >
              <div className="flex items-center justify-between gap-2">
                <span className="truncate text-sm font-semibold text-ink">{label(c)}</span>
                <span className="flex-none text-[11px] text-dim">{shortTime(c.last_message_at)}</span>
              </div>
              <span className="truncate text-[13px] leading-[1.4] text-faint">{c.preview ?? "—"}</span>
              <span className="self-start">
                <StatusPill status={c.status} />
              </span>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
