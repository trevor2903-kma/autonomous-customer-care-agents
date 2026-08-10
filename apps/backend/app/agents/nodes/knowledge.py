"""Node 2 — Knowledge Agent / RAG (PRD §7.2, §13). Truy hồi tri thức từ KHO TRI THỨC (chính sách/FAQ/sản phẩm).

- `retrieve_knowledge(query)` = hàm THUẦN (tái dùng): gọi `rag_service.search` (tầng service) → `rag_contexts`
  (text+source+score) + `retrieval_confidence` + cờ. Đây là VAI của Agent 2 (Agent 1 KHÔNG retrieval nữa).
- `resolve_order(...)`: với intent gắn-với-đơn, tra đơn của khách **SCOPED theo `customer_id`** →
  `order_context` (nguồn grounding thứ ba của Agent 4), hoặc `order_not_found` (báo lại cho khách), hoặc
  cờ `order_unresolved` (chuyển người). KB không thể trả lời về MỘT đơn cụ thể — trước đây RAG vận chuyển
  trúng nên lượt vẫn auto_reply mà chẳng có dữ liệu đơn nào.
- Cờ Agent 2: `no_relevant_knowledge` (không tri thức) / `low_retrieval_score` (điểm thấp) /
  `order_unresolved` (tra đơn HỎNG, hoặc lần thứ hai vẫn không ra trong cùng ca).
- Grounding (PRD §5 trụ cột 3, FR-PIPE-5): Agent 2 chỉ PHÁT cờ; Decision Engine (sau) đọc cờ → human_handoff
  nếu không có tri thức. Agent 2 KHÔNG tự quyết.
- Degrade AN TOÀN offline: thiếu key / Qdrant lỗi / collection trống / không hits → `rag_contexts=[]`,
  `retrieval_confidence=0.0`, `["no_relevant_knowledge"]` (KHÔNG network vô ích, KHÔNG ném lỗi) → `make test` offline.
"""

from __future__ import annotations

import uuid
from typing import Any

from ...core.config import settings
from ...core.logging import get_logger
from ...models.enums import ConversationStatus
from ...services import order_service, rag_service
from ..state import ConversationState
from ._entities import extract_entities_rule

log = get_logger("agent.knowledge")

# Lượt KHÔNG cần tri thức: xã giao không phát biểu sự thật nào → không có gì để "không grounded".
# Bỏ qua retrieval và KHÔNG phát cờ grounding (nếu phát, Agent 3 sẽ escalate một lời chào — lỗi cũ).
# Đây là KHOANH PHẠM VI grounding, KHÔNG phải nới lỏng: Agent 3 giữ nguyên, BLOCKING_FLAGS không đổi.
NO_RETRIEVAL_INTENTS: frozenset[str] = frozenset({"greeting"})

# Intent gắn với MỘT đơn cụ thể → tra đơn (song song RAG: dữ liệu đơn + chính sách bổ trợ nhau).
# `shipping` chỉ tra khi khách có đưa mã ("đơn 1234 ship tới đâu"); hỏi phí/thời gian ship chung thì KB đủ.
ORDER_INTENTS: frozenset[str] = frozenset({"order_status", "shipping"})


def _degrade(flags: list[str]) -> dict[str, Any]:
    return {"rag_contexts": [], "retrieval_confidence": 0.0, "uncertainty_flags": flags}


async def retrieve_knowledge(query: str, top_k: int = 4, intent: str | None = None) -> dict[str, Any]:
    """Truy hồi tri thức cho `query`, ưu tiên chunk cùng `intent`. Trả
    {rag_contexts, retrieval_confidence, uncertainty_flags}."""
    if intent in NO_RETRIEVAL_INTENTS:
        return _degrade([])  # rỗng nhưng KHÔNG cờ — Agent 4 trả câu chào mẫu (P5)

    # Thiếu key -> không embed/search được -> degrade (không network).
    if not settings.llm_api_key:
        return _degrade(["no_relevant_knowledge"])

    try:
        hits = await rag_service.search(query, top_k, intent=intent)
    except Exception as exc:  # noqa: BLE001 — Qdrant/embed lỗi / collection chưa có -> degrade, KHÔNG ném.
        log.warning("knowledge.search failed -> degrade no_relevant_knowledge: %s", exc)
        return _degrade(["no_relevant_knowledge"])

    if not hits:
        return _degrade(["no_relevant_knowledge"])

    # `type`/`title` để Agent 4 gắn nhãn loại tri thức (quy trình xử lý vs tra cứu) — plan §2.5/§3-P5.
    rag_contexts = [
        {
            "text": h.get("text"),
            "source": h.get("source"),
            "type": h.get("type"),
            "title": h.get("title"),
            "score": round(float(h["score"]), 4),
        }
        for h in hits
    ]
    retrieval_confidence = float(hits[0]["score"])
    flags: list[str] = []
    # Ngưỡng RIÊNG cho cosine (retrieval_threshold) — KHÔNG dùng confidence_threshold (thang intent LLM).
    if retrieval_confidence < settings.retrieval_threshold:
        flags.append("low_retrieval_score")

    return {
        "rag_contexts": rag_contexts,
        "retrieval_confidence": retrieval_confidence,
        "uncertainty_flags": flags,
    }


async def _failed_lookups_before(
    history: list[dict[str, Any]] | None, owner_id: uuid.UUID | None
) -> int:
    """Đếm số mã đơn KHÁC NHAU khách đã đưa TRONG CÙNG CA mà tra không ra (dựa trên `history`).

    Suy lại từ LỜI KHÁCH + sự thật DB, KHÔNG dò chữ trong câu trả lời của bot (đúng cái bug handoff cũ):
    lấy `order_id` bằng chính regex của Agent 1 rồi tra lại scoped. `history` chỉ chứa các lượt TRƯỚC
    (WS nạp history trước khi lưu tin hiện tại) nên không đếm nhầm lượt đang xử lý.
    """
    codes = {
        code
        for m in history or []
        if m.get("sender") == "customer"
        for code in [extract_entities_rule(str(m.get("content") or "")).get("order_id")]
        if code
    }
    if not codes:
        return 0
    try:
        results = [await order_service.lookup(code, owner_id) for code in codes]
    except Exception as exc:  # noqa: BLE001 — không đếm được → coi như chưa từng hỏi (BÁO, đừng escalate vội).
        log.warning("đếm lượt tra đơn hỏng trong lịch sử thất bại (bỏ qua): %s", exc)
        return 0
    return sum(1 for order in results if order is None)


async def resolve_order(
    intent: str | None,
    entities: dict[str, Any] | None,
    customer_id: str | None,
    history: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Tra đơn SCOPED cho intent gắn-với-đơn. Trả `{order_context, order_not_found, uncertainty_flags}`.

    Agent 2 chỉ PHÁT TÍN HIỆU, KHÔNG tự quyết (Agent 3 mới quyết):
    - có mã + tra THẤY (đúng chủ đơn) → `order_context` để Agent 4 báo trạng thái grounded.
    - có mã + KHÔNG thấy / không thuộc khách → `order_not_found` (**KHÔNG** phải cờ chặn): "không tìm thấy"
      LÀ một câu trả lời được — kết quả lookup chính là grounding, và phần lớn là khách gõ nhầm mã.
      Chỉ khi đây là lần **thứ hai** vẫn không ra trong CÙNG ca mới bật `order_unresolved` (chuyển người):
      hỏi lại một lần là hợp lý, hỏi lại mãi là đang làm khó khách.
    - KHÔNG mã → không tín hiệu gì: để Agent 4 hỏi mã đơn (auto_reply bình thường).

    Lưu ý đa lượt: `order_id` có thể do Agent 1 GIẢI THAM CHIẾU từ lịch sử ("đơn của mình" ngay sau lượt hỏi
    "đơn 716449") — khi đó lượt này vẫn TRA LẠI đơn, nên dữ liệu là MỚI chứ không phải chép lại lời cũ.
    Nhánh "không mã" vì vậy chỉ xảy ra khi thật sự không có đơn nào đang được nói tới.

    Degrade AN TOÀN: DB lỗi → `order_unresolved` (chuyển người), KHÔNG hạ xuống `order_not_found`: lookup
    HỎNG khác lookup TRẢ RỖNG — nói "không thấy đơn trong tài khoản của bạn" khi chưa tra được là nói sai.
    """
    empty = {"order_context": None, "order_not_found": None, "uncertainty_flags": []}
    if intent not in ORDER_INTENTS:
        return empty

    order_code = str((entities or {}).get("order_id") or "").strip()
    if not order_code:
        return empty

    try:
        owner_id = uuid.UUID(customer_id) if customer_id else None
    except (ValueError, TypeError):
        owner_id = None

    try:
        order = await order_service.lookup(order_code, owner_id)
    except Exception as exc:  # noqa: BLE001 — DB lỗi → không tra được → chuyển người (đừng bịa).
        log.warning("order lookup failed -> order_unresolved: %s", exc)
        return {"order_context": None, "order_not_found": None, "uncertainty_flags": ["order_unresolved"]}

    if order is not None:
        return {
            "order_context": order_service.to_context(order),
            "order_not_found": None,
            "uncertainty_flags": [],
        }

    # Không thấy: lần đầu → BÁO cho khách kiểm tra lại mã; đã hỏng ít nhất một lần trước đó → chuyển người.
    if await _failed_lookups_before(history, owner_id) >= 1:
        return {"order_context": None, "order_not_found": None, "uncertainty_flags": ["order_unresolved"]}
    return {"order_context": None, "order_not_found": order_code, "uncertainty_flags": []}


async def knowledge_node(state: ConversationState) -> dict[str, Any]:
    """Node graph: retrieve_knowledge trên input (ưu tiên intent của Agent 1) rồi ghi state + trace.
    Ghi `rag_contexts` (VAI Agent 2) + `retrieval_confidence`; `uncertainty_flags` tích luỹ (reducer add).

    Kèm TRA ĐƠN scoped (`resolve_order`) cho intent gắn-với-đơn: RAG (chính sách) và dữ liệu đơn bổ trợ
    nhau, nên chạy CẢ HAI rồi gộp cờ — không cái nào thay được cái nào."""
    intent = state.get("intent")
    result = await retrieve_knowledge(state.get("input", ""), intent=intent)
    order = await resolve_order(
        intent, state.get("entities"), state.get("customer_id"), state.get("history")
    )
    flags = result["uncertainty_flags"] + order["uncertainty_flags"]
    return {
        "status": ConversationStatus.RETRIEVING,
        "rag_contexts": result["rag_contexts"],
        "order_context": order["order_context"],
        "order_not_found": order["order_not_found"],
        "retrieval_confidence": result["retrieval_confidence"],
        "uncertainty_flags": flags,
        "trace": [
            {
                "node": "knowledge",
                "confidence": result["retrieval_confidence"],
                "branch": None,
                # `skipped` để audit thấy RÕ lượt xã giao không retrieve (khác với retrieve xong rỗng).
                "detail": {
                    "contexts": len(result["rag_contexts"]),
                    "intent": intent,
                    "skipped": intent in NO_RETRIEVAL_INTENTS,
                    # Tra đơn có chạy không / có ra đơn không — để audit truy được vì sao lượt bị escalate.
                    "order_found": bool(order["order_context"]),
                    "order_not_found": order["order_not_found"],
                },
            }
        ],
    }
