"""Giới hạn tần suất IN-PROCESS theo cửa sổ trượt (audit v2, SEC-XC.2).

Chặn brute-force đăng nhập, spam đăng ký và đốt tiền LLM qua /ws/chat. Cùng ràng buộc với hub (1 uvicorn
worker, PRD §10): bộ đếm sống trong tiến trình. Lên đa-worker thì thay phần lưu bằng Redis (INCR + EXPIRE)
sau cùng interface `hit()` — call-site không đổi.

`hit()` là hàm SYNC không có `await` nên nguyên tử trong event loop (không cần lock).
"""

from __future__ import annotations

import math
import time
from collections import deque
from itertools import islice


class SlidingWindowLimiter:
    """Cho phép tối đa `limit` lần trong `window_seconds` cho mỗi khoá. `limit <= 0` = tắt (luôn cho qua).

    `max_keys` chặn bộ nhớ phình khi bị dội bằng nhiều khoá (nhiều IP/email): đầy thì bỏ khoá đã hết hạn,
    vẫn đầy thì bỏ nửa số khoá CŨ NHẤT (theo thứ tự thêm vào) — không xoá sạch, để kẻ tấn công không tự
    reset được bộ đếm của khoá đang bị chặn.
    """

    def __init__(self, limit: int, window_seconds: float, *, max_keys: int = 10_000) -> None:
        self.limit = limit
        self.window = float(window_seconds)
        self.max_keys = max_keys
        self._hits: dict[str, deque[float]] = {}

    def hit(self, key: str, now: float | None = None) -> bool:
        """Ghi một lần cho `key`. Trả False (và KHÔNG ghi) nếu khoá đã chạm trần trong cửa sổ."""
        if self.limit <= 0:
            return True
        now = time.monotonic() if now is None else now
        cutoff = now - self.window
        q = self._hits.get(key)
        if q is None:
            if len(self._hits) >= self.max_keys:
                self._evict(cutoff)
            q = self._hits[key] = deque()
        while q and q[0] <= cutoff:
            q.popleft()
        if len(q) >= self.limit:
            return False
        q.append(now)
        return True

    def retry_after(self, key: str, now: float | None = None) -> int:
        """Số giây (làm tròn lên, ≥ 1) tới khi khoá được phép lại — cho header `Retry-After`."""
        q = self._hits.get(key)
        if not q:
            return 1
        now = time.monotonic() if now is None else now
        return max(1, math.ceil(q[0] + self.window - now))

    def reset(self) -> None:
        """Xoá mọi bộ đếm (test dùng giữa các ca)."""
        self._hits.clear()

    def _evict(self, cutoff: float) -> None:
        for k in [k for k, q in self._hits.items() if not q or q[-1] <= cutoff]:
            del self._hits[k]
        if len(self._hits) >= self.max_keys:
            for k in list(islice(self._hits, len(self._hits) // 2)):
                del self._hits[k]
