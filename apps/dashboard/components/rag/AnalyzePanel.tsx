"use client";

import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import type { PipelineResult } from "shared-types";
import { runPipeline } from "@/lib/api";
import { Badge } from "./ClassifyTester";

// Pipeline Inspector (PRD §17): chạy ĐỦ 4 agent cho 1 câu test → QUAN SÁT quyết định Agent 3 (auto_reply /
// human_handoff + priority/severity/escalation) và câu trả lời Agent 4. Metadata dev, single-shot, KHÔNG persist
// (đa lượt test qua /chat). Câu trả lời tới khách vẫn CHỈ từ Response Generator (§7.4).

// Cờ "grounding yếu" -> tô amber (đều dẫn tới human_handoff an toàn).
const WEAK_GROUNDING = new Set(["no_relevant_knowledge", "low_retrieval_score"]);

// Nhãn loại chunk — cùng cách gọi với nhãn Agent 4 nhìn thấy trong prompt (_TYPE_LABEL ở response.py).
const TYPE_LABEL: Record<string, string> = {
  case: "Quy trình xử lý",
  reference: "Tra cứu",
  faq: "Hỏi đáp",
  promotion: "Khuyến mãi",
  upload: "Tải lên",
};

function snippet(text?: string): string {
  if (!text) return "—";
  const t = text.trim();
  return t.length > 120 ? `${t.slice(0, 120)}…` : t;
}

export function AnalyzePanel() {
  const [message, setMessage] = useState("shop cho đổi trả trong bao lâu?");
  const mutation = useMutation<PipelineResult, Error, string>({ mutationFn: runPipeline });
  const r = mutation.data;
  const isHandoff = r?.action === "human_handoff";

  return (
    <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
      <h2 className="text-sm font-semibold uppercase tracking-wide text-neutral-500">
        Pipeline Inspector · Agent 1 → 2 → 3 → 4
      </h2>
      <p className="mb-3 mt-1 text-xs text-neutral-400">
        /pipeline chạy đủ 4 agent cho một câu — quan sát quyết định Agent 3 &amp; câu trả lời Agent 4 (single-shot,
        không lưu).
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
          {mutation.isPending ? "Đang chạy…" : "Chạy pipeline"}
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
              <Badge label={`${r.rag_contexts.length} chunk`} />
            </div>
            {r.rag_contexts.length === 0 ? (
              <span className="text-neutral-400">
                {r.intent === "greeting"
                  ? "— lượt xã giao: bỏ qua truy hồi, không phát cờ grounding —"
                  : "— không truy hồi được tri thức —"}
              </span>
            ) : (
              <ul className="space-y-1.5">
                {r.rag_contexts.map((c, i) => (
                  <li key={i} className="rounded border border-neutral-200 bg-white p-2 text-xs">
                    <div className="mb-0.5 flex flex-wrap items-center gap-2 text-neutral-500">
                      <span className="font-semibold text-neutral-400">#{i + 1}</span>
                      {c.type && (
                        <span className="rounded bg-neutral-200 px-1.5 py-0.5 text-[10.5px] font-medium text-neutral-700">
                          {TYPE_LABEL[c.type] ?? c.type}
                        </span>
                      )}
                      {c.title && <span className="font-medium text-neutral-700">{c.title}</span>}
                      <code className="text-neutral-500">{c.source}</code>
                      <span className="ml-auto font-mono font-semibold text-neutral-700">
                        {c.score.toFixed(4)}
                      </span>
                    </div>
                    <p className="text-neutral-600">{snippet(c.text)}</p>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* ── Agent 3 · Decision Engine (NỔI BẬT — chỗ test Agent 3) ───── */}
          <div
            className={`rounded-md border p-3 ${
              isHandoff ? "border-amber-300 bg-amber-50" : "border-green-200 bg-green-50"
            }`}
          >
            <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-neutral-600">
              Agent 3 · Decision Engine
            </div>
            <div className="flex flex-wrap gap-2">
              <Badge label={`action: ${r.action ?? "—"}`} tone={isHandoff ? "amber" : "blue"} />
              <Badge label={`priority: ${r.priority ?? "—"}`} />
              <Badge label={`severity: ${r.severity ?? "—"}`} />
            </div>
            {r.escalation_reason && (
              <p className="mt-2 text-xs text-amber-700">
                escalation_reason: <code>{r.escalation_reason}</code>
              </p>
            )}
            {r.uncertainty_flags.length > 0 && (
              <div className="mt-2 flex flex-wrap items-center gap-2">
                <span className="text-xs font-semibold uppercase tracking-wide text-neutral-500">Cờ</span>
                {r.uncertainty_flags.map((f) => (
                  <Badge key={f} label={f} tone={WEAK_GROUNDING.has(f) ? "amber" : "neutral"} />
                ))}
              </div>
            )}
          </div>

          {/* ── Agent 4 · Response Generator ────────────────────────────── */}
          <div className="rounded-md border border-neutral-200 bg-white p-3">
            <div className="mb-1 text-xs font-semibold uppercase tracking-wide text-neutral-600">
              Agent 4 · Response Generator {isHandoff && <span className="text-amber-600">(thông báo chuyển người)</span>}
            </div>
            <p className="text-neutral-800">{r.reply ?? "—"}</p>
          </div>
        </div>
      )}
    </section>
  );
}
