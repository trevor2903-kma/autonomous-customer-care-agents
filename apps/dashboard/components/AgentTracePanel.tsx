"use client";

import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import type { RunDemoResult } from "shared-types";
import { runDemo } from "@/lib/api";

export function AgentTracePanel() {
  const [forceHandoff, setForceHandoff] = useState(false);
  const mutation = useMutation<RunDemoResult, Error, boolean>({
    mutationFn: (handoff: boolean) => runDemo(handoff ? "handoff" : undefined),
  });
  const result = mutation.data;

  return (
    <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-neutral-500">
          Agent Trace — Pipeline cố định
        </h2>
        <div className="flex items-center gap-3">
          <label className="flex items-center gap-1.5 text-xs text-neutral-600">
            <input
              type="checkbox"
              checked={forceHandoff}
              onChange={(e) => setForceHandoff(e.target.checked)}
            />
            ép human_handoff
          </label>
          <button
            onClick={() => mutation.mutate(forceHandoff)}
            disabled={mutation.isPending}
            className="rounded-md bg-neutral-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-neutral-700 disabled:opacity-50"
          >
            {mutation.isPending ? "Đang chạy…" : "Run demo"}
          </button>
        </div>
      </div>

      {mutation.isError && (
        <p className="text-sm text-red-500">Lỗi gọi run-demo — backend chạy chưa?</p>
      )}

      {result && (
        <div>
          <div className="mb-3 flex flex-wrap gap-2 text-xs">
            <Badge label={`branch: ${result.branch}`} tone={result.require_human_handoff ? "amber" : "green"} />
            <Badge label={`action: ${result.action ?? "—"}`} />
            <Badge label={`status: ${result.status}`} />
            <Badge label={`confidence: ${result.confidence ?? "—"}`} />
            {result.escalation_reason && (
              <Badge label={`escalation: ${result.escalation_reason}`} tone="amber" />
            )}
          </div>
          <ol className="flex flex-wrap items-center gap-1 text-sm">
            {result.trace.map((step, i) => (
              <li key={i} className="flex items-center gap-1">
                <span className="rounded border border-neutral-300 bg-neutral-50 px-2 py-1 font-mono text-xs">
                  {step.node}
                  <span className="ml-1 text-neutral-400">({step.confidence ?? "—"})</span>
                </span>
                {i < result.trace.length - 1 && <span className="text-neutral-400">→</span>}
              </li>
            ))}
          </ol>
          {result.reply && (
            <p className="mt-3 rounded-md bg-neutral-50 p-2 text-sm text-neutral-700">
              {result.reply}
            </p>
          )}
        </div>
      )}

      {!result && !mutation.isPending && (
        <p className="text-sm text-neutral-400">
          Bấm <strong>Run demo</strong> để chạy pipeline stub (intent → knowledge → decision →
          response / human_handoff).
        </p>
      )}
    </section>
  );
}

function Badge({ label, tone = "neutral" }: { label: string; tone?: "neutral" | "green" | "amber" }) {
  const tones = {
    neutral: "bg-neutral-100 text-neutral-700",
    green: "bg-green-100 text-green-700",
    amber: "bg-amber-100 text-amber-700",
  } as const;
  return <span className={`rounded px-2 py-1 ${tones[tone]}`}>{label}</span>;
}
