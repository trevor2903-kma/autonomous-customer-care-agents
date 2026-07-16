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


class Category(StrEnum):
    # Nhóm category của intent (PRD §7.1). Chunk generic KHÔNG mang category → suy từ INTENT_CATEGORY.
    PRE_SALE = "pre_sale"
    AFTER_SALE = "after_sale"
    GENERAL = "general"


# Map tĩnh intent -> category (chunk generic không mang nhãn category).
INTENT_CATEGORY: dict[Intent, Category] = {
    Intent.PRODUCT_PRICE: Category.PRE_SALE,
    Intent.PRODUCT_INFORMATION: Category.PRE_SALE,
    Intent.SIZE_CONSULTING: Category.PRE_SALE,
    Intent.PROMOTION: Category.PRE_SALE,
    Intent.ORDER_STATUS: Category.AFTER_SALE,
    Intent.REFUND: Category.AFTER_SALE,
    Intent.EXCHANGE: Category.AFTER_SALE,
    Intent.COMPLAINT: Category.AFTER_SALE,
    Intent.SHIPPING: Category.GENERAL,
    Intent.OTHER: Category.GENERAL,
}


class MessageSender(StrEnum):
    CUSTOMER = "customer"
    AI = "ai"
    ADMIN = "admin"


class AgentAction(StrEnum):
    # Decision Engine output (PRD §7.3)
    AUTO_REPLY = "auto_reply"
    HUMAN_HANDOFF = "human_handoff"


class Priority(StrEnum):
    # Ưu tiên ca (Decision Engine — PRD §7.3, §5 trụ cột 1 Agent Monitoring). Theo intent, tất định.
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Severity(StrEnum):
    # Mức nghiêm trọng ca (Decision Engine — PRD §7.3). Theo intent, tất định.
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TicketStatus(StrEnum):
    # Cấp ticket — thô hơn conversation (PRD §15 ghi chú)
    OPEN = "open"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"
