#!/usr/bin/env python3
"""Generate deterministic state-instrument familiar spritesheets."""

from __future__ import annotations

import math
from collections.abc import Callable
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
CELL_WIDTH = 192
CELL_HEIGHT = 208
COLUMNS = 8
SCALE = 4

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

GENERATORS: dict[str, Callable[[str, int, int], Image.Image]] = {}


def pet(fn: Callable[[str, int, int], Image.Image]) -> Callable[[str, int, int], Image.Image]:
    GENERATORS[fn.__name__.replace("draw_", "").replace("_", "-")] = fn
    return fn


def rgb(color: str) -> tuple[int, int, int]:
    value = color.strip("#")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


def rgba(color: str, alpha: int = 255) -> tuple[int, int, int, int]:
    return (*rgb(color), alpha)


def mix(a: str, b: str, amount: float) -> tuple[int, int, int]:
    left = rgb(a)
    right = rgb(b)
    amount = max(0.0, min(1.0, amount))
    return tuple(round(left[index] + (right[index] - left[index]) * amount) for index in range(3))


def state_palette(state: str) -> dict[str, str]:
    if state == "failed":
        return {"base": "#3a1222", "accent": "#ff5065", "second": "#ffb34f", "rim": "#ffd6c4"}
    if state == "waiting":
        return {"base": "#242238", "accent": "#ffca5f", "second": "#78dbff", "rim": "#fff0b6"}
    if state == "review":
        return {"base": "#101e39", "accent": "#9bdfff", "second": "#ffffff", "rim": "#e8fbff"}
    if state in {"running", "running-right", "running-left"}:
        return {"base": "#062d35", "accent": "#31f0d4", "second": "#b8ff67", "rim": "#dbfff9"}
    return {"base": "#0b2634", "accent": "#36ece4", "second": "#7fffb4", "rim": "#d9fffb"}


def phase(frame: int, count: int) -> float:
    return frame / count


def wave(value: float) -> float:
    return math.sin(value * math.tau)


def ease(value: float) -> float:
    value = max(0.0, min(1.0, value))
    return value * value * (3 - 2 * value)


def blank(size: tuple[int, int] | None = None) -> Image.Image:
    size = size or (CELL_WIDTH * SCALE, CELL_HEIGHT * SCALE)
    return Image.new("RGBA", size, (0, 0, 0, 0))


def draw_glow(image: Image.Image, mask: Image.Image, color: str, alpha: int, blur: int) -> None:
    glow = Image.new("RGBA", image.size, rgba(color, alpha))
    glow.putalpha(mask.filter(ImageFilter.GaussianBlur(blur * SCALE)))
    image.alpha_composite(glow)


def paste_center(canvas: Image.Image, sprite: Image.Image, cx: int, cy: int, angle: float = 0.0) -> None:
    rotated = sprite.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
    canvas.alpha_composite(rotated, (cx - rotated.width // 2, cy - rotated.height // 2))


def dot(draw: ImageDraw.ImageDraw, center: tuple[float, float], radius: float, fill: tuple[int, int, int, int]) -> None:
    x, y = center
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=fill)


def frame_transform(state: str, frame: int, count: int) -> tuple[int, int, float]:
    p = phase(frame, count)
    drift = frame - (count - 1) / 2
    if state == "jumping":
        return round(drift * 0.8 * SCALE), -round(math.sin(p * math.pi) * 22 * SCALE), drift * 0.7
    if state == "running-right":
        return round((drift * 0.65 + wave(p) * 4) * SCALE), round(wave(p + 0.25) * 2 * SCALE), -4 + wave(p) * 1.5
    if state == "running-left":
        return round((-drift * 0.65 - wave(p) * 4) * SCALE), round(wave(p + 0.25) * 2 * SCALE), 4 + wave(p) * 1.5
    if state == "failed":
        return round(wave(p * 2.5) * 3 * SCALE), round(2 * SCALE), wave(p * 3) * 1.8
    if state == "waiting":
        return round(drift * 0.28 * SCALE), -round((0.5 + 0.5 * wave(p)) * 4 * SCALE), drift * 0.08
    if state == "review":
        return round(drift * 0.3 * SCALE), round(wave(p) * 1.5 * SCALE), drift * 0.08
    if state == "waving":
        return 0, round(wave(p + 0.25) * 2 * SCALE), wave(p) * 4
    return round(drift * 0.2 * SCALE), round(wave(p) * 2 * SCALE), wave(p) * 0.8


def compose(sprite: Image.Image, state: str, frame: int, count: int, y: int = 106) -> Image.Image:
    canvas = blank()
    dx, dy, angle = frame_transform(state, frame, count)
    paste_center(canvas, sprite, CELL_WIDTH * SCALE // 2 + dx, y * SCALE + dy, angle)
    return canvas.resize((CELL_WIDTH, CELL_HEIGHT), Image.Resampling.LANCZOS)


def compass_needle(draw: ImageDraw.ImageDraw, cx: int, cy: int, length: int, angle: float, color: str, alpha: int = 230) -> None:
    tip = (cx + math.cos(angle) * length, cy + math.sin(angle) * length)
    tail = (cx - math.cos(angle) * length * 0.5, cy - math.sin(angle) * length * 0.5)
    side = angle + math.pi / 2
    left = (cx + math.cos(side) * 7 * SCALE, cy + math.sin(side) * 7 * SCALE)
    right = (cx - math.cos(side) * 7 * SCALE, cy - math.sin(side) * 7 * SCALE)
    draw.polygon([tip, left, tail, right], fill=rgba(color, alpha))


@pet
def draw_intent_compass(state: str, frame: int, count: int) -> Image.Image:
    p = phase(frame, count)
    colors = state_palette(state)
    sprite = blank((132 * SCALE, 132 * SCALE))
    draw = ImageDraw.Draw(sprite, "RGBA")
    cx = cy = 66 * SCALE
    r = 52 * SCALE
    breath = 0.5 + 0.5 * wave(p)

    mask = Image.new("L", sprite.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)
    draw_glow(sprite, mask, colors["accent"], 46, 8)

    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=rgba("#171d25", 245), outline=rgba("#f1c66c", 210), width=4 * SCALE)
    draw.ellipse((cx - 43 * SCALE, cy - 43 * SCALE, cx + 43 * SCALE, cy + 43 * SCALE), fill=rgba(colors["base"], 230), outline=rgba(colors["rim"], 110 + round(70 * breath)), width=2 * SCALE)

    for index in range(12):
        angle = index * math.tau / 12
        inner = 31 if index % 3 else 27
        outer = 38
        draw.line(
            (
                cx + math.cos(angle) * inner * SCALE,
                cy + math.sin(angle) * inner * SCALE,
                cx + math.cos(angle) * outer * SCALE,
                cy + math.sin(angle) * outer * SCALE,
            ),
            fill=rgba(colors["rim"], 125 if index % 3 else 180),
            width=1 * SCALE,
        )

    if state == "running-right":
        angle = -0.08 + wave(p) * 0.08
    elif state == "running-left":
        angle = math.pi + 0.08 + wave(p) * 0.08
    elif state == "running":
        angle = p * math.tau * 1.8 - math.pi / 2
    elif state == "waiting":
        angle = -math.pi / 2 + wave(p * 2) * 0.55
    elif state == "failed":
        angle = -math.pi / 2 + wave(p * 3) * 1.0
    elif state == "review":
        angle = -math.pi / 4 + ease(p) * math.pi / 2
    elif state == "waving":
        angle = -math.pi / 2 + wave(p) * 0.75
    else:
        angle = -math.pi / 2 + wave(p) * 0.12

    if state == "failed":
        compass_needle(draw, cx - 4 * SCALE, cy, 35 * SCALE, angle - 0.42, colors["accent"], 210)
        compass_needle(draw, cx + 4 * SCALE, cy, 32 * SCALE, angle + 0.42, colors["second"], 170)
        draw.line((cx - 28 * SCALE, cy - 22 * SCALE, cx - 7 * SCALE, cy, cx - 18 * SCALE, cy + 25 * SCALE), fill=rgba(colors["rim"], 150), width=2 * SCALE)
    else:
        compass_needle(draw, cx, cy, 41 * SCALE, angle, colors["accent"], 230)
        compass_needle(draw, cx, cy, 24 * SCALE, angle + math.pi, colors["second"], 170)

    if state == "review":
        scan = round((cy - 28 * SCALE) + p * 55 * SCALE)
        draw.line((cx - 32 * SCALE, scan, cx + 32 * SCALE, scan), fill=rgba(colors["second"], 170), width=2 * SCALE)
    if state == "waiting":
        draw.arc((cx - 31 * SCALE, cy - 31 * SCALE, cx + 31 * SCALE, cy + 31 * SCALE), 210, 330, fill=rgba(colors["accent"], 165), width=3 * SCALE)
    if state == "jumping":
        dot(draw, (cx, cy), (7 + breath * 3) * SCALE, rgba(colors["second"], 150))
    else:
        dot(draw, (cx, cy), 6 * SCALE, rgba(colors["rim"], 210))

    return compose(sprite, state, frame, count, y=106)


@pet
def draw_thread_totem(state: str, frame: int, count: int) -> Image.Image:
    p = phase(frame, count)
    colors = state_palette(state)
    sprite = blank((128 * SCALE, 170 * SCALE))
    draw = ImageDraw.Draw(sprite, "RGBA")
    cx = 64 * SCALE
    top = 10 * SCALE
    bottom = 157 * SCALE
    breath = 0.5 + 0.5 * wave(p)

    cord_shift = round(wave(p) * 6 * SCALE)
    if state == "failed":
        cord_points = [(cx, top), (cx - 12 * SCALE, 58 * SCALE), (cx + 14 * SCALE, 98 * SCALE), (cx - 5 * SCALE, bottom)]
    else:
        cord_points = [(cx + cord_shift // 3, top), (cx - cord_shift // 2, 62 * SCALE), (cx + cord_shift // 2, 110 * SCALE), (cx, bottom)]
    draw.line(cord_points, fill=rgba("#06131c", 210), width=7 * SCALE, joint="curve")
    draw.line(cord_points, fill=rgba(colors["rim"], 190), width=4 * SCALE, joint="curve")

    bead_base = [25, 56, 87, 118, 148]
    for index, y_base in enumerate(bead_base):
        local = (p + index * 0.15) % 1
        x = cx + round(wave(local) * (4 + index % 2) * SCALE)
        y = y_base * SCALE
        radius = (14 + (index % 2) * 3) * SCALE
        fill = colors["accent"] if index in {1, 3} else colors["base"]
        if state == "running":
            y = (25 + ((y_base - 25 - p * 48) % 123)) * SCALE
            fill = colors["second"] if index == frame % 5 else colors["accent"]
        elif state == "waiting" and index == 2:
            radius = round((18 + breath * 4) * SCALE)
            fill = colors["accent"]
        elif state == "failed" and index == 3:
            x += round(wave(p * 4) * 11 * SCALE)
            fill = colors["accent"]
        elif state == "review":
            x = cx
            fill = colors["second"] if index == frame % 5 else colors["accent"]
        elif state == "running-right":
            x += round((index - 2) * 3 * SCALE + 11 * wave(p + index * 0.08) * SCALE)
        elif state == "running-left":
            x -= round((index - 2) * 3 * SCALE + 11 * wave(p + index * 0.08) * SCALE)
        elif state == "waving" and index == 0:
            x += round(16 * wave(p) * SCALE)

        draw.ellipse((x - radius - 2 * SCALE, y - radius - 2 * SCALE, x + radius + 2 * SCALE, y + radius + 2 * SCALE), fill=rgba("#07131c", 170))
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=rgba(fill, 235), outline=rgba(colors["rim"], 210), width=2 * SCALE)
        dot(draw, (x - radius * 0.35, y - radius * 0.35), radius * 0.2, rgba("#ffffff", 80))

    if state == "failed":
        draw.line((cx - 26 * SCALE, 88 * SCALE, cx + 26 * SCALE, 104 * SCALE), fill=rgba(colors["second"], 190), width=4 * SCALE)
    if state == "review":
        draw.rounded_rectangle((cx - 29 * SCALE, 151 * SCALE, cx + 29 * SCALE, 159 * SCALE), radius=4 * SCALE, fill=rgba(colors["second"], 120))

    return compose(sprite, state, frame, count, y=108)


@pet
def draw_pocket_oracle(state: str, frame: int, count: int) -> Image.Image:
    p = phase(frame, count)
    colors = state_palette(state)
    sprite = blank((120 * SCALE, 140 * SCALE))
    draw = ImageDraw.Draw(sprite, "RGBA")
    cx = 60 * SCALE
    cy = 70 * SCALE
    breath = 0.5 + 0.5 * wave(p)

    body = (18 * SCALE, 10 * SCALE, 102 * SCALE, 130 * SCALE)
    mask = Image.new("L", sprite.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle(body, radius=18 * SCALE, fill=255)
    draw_glow(sprite, mask, colors["accent"], 45, 9)

    draw.rounded_rectangle(body, radius=18 * SCALE, fill=rgba("#151922", 245), outline=rgba("#66768a", 210), width=3 * SCALE)
    draw.rounded_rectangle((27 * SCALE, 20 * SCALE, 93 * SCALE, 120 * SCALE), radius=13 * SCALE, fill=rgba(colors["base"], 230), outline=rgba(colors["rim"], 120 + round(60 * breath)), width=2 * SCALE)

    aperture = 21 + (7 * breath)
    if state == "waiting":
        aperture = 31 + 5 * breath
    elif state == "failed":
        aperture = 18 + 3 * wave(p * 3)
    elif state == "review":
        aperture = 24

    draw.ellipse(
        (cx - aperture * SCALE, cy - aperture * SCALE, cx + aperture * SCALE, cy + aperture * SCALE),
        fill=rgba(colors["accent"], 58 + round(50 * breath)),
        outline=rgba(colors["rim"], 170),
        width=2 * SCALE,
    )

    if state in {"running", "running-right", "running-left"}:
        direction = 1 if state != "running-left" else -1
        for index in range(5):
            angle = p * math.tau * direction + index * math.tau / 5
            x = cx + math.cos(angle) * 25 * SCALE
            y = cy + math.sin(angle) * 25 * SCALE
            dot(draw, (x, y), (3 + index % 2) * SCALE, rgba(colors["second"], 115))
    elif state == "waving":
        fold = (18 + 5 * breath) * SCALE
        draw.polygon([(102 * SCALE, 10 * SCALE), (102 * SCALE, 10 * SCALE + fold), (102 * SCALE - fold, 10 * SCALE)], fill=rgba(colors["second"], 180))
    elif state == "jumping":
        draw.arc((cx - 31 * SCALE, cy - 35 * SCALE, cx + 31 * SCALE, cy + 35 * SCALE), 25, 155, fill=rgba(colors["second"], 145), width=3 * SCALE)
    elif state == "failed":
        draw.line((44 * SCALE, 39 * SCALE, 55 * SCALE, 62 * SCALE, 48 * SCALE, 91 * SCALE), fill=rgba(colors["rim"], 160), width=2 * SCALE)
        draw.line((72 * SCALE, 41 * SCALE, 64 * SCALE, 70 * SCALE, 78 * SCALE, 103 * SCALE), fill=rgba(colors["second"], 130), width=2 * SCALE)
    elif state == "waiting":
        draw.arc((cx - 34 * SCALE, cy - 34 * SCALE, cx + 34 * SCALE, cy + 34 * SCALE), 198, 342, fill=rgba(colors["accent"], 170), width=3 * SCALE)
    elif state == "review":
        scan = round((42 + p * 56) * SCALE)
        draw.line((34 * SCALE, scan, 86 * SCALE, scan), fill=rgba(colors["second"], 175), width=2 * SCALE)
        for index in range(3):
            y = (47 + index * 18) * SCALE
            draw.line((41 * SCALE, y, 52 * SCALE, y), fill=rgba(colors["rim"], 150), width=2 * SCALE)

    return compose(sprite, state, frame, count, y=108)


@pet
def draw_loop_loom(state: str, frame: int, count: int) -> Image.Image:
    p = phase(frame, count)
    colors = state_palette(state)
    sprite = blank((136 * SCALE, 128 * SCALE))
    draw = ImageDraw.Draw(sprite, "RGBA")
    breath = 0.5 + 0.5 * wave(p)

    left = 22 * SCALE
    right = 114 * SCALE
    top = 25 * SCALE
    bottom = 104 * SCALE
    draw.rounded_rectangle((left, top, right, bottom), radius=10 * SCALE, outline=rgba("#d5b36f", 220), width=4 * SCALE)
    draw.rounded_rectangle((left + 10 * SCALE, top + 9 * SCALE, right - 10 * SCALE, bottom - 9 * SCALE), radius=8 * SCALE, fill=rgba(colors["base"], 220), outline=rgba(colors["rim"], 130), width=2 * SCALE)

    for index in range(5):
        x = (38 + index * 14) * SCALE
        sway = wave(p + index * 0.13) * 4 * SCALE
        if state == "failed" and index == 2:
            draw.line((x, top + 14 * SCALE, x + 7 * SCALE, 62 * SCALE, x - 6 * SCALE, bottom - 12 * SCALE), fill=rgba(colors["accent"], 190), width=2 * SCALE)
        else:
            draw.line((x + sway * 0.12, top + 12 * SCALE, x - sway * 0.12, bottom - 12 * SCALE), fill=rgba(colors["rim"], 112), width=1 * SCALE)

    if state in {"running-right", "running-left", "running"}:
        direction = 1 if state != "running-left" else -1
        shuttle_x = (34 + ((p if direction == 1 else 1 - p) * 64)) * SCALE
    elif state == "waiting":
        shuttle_x = (33 + breath * 7) * SCALE
    elif state == "review":
        shuttle_x = 82 * SCALE
    elif state == "failed":
        shuttle_x = (66 + wave(p * 3) * 5) * SCALE
    else:
        shuttle_x = (68 + wave(p) * 8) * SCALE

    for index in range(4):
        y = (44 + index * 13) * SCALE
        offset = wave(p + index * 0.25) * 5 * SCALE
        thread_color = colors["accent"] if index % 2 else colors["second"]
        draw.line((left + 17 * SCALE, y, right - 17 * SCALE, y + offset * 0.12), fill=rgba(thread_color, 100 + index * 18), width=2 * SCALE)

    if state == "failed":
        knot_cx, knot_cy = 67 * SCALE, 72 * SCALE
        draw.ellipse((knot_cx - 10 * SCALE, knot_cy - 8 * SCALE, knot_cx + 10 * SCALE, knot_cy + 8 * SCALE), fill=rgba(colors["accent"], 190), outline=rgba(colors["second"], 160), width=2 * SCALE)
    elif state == "review":
        draw.rounded_rectangle((42 * SCALE, 67 * SCALE, 94 * SCALE, 78 * SCALE), radius=4 * SCALE, fill=rgba(colors["second"], 80), outline=rgba(colors["rim"], 160), width=1 * SCALE)
    else:
        draw.rounded_rectangle((shuttle_x - 14 * SCALE, 61 * SCALE, shuttle_x + 14 * SCALE, 75 * SCALE), radius=7 * SCALE, fill=rgba(colors["accent"], 220), outline=rgba(colors["rim"], 190), width=2 * SCALE)

    if state == "waving":
        draw.arc((82 * SCALE, 21 * SCALE, 118 * SCALE, 61 * SCALE), 205, 345, fill=rgba(colors["second"], 155), width=3 * SCALE)
    if state == "jumping":
        draw.line((47 * SCALE, 39 * SCALE, 89 * SCALE, 39 * SCALE), fill=rgba(colors["second"], 135 + round(40 * breath)), width=3 * SCALE)

    return compose(sprite, state, frame, count, y=108)


@pet
def draw_tide_stone(state: str, frame: int, count: int) -> Image.Image:
    p = phase(frame, count)
    colors = state_palette(state)
    sprite = blank((132 * SCALE, 118 * SCALE))
    draw = ImageDraw.Draw(sprite, "RGBA")
    cx = 66 * SCALE
    cy = 60 * SCALE
    breath = 0.5 + 0.5 * wave(p)

    mask = Image.new("L", sprite.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((17 * SCALE, 12 * SCALE, 115 * SCALE, 106 * SCALE), fill=255)
    draw_glow(sprite, mask, colors["accent"], 42, 10)
    draw.ellipse((17 * SCALE, 12 * SCALE, 115 * SCALE, 106 * SCALE), fill=rgba("#151d25", 245), outline=rgba(colors["rim"], 170), width=3 * SCALE)
    draw.ellipse((27 * SCALE, 23 * SCALE, 105 * SCALE, 97 * SCALE), fill=rgba(colors["base"], 235), outline=rgba("#0b1118", 145), width=2 * SCALE)

    liquid = Image.new("RGBA", sprite.size, (0, 0, 0, 0))
    liquid_draw = ImageDraw.Draw(liquid, "RGBA")
    if state == "waiting":
        level = 68 - round(breath * 12)
        color = colors["accent"]
    elif state == "failed":
        level = 77 + round(wave(p * 2) * 6)
        color = colors["accent"]
    elif state == "review":
        level = 57
        color = colors["second"]
    elif state in {"running", "running-right", "running-left"}:
        level = 60 + round(wave(p) * 10)
        color = colors["accent"]
    else:
        level = 65 + round(wave(p) * 6)
        color = colors["accent"]

    points = [(26 * SCALE, 99 * SCALE)]
    for x in range(26, 107, 6):
        y = (level + math.sin((x / 13) + p * math.tau * (1.4 if state == "running" else 0.7)) * 7) * SCALE
        if state == "running-right":
            y += math.sin((x / 10) - p * math.tau * 1.6) * 6 * SCALE
        elif state == "running-left":
            y += math.sin((x / 10) + p * math.tau * 1.6) * 6 * SCALE
        points.append((x * SCALE, y))
    points.append((106 * SCALE, 99 * SCALE))
    liquid_draw.polygon(points, fill=rgba(color, 105 if state != "failed" else 155))
    liquid.putalpha(Image.composite(liquid.getchannel("A"), Image.new("L", sprite.size, 0), mask))
    sprite.alpha_composite(liquid)

    if state == "failed":
        draw.line((50 * SCALE, 31 * SCALE, 62 * SCALE, 52 * SCALE, 55 * SCALE, 82 * SCALE), fill=rgba(colors["rim"], 165), width=2 * SCALE)
        draw.arc((36 * SCALE, 37 * SCALE, 96 * SCALE, 90 * SCALE), 190, 345, fill=rgba(colors["second"], 155), width=3 * SCALE)
    elif state == "waiting":
        draw.ellipse((cx - 19 * SCALE, cy - 19 * SCALE, cx + 19 * SCALE, cy + 19 * SCALE), outline=rgba(colors["accent"], 105 + round(50 * breath)), width=3 * SCALE)
    elif state == "review":
        scan = (35 + p * 54) * SCALE
        draw.line((38 * SCALE, scan, 94 * SCALE, scan), fill=rgba(colors["accent"], 170), width=2 * SCALE)
        draw.arc((40 * SCALE, 35 * SCALE, 92 * SCALE, 85 * SCALE), 205, 335, fill=rgba(colors["second"], 130), width=3 * SCALE)
    elif state == "waving":
        draw.arc((70 * SCALE, 30 * SCALE, 102 * SCALE, 78 * SCALE), 210, 345, fill=rgba(colors["second"], 150), width=3 * SCALE)
    elif state == "jumping":
        draw.ellipse((cx - 11 * SCALE, cy - 30 * SCALE, cx + 11 * SCALE, cy - 8 * SCALE), fill=rgba(colors["second"], 70 + round(60 * breath)))
    else:
        dot(draw, (47 * SCALE, 38 * SCALE), (5 + breath * 2) * SCALE, rgba("#ffffff", 70))

    return compose(sprite, state, frame, count, y=108)


def build_atlas(pet_id: str) -> None:
    generator = GENERATORS[pet_id]
    atlas = blank((CELL_WIDTH * COLUMNS, CELL_HEIGHT * len(ROWS)))
    for row_index, (state, count) in enumerate(ROWS):
        for frame in range(count):
            atlas.alpha_composite(generator(state, frame, count), (frame * CELL_WIDTH, row_index * CELL_HEIGHT))

    out = ROOT / "pets" / pet_id / "spritesheet.webp"
    out.parent.mkdir(parents=True, exist_ok=True)
    atlas.save(out, "WEBP", lossless=True, quality=100, method=6)
    print(f"wrote {out.relative_to(ROOT)}")


def main() -> None:
    for pet_id in sorted(GENERATORS):
        build_atlas(pet_id)


if __name__ == "__main__":
    main()
