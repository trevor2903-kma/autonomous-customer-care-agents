// shared-types — type dùng chung backend ↔ dashboard.
// ConversationStatus là tập canonical PRD §15 — đồng bộ với backend app/models/enums.py.
// Mọi thay đổi trạng thái: sửa PRD trước, rồi đồng bộ cả hai nơi (CLAUDE.md).

export enum ConversationStatus {
  NEW = "NEW",
  ACTIVE_AI = "ACTIVE_AI",
  CLASSIFYING = "CLASSIFYING",
  RETRIEVING = "RETRIEVING",
  DECIDING = "DECIDING",
  RESPONDING = "RESPONDING",
  REPLIED = "REPLIED",
  AWAITING_CUSTOMER = "AWAITING_CUSTOMER",
  PENDING_APPROVAL = "PENDING_APPROVAL",
  IN_HUMAN_QUEUE = "IN_HUMAN_QUEUE",
  HUMAN_HANDLING = "HUMAN_HANDLING",
  RESOLVED = "RESOLVED",
  CLOSED = "CLOSED",
}

export type MessageSender = "customer" | "ai" | "admin";

export interface Message {
  id: string;
  sender: MessageSender;
  content: string;
  intent?: string | null;
  confidence?: number | null;
  created_at: string;
}

export interface Conversation {
  id: string;
  customer_identifier?: string | null;
  status: ConversationStatus | string;
  current_intent?: string | null;
  entities?: Record<string, unknown>;
  confidence?: number | null;
  uncertainty_flags?: string[];
  escalation_reason?: string | null;
  created_at: string;
  updated_at: string;
  last_message_at?: string | null;
  messages?: Message[];
}

// Một bước trong agent-trace (PRD §17 Module 3 — Agent Monitoring).
export interface AgentTraceStep {
  node: string;
  confidence?: number | null;
  branch?: string | null;
  detail?: Record<string, unknown>;
}

export interface RunDemoResult {
  thread_id: string;
  branch: string; // response | human_handoff
  status: string;
  action?: string | null;
  confidence?: number | null;
  require_human_handoff: boolean;
  escalation_reason?: string | null;
  reply?: string | null;
  trace: AgentTraceStep[];
}

// RAG management (PRD §17 Module 1) + Intent Classifier metadata (PRD §7.1).
export interface RagUploadResult {
  source: string;
  chunks: number;
  collection: string;
}

export interface RagInfo {
  collection: string;
  points_count: number;
  sources: string[];
}

// Agent 1 · Intent Classifier (PRD §7.1) — metadata phân loại SẠCH, KHÔNG retrieval (khớp ClassifyResult).
export interface IntentClassification {
  intent: string;
  category: string | null;
  entities: Record<string, unknown>;
  confidence: number;
  uncertainty_flags: string[];
}

// Một đoạn tri thức Agent 2 truy hồi được. `type`/`title` từ frontmatter KB (chunk repo); doc upload
// ad-hoc không có frontmatter nên hai trường này vắng.
export interface RagContext {
  text?: string;
  source: string;
  type?: string | null; // faq | case | reference | promotion | upload
  title?: string | null;
  score: number;
}

// Agent 1 (intent/entities) + Agent 2 · Knowledge Agent (retrieval) — PRD §7.2 (khớp AnalyzeResult backend).
export interface AnalyzeResult {
  intent: string; // Agent 1
  category: string | null; // Agent 1
  entities: Record<string, unknown>; // Agent 1
  intent_confidence: number; // Agent 1
  retrieval_confidence: number; // Agent 2
  uncertainty_flags: string[]; // gộp cờ Agent 1 + Agent 2
  rag_contexts: RagContext[]; // Agent 2
}

// FULL pipeline slice (4 agent) cho inspector — quan sát quyết định Agent 3 + câu trả lời Agent 4.
export interface PipelineResult {
  intent: string; // Agent 1
  category: string | null; // Agent 1
  entities: Record<string, unknown>; // Agent 1
  intent_confidence: number; // Agent 1
  retrieval_confidence: number; // Agent 2
  rag_contexts: RagContext[]; // Agent 2
  action: string | null; // Agent 3 (auto_reply | human_handoff)
  priority: string | null; // Agent 3
  severity: string | null; // Agent 3
  escalation_reason: string | null; // Agent 3
  uncertainty_flags: string[];
  reply: string | null; // Agent 4
}

// HITL admin (08b, PRD §11/§17) — EscalationCard + hàng đợi + hội thoại cho màn admin.
export interface EscalationCard {
  summary: string;
  intent: string | null;
  entities: Record<string, unknown>;
  rag_context: { source: string; score?: number | null; snippet: string }[];
  escalation_reason: string | null;
  priority: string | null;
  severity: string | null;
  suggested_reply: string;
}

export interface Escalation {
  conversation_id: string;
  customer_identifier?: string | null;
  status: ConversationStatus | string;
  priority?: string | null;
  severity?: string | null;
  escalation_reason?: string | null;
  escalation_card?: EscalationCard | null;
  last_message_at?: string | null;
}

// Một dòng danh sách hội thoại admin (10a) — preview = tin cuối.
export interface ConversationListItem {
  id: string;
  customer_identifier?: string | null;
  status: ConversationStatus | string;
  current_intent?: string | null;
  last_message_at?: string | null;
  preview?: string | null;
}

export interface AdminConversation {
  id: string;
  customer_identifier?: string | null;
  status: ConversationStatus | string;
  priority?: string | null;
  severity?: string | null;
  escalation_reason?: string | null;
  escalation_card?: EscalationCard | null;
  assigned_admin_id?: string | null;
  created_at: string;
  last_message_at?: string | null;
  messages: Message[];
}

export interface ServiceProbe {
  ok: boolean;
  detail: unknown;
}

export interface HealthStatus {
  status: string; // ok | degraded
  api: string;
  enable_llm: boolean;
  services: {
    database: ServiceProbe;
    redis: ServiceProbe;
    qdrant: ServiceProbe;
  };
}
