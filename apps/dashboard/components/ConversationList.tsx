"use client";

import { useQuery } from "@tanstack/react-query";
import type { Conversation } from "shared-types";
import { listConversations } from "@/lib/api";

export function ConversationList() {
  const { data, isLoading, isError } = useQuery<Conversation[]>({
    queryKey: ["conversations"],
    queryFn: listConversations,
    refetchInterval: 15_000,
  });

  return (
    <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
      <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-neutral-500">
        Conversations <span className="font-normal text-neutral-400">(placeholder)</span>
      </h2>
      {isLoading && <p className="text-sm text-neutral-400">Đang tải…</p>}
      {isError && <p className="text-sm text-red-500">Không tải được danh sách.</p>}
      {data && data.length === 0 && (
        <p className="text-sm text-neutral-400">
          Chưa có hội thoại. Mở <code>/chat</code> hoặc POST <code>/api/conversations</code>.
        </p>
      )}
      {data && data.length > 0 && (
        <ul className="divide-y divide-neutral-100">
          {data.slice(0, 10).map((c) => (
            <li key={c.id} className="flex items-center justify-between py-2 text-sm">
              <span className="truncate">
                <span className="font-mono text-xs text-neutral-400">{c.id.slice(0, 8)}</span>{" "}
                {c.customer_identifier ?? "guest"}
                {c.messages && c.messages.length > 0 && (
                  <span className="ml-2 text-neutral-500">
                    “{c.messages[c.messages.length - 1].content.slice(0, 40)}”
                  </span>
                )}
              </span>
              <span className="rounded bg-neutral-100 px-2 py-0.5 text-xs text-neutral-600">
                {c.status}
              </span>
            </li>
          ))}
        </ul>
      )}
      <p className="mt-3 text-xs text-neutral-400">
        TODO (PRD §14 FR-ADMIN-CONV-1): tìm kiếm + lọc theo trạng thái + 3 rổ (đang xử lý / chờ Admin / kết thúc).
      </p>
    </section>
  );
}
