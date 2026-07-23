"""Đo `retrieval_threshold` trên KB thật (plan §3-P6) — điểm cosine top-1 của Agent 2.

Cách đo: chạy ĐÚNG lời gọi production `rag_service.search(query, top_k, intent)` trên hai tập truy vấn
rồi so phân bố điểm top-1:

- **Trả-lời-được**: câu KB thật sự phủ. Viết bằng GIỌNG KHÁC `questions[]` trong KB (nếu lặp lại nguyên văn
  thì query-expansion cho ~1.0 và phép đo thành vô nghĩa).
- **Không-trả-lời-được**: câu ngoài phạm vi, hoặc trong phạm vi shop nhưng KB KHÔNG có dữ liệu.

Ngưỡng tốt nằm trong "khe" giữa hai phân bố. Script quét các ngưỡng ứng viên và đếm hai loại lỗi:
- **escalate oan** (trả-lời-được mà < ngưỡng → cờ `low_retrieval_score` → chuyển người vô ích),
- **trả bừa** (không-trả-lời-được mà ≥ ngưỡng → bot bám chunk lạc rồi nói sảng).

Chạy (cần .env: QDRANT + LLM_API_KEY; KB đã `make ingest-kb`):
    cd apps/backend && uv run python ../../scripts/measure_threshold.py
"""

from __future__ import annotations

import asyncio
import statistics
import sys
from pathlib import Path

from dotenv import load_dotenv

_REPO_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(_REPO_ROOT / ".env")
sys.path.insert(0, str(_REPO_ROOT / "apps" / "backend"))

from app.core.config import settings  # noqa: E402
from app.core.embeddings import close_openai  # noqa: E402
from app.core.qdrant_client import close_qdrant  # noqa: E402
from app.services import rag_service  # noqa: E402

# (câu khách, intent Agent 1 dự kiến) — intent truyền y như production để đo đúng đường đi thật.
ANSWERABLE: list[tuple[str, str]] = [
    ("gửi hàng ra Hà Nội tốn bao nhiêu tiền", "shipping"),
    ("mua bao nhiêu thì được miễn phí giao hàng", "shipping"),
    ("bao lâu thì em nhận được hàng", "shipping"),
    ("em ở đảo thì giao lâu hơn đúng không", "shipping"),
    ("có cho ra cửa hàng lấy đồ không", "shipping"),
    ("mã vận đơn shop gửi qua đâu", "order_status"),
    ("đơn của em giờ tới đâu rồi", "order_status"),
    ("muốn đặt hàng thì làm sao", "order_status"),
    ("shop nhận trả tiền mặt khi nhận hàng không", "payment"),
    ("chuyển khoản cho shop được không", "payment"),
    ("làm sao để thành khách thành viên", "membership"),
    ("điểm tích được dùng vào việc gì", "membership"),
    ("dạo này shop có giảm giá gì không", "promotion"),
    ("mã giảm giá nhập ở chỗ nào", "promotion"),
    ("giá trên web với ngoài tiệm có bằng nhau không", "product_price"),
    ("em xem giá món đồ ở đâu", "product_price"),
    ("em cao 1m70 nặng 65 thì mặc số mấy", "size_consulting"),
    ("đo vòng ngực kiểu gì cho đúng", "size_consulting"),
    ("số đo em nằm giữa hai size thì lấy cái nào", "size_consulting"),
    ("áo này giặt máy được không", "product_information"),
    ("phơi đồ kiểu gì cho khỏi giãn", "product_information"),
    ("mua xong bao lâu thì được trả lại", "return_exchange_policy"),
    ("đồ giặt rồi còn đổi được không", "return_exchange_policy"),
    ("mua ở cửa hàng có trả lại được không", "return_exchange_policy"),
    ("đồ lót đã bóc ra rồi có đổi được không", "return_exchange_policy"),
    ("hàng lỗi của nhà sản xuất thì bảo hành bao lâu", "return_exchange_policy"),
    ("shop làm việc tới mấy giờ", "store_information"),
    ("có số điện thoại nào gọi được không", "store_information"),
    ("ngoài giờ hành chính có ai trả lời không", "store_information"),
    ("em muốn đổi cái áo sang size to hơn", "exchange"),
    ("nhận được hàng bị rách chỉ thì làm sao", "complaint"),
    ("đặt lâu rồi mà chưa thấy ship tới", "order_status"),
]

# Trong phạm vi shop nhưng KB KHÔNG có dữ liệu, + câu hoàn toàn lạc đề.
UNANSWERABLE: list[tuple[str, str]] = [
    ("cho mình hỏi vé xem phim tối nay giá bao nhiêu", "other"),
    ("mai trời có mưa không shop", "other"),
    ("tối qua đội nào thắng vậy", "other"),
    ("shop biết chỗ nào sửa xe máy gần đây không", "other"),
    ("cho xin công thức nấu phở với", "other"),
    ("shop có tuyển nhân viên bán hàng không", "store_information"),
    ("cửa hàng ở Huế nằm đường nào", "store_information"),
    ("shop thành lập năm nào vậy", "store_information"),
    ("cho xin mã số thuế của công ty", "store_information"),
    ("shop có ship đi Mỹ không", "shipping"),
    ("giao hàng trong 2 tiếng có được không", "shipping"),
    ("shop có bán giày da nam không", "product_information"),
    ("có bán đồ cho em bé sơ sinh không", "product_information"),
    ("áo này có size 5XL không", "size_consulting"),
    ("vải này có chống tia UV không", "product_information"),
    ("shop có cho thuê váy cưới không", "product_information"),
    ("có bán thẻ quà tặng không", "promotion"),
    ("cho mình xin mã giảm 70% đi", "promotion"),
    ("shop có trả góp 0 đồng không", "payment"),
    ("thanh toán bằng tiền điện tử bitcoin được không", "payment"),
    ("thẻ thành viên hạng kim cương cần bao nhiêu điểm", "membership"),
    ("shop có chương trình tích điểm đổi vé máy bay không", "membership"),
    ("cho mình xin số tài khoản của giám đốc", "payment"),
    ("shop có nhận đặt may riêng theo số đo không", "size_consulting"),
    ("đơn của em có được bảo hiểm hàng hoá không", "shipping"),
]

CANDIDATES = [round(0.05 * i, 2) for i in range(2, 17)]  # 0.10 … 0.80

# HAI LOẠI LỖI KHÔNG NGANG GIÁ — đừng cộng chúng rồi tìm cực tiểu:
# - "escalate oan" là lỗi CUỐI: khách hỏi câu shop trả lời được mà vẫn phải chờ người → mất đúng thứ hệ
#   thống sinh ra để làm. Không ai bắt được nó sau đó nữa.
# - "trả bừa" CÒN hai tuyến sau: Agent 1 gắn `out_of_domain` cho câu lạc đề (→ handoff bất kể điểm), và
#   Agent 4 chỉ nói từ nguồn được cấp, thiếu thì bảo chuyển nhân viên.
# Nên chọn ngưỡng CAO NHẤT mà tỉ lệ escalate oan còn trong ngân sách, thay vì cực tiểu tổng lỗi.
FALSE_ESCALATION_BUDGET = 0.05


def _pcts(scores: list[float]) -> str:
    s = sorted(scores)
    q = statistics.quantiles(s, n=100, method="inclusive")
    return (f"min={s[0]:.3f}  p10={q[9]:.3f}  p25={q[24]:.3f}  median={q[49]:.3f}  "
            f"p75={q[74]:.3f}  p90={q[89]:.3f}  max={s[-1]:.3f}")


async def _measure(rows: list[tuple[str, str]], label: str) -> list[dict]:
    out: list[dict] = []
    print(f"\n{label} ({len(rows)} câu)")
    print(f"  {'SCORE':>7}  {'KIỂU':<5} {'NGUỒN':<40} CÂU")
    for text, intent in rows:
        hits = await rag_service.search(text, top_k=4, intent=intent)
        top = hits[0] if hits else None
        score = float(top["score"]) if top else 0.0
        kind = "q-exp" if (top and top.get("question")) else "thân"
        out.append({"text": text, "intent": intent, "score": score, "kind": kind,
                    "source": (top or {}).get("source") or "—"})
        print(f"  {score:>7.4f}  {kind:<5} {((top or {}).get('source') or '—'):<40} {text}")
    return out


def _report(ans: list[dict], una: list[dict]) -> float:
    a_scores = [r["score"] for r in ans]
    u_scores = [r["score"] for r in una]

    print("\n" + "=" * 92)
    print("PHÂN BỐ ĐIỂM TOP-1")
    print(f"  trả-lời-được      : {_pcts(a_scores)}")
    print(f"  không-trả-lời-được: {_pcts(u_scores)}")

    body = [r["score"] for r in ans if r["kind"] == "thân"]
    qexp = [r["score"] for r in ans if r["kind"] == "q-exp"]
    print(f"\n  Trong tập trả-lời-được: {len(qexp)} câu khớp qua query-expansion, {len(body)} câu khớp thân.")
    if qexp:
        print(f"    khớp q-exp: {_pcts(qexp)}")
    if body:
        print(f"    khớp thân : {_pcts(body)}   <- ngưỡng canh chủ yếu cho nhóm này (§2.7)")

    print("\n" + "=" * 92)
    print("QUÉT NGƯỠNG — escalate oan (trả-lời-được < ngưỡng) vs trả bừa (không-trả-lời-được >= ngưỡng)")
    print(f"  {'NGƯỠNG':>7}  {'ESCALATE OAN':>13}  {'TỈ LỆ':>7}  {'TRẢ BỪA':>9}  {'TỔNG LỖI':>9}")
    budget = FALSE_ESCALATION_BUDGET * len(a_scores)
    best = CANDIDATES[0]
    min_total, at_min_total = None, None
    for t in CANDIDATES:
        oan = sum(1 for s in a_scores if s < t)
        bua = sum(1 for s in u_scores if s >= t)
        total = oan + bua
        if oan <= budget:
            best = t  # ngưỡng CAO NHẤT còn trong ngân sách escalate oan
        if min_total is None or total < min_total:
            min_total, at_min_total = total, t
        print(f"  {t:>7.2f}  {oan:>13}  {oan / len(a_scores):>6.0%}  {bua:>9}  {total:>9}")

    oan_best = sum(1 for s in a_scores if s < best)
    print(f"\n  Ngân sách escalate oan: <= {FALSE_ESCALATION_BUDGET:.0%} "
          f"({budget:.1f}/{len(a_scores)} câu)")
    print(f"  -> ngưỡng cao nhất còn trong ngân sách: {best:.2f} (escalate oan {oan_best}/{len(a_scores)})")
    oan_min = sum(1 for s in a_scores if s < at_min_total)
    print(f"  (Cực tiểu TỔNG lỗi là {min_total} tại {at_min_total:.2f}, NHƯNG phải trả bằng "
          f"{oan_min}/{len(a_scores)} = {oan_min / len(a_scores):.0%} escalate oan — không đáng.)")

    # "Khe" giữa hai phân bố: từ điểm cao nhất của nhóm không-trả-lời-được tới điểm thấp nhất nhóm kia.
    lo, hi = max(u_scores), min(a_scores)
    print(f"\n  Khe: max(không-trả-lời-được)={lo:.4f} · min(trả-lời-được)={hi:.4f} -> "
          + ("KHE RỖNG — hai phân bố chồng nhau, cosine top-1 KHÔNG tách được hai tập trên KB này"
             if lo >= hi else f"khe = [{lo:.4f}, {hi:.4f}]"))
    print(f"  Ngưỡng hiện tại: {settings.retrieval_threshold}")
    return best


async def main() -> int:
    ans = await _measure(ANSWERABLE, "TẬP 1 — TRẢ-LỜI-ĐƯỢC")
    una = await _measure(UNANSWERABLE, "TẬP 2 — KHÔNG-TRẢ-LỜI-ĐƯỢC")
    await close_openai()
    await close_qdrant()
    best = _report(ans, una)
    print(f"\nĐỀ XUẤT: RETRIEVAL_THRESHOLD={best:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
