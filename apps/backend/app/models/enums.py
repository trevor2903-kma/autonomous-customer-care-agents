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
    PAYMENT = "payment"
    MEMBERSHIP = "membership"
    STORE_INFORMATION = "store_information"
    # HỎI chính sách đổi/trả/hoàn (thông tin) — TÁCH khỏi refund/exchange (yêu cầu thực trên đơn).
    RETURN_EXCHANGE_POLICY = "return_exchange_policy"
    REFUND = "refund"
    EXCHANGE = "exchange"
    COMPLAINT = "complaint"
    PROMOTION = "promotion"
    GREETING = "greeting"
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
    # Chính sách/logistics/tài khoản = tra cứu, không gắn với một đơn cụ thể → GENERAL (như shipping).
    Intent.SHIPPING: Category.GENERAL,
    Intent.PAYMENT: Category.GENERAL,
    Intent.MEMBERSHIP: Category.GENERAL,
    Intent.STORE_INFORMATION: Category.GENERAL,
    Intent.RETURN_EXCHANGE_POLICY: Category.GENERAL,
    Intent.GREETING: Category.GENERAL,
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


class OrderStatus(StrEnum):
    # Vòng đời đơn hàng (slice tích hợp đơn). Hệ thống chỉ TRA CỨU trạng thái — KHÔNG thao tác trên đơn.
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERING = "delivering"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


# Nhãn tiếng Việt của trạng thái đơn — Agent 4 nói tiếng Việt nên khối context phải là nhãn khách hiểu,
# KHÔNG phải mã enum (nói "shipped" với khách là rò chi tiết kỹ thuật).
ORDER_STATUS_LABEL_VI: dict[OrderStatus, str] = {
    OrderStatus.PENDING: "chờ xác nhận",
    OrderStatus.PROCESSING: "đang chuẩn bị hàng",
    OrderStatus.SHIPPED: "đã bàn giao cho đơn vị vận chuyển",
    OrderStatus.DELIVERING: "đang trên đường giao",
    OrderStatus.DELIVERED: "đã giao thành công",
    OrderStatus.CANCELLED: "đã huỷ",
}


class TicketStatus(StrEnum):
    # Cấp ticket — thô hơn conversation (PRD §15 ghi chú)
    OPEN = "open"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"


class UserRole(StrEnum):
    # RBAC (slice 11 auth) — lưu dạng String ở cột user.role.
    ADMIN = "admin"
    CUSTOMER = "customer"


class AuditNode(StrEnum):
    # Giá trị cột `audit_log.node`: 4 node pipeline + 2 sự kiện BAO QUANH một lượt khách (observability).
    CUSTOMER = "customer"  # nhận tin khách
    INTENT = "intent"
    KNOWLEDGE = "knowledge"
    DECISION = "decision"
    RESPONSE = "response"
    DELIVERY = "delivery"  # kết cục giao (gửi thẳng / giữ nháp / chuyển người)


class TurnOutcome(StrEnum):
    """Kết cục GIAO của một lượt khách — nguồn của KPI %auto / %duyệt nháp / %chuyển người (PRD §9).

    KHÁC `AgentAction` (quyết định của Agent 3): một lượt `auto_reply` vẫn có thể bị GATE giữ nháp,
    nên phải đo kết cục THẬT chứ không đọc action.
    """

    SENT = "sent"  # gửi thẳng cho khách
    HELD_FOR_APPROVAL = "held_for_approval"  # gate giữ nháp → PENDING_APPROVAL
    QUEUED_FOR_HUMAN = "queued_for_human"  # handoff → IN_HUMAN_QUEUE
    ERROR = "error"  # pipeline lỗi → câu xin lỗi
