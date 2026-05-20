#!/usr/bin/env python3
"""
Generates assets for the Shareen psychology library:
  - covers/*.jpg  Arabic title-card covers for the 4 noor-book entries
  - qr.png        QR code for the site URL

Run from the project root:
    .venv/bin/python tools/build.py

Uses Pillow's RAQM layout engine for proper Arabic shaping (so we pass
raw Arabic text — no manual reshape/bidi).
"""

from __future__ import annotations

import os
from pathlib import Path

import qrcode
from PIL import Image, ImageDraw, ImageFont, features

ROOT = Path(__file__).resolve().parent.parent
COVERS = ROOT / "covers"
SITE_URL = "https://psychology-weld.vercel.app/"

FONT_REGULAR = str(ROOT / "fonts" / "Cairo-Regular.ttf")
FONT_BOLD = str(ROOT / "fonts" / "Cairo-Bold.ttf")
for _p in (FONT_REGULAR, FONT_BOLD):
    if not os.path.exists(_p):
        raise SystemExit(f"Missing font file: {_p}")
if not features.check("raqm"):
    raise SystemExit(
        "Pillow was built without libraqm. Reinstall in this venv with:\n"
        "  pip install --upgrade --force-reinstall 'pillow[raqm]'"
    )

LAYOUT = ImageFont.Layout.RAQM
DIRECTION = "rtl"


def load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size, layout_engine=LAYOUT)


def text_size(draw: ImageDraw.ImageDraw, text: str, font):
    bbox = draw.textbbox((0, 0), text, font=font, direction=DIRECTION)
    return bbox[2] - bbox[0], bbox[3] - bbox[1], bbox


def draw_centered_rtl(draw: ImageDraw.ImageDraw, xy_center, text, font, fill):
    w, h, bbox = text_size(draw, text, font)
    cx, cy = xy_center
    draw.text(
        (cx - w / 2 - bbox[0], cy - h / 2 - bbox[1]),
        text,
        font=font,
        fill=fill,
        direction=DIRECTION,
    )


def wrap(text: str, font, max_width: int, draw: ImageDraw.ImageDraw):
    words = text.split()
    lines, current = [], ""
    for w in words:
        trial = f"{current} {w}".strip()
        if draw.textlength(trial, font=font, direction=DIRECTION) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines


def make_cover(out_path: Path, title: str, subtitle: str, top_color, bot_color):
    W, H = 600, 900
    img = Image.new("RGB", (W, H), top_color)
    # vertical gradient
    for y in range(H):
        t = y / (H - 1)
        r = int(top_color[0] * (1 - t) + bot_color[0] * t)
        g = int(top_color[1] * (1 - t) + bot_color[1] * t)
        b = int(top_color[2] * (1 - t) + bot_color[2] * t)
        for x in range(W):
            img.putpixel((x, y), (r, g, b))
    d = ImageDraw.Draw(img)

    # decorative top/bottom band
    d.rectangle((0, 0, W, 12), fill=(255, 255, 255, 80))
    d.rectangle((0, H - 12, W, H), fill=(255, 255, 255, 80))

    # Title — wrap to fit
    title_font = load_font(FONT_BOLD, 56)
    max_text_w = W - 80
    lines = wrap(title, title_font, max_text_w, d)
    if len(lines) > 4:
        title_font = load_font(FONT_BOLD, 44)
        lines = wrap(title, title_font, max_text_w, d)

    line_h = title_font.size + 12
    total_h = line_h * len(lines)
    y = (H - total_h) // 2 - 40
    for line in lines:
        draw_centered_rtl(d, (W // 2, y + line_h // 2), line, title_font, fill=(255, 255, 255))
        y += line_h

    # Subtitle (author / source)
    if subtitle:
        sub_font = load_font(FONT_REGULAR, 28)
        draw_centered_rtl(d, (W // 2, H - 100), subtitle, sub_font, fill=(255, 255, 255))

    img.save(out_path, "JPEG", quality=88)
    print(f"wrote {out_path.relative_to(ROOT)}")


GENERATED_COVERS = [
    {
        "slug": "al-murahaqa-wal-inaya",
        "title": "المراهقة والعناية بالمراهقين",
        "subtitle": "",
        "top": (79, 70, 229),
        "bot": (30, 27, 75),
    },
    {
        "slug": "zahran-tufula-murahaqa",
        "title": "علم نفس النمو: الطفولة والمراهقة",
        "subtitle": "د. حامد عبد السلام زهران",
        "top": (13, 148, 136),
        "bot": (4, 47, 46),
    },
    {
        "slug": "usra-hal-mushkilat",
        "title": "سيكولوجية الطفولة والمراهقة — الأسرة ودورها في حل مشكلات الطفل",
        "subtitle": "",
        "top": (217, 119, 6),
        "bot": (69, 26, 3),
    },
    {
        "slug": "sikolojia-tifl-murahiq",
        "title": "سيكولوجية الطفل والمراهق",
        "subtitle": "",
        "top": (225, 29, 72),
        "bot": (76, 5, 25),
    },
]


def build_covers():
    COVERS.mkdir(exist_ok=True)
    for c in GENERATED_COVERS:
        make_cover(
            out_path=COVERS / f"{c['slug']}.jpg",
            title=c["title"],
            subtitle=c["subtitle"],
            top_color=c["top"],
            bot_color=c["bot"],
        )


def build_qr():
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_Q,
        box_size=14,
        border=2,
    )
    qr.add_data(SITE_URL)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0f172a", back_color="white").convert("RGB")
    out = ROOT / "qr.png"
    img.save(out, "PNG")
    print(f"wrote {out.relative_to(ROOT)}  ({img.size[0]}x{img.size[1]})")


if __name__ == "__main__":
    build_covers()
    build_qr()
