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
