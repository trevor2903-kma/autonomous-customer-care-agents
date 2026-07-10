"use client";

import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import type { IntentClassification } from "shared-types";
import { classifyMessage } from "@/lib/api";

// Widget test Agent 1 · Intent Classifier (PRD §7.1): nhập câu khách → intent/category/confidence/cờ + ENTITIES.
// Agent 1 SẠCH — KHÔNG truy hồi (retrieval là việc Agent 2, §7.2). Để test truy hồi xem AnalyzePanel (/analyze).
// Metadata phân loại (KHÔNG phải câu trả lời khách — Response Generator lo việc đó, PRD §7.4).
export function ClassifyTester() {
  const [message, setMessage] = useState("Đơn hàng 6578 của tôi sắp giao tới nơi chưa?");
  const mutation = useMutation<IntentClassification, Error, string>({ mutationFn: classifyMessage });
  const r = mutation.data;

  return (
    <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
      <h2 className="text-sm font-semibold uppercase tracking-wide text-neutral-500">
        Test Agent 1 · Intent Classifier
      </h2>
      <p className="mb-3 mt-1 text-xs text-neutral-400">
        Agent 1 sạch — không truy hồi (retrieval là việc của Agent 2, §7.2).
      </p>

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
        </div>
      )}
    </section>
  );
}

// Badge nhỏ tái dùng (ClassifyTester + AnalyzePanel) — tránh trùng lặp presentational helper.
export function Badge({ label, tone = "neutral" }: { label: string; tone?: "neutral" | "blue" | "amber" }) {
  const tones = {
    neutral: "bg-neutral-100 text-neutral-700",
    blue: "bg-blue-100 text-blue-700",
    amber: "bg-amber-100 text-amber-700",
  } as const;
  return <span className={`rounded px-2 py-1 ${tones[tone]}`}>{label}</span>;
}
