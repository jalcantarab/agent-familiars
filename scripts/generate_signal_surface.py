#!/usr/bin/env python3
"""Generate the Signal Surface Codex pet spritesheet."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pets" / "signal-surface" / "spritesheet.webp"

CELL_WIDTH = 192
CELL_HEIGHT = 208
COLUMNS = 8
ROWS = [
    ("idle", 6),
    ("running-right", 8),
    ("running-left", 8),
    ("waving", 4),
    ("jumping", 5),
    ("failed", 8),
    ("waiting", 6),
    ("running", 6),
    ("review", 6),
]

SCALE = 4
TILE_WIDTH = 120
TILE_HEIGHT = 94


def rgb(hex_color: str) -> tuple[int, int, int]:
    stripped = hex_color.strip("#")
    return (
        int(stripped[0:2], 16),
        int(stripped[2:4], 16),
        int(stripped[4:6], 16),
    )


def rgba(hex_color: str, alpha: int = 255) -> tuple[int, int, int, int]:
    return (*rgb(hex_color), alpha)


def mix(a: tuple[int, int, int], b: tuple[int, int, int], amount: float) -> tuple[int, int, int]:
    amount = max(0.0, min(1.0, amount))
    return tuple(round(a[index] + (b[index] - a[index]) * amount) for index in range(3))


def palette(state: str, phase: float) -> dict[str, str]:
    if state in {"idle", "waving", "jumping"}:
        return {
            "top": "#08212d",
            "bottom": "#0b4654",
            "accent": "#36f0e4",
            "second": "#7dffb2",
            "rim": "#d6fffb",
        }
    if state in {"running", "running-right", "running-left"}:
        return {
            "top": "#072335",
            "bottom": "#075655",
            "accent": "#31f4cf",
            "second": "#b6ff68",
            "rim": "#e4fff8",
        }
    if state == "waiting":
        return {
            "top": "#1d2038",
            "bottom": "#47301c",
            "accent": "#ffcb5c",
            "second": "#7ddcff",
            "rim": "#fff1b8",
        }
    if state == "failed":
        hot = 0.5 + 0.5 * math.sin(phase * math.tau)
        return {
            "top": "#321622",
            "bottom": "#671b25",
            "accent": "#ff5268" if hot > 0.45 else "#d83d53",
            "second": "#ffad4d",
            "rim": "#ffd6c7",
        }
    if state == "review":
        return {
            "top": "#0d1934",
            "bottom": "#123b5f",
            "accent": "#9edcff",
            "second": "#ffffff",
            "rim": "#e8fbff",
        }
    raise ValueError(f"unknown state {state!r}")


def rounded_mask(size: tuple[int, int], radius: int) -> Image.Image:
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=radius, fill=255)
    return mask


def diagonal_gradient(size: tuple[int, int], top: str, bottom: str, accent: str, phase: float) -> Image.Image:
    width, height = size
    top_rgb = rgb(top)
    bottom_rgb = rgb(bottom)
    accent_rgb = rgb(accent)
    band = (phase * 1.2 - 0.1) % 1.0
    pixels = []
    for y in range(height):
        for x in range(width):
            base_amount = (x / max(1, width - 1)) * 0.35 + (y / max(1, height - 1)) * 0.65
            color = mix(top_rgb, bottom_rgb, base_amount)
            distance = abs(((x / width) * 0.55 + (y / height) * 0.45) - band)
            accent_amount = max(0.0, 1.0 - distance * 8.0) * 0.34
            color = mix(color, accent_rgb, accent_amount)
            pixels.append((*color, 255))
    image = Image.new("RGBA", size)
    image.putdata(pixels)
    return image


def clip_to(mask: Image.Image, image: Image.Image) -> Image.Image:
    clipped = image.copy()
    clipped.putalpha(ImageChops.multiply(clipped.getchannel("A"), mask))
    return clipped


def draw_status_surface(state: str, frame: int, count: int) -> Image.Image:
    phase = frame / count
    colors = palette(state, phase)
    width = TILE_WIDTH * SCALE
    height = TILE_HEIGHT * SCALE
    radius = 18 * SCALE
    mask = rounded_mask((width, height), radius)

    tile = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    glow = rounded_mask((width, height), radius)
    glow_layer = Image.new("RGBA", (width, height), rgba(colors["accent"], 70))
    glow_layer.putalpha(glow.filter(ImageFilter.GaussianBlur(10 * SCALE)))
    tile.alpha_composite(glow_layer)

    body = diagonal_gradient((width, height), colors["top"], colors["bottom"], colors["accent"], phase)
    body.putalpha(mask)
    tile.alpha_composite(body)

    detail = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(detail)
    inset = 9 * SCALE
    inner = (inset, inset, width - inset, height - inset)

    breath = 0.5 + 0.5 * math.sin(phase * math.tau)
    draw.rounded_rectangle(inner, radius=12 * SCALE, outline=rgba(colors["rim"], 96 + round(80 * breath)), width=2 * SCALE)
    draw.rounded_rectangle(
        (17 * SCALE, 18 * SCALE, width - 17 * SCALE, height - 17 * SCALE),
        radius=10 * SCALE,
        outline=rgba("#07151f", 118),
        width=1 * SCALE,
    )
    draw.line((18 * SCALE, height - 19 * SCALE, width - 18 * SCALE, height - 19 * SCALE), fill=rgba(colors["accent"], 160), width=3 * SCALE)

    if state == "idle":
        draw.ellipse(
            (38 * SCALE, 30 * SCALE, 82 * SCALE, 66 * SCALE),
            fill=rgba(colors["accent"], 28 + round(38 * breath)),
            outline=rgba(colors["accent"], 90),
            width=1 * SCALE,
        )
        draw.rounded_rectangle(
            (25 * SCALE, 70 * SCALE, 95 * SCALE, 76 * SCALE),
            radius=3 * SCALE,
            fill=rgba(colors["second"], 52 + round(38 * breath)),
        )

    elif state in {"running-right", "running-left"}:
        direction = 1 if state == "running-right" else -1
        for index in range(4):
            offset = ((phase + index * 0.24) % 1.0) if direction == 1 else ((1 - phase + index * 0.24) % 1.0)
            x = round((14 + offset * 92) * SCALE)
            draw.rounded_rectangle(
                (x, 20 * SCALE, x + 12 * SCALE, 74 * SCALE),
                radius=5 * SCALE,
                fill=rgba(colors["accent"], 78),
            )
            draw.line((x + 15 * SCALE * direction, 28 * SCALE, x + 27 * SCALE * direction, 44 * SCALE), fill=rgba(colors["second"], 120), width=2 * SCALE)
        draw.rounded_rectangle((22 * SCALE, 77 * SCALE, 98 * SCALE, 84 * SCALE), radius=3 * SCALE, fill=rgba(colors["second"], 70))

    elif state == "waving":
        fold = 22 + round(8 * breath)
        draw.polygon(
            [
                (width - fold * SCALE, 0),
                (width, 0),
                (width, fold * SCALE),
            ],
            fill=rgba(colors["second"], 180),
        )
        draw.line((width - fold * SCALE, 0, width, fold * SCALE), fill=rgba(colors["rim"], 180), width=2 * SCALE)
        draw.arc((22 * SCALE, 30 * SCALE, 98 * SCALE, 88 * SCALE), start=205, end=330, fill=rgba(colors["accent"], 128), width=4 * SCALE)

    elif state == "jumping":
        fill_top = (67 - round(26 * math.sin(phase * math.pi))) * SCALE
        draw.rounded_rectangle(
            (24 * SCALE, fill_top, 96 * SCALE, 78 * SCALE),
            radius=8 * SCALE,
            fill=rgba(colors["accent"], 76),
        )
        draw.line((36 * SCALE, 28 * SCALE, 84 * SCALE, 28 * SCALE), fill=rgba(colors["rim"], 132), width=2 * SCALE)
        draw.line((40 * SCALE, 36 * SCALE, 80 * SCALE, 36 * SCALE), fill=rgba(colors["second"], 92), width=2 * SCALE)

    elif state == "failed":
        draw.rounded_rectangle(
            (21 * SCALE, 21 * SCALE, 99 * SCALE, 74 * SCALE),
            radius=10 * SCALE,
            fill=rgba(colors["accent"], 50 + round(38 * breath)),
        )
        crack_color = rgba(colors["rim"], 156)
        crack_shift = round(math.sin(phase * math.tau) * 3) * SCALE
        draw.line((37 * SCALE + crack_shift, 20 * SCALE, 54 * SCALE, 42 * SCALE, 48 * SCALE, 62 * SCALE), fill=crack_color, width=2 * SCALE)
        draw.line((75 * SCALE - crack_shift, 23 * SCALE, 65 * SCALE, 46 * SCALE, 79 * SCALE, 69 * SCALE), fill=crack_color, width=2 * SCALE)
        draw.line((25 * SCALE, 78 * SCALE, 95 * SCALE, 78 * SCALE), fill=rgba(colors["second"], 150), width=3 * SCALE)

    elif state == "waiting":
        cx = width // 2
        cy = height // 2
        pulse = round(8 * breath) * SCALE
        draw.ellipse(
            (cx - 21 * SCALE - pulse, cy - 21 * SCALE - pulse, cx + 21 * SCALE + pulse, cy + 21 * SCALE + pulse),
            outline=rgba(colors["accent"], 82),
            width=2 * SCALE,
        )
        draw.ellipse((cx - 16 * SCALE, cy - 16 * SCALE, cx + 16 * SCALE, cy + 16 * SCALE), fill=rgba(colors["accent"], 68))
        draw.rounded_rectangle((31 * SCALE, 72 * SCALE, 89 * SCALE, 79 * SCALE), radius=3 * SCALE, fill=rgba(colors["second"], 68))

    elif state == "running":
        for index in range(3):
            wave_phase = phase * math.tau + index * 1.7
            points = []
            for step in range(0, 74, 6):
                x = (23 + step) * SCALE
                y = round((37 + index * 12 + math.sin(step * 0.18 + wave_phase) * 7) * SCALE)
                points.append((x, y))
            draw.line(points, fill=rgba(colors["accent"] if index != 1 else colors["second"], 92 + index * 20), width=3 * SCALE)
        scan = round((18 + phase * 84) * SCALE)
        draw.line((scan, 15 * SCALE, scan - 14 * SCALE, 83 * SCALE), fill=rgba(colors["rim"], 100), width=2 * SCALE)

    elif state == "review":
        scan_y = round((22 + phase * 48) * SCALE)
        draw.rounded_rectangle((21 * SCALE, 23 * SCALE, 99 * SCALE, 72 * SCALE), radius=8 * SCALE, outline=rgba(colors["second"], 126), width=2 * SCALE)
        draw.line((24 * SCALE, scan_y, 96 * SCALE, scan_y), fill=rgba(colors["accent"], 150), width=3 * SCALE)
        for index in range(5):
            x = (30 + index * 14) * SCALE
            top = (35 + (index % 2) * 11) * SCALE
            draw.line((x, top, x + 6 * SCALE, top), fill=rgba(colors["rim"], 150), width=2 * SCALE)
        draw.line((44 * SCALE, 68 * SCALE, 56 * SCALE, 78 * SCALE, 78 * SCALE, 50 * SCALE), fill=rgba(colors["second"], 132), width=3 * SCALE)

    tile.alpha_composite(clip_to(mask, detail))

    outline = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    outline_draw = ImageDraw.Draw(outline)
    outline_draw.rounded_rectangle(
        (1 * SCALE, 1 * SCALE, width - 2 * SCALE, height - 2 * SCALE),
        radius=radius,
        outline=rgba(colors["rim"], 170),
        width=2 * SCALE,
    )
    outline_draw.rounded_rectangle(
        (4 * SCALE, 4 * SCALE, width - 5 * SCALE, height - 5 * SCALE),
        radius=radius - 3 * SCALE,
        outline=rgba("#07121b", 140),
        width=1 * SCALE,
    )
    tile.alpha_composite(outline)

    return tile


def state_transform(state: str, frame: int, count: int) -> tuple[float, int, int, float, float]:
    phase = frame / count
    if state == "idle":
        drift = frame - (count - 1) / 2
        return math.sin(phase * math.tau) * 1.2 + drift * 0.18, round(drift * 0.5), round(math.sin(phase * math.tau) * 3), 1.0, 1.0
    if state == "running-right":
        return -4.0 + math.sin(phase * math.tau) * 1.5, round(math.sin(phase * math.tau) * 6), 0, 1.0, 1.0
    if state == "running-left":
        return 4.0 + math.sin(phase * math.tau) * 1.5, round(math.sin(phase * math.tau) * -6), 0, 1.0, 1.0
    if state == "waving":
        return math.sin(phase * math.tau) * 7.5, 0, round(math.cos(phase * math.tau) * 2), 1.0, 1.0
    if state == "jumping":
        jump = math.sin(phase * math.pi)
        drift = frame - (count - 1) / 2
        return drift * 1.1, round(drift * 0.8), -round(jump * 24), 1.0 + jump * 0.04, 1.0 - jump * 0.06
    if state == "failed":
        return math.sin(phase * math.tau * 2) * 2.2, round(math.sin(phase * math.tau * 3) * 3), 2, 1.0, 1.0
    if state == "waiting":
        drift = frame - (count - 1) / 2
        return math.sin(phase * math.tau) * 0.8 + drift * 0.12, round(drift * 0.35), -round((0.5 + 0.5 * math.sin(phase * math.tau)) * 5), 1.0, 1.0
    if state == "running":
        drift = frame - (count - 1) / 2
        return math.sin(phase * math.tau) * 1.6 + drift * 0.18, round(drift * 0.45), round(math.cos(phase * math.tau * 2) * 2), 1.0, 1.0
    if state == "review":
        drift = frame - (count - 1) / 2
        return drift * 0.16, round(drift * 0.5), round(math.sin(phase * math.tau) * 1.5), 1.0, 1.0
    raise ValueError(f"unknown state {state!r}")


def frame_image(state: str, frame: int, count: int) -> Image.Image:
    high = Image.new("RGBA", (CELL_WIDTH * SCALE, CELL_HEIGHT * SCALE), (0, 0, 0, 0))
    tile = draw_status_surface(state, frame, count)
    angle, offset_x, offset_y, scale_x, scale_y = state_transform(state, frame, count)

    if scale_x != 1.0 or scale_y != 1.0:
        tile = tile.resize((round(tile.width * scale_x), round(tile.height * scale_y)), Image.Resampling.LANCZOS)

    rotated = tile.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
    x = (high.width - rotated.width) // 2 + offset_x * SCALE
    y = 56 * SCALE + offset_y * SCALE
    high.alpha_composite(rotated, (x, y))

    return high.resize((CELL_WIDTH, CELL_HEIGHT), Image.Resampling.LANCZOS)


def main() -> None:
    atlas = Image.new("RGBA", (CELL_WIDTH * COLUMNS, CELL_HEIGHT * len(ROWS)), (0, 0, 0, 0))
    for row_index, (state, count) in enumerate(ROWS):
        for frame in range(count):
            atlas.alpha_composite(frame_image(state, frame, count), (frame * CELL_WIDTH, row_index * CELL_HEIGHT))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    atlas.save(OUT, "WEBP", lossless=True, quality=100, method=6)
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
