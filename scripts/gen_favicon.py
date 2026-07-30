"""Sinh favicon + icon PWA từ nhãn thương hiệu "T" (slice obs P5).

Ảnh gốc trong file design là asset có href UUID (không tải được), nên dựng lại nhãn từ token màu:
ô nền `#211F1B` bo góc + chữ T serif màu kem `#F7F5F0` — đúng ô "T" ở TopBar.

Pillow KHÔNG nằm trong dependency của backend (chỉ cần lúc sinh ảnh, không cần lúc chạy app) → gọi qua
môi trường tạm của uv, giống `make check-conn`:

    uv run --python 3.12 --with pillow scripts/gen_favicon.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "apps" / "dashboard" / "public"

BOX = "#211F1B"  # ink — nền ô
LETTER = "#F7F5F0"  # ink-paper — chữ T
# Georgia = fallback serif khai trong tailwind.config.ts, nên nhãn khớp với chữ hiển thị trên web.
FONT_CANDIDATES = ("georgiab.ttf", "georgia.ttf", "timesbd.ttf", "times.ttf")

# (tên tệp, cạnh px). 16/32/48 cho tab trình duyệt · 256 cho màn hình lớn/Windows ·
# 192/512 cho PWA · apple-touch 512 cho iOS (iOS KHÔNG đọc SVG, buộc phải có PNG).
TARGETS = [
    ("favicon-16.png", 16),
    ("favicon-32.png", 32),
    ("favicon-48.png", 48),
    ("icon-192.png", 192),
    ("icon-256.png", 256),
    ("icon-512.png", 512),
    ("apple-touch-icon.png", 512),
]


def _font(size: int) -> ImageFont.FreeTypeFont:
    for name in FONT_CANDIDATES:
        path = Path("C:/Windows/Fonts") / name
        if path.exists():
            return ImageFont.truetype(str(path), size)
    raise SystemExit(f"Không thấy font serif nào trong {FONT_CANDIDATES}")


def render(size: int) -> Image.Image:
    # Vẽ ở 4× rồi thu nhỏ: bo góc + nét chữ mượt hơn hẳn so với vẽ thẳng ở 16px.
    scale = 4
    side = size * scale
    img = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    radius = round(side * 7 / 26)  # tỉ lệ bo góc lấy từ ô "T" 26px bo 7px ở TopBar
    draw.rounded_rectangle([0, 0, side - 1, side - 1], radius=radius, fill=BOX)

    font = _font(round(side * 0.66))
    left, top, right, bottom = draw.textbbox((0, 0), "T", font=font)
    draw.text(
        ((side - (right - left)) / 2 - left, (side - (bottom - top)) / 2 - top),
        "T",
        font=font,
        fill=LETTER,
    )
    return img.resize((size, size), Image.LANCZOS)


def main() -> int:
    if not OUT_DIR.is_dir():
        print(f"FAIL: không thấy {OUT_DIR}")
        return 1

    cache: dict[int, Image.Image] = {}
    for name, size in TARGETS:
        img = cache.get(size) or render(size)
        cache[size] = img
        img.save(OUT_DIR / name)
        print(f"  {name:<24} {size}×{size}")

    # .ico đa kích thước cho trình duyệt/Windows cũ (vẫn dò /favicon.ico trước khi đọc thẻ <link>).
    cache[48].save(OUT_DIR / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    print(f"  {'favicon.ico':<24} 16+32+48")
    print(f"\nĐã ghi {len(TARGETS) + 1} tệp vào {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
