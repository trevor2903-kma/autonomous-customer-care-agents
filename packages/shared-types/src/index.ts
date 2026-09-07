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

// RAG management (PRD §17 Module 1).
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

// Hai panel dev (slice obs P4) rồi `Conversation`/`RunDemoResult`/`AnalyzeResult` (dọn code chết) đã GỠ:
// việc quan sát pipeline nay là của tab Báo cáo, dựng từ `audit_log` (type ở apps/dashboard/lib/api.ts).
// Route backend `/api/agents/analyze` + `/api/health` vẫn còn — chỉ chưa có client TS nào dùng.

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
