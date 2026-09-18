"""Biểu đồ số liệu của báo cáo — dựng từ CHÍNH số liệu các bảng trong báo cáo (không số liệu nào khác).

Chạy (không cần cài gì vào dự án, uv tự tạo môi trường tạm):
    uv run --with matplotlib python baocao/hinh-ve/bieu-do.py

Ảnh PNG ghi cạnh các tệp .puml của từng chương, kích thước in thật rộng 16 cm, 300 dpi, nên cỡ chữ
trong ảnh đúng bằng cỡ chữ khi in.

Bảng màu: slot 1–3 của bảng màu phân loại đã kiểm định (validate_palette.js, nền trắng: PASS; aqua
tương phản 2,82:1 → luôn kèm nhãn trực tiếp). Mỗi chuỗi có thêm hình dạng marker riêng để bản in đen
trắng vẫn phân biệt được.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

HERE = Path(__file__).resolve().parent

# ── Token màu & mực ────────────────────────────────────────────────────────────
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK_2, MUTED = "#0b0b0b", "#52514e", "#898781"
GRID, AXIS, SURFACE = "#e1e0d9", "#c3c2b7", "#ffffff"
WASH_GRAY = "#f0efec"

CM = 1 / 2.54
WIDTH = 16 * CM
DPI = 300

plt.rcParams.update(
    {
        "font.family": "Arial",
        "font.size": 9,
        "axes.edgecolor": AXIS,
        "axes.linewidth": 0.8,
        "axes.labelcolor": INK_2,
        "axes.labelsize": 9.5,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "xtick.labelcolor": INK_2,
        "ytick.labelcolor": INK_2,
        "xtick.major.size": 0,
        "ytick.major.size": 0,
        "legend.frameon": False,
        "legend.fontsize": 8.5,
        "savefig.facecolor": SURFACE,
        "figure.facecolor": SURFACE,
    }
)


def vn(x: float, digits: int = 2) -> str:
    """Số thập phân kiểu Việt Nam: 0,40 thay cho 0.40."""
    return f"{x:.{digits}f}".replace(".", ",")


def grid(ax, axis: str = "y") -> None:
    ax.grid(axis=axis, color=GRID, linewidth=0.6, linestyle="-")
    ax.set_axisbelow(True)


def save(fig, relpath: str) -> None:
    out = HERE / relpath
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=DPI, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)
    print(f"  đã ghi {out.relative_to(HERE)}")


# ══════════════════════════════════════════════════════════════════════════════
# Hình 1.5 — Bản đồ định vị (dữ liệu: Bảng 1.1, hai tiêu chí đầu, thang thứ bậc)
# ══════════════════════════════════════════════════════════════════════════════
BANG_1_1 = [
    # (nhóm giải pháp, hiểu ngôn ngữ tự do, dự đoán được luồng chạy)
    ("Chatbot\ntheo kịch bản", "Không", "Cao"),
    ("Chatbot NLU\ntruyền thống", "Trung bình", "Cao"),
    ("LLM/RAG một bước", "Tốt", "Trung bình"),
    ("Đa tác tử có Supervisor", "Tốt", "Thấp"),
    ("Hệ thống đề xuất", "Tốt", "Cao"),
]
MUC_NGON_NGU = {"Không": 1, "Trung bình": 2, "Tốt": 3}
MUC_DU_DOAN = {"Thấp": 1, "Trung bình": 2, "Cao": 3}


def hinh_1_05() -> None:
    fig, ax = plt.subplots(figsize=(WIDTH, 10.5 * CM))

    # Góc phần tư khoảng trống: hiểu ngôn ngữ tốt + dự đoán được cao
    ax.axvspan(2.5, 3.6, ymin=(2.5 - 0.4) / 3.2, ymax=1, color=BLUE, alpha=0.08, lw=0)
    ax.text(3.55, 3.52, "Khoảng trống đề tài hướng tới", ha="right", va="top", fontsize=8.5,
            color=INK_2, fontweight="bold")

    # Vị trí nhãn đặt tay để không đè lên điểm
    offsets = {
        "Chatbot\ntheo kịch bản": (0.0, -0.24, "center"),
        "Chatbot NLU\ntruyền thống": (0.0, -0.24, "center"),
        "LLM/RAG một bước": (-0.09, 0.0, "right"),
        "Đa tác tử có Supervisor": (-0.09, 0.0, "right"),
        "Hệ thống đề xuất": (-0.09, -0.02, "right"),
    }
    for name, ngon_ngu, du_doan in BANG_1_1:
        x, y = MUC_NGON_NGU[ngon_ngu], MUC_DU_DOAN[du_doan]
        de_xuat = name == "Hệ thống đề xuất"
        ax.plot(x, y, "o", ms=11 if de_xuat else 9, color=BLUE if de_xuat else MUTED,
                mec=SURFACE, mew=1.8, zorder=4)
        dx, dy, ha = offsets[name]
        ax.text(x + dx, y + dy, name, ha=ha, va="center", fontsize=9,
                color=INK if de_xuat else INK_2, fontweight="bold" if de_xuat else "normal", zorder=5)

    # Hướng dịch chuyển của đề tài
    ax.annotate("", xy=(3.16, 2.86), xytext=(3.16, 1.12),
                arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.2, shrinkA=0, shrinkB=0))
    ax.text(3.24, 1.95, "giữ năng lực ngôn ngữ\nở tầng tác tử,\nrút quyền tự trị\nkhỏi tầng điều phối",
            ha="left", va="center", fontsize=8, color=INK_2, linespacing=1.25)

    ax.set_xlim(0.4, 3.9)
    ax.set_ylim(0.4, 3.6)
    ax.set_xticks([1, 2, 3], ["Không", "Trung bình", "Tốt"])
    for t in ax.get_xticklabels():  # chữ có dấu cao làm lệch hàng khi căn theo đỉnh → căn theo baseline
        t.set_va("baseline")
    ax.tick_params(axis="x", pad=14)
    ax.set_yticks([1, 2, 3], ["Thấp", "Trung bình", "Cao"])
    ax.set_xlabel("Năng lực hiểu ngôn ngữ tự nhiên")
    ax.set_ylabel("Mức độ dự đoán được của luồng chạy")
    grid(ax, "both")
    ax.text(0.42, 0.45, "Vị trí định tính theo Bảng 1.1 (thang thứ bậc, không phải số đo)",
            fontsize=7.5, color=MUTED, ha="left", va="bottom")
    save(fig, "chuong-1/hinh-1-05-ban-do-dinh-vi.png")


# ══════════════════════════════════════════════════════════════════════════════
# Hình 3.2 — Phân bố điểm cosine (dữ liệu: Bảng 3.9)
# ══════════════════════════════════════════════════════════════════════════════
BANG_3_9 = {
    # tập: (n, min, p10, p25, trung vị, p75, p90, max)
    "Trả lời được": (32, 0.380, 0.477, 0.560, 0.648, 0.723, 0.777, 0.804),
    "Không trả lời được": (25, 0.383, 0.393, 0.416, 0.549, 0.579, 0.608, 0.658),
}
RETRIEVAL_THRESHOLD = 0.40  # .env.example / mục 3.3.5


def hinh_3_02() -> None:
    fig, ax = plt.subplots(figsize=(WIDTH, 7.2 * CM))
    rows = [("Không trả lời được", ORANGE, 1.0), ("Trả lời được", BLUE, 2.0)]

    lo = BANG_3_9["Trả lời được"][1]  # min của tập trả lời được
    hi = BANG_3_9["Không trả lời được"][7]  # max của tập không trả lời được
    ax.axvspan(lo, hi, color=WASH_GRAY, lw=0, zorder=0)
    ax.text((lo + hi) / 2 + 0.03, 2.6, f"Vùng chồng lấn {vn(lo, 3)} – {vn(hi, 3)}\nkhông ngưỡng nào tách sạch hai tập",
            ha="center", va="center", fontsize=8, color=INK_2, linespacing=1.3, zorder=5,
            bbox=dict(boxstyle="square,pad=0.25", facecolor=WASH_GRAY, edgecolor="none"))

    for name, color, y in rows:
        n, mn, p10, p25, med, p75, p90, mx = BANG_3_9[name]
        h = 0.42
        ax.add_patch(plt.Rectangle((p25, y - h / 2), p75 - p25, h, facecolor=color, alpha=0.18,
                                   edgecolor=color, lw=1.4, zorder=2))
        ax.plot([med, med], [y - h / 2, y + h / 2], color=INK, lw=2.2, solid_capstyle="butt", zorder=3)
        for a, b in ((p10, p25), (p75, p90)):
            ax.plot([a, b], [y, y], color=color, lw=1.4, zorder=2)
        for p in (p10, p90):
            ax.plot([p, p], [y - h / 4, y + h / 4], color=color, lw=1.4, zorder=2)
        ax.plot([mn, mx], [y, y], "o", ms=6.5, color=color, mec=SURFACE, mew=1.4, zorder=4)
        ax.text(med, y + h / 2 + 0.07, f"trung vị {vn(med, 3)}", ha="center", va="bottom",
                fontsize=8, color=INK_2)

    # Hai cực trị định nghĩa vùng chồng lấn
    ax.annotate(f"min {vn(lo, 3)}", xy=(lo, 2.0), xytext=(lo - 0.004, 1.62), ha="right", fontsize=8,
                color=INK_2, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    ax.annotate(f"max {vn(hi, 3)}", xy=(hi, 1.0), xytext=(hi + 0.004, 1.38), ha="left", fontsize=8,
                color=INK_2, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))

    ax.axvline(RETRIEVAL_THRESHOLD, color=INK_2, lw=1.1, ls=(0, (4, 3)), zorder=1)
    ax.text(RETRIEVAL_THRESHOLD - 0.004, 0.42, f"ngưỡng truy hồi {vn(RETRIEVAL_THRESHOLD)}",
            ha="right", va="bottom", fontsize=8, color=INK_2)

    ax.set_ylim(0.35, 2.9)
    ax.set_xlim(0.33, 0.83)
    ax.set_yticks([1, 2], [f"Không trả lời được\n(n = {BANG_3_9['Không trả lời được'][0]})",
                           f"Trả lời được\n(n = {BANG_3_9['Trả lời được'][0]})"])
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: vn(v)))
    ax.set_xlabel("Điểm cosine của kết quả truy hồi tốt nhất")
    grid(ax, "x")

    key = [
        Patch(facecolor=MUTED, alpha=0.25, edgecolor=MUTED, label="hộp: p25 – p75"),
        Line2D([], [], color=INK, lw=2.2, label="vạch đậm: trung vị"),
        Line2D([], [], color=MUTED, lw=1.4, label="râu: p10 – p90"),
        Line2D([], [], ls="", marker="o", ms=6.5, color=MUTED, mec=SURFACE, label="chấm: min, max"),
    ]
    ax.legend(handles=key, loc="upper center", bbox_to_anchor=(0.5, -0.24), ncol=4, handlelength=1.6,
              columnspacing=1.4)
    save(fig, "chuong-3/hinh-3-02-phan-bo-cosine.png")


# ══════════════════════════════════════════════════════════════════════════════
# Hình 3.3 — Quét ngưỡng truy hồi (dữ liệu: Bảng 3.10)
# ══════════════════════════════════════════════════════════════════════════════
BANG_3_10 = [
    # (ngưỡng, escalate oan /32, trả bừa /25, tổng lỗi)
    (0.35, 0, 25, 25),
    (0.40, 1, 21, 22),
    (0.45, 2, 18, 20),
    (0.50, 5, 16, 21),
    (0.55, 7, 12, 19),
    (0.60, 13, 4, 17),
    (0.65, 16, 1, 17),
    (0.70, 18, 0, 18),
]
N_TRA_LOI_DUOC = 32
NGAN_SACH_ESCALATE_OAN = 0.05  # quy tắc chọn ngưỡng, mục 3.3.5


def hinh_3_03() -> None:
    fig, ax = plt.subplots(figsize=(WIDTH, 9.0 * CM))
    xs = [r[0] for r in BANG_3_10]
    series = [
        ("Escalate oan (trên 32 câu trả lời được)", [r[1] for r in BANG_3_10], BLUE, "o"),
        ("Trả bừa (trên 25 câu không trả lời được)", [r[2] for r in BANG_3_10], ORANGE, "s"),
        ("Tổng lỗi", [r[3] for r in BANG_3_10], AQUA, "^"),
    ]

    ax.axvspan(0.60, 0.65, color=WASH_GRAY, lw=0, zorder=0)
    ax.text(0.625, 27.3, "cực tiểu tổng lỗi (17)\nnhưng escalate oan 41–50%", ha="center", va="top",
            fontsize=8, color=INK_2)

    budget = NGAN_SACH_ESCALATE_OAN * N_TRA_LOI_DUOC
    ax.axhline(budget, color=MUTED, lw=0.9, ls=(0, (2, 2)), zorder=1)
    ax.text(0.468, budget - 0.45, f"ngân sách escalate oan 5% ≈ {vn(budget, 1)} câu", ha="left", va="top",
            fontsize=7.5, color=MUTED)

    ax.axvline(0.40, color=INK_2, lw=1.1, ls=(0, (4, 3)), zorder=1)
    ax.text(0.404, 27.3, "ngưỡng chọn 0,40", ha="left", va="top", fontsize=8, color=INK, fontweight="bold")

    for label, ys, color, marker in series:
        ax.plot(xs, ys, color=color, lw=2, marker=marker, ms=6.5, mec=SURFACE, mew=1.4, label=label,
                solid_joinstyle="round", solid_capstyle="round", zorder=3)

    # Nhãn chọn lọc: điểm tại ngưỡng đã chọn
    ax.annotate("1 câu (3%)", xy=(0.40, 1), xytext=(0.418, 4.6), fontsize=8, color=INK_2,
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    ax.annotate("tổng lỗi 22", xy=(0.40, 22), xytext=(0.408, 23.1), fontsize=8, color=INK_2, ha="left")

    ax.set_xticks(xs, [vn(x) for x in xs])
    ax.set_xlim(0.335, 0.715)
    ax.set_ylim(0, 27.5)
    ax.set_xlabel("Ngưỡng truy hồi (RETRIEVAL_THRESHOLD)")
    ax.set_ylabel("Số câu hỏi bị xử lý sai")
    grid(ax, "y")
    handles = [Line2D([], [], color=c, lw=2, marker=m, ms=6.5, mec=c, label=lb) for lb, _, c, m in series]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=3, handlelength=2.2,
              columnspacing=1.2)
    save(fig, "chuong-3/hinh-3-03-quet-nguong.png")


# ══════════════════════════════════════════════════════════════════════════════
# Hình 3.14 — p95 theo số hội thoại đồng thời (dữ liệu: Bảng 3.18)
# Cột p95 (ms) của Bảng 3.18 — số phía máy chủ (dòng delivery của audit_log), đo 18/09/2026 bằng `make bench`, hồ kết nối 20 + 30.
# ══════════════════════════════════════════════════════════════════════════════
BANG_3_18_P95_MS: dict[int, float | None] = {1: 5860, 10: 5648, 25: 5481, 50: 6598, 100: 9705}
NFR_1_P95_MS = 5000  # PRD: NFR-1 — phản hồi tự động P95 ≤ 5 giây


def hinh_3_14() -> None:
    if any(v is None for v in BANG_3_18_P95_MS.values()):
        print("  BỎ QUA Hình 3.14 — Bảng 3.18 chưa có số liệu (điền BANG_3_18_P95_MS sau khi chạy make bench)")
        return
    fig, ax = plt.subplots(figsize=(WIDTH, 8.0 * CM))
    xs = list(BANG_3_18_P95_MS)
    ys = [BANG_3_18_P95_MS[x] / 1000 for x in xs]
    ax.axhline(NFR_1_P95_MS / 1000, color=INK_2, lw=1.1, ls=(0, (4, 3)))
    ax.text(xs[-1], NFR_1_P95_MS / 1000 + 0.1, "NFR-1: P95 ≤ 5 giây", ha="right", va="bottom", fontsize=8,
            color=INK_2)
    ax.plot(xs, ys, color=BLUE, lw=2, marker="o", ms=6.5, mec=SURFACE, mew=1.4, zorder=3)
    ax.annotate(f"{vn(ys[-1], 1)} s", xy=(xs[-1], ys[-1]), xytext=(6, 0), textcoords="offset points",
                va="center", fontsize=8, color=INK_2)
    ax.set_xticks(xs, [str(x) for x in xs])
    ax.set_ylim(0, max(max(ys), NFR_1_P95_MS / 1000) * 1.2)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: vn(v, 1)))
    ax.set_xlabel("Số hội thoại đồng thời")
    ax.set_ylabel("Độ trễ p95 phía máy chủ (giây)")
    grid(ax, "y")
    save(fig, "chuong-3/hinh-3-14-p95-theo-tai.png")


if __name__ == "__main__":
    print("Dựng biểu đồ số liệu ...")
    hinh_1_05()
    hinh_3_02()
    hinh_3_03()
    hinh_3_14()
