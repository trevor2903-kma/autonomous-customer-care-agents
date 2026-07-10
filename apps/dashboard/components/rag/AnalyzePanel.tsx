"use client";

import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import type { AnalyzeResult } from "shared-types";
import { analyzeMessage } from "@/lib/api";
import { Badge } from "./ClassifyTester";

// Widget test TÁCH VAI (PRD §7.1 + §7.2): nhập câu khách → /analyze → hiện HAI khối riêng:
//   Agent 1 · Intent Classifier (intent/entities, KHÔNG retrieval) và Agent 2 · Knowledge Agent (truy hồi).
// Metadata dev xem — KHÔNG phải câu trả lời khách (Response Generator lo, PRD §7.4).

// Cờ "grounding yếu" -> tô amber (đều dẫn tới human_handoff an toàn).
const WEAK_GROUNDING = new Set(["no_relevant_knowledge", "low_retrieval_score"]);

function snippet(text?: string): string {
  if (!text) return "—";
  const t = text.trim();
  return t.length > 120 ? `${t.slice(0, 120)}…` : t;
}

export function AnalyzePanel() {
  const [message, setMessage] = useState("phí ship đi tỉnh bao nhiêu?");
  const mutation = useMutation<AnalyzeResult, Error, string>({ mutationFn: analyzeMessage });
  const r = mutation.data;

  return (
    <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
      <h2 className="text-sm font-semibold uppercase tracking-wide text-neutral-500">
        Test tách vai · Agent 1 → Agent 2
      </h2>
      <p className="mb-3 mt-1 text-xs text-neutral-400">
        /analyze = Agent 1 (intent/entities) + Agent 2 · Knowledge Agent (truy hồi kho tri thức, §7.2).
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
          {mutation.isPending ? "Đang phân tích…" : "Phân tích"}
        </button>
      </div>

      {mutation.isError && <p className="mt-2 text-sm text-red-500">Lỗi: {mutation.error.message}</p>}

      {r && (
        <div className="mt-3 space-y-3 text-sm">
          {/* ── Agent 1 · Intent Classifier ─────────────────────────────── */}
          <div className="rounded-md border border-blue-100 bg-blue-50/40 p-3">
            <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-blue-700">
              Agent 1 · Intent Classifier
            </div>
            <div className="flex flex-wrap gap-2">
              <Badge label={`intent: ${r.intent}`} tone="blue" />
              <Badge label={`category: ${r.category ?? "—"}`} />
              <Badge label={`intent_confidence: ${r.intent_confidence.toFixed(2)}`} />
            </div>
            <div className="mt-2">
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

          {/* ── Agent 2 · Knowledge Agent ───────────────────────────────── */}
          <div className="rounded-md border border-neutral-200 bg-neutral-50 p-3">
            <div className="mb-2 flex flex-wrap items-center gap-2">
              <span className="text-xs font-semibold uppercase tracking-wide text-neutral-600">
                Agent 2 · Knowledge Agent
              </span>
              <Badge label={`retrieval_confidence: ${r.retrieval_confidence.toFixed(2)}`} />
            </div>
            {r.rag_contexts.length === 0 ? (
              <span className="text-neutral-400">— không truy hồi được tri thức —</span>
            ) : (
              <ul className="space-y-1.5">
                {r.rag_contexts.map((c, i) => (
                  <li key={i} className="rounded border border-neutral-200 bg-white p-2 text-xs">
                    <div className="mb-0.5 flex flex-wrap items-center gap-2 text-neutral-500">
                      <code className="text-neutral-700">{c.source}</code>
                      <span>· score {c.score.toFixed(3)}</span>
                    </div>
                    <p className="text-neutral-600">{snippet(c.text)}</p>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* ── Cờ bất định (gộp Agent 1 + Agent 2) ─────────────────────── */}
          {r.uncertainty_flags.length > 0 && (
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs font-semibold uppercase tracking-wide text-neutral-500">
                Cờ bất định
              </span>
              {r.uncertainty_flags.map((f) => (
                <Badge key={f} label={f} tone={WEAK_GROUNDING.has(f) ? "amber" : "neutral"} />
              ))}
            </div>
          )}
        </div>
      )}
    </section>
  );
}
