#!/usr/bin/env python3
"""Render Familiars showcase GIFs and social videos from committed spritesheets."""

from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Callable

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
PETS = ROOT / "pets"
BRAND_LOGO = ROOT / "assets" / "brand" / "zentrik-logo.png"
SHOWCASE = ROOT / "assets" / "showcase"
CELL_WIDTH = 192
CELL_HEIGHT = 208
ROWS = {
    "idle": (0, 6),
    "running-right": (1, 8),
    "running-left": (2, 8),
    "waving": (3, 4),
    "jumping": (4, 5),
    "failed": (5, 8),
    "waiting": (6, 6),
    "running": (7, 6),
    "review": (8, 6),
}


@dataclass(frozen=True)
class Scene:
    pet_id: str
    state: str
    display: str
    caption: str
    effect: str


@dataclass(frozen=True)
class OutputSpec:
    name: str
    width: int
    height: int
    fps: int
    gif: Path | None
    mp4: Path | None
    poster: Path | None


@dataclass(frozen=True)
class TeamMember:
    pet_id: str
    state: str
    x: float
    y: float
    h: float
    phase: int
    effect: str
    label: str


@dataclass(frozen=True)
class TeamPacing:
    duration_seconds: float
    action_start: float
    action_span: float
    labels_until: float
    burst_center: float
    burst_window: float
    burst_alpha: int
    burst_base_length: float
    burst_extra_length: float
    effect_floor: float
    effect_range: float
    tick_scale: float
    lift_scale: float
    final_from: float


HERO_SCENES = [
    Scene("zentri", "idle", "Zentri", "folded intent", "paper"),
    Scene("signal-heron", "waiting", "Signal Heron", "quiet signal", "zen"),
    Scene("no-knight", "waiting", "No Knight", "scope says no", "shield"),
    Scene("ci-phoenix", "failed", "CI Phoenix", "failure learns", "ash"),
    Scene("merge-mammoth", "running", "Merge Mammoth", "patient merges", "merge"),
    Scene("launch-lantern", "review", "Launch Lantern", "release glow", "glow"),
    Scene("trace-manta", "running", "Trace Manta", "signals in motion", "trace"),
    Scene("design-finch", "review", "Design Finch", "one pixel better", "polish"),
]

HERO_TRANSITIONS = ["paper", "ripple", "stamp", "ash", "merge", "glow", "trace"]

COUNCIL_PETS = {
    "no-knight": ("idle", "No Knight"),
    "signal-heron": ("waiting", "Signal Heron"),
    "backlog-archaeologist": ("review", "Backlog Archaeologist"),
    "priority-sphinx": ("review", "Priority Sphinx"),
    "launch-lantern": ("review", "Launch Lantern"),
    "tradeoff-scale": ("review", "Tradeoff Scale"),
}

KNIGHT_BEATS = [
    {
        "state": "waiting",
        "caption": "decision pause",
        "cards": [("feature?", "left", 0), ("evidence?", "right", 0), ("later", "left", 1)],
    },
    {
        "state": "waving",
        "caption": "polite boundary",
        "cards": [("nice idea", "left", 0), ("not now", "right", 0), ("tradeoff?", "right", 1)],
    },
    {
        "state": "running-right",
        "caption": "carries focus forward",
        "cards": [("scope creep", "left", 0), ("park it", "left", 1), ("core first", "right", 0)],
    },
    {
        "state": "running",
        "caption": "cuts to the point",
        "cards": [("cut", "left", 0), ("keep the spine", "right", 0), ("one job", "right", 1)],
    },
    {
        "state": "review",
        "caption": "asks the useful question",
        "cards": [("why now?", "left", 0), ("what moves?", "right", 0), ("show signal", "left", 1)],
    },
    {
        "state": "failed",
        "caption": "too many asks",
        "cards": [("pile-on", "left", 0), ("reset", "right", 0), ("still no", "right", 1)],
    },
]

KNIGHT_TRANSITIONS = [
    "holds",
    "salutes",
    "marches",
    "cuts",
    "reviews",
    "resets",
]

REEL_DESCRIPTIONS = {
    "hero": "main README reel with broad collection preview",
    "team": "group scene with several pets acting together",
    "team-calm": "slower team scene for calmer pacing",
    "council": "product-review scene with product-folklore pets",
    "knight": "focused No Knight character spotlight",
}

TEAM_MEMBERS = [
    TeamMember("zentri", "idle", 0.17, 0.58, 0.25, 0, "paper", "intent"),
    TeamMember("signal-heron", "waiting", 0.31, 0.58, 0.29, 2, "zen", "signal"),
    TeamMember("no-knight", "idle", 0.47, 0.62, 0.32, 4, "shield", "scope"),
    TeamMember("launch-lantern", "review", 0.61, 0.62, 0.29, 1, "glow", "launch"),
    TeamMember("merge-mammoth", "running", 0.77, 0.63, 0.28, 3, "merge", "merge"),
    TeamMember("ci-phoenix", "failed", 0.26, 0.78, 0.21, 6, "ash", "recover"),
    TeamMember("trace-manta", "running", 0.47, 0.79, 0.22, 5, "trace", "trace"),
    TeamMember("design-finch", "review", 0.68, 0.79, 0.21, 7, "polish", "polish"),
]

TEAM_PACING = {
    "standard": TeamPacing(8.4, 0.29, 0.58, 0.48, 0.66, 0.32, 36, 0.10, 0.055, 0.14, 0.66, 0.74, 0.86, 0.78),
    "calm": TeamPacing(10.2, 0.34, 0.62, 0.56, 0.70, 0.38, 26, 0.075, 0.04, 0.10, 0.48, 0.56, 0.68, 0.82),
}


def load_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "",
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/SFNS.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def load_manifest(pet_id: str) -> dict[str, object]:
    path = PETS / pet_id / "pet.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_atlas(pet_id: str) -> Image.Image:
    manifest = load_manifest(pet_id)
    spritesheet = manifest.get("spritesheetPath")
    if not isinstance(spritesheet, str):
        raise SystemExit(f"{pet_id}: pet.json missing spritesheetPath")
    path = PETS / pet_id / spritesheet
    if not path.is_file():
        raise SystemExit(f"{pet_id}: missing {spritesheet}")
    with Image.open(path) as opened:
        return opened.convert("RGBA")


@lru_cache(maxsize=None)
def state_frames(pet_id: str, state: str) -> tuple[Image.Image, ...]:
    if state not in ROWS:
        raise SystemExit(f"unknown state {state!r}")
    row, count = ROWS[state]
    atlas = load_atlas(pet_id)
    return tuple(
        atlas.crop(
            (
                column * CELL_WIDTH,
                row * CELL_HEIGHT,
                (column + 1) * CELL_WIDTH,
                (row + 1) * CELL_HEIGHT,
            )
        )
        for column in range(count)
    )


def fit_sprite(sprite: Image.Image, target_height: int) -> Image.Image:
    bbox = sprite.getbbox()
    if bbox is None:
        return Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    cropped = sprite.crop(bbox)
    scale = target_height / cropped.height
    width = max(1, round(cropped.width * scale))
    height = max(1, round(cropped.height * scale))
    return cropped.resize((width, height), Image.Resampling.LANCZOS)


def with_opacity(sprite: Image.Image, opacity: float) -> Image.Image:
    output = sprite.copy()
    alpha = output.getchannel("A").point(lambda value: round(value * max(0, min(1, opacity))))
    output.putalpha(alpha)
    return output


def ease(value: float) -> float:
    return value * value * (3 - 2 * value)


def wave(value: float) -> float:
    return math.sin(value * math.tau)


def rgba(hex_color: str, alpha: int) -> tuple[int, int, int, int]:
    value = hex_color.lstrip("#")
    return (int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16), alpha)


def text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


def draw_centered_text(
    draw: ImageDraw.ImageDraw,
    center: tuple[float, float],
    text: str,
    font: ImageFont.ImageFont,
    fill: tuple[int, int, int, int] | str,
) -> None:
    box = draw.textbbox((0, 0), text, font=font)
    draw.text((center[0] - (box[2] - box[0]) / 2, center[1] - (box[3] - box[1]) / 2), text, font=font, fill=fill)


def draw_background(width: int, height: int, tick: int, mood: str = "default") -> Image.Image:
    image = Image.new("RGBA", (width, height), "#091221")
    draw = ImageDraw.Draw(image, "RGBA")
    grid = max(64, round(width / 10))
    offset = (tick * max(1, round(width / 640))) % grid
    grid_alpha = 18 if mood != "council" else 14
    for x in range(-grid + offset, width + grid, grid):
        draw.line((x, 0, x, height), fill=(132, 190, 238, grid_alpha), width=1)
    for y in range(-grid + offset, height + grid, grid):
        draw.line((0, y, width, y), fill=(132, 190, 238, grid_alpha), width=1)

    draw.rectangle((0, 0, width - 1, height - 1), outline=(132, 190, 238, 44), width=1)
    draw.line((0, height - max(3, height // 140), width, height - max(3, height // 140)), fill=(33, 231, 220, 120), width=max(2, width // 320))

    if mood == "council":
        table_y = round(height * 0.69)
        draw.rounded_rectangle(
            (round(width * 0.16), table_y, round(width * 0.84), round(height * 0.86)),
            radius=max(10, width // 50),
            fill=(11, 22, 39, 178),
            outline=(132, 190, 238, 52),
            width=max(1, width // 500),
        )
        draw.line((round(width * 0.21), table_y + 2, round(width * 0.79), table_y + 2), fill=(33, 231, 220, 58), width=max(1, width // 640))
    else:
        for scale, alpha in ((0.07, 30), (0.12, 14)):
            radius = round(width * scale)
            cx = round(width * 0.9)
            cy = round(height * 0.3)
            draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), outline=(19, 191, 233, alpha), width=max(1, width // 320))

    return image


def draw_logo(frame: Image.Image) -> None:
    draw = ImageDraw.Draw(frame, "RGBA")
    width, height = frame.size
    logo_size = max(24, round(width * 0.043))
    padding = max(18, round(width * 0.04))
    x = width - padding - logo_size
    y = max(16, round(height * 0.055))

    if BRAND_LOGO.is_file():
        with Image.open(BRAND_LOGO) as logo:
            mark = logo.convert("RGBA").resize((logo_size, logo_size), Image.Resampling.LANCZOS)
        frame.alpha_composite(mark, (x, y))

    mark_font = load_font(max(10, round(width * 0.017)), bold=True)
    label = "zentrik.ai"
    label_width, _ = text_size(draw, label, mark_font)
    draw.text((x - label_width - round(width * 0.012), y + logo_size * 0.31), label, fill="#c4d2e8", font=mark_font)


def draw_brand_title(draw: ImageDraw.ImageDraw, position: tuple[int, int], title: str, font: ImageFont.ImageFont) -> None:
    if not title.startswith("Familiars"):
        draw.text(position, title, fill="#f8fafc", font=font)
        return

    x, y = position
    cursor = x
    for text, fill in (("Famil", "#f8fafc"), ("ia", "#21e7dc"), ("rs", "#f8fafc")):
        draw.text((cursor, y), text, fill=fill, font=font)
        cursor += text_size(draw, text, font)[0]
    suffix = title[len("Familiars") :]
    if suffix:
        draw.text((cursor, y), suffix, fill="#f8fafc", font=font)


def draw_title(frame: Image.Image, title: str, subtitle: str) -> None:
    draw = ImageDraw.Draw(frame, "RGBA")
    width, _ = frame.size
    title_font = load_font(max(26, round(width * 0.053)), bold=True)
    sub_font = load_font(max(12, round(width * 0.021)))
    left = max(28, round(width * 0.05))
    draw_brand_title(draw, (left, max(22, round(width * 0.035))), title, title_font)
    draw.text((left + 2, max(62, round(width * 0.092))), subtitle, fill="#dbeafe", font=sub_font)


def draw_scene_label(frame: Image.Image, scene: Scene, opacity: float = 1.0) -> None:
    draw = ImageDraw.Draw(frame, "RGBA")
    width, height = frame.size
    name_font = load_font(max(18, round(width * 0.036)), bold=True)
    caption_font = load_font(max(12, round(width * 0.021)))
    alpha = round(255 * max(0, min(1, opacity)))
    x = max(30, round(width * 0.052))
    y = height - max(88, round(height * 0.245))
    draw.text((x, y), scene.display, fill=(248, 250, 252, alpha), font=name_font)
    draw.text((x, y + max(28, round(height * 0.08))), scene.caption, fill=(184, 196, 214, alpha), font=caption_font)


def draw_card(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int, int, int],
    text: str,
    font: ImageFont.ImageFont,
    fill: tuple[int, int, int, int] = (248, 250, 252, 232),
    outline: tuple[int, int, int, int] = (33, 231, 220, 110),
    text_fill: tuple[int, int, int, int] = (17, 24, 39, 255),
) -> None:
    draw.rounded_rectangle(xy, radius=max(6, (xy[2] - xy[0]) // 22), fill=fill, outline=outline, width=max(1, (xy[2] - xy[0]) // 90))
    fitted_font = font
    size = int(getattr(font, "size", 14))
    max_width = max(4, xy[2] - xy[0] - max(8, (xy[2] - xy[0]) // 10))
    max_height = max(4, xy[3] - xy[1] - max(6, (xy[3] - xy[1]) // 5))
    while size > 8:
        text_width, text_height = text_size(draw, text, fitted_font)
        if text_width <= max_width and text_height <= max_height:
            break
        size -= 1
        fitted_font = load_font(size, bold=True)
    draw_centered_text(draw, ((xy[0] + xy[2]) / 2, (xy[1] + xy[3]) / 2), text, fitted_font, text_fill)


def paste_center(base: Image.Image, sprite: Image.Image, center: tuple[float, float]) -> tuple[int, int, int, int]:
    x = round(center[0] - sprite.width / 2)
    y = round(center[1] - sprite.height / 2)
    base.alpha_composite(sprite, (x, y))
    return (x, y, x + sprite.width, y + sprite.height)


def draw_pet(
    frame: Image.Image,
    sprite: Image.Image,
    center: tuple[float, float],
    target_height: int,
    opacity: float = 1.0,
) -> tuple[int, int, int, int]:
    fitted = fit_sprite(sprite, target_height)
    if opacity < 1:
        fitted = with_opacity(fitted, opacity)
    return paste_center(frame, fitted, center)


def sprite_for(pet_id: str, state: str, tick: int) -> Image.Image:
    frames = state_frames(pet_id, state)
    return frames[tick % len(frames)]


def draw_effect(frame: Image.Image, scene: Scene, tick: int) -> None:
    draw = ImageDraw.Draw(frame, "RGBA")
    width, height = frame.size
    cx = round(width * 0.61)
    cy = round(height * 0.54)
    unit = width / 640

    if scene.effect == "paper":
        for i in range(4):
            x = cx - round((72 - i * 24) * unit)
            draw.line((x, cy - round(90 * unit), x + round(62 * unit), cy + round(60 * unit)), fill=(220, 252, 255, 26 + i * 10), width=max(1, round(2 * unit)))
    elif scene.effect == "zen":
        for i in range(3):
            pulse = (tick * 0.08 + i / 3) % 1
            radius = round((38 + 58 * pulse) * unit)
            alpha = round(88 * (1 - pulse))
            draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), outline=(33, 231, 220, alpha), width=max(1, round(2 * unit)))
    elif scene.effect == "shield":
        font = load_font(max(18, round(width * 0.038)), bold=True)
        word = "NO" if tick % 18 < 12 else "LATER"
        draw_card(
            draw,
            (
                round(width * 0.72),
                round(height * 0.33),
                round(width * 0.86),
                round(height * 0.45),
            ),
            word,
            font,
            fill=(255, 242, 203, 238),
            outline=(33, 231, 220, 120),
            text_fill=(17, 24, 39, 255),
        )
    elif scene.effect == "ash":
        for i in range(18):
            px = cx + round(math.sin(tick * 0.4 + i) * 72 * unit)
            py = cy + round(math.cos(tick * 0.23 + i * 1.7) * 38 * unit) - round((tick % 8) * unit)
            color = (244, 114, 35, 70) if i % 3 == 0 else (203, 213, 225, 48)
            r = max(1, round((1 + i % 3) * unit))
            draw.ellipse((px - r, py - r, px + r, py + r), fill=color)
    elif scene.effect == "merge":
        left = round(width * 0.42)
        right = round(width * 0.76)
        mid = round(width * 0.59)
        for offset in (-42, 0, 42):
            y = cy + round(offset * unit)
            draw.line((left, y, mid, cy), fill=(33, 231, 220, 86), width=max(2, round(3 * unit)))
        draw.line((mid, cy, right, cy), fill=(33, 231, 220, 118), width=max(2, round(3 * unit)))
    elif scene.effect == "glow":
        for i in range(5, 0, -1):
            radius = round((22 + i * 18 + abs(wave((tick + i) / 18)) * 6) * unit)
            draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=(250, 204, 21, 10 + i * 4))
    elif scene.effect == "trace":
        for i in range(6):
            y = round(height * (0.36 + i * 0.052))
            shift = round(((tick * 10 + i * 47) % round(width * 0.32)) * unit / max(1, unit))
            draw.line((round(width * 0.43) + shift, y, round(width * 0.56) + shift, y), fill=(33, 231, 220, 55 + i * 7), width=max(1, round(2 * unit)))
    elif scene.effect == "polish":
        for i in range(7):
            x = round(width * 0.47 + i * width * 0.035)
            y = round(height * 0.38 + ((i + tick) % 3) * height * 0.038)
            draw.rectangle((x, y, x + max(4, round(7 * unit)), y + max(4, round(7 * unit))), fill=(33, 231, 220, 90))


def scene_frame(scene: Scene, tick: int, width: int, height: int, title: bool = True) -> Image.Image:
    frame = draw_background(width, height, tick)
    if title:
        draw_title(frame, "Familiars", "Codex pets for agent work")
    draw_logo(frame)
    draw_effect(frame, scene, tick)
    draw_scene_label(frame, scene)
    sprite = sprite_for(scene.pet_id, scene.state, tick)
    bob = wave(tick / 18) * height * 0.014
    target_height = round(height * (0.54 if scene.pet_id != "signal-heron" else 0.58))
    draw_pet(frame, sprite, (width * 0.61, height * 0.57 + bob), target_height)
    return frame.convert("RGB")


def draw_transition_overlay(draw: ImageDraw.ImageDraw, style: str, width: int, height: int, amount: float, tick: int) -> None:
    unit = width / 640
    if style == "paper":
        crease_x = round(width * (0.32 + 0.38 * amount))
        draw.polygon(
            [(crease_x - round(34 * unit), 0), (crease_x + round(10 * unit), 0), (crease_x - round(110 * unit), height), (crease_x - round(154 * unit), height)],
            fill=(33, 231, 220, 34),
        )
        draw.line((crease_x + round(10 * unit), 0, crease_x - round(110 * unit), height), fill=(33, 231, 220, 168), width=max(2, round(4 * unit)))
    elif style == "ripple":
        cx, cy = width * 0.61, height * 0.55
        for i in range(5):
            radius = round((30 + amount * 250 + i * 32) * unit)
            alpha = max(0, round(112 * (1 - amount) - i * 12))
            draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), outline=(33, 231, 220, alpha), width=max(1, round(3 * unit)))
    elif style == "stamp":
        font = load_font(max(54, round(width * 0.13)), bold=True)
        stamp = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        stamp_draw = ImageDraw.Draw(stamp, "RGBA")
        box_w, box_h = text_size(stamp_draw, "NO", font)
        x = width * (0.16 + 0.4 * amount)
        y = height * (0.25 + 0.09 * math.sin(amount * math.pi))
        stamp_draw.rounded_rectangle(
            (round(x - box_w * 0.28), round(y - box_h * 0.08), round(x + box_w * 1.2), round(y + box_h * 1.18)),
            radius=max(8, round(14 * unit)),
            outline=(248, 113, 113, 150),
            width=max(2, round(5 * unit)),
        )
        stamp_draw.text((x, y), "NO", font=font, fill=(248, 113, 113, 158))
        draw.bitmap((0, 0), stamp.rotate(-8, resample=Image.Resampling.BICUBIC), fill=None)
    elif style == "ash":
        for i in range(36):
            px = round(width * 0.61 + math.sin(i * 2.1 + tick) * width * 0.17 * amount)
            py = round(height * 0.55 + math.cos(i * 1.4 + tick) * height * 0.13 * amount + height * 0.18 * amount)
            r = max(1, round((1 + i % 3) * unit))
            draw.ellipse((px - r, py - r, px + r, py + r), fill=(203, 213, 225, max(0, round(110 * (1 - amount)))))
    elif style == "merge":
        left = width * 0.28
        mid = width * (0.44 + 0.26 * amount)
        right = width * 0.85
        for offset in (-height * 0.16, 0, height * 0.16):
            draw.line((left, height * 0.52 + offset, mid, height * 0.52), fill=(33, 231, 220, 90), width=max(2, round(4 * unit)))
        draw.line((mid, height * 0.52, right, height * 0.52), fill=(33, 231, 220, 130), width=max(2, round(4 * unit)))
    elif style == "glow":
        cx, cy = width * 0.62, height * 0.55
        for i in range(7, 0, -1):
            radius = round((i * 24 + amount * 80) * unit)
            draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=(250, 204, 21, max(4, 18 - i)))
    elif style == "trace":
        for i in range(8):
            y = round(height * (0.28 + i * 0.066))
            x = round(width * (0.12 + amount * 0.62 + i * 0.018))
            draw.line((x, y, x + round(width * 0.34), y + round(math.sin(i) * height * 0.02)), fill=(33, 231, 220, 86), width=max(1, round(3 * unit)))


def transition_frame(
    previous: Scene,
    next_scene: Scene,
    previous_sprite: Image.Image,
    next_sprite: Image.Image,
    style: str,
    step: int,
    steps: int,
    width: int,
    height: int,
    tick: int,
) -> Image.Image:
    amount = ease((step + 1) / steps)
    frame = draw_background(width, height, tick)
    draw_title(frame, "Familiars", "Codex pets for agent work")
    draw_logo(frame)
    draw = ImageDraw.Draw(frame, "RGBA")
    draw_transition_overlay(draw, style, width, height, amount, tick)

    y = height * 0.57
    old_x = width * 0.61 - amount * width * 0.31
    new_x = width * 0.61 + (1 - amount) * width * 0.31
    draw_pet(frame, previous_sprite, (old_x, y), round(height * (0.52 - 0.08 * amount)), 1 - amount * 0.7)
    draw_pet(frame, next_sprite, (new_x, y), round(height * (0.44 + 0.08 * amount)), 0.28 + amount * 0.72)
    if amount < 0.52:
        draw_scene_label(frame, previous, max(0.18, 1 - amount * 1.35))
    else:
        draw_scene_label(frame, next_scene, max(0.2, amount))
    return frame.convert("RGB")


def build_hero_frames(width: int, height: int, fps: int) -> list[Image.Image]:
    hold = max(8, round(fps * 0.95))
    transition = max(6, round(fps * 0.62))
    sprites = {scene: state_frames(scene.pet_id, scene.state) for scene in HERO_SCENES}
    frames: list[Image.Image] = []
    for index, scene in enumerate(HERO_SCENES):
        for hold_index in range(hold):
            frames.append(scene_frame(scene, hold_index + len(frames), width, height))
        if index + 1 < len(HERO_SCENES):
            next_scene = HERO_SCENES[index + 1]
            for step in range(transition):
                frames.append(
                    transition_frame(
                        scene,
                        next_scene,
                        sprites[scene][-1],
                        sprites[next_scene][0],
                        HERO_TRANSITIONS[index],
                        step,
                        transition,
                        width,
                        height,
                        len(frames),
                    )
                )
    return frames


def council_sprite(pet_id: str, tick: int) -> Image.Image:
    state, _ = COUNCIL_PETS[pet_id]
    return sprite_for(pet_id, state, tick)


def draw_shield_text(frame: Image.Image, box: tuple[int, int, int, int], text: str, scale: float = 1.0) -> None:
    width = frame.size[0]
    box_width = box[2] - box[0]
    box_height = box[3] - box[1]
    draw = ImageDraw.Draw(frame, "RGBA")
    font = load_font(max(15, round(width * 0.038 * scale)), bold=True)
    cx = (box[0] + box[2]) / 2
    cy = box[1] + (box[3] - box[1]) * 0.56
    plaque_width = box_width * (0.72 if len(text) > 5 else 0.52)
    plaque_height = box_height * 0.19
    draw_card(
        draw,
        (
            round(cx - plaque_width / 2),
            round(cy - plaque_height / 2),
            round(cx + plaque_width / 2),
            round(cy + plaque_height / 2),
        ),
        text,
        font,
        fill=(255, 242, 203, 242),
        outline=(12, 18, 28, 154),
        text_fill=(17, 24, 39, 255),
    )


def draw_council_note(frame: Image.Image, text: str, x: float, y: float, w: float, h: float, emphatic: bool = False) -> None:
    draw = ImageDraw.Draw(frame, "RGBA")
    width, height = frame.size
    font = load_font(max(12, round(width * (0.024 if not emphatic else 0.031))), bold=True)
    draw_card(
        draw,
        (round(x * width), round(y * height), round((x + w) * width), round((y + h) * height)),
        text,
        font,
        fill=(255, 248, 220, 234) if emphatic else (219, 234, 254, 226),
        outline=(33, 231, 220, 105),
        text_fill=(17, 24, 39, 255),
    )


def draw_council_pet(frame: Image.Image, pet_id: str, x: float, y: float, h: float, tick: int, opacity: float = 1.0) -> tuple[int, int, int, int]:
    return draw_pet(frame, council_sprite(pet_id, tick), (frame.size[0] * x, frame.size[1] * y), round(frame.size[1] * h), opacity)


def draw_small_team_member(
    frame: Image.Image,
    pet_id: str,
    state: str,
    x: float,
    y: float,
    h: float,
    tick: int,
    opacity: float = 1.0,
) -> tuple[int, int, int, int]:
    return draw_pet(frame, sprite_for(pet_id, state, tick), (frame.size[0] * x, frame.size[1] * y), round(frame.size[1] * h), opacity)


def draw_team_effect(frame: Image.Image, member: TeamMember, tick: int, intensity: float, motion: float = 1.0) -> None:
    draw = ImageDraw.Draw(frame, "RGBA")
    width, height = frame.size
    unit = width / 640
    cx = width * member.x
    cy = height * member.y
    alpha = round(100 * max(0, min(1, intensity)))
    motion_tick = tick * motion

    if member.effect == "paper":
        for i in range(3):
            draw.line(
                (
                    cx - (30 - i * 12) * unit,
                    cy - 42 * unit,
                    cx + (16 + i * 14) * unit,
                    cy + 34 * unit,
                ),
                fill=(220, 252, 255, max(18, alpha // 2)),
                width=max(1, round(2 * unit)),
            )
    elif member.effect == "zen":
        for i in range(2):
            pulse = (motion_tick * 0.045 + i * 0.5) % 1
            radius = round((24 + pulse * 58) * unit)
            draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), outline=(33, 231, 220, round(alpha * (1 - pulse))), width=max(1, round(2 * unit)))
    elif member.effect == "shield":
        font = load_font(max(12, round(width * 0.025)), bold=True)
        draw_card(
            draw,
            (
                round(cx - 34 * unit),
                round(cy - 88 * unit),
                round(cx + 34 * unit),
                round(cy - 50 * unit),
            ),
            "NO",
            font,
            fill=(255, 242, 203, 210),
            outline=(33, 231, 220, 90),
        )
    elif member.effect == "glow":
        for i in range(4, 0, -1):
            radius = round((15 + i * 13 + abs(wave(motion_tick / 26)) * 6) * unit)
            draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=(250, 204, 21, max(5, alpha // (i + 2))))
    elif member.effect == "merge":
        for offset in (-20, 0, 20):
            draw.line((cx - 52 * unit, cy + offset * unit, cx - 8 * unit, cy), fill=(33, 231, 220, alpha), width=max(1, round(2 * unit)))
        draw.line((cx - 8 * unit, cy, cx + 52 * unit, cy), fill=(33, 231, 220, alpha), width=max(1, round(2 * unit)))
    elif member.effect == "ash":
        for i in range(10):
            px = cx + math.sin(motion_tick * 0.18 + i) * 30 * unit
            py = cy - 20 * unit + math.cos(motion_tick * 0.12 + i * 1.4) * 20 * unit
            r = max(1, round((1 + i % 2) * unit))
            draw.ellipse((px - r, py - r, px + r, py + r), fill=(244, 114, 35, max(18, alpha // 2)))
    elif member.effect == "trace":
        for i in range(4):
            y = cy - 30 * unit + i * 16 * unit
            x = cx - 58 * unit + ((motion_tick * 4 + i * 24) % max(1, round(72 * unit)))
            draw.line((x, y, x + 50 * unit, y), fill=(33, 231, 220, alpha), width=max(1, round(2 * unit)))
    elif member.effect == "polish":
        for i in range(5):
            x = cx - 32 * unit + i * 14 * unit
            y = cy - 46 * unit + ((i + round(motion_tick * 0.42)) % 3) * 8 * unit
            size = max(3, round(5 * unit))
            draw.rectangle((x, y, x + size, y + size), fill=(33, 231, 220, alpha))
    elif member.effect == "riddle":
        font = load_font(max(14, round(width * 0.024)), bold=True)
        draw_centered_text(draw, (cx, cy - 64 * unit), "?", font, (219, 234, 254, alpha + 90))


def draw_team_member(
    frame: Image.Image,
    member: TeamMember,
    tick: int,
    action: float,
    intro: float = 1.0,
    lift_scale: float = 1.0,
) -> tuple[int, int, int, int]:
    width, height = frame.size
    phase_tick = tick + member.phase * 3
    lift = -height * 0.026 * lift_scale * max(0, wave(action * 0.72 + member.phase / 9))
    if member.pet_id in {"signal-heron", "trace-manta"}:
        lift = height * 0.013 * lift_scale * wave(phase_tick / 26)
    elif member.pet_id == "launch-lantern":
        lift = height * 0.007 * lift_scale * wave(phase_tick / 24)
    x = member.x + (1 - intro) * (0.5 - member.x) * 0.18
    y = member.y + lift / height + (1 - intro) * 0.04
    return draw_pet(
        frame,
        sprite_for(member.pet_id, member.state, phase_tick),
        (width * x, height * y),
        round(height * member.h * (0.9 + 0.1 * intro)),
        0.25 + intro * 0.75,
    )


def draw_team_labels(frame: Image.Image, tick: int) -> None:
    draw = ImageDraw.Draw(frame, "RGBA")
    width, height = frame.size
    font = load_font(max(10, round(width * 0.017)), bold=True)
    labels = [
        ("intent", 0.14, 0.35),
        ("signal", 0.3, 0.35),
        ("launch", 0.63, 0.35),
        ("merge", 0.79, 0.36),
    ]
    for index, (label, x, y) in enumerate(labels):
        pulse = 0.75 + 0.25 * abs(wave(tick / 20 + index / 5))
        draw_card(
            draw,
            (
                round(width * x),
                round(height * y),
                round(width * (x + 0.11)),
                round(height * (y + 0.065)),
            ),
            label,
            font,
            fill=(219, 234, 254, round(140 + 60 * pulse)),
            outline=(33, 231, 220, round(55 + 40 * pulse)),
            text_fill=(15, 23, 42, 230),
        )


def team_frame(tick: int, width: int, height: int, fps: int, variant: str = "standard") -> Image.Image:
    pacing = TEAM_PACING[variant]
    scene_tick = round(tick * pacing.tick_scale)
    frame = draw_background(width, height, scene_tick)
    draw_title(frame, "Familiars Team Rally", "one repo, many tiny opinions")
    draw_logo(frame)
    draw = ImageDraw.Draw(frame, "RGBA")
    duration = max(1, round(fps * pacing.duration_seconds))
    progress = tick / max(1, duration - 1)
    action = ease(max(0, min(1, (progress - pacing.action_start) / pacing.action_span)))
    intro = 1.0

    if progress < pacing.labels_until:
        draw_team_labels(frame, scene_tick)
    else:
        font = load_font(max(17, round(width * 0.032)), bold=True)
        card_alpha = ease(max(0, min(1, (progress - pacing.labels_until) / 0.12)))
        draw_card(
            draw,
            (
                round(width * 0.35),
                round(height * 0.28),
                round(width * 0.65),
                round(height * 0.38),
            ),
            "all hands, tiny scale",
            font,
            fill=(255, 248, 220, round(165 + 53 * card_alpha)),
            outline=(33, 231, 220, round(72 + 36 * card_alpha)),
        )

    burst = max(0, 1 - abs(progress - pacing.burst_center) / pacing.burst_window)
    if burst > 0:
        cx, cy = width * 0.5, height * 0.64
        for i in range(9):
            angle = i * math.tau / 9 + scene_tick * 0.012
            length = width * (pacing.burst_base_length + pacing.burst_extra_length * burst)
            draw.line(
                (cx, cy, cx + math.cos(angle) * length, cy + math.sin(angle) * length),
                fill=(33, 231, 220, round(pacing.burst_alpha * burst)),
                width=max(1, round(width * 0.003)),
            )

    for member in TEAM_MEMBERS:
        draw_team_effect(frame, member, scene_tick + member.phase, pacing.effect_floor + pacing.effect_range * action, pacing.tick_scale)

    for member in sorted(TEAM_MEMBERS, key=lambda item: item.y):
        box = draw_team_member(frame, member, scene_tick, action, intro, pacing.lift_scale)
        if member.pet_id == "no-knight" and action > 0.35:
            draw_shield_text(frame, box, "NO", 0.7)

    if progress > pacing.final_from:
        font = load_font(max(13, round(width * 0.023)), bold=True)
        draw_card(
            draw,
            (
                round(width * 0.39),
                round(height * 0.86),
                round(width * 0.61),
                round(height * 0.93),
            ),
            "ship with judgment",
            font,
            fill=(219, 234, 254, 190),
            outline=(33, 231, 220, 82),
        )

    return frame.convert("RGB")


def build_team_frames(width: int, height: int, fps: int) -> list[Image.Image]:
    duration = max(72, round(fps * TEAM_PACING["standard"].duration_seconds))
    return [team_frame(tick, width, height, fps, "standard") for tick in range(duration)]


def build_team_calm_frames(width: int, height: int, fps: int) -> list[Image.Image]:
    duration = max(96, round(fps * TEAM_PACING["calm"].duration_seconds))
    return [team_frame(tick, width, height, fps, "calm") for tick in range(duration)]


def council_frame(beat: int, local_tick: int, width: int, height: int, fps: int) -> Image.Image:
    frame = draw_background(width, height, local_tick + beat * 13, mood="council")
    draw_title(frame, "Product Review Council", "a tiny meeting with opinions")
    draw_logo(frame)
    draw = ImageDraw.Draw(frame, "RGBA")
    unit = width / 640

    beat_progress = local_tick / max(1, round(fps * 1.05))
    beat_progress = max(0, min(1, beat_progress))

    if beat == 0:
        draw_council_note(frame, "new idea", 0.41 - 0.1 * (1 - ease(beat_progress)), 0.35, 0.18, 0.12, True)
        draw_council_note(frame, "one customer said this", 0.17, 0.25, 0.27, 0.1)
        draw_council_pet(frame, "signal-heron", 0.26, 0.58 + 0.02 * wave(local_tick / 18), 0.32, local_tick)
        box = draw_council_pet(frame, "no-knight", 0.66, 0.58, 0.42, local_tick, 0.88)
        draw_shield_text(frame, box, "...")
    elif beat == 1:
        box = draw_council_pet(frame, "no-knight", 0.5, 0.58 + 0.012 * wave(local_tick / 10), 0.54, local_tick)
        draw_shield_text(frame, box, "NO", 1.35)
        draw_council_note(frame, "scope", 0.15, 0.34, 0.15, 0.1)
        draw_council_note(frame, "roadmap", 0.7, 0.32, 0.18, 0.1)
        draw_council_note(frame, "useful friction", 0.39, 0.22, 0.22, 0.09, True)
    elif beat == 2:
        for i in range(4):
            pulse = (beat_progress + i / 4) % 1
            radius = round((42 + pulse * 132) * unit)
            cx, cy = width * 0.34, height * 0.54
            draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), outline=(33, 231, 220, round(90 * (1 - pulse))), width=max(1, round(2 * unit)))
        draw_council_pet(frame, "signal-heron", 0.34, 0.56 + 0.04 * wave(local_tick / 20), 0.5, local_tick)
        box = draw_council_pet(frame, "no-knight", 0.7, 0.61, 0.36, local_tick, 0.94)
        draw_shield_text(frame, box, "SIGNAL?")
        draw_council_note(frame, "not vibes", 0.49, 0.27, 0.2, 0.1)
    elif beat == 3:
        draw_council_pet(frame, "backlog-archaeologist", 0.34, 0.6, 0.48, local_tick)
        draw_council_note(frame, "Q3 2022", 0.48, 0.46 + 0.03 * wave(local_tick / 12), 0.17, 0.1, True)
        draw_council_note(frame, "already tried", 0.58, 0.28, 0.2, 0.1)
        box = draw_council_pet(frame, "no-knight", 0.75, 0.63, 0.32, local_tick, 0.82)
        draw_shield_text(frame, box, "STILL NO")
    elif beat == 4:
        draw_council_pet(frame, "priority-sphinx", 0.32, 0.61, 0.42, local_tick)
        draw_council_pet(frame, "tradeoff-scale", 0.61, 0.6, 0.43, local_tick)
        draw_council_note(frame, "why now?", 0.43, 0.26, 0.18, 0.1, True)
        draw_council_note(frame, "what moves?", 0.62, 0.33, 0.2, 0.1)
        draw.line((width * 0.47, height * 0.46, width * 0.55, height * 0.46), fill=(33, 231, 220, 110), width=max(2, round(3 * unit)))
    else:
        glow = 26 + 18 * abs(wave(local_tick / 18))
        for i in range(5, 0, -1):
            r = round((glow + i * 24) * unit)
            cx, cy = width * 0.51, height * 0.53
            draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(250, 204, 21, 8 + i * 4))
        draw_small_team_member(frame, "signal-heron", "waiting", 0.18, 0.63, 0.28, local_tick)
        draw_small_team_member(frame, "backlog-archaeologist", "review", 0.31, 0.66, 0.28, local_tick + 2)
        draw_small_team_member(frame, "priority-sphinx", "review", 0.43, 0.66, 0.28, local_tick + 4)
        draw_council_pet(frame, "launch-lantern", 0.55, 0.62, 0.36, local_tick)
        draw_small_team_member(frame, "tradeoff-scale", "review", 0.68, 0.66, 0.3, local_tick + 6)
        box = draw_council_pet(frame, "no-knight", 0.82, 0.67, 0.31, local_tick)
        final_word = "OK, BUT WHY?" if local_tick % 18 < 13 else "NO"
        draw_shield_text(frame, box, final_word, 0.78)
        draw_council_note(frame, "ship when clear", 0.39, 0.3, 0.23, 0.09, True)
        draw_council_note(frame, "all opinions present", 0.12, 0.36, 0.25, 0.09)

    return frame.convert("RGB")


def build_council_frames(width: int, height: int, fps: int) -> list[Image.Image]:
    hold = max(10, round(fps * 1.15))
    frames: list[Image.Image] = []
    for beat in range(6):
        for local_tick in range(hold):
            frames.append(council_frame(beat, local_tick, width, height, fps))
    return frames


def draw_knight_lane_card(
    frame: Image.Image,
    text: str,
    side: str,
    slot: int,
    tick: int,
    beat_progress: float,
    emphatic: bool = False,
) -> None:
    draw = ImageDraw.Draw(frame, "RGBA")
    width, height = frame.size
    unit = width / 640
    card_w = width * (0.19 if len(text) <= 9 else 0.23)
    card_h = height * 0.075
    lane_x = width * 0.09 if side == "left" else width * 0.91 - card_w
    y_slots = [height * 0.34, height * 0.49, height * 0.64]
    y = y_slots[slot % len(y_slots)]

    entrance = ease(min(1, 0.35 + beat_progress * 2.0))
    slide = (1 - entrance) * width * 0.04 * (-1 if side == "left" else 1)
    pulse = 0.78 + 0.22 * abs(wave(tick / 18 + slot / 5))
    x0 = round(lane_x + slide)
    y0 = round(y + math.sin(tick * 0.035 + slot) * height * 0.008)
    x1 = round(x0 + card_w)
    y1 = round(y0 + card_h)

    font = load_font(max(11, round(width * (0.019 if not emphatic else 0.022))), bold=True)
    draw_card(
        draw,
        (x0, y0, x1, y1),
        text,
        font,
        fill=(255, 248, 220, round(218 * entrance)) if emphatic else (219, 234, 254, round(198 * entrance)),
        outline=(33, 231, 220, round((62 + 42 * pulse) * entrance)),
        text_fill=(17, 24, 39, round(246 * entrance)),
    )

    # Keep the notes visually connected to the shield while never covering it.
    anchor_x = width * (0.43 if side == "left" else 0.62)
    anchor_y = height * (0.58 + 0.02 * (slot - 1))
    edge_x = x1 if side == "left" else x0
    edge_y = (y0 + y1) / 2
    draw.line(
        (edge_x, edge_y, anchor_x, anchor_y),
        fill=(33, 231, 220, round(50 * entrance)),
        width=max(1, round(1.5 * unit)),
    )


def draw_knight_transition(frame: Image.Image, label: str, tick: int, beat_progress: float) -> None:
    draw = ImageDraw.Draw(frame, "RGBA")
    width, height = frame.size
    unit = width / 640
    alpha = round(82 * (1 - abs(beat_progress - 0.5) * 1.3))
    alpha = max(0, min(82, alpha))
    if alpha <= 0:
        return

    cx = width * 0.52
    cy = height * 0.57
    if label == "marches":
        for offset in (-34, 0, 34):
            draw.line((cx - 155 * unit, cy + offset * unit, cx - 78 * unit, cy + offset * unit), fill=(33, 231, 220, alpha), width=max(1, round(2 * unit)))
    elif label == "cuts":
        draw.line((cx - 150 * unit, cy - 78 * unit, cx - 86 * unit, cy - 28 * unit), fill=(33, 231, 220, alpha), width=max(1, round(3 * unit)))
        draw.line((cx + 86 * unit, cy + 28 * unit, cx + 150 * unit, cy + 78 * unit), fill=(33, 231, 220, alpha), width=max(1, round(3 * unit)))
    elif label == "reviews":
        for i in range(3):
            y = cy - (46 - i * 22) * unit
            draw.line((cx - 164 * unit, y, cx - 92 * unit, y), fill=(33, 231, 220, alpha), width=max(1, round(2 * unit)))
            draw.line((cx + 92 * unit, y, cx + 164 * unit, y), fill=(33, 231, 220, alpha), width=max(1, round(2 * unit)))
    elif label == "resets":
        for i in range(12):
            px = cx + math.sin(tick * 0.27 + i) * 128 * unit
            py = cy + math.cos(tick * 0.19 + i * 1.7) * 54 * unit
            radius = max(1, round((1 + i % 3) * unit))
            draw.ellipse((px - radius, py - radius, px + radius, py + radius), fill=(244, 114, 35, alpha // 2))
    else:
        radius = round((74 + 16 * wave(tick / 20)) * unit)
        draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), outline=(33, 231, 220, alpha), width=max(1, round(2 * unit)))


def knight_frame(tick: int, width: int, height: int, fps: int) -> Image.Image:
    frame = draw_background(width, height, tick)
    draw_title(frame, "No Knight", "the roadmap guardian")
    draw_logo(frame)
    draw = ImageDraw.Draw(frame, "RGBA")

    beat_length = max(8, round(fps * 0.95))
    beat_index = (tick // beat_length) % len(KNIGHT_BEATS)
    local_tick = tick % beat_length
    beat_progress = local_tick / max(1, beat_length - 1)
    beat = KNIGHT_BEATS[beat_index]
    state = str(beat["state"])

    center_x = width * 0.52
    center_y = height * 0.6
    if state == "running-right":
        center_x = width * (0.45 + 0.13 * ease(beat_progress))
    elif state == "failed":
        center_y += height * 0.025 * ease(beat_progress)
    elif state == "waving":
        center_x += width * 0.012 * wave(local_tick / 10)
    elif state == "review":
        center_x += width * 0.006 * wave(local_tick / 18)

    draw_knight_transition(frame, KNIGHT_TRANSITIONS[beat_index], tick, beat_progress)

    for index, (text, side, slot) in enumerate(beat["cards"]):
        draw_knight_lane_card(frame, text, side, int(slot), tick + index * 3, beat_progress, emphatic=index == 0)

    sprite_tick = local_tick
    sprite = sprite_for("no-knight", state, sprite_tick)
    box = draw_pet(frame, sprite, (center_x, center_y), round(height * 0.62))

    # The sprite art already carries the shield word. Do not cover it with a
    # separate plaque; underline it instead so the gag stays readable.
    underline_y = box[1] + (box[3] - box[1]) * 0.66
    draw.line(
        (box[0] + (box[2] - box[0]) * 0.31, underline_y, box[0] + (box[2] - box[0]) * 0.69, underline_y),
        fill=(33, 231, 220, round(88 + 42 * abs(wave(tick / 16)))),
        width=max(2, round(width * 0.004)),
    )

    caption_font = load_font(max(11, round(width * 0.019)), bold=True)
    caption = str(beat["caption"])
    draw_card(
        draw,
        (
            round(width * 0.08),
            round(height * 0.78),
            round(width * 0.27),
            round(height * 0.855),
        ),
        caption,
        caption_font,
        fill=(9, 18, 33, 178),
        outline=(33, 231, 220, 82),
        text_fill=(219, 234, 254, 238),
    )
    return frame.convert("RGB")


def build_knight_frames(width: int, height: int, fps: int) -> list[Image.Image]:
    duration = max(60, round(fps * 0.95) * len(KNIGHT_BEATS))
    return [knight_frame(tick, width, height, fps) for tick in range(duration)]


def save_gif(frames: list[Image.Image], output: Path, fps: int) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        output,
        save_all=True,
        append_images=frames[1:],
        duration=round(1000 / fps),
        loop=0,
        optimize=True,
    )


def save_mp4(frames: list[Image.Image], output: Path, fps: int) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise SystemExit("ffmpeg is required for MP4 output")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)
        for index, frame in enumerate(frames):
            frame.save(temp / f"frame-{index:04d}.png")
        subprocess.run(
            [
                ffmpeg,
                "-y",
                "-framerate",
                str(fps),
                "-i",
                str(temp / "frame-%04d.png"),
                "-vf",
                "format=yuv420p",
                "-c:v",
                "libx264",
                "-crf",
                "24",
                "-movflags",
                "+faststart",
                str(output),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


def write_outputs(spec: OutputSpec, builder: Callable[[int, int, int], list[Image.Image]]) -> None:
    frames = builder(spec.width, spec.height, spec.fps)
    if spec.poster:
        spec.poster.parent.mkdir(parents=True, exist_ok=True)
        frames[0].save(spec.poster)
        print(f"wrote {spec.poster.relative_to(ROOT)}")
    if spec.gif:
        save_gif(frames, spec.gif, spec.fps)
        print(f"wrote {spec.gif.relative_to(ROOT)}")
    if spec.mp4:
        save_mp4(frames, spec.mp4, spec.fps)
        print(f"wrote {spec.mp4.relative_to(ROOT)}")


def expected_outputs() -> list[Path]:
    return [
        SHOWCASE / "familiars-reel-poster.png",
        SHOWCASE / "familiars-reel.gif",
        SHOWCASE / "familiars-reel.mp4",
        SHOWCASE / "team-rally-poster.png",
        SHOWCASE / "team-rally.gif",
        SHOWCASE / "team-rally.mp4",
        SHOWCASE / "team-rally-calm-poster.png",
        SHOWCASE / "team-rally-calm.gif",
        SHOWCASE / "team-rally-calm.mp4",
        SHOWCASE / "product-review-council-poster.png",
        SHOWCASE / "product-review-council.gif",
        SHOWCASE / "product-review-council.mp4",
        SHOWCASE / "no-knight-spotlight-poster.png",
        SHOWCASE / "no-knight-spotlight.gif",
        SHOWCASE / "no-knight-spotlight.mp4",
    ]


def check_outputs() -> None:
    missing = [path.relative_to(ROOT) for path in expected_outputs() if not path.is_file()]
    if missing:
        raise SystemExit("missing showcase assets: " + ", ".join(str(path) for path in missing))
    oversized = [path.relative_to(ROOT) for path in expected_outputs() if path.stat().st_size > 5_000_000]
    if oversized:
        raise SystemExit("showcase assets over 5 MB: " + ", ".join(str(path) for path in oversized))
    print("showcase assets ok")


def render_all(no_gif: bool = False, no_mp4: bool = False) -> None:
    specs = [
        (
            OutputSpec(
                name="hero-gif",
                width=640,
                height=360,
                fps=12,
                gif=None if no_gif else SHOWCASE / "familiars-reel.gif",
                mp4=None,
                poster=SHOWCASE / "familiars-reel-poster.png",
            ),
            build_hero_frames,
        ),
        (
            OutputSpec(
                name="hero-mp4",
                width=1280,
                height=720,
                fps=12,
                gif=None,
                mp4=None if no_mp4 else SHOWCASE / "familiars-reel.mp4",
                poster=None,
            ),
            build_hero_frames,
        ),
        (
            OutputSpec(
                name="council-gif",
                width=640,
                height=360,
                fps=12,
                gif=None if no_gif else SHOWCASE / "product-review-council.gif",
                mp4=None,
                poster=SHOWCASE / "product-review-council-poster.png",
            ),
            build_council_frames,
        ),
        (
            OutputSpec(
                name="council-mp4",
                width=1280,
                height=720,
                fps=12,
                gif=None,
                mp4=None if no_mp4 else SHOWCASE / "product-review-council.mp4",
                poster=None,
            ),
            build_council_frames,
        ),
        (
            OutputSpec(
                name="team-gif",
                width=640,
                height=360,
                fps=12,
                gif=None if no_gif else SHOWCASE / "team-rally.gif",
                mp4=None,
                poster=SHOWCASE / "team-rally-poster.png",
            ),
            build_team_frames,
        ),
        (
            OutputSpec(
                name="team-mp4",
                width=1280,
                height=720,
                fps=12,
                gif=None,
                mp4=None if no_mp4 else SHOWCASE / "team-rally.mp4",
                poster=None,
            ),
            build_team_frames,
        ),
        (
            OutputSpec(
                name="team-calm-gif",
                width=640,
                height=360,
                fps=10,
                gif=None if no_gif else SHOWCASE / "team-rally-calm.gif",
                mp4=None,
                poster=SHOWCASE / "team-rally-calm-poster.png",
            ),
            build_team_calm_frames,
        ),
        (
            OutputSpec(
                name="team-calm-mp4",
                width=1280,
                height=720,
                fps=10,
                gif=None,
                mp4=None if no_mp4 else SHOWCASE / "team-rally-calm.mp4",
                poster=None,
            ),
            build_team_calm_frames,
        ),
        (
            OutputSpec(
                name="knight-gif",
                width=640,
                height=360,
                fps=12,
                gif=None if no_gif else SHOWCASE / "no-knight-spotlight.gif",
                mp4=None,
                poster=SHOWCASE / "no-knight-spotlight-poster.png",
            ),
            build_knight_frames,
        ),
        (
            OutputSpec(
                name="knight-mp4",
                width=1280,
                height=720,
                fps=12,
                gif=None,
                mp4=None if no_mp4 else SHOWCASE / "no-knight-spotlight.mp4",
                poster=None,
            ),
            build_knight_frames,
        ),
    ]
    for spec, builder in specs:
        write_outputs(spec, builder)


def render_named(name: str, no_gif: bool = False, no_mp4: bool = False) -> None:
    mapping: dict[str, tuple[list[OutputSpec], Callable[[int, int, int], list[Image.Image]]]] = {
        "hero": (
            [
                OutputSpec(
                    "hero-gif",
                    640,
                    360,
                    12,
                    None if no_gif else SHOWCASE / "familiars-reel.gif",
                    None,
                    SHOWCASE / "familiars-reel-poster.png",
                ),
                OutputSpec(
                    "hero-mp4",
                    1280,
                    720,
                    12,
                    None,
                    None if no_mp4 else SHOWCASE / "familiars-reel.mp4",
                    None,
                ),
            ],
            build_hero_frames,
        ),
        "council": (
            [
                OutputSpec(
                    "council-gif",
                    640,
                    360,
                    12,
                    None if no_gif else SHOWCASE / "product-review-council.gif",
                    None,
                    SHOWCASE / "product-review-council-poster.png",
                ),
                OutputSpec(
                    "council-mp4",
                    1280,
                    720,
                    12,
                    None,
                    None if no_mp4 else SHOWCASE / "product-review-council.mp4",
                    None,
                ),
            ],
            build_council_frames,
        ),
        "team": (
            [
                OutputSpec(
                    "team-gif",
                    640,
                    360,
                    12,
                    None if no_gif else SHOWCASE / "team-rally.gif",
                    None,
                    SHOWCASE / "team-rally-poster.png",
                ),
                OutputSpec(
                    "team-mp4",
                    1280,
                    720,
                    12,
                    None,
                    None if no_mp4 else SHOWCASE / "team-rally.mp4",
                    None,
                ),
            ],
            build_team_frames,
        ),
        "team-calm": (
            [
                OutputSpec(
                    "team-calm-gif",
                    640,
                    360,
                    10,
                    None if no_gif else SHOWCASE / "team-rally-calm.gif",
                    None,
                    SHOWCASE / "team-rally-calm-poster.png",
                ),
                OutputSpec(
                    "team-calm-mp4",
                    1280,
                    720,
                    10,
                    None,
                    None if no_mp4 else SHOWCASE / "team-rally-calm.mp4",
                    None,
                ),
            ],
            build_team_calm_frames,
        ),
        "knight": (
            [
                OutputSpec(
                    "knight-gif",
                    640,
                    360,
                    12,
                    None if no_gif else SHOWCASE / "no-knight-spotlight.gif",
                    None,
                    SHOWCASE / "no-knight-spotlight-poster.png",
                ),
                OutputSpec(
                    "knight-mp4",
                    1280,
                    720,
                    12,
                    None,
                    None if no_mp4 else SHOWCASE / "no-knight-spotlight.mp4",
                    None,
                ),
            ],
            build_knight_frames,
        ),
    }
    if name not in mapping:
        raise SystemExit(f"unknown reel {name!r}; choose {', '.join(sorted(mapping))}")
    specs, builder = mapping[name]
    for spec in specs:
        write_outputs(spec, builder)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", choices=["hero", "council", "team", "team-calm", "knight"], help="Render one showcase asset family.")
    parser.add_argument("--list", action="store_true", help="List available showcase asset families.")
    parser.add_argument("--check", action="store_true", help="Verify committed showcase assets exist and stay small enough for the repo.")
    parser.add_argument("--no-gif", action="store_true")
    parser.add_argument("--no-mp4", action="store_true")
    args = parser.parse_args()

    if args.list:
        for name, description in REEL_DESCRIPTIONS.items():
            print(f"{name:10} {description}")
        return

    if args.check:
        check_outputs()
        return

    if args.only:
        render_named(args.only, no_gif=args.no_gif, no_mp4=args.no_mp4)
    else:
        render_all(no_gif=args.no_gif, no_mp4=args.no_mp4)


if __name__ == "__main__":
    main()
