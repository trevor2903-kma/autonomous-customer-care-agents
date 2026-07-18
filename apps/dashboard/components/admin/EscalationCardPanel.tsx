import type { EscalationCard } from "shared-types";

// EscalationCard (design, PRD §11): vì sao ca này cần người — ưu tiên/mức độ, lý do + cờ, tóm tắt,
// intent & thực thể, tri thức RAG đã truy hồi. Đây là ngữ cảnh để admin nắm ca trong vài giây.

const PRIO: Record<string, { color: string; soft: string; label: string }> = {
  high: { color: "#B25B3C", soft: "#F6E7DF", label: "cao" },
  medium: { color: "#B98534", soft: "#F7EFDD", label: "trung bình" },
  low: { color: "#8E887B", soft: "#F0EDE6", label: "thấp" },
};

// escalation_reason có dạng `blocking_flags=['out_of_domain', ...]` → tách thành chip cho dễ đọc.
function flagsFromReason(reason?: string | null): string[] {
  const m = reason?.match(/\[(.*)\]/);
  if (!m) return [];
  return m[1]
    .split(",")
    .map((s) => s.trim().replace(/^['"]|['"]$/g, ""))
    .filter(Boolean);
}

export function EscalationCardPanel({
  card,
  identifier,
}: {
  card: EscalationCard;
  identifier?: string | null;
}) {
  const prio = PRIO[card.priority ?? ""] ?? PRIO.low;
  const flags = flagsFromReason(card.escalation_reason);

  return (
    <section className="flex flex-col gap-[18px]">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <div className="text-[11px] uppercase tracking-[1.5px] text-dim">EscalationCard</div>
          <div className="mt-1 truncate font-mono text-[12.5px] text-faint">{identifier ?? "—"}</div>
        </div>
        <div className="flex flex-none gap-2">
          <span
            className="rounded-[7px] px-[11px] py-[5px] text-xs"
            style={{ color: prio.color, background: prio.soft }}
          >
            Ưu tiên {prio.label}
          </span>
          <span className="rounded-[7px] bg-line-soft px-[11px] py-[5px] text-xs text-faint">
            Mức độ {card.severity ?? "—"}
          </span>
        </div>
      </div>

      <div className="rounded-[11px] border border-terracotta-line bg-terracotta-soft px-4 py-3.5">
        <div className="mb-1.5 text-[11px] uppercase tracking-[0.8px] text-terracotta">Lý do chuyển tiếp</div>
        <div className="text-sm leading-[1.5] text-terracotta-ink">{card.escalation_reason ?? "—"}</div>
        {flags.length > 0 && (
          <div className="mt-2.5 flex flex-wrap gap-[7px]">
            {flags.map((f) => (
              <span
                key={f}
                className="rounded-[5px] border border-terracotta-line bg-white px-2 py-0.5 font-mono text-[11px] text-terracotta"
              >
                {f}
              </span>
            ))}
          </div>
        )}
      </div>

      <div className="rounded-[11px] border border-line bg-white px-[18px] py-4">
        <div className="mb-1.5 text-[11px] uppercase tracking-[0.8px] text-dim">Tin khách kích hoạt</div>
        <div className="text-[14.5px] leading-[1.6] text-ink-2">{card.summary || "—"}</div>
      </div>

      <div className="flex flex-wrap gap-3.5">
        <div className="min-w-[200px] flex-1 rounded-[11px] border border-line bg-white px-[18px] py-4">
          <div className="mb-2 text-[11px] uppercase tracking-[0.8px] text-dim">Intent &amp; thực thể</div>
          <span className="rounded-md bg-olive-soft px-[9px] py-[3px] font-mono text-[12.5px] text-olive-dark">
            {card.intent ?? "—"}
          </span>
          <div className="mt-3 flex flex-col gap-1.5">
            {Object.entries(card.entities ?? {}).length === 0 && (
              <span className="text-[13px] text-dim">— không có thực thể —</span>
            )}
            {Object.entries(card.entities ?? {}).map(([k, v]) => (
              <div key={k} className="flex items-center justify-between gap-3 text-[13px]">
                <span className="font-mono text-faint">{k}</span>
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
                <span className="truncate font-mono text-[11.5px] text-olive-dark">{r.source}</span>
                {r.score != null && <span className="flex-none text-[11px] text-dim">điểm {r.score}</span>}
              </div>
              <div className="mt-0.5 text-[12.5px] leading-[1.5] text-muted">{r.snippet}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
