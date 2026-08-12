import type { EscalationCard } from "shared-types";
import { FLAG_LABEL, SEVERITY_LABEL, formatEscalationReason, formatIntent, parseBlockingFlags } from "@/components/reports/labels";

// EscalationCard (design, PRD §11): vì sao ca này cần người — ưu tiên/mức độ, lý do + cờ, tóm tắt,
// intent & thực thể, tri thức RAG đã truy hồi. Đây là ngữ cảnh để admin nắm ca trong vài giây.

const PRIO: Record<string, { color: string; soft: string; label: string }> = {
  high: { color: "#B25B3C", soft: "#F6E7DF", label: "cao" },
  medium: { color: "#B98534", soft: "#F7EFDD", label: "trung bình" },
  low: { color: "#8E887B", soft: "#F0EDE6", label: "thấp" },
};

export function EscalationCardPanel({
  card,
  identifier,
}: {
  card: EscalationCard;
  identifier?: string | null;
}) {
  const flags = parseBlockingFlags(card.escalation_reason);

  return (
    <div className="flex flex-col gap-4 rounded-[14px] border border-line bg-cream-soft p-5">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-line pb-3.5">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-[16px] font-semibold text-ink">Thẻ tổng quan ca</span>
          {/* {identifier && <span className="text-[14px] text-faint"> {identifier}</span>} */}
        </div>
        <div className="flex items-center gap-2">
          <span
            className="rounded-full px-2.5 py-0.5 text-[11.5px] font-medium"
            style={{
              color: (PRIO[card.priority ?? ""] ?? PRIO.medium).color,
              backgroundColor: (PRIO[card.priority ?? ""] ?? PRIO.medium).soft,
            }}
          >
            Ưu tiên {PRIO[card.priority ?? ""]?.label ?? card.priority}
          </span>
          <span className="rounded-full bg-cream px-2.5 py-0.5 text-[11.5px] text-muted">
            Mức độ: {SEVERITY_LABEL[card.severity ?? ""] ?? card.severity}
          </span>
        </div>
      </div>

      <div>
        <div className="mb-1 text-[11px] uppercase tracking-[0.8px] text-dim">Lý do chuyển người</div>
        <div className="text-[13.5px] font-medium text-terracotta-ink">
          {formatEscalationReason(card.escalation_reason)}
        </div>
        {flags.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1.5">
            {flags.map((f) => (
              <span
                key={f}
                className="rounded-md border border-terracotta-line bg-terracotta-soft px-2 py-0.5 text-[11.5px] text-terracotta"
              >
                {FLAG_LABEL[f] ?? f}
              </span>
            ))}
          </div>
        )}
      </div>

      <div>
        <div className="mb-1 text-[11px] uppercase tracking-[0.8px] text-dim">Tóm tắt bối cảnh</div>
        <div className="text-[14.5px] leading-[1.6] text-ink-2">{card.summary || "—"}</div>
      </div>

      <div className="flex flex-wrap gap-3.5">
        <div className="min-w-[200px] flex-1 rounded-[11px] border border-line bg-white px-[18px] py-4">
          <div className="mb-2 text-[11px] uppercase tracking-[0.8px] text-dim">Intent &amp; thực thể</div>
          <span className="rounded-md bg-olive-soft px-[9px] py-[3px] text-[12.5px] text-olive-dark">
            {formatIntent(card.intent)}
          </span>
          <div className="mt-3 flex flex-col gap-1.5">
            {Object.entries(card.entities ?? {}).length === 0 && (
              <span className="text-[13px] text-dim">— không có thực thể —</span>
            )}
            {Object.entries(card.entities ?? {}).map(([k, v]) => (
              <div key={k} className="flex items-center justify-between gap-3 text-[13px]">
                <span className="text-faint">{k}</span>
                <span className="font-semibold text-ink">{String(v)}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="min-w-[200px] flex-1 rounded-[11px] border border-line bg-white px-[18px] py-4">
          <div className="mb-2 text-[11px] uppercase tracking-[0.8px] text-dim">Tri thức truy hồi (RAG)</div>
          {card.rag_context.length === 0 && (
            <span className="text-[13px] text-dim">— không truy hồi được tri thức —</span>
          )}
          {card.rag_context.map((r, i) => (
            <div key={i} className="mb-2 border-l-2 border-line-olive pl-[11px]">
              <div className="flex items-center justify-between gap-2">
                <span className="truncate text-[11.5px] text-olive-dark">{r.source}</span>
                {r.score != null && <span className="flex-none text-[11px] text-dim">điểm {r.score}</span>}
              </div>
              <div className="mt-0.5 text-[12.5px] leading-[1.5] text-muted">{r.snippet}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
