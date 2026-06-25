"use client";

import { useQuery } from "@tanstack/react-query";
import type { HealthStatus, ServiceProbe } from "shared-types";
import { getHealth } from "@/lib/api";

function Dot({ ok }: { ok: boolean }) {
  return (
    <span
      className={`inline-block h-2.5 w-2.5 rounded-full ${
        ok ? "bg-green-500" : "bg-red-500"
      }`}
    />
  );
}

function Row({ name, probe }: { name: string; probe?: ServiceProbe }) {
  const ok = !!probe?.ok;
  return (
    <div className="flex items-center justify-between rounded-md border border-neutral-200 bg-white px-3 py-2">
      <span className="flex items-center gap-2 text-sm font-medium">
        <Dot ok={ok} />
        {name}
      </span>
      <span className="text-xs text-neutral-500">
        {ok ? "ok" : String(probe?.detail ?? "—")}
      </span>
    </div>
  );
}

export function ServiceStatus() {
  const { data, isLoading, isError } = useQuery<HealthStatus>({
    queryKey: ["health"],
    queryFn: getHealth,
    refetchInterval: 10_000,
  });

  return (
    <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
      <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-neutral-500">
        Service Status
      </h2>
      {isLoading && <p className="text-sm text-neutral-400">Đang kiểm tra…</p>}
      {isError && (
        <p className="text-sm text-red-500">
          Không gọi được backend — chạy <code>make dev-backend</code>?
        </p>
      )}
      {data && (
        <div className="grid gap-2 sm:grid-cols-2">
          <Row name="API" probe={{ ok: data.api === "ok", detail: data.api }} />
          <Row name="Neon (Postgres)" probe={data.services?.database} />
          <Row name="Upstash (Redis)" probe={data.services?.redis} />
          <Row name="Qdrant" probe={data.services?.qdrant} />
          <Row
            name="LLM (scaffold)"
            probe={{ ok: !data.enable_llm, detail: data.enable_llm ? "on" : "off (scaffold)" }}
          />
        </div>
      )}
    </section>
  );
}
