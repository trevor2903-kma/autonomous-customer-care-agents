"use client";

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import {
  type IntentRow,
  type ReportRange,
  type ReportResult,
  type ReportSummary,
  type TurnList,
  getReportByIntent,
  getReportSummary,
  getReportTurns,
} from "@/lib/api";
import { TurnDetailView } from "@/components/reports/TurnDetailView";
import { FLAG_LABEL, OUTCOME_LABEL, OUTCOME_TONE, fmtMs, fmtTime } from "@/components/reports/labels";

// Tab "Báo cáo hoạt động" (slice obs P4). NGUỒN: audit_log qua /api/admin/reports/* — Langfuse chỉ là
// link bổ trợ. Bố cục theo design: lọc thời gian → 3 thẻ KPI → bảng theo intent → danh sách lượt →
// drill-down 4 tác tử + nhật ký kiểm toán.

const RANGES: { key: ReportRange; label: string }[] = [
  { key: "today", label: "Hôm nay" },
  { key: "7d", label: "7 ngày" },
  { key: "all", label: "Tất cả" },
];

const RESULTS: { key: ReportResult; label: string }[] = [
  { key: "all", label: "Tất cả" },
  { key: "auto", label: "Gửi thẳng" },
  { key: "draft", label: "Giữ nháp" },
  { key: "handoff", label: "Chuyển nhân viên" },
];

function Segmented<T extends string>({
  options,
  value,
  onChange,
}: {
  options: { key: T; label: string }[];
  value: T;
  onChange: (v: T) => void;
}) {
  return (
    <div className="inline-flex flex-wrap gap-1 rounded-[10px] border border-line bg-white p-1">
      {options.map((o) => (
        <button
          key={o.key}
          onClick={() => onChange(o.key)}
          className={`rounded-[7px] px-3 py-1.5 text-[12.5px] font-medium transition-colors ${
            value === o.key ? "bg-cream text-ink" : "text-faint hover:text-muted"
          }`}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}

function KpiCard({ label, value, note }: { label: string; value: string; note: React.ReactNode }) {
  return (
    <div className="min-w-0 flex-1 rounded-[12px] border border-line bg-white px-[18px] py-[15px] shadow-soft">
      <div className="text-[11px] uppercase tracking-[0.8px] text-dim">{label}</div>
      <div className="mt-[7px] font-serif text-[29px] leading-[1.1] text-ink">{value}</div>
      <div className="mt-[3px] text-[12px] leading-[1.5] text-faint">{note}</div>
    </div>
  );
}

function KpiRow({ s }: { s: ReportSummary }) {
  const sent = s.outcomes.sent ?? 0;
  const handoff = s.outcomes.queued_for_human ?? 0;
  const top = s.escalation_reasons[0];
  const lat = s.latency;
  const within = lat.within_nfr_pct;
  return (
    <div className="mt-[22px] flex gap-3 mob:flex-col">
      <KpiCard
        label="Tự động trả lời"
        value={`${s.auto_reply_pct}%`}
        note={`${sent}/${s.turns} lượt gửi thẳng · ${s.draft_pct}% giữ nháp chờ duyệt`}
      />
      <KpiCard
        label="Chuyển nhân viên"
        value={`${s.handoff_pct}%`}
        note={
          top ? (
            <>
              {handoff}/{s.turns} lượt · chủ yếu do{" "}
              <span className="text-muted">{FLAG_LABEL[top.flag] ?? top.flag}</span> ({top.pct}%)
            </>
          ) : (
            `${handoff}/${s.turns} lượt · chưa có lượt nào phải chuyển`
          )
        }
      />
      <KpiCard
        label="Độ trễ phản hồi"
        value={fmtMs(lat.p50_ms)}
        note={
          <>
            Từ khi nhận tin đến khi phản hồi.
          </>
        }
      />
    </div>
  );
}

function EscalationReasons({ s }: { s: ReportSummary }) {
  if (!s.escalation_reasons.length) return null;
  return (
    <div className="mt-3 rounded-[12px] border border-line bg-white px-[18px] py-4 shadow-soft">
      <h2 className="text-[13.5px] font-semibold text-ink">Vì sao phải chuyển nhân viên</h2>
      <div className="mt-2.5 flex flex-col gap-2">
        {s.escalation_reasons.map((r) => (
          <div key={r.flag} className="flex items-center gap-3">
            <span className="w-[190px] flex-none text-[12.5px] text-muted">
              {FLAG_LABEL[r.flag] ?? r.flag}
            </span>
            <div className="h-2 flex-1 overflow-hidden rounded-full bg-[#EFEBE2]">
              <div className="h-full rounded-full bg-terracotta/60" style={{ width: `${r.pct}%` }} />
            </div>
            <span className="w-[92px] flex-none text-right font-mono text-[12px] text-faint">
              {r.count} lượt · {r.pct}%
            </span>
          </div>
        ))}
      </div>
      <p className="mt-2.5 text-[11.5px] leading-[1.5] text-dim">
        Cờ chặn do Agent 3 ghi nhận — escalation an toàn luôn bật, gate không ghi đè được.
      </p>
    </div>
  );
}

function IntentTable({ rows }: { rows: IntentRow[] }) {
  return (
    <section className="mt-7">
      <h2 className="mb-2.5 text-[14px] font-semibold text-ink">Phân tích theo ý định</h2>
      <div className="overflow-x-auto rounded-[13px] border border-line bg-white shadow-soft">
        <div className="min-w-[560px]">
          <div className="grid grid-cols-[minmax(0,1fr)_70px_80px_90px_110px_90px] gap-3 border-b border-line-soft px-[18px] py-3 text-[11px] uppercase tracking-[0.6px] text-dim">
            <span>Ý định</span>
            <span className="text-right">Lượt</span>
            <span className="text-right">Gửi thẳng</span>
            <span className="text-right">Giữ nháp</span>
            <span className="text-right">Chuyển người</span>
            <span className="text-right">Độ trễ TB</span>
          </div>
          {rows.length === 0 && (
            <p className="px-[18px] py-4 text-[13px] text-dim">Chưa có lượt nào trong khoảng này.</p>
          )}
          {rows.map((r) => (
            <div
              key={r.intent}
              className="grid grid-cols-[minmax(0,1fr)_70px_80px_90px_110px_90px] gap-3 border-b border-line-soft px-[18px] py-2.5 text-[12.5px] last:border-b-0"
            >
              <code className="truncate font-mono text-[12px] text-ink">{r.intent}</code>
              <span className="text-right text-muted">{r.turns}</span>
              <span className="text-right text-olive-dark">{r.auto_pct}%</span>
              <span className="text-right text-gold">{r.draft_pct}%</span>
              <span className="text-right text-terracotta">{r.handoff_pct}%</span>
              <span className="text-right font-mono text-muted">{fmtMs(r.avg_latency_ms)}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default function ReportsPage() {
  const [range, setRange] = useState<ReportRange>("7d");
  const [result, setResult] = useState<ReportResult>("all");
  const [selected, setSelected] = useState<string | null>(null);

  const summary = useQuery<ReportSummary, Error>({
    queryKey: ["report-summary", range],
    queryFn: () => getReportSummary(range),
  });
  const byIntent = useQuery<IntentRow[], Error>({
    queryKey: ["report-by-intent", range],
    queryFn: () => getReportByIntent(range),
  });
  const turns = useQuery<TurnList, Error>({
    queryKey: ["report-turns", range, result],
    queryFn: () => getReportTurns(range, result),
  });

  const err = summary.error ?? byIntent.error ?? turns.error;

  return (
    <div className="mx-auto w-full max-w-5xl px-8 pb-12 pt-7 mob:px-4">
      <header>
        <h1 className="font-serif text-[27px] text-ink">Báo cáo hoạt động</h1>
        <p className="mt-1.5 max-w-[620px] text-[13.5px] leading-[1.55] text-faint">
          Luồng xử lý của 4 tác tử cho từng tin nhắn, dựng lại từ nhật ký kiểm toán (audit log).
        </p>
      </header>

      <div className="mt-4 flex flex-wrap items-center gap-3">
        <Segmented options={RANGES} value={range} onChange={setRange} />
        {summary.data?.langfuse_url && (
          <a
            href={summary.data.langfuse_url}
            target="_blank"
            rel="noreferrer"
            className="ml-auto rounded-[8px] border border-line px-3 py-1.5 text-[12.5px] text-muted transition-colors hover:bg-cream"
          >
            Xem trace LLM chi tiết ↗
          </a>
        )}
      </div>

      {err && <p className="mt-4 text-[13px] text-terracotta">Lỗi: {err.message}</p>}
      {summary.isLoading && <p className="mt-6 text-[13px] text-dim">Đang tải số liệu…</p>}

      {summary.data && (
        <>
          <KpiRow s={summary.data} />
          {summary.data.turns === 0 ? (
            <p className="mt-4 rounded-[12px] border border-line bg-white px-[18px] py-4 text-[13px] text-dim shadow-soft">
              Chưa có lượt xử lý nào trong khoảng thời gian này. Hãy thử mở rộng sang “Tất cả”.
            </p>
          ) : (
            <>
              {summary.data.fallback_pct > 0 && (
                <p className="mt-3 rounded-[12px] border border-gold/30 bg-gold-soft px-[18px] py-3 text-[12.5px] text-muted">
                  <span className="font-semibold text-gold">{summary.data.fallback_pct}%</span> lượt phải
                  dùng câu trả lời dự phòng vì không đủ căn cứ trong kho tri thức — cân nhắc bổ sung tài liệu.
                </p>
              )}
              <EscalationReasons s={summary.data} />
            </>
          )}
        </>
      )}

      {byIntent.data && byIntent.data.length > 0 && <IntentTable rows={byIntent.data} />}

      {/* Danh sách lượt gần đây */}
      <section className="mt-7">
        <div className="mb-2.5 flex flex-wrap items-center gap-3">
          <h2 className="text-[14px] font-semibold text-ink">Lượt xử lý gần đây</h2>
          <Segmented options={RESULTS} value={result} onChange={setResult} />
          {turns.data && <span className="text-[12.5px] text-faint">{turns.data.total} lượt</span>}
        </div>

        <div className="overflow-x-auto rounded-[13px] border border-line bg-white shadow-soft">
          <div className="min-w-[650px]">
            {/* Header bảng */}
            <div className="flex items-center gap-3 border-b border-line-soft bg-cream-soft/40 px-[18px] py-2.5 text-[11px] font-medium uppercase tracking-[0.6px] text-dim">
              <span className="w-[95px] flex-none">Mã lượt</span>
              <span className="min-w-0 flex-1">Nội dung tin nhắn</span>
              <span className="w-[100px] flex-none text-right">Ý định</span>
              <span className="w-[90px] flex-none text-center">Kết quả</span>
              <span className="w-[65px] flex-none text-right">Độ trễ</span>
              <span className="w-[110px] flex-none text-right">Thời gian</span>
            </div>

            {turns.isLoading && <p className="px-[18px] py-4 text-[13px] text-dim">Đang tải…</p>}
            {turns.data?.items.length === 0 && (
              <p className="px-[18px] py-4 text-[13px] text-dim">
                Không có lượt nào khớp bộ lọc này.
              </p>
            )}
            <div className="divide-y divide-line-soft">
              {turns.data?.items.map((t) => {
                const tone = OUTCOME_TONE[t.outcome] ?? OUTCOME_TONE.error;
                const active = selected === t.turn_id;
                return (
                  <button
                    key={t.turn_id}
                    onClick={() => setSelected(active ? null : t.turn_id)}
                    className={`flex w-full items-center gap-3 px-[18px] py-3 text-left transition-colors ${
                      active ? "bg-cream" : "hover:bg-cream/50"
                    }`}
                  >
                    <span className="w-[95px] flex-none font-mono text-[11.5px] text-dim">
                      {t.short_id}
                    </span>
                    <span className="min-w-0 flex-1 truncate text-[13.5px] text-ink">
                      {t.customer_text || "—"}
                    </span>
                    <span className="w-[100px] flex-none text-right">
                      {t.intent ? (
                        <code className="truncate font-mono text-[11.5px] text-faint">
                          {t.intent}
                        </code>
                      ) : (
                        <span className="text-[11.5px] text-faint">—</span>
                      )}
                    </span>
                    <span className="w-[90px] flex-none text-center">
                      <span
                        className={`inline-block rounded-[5px] border px-1.5 py-0.5 text-[10.5px] font-medium ${tone.border} ${tone.bg} ${tone.text}`}
                      >
                        {OUTCOME_LABEL[t.outcome] ?? t.outcome}
                      </span>
                    </span>
                    <span className="w-[65px] flex-none text-right font-mono text-[12px] text-muted">
                      {fmtMs(t.duration_ms)}
                    </span>
                    <span className="w-[110px] flex-none text-right text-[11.5px] text-faint">
                      {fmtTime(t.created_at)}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      </section>

      {selected && <TurnDetailView turnId={selected} />}
    </div>
  );
}
