"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import type { Escalation } from "shared-types";
import { getEscalations } from "@/lib/api";
import { Badge } from "@/components/rag/ClassifyTester";

// Hàng đợi Escalation (08b, PRD §11/§17): ca IN_HUMAN_QUEUE + PENDING_APPROVAL, sắp priority cao→thấp (backend).
// Chọn một mục → mở màn tiếp quản /admin/[id] (08c). Refresh thủ công/định kỳ — push realtime là phase sau.

const PRIORITY_TONE: Record<string, string> = {
  high: "bg-red-100 text-red-700",
  medium: "bg-amber-100 text-amber-700",
  low: "bg-neutral-100 text-neutral-600",
};

function PriorityBadge({ priority }: { priority?: string | null }) {
  const p = priority ?? "—";
  return (
    <span className={`rounded px-2 py-1 text-xs font-semibold ${PRIORITY_TONE[p] ?? "bg-neutral-100 text-neutral-400"}`}>
      priority: {p}
    </span>
  );
}

export default function AdminQueuePage() {
  const { data, isLoading, isError, error, refetch, isFetching } = useQuery<Escalation[], Error>({
    queryKey: ["escalations"],
    queryFn: getEscalations,
    refetchInterval: 8000, // định kỳ nhẹ (dashboard admin) — realtime push đúng nghĩa = phase sau
  });

  return (
    <main className="w-full flex-1 overflow-y-auto px-6 py-10">
      <header className="mb-6 flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">Hàng đợi Escalation</h1>
          <p className="text-sm text-neutral-500">
            Ca cần người xử lý (chuyển tiếp + chờ duyệt nháp) — ưu tiên cao lên trước.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => refetch()}
            disabled={isFetching}
            className="rounded-md border border-neutral-300 px-3 py-1.5 text-sm hover:bg-neutral-100 disabled:opacity-50"
          >
            {isFetching ? "Đang tải…" : "Làm mới"}
          </button>
          <Link
            href="/"
            className="rounded-md border border-neutral-300 px-3 py-1.5 text-sm hover:bg-neutral-100"
          >
            ← Dashboard
          </Link>
        </div>
      </header>

      {isLoading && <p className="text-sm text-neutral-400">Đang tải hàng đợi…</p>}
      {isError && <p className="text-sm text-red-500">Lỗi: {error.message}</p>}
      {data && data.length === 0 && (
        <p className="rounded-lg border border-dashed border-neutral-300 p-8 text-center text-sm text-neutral-400">
          Không có ca nào trong hàng đợi.
        </p>
      )}

      <ul className="space-y-3">
        {data?.map((e) => {
          const card = e.escalation_card;
          return (
            <li key={e.conversation_id}>
              <Link
                href={`/admin/${e.conversation_id}`}
                className="block rounded-lg border border-neutral-200 bg-white p-4 shadow-sm transition hover:border-neutral-400"
              >
                <div className="flex flex-wrap items-center gap-2">
                  <PriorityBadge priority={e.priority} />
                  <Badge label={`severity: ${e.severity ?? "—"}`} />
                  <Badge label={e.status} tone="amber" />
                  {card?.intent && <Badge label={`intent: ${card.intent}`} tone="blue" />}
                  {e.customer_identifier && (
                    <span className="ml-auto font-mono text-xs text-neutral-400">
                      {e.customer_identifier.slice(0, 8)}
                    </span>
                  )}
                </div>
                <p className="mt-2 text-sm text-neutral-800">
                  <span className="text-neutral-400">Tin khách: </span>
                  {card?.summary ?? "—"}
                </p>
                <p className="mt-1 text-xs text-neutral-500">
                  <span className="text-neutral-400">Lý do: </span>
                  <code>{e.escalation_reason ?? "—"}</code>
                </p>
                {card?.suggested_reply ? (
                  <p className="mt-1 text-xs text-emerald-700">
                    <span className="text-neutral-400">Nháp AI chờ duyệt: </span>
                    {card.suggested_reply}
                  </p>
                ) : null}
              </Link>
            </li>
          );
        })}
      </ul>
    </main>
  );
}
