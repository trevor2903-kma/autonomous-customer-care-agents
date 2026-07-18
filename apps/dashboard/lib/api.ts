import type {
  AdminConversation,
  AnalyzeResult,
  Conversation,
  ConversationListItem,
  Escalation,
  HealthStatus,
  IntentClassification,
  PipelineResult,
  RagInfo,
  RagUploadResult,
  RunDemoResult,
} from "shared-types";

export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
export const WS_URL =
  process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000/ws/chat";
// Base WS (bỏ đuôi /ws/chat) để dựng URL admin: {base}/ws/admin/{id}.
export const WS_BASE = WS_URL.replace(/\/ws\/chat$/, "");
export function adminWsUrl(conversationId: string): string {
  return `${WS_BASE}/ws/admin/${conversationId}`;
}

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

// FULL pipeline (4 agent) cho inspector — quan sát Agent 3 (quyết định) + Agent 4 (reply). Single-shot, KHÔNG persist.
export async function runPipeline(message: string): Promise<PipelineResult> {
  const res = await fetch(`${API_BASE}/api/agents/pipeline`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
  if (!res.ok) throw new Error(`pipeline ${res.status}`);
  return res.json();
}

// ── Admin HITL (08b, PRD §11/§17) ────────────────────────────────────────────
// Hàng đợi escalation (sắp theo priority ở backend).
export async function getEscalations(): Promise<Escalation[]> {
  const res = await fetch(`${API_BASE}/api/admin/escalations`, { cache: "no-store" });
  if (!res.ok) throw new Error(`escalations ${res.status}`);
  return res.json();
}

// Hội thoại đầy đủ (messages + EscalationCard) cho màn admin tiếp quản/duyệt.
export async function getAdminConversation(id: string): Promise<AdminConversation> {
  const res = await fetch(`${API_BASE}/api/admin/conversations/${id}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`admin conversation ${res.status}`);
  return res.json();
}

// Danh sách hội thoại (10a) — truyền nhiều status để lọc theo nhóm.
export async function getConversations(
  statuses?: string[],
  limit = 50,
): Promise<ConversationListItem[]> {
  const qs = new URLSearchParams();
  for (const s of statuses ?? []) qs.append("status", s);
  qs.set("limit", String(limit));
  const res = await fetch(`${API_BASE}/api/admin/conversations?${qs.toString()}`, {
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`conversations ${res.status}`);
  return res.json();
}

// Tiếp quản TƯỜNG MINH (08c) — mở hội thoại chỉ là xem, đổi trạng thái chỉ khi bấm nút này.
export async function takeoverConversation(id: string): Promise<AdminConversation> {
  const res = await fetch(`${API_BASE}/api/admin/conversations/${id}/takeover`, { method: "POST" });
  if (!res.ok) throw new Error(`takeover ${res.status}`);
  return res.json();
}

// Duyệt nháp (08a): gửi nháp (đã duyệt/sửa) tới khách. Bỏ trống content → dùng nháp trong card.
export async function approveDraft(id: string, content?: string): Promise<AdminConversation> {
  const res = await fetch(`${API_BASE}/api/admin/conversations/${id}/approve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content: content ?? null }),
  });
  if (!res.ok) throw new Error(`approve ${res.status}`);
  return res.json();
}

// Đóng ca sau khi xử lý xong → RESOLVED.
export async function resolveConversation(id: string): Promise<AdminConversation> {
  const res = await fetch(`${API_BASE}/api/admin/conversations/${id}/resolve`, { method: "POST" });
  if (!res.ok) throw new Error(`resolve ${res.status}`);
  return res.json();
}

// Từ chối nháp (08a) → IN_HUMAN_QUEUE (admin tự tiếp quản xử lý).
export async function rejectDraft(id: string): Promise<AdminConversation> {
  const res = await fetch(`${API_BASE}/api/admin/conversations/${id}/reject`, { method: "POST" });
  if (!res.ok) throw new Error(`reject ${res.status}`);
  return res.json();
}
