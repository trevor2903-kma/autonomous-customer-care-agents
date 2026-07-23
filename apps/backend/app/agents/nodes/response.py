"""Node 4 — Response Generator (Agent 4). ĐIỂM PHÁT NGÔN DUY NHẤT tới khách. PRD §7.4, §14 FR-PIPE-5.

- `generate_reply(query, intent, entities, rag_contexts)` = hàm THUẦN (tái dùng): sinh câu trả lời CSKH
  tiếng Việt GROUNDED từ **`facts.md` (luôn-bật) + `rag_contexts`**. Phanh anti-hallucination (PRD §5 trụ cột 3,
  §14 FR-PIPE-5): `rag_contexts` rỗng **hoặc** thiếu `settings.llm_api_key` → KHÔNG gọi LLM bịa → câu fallback
  lịch sự + cờ `hallucination_risk`. (Phanh này TẠM gánh vai an toàn thay Decision Engine/Agent 3 — ROADMAP 05.)
- **Grounding cả HÀNH ĐỘNG**: chỉ được hứa việc hệ thống LÀM ĐƯỢC. Chưa tra được đơn / chưa hoàn được tiền →
  nói sẽ chuyển nhân viên, KHÔNG nói "đã hoàn tiền/đã kiểm tra đơn cho bạn".
- `greeting` = lượt xã giao, KHÔNG phát biểu sự thật nào → câu chào mẫu, KHÔNG gọi LLM, KHÔNG cờ. Nhánh này
  chạy **TRƯỚC** phanh "rag_contexts rỗng → FALLBACK" (Agent 2 đã cố ý không retrieve — plan §3-P4/P5).
- `response_node` là **NODE DUY NHẤT** được ghi tin nhắn AI vào `state["messages"]` (PRD §7.4).
- Degrade AN TOÀN: thiếu key / LLM lỗi / LLM trả rỗng → fallback (KHÔNG ném lỗi) → pipeline không rớt,
  `make test` chạy offline.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import frontmatter

from ...core.config import settings
from ...core.embeddings import get_openai
from ...core.logging import get_logger
from ...models.enums import AgentAction, ConversationStatus
from ..state import ConversationState
from ._history import format_history

log = get_logger("agent.response")

# Câu fallback lịch sự khi KHÔNG đủ tri thức để trả lời chắc chắn (KHÔNG bịa — PRD §14 FR-PIPE-5).
FALLBACK_REPLY = (
    "Dạ câu hỏi này em xin phép chuyển tới nhân viên hỗ trợ để được giải đáp chính xác hơn ạ. "
    "Mong anh/chị thông cảm và chờ trong giây lát ạ."
)

# Thông báo khi Agent 3 quyết human_handoff — Response Generator phát (KHÔNG gọi LLM). Node human_handoff
# đầy đủ (EscalationCard + admin queue) = slice 08b.
HANDOFF_NOTICE = "Yêu cầu của bạn đã được chuyển tới nhân viên hỗ trợ."

# Lượt xã giao: câu mẫu cố định, KHÔNG gọi LLM (không có gì để grounded, cũng không có gì để bịa).
GREETING_REPLY = (
    "Dạ em chào anh/chị ạ! Em là trợ lý của shop. "
    "Anh/chị cần em hỗ trợ gì về sản phẩm, size, đơn hàng hay chính sách đổi/trả ạ?"
)
# Intent trả câu mẫu, KHÔNG qua LLM — khớp `knowledge.NO_RETRIEVAL_INTENTS` (Agent 2 đã bỏ retrieval).
CANNED_INTENTS: dict[str, str] = {"greeting": GREETING_REPLY}

# facts.md = sự thật lõi cửa hàng, LUÔN nạp vào prompt (plan §2.6). Không vào Qdrant (ingest bỏ qua).
_FACTS_PATH = Path(__file__).resolve().parents[3] / "knowledge" / "facts.md"
_facts_cache: str | None = None

# Nhãn hiển thị theo `type` của chunk — cho LLM biết đoạn nào là QUY TRÌNH phải bám từng bước, đoạn nào
# chỉ là thông tin tra cứu.
_TYPE_LABEL = {
    "case": "Quy trình xử lý",
    "reference": "Tra cứu",
    "faq": "Hỏi đáp",
    "promotion": "Khuyến mãi",
}


def load_facts() -> str:
    """Đọc `knowledge/facts.md` MỘT LẦN rồi cache (đọc lúc khởi động qua `warmup_facts`)."""
    global _facts_cache
    if _facts_cache is None:
        try:
            _facts_cache = frontmatter.load(_FACTS_PATH).content.strip()
        except OSError as exc:  # thiếu file → chạy không facts, đừng làm rớt app
            log.warning("facts.md không đọc được (%s) — bỏ qua khối SỰ THẬT CỬA HÀNG", exc)
            _facts_cache = ""
    return _facts_cache


def _system_prompt() -> str:
    facts = load_facts()
    facts_block = f"\n\nSỰ THẬT CỬA HÀNG (luôn đúng, được phép dùng để trả lời):\n{facts}" if facts else ""
    return (
        "Bạn là nhân viên chăm sóc khách hàng của một shop quần áo. "
        "Soạn câu trả lời tiếng Việt thân thiện, lịch sự, NGẮN GỌN cho khách. "
        "CHỈ dựa trên SỰ THẬT CỬA HÀNG và các ĐOẠN TRI THỨC được cung cấp — TUYỆT ĐỐI KHÔNG bịa thông tin "
        "ngoài các nguồn đó. Nếu không đủ để trả lời chắc chắn, hãy nói sẽ chuyển câu hỏi tới nhân viên hỗ "
        "trợ, KHÔNG được bịa. Không nhắc tới 'đoạn tri thức'/'context' trong câu trả lời.\n"
        "BÁM QUY TRÌNH: nếu có đoạn '[Quy trình xử lý]', làm theo ĐÚNG THỨ TỰ các bước — hỏi thông tin còn "
        "thiếu ở bước hiện tại (vd mã đơn) TRƯỚC, mỗi lượt chỉ hỏi 1–2 điều, KHÔNG nhảy tới kết luận.\n"
        "GIỚI HẠN HÀNH ĐỘNG: bạn chỉ TRẢ LỜI, không thao tác được trên hệ thống. TUYỆT ĐỐI KHÔNG nói đã tra "
        "đơn, đã kiểm tra vận đơn, đã hoàn tiền, đã đổi hàng hay đã tạo yêu cầu. Việc cần thao tác thật → nói "
        "sẽ chuyển nhân viên xử lý. KHÔNG hứa thời hạn/số tiền không có trong nguồn."
        f"{facts_block}"
    )


def _context_block(rag_contexts: list[dict[str, Any]]) -> str:
    """Ghép các đoạn tri thức thành context, gắn NHÃN LOẠI để phân biệt quy trình với tra cứu."""
    parts: list[str] = []
    for i, c in enumerate(rag_contexts, 1):
        text = (c.get("text") or "").strip()
        source = c.get("source") or "?"
        label = _TYPE_LABEL.get(c.get("type") or "", "Tri thức")
        title = c.get("title")
        head = f"[Đoạn {i} · {label}" + (f" · {title}" if title else "") + f" · nguồn: {source}]"
        parts.append(f"{head}\n{text}")
    return "\n\n".join(parts)


async def generate_reply(
    query: str,
    intent: str | None,
    entities: dict[str, Any] | None,
    rag_contexts: list[dict[str, Any]] | None,
    history: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Sinh câu trả lời GROUNDED từ facts.md + `rag_contexts`. Trả `{reply, uncertainty_flags}`. `history`
    (đầu vào chỉ-đọc) giúp hiểu tham chiếu đa lượt — NHƯNG nội dung vẫn grounded từ nguồn được cấp,
    KHÔNG từ lịch sử.

    Phanh: rag_contexts rỗng HOẶC thiếu llm_api_key → fallback + `hallucination_risk` (KHÔNG gọi LLM bịa)."""
    # TRƯỚC phanh: lượt xã giao KHÔNG có (và không cần) rag_contexts — nếu để rơi xuống phanh thì khách
    # chào lại nhận câu "xin chuyển nhân viên hỗ trợ". Đi cặp với `knowledge.NO_RETRIEVAL_INTENTS` (P4).
    canned = CANNED_INTENTS.get(intent or "")
    if canned:
        return {"reply": canned, "uncertainty_flags": []}

    contexts = rag_contexts or []
    if not contexts or not settings.llm_api_key:
        # KHÔNG có tri thức để bám (hoặc không thể gọi LLM) → KHÔNG bịa (PRD §14 FR-PIPE-5).
        return {"reply": FALLBACK_REPLY, "uncertainty_flags": ["hallucination_risk"]}

    user_msg = (
        f"{format_history(history, settings.history_window)}"
        f"Câu hỏi của khách: {query!r}\n"
        f"(intent: {intent}; entities: {entities or {}})\n\n"
        f"ĐOẠN TRI THỨC:\n{_context_block(contexts)}"
    )
    try:
        resp = await get_openai().chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": _system_prompt()},
                {"role": "user", "content": user_msg},
            ],
            temperature=0,
        )
        reply = (resp.choices[0].message.content or "").strip()
    except Exception as exc:  # noqa: BLE001 — LLM lỗi → fallback (đừng ném, đừng bịa) → pipeline không rớt.
        log.warning("response.llm failed -> fallback: %s", exc)
        return {"reply": FALLBACK_REPLY, "uncertainty_flags": ["hallucination_risk"]}

    if not reply:  # LLM trả rỗng → fallback an toàn.
        return {"reply": FALLBACK_REPLY, "uncertainty_flags": ["hallucination_risk"]}
    return {"reply": reply, "uncertainty_flags": []}


async def response_node(state: ConversationState) -> dict[str, Any]:
    """Node 4 — SOLE-EGRESS: branch theo `state["action"]` (Agent 3). NODE DUY NHẤT ghi tin AI (PRD §7.4).

    - `human_handoff` → phát `HANDOFF_NOTICE` (KHÔNG gọi LLM) → status IN_HUMAN_QUEUE.
    - `auto_reply` → `generate_reply` grounded → status REPLIED.
    Cả hai đều set `result.reply` → WS/khách nhận qua CÙNG một đường (không phải sửa WS).
    """
    action = state.get("action")
    if action == AgentAction.HUMAN_HANDOFF:
        reply = HANDOFF_NOTICE
        status = ConversationStatus.IN_HUMAN_QUEUE
        branch = "human_handoff"
        flags: list[str] = []
    else:
        result = await generate_reply(
            query=state.get("input", ""),
            intent=state.get("intent"),
            entities=state.get("entities") or {},
            rag_contexts=state.get("rag_contexts") or [],
            history=state.get("history"),
        )
        reply = result["reply"]
        status = ConversationStatus.REPLIED
        branch = "response"
        flags = result["uncertainty_flags"]

    return {
        "status": status,
        "draft_reply": reply,
        "messages": [{"sender": "ai", "content": reply}],
        "result": {
            "branch": branch,
            "action": str(action) if action else None,
            "reply": reply,
            "escalation_reason": state.get("escalation_reason"),
        },
        # Reducer `add`: CHỈ cờ MỚI của node này (hallucination_risk khi auto_reply phải fallback).
        "uncertainty_flags": flags,
        "trace": [
            {
                "node": "response",
                "confidence": state.get("confidence"),
                "branch": branch,
                "detail": {"action": str(action) if action else None, "flags": flags},
            }
        ],
    }
