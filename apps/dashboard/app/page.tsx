import Link from "next/link";
import { AgentTracePanel } from "@/components/AgentTracePanel";
import { ConversationList } from "@/components/ConversationList";
import { ServiceStatus } from "@/components/ServiceStatus";

export default function DashboardPage() {
  return (
    <main className="mx-auto max-w-5xl px-6 py-10">
      <header className="mb-8 flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">
            Autonomous Customer Support — Admin Dashboard
          </h1>
          <p className="text-sm text-neutral-500">
            Scaffold · pipeline cố định (không Supervisor) · node là stub
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Link
            href="/rag"
            className="rounded-md border border-neutral-300 px-3 py-1.5 text-sm hover:bg-neutral-100"
          >
            Quản lý tri thức (RAG) →
          </Link>
          <Link
            href="/chat"
            className="rounded-md border border-neutral-300 px-3 py-1.5 text-sm hover:bg-neutral-100"
          >
            Cổng chat khách →
          </Link>
        </div>
      </header>

      <div className="grid gap-6">
        <ServiceStatus />
        <AgentTracePanel />
        <ConversationList />
      </div>

      <footer className="mt-10 text-xs text-neutral-400">
        Nguồn chân lý: <code>PRD.md</code>. Module Admin đầy đủ (RAG · Monitoring ·
        Analytics · Audit · Gate — PRD §17) là phase sau.
      </footer>
    </main>
  );
}
