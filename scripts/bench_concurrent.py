"""Tạo tải ĐỒNG THỜI trên `/ws/chat` để đo độ trễ lượt khách ở nhiều mức hội thoại song song.

Mục đích: lấy số liệu THẬT cho mục 3.5.6 của báo cáo (benchmark đồng thời — Bảng 3.18 và Bảng 3.19).
Script mở N kết nối WebSocket của N khách KHÁC NHAU, cho cả N gửi một tin nhắn cùng lúc, rồi đo thời gian
tới khung kết thúc lượt (`reply` / `handoff` / `pending` / `status`).

**CON SỐ CHÍNH THỨC của báo cáo KHÔNG phải số script này in ra.** Số chính thức là độ trễ end-to-end PHÍA
SERVER, đọc ở dòng `delivery` của bảng `audit_log` (cột `duration_ms`) hoặc ở tab **Báo cáo**
(`/admin/reports`) — đó là con số đối chiếu NFR-1. Số script in ra là số PHÍA CLIENT: có thêm thời gian
thiết lập/đi-về trên mạng và thời gian event loop của chính script, nên luôn lớn hơn hoặc bằng số server;
dùng nó để đối chiếu và để biết mức tải nào bắt đầu có lượt lỗi/hết thời gian chờ.

Chạy (cần backend đang chạy — `make dev-backend`):

    uv run --python 3.12 --with websockets --with httpx scripts/bench_concurrent.py \
           --concurrency 1,10,25,50,100

hoặc:  make bench                (mức mặc định)
       make bench ARGS="--concurrency 1,10,25,50"

Câu hỏi RIÊNG cho từng tài khoản (vd lượt tra đơn: mỗi khách hỏi đúng mã đơn của mình — mã đơn là duy nhất toàn
hệ thống nên không thể dùng một câu chung): `--message-map map.json`, với `map.json` là
`{"<email tài khoản benchmark>": "<câu hỏi>"}`; tài khoản không có trong tệp dùng `--message`.

LƯU Ý trước khi đo:
- Mỗi lượt tốn hạn mức LLM thật (2 lời gọi LLM + 1 embedding). N=100 là 100 lượt.
- Bộ giới hạn tần suất của backend tính theo IP cho `/auth/register` + `/auth/login`
  (`REGISTER_RATE_PER_IP`, `LOGIN_RATE_PER_IP`). Tạo hàng chục tài khoản benchmark từ một máy sẽ bị 429;
  đặt hai biến đó `=0` trong `.env` (tắt) rồi khởi động lại backend trước khi đo, và bật lại sau khi đo.
- Lượt nào kết thúc ở `IN_HUMAN_QUEUE` / `HUMAN_HANDLING` / `PENDING_APPROVAL` (chuyển người, hoặc gate giữ
  nháp) thì ca của tài khoản đó rơi vào status-gate: từ lượt SAU, AI không chạy nữa và khách KHÔNG nhận khung
  kết cục nào, nên mức tải sau chỉ đo được "timeout" trên tài khoản đó. Script tự LOẠI các tài khoản như vậy
  trước mỗi mức (in số bị loại); muốn đo đủ N thì dùng `--email-prefix` MỚI cho mỗi lần đo, hoặc để nhân viên
  đóng các ca đang giữ trước khi đo lại.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from urllib.parse import urlsplit, urlunsplit

import httpx
import websockets

# Khung server trả về ĐÁNH DẤU LƯỢT ĐÃ XONG (contract v2 — xem `app/api/ws/chat.py`):
# `reply` = trả lời tự động · `handoff` = ca vào hàng đợi người · `pending` = gate giữ nháp chờ duyệt ·
# `status` = lượt bị bỏ vì trạng thái ca đổi (admin tiếp quản/đóng giữa lượt). Bốn khung này đều là KẾT CỤC
# của lượt nên đều tính là "đo được".
TERMINAL_FRAMES = frozenset({"reply", "handoff", "pending", "status"})

# Khung trung gian — BỎ QUA, không phải kết cục: `ack` (biên nhận tin), `typing` (báo đang xử lý),
# `pong` (heartbeat), `system` (chào lúc nối xong).
IGNORED_FRAMES = frozenset({"ack", "typing", "pong", "system"})

# Trạng thái ca "đang có người xử lý" (PRD §15) — copy của `chat.HUMAN_HANDLED_STATUSES`: với các trạng thái này
# status-gate của backend KHÔNG cho AI chạy, tin khách chỉ được định tuyến sang admin nên socket của khách không
# nhận khung kết cục nào (lượt chỉ đứng chờ tới hết `--timeout`). Tài khoản benchmark đã rơi vào đây một lần thì
# hỏng cho MỌI mức tải sau → loại ra trước khi đo thay vì đếm thành timeout.
HUMAN_HANDLED_STATUSES = frozenset({"IN_HUMAN_QUEUE", "HUMAN_HANDLING", "PENDING_APPROVAL"})

# Mốc NFR-1 (PRD): độ trễ một lượt ≤ 5 giây. Trùng `settings.nfr_latency_ms` của backend — để hằng số tại đây
# vì script chạy độc lập, KHÔNG import `app`.
NFR_LATENCY_MS = 5000

# Câu hỏi chính sách mặc định: đi hết pipeline 4 tác tử (intent → knowledge → decision → response) và KHÔNG
# cần mã đơn nên không rơi vào lượt clarification — mọi lượt đo có cùng hình dạng công việc.
# Phải là MỘT ý định: câu hỏi gộp hai việc ("phí giao hàng bao nhiêu VÀ bao lâu nhận được") bị Agent 1 gắn cờ chặn
# `multi_intent` ở 36–46% lượt (đo 18/09/2026, N=10–100) → chuyển người, không gọi mô hình sinh — tức là trộn
# hai hình dạng công việc vào cùng một phép đo.
DEFAULT_MESSAGE = "Phí giao hàng của shop là bao nhiêu vậy?"


# ── Kiểu dữ liệu ─────────────────────────────────────────────────────────────
@dataclass
class TurnResult:
    """Kết quả MỘT lượt: đo được thì `latency_ms` có giá trị, ngược lại `error` nói vì sao."""

    ok: bool
    latency_ms: float | None = None
    error: str | None = None


@dataclass
class LevelStats:
    """Thống kê của MỘT mức tải (phía client)."""

    concurrency: int
    measured: int  # số lượt đo được (nhận khung kết thúc)
    failed: int  # số lượt lỗi hoặc hết thời gian chờ
    avg_ms: float | None
    p50_ms: float | None
    p95_ms: float | None
    p99_ms: float | None
    max_ms: float | None
    within_nfr_pct: float | None
    errors: dict[str, int] = field(default_factory=dict)


# ── Phân vị ──────────────────────────────────────────────────────────────────
def percentile(values: list[float], pct: float) -> float | None:
    """Phân vị theo NEAREST-RANK (KHÔNG nội suy).

    Cố ý dùng ĐÚNG cách tính của `report_service.percentile` ở backend (`rank = ceil(pct * n / 100)`, kẹp vào
    [1, n], lấy phần tử thứ `rank`): số script in ra và số tab Báo cáo in ra phải so sánh được với nhau, mà
    với n nhỏ thì nội suy tạo ra giá trị không tồn tại trong tập đo.
    """
    if not values:
        return None
    ordered = sorted(values)
    rank = max(1, min(len(ordered), int(-(-pct * len(ordered) // 100))))  # ceil
    return ordered[rank - 1]


def _summarize(concurrency: int, results: list[TurnResult]) -> LevelStats:
    latencies = [r.latency_ms for r in results if r.ok and r.latency_ms is not None]
    errors: dict[str, int] = {}
    for r in results:
        if not r.ok:
            errors[r.error or "(không rõ)"] = errors.get(r.error or "(không rõ)", 0) + 1
    within = (
        round(100.0 * sum(1 for ms in latencies if ms <= NFR_LATENCY_MS) / len(latencies), 1)
        if latencies
        else None
    )
    return LevelStats(
        concurrency=concurrency,
        measured=len(latencies),
        failed=len(results) - len(latencies),
        avg_ms=(sum(latencies) / len(latencies)) if latencies else None,
        p50_ms=percentile(latencies, 50),
        p95_ms=percentile(latencies, 95),
        p99_ms=percentile(latencies, 99),
        max_ms=max(latencies) if latencies else None,
        within_nfr_pct=within,
        errors=errors,
    )


# ── Tài khoản benchmark ──────────────────────────────────────────────────────
def _email(prefix: str, index: int) -> str:
    return f"{prefix}{index:04d}@bench.local"


_RATE_RETRIES = 3
_RATE_WAIT_CAP_SECONDS = 60


async def _get_token(
    client: httpx.AsyncClient, base_url: str, email: str, password: str
) -> tuple[str | None, str | None]:
    """Bảo đảm có tài khoản khách `email` và trả access token.

    Đăng ký trước (`POST /api/auth/register`); email đã tồn tại (409 — lần đo thứ hai trở đi) thì đăng nhập
    (`POST /api/auth/login`). Gặp 429 thì chờ theo header `Retry-After` rồi thử lại, tối đa `_RATE_RETRIES`
    lần: bộ giới hạn theo IP của backend chặn cả register lẫn login.
    """
    for attempt in range(_RATE_RETRIES + 1):
        try:
            resp = await client.post(
                f"{base_url}/api/auth/register",
                json={"email": email, "password": password, "display_name": "bench"},
            )
            if resp.status_code == 409:  # đã có tài khoản → đăng nhập
                resp = await client.post(
                    f"{base_url}/api/auth/login", json={"email": email, "password": password}
                )
            if resp.status_code == 429:
                if attempt >= _RATE_RETRIES:
                    return None, "rate_limited (đặt REGISTER_RATE_PER_IP=0 và LOGIN_RATE_PER_IP=0 trong .env)"
                wait = min(_RATE_WAIT_CAP_SECONDS, max(1, int(resp.headers.get("Retry-After", "5") or 5)))
                print(f"    429 khi lấy token {email} — chờ {wait}s rồi thử lại")
                await asyncio.sleep(wait)
                continue
            if resp.status_code >= 400:
                return None, f"HTTP {resp.status_code}"
            token = resp.json().get("access_token")
            return (token, None) if token else (None, "phản hồi thiếu access_token")
        except Exception as exc:  # noqa: BLE001 — công cụ đo: gom lỗi để đếm, không làm sập lượt đo
            return None, f"{type(exc).__name__}: {exc}"
    return None, "rate_limited"


async def _ensure_tokens(
    base_url: str, prefix: str, password: str, count: int, cache: dict[str, str], timeout: float
) -> list[tuple[str, str]]:
    """Trả `(email, token)` của `count` tài khoản benchmark ĐẦU TIÊN (dùng lại token đã lấy ở mức tải trước).

    Vì sao phải N tài khoản RIÊNG BIỆT, không dùng chung một tài khoản: backend giới hạn tần suất tin nhắn
    `/ws/chat` THEO KHÁCH (`chat_rate_per_customer`, mặc định 20 tin mỗi 60 giây, cộng dồn mọi tab) và tuần
    tự hoá lượt THEO KHÁCH (một `asyncio.Lock` cho mỗi `customer_id` — hai lượt của cùng khách chạy nối
    tiếp, không song song). Dùng chung một tài khoản thì phép đo sẽ đo chính bộ giới hạn tần suất và hàng đợi
    của khoá đó, chứ không đo khả năng xử lý đồng thời của hệ thống.
    """
    tokens: list[tuple[str, str]] = []
    async with httpx.AsyncClient(timeout=timeout) as client:
        for i in range(1, count + 1):
            email = _email(prefix, i)
            cached = cache.get(email)
            if cached is not None:
                tokens.append((email, cached))
                continue
            token, err = await _get_token(client, base_url, email, password)
            if token is None:
                print(f"    KHÔNG lấy được token cho {email}: {err}")
                if err is not None and err.startswith("rate_limited"):
                    # Bộ giới hạn theo IP còn bật: mọi tài khoản còn lại cũng sẽ 429 sau khi chờ hết số lần thử
                    # → dừng ngay thay vì treo hàng giờ.
                    print("    DỪNG tạo tài khoản: tắt giới hạn theo IP rồi đo lại.")
                    break
                continue
            cache[email] = token
            tokens.append((email, token))
    return tokens


async def _drop_human_handled(
    base_url: str, tokens: list[tuple[str, str]], timeout: float
) -> tuple[list[tuple[str, str]], int]:
    """Bỏ các tài khoản mà ca đang mở ở trạng thái do nhân viên xử lý (xem `HUMAN_HANDLED_STATUSES`).

    Trạng thái đọc qua `GET /api/me/thread` (`active_status`) với header Bearer. Không đọc được (HTTP lỗi / mạng
    lỗi) → GIỮ tài khoản: phép đo không nên bị bớt tải vì một lần đọc phụ trợ thất bại.
    """
    usable: list[tuple[str, str]] = []
    dropped = 0
    async with httpx.AsyncClient(timeout=timeout) as client:
        for email, token in tokens:
            status: str | None = None
            try:
                resp = await client.get(
                    f"{base_url}/api/me/thread", headers={"Authorization": f"Bearer {token}"}
                )
                if resp.status_code < 400:
                    status = resp.json().get("active_status")
            except Exception as exc:  # noqa: BLE001 — bước phụ trợ: lỗi thì coi như không biết trạng thái
                print(f"    không đọc được trạng thái ca: {type(exc).__name__}: {exc}")
            if status in HUMAN_HANDLED_STATUSES:
                dropped += 1
                continue
            usable.append((email, token))
    return usable, dropped


# ── Một lượt qua WebSocket ───────────────────────────────────────────────────
def _ws_url(base_url: str, token: str) -> str:
    """`http(s)://host` → `ws(s)://host/ws/chat?token=…`.

    Token truyền qua query-param: backend đọc `access_token` từ cookie httpOnly TRƯỚC, rồi mới tới
    `?token=` (`app/api/ws/auth.py`). Script không phải trình duyệt nên không có cookie jar → dùng nhánh
    query-param mà backend hỗ trợ sẵn.
    """
    parts = urlsplit(base_url)
    scheme = "wss" if parts.scheme == "https" else "ws"
    return urlunsplit((scheme, parts.netloc, "/ws/chat", f"token={token}", ""))


async def _run_turn(
    url: str, message: str, timeout: float, ready: asyncio.Event, start: asyncio.Event
) -> TurnResult:
    """Nối WS → báo `ready` → chờ `start` → gửi MỘT tin → chờ khung kết thúc lượt.

    Hai cờ `ready`/`start` để cả N kết nối được thiết lập TRƯỚC, rồi mới cùng gửi: nếu vừa nối vừa gửi thì
    thời gian handshake của kết nối thứ N bị cộng vào độ trễ, phép đo không còn là "N lượt đồng thời".
    Mọi lỗi của một kết nối chỉ làm hỏng LƯỢT ĐÓ (trả `TurnResult(ok=False)`), không làm sập mức đo.
    """
    try:
        async with websockets.connect(url, open_timeout=timeout, close_timeout=5) as ws:
            ready.set()
            await start.wait()
            payload = json.dumps(
                {"type": "message", "content": message, "client_msg_id": uuid.uuid4().hex}
            )
            sent = time.perf_counter()
            await ws.send(payload)
            deadline = sent + timeout
            while True:
                remaining = deadline - time.perf_counter()
                if remaining <= 0:
                    return TurnResult(False, error="timeout")
                raw = await asyncio.wait_for(ws.recv(), timeout=remaining)
                elapsed_ms = (time.perf_counter() - sent) * 1000.0
                try:
                    frame = json.loads(raw)
                except ValueError:
                    return TurnResult(False, error="khung không phải JSON")
                kind = frame.get("type") if isinstance(frame, dict) else None
                if kind in TERMINAL_FRAMES:
                    return TurnResult(True, latency_ms=elapsed_ms)
                if kind == "error":
                    return TurnResult(False, error=f"error:{frame.get('code') or '(không rõ)'}")
                if kind not in IGNORED_FRAMES:
                    return TurnResult(False, error=f"khung lạ: {kind!r}")
    except asyncio.TimeoutError:
        return TurnResult(False, error="timeout")
    except asyncio.CancelledError:
        raise
    except Exception as exc:  # noqa: BLE001 — công cụ đo: đếm lỗi thay vì dừng cả phép đo
        return TurnResult(False, error=f"{type(exc).__name__}: {exc}")


async def _run_level(
    base_url: str,
    tokens: list[tuple[str, str]],
    message: str,
    timeout: float,
    message_map: dict[str, str] | None = None,
) -> list[TurnResult]:
    """Chạy một mức tải: mỗi tài khoản một kết nối, tất cả gửi cùng lúc (câu riêng lấy từ `message_map`)."""
    start = asyncio.Event()
    readies = [asyncio.Event() for _ in tokens]
    tasks = [
        asyncio.create_task(
            _run_turn(_ws_url(base_url, t), (message_map or {}).get(email, message), timeout, r, start)
        )
        for (email, t), r in zip(tokens, readies)
    ]
    # Chờ mọi kết nối sẵn sàng (kết nối lỗi thì task của nó kết thúc sớm và `ready` không bao giờ set →
    # chờ có hạn, hết hạn thì mở cổng với những kết nối đã sẵn sàng).
    try:
        await asyncio.wait_for(
            asyncio.gather(*(r.wait() for r in readies)), timeout=timeout
        )
    except asyncio.TimeoutError:
        print("    (một số kết nối chưa sẵn sàng sau thời gian chờ — vẫn bắt đầu với số còn lại)")
    start.set()
    return list(await asyncio.gather(*tasks))


# ── In kết quả ───────────────────────────────────────────────────────────────
def _ms(value: float | None) -> str:
    """Số đo -> chuỗi; CHƯA đo được thì bỏ trống (không bao giờ điền số thay)."""
    return "" if value is None else f"{value:.0f}"


def _pct(value: float | None) -> str:
    return "" if value is None else f"{value:.1f}%"


def _print_level(stats: LevelStats) -> None:
    print(
        f"  N={stats.concurrency:<4} do_duoc={stats.measured:<4} loi={stats.failed:<4} "
        f"Avg={_ms(stats.avg_ms):>6} p50={_ms(stats.p50_ms):>6} p95={_ms(stats.p95_ms):>6} "
        f"p99={_ms(stats.p99_ms):>6} Max={_ms(stats.max_ms):>6} (ms, phía client)"
    )
    for reason, n in sorted(stats.errors.items(), key=lambda kv: -kv[1]):
        print(f"      lỗi ×{n}: {reason}")


def _print_markdown(all_stats: list[LevelStats]) -> None:
    """Bảng markdown khớp ĐÚNG các cột Bảng 3.18 của báo cáo — dán thẳng vào mục 3.5.6.

    Cột "Tổng số lượt" = số lượt ĐO ĐƯỢC (có khung kết thúc), cũng là mẫu để tính Avg/phân vị; lượt lỗi hoặc
    hết thời gian chờ được liệt kê riêng bên dưới bảng, không trộn vào số liệu độ trễ.
    """
    print("\n--- Bảng 3.18 (số phía CLIENT — đối chiếu; số chính thức lấy ở dòng `delivery`) ---\n")
    print(
        "| Số hội thoại đồng thời | Tổng số lượt | Avg | p50 | p95 | p99 | Max | Tỉ lệ đạt NFR-1 |"
    )
    print("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for s in all_stats:
        print(
            f"| {s.concurrency} | {s.measured} | {_ms(s.avg_ms)} | {_ms(s.p50_ms)} | "
            f"{_ms(s.p95_ms)} | {_ms(s.p99_ms)} | {_ms(s.max_ms)} | {_pct(s.within_nfr_pct)} |"
        )
    print(f"\n(Avg/p50/p95/p99/Max đơn vị ms. Tỉ lệ đạt NFR-1 tính theo mốc {NFR_LATENCY_MS} ms.)")
    failing = [s for s in all_stats if s.failed]
    if failing:
        print("Lượt lỗi / hết thời gian chờ: " + " · ".join(f"N={s.concurrency}: {s.failed}" for s in failing))
        print(
            "Các lượt này KHÔNG được tính vào Avg/phân vị/tỉ lệ đạt NFR-1 (không có số đo) — khi báo cáo phải "
            "nêu kèm số lượt lỗi, đừng chỉ nêu tỉ lệ đạt."
        )


def _print_server_side_hint(started_at: datetime, finished_at: datetime) -> None:
    fmt = "%Y-%m-%d %H:%M:%S+00"
    print(
        "\nSỐ CHÍNH THỨC cho báo cáo lấy PHÍA SERVER, không phải bảng trên:\n"
        "  - mở tab Báo cáo (`/admin/reports`) và chọn khoảng thời gian vừa chạy, hoặc\n"
        "  - truy vấn dòng `delivery` của `audit_log` (`duration_ms` = end-to-end một lượt phía server):\n\n"
        "SELECT count(*) AS tong_luot,\n"
        "       round(avg(duration_ms)) AS avg_ms,\n"
        "       percentile_disc(0.50) WITHIN GROUP (ORDER BY duration_ms) AS p50_ms,\n"
        "       percentile_disc(0.95) WITHIN GROUP (ORDER BY duration_ms) AS p95_ms,\n"
        "       percentile_disc(0.99) WITHIN GROUP (ORDER BY duration_ms) AS p99_ms,\n"
        "       max(duration_ms) AS max_ms,\n"
        f"       round(100.0 * count(*) FILTER (WHERE duration_ms <= {NFR_LATENCY_MS}) / count(*), 1)"
        " AS nfr1_pct\n"
        "FROM audit_log\n"
        "WHERE node = 'delivery'\n"
        f"  AND created_at BETWEEN '{started_at.strftime(fmt)}' AND '{finished_at.strftime(fmt)}';\n\n"
        "(`percentile_disc` = phân vị KHÔNG nội suy, cùng cách tính với `report_service.percentile`.\n"
        " Thêm điều kiện lọc theo mức tải bằng cách chạy từng mức rồi ghi lại mốc thời gian của mức đó.)"
    )


# ── CLI ──────────────────────────────────────────────────────────────────────
def _parse_concurrency(raw: str) -> list[int]:
    levels: list[int] = []
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        value = int(part)
        if value < 1:
            raise argparse.ArgumentTypeError("--concurrency phải là các số nguyên ≥ 1")
        levels.append(value)
    if not levels:
        raise argparse.ArgumentTypeError("--concurrency rỗng")
    return levels


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Tạo tải đồng thời trên /ws/chat để đo độ trễ lượt khách (mục 3.5.6 của báo cáo)."
    )
    parser.add_argument(
        "--concurrency",
        type=_parse_concurrency,
        default=[10],
        help="số hội thoại đồng thời; danh sách để chạy nhiều mức liên tiếp, vd 1,10,25,50,100 (mặc định 10)",
    )
    parser.add_argument("--message", default=DEFAULT_MESSAGE, help="nội dung tin nhắn gửi mỗi lượt")
    parser.add_argument(
        "--message-map",
        default=None,
        help='tệp JSON {"email": "câu hỏi"} — câu riêng cho từng tài khoản; tài khoản không có trong tệp dùng --message',
    )
    parser.add_argument("--base-url", default="http://localhost:8000", help="gốc backend (mặc định http://localhost:8000)")
    parser.add_argument("--timeout", type=float, default=60.0, help="thời gian chờ mỗi lượt, giây (mặc định 60)")
    parser.add_argument("--email-prefix", default="bench", help="tiền tố email tài khoản benchmark (mặc định bench)")
    parser.add_argument("--password", default="bench-password-123", help="mật khẩu dùng cho tài khoản benchmark")
    return parser


async def main() -> int:
    args = _build_parser().parse_args()
    base_url = args.base_url.rstrip("/")
    levels: list[int] = args.concurrency

    print("=== Benchmark đồng thời /ws/chat ===")
    print(f"base-url = {base_url} · mức tải = {','.join(str(n) for n in levels)} · timeout = {args.timeout:g}s")
    print(f"tin nhắn  = {args.message!r}")
    print(
        "Mỗi lượt tốn hạn mức LLM thật. Nếu gặp 429 khi tạo tài khoản: đặt REGISTER_RATE_PER_IP=0 và "
        "LOGIN_RATE_PER_IP=0 trong .env rồi khởi động lại backend."
    )

    message_map: dict[str, str] | None = None
    if args.message_map:
        with open(args.message_map, encoding="utf-8") as fh:
            message_map = json.load(fh)
        print(f"câu riêng = {len(message_map)} tài khoản (từ {args.message_map})")

    token_cache: dict[str, str] = {}
    all_stats: list[LevelStats] = []
    started_at = datetime.now(timezone.utc)

    for n in levels:
        print(f"\n[mức tải N={n}] chuẩn bị {n} tài khoản khách riêng biệt…")
        tokens = await _ensure_tokens(
            base_url, args.email_prefix, args.password, n, token_cache, args.timeout
        )
        if not tokens:
            print(f"  BỎ QUA N={n}: không lấy được token nào.")
            continue
        tokens, dropped = await _drop_human_handled(base_url, tokens, args.timeout)
        if dropped:
            print(
                f"  LOẠI {dropped} tài khoản có ca đang do nhân viên xử lý (AI không chạy → lượt không có khung "
                "kết cục). Đo đủ N: dùng --email-prefix khác, hoặc đóng các ca đó trước."
            )
        if not tokens:
            print(f"  BỎ QUA N={n}: mọi tài khoản đều đang ở trạng thái do nhân viên xử lý.")
            continue
        if len(tokens) < n:
            print(f"  chỉ có {len(tokens)}/{n} tài khoản — mức tải thực tế là {len(tokens)}.")
        print(f"[mức tải N={len(tokens)}] gửi {len(tokens)} tin nhắn đồng thời…")
        results = await _run_level(base_url, tokens, args.message, args.timeout, message_map)
        stats = _summarize(len(tokens), results)
        all_stats.append(stats)
        _print_level(stats)

    finished_at = datetime.now(timezone.utc)
    if not all_stats:
        print("\nKhông có mức tải nào chạy được — kiểm tra backend đã chạy chưa (`make dev-backend`).")
        return 1

    _print_markdown(all_stats)
    _print_server_side_hint(started_at, finished_at)
    return 0


if __name__ == "__main__":
    # Bảng kết quả có dấu tiếng Việt và được dán vào báo cáo: console/pipe dùng codepage cũ (cp1252) sẽ làm
    # `print` vỡ GIỮA lượt đo — tức là mất luôn hạn mức LLM đã tiêu. Ép UTF-8 cho stdout (bỏ qua nếu không được).
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except (AttributeError, OSError, ValueError):
        pass
    try:
        raise SystemExit(asyncio.run(main()))
    except KeyboardInterrupt:
        print("\nĐã dừng (Ctrl+C) — số liệu của các lượt đang chạy bị bỏ, phần đã in vẫn dùng được.")
        sys.exit(130)
