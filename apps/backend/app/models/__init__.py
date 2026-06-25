"""Models package — import tất cả để Alembic autogenerate thấy & registry resolve quan hệ."""

from __future__ import annotations

from .audit_log import AuditLog
from .base import Base, TimestampMixin, UUIDMixin
from .conversation import Conversation
from .enums import AgentAction, ConversationStatus, MessageSender, TicketStatus
from .knowledge_document import KnowledgeDocument
from .message import Message

__all__ = [
    "Base",
    "TimestampMixin",
    "UUIDMixin",
    "Conversation",
    "Message",
    "KnowledgeDocument",
    "AuditLog",
    "ConversationStatus",
    "MessageSender",
    "AgentAction",
    "TicketStatus",
]
