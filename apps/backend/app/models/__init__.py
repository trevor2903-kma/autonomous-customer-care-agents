"""Models package — import tất cả để Alembic autogenerate thấy & registry resolve quan hệ."""

from __future__ import annotations

from .audit_log import AuditLog
from .base import Base, TimestampMixin, UUIDMixin
from .conversation import Conversation
from .enums import (
    AgentAction,
    ConversationStatus,
    MessageSender,
    TicketStatus,
    UserRole,
)
from .gate_config import GateConfig
from .gate_intent_rule import GateIntentRule
from .knowledge_document import KnowledgeDocument
from .message import Message
from .user import User

__all__ = [
    "Base",
    "TimestampMixin",
    "UUIDMixin",
    "Conversation",
    "Message",
    "KnowledgeDocument",
    "AuditLog",
    "User",
    "GateConfig",
    "GateIntentRule",
    "ConversationStatus",
    "MessageSender",
    "AgentAction",
    "TicketStatus",
    "UserRole",
]
