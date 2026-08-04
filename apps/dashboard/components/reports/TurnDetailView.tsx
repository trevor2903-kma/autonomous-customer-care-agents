"use client";

import { useQuery } from "@tanstack/react-query";
import { type TurnDetail, type TurnStep, getTurnDetail } from "@/lib/api";
import {
  ACTION_LABEL,
  AUDIT_ACTION_LABEL,
  FLAG_LABEL,
  KB_TYPE_LABEL,
  NODE_LABEL,
  NODE_SHORT,
  OUTCOME_LABEL,
  OUTCOME_TONE,
  PRIORITY_LABEL,
  SEVERITY_LABEL,
  formatEscalationReason,
  fmtClock,
  fmtMs,
} from "./labels";

// Drill-down MỘT lượt: hàng thẻ 4 tác tử + timeline ms + bảng Nhật ký kiểm toán (design "Báo cáo hoạt động").
// Nguồn: /admin/reports/turns/{id} — dựng lại từ audit_log, KHÔNG phải Langfuse.

const PIPELINE_NODES = ["intent", "knowledge", "decision", "response"];

function num(v: unknown): number | null {
  return typeof v === "number" ? v : null;
}

/** Tóm tắt một bước cho thẻ tác tử — đọc từ `detail` mà chính node đó đã ghi. */
function stepSummary(step: TurnStep, d: TurnDetail): { line: string; sub: string } {
  const detail = step.detail ?? {};
  switch (step.node) {
    case "intent": {
      const ents = Object.keys((detail.entities as Record<string, unknown>) ?? {});
      return {
        line: `Ý định: ${String(detail.intent ?? "—")}`,
        sub: ents.length ? `Thực thể: ${ents.join(", ")}` : "Không có thực thể",
      };
    }
    case "knowledge": {
      const n = num(detail.contexts) ?? 0;
      if (detail.skipped === true) return { line: "Bỏ qua truy hồi (lượt xã giao)", sub: "Không cần tri thức" };
      const conf = num(detail.retrieval_confidence);
      return {
        line: `Truy hồi ${n} đoạn tri thức`,
        sub: conf !== null ? `Điểm cao nhất ${conf.toFixed(2)}` : "—",
      };
    }
    case "decision": {
      const blocking = (detail.blocking_flags as string[]) ?? [];
      const prio = PRIORITY_LABEL[String(detail.priority)] ?? String(detail.priority ?? "—");
      const sev = SEVERITY_LABEL[String(detail.severity)] ?? String(detail.severity ?? "—");
      return {
        line: ACTION_LABEL[String(step.action)] ?? String(step.action ?? "—"),
        sub: blocking.length
          ? `Cờ chặn: ${blocking.map((f) => FLAG_LABEL[f] ?? f).join(", ")}`
          : `Ưu tiên ${prio} · mức ${sev}`,
      };
    }
    case "response": {
      const len = num(detail.reply_len) ?? 0;
      return {
        line: step.flags.includes("hallucination_risk")
          ? "Không đủ căn cứ → câu trả lời dự phòng"
          : `Soạn phản hồi ${len} ký tự`,
        sub: OUTCOME_LABEL[d.outcome] ?? d.outcome,
      };
    }
    default:
      return { line: String(step.action ?? "—"), sub: "" };
  }
}

function AgentCard({ step, detail, index }: { step: TurnStep; detail: TurnDetail; index: number }) {
  const { line, sub } = stepSummary(step, detail);
  const bad = step.flags.length > 0 || step.node === "decision" && step.action === "human_handoff";
  return (
    <div className="flex min-w-0 flex-1 flex-col gap-1.5 rounded-[12px] border border-line bg-white p-[15px] shadow-soft">
      <div className="flex items-center justify-between gap-2">
        <span className="text-[11px] uppercase tracking-[0.6px] text-dim">Tác tử {index + 1}</span>
        <span className="font-mono text-[11.5px] font-semibold text-muted">{fmtMs(step.duration_ms)}</span>
      </div>
      <div className="text-[13.5px] font-semibold text-ink">{NODE_SHORT[step.node] ?? step.node}</div>
      <div className={`text-[12.5px] leading-[1.5] ${bad ? "text-terracotta" : "text-muted"}`}>{line}</div>
      <div className="text-[11.5px] text-faint">{sub}</div>
    </div>
  );
}

/** Timeline ms: mỗi bước một dải, rộng theo tỉ lệ thời gian — nhìn ra ngay đâu là chỗ tốn. */
function Timeline({ steps }: { steps: TurnStep[] }) {
  const measured = steps.filter((s) => s.duration_ms !== null);
  const total = measured.reduce((sum, s) => sum + (s.duration_ms ?? 0), 0);
  if (!total) return null;
  return (
    <div className="mt-3">
      <div className="flex h-2.5 w-full overflow-hidden rounded-full bg-[#EFEBE2]">
        {measured.map((s, i) => (
          <div
            key={s.node}
            title={`${NODE_SHORT[s.node] ?? s.node}: ${fmtMs(s.duration_ms)}`}
            style={{ width: `${((s.duration_ms ?? 0) / total) * 100}%` }}
            className={i % 2 === 0 ? "bg-olive/75" : "bg-steel-2/70"}
          />
        ))}
      </div>
      <div className="mt-1.5 flex flex-wrap gap-x-4 gap-y-1 text-[11.5px] text-faint">
        {measured.map((s) => (
          <span key={s.node}>
            {NODE_SHORT[s.node] ?? s.node} <span className="font-mono text-muted">{fmtMs(s.duration_ms)}</span>
          </span>
        ))}
      </div>
    </div>
  );
}

function auditResult(step: TurnStep): string {
  const d = step.detail ?? {};
  switch (step.node) {
    case "customer":
      return "—";
    case "intent":
      return `${String(d.intent ?? "—")}${step.confidence !== null ? ` · ${step.confidence.toFixed(2)}` : ""}`;
    case "knowledge":
      return d.skipped === true
        ? "bỏ qua"
        : `${num(d.contexts) ?? 0} đoạn${step.confidence !== null ? ` · ${step.confidence.toFixed(2)}` : ""}`;
    case "decision":
      return String(step.action ?? "—");
    case "response":
      return `${num(d.reply_len) ?? 0} ký tự`;
    default:
      return String(step.action ?? "—");
  }
}

export function TurnDetailView({ turnId }: { turnId: string }) {
  const { data, isLoading, isError, error } = useQuery<TurnDetail, Error>({
    queryKey: ["report-turn", turnId],
    queryFn: () => getTurnDetail(turnId),
  });

  if (isLoading) return <p className="mt-6 text-[13px] text-dim">Đang tải chi tiết lượt…</p>;
  if (isError) return <p className="mt-6 text-[13px] text-terracotta">Lỗi: {error.message}</p>;
  if (!data) return null;

  const tone = OUTCOME_TONE[data.outcome] ?? OUTCOME_TONE.error;
  const pipelineSteps = data.steps.filter((s) => PIPELINE_NODES.includes(s.node));

  return (
    <section className="mt-7">
      {/* Đầu lượt */}
      <div className="flex flex-wrap items-center gap-3">
        <h2 className="text-[14px] font-semibold text-ink">Chi tiết lượt xử lý</h2>
        <span className="font-mono text-[12.5px] text-faint">{data.short_id}</span>
        <span className={`rounded-[6px] border px-2 py-0.5 text-[11.5px] font-medium ${tone.border} ${tone.bg} ${tone.text}`}>
          {OUTCOME_LABEL[data.outcome] ?? data.outcome}
        </span>
        <span className="ml-auto font-mono text-[12.5px] font-semibold text-muted">
          Tổng {fmtMs(data.total_ms)}
        </span>
      </div>

      <div className="mt-2.5 rounded-[12px] border border-line bg-white px-[18px] py-3.5 shadow-soft">
        <div className="text-[11px] uppercase tracking-[0.6px] text-dim">Câu khách</div>
        <p className="mt-1 text-[14px] leading-[1.55] text-ink">{data.customer_text || "—"}</p>
        {data.reply_preview && (
          <>
            <div className="mt-3 text-[11px] uppercase tracking-[0.6px] text-dim">Phản hồi đã gửi</div>
            <p className="mt-1 text-[13.5px] leading-[1.55] text-muted">{data.reply_preview}</p>
          </>
        )}
        {data.escalation_reason && (
          <p className="mt-3 text-[12.5px] font-medium text-terracotta">{formatEscalationReason(data.escalation_reason)}</p>
        )}
        <Timeline steps={pipelineSteps} />
      </div>

      {/* Hàng thẻ 4 tác tử */}
      <div className="mt-3 flex flex-wrap gap-3 mob:flex-col">
        {pipelineSteps.map((s, i) => (
          <AgentCard key={s.node} step={s} detail={data} index={i} />
        ))}
      </div>

      {/* Nguồn tri thức (.md trong repo — KHÔNG phải PDF) */}
      {data.rag_sources.length > 0 && (
        <div className="mt-3 overflow-hidden rounded-[12px] border border-line bg-white shadow-soft">
          <div className="border-b border-line-soft px-[18px] py-3">
            <h3 className="text-[13.5px] font-semibold text-ink">
              Tri thức đã truy hồi ({data.rag_sources.length} đoạn)
            </h3>
          </div>
          <div className="divide-y divide-line-soft">
            {data.rag_sources.map((s, i) => (
              <div key={`${s.source}-${i}`} className="flex flex-wrap items-center gap-2 px-[18px] py-2.5">
                <span className="rounded-[5px] border border-line bg-[#F6F3EC] px-1.5 py-0.5 text-[10.5px] font-medium text-dim">
                  {KB_TYPE_LABEL[s.type ?? ""] ?? s.type ?? "—"}
                </span>
                <span className="text-[13px] font-medium text-ink">{s.title ?? "—"}</span>
                <code className="font-mono text-[11.5px] text-dim">{s.source}</code>
                <span className="ml-auto font-mono text-[12px] font-semibold text-muted">
                  {s.score !== null ? s.score.toFixed(4) : "—"}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Nhật ký kiểm toán per-step */}
      <div className="mt-7 flex flex-wrap items-center gap-3">
        <h3 className="text-[14px] font-semibold text-ink">Nhật ký kiểm toán</h3>
        <span className="font-mono text-[12.5px] text-faint">
          {data.short_id} · {data.steps.length} bản ghi
        </span>
      </div>
      <div className="mt-2.5 overflow-x-auto rounded-[13px] border border-line bg-white shadow-soft">
        <div className="min-w-[640px]">
          <div className="grid grid-cols-[100px_190px_minmax(0,1fr)_140px] gap-3 border-b border-line-soft px-[18px] py-3 text-[11px] uppercase tracking-[0.6px] text-dim">
            <span>Thời điểm</span>
            <span>Tác tử</span>
            <span>Hành động</span>
            <span>Kết quả</span>
          </div>
          {data.steps.map((s, i) => (
            <div
              key={`${s.node}-${i}`}
              className="grid grid-cols-[100px_190px_minmax(0,1fr)_140px] gap-3 border-b border-line-soft px-[18px] py-2.5 text-[12.5px] last:border-b-0"
            >
              <span className="font-mono text-faint">{fmtClock(s.created_at)}</span>
              <span className="text-ink">{NODE_LABEL[s.node] ?? s.node}</span>
              <span className="min-w-0 text-muted">
                {AUDIT_ACTION_LABEL[String(s.action)] ?? String(s.action ?? "—")}
                {s.flags.length > 0 && (
                  <span className="ml-1.5 text-terracotta">
                    ({s.flags.map((f) => FLAG_LABEL[f] ?? f).join(", ")})
                  </span>
                )}
              </span>
              <span className="truncate font-mono text-muted">{auditResult(s)}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
