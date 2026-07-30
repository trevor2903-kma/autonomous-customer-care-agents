"""Langfuse tracing — observability cấp LLM (slice obs P3). **BỔ TRỢ, không phải nguồn báo cáo.**

Tab Báo cáo đọc `audit_log` (dữ liệu mình kiểm soát, có ở mọi môi trường). Langfuse thêm thứ audit_log
không có: prompt/completion đầy đủ, token, chi phí, độ trễ từng lời gọi LLM — xem trên dashboard riêng.

**Thiếu key → no-op HOÀN TOÀN**: không khởi tạo client, không network, không log ồn. Mọi hàm ở đây phải
an toàn khi gọi mà chưa cấu hình gì — pipeline không được biết Langfuse có tồn tại hay không.

Nối với audit_log qua `turn_id`: một lượt trên tab Báo cáo (`trc_…`) tra ngược được đúng trace Langfuse.
`conversation_id` → `session_id` để Langfuse gom các lượt cùng một ca.
"""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any

from .config import settings
from .logging import get_logger

log = get_logger("tracing")

# Ngữ cảnh lượt hiện tại — đặt ở lớp WS (nơi biết cả turn_id lẫn conversation_id), đọc ở đây.
# Dùng contextvar thay vì luồn tham số qua 4 node: mỗi lượt chạy trong chuỗi task riêng nên không lẫn.
_turn_ctx: ContextVar[dict[str, str] | None] = ContextVar("langfuse_turn_ctx", default=None)

_client: Any = None
_init_done = False


def enabled() -> bool:
    """Có đủ cặp key mới bật. Thiếu một trong hai = coi như tắt (nửa vời sẽ lỗi lúc gửi)."""
    return bool(settings.langfuse_public_key and settings.langfuse_secret_key)


def _get_client() -> Any:
    """Client dùng chung, khởi tạo LƯỜI. Lỗi khởi tạo → tắt vĩnh viễn, KHÔNG ném lên pipeline."""
    global _client, _init_done
    if _init_done:
        return _client
    _init_done = True
    if not enabled():
        return None
    try:
        from langfuse import Langfuse

        kwargs: dict[str, Any] = {
            "public_key": settings.langfuse_public_key,
            "secret_key": settings.langfuse_secret_key,
            "environment": settings.env,
        }
        if settings.langfuse_base_url:
            kwargs["host"] = settings.langfuse_base_url
        _client = Langfuse(**kwargs)
        log.info("Langfuse BẬT (host=%s)", settings.langfuse_base_url or "cloud mặc định")
    except Exception as exc:  # noqa: BLE001 — thiếu gói/sai cấu hình → chạy tiếp không tracing.
        log.warning("Langfuse không khởi tạo được (bỏ qua tracing): %s", exc)
        _client = None
    return _client


def set_turn(turn_id: str | None, conversation_id: str | None) -> None:
    """Gắn ngữ cảnh lượt cho các span sinh ra sau đó (gọi ở WS trước khi chạy pipeline)."""
    _turn_ctx.set({"turn_id": str(turn_id or ""), "conversation_id": str(conversation_id or "")})


def _ctx() -> dict[str, str]:
    return _turn_ctx.get() or {}


class _Span:
    """Bọc span Langfuse. `finish` an toàn kể cả khi span là None (nhánh no-op)."""

    __slots__ = ("_span",)

    def __init__(self, span: Any = None) -> None:
        self._span = span

    def finish(self, *, output: Any = None, usage: Any = None, metadata: dict | None = None) -> None:
        if self._span is None:
            return
        try:
            payload: dict[str, Any] = {}
            if output is not None:
                payload["output"] = output
            if metadata:
                payload["metadata"] = metadata
            if usage is not None:
                payload["usage_details"] = _usage_dict(usage)
            if payload:
                self._span.update(**payload)
        except Exception as exc:  # noqa: BLE001 — tracing hỏng KHÔNG được làm hỏng lượt trả lời.
            log.debug("langfuse span update lỗi (bỏ qua): %s", exc)


def _usage_dict(usage: Any) -> dict[str, int]:
    """Chuẩn hoá usage của OpenAI SDK → dict token cho Langfuse (để nó tính chi phí)."""
    if isinstance(usage, dict):
        return {k: int(v) for k, v in usage.items() if isinstance(v, (int, float))}
    out: dict[str, int] = {}
    for src, dst in (("prompt_tokens", "input"), ("completion_tokens", "output"), ("total_tokens", "total")):
        value = getattr(usage, src, None)
        if isinstance(value, int):
            out[dst] = value
    return out


def _observation(client: Any, as_type: str, **kwargs: Any):
    """Mở span/generation, ưu tiên API mới của Langfuse 3.x.

    `start_as_current_generation` đã deprecated (sẽ bỏ); `start_as_current_observation(as_type=...)` là
    bản thay thế. Thử bản mới trước, rơi về bản cũ để không khoá cứng vào một minor version.
    """
    new_api = getattr(client, "start_as_current_observation", None)
    if new_api is not None:
        return new_api(as_type=as_type, **kwargs)
    if as_type == "generation":
        return client.start_as_current_generation(**kwargs)
    return client.start_as_current_span(**kwargs)


def _apply_trace_ctx(client: Any, ctx: dict[str, str], meta: dict[str, Any]) -> None:
    """Gắn session/metadata lên TRACE bao ngoài (không chỉ span) để tra ngược được từ tab Báo cáo."""
    try:
        if ctx.get("conversation_id"):
            # session_id: Langfuse gom mọi lượt của cùng một ca vào một phiên.
            client.update_current_trace(session_id=ctx["conversation_id"], metadata=meta)
        elif meta:
            client.update_current_trace(metadata=meta)
    except Exception as exc:  # noqa: BLE001
        log.debug("langfuse update_current_trace lỗi (bỏ qua): %s", exc)


@contextmanager
def observe_turn(input_text: str | None = None):
    """Span GỐC của một lượt — mọi lời gọi LLM/embedding trong lượt nằm LỒNG bên trong.

    Không có nó thì mỗi lời gọi thành một trace rời (đo được: 1 lượt → 3 trace tách rời), không nhìn
    được tổng độ trễ/chi phí của MỘT lượt — thứ chính mà tab Báo cáo cần đối chiếu.
    """
    client = _get_client()
    if client is None:
        yield _Span()
        return

    ctx = _ctx()
    meta = {"turn_id": ctx["turn_id"]} if ctx.get("turn_id") else {}
    try:
        with _observation(client, "span", name="turn", input=input_text, metadata=meta) as span:
            _apply_trace_ctx(client, ctx, meta)
            try:
                client.update_current_trace(name="turn", input=input_text)
            except Exception as exc:  # noqa: BLE001
                log.debug("langfuse đặt tên trace lỗi (bỏ qua): %s", exc)
            yield _Span(span)
    except Exception as exc:  # noqa: BLE001 — không dựng được span → chạy tiếp KHÔNG tracing.
        log.debug("langfuse turn span lỗi (bỏ qua): %s", exc)
        yield _Span()


@contextmanager
def observe_llm(name: str, *, model: str | None = None, input: Any = None, metadata: dict | None = None):
    """Bọc MỘT lời gọi LLM/embedding thành generation trên Langfuse. No-op nếu tắt.

    Không nuốt lỗi của lời gọi bên trong (LLM lỗi vẫn ném lên cho caller degrade như cũ) — chỉ nuốt lỗi
    của chính việc tracing.
    """
    client = _get_client()
    if client is None:
        yield _Span()
        return

    ctx = _ctx()
    meta = {**(metadata or {}), **({"turn_id": ctx["turn_id"]} if ctx.get("turn_id") else {})}
    try:
        with _observation(client, "generation", name=name, model=model, input=input, metadata=meta) as gen:
            _apply_trace_ctx(client, ctx, meta)
            yield _Span(gen)
    except Exception as exc:  # noqa: BLE001 — không dựng được span → chạy tiếp KHÔNG tracing.
        log.debug("langfuse generation lỗi (bỏ qua): %s", exc)
        yield _Span()


def flush() -> None:
    """Đẩy nốt sự kiện còn trong hàng đợi (gọi lúc shutdown). An toàn khi tracing tắt."""
    if _client is None:
        return
    try:
        _client.flush()
    except Exception as exc:  # noqa: BLE001
        log.debug("langfuse flush lỗi (bỏ qua): %s", exc)


def trace_url() -> str | None:
    """URL dashboard Langfuse để FE link sang (None = chưa bật → FE ẩn nút)."""
    return settings.langfuse_base_url if enabled() else None
