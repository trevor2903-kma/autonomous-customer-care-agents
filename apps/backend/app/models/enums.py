"""Enum canonical — dùng thống nhất backend + shared-types + dashboard (CLAUDE.md).

`ConversationStatus` = tập canonical PRD §15. KHÔNG tự thêm/bớt trạng thái — sửa PRD trước.
"""

from __future__ import annotations

from enum import StrEnum


class ConversationStatus(StrEnum):
    # Vòng đời hội thoại (PRD §15)
    NEW = "NEW"
    ACTIVE_AI = "ACTIVE_AI"
    CLASSIFYING = "CLASSIFYING"
    RETRIEVING = "RETRIEVING"
    DECIDING = "DECIDING"
    RESPONDING = "RESPONDING"
    REPLIED = "REPLIED"
    AWAITING_CUSTOMER = "AWAITING_CUSTOMER"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    IN_HUMAN_QUEUE = "IN_HUMAN_QUEUE"
    HUMAN_HANDLING = "HUMAN_HANDLING"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class Intent(StrEnum):
    # Tập ĐÓNG intent (PRD §7.1) — dùng validate nhãn LLM trả về (chống trôi nhãn). Ngoài tập -> other.
    PRODUCT_PRICE = "product_price"
    PRODUCT_INFORMATION = "product_information"
    SIZE_CONSULTING = "size_consulting"
    SHIPPING = "shipping"
    ORDER_STATUS = "order_status"
    REFUND = "refund"
    EXCHANGE = "exchange"
    COMPLAINT = "complaint"
    PROMOTION = "promotion"
    OTHER = "other"


class MessageSender(StrEnum):
    CUSTOMER = "customer"
    AI = "ai"
    ADMIN = "admin"


class AgentAction(StrEnum):
    # Decision Engine output (PRD §7.3)
    AUTO_REPLY = "auto_reply"
    HUMAN_HANDOFF = "human_handoff"


class TicketStatus(StrEnum):
    # Cấp ticket — thô hơn conversation (PRD §15 ghi chú)
    OPEN = "open"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"
