#!/usr/bin/env python3
"""Render static brand assets from committed Familiars spritesheets."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from render_reel import (  # noqa: E402
    draw_background,
    draw_brand_title,
    draw_card,
    draw_pet,
    load_font,
    sprite_for,
    text_size,
    wave,
)


BRAND = ROOT / "assets" / "brand"
BANNER = BRAND / "familiars-banner.webp"
SOCIAL_PREVIEW = BRAND / "social-preview.png"
BRAND_LOGO = BRAND / "zentrik-logo.png"
MAX_BANNER_BYTES = 450_000


def draw_pill(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    text: str,
    accent: tuple[int, int, int, int],
) -> int:
    font = load_font(24, bold=True)
    padding_x = 28
    text_width, text_height = text_size(draw, text, font)
    width = text_width + padding_x * 2
    height = 48
    draw.rounded_rectangle(
        (x, y, x + width, y + height),
        radius=height // 2,
        fill=(9, 18, 33, 210),
        outline=accent,
        width=2,
    )
    draw.text((x + padding_x, y + (height - text_height) / 2 - 2), text, fill="#f8fafc", font=font)
    return x + width + 18


def draw_micro_label(draw: ImageDraw.ImageDraw, x: int, y: int, text: str) -> None:
    font = load_font(22, bold=True)
    draw_card(
        draw,
        (x, y, x + 132, y + 42),
        text,
        font,
        fill=(219, 234, 254, 222),
        outline=(33, 231, 220, 105),
        text_fill=(17, 24, 39, 255),
    )


def draw_zentrik_mark(frame: Image.Image) -> None:
    draw = ImageDraw.Draw(frame, "RGBA")
    font = load_font(23, bold=True)
    x, y = 1326, 456
    draw.text((x, y + 12), "zentrik.ai", fill="#dbeafe", font=font)
    if BRAND_LOGO.is_file():
        with Image.open(BRAND_LOGO) as logo:
            mark = logo.convert("RGBA").resize((52, 52), Image.Resampling.LANCZOS)
        frame.alpha_composite(mark, (x + 142, y))


def render_banner() -> Image.Image:
    width, height = 1600, 520
    frame = draw_background(width, height, tick=8)
    draw = ImageDraw.Draw(frame, "RGBA")

    # A single diagonal accent keeps the brand energy from the reels without
    # turning the README header into another dense animation frame.
    draw.polygon(
        [(760, -20), (824, -20), (690, height + 28), (626, height + 28)],
        fill=(33, 231, 220, 210),
    )
    draw.polygon(
        [(824, -20), (842, -20), (708, height + 28), (690, height + 28)],
        fill=(10, 18, 32, 190),
    )

    title_font = load_font(86, bold=True)
    subtitle_font = load_font(35, bold=True)
    body_font = load_font(28)
    small_font = load_font(22)

    draw_brand_title(draw, (80, 95), "Familiars", title_font)
    draw.text((84, 190), "Codex pets for product work", fill="#f8fafc", font=subtitle_font)
    draw.text((84, 245), "Small companions for roadmaps, reviews,", fill="#cbd5e1", font=body_font)
    draw.text((84, 286), "agent sessions, and useful taste.", fill="#cbd5e1", font=body_font)

    next_x = 84
    for label, accent in (
        ("install", (33, 231, 220, 180)),
        ("browse", (132, 190, 238, 150)),
        ("create", (33, 231, 220, 180)),
    ):
        next_x = draw_pill(draw, next_x, 358, label, accent)

    draw.text((84, 460), "github.com/jalcantarab/agent-familiars", fill="#c4d2e8", font=small_font)

    panel = (900, 80, 1502, 448)
    draw.rounded_rectangle(
        panel,
        radius=30,
        fill=(9, 18, 33, 176),
        outline=(33, 231, 220, 156),
        width=3,
    )
    draw.rounded_rectangle(
        (panel[0] + 24, panel[1] + 24, panel[2] - 24, panel[3] - 24),
        radius=24,
        fill=(11, 22, 39, 120),
        outline=(132, 190, 238, 80),
        width=2,
    )

    draw.text((936, 112), "Product folklore", fill="#f8fafc", font=load_font(34, bold=True))
    draw.text((938, 155), "scope, signal, launch, tradeoff", fill="#cbd5e1", font=load_font(23))

    for cx, cy, radius, alpha in ((1160, 286, 118, 28), (1160, 286, 78, 42)):
        draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), outline=(33, 231, 220, alpha), width=3)

    draw_pet(frame, sprite_for("signal-heron", "waiting", 2), (1008, 318 + 8 * wave(0.2)), 205)
    knight_box = draw_pet(frame, sprite_for("no-knight", "waiting", 3), (1170, 326), 250)
    draw_pet(frame, sprite_for("launch-lantern", "review", 1), (1340, 328 + 5 * wave(0.4)), 206)

    underline_y = knight_box[1] + (knight_box[3] - knight_box[1]) * 0.66
    draw.line(
        (
            knight_box[0] + (knight_box[2] - knight_box[0]) * 0.3,
            underline_y,
            knight_box[0] + (knight_box[2] - knight_box[0]) * 0.7,
            underline_y,
        ),
        fill=(33, 231, 220, 140),
        width=5,
    )

    draw_micro_label(draw, 952, 386, "signal")
    draw_micro_label(draw, 1122, 386, "scope")
    draw_micro_label(draw, 1292, 386, "launch")

    draw_zentrik_mark(frame)
    return frame.convert("RGB")


def render_assets() -> None:
    BRAND.mkdir(parents=True, exist_ok=True)
    render_banner().save(BANNER, "WEBP", quality=92, method=6)
    print(f"wrote {BANNER.relative_to(ROOT)} ({BANNER.stat().st_size:,} bytes)")


def check_assets() -> None:
    missing = [path.relative_to(ROOT) for path in (BANNER, SOCIAL_PREVIEW) if not path.is_file()]
    if missing:
        raise SystemExit("missing brand assets: " + ", ".join(str(path) for path in missing))
    if BANNER.stat().st_size > MAX_BANNER_BYTES:
        raise SystemExit(
            f"{BANNER.relative_to(ROOT)} is {BANNER.stat().st_size:,} bytes; "
            f"keep it under {MAX_BANNER_BYTES:,}"
        )
    print("brand assets ok")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify committed brand assets exist and stay small.")
    args = parser.parse_args()

    if args.check:
        check_assets()
    else:
        render_assets()


if __name__ == "__main__":
    main()
