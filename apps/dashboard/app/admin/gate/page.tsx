"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  type GateConfig,
  type GateConfigUpdate,
  getGateConfig,
  updateGateConfig,
} from "@/lib/api";

// Module Cấu hình Gate (slice 11 P5) — 2 toggle hệ thống + bảng per-intent (Gửi thẳng/Duyệt nháp)
// + slider "Ngưỡng confidence chuyển người" READ-ONLY. Gate = van cho auto_reply; escalation an toàn KHÔNG bị gate.

function Switch({
  checked,
  onChange,
  variant = "system",
  disabled = false,
}: {
  checked: boolean;
  onChange: (v: boolean) => void;
  variant?: "system" | "intent";
  disabled?: boolean;
}) {
  const w = variant === "system" ? 48 : 44;
  const h = variant === "system" ? 27 : 25;
  const knob = variant === "system" ? 21 : 19;
  const pad = 3;
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      disabled={disabled}
      onClick={() => onChange(!checked)}
      style={{ width: w, height: h }}
      className={`relative flex-none rounded-full transition-colors ${
        checked ? "bg-olive" : "bg-[#DAD5C8]"
      } ${disabled ? "cursor-not-allowed opacity-60" : ""}`}
    >
      <span
        style={{
          width: knob,
          height: knob,
          top: (h - knob) / 2,
          left: pad,
          transform: checked ? `translateX(${w - knob - pad * 2}px)` : "translateX(0)",
        }}
        className="absolute rounded-full bg-white shadow-[0_1px_2px_rgba(0,0,0,0.2)] transition-transform"
      />
    </button>
  );
}

function applyPatch(cfg: GateConfig, patch: GateConfigUpdate): GateConfig {
  const next: GateConfig = { ...cfg };
  if (patch.auto_reply_enabled !== undefined) next.auto_reply_enabled = patch.auto_reply_enabled;
  if (patch.auto_resolve_enabled !== undefined) next.auto_resolve_enabled = patch.auto_resolve_enabled;
  if (patch.auto_resolve_minutes !== undefined) next.auto_resolve_minutes = patch.auto_resolve_minutes;
  if (patch.rules) {
    const m = new Map(patch.rules.map((r) => [r.intent, r.send_directly]));
    next.rules = cfg.rules.map((r) => (m.has(r.intent) ? { ...r, send_directly: m.get(r.intent)! } : r));
  }
  return next;
}

function ToggleRow({
  label,
  desc,
  checked,
  onChange,
}: {
  label: string;
  desc: string;
  checked: boolean;
  onChange: (v: boolean) => void;
}) {
  return (
    <div className="flex items-center justify-between gap-4 rounded-[12px] border border-line bg-white px-[18px] py-4 shadow-soft">
      <div className="min-w-0">
        <div className="text-[14.5px] font-semibold text-ink">{label}</div>
        <div className="mt-0.5 text-[12.5px] leading-[1.5] text-faint">{desc}</div>
      </div>
      <Switch checked={checked} onChange={onChange} variant="system" />
    </div>
  );
}

export default function GatePage() {
  const qc = useQueryClient();
  const { data: cfg, isLoading, isError, error } = useQuery<GateConfig, Error>({
    queryKey: ["gate-config"],
    queryFn: getGateConfig,
  });

  const mutation = useMutation<GateConfig, Error, GateConfigUpdate, { prev?: GateConfig }>({
    mutationFn: updateGateConfig,
    onMutate: async (patch) => {
      await qc.cancelQueries({ queryKey: ["gate-config"] });
      const prev = qc.getQueryData<GateConfig>(["gate-config"]);
      if (prev) qc.setQueryData(["gate-config"], applyPatch(prev, patch));
      return { prev };
    },
    onError: (_e, _v, ctx) => {
      if (ctx?.prev) qc.setQueryData(["gate-config"], ctx.prev);
    },
    onSuccess: (data) => qc.setQueryData(["gate-config"], data),
  });

  return (
    <div className="mx-auto w-full max-w-3xl px-6 py-8 mob:px-4">
      <header className="mb-6">
        <h1 className="font-serif text-[27px] text-ink">Cấu hình Gate</h1>
        <p className="mt-1.5 max-w-2xl text-[13.5px] leading-[1.6] text-faint">
          Gate chỉ điều chỉnh mức độ tự động cho ca AI tự tin. Ca có cờ bất định luôn được chuyển nhân
          viên — an toàn không bị gate ghi đè.
        </p>
      </header>

      {isLoading && <p className="text-sm text-dim">Đang tải cấu hình…</p>}
      {isError && <p className="text-sm text-terracotta">Lỗi: {error.message}</p>}

      {cfg && (
        <div className="flex flex-col gap-6">
          {/* Toggle hệ thống */}
          <div className="flex flex-col gap-3">
            <ToggleRow
              label="Auto-reply (toàn hệ thống)"
              desc="Bật: ca AI tự tin gửi trả lời theo luật per-intent bên dưới. Tắt: mọi trả lời tự động giữ lại chờ duyệt nháp."
              checked={cfg.auto_reply_enabled}
              onChange={(v) => mutation.mutate({ auto_reply_enabled: v })}
            />
            <ToggleRow
              label="Auto-resolve"
              desc={`Tự đóng ca không hoạt động sau ${cfg.auto_resolve_minutes} phút.`}
              checked={cfg.auto_resolve_enabled}
              onChange={(v) => mutation.mutate({ auto_resolve_enabled: v })}
            />
          </div>

          {/* Bảng per-intent */}
          <section className="overflow-hidden rounded-[12px] border border-line bg-white shadow-soft">
            <div className="border-b border-line-soft px-[18px] py-3.5">
              <h2 className="text-[14px] font-semibold text-ink">Auto-reply theo intent / category</h2>
            </div>
            <div className="divide-y divide-line-soft">
              {cfg.rules.map((r) => (
                <div key={r.intent} className="flex items-center justify-between gap-3 px-[18px] py-3">
                  <div className="flex min-w-0 flex-col gap-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="text-[14px] font-medium text-ink">{r.label}</span>
                      {r.sensitive && (
                        <span className="rounded-[5px] border border-terracotta-line bg-terracotta-soft px-1.5 py-0.5 text-[10.5px] font-medium text-terracotta">
                          nhạy cảm
                        </span>
                      )}
                    </div>
                    <span className="font-mono text-[11.5px] text-dim">{r.intent}</span>
                  </div>
                  <div className="flex flex-none items-center gap-2.5">
                    <span
                      className={`w-[62px] text-right text-[12px] font-medium ${
                        r.send_directly ? "text-olive" : "text-gold"
                      }`}
                    >
                      {r.send_directly ? "Gửi thẳng" : "Duyệt nháp"}
                    </span>
                    <Switch
                      checked={r.send_directly}
                      onChange={(v) => mutation.mutate({ rules: [{ intent: r.intent, send_directly: v }] })}
                      variant="intent"
                    />
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* Slider READ-ONLY (P3-b hoãn) */}
          <div className="rounded-[12px] border border-line bg-white px-[18px] py-4 shadow-soft">
            <div className="flex items-center justify-between">
              <h2 className="text-[14px] font-semibold text-ink">Ngưỡng confidence chuyển người</h2>
              <span className="font-mono text-[14px] font-semibold text-olive">
                {cfg.retrieval_threshold.toFixed(2)}
              </span>
            </div>
            <div className="mt-3 h-1.5 w-full rounded-full bg-[#EFEBE2]" aria-hidden>
              <div
                className="h-full rounded-full bg-olive/70"
                style={{ width: `${Math.max(0, Math.min(1, cfg.retrieval_threshold)) * 100}%` }}
              />
            </div>
            <p className="mt-2.5 text-[12px] leading-[1.5] text-dim">
              Dưới ngưỡng → Decision Engine đặt action = human_handoff · điều chỉnh ở phiên bản sau.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
