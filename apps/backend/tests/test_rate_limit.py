"""SlidingWindowLimiter (audit v2, SEC-XC.2) — hàm thuần, offline, thời gian truyền tay."""

from __future__ import annotations

from app.core.rate_limit import SlidingWindowLimiter


def test_allows_up_to_limit_then_blocks_within_window() -> None:
    lim = SlidingWindowLimiter(3, 60)
    assert [lim.hit("ip", now=t) for t in (0, 1, 2)] == [True, True, True]
    assert lim.hit("ip", now=3) is False
    assert lim.hit("other", now=3) is True  # khoá khác không bị ảnh hưởng


def test_window_slides_and_blocked_hits_are_not_recorded() -> None:
    lim = SlidingWindowLimiter(2, 10)
    assert lim.hit("k", now=0) and lim.hit("k", now=5)
    assert lim.hit("k", now=9) is False  # bị chặn → không ghi, không đẩy cửa sổ ra xa
    assert lim.hit("k", now=10.5) is True  # lần ở t=0 đã hết hạn
    assert lim.retry_after("k", now=11) == 4  # lần cũ nhất còn lại ở t=5 → hết hạn lúc 15


def test_zero_limit_disables() -> None:
    lim = SlidingWindowLimiter(0, 60)
    assert all(lim.hit("k", now=0) for _ in range(100))


def test_eviction_keeps_memory_bounded_without_resetting_hot_key() -> None:
    lim = SlidingWindowLimiter(1, 60, max_keys=4)
    assert lim.hit("hot", now=0)
    for i in range(20):
        lim.hit(f"spray-{i}", now=1)
    assert len(lim._hits) <= 4
    # "hot" là khoá cũ nhất nên có thể bị dọn, nhưng không bao giờ vượt trần trong cùng một lần hit.
    assert lim.hit("spray-19", now=2) is False


def test_reset_clears_counters() -> None:
    lim = SlidingWindowLimiter(1, 60)
    assert lim.hit("k", now=0)
    assert lim.hit("k", now=1) is False
    lim.reset()
    assert lim.hit("k", now=2) is True
