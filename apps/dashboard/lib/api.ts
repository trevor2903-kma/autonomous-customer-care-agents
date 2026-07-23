import type {
  AdminConversation,
  AnalyzeResult,
  Conversation,
  ConversationListItem,
  Escalation,
  HealthStatus,
  IntentClassification,
  MessageSender,
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

// ── Auth token (slice 11 P4) — lưu localStorage, gắn Bearer cho mọi request ──
const TOKEN_KEY = "tys_token";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY);
}
export function setToken(token: string): void {
  if (typeof window !== "undefined") window.localStorage.setItem(TOKEN_KEY, token);
}
export function clearToken(): void {
  if (typeof window !== "undefined") window.localStorage.removeItem(TOKEN_KEY);
}

function authHeaders(): Record<string, string> {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

// Wrapper fetch: prepend API_BASE + gắn Bearer + no-store. Giữ header init (Content-Type) đè lên.
async function req(path: string, init: RequestInit = {}): Promise<Response> {
  return fetch(`${API_BASE}${path}`, {
    cache: "no-store",
    ...init,
    headers: { ...authHeaders(), ...(init.headers ?? {}) },
  });
}

async function fail(res: Response, fallback: string): Promise<never> {
  let detail = fallback;
  try {
    const body = await res.json();
    if (body?.detail) detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
  } catch {
    // body không phải JSON → dùng fallback
  }
  throw new Error(detail);
}

// ── WS URL kèm token (browser không set được header WS → query-param) ─────────
export function chatWsUrl(token: string): string {
  return `${WS_URL}?token=${encodeURIComponent(token)}`;
}
export function adminWsUrl(conversationId: string, token: string): string {
  return `${WS_BASE}/ws/admin/${conversationId}?token=${encodeURIComponent(token)}`;
}

// ── Auth (slice 11) ──────────────────────────────────────────────────────────
export interface AuthUser {
  id: string;
  email: string;
  role: "admin" | "customer" | string;
  display_name?: string | null;
}
export interface TokenResponse {
  access_token: string;
  token_type: string;
  user_id: string;
  role: "admin" | "customer" | string;
  display_name?: string | null;
}

export async function login(email: string, password: string): Promise<TokenResponse> {
  const res = await req("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) await fail(res, "Đăng nhập thất bại");
  return res.json();
}

export async function register(
  email: string,
  password: string,
  displayName?: string,
): Promise<TokenResponse> {
  const res = await req("/api/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, display_name: displayName || null }),
  });
  if (!res.ok) await fail(res, "Tạo tài khoản thất bại");
  return res.json();
}

export async function getMe(): Promise<AuthUser> {
  const res = await req("/api/auth/me");
  if (!res.ok) throw new Error(`me ${res.status}`);
  return res.json();
}

export async function getHealth(): Promise<HealthStatus> {
  const res = await req("/api/health");
  if (!res.ok) throw new Error(`health ${res.status}`);
  return res.json();
}

export async function runDemo(force?: "handoff"): Promise<RunDemoResult> {
  const qs = force ? `?force=${force}` : "";
  const res = await req(`/api/agents/run-demo${qs}`, { method: "POST" });
  if (!res.ok) throw new Error(`run-demo ${res.status}`);
  return res.json();
}

export async function listConversations(): Promise<Conversation[]> {
  const res = await req("/api/conversations");
  if (!res.ok) throw new Error(`conversations ${res.status}`);
  return res.json();
}

// ── RAG management (PRD §17 Module 1) ────────────────────────────────────────
export async function uploadKnowledgeDoc(file: File): Promise<RagUploadResult> {
  const form = new FormData();
  form.append("file", file);
  // KHÔNG tự set Content-Type — để trình duyệt gắn multipart boundary.
  const res = await req("/api/rag/upload", { method: "POST", body: form });
  if (!res.ok) throw new Error(`upload ${res.status}: ${await res.text()}`);
  return res.json();
}

export async function getRagInfo(): Promise<RagInfo> {
  const res = await req("/api/rag/info");
  if (!res.ok) throw new Error(`rag info ${res.status}`);
  return res.json();
}

export async function resetRag(): Promise<RagInfo> {
  const res = await req("/api/rag/reset", { method: "POST" });
  if (!res.ok) throw new Error(`rag reset ${res.status}`);
  return res.json();
}

// ── Sổ tài liệu tri thức (P3) — repo là nguồn chân lý, upload chỉ là ad-hoc ──
export interface KnowledgeDocument {
  id: string;
  source: string;
  title: string;
  doc_type: string | null; // faq|case|reference|promotion|upload
  intent: string | null;
  format: string | null;
  status: string;
  chunks: number;
  canonical: boolean; // false = ad-hoc, mất khi nạp lại từ repo
  indexed_at: string | null;
}
export interface ReindexResult {
  documents: number;
  points: number;
  collection: string;
}

export async function getRagDocuments(): Promise<KnowledgeDocument[]> {
  const res = await req("/api/rag/documents");
  if (!res.ok) await fail(res, `rag documents ${res.status}`);
  return res.json();
}

export async function reindexRag(): Promise<ReindexResult> {
  const res = await req("/api/rag/reindex", { method: "POST" });
  if (!res.ok) await fail(res, `rag reindex ${res.status}`);
  return res.json();
}

export async function deleteRagDocument(id: string): Promise<KnowledgeDocument> {
  const res = await req(`/api/rag/documents/${id}`, { method: "DELETE" });
  if (!res.ok) await fail(res, `rag delete ${res.status}`);
  return res.json();
}

// Agent 1 · Intent Classifier (PRD §7.1) — chỉ intent/entities, KHÔNG retrieval.
export async function classifyMessage(message: string): Promise<IntentClassification> {
  const res = await req("/api/agents/classify", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
  if (!res.ok) throw new Error(`classify ${res.status}`);
  return res.json();
}

// Agent 1 + Agent 2 · Knowledge Agent (PRD §7.2) — tách vai: intent/entities + truy hồi rag_contexts.
export async function analyzeMessage(message: string): Promise<AnalyzeResult> {
  const res = await req("/api/agents/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
  if (!res.ok) throw new Error(`analyze ${res.status}`);
  return res.json();
}

// FULL pipeline (4 agent) cho inspector — quan sát Agent 3 (quyết định) + Agent 4 (reply). Single-shot, KHÔNG persist.
export async function runPipeline(message: string): Promise<PipelineResult> {
  const res = await req("/api/agents/pipeline", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
  if (!res.ok) throw new Error(`pipeline ${res.status}`);
  return res.json();
}

// ── Admin HITL (08b, PRD §11/§17) ────────────────────────────────────────────
export async function getEscalations(): Promise<Escalation[]> {
  const res = await req("/api/admin/escalations");
  if (!res.ok) throw new Error(`escalations ${res.status}`);
  return res.json();
}

export async function getAdminConversation(id: string): Promise<AdminConversation> {
  const res = await req(`/api/admin/conversations/${id}`);
  if (!res.ok) throw new Error(`admin conversation ${res.status}`);
  return res.json();
}

export async function getConversations(
  statuses?: string[],
  limit = 50,
): Promise<ConversationListItem[]> {
  const qs = new URLSearchParams();
  for (const s of statuses ?? []) qs.append("status", s);
  qs.set("limit", String(limit));
  const res = await req(`/api/admin/conversations?${qs.toString()}`);
  if (!res.ok) throw new Error(`conversations ${res.status}`);
  return res.json();
}

export async function takeoverConversation(id: string): Promise<AdminConversation> {
  const res = await req(`/api/admin/conversations/${id}/takeover`, { method: "POST" });
  if (!res.ok) throw new Error(`takeover ${res.status}`);
  return res.json();
}

export async function approveDraft(id: string, content?: string): Promise<AdminConversation> {
  const res = await req(`/api/admin/conversations/${id}/approve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content: content ?? null }),
  });
  if (!res.ok) throw new Error(`approve ${res.status}`);
  return res.json();
}

export async function resolveConversation(id: string): Promise<AdminConversation> {
  const res = await req(`/api/admin/conversations/${id}/resolve`, { method: "POST" });
  if (!res.ok) throw new Error(`resolve ${res.status}`);
  return res.json();
}

export async function rejectDraft(id: string): Promise<AdminConversation> {
  const res = await req(`/api/admin/conversations/${id}/reject`, { method: "POST" });
  if (!res.ok) throw new Error(`reject ${res.status}`);
  return res.json();
}

// ── Gate động (slice 11 P3/P5) ───────────────────────────────────────────────
export interface GateIntentRule {
  intent: string;
  label: string;
  sensitive: boolean;
  send_directly: boolean;
}
export interface GateConfig {
  auto_reply_enabled: boolean;
  auto_resolve_enabled: boolean;
  auto_resolve_minutes: number;
  retrieval_threshold: number; // read-only hiển thị (P3-b hoãn)
  rules: GateIntentRule[];
}
export interface GateConfigUpdate {
  auto_reply_enabled?: boolean;
  auto_resolve_enabled?: boolean;
  auto_resolve_minutes?: number;
  rules?: { intent: string; send_directly: boolean }[];
}

export async function getGateConfig(): Promise<GateConfig> {
  const res = await req("/api/admin/gate-config");
  if (!res.ok) throw new Error(`gate-config ${res.status}`);
  return res.json();
}

export async function updateGateConfig(payload: GateConfigUpdate): Promise<GateConfig> {
  const res = await req("/api/admin/gate-config", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`gate-config update ${res.status}`);
  return res.json();
}

// ── Mạch ghép của khách (slice 11 P2/P6) ─────────────────────────────────────
export interface ThreadMessage {
  id: string;
  conversation_id: string;
  sender: MessageSender;
  content: string;
  created_at: string;
}
export interface CustomerThread {
  messages: ThreadMessage[];
  active_conversation_id: string | null;
  active_status: string | null;
}

export async function getMyThread(): Promise<CustomerThread> {
  const res = await req("/api/me/thread");
  if (!res.ok) throw new Error(`thread ${res.status}`);
  return res.json();
}
