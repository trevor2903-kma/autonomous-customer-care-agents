"use client";

import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import type { IntentClassification } from "shared-types";
import { classifyMessage } from "@/lib/api";

// Widget test phân loại: nhập câu khách → intent/category/confidence/cờ + ENTITIES (nổi bật) + nguồn RAG.
// Metadata phân loại (KHÔNG phải câu trả lời khách — Response Generator lo việc đó, PRD §7.4).
export function ClassifyTester() {
  const [message, setMessage] = useState("Đơn hàng 6578 của tôi sắp giao tới nơi chưa?");
  const mutation = useMutation<IntentClassification, Error, string>({ mutationFn: classifyMessage });
  const r = mutation.data;

  return (
    <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
      <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-neutral-500">
        Test phân loại (Intent Classifier)
      </h2>

      <div className="flex flex-wrap items-center gap-2">
        <input
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && message.trim()) mutation.mutate(message);
          }}
          placeholder="Nhập câu khách…"
          className="min-w-0 flex-1 rounded-md border border-neutral-300 px-3 py-1.5 text-sm"
        />
        <button
          onClick={() => message.trim() && mutation.mutate(message)}
          disabled={mutation.isPending || !message.trim()}
          className="rounded-md bg-neutral-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-neutral-700 disabled:opacity-50"
        >
          {mutation.isPending ? "Đang phân loại…" : "Phân loại"}
        </button>
      </div>

      {mutation.isError && <p className="mt-2 text-sm text-red-500">Lỗi: {mutation.error.message}</p>}

      {r && (
        <div className="mt-3 space-y-2 text-sm">
          <div className="flex flex-wrap gap-2">
            <Badge label={`intent: ${r.intent}`} tone="blue" />
            <Badge label={`category: ${r.category ?? "—"}`} />
            <Badge label={`confidence: ${r.confidence.toFixed(2)}`} />
            {r.uncertainty_flags.map((f) => (
              <Badge key={f} label={f} tone="amber" />
            ))}
          </div>

          <div className="rounded-md bg-neutral-50 p-3">
            <div className="mb-1 text-xs font-semibold uppercase tracking-wide text-neutral-500">
              Entities
            </div>
            {Object.keys(r.entities).length === 0 ? (
              <span className="text-neutral-400">— không có —</span>
            ) : (
              <div className="flex flex-wrap gap-2">
                {Object.entries(r.entities).map(([k, v]) => (
                  <span
                    key={k}
                    className="rounded bg-green-100 px-2 py-1 font-mono text-xs text-green-800"
                  >
                    {k}={String(v)}
                  </span>
                ))}
              </div>
            )}
          </div>

          {r.rag_contexts.length > 0 && (
            <div className="text-xs text-neutral-500">
              <span className="font-semibold">Nguồn RAG:</span>{" "}
              {r.rag_contexts.map((c, i) => (
                <span key={i} className="mr-2">
                  <code>{c.source}</code> ({c.score.toFixed(3)})
                </span>
              ))}
            </div>
          )}
        </div>
      )}
    </section>
  );
}

function Badge({ label, tone = "neutral" }: { label: string; tone?: "neutral" | "blue" | "amber" }) {
  const tones = {
    neutral: "bg-neutral-100 text-neutral-700",
    blue: "bg-blue-100 text-blue-700",
    amber: "bg-amber-100 text-amber-700",
  } as const;
  return <span className={`rounded px-2 py-1 ${tones[tone]}`}>{label}</span>;
}
