import type { Conversation, HealthStatus, RunDemoResult } from "shared-types";

export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
export const WS_URL =
  process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000/ws/chat";

export async function getHealth(): Promise<HealthStatus> {
  const res = await fetch(`${API_BASE}/api/health`, { cache: "no-store" });
  if (!res.ok) throw new Error(`health ${res.status}`);
  return res.json();
}

export async function runDemo(force?: "handoff"): Promise<RunDemoResult> {
  const qs = force ? `?force=${force}` : "";
  const res = await fetch(`${API_BASE}/api/agents/run-demo${qs}`, {
    method: "POST",
  });
  if (!res.ok) throw new Error(`run-demo ${res.status}`);
  return res.json();
}

export async function listConversations(): Promise<Conversation[]> {
  const res = await fetch(`${API_BASE}/api/conversations`, {
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`conversations ${res.status}`);
  return res.json();
}
