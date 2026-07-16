"""Agent 4 — Response Generator: grounded reply + phanh anti-hallucination. Offline (monkeypatch LLM)."""

from __future__ import annotations

import pytest

from app.agents.nodes import response as resp


class _FakeCompletions:
    def __init__(self, content: str) -> None:
        self._content = content

    async def create(self, *args: object, **kwargs: object) -> object:
        msg = type("Msg", (), {"content": self._content})
        choice = type("Choice", (), {"message": msg})
        return type("Resp", (), {"choices": [choice]})


class _FakeClient:
    def __init__(self, content: str) -> None:
        self.chat = type("Chat", (), {"completions": _FakeCompletions(content)})


async def test_generate_reply_grounded_uses_context(monkeypatch: pytest.MonkeyPatch) -> None:
    # Có rag_contexts + key -> gọi LLM (fake) -> trả nội dung grounded, KHÔNG cờ.
    monkeypatch.setattr(resp.settings, "llm_api_key", "sk-test")
    monkeypatch.setattr(resp, "get_openai", lambda: _FakeClient("Dạ, shop cho đổi trả trong vòng 7 ngày ạ."))
    r = await resp.generate_reply(
        "shop cho đổi trả trong bao lâu?",
        "refund",
        {},
        [{"text": "Khách được đổi trả trong vòng 7 ngày kể từ khi nhận hàng.", "source": "kb.pdf", "score": 0.8}],
    )
    assert "7 ngày" in r["reply"]
    assert r["uncertainty_flags"] == []


async def test_generate_reply_no_context_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    # rag_contexts rỗng -> KHÔNG gọi LLM (phanh), fallback + hallucination_risk.
    # Dùng SPY đếm lần gọi: assert calls==0 chạy NGOÀI generate_reply nên không bị `except` nuốt (nếu
    # phanh bị gỡ, get_openai bị gọi -> calls==1 -> test đỏ; AssertionError bên trong try KHÔNG đủ tin cậy).
    monkeypatch.setattr(resp.settings, "llm_api_key", "sk-test")
    calls = {"n": 0}

    def _spy() -> object:
        calls["n"] += 1
        raise AssertionError("KHÔNG được gọi LLM khi rag_contexts rỗng")

    monkeypatch.setattr(resp, "get_openai", _spy)
    r = await resp.generate_reply("thời tiết hôm nay thế nào?", "other", {}, [])
    assert calls["n"] == 0  # phanh phải chặn TRƯỚC get_openai
    assert r["reply"] == resp.FALLBACK_REPLY
    assert "hallucination_risk" in r["uncertainty_flags"]


async def test_generate_reply_no_key_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    # Thiếu key -> KHÔNG gọi LLM, fallback + hallucination_risk (dù có rag_contexts). Spy đếm như trên.
    monkeypatch.setattr(resp.settings, "llm_api_key", "")
    calls = {"n": 0}

    def _spy() -> object:
        calls["n"] += 1
        raise AssertionError("KHÔNG được gọi LLM khi thiếu key")

    monkeypatch.setattr(resp, "get_openai", _spy)
    r = await resp.generate_reply(
        "đổi trả bao lâu?", "refund", {}, [{"text": "7 ngày", "source": "kb.pdf", "score": 0.8}]
    )
    assert calls["n"] == 0  # phanh phải chặn TRƯỚC get_openai
    assert r["reply"] == resp.FALLBACK_REPLY
    assert "hallucination_risk" in r["uncertainty_flags"]


async def test_generate_reply_empty_llm_output_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    # LLM trả rỗng/toàn khoảng trắng -> fallback + hallucination_risk (nhánh `if not reply`).
    monkeypatch.setattr(resp.settings, "llm_api_key", "sk-test")
    monkeypatch.setattr(resp, "get_openai", lambda: _FakeClient("   "))  # strip() -> "" -> phanh
    r = await resp.generate_reply(
        "đổi trả bao lâu?", "refund", {}, [{"text": "7 ngày", "source": "kb.pdf", "score": 0.8}]
    )
    assert r["reply"] == resp.FALLBACK_REPLY
    assert "hallucination_risk" in r["uncertainty_flags"]


async def test_generate_reply_llm_error_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    # LLM lỗi -> degrade fallback (KHÔNG ném) -> pipeline không rớt.
    monkeypatch.setattr(resp.settings, "llm_api_key", "sk-test")

    class _Boom:
        class chat:
            class completions:
                @staticmethod
                async def create(*a: object, **k: object) -> object:
                    raise RuntimeError("openai down")

    monkeypatch.setattr(resp, "get_openai", lambda: _Boom())
    r = await resp.generate_reply(
        "đổi trả bao lâu?", "refund", {}, [{"text": "7 ngày", "source": "kb.pdf", "score": 0.8}]
    )
    assert r["reply"] == resp.FALLBACK_REPLY
    assert "hallucination_risk" in r["uncertainty_flags"]


async def test_response_node_is_single_speaker(monkeypatch: pytest.MonkeyPatch) -> None:
    # response_node là node DUY NHẤT ghi tin AI: messages[sender=ai] + result.reply + REPLIED.
    async def fake_gen(query, intent, entities, rag_contexts):  # type: ignore[no-untyped-def]
        return {"reply": "Dạ shop cho đổi trả trong 7 ngày ạ.", "uncertainty_flags": []}

    monkeypatch.setattr(resp, "generate_reply", fake_gen)
    out = await resp.response_node(
        {
            "input": "đổi trả bao lâu?",
            "intent": "refund",
            "entities": {},
            "rag_contexts": [{"text": "7 ngày", "source": "kb.pdf", "score": 0.8}],
            "action": "auto_reply",
            "confidence": 1.0,
        }
    )
    assert out["status"] == "REPLIED"
    assert out["messages"] == [{"sender": "ai", "content": "Dạ shop cho đổi trả trong 7 ngày ạ."}]
    assert out["draft_reply"] == "Dạ shop cho đổi trả trong 7 ngày ạ."
    assert out["result"]["branch"] == "response"
    assert out["result"]["action"] == "auto_reply"
    assert out["result"]["reply"] == "Dạ shop cho đổi trả trong 7 ngày ạ."
    assert out["uncertainty_flags"] == []


async def test_response_node_handoff_emits_notice() -> None:
    # SOLE-EGRESS: action=human_handoff -> Response Generator phát HANDOFF_NOTICE, IN_HUMAN_QUEUE, KHÔNG gọi LLM.
    out = await resp.response_node(
        {"action": "human_handoff", "escalation_reason": "blocking_flags=['no_relevant_knowledge']"}
    )
    assert out["status"] == "IN_HUMAN_QUEUE"
    assert out["result"]["branch"] == "human_handoff"
    assert out["result"]["reply"] == resp.HANDOFF_NOTICE
    assert out["messages"] == [{"sender": "ai", "content": resp.HANDOFF_NOTICE}]
    assert out["uncertainty_flags"] == []
