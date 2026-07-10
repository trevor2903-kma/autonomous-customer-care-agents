import type {
  AnalyzeResult,
  Conversation,
  HealthStatus,
  IntentClassification,
  RagInfo,
  RagUploadResult,
  RunDemoResult,
} from "shared-types";

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

// ── RAG management (PRD §17 Module 1) ────────────────────────────────────────
export async function uploadKnowledgeDoc(file: File): Promise<RagUploadResult> {
  const form = new FormData();
  form.append("file", file);
  // KHÔNG tự set Content-Type — để trình duyệt gắn multipart boundary.
  const res = await fetch(`${API_BASE}/api/rag/upload`, { method: "POST", body: form });
  if (!res.ok) throw new Error(`upload ${res.status}: ${await res.text()}`);
  return res.json();
}

export async function getRagInfo(): Promise<RagInfo> {
  const res = await fetch(`${API_BASE}/api/rag/info`, { cache: "no-store" });
  if (!res.ok) throw new Error(`rag info ${res.status}`);
  return res.json();
}

export async function resetRag(): Promise<RagInfo> {
  const res = await fetch(`${API_BASE}/api/rag/reset`, { method: "POST" });
  if (!res.ok) throw new Error(`rag reset ${res.status}`);
  return res.json();
}

// Agent 1 · Intent Classifier (PRD §7.1) — chỉ intent/entities, KHÔNG retrieval.
export async function classifyMessage(message: string): Promise<IntentClassification> {
  const res = await fetch(`${API_BASE}/api/agents/classify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
  if (!res.ok) throw new Error(`classify ${res.status}`);
  return res.json();
}

// Agent 1 + Agent 2 · Knowledge Agent (PRD §7.2) — tách vai: intent/entities + truy hồi rag_contexts.
export async function analyzeMessage(message: string): Promise<AnalyzeResult> {
  const res = await fetch(`${API_BASE}/api/agents/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
  if (!res.ok) throw new Error(`analyze ${res.status}`);
  return res.json();
}
