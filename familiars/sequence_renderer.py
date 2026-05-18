"""Render Familiars sequence recipes to GIF, MP4, and poster outputs."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from .limits import MAX_TOTAL_FRAMES
from .pet_assets import ROOT, display_name, fit_sprite, state_frame


BRAND_LOGO = ROOT / "assets" / "brand" / "zentrik-logo.png"


class SequenceRenderError(ValueError):
    """Raised when a normalized sequence cannot be rendered."""


def hex_rgb(value: str, fallback: str = "#ffffff") -> tuple[int, int, int]:
    raw = value if isinstance(value, str) else fallback
    raw = raw.strip("#")
    if len(raw) != 6:
        raw = fallback.strip("#")
    try:
        return int(raw[0:2], 16), int(raw[2:4], 16), int(raw[4:6], 16)
    except ValueError:
        return hex_rgb(fallback)


def rgba(value: str, alpha: int = 255) -> tuple[int, int, int, int]:
    return (*hex_rgb(value), alpha)


def load_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "",
        "/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    words = text.split()
    if not words:
        return [""]
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if text_size(draw, candidate, font)[0] <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def draw_card(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    text: str,
    font: ImageFont.ImageFont,
    *,
    fill: tuple[int, int, int, int],
    outline: tuple[int, int, int, int],
    text_fill: tuple[int, int, int, int],
    radius: int,
) -> None:
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=max(1, radius // 8))
    max_width = max(1, x1 - x0 - radius * 2)
    lines = wrap_text(draw, text, font, max_width)
    line_heights = [text_size(draw, line, font)[1] for line in lines]
    total_height = sum(line_heights) + max(0, len(lines) - 1) * max(2, radius // 5)
    y = y0 + max(0, (y1 - y0 - total_height) // 2)
    for line, line_height in zip(lines, line_heights):
        width, _height = text_size(draw, line, font)
        draw.text((x0 + (x1 - x0 - width) // 2, y), line, fill=text_fill, font=font)
        y += line_height + max(2, radius // 5)


def draw_background(frame: Image.Image, theme: dict[str, Any], tick: int) -> None:
    draw = ImageDraw.Draw(frame, "RGBA")
    width, height = frame.size
    background = str(theme.get("background", "#07111f"))
    grid = str(theme.get("grid", "#4ea6d8"))
    accent = str(theme.get("accent", "#21e7dc"))
    draw.rectangle((0, 0, width, height), fill=rgba(background, 255))

    grid_size = max(28, round(width / 18))
    offset = round((tick * 0.12) % grid_size)
    for x in range(-offset, width + grid_size, grid_size):
        draw.line((x, 0, x, height), fill=rgba(grid, 58), width=1)
    for y in range(-offset, height + grid_size, grid_size):
        draw.line((0, y, width, y), fill=rgba(grid, 48), width=1)
    draw.line((0, height - 2, width, height - 2), fill=rgba(accent, 210), width=2)


def draw_title(frame: Image.Image, recipe: dict[str, Any], scene: dict[str, Any], theme: dict[str, Any]) -> None:
    draw = ImageDraw.Draw(frame, "RGBA")
    width, height = frame.size
    title = scene.get("title") or recipe["title"]
    subtitle = scene.get("subtitle") or recipe.get("subtitle")
    title_font = load_font(max(20, round(width * 0.048)), bold=True)
    subtitle_font = load_font(max(11, round(width * 0.021)))
    x = round(width * 0.075)
    y = round(height * 0.08)
    draw.text((x, y), str(title), fill=rgba(str(theme.get("text", "#eef5ff")), 245), font=title_font)
    if subtitle:
        draw.text((x + 2, y + round(height * 0.075)), str(subtitle), fill=rgba(str(theme.get("muted", "#9fb2ca")), 230), font=subtitle_font)


def draw_brand(frame: Image.Image, recipe: dict[str, Any], theme: dict[str, Any]) -> None:
    brand = recipe.get("brand", {})
    if not isinstance(brand, dict) or brand.get("mode") == "none":
        return
    draw = ImageDraw.Draw(frame, "RGBA")
    width, height = frame.size
    footer = brand.get("footer")
    if isinstance(footer, str) and footer:
        font = load_font(max(10, round(width * 0.018)), bold=True)
        tw, th = text_size(draw, footer, font)
        draw.text((width - tw - round(width * 0.07), height - th - round(height * 0.055)), footer, fill=rgba(str(theme.get("muted", "#9fb2ca")), 210), font=font)

    if brand.get("logo") == "zentrik" and BRAND_LOGO.is_file():
        with Image.open(BRAND_LOGO) as opened:
            logo = opened.convert("RGBA")
        target_w = round(width * 0.07)
        scale = target_w / logo.width
        logo = logo.resize((target_w, max(1, round(logo.height * scale))), Image.Resampling.LANCZOS)
        if brand.get("watermark") == "subtle":
            alpha = logo.getchannel("A").point(lambda value: round(value * 0.72))
            logo.putalpha(alpha)
        frame.alpha_composite(logo, (width - logo.width - round(width * 0.055), round(height * 0.055)))


def draw_pet(frame: Image.Image, pet_id: str, state: str, tick: int, center: tuple[float, float], target_height: int) -> tuple[int, int, int, int]:
    sprite = fit_sprite(state_frame(pet_id, state, tick), target_height)
    x = round(center[0] - sprite.width / 2)
    y = round(center[1] - sprite.height / 2)
    frame.alpha_composite(sprite, (x, y))
    return x, y, x + sprite.width, y + sprite.height


def draw_spotlight(frame: Image.Image, recipe: dict[str, Any], scene: dict[str, Any], tick: int, beat_index: int) -> None:
    theme = recipe["themeData"]
    draw = ImageDraw.Draw(frame, "RGBA")
    width, height = frame.size
    entry = scene["pets"][0]
    beat = entry["beats"][min(beat_index, len(entry["beats"]) - 1)]
    state = beat["state"]

    spotlight_title = {
        "title": scene.get("title") or entry["title"],
        "subtitle": scene.get("subtitle") or entry.get("subtitle"),
    }
    draw_title(frame, recipe, spotlight_title, theme)
    draw_pet(frame, entry["pet"], state, tick, (width * 0.55, height * 0.58), round(height * 0.48))

    captions = recipe.get("captions", {})
    if captions.get("mode", "card") != "none":
        font = load_font(max(12, round(width * 0.024)), bold=True)
        draw_card(
            draw,
            (
                round(width * 0.075),
                round(height * 0.76),
                round(width * 0.42),
                round(height * 0.87),
            ),
            str(beat["caption"]),
            font,
            fill=rgba(str(theme.get("card", "#dbeafe")), 218),
            outline=rgba(str(theme.get("accent", "#21e7dc")), 110),
            text_fill=rgba(str(theme.get("cardText", "#111827")), 245),
            radius=max(8, round(width * 0.012)),
        )
    state_font = load_font(max(10, round(width * 0.017)), bold=True)
    draw.text((round(width * 0.078), round(height * 0.69)), state, fill=rgba(str(theme.get("muted", "#9fb2ca")), 210), font=state_font)


def draw_comparison(frame: Image.Image, recipe: dict[str, Any], scene: dict[str, Any], tick: int, beat_index: int) -> None:
    theme = recipe["themeData"]
    draw = ImageDraw.Draw(frame, "RGBA")
    width, height = frame.size
    entries = scene["pets"]
    draw_title(frame, recipe, scene, theme)
    columns = len(entries)
    top = height * 0.32
    margin = width * 0.085
    slot_width = (width - margin * 2) / columns
    for index, entry in enumerate(entries):
        beat = entry["beats"][min(beat_index, len(entry["beats"]) - 1)]
        slot_center = margin + slot_width * (index + 0.5)
        target = round(min(height * (0.27 if columns > 4 else 0.34), slot_width * 0.9))
        draw_pet(frame, entry["pet"], beat["state"], tick + index * 2, (slot_center, top + target * 0.55), target)
        name_font = load_font(max(10, round(width * 0.015)), bold=True)
        caption_font = load_font(max(9, round(width * 0.014)))
        name = str(entry.get("title") or display_name(entry["pet"]))
        name_lines = wrap_text(draw, name, name_font, max(52, round(slot_width * 0.84)))[:2]
        y = round(height * 0.67)
        for line in name_lines:
            tw, th = text_size(draw, line, name_font)
            draw.text((round(slot_center - tw / 2), y), line, fill=rgba(str(theme.get("text", "#eef5ff")), 240), font=name_font)
            y += th + 3
        caption = str(beat["caption"])
        lines = wrap_text(draw, caption, caption_font, max(56, round(slot_width * 0.78)))[:2]
        y = max(round(height * 0.735), y + 2)
        for line in lines:
            lw, lh = text_size(draw, line, caption_font)
            draw.text((round(slot_center - lw / 2), y), line, fill=rgba(str(theme.get("muted", "#9fb2ca")), 225), font=caption_font)
            y += lh + 3

    state = entries[0]["beats"][min(beat_index, len(entries[0]["beats"]) - 1)]["state"]
    state_font = load_font(max(10, round(width * 0.017)), bold=True)
    draw_card(
        draw,
        (
            round(width * 0.39),
            round(height * 0.84),
            round(width * 0.61),
            round(height * 0.91),
        ),
        str(state),
        state_font,
        fill=rgba(str(theme.get("card", "#dbeafe")), 198),
        outline=rgba(str(theme.get("accent", "#21e7dc")), 90),
        text_fill=rgba(str(theme.get("cardText", "#111827")), 245),
        radius=max(8, round(width * 0.01)),
    )


def render_scene_frame(recipe: dict[str, Any], scene: dict[str, Any], tick: int, beat_index: int) -> Image.Image:
    frame = Image.new("RGBA", (recipe["width"], recipe["height"]), (0, 0, 0, 0))
    draw_background(frame, recipe["themeData"], tick)
    layout = scene.get("layout", "spotlight")
    if layout == "comparison":
        draw_comparison(frame, recipe, scene, tick, beat_index)
    else:
        draw_spotlight(frame, recipe, scene, tick, beat_index)
    draw_brand(frame, recipe, recipe["themeData"])
    return frame.convert("RGB")


def build_frames(recipe: dict[str, Any]) -> list[Image.Image]:
    fps = int(recipe["fps"])
    schedule: list[tuple[dict[str, Any], int, int]] = []
    total_frames = 0
    for scene in recipe["scenes"]:
        beat_count = max(len(entry["beats"]) for entry in scene["pets"])
        for beat_index in range(beat_count):
            durations = []
            for entry in scene["pets"]:
                beat = entry["beats"][min(beat_index, len(entry["beats"]) - 1)]
                durations.append(float(beat.get("duration", scene["beatSeconds"])))
            frame_count = max(1, round(max(durations) * fps))
            total_frames += frame_count
            if total_frames > MAX_TOTAL_FRAMES:
                raise SequenceRenderError(f"recipe would produce more than {MAX_TOTAL_FRAMES} frames")
            schedule.append((scene, beat_index, frame_count))

    frames: list[Image.Image] = []
    global_tick = 0
    for scene, beat_index, frame_count in schedule:
        for local_tick in range(frame_count):
            frames.append(render_scene_frame(recipe, scene, global_tick + local_tick, beat_index))
        global_tick += frame_count
    if not frames:
        raise SequenceRenderError("recipe produced no frames")
    return frames


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
        raise SequenceRenderError("ffmpeg is required for MP4 output")
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


def output_paths(recipe: dict[str, Any]) -> dict[str, Path]:
    output_dir = Path(recipe["outputs"]["dir"])
    slug = recipe["slug"]
    return {
        "gif": output_dir / f"{slug}.gif",
        "mp4": output_dir / f"{slug}.mp4",
        "poster": output_dir / f"{slug}-poster.png",
    }


def render_outputs(recipe: dict[str, Any]) -> list[Path]:
    frames = build_frames(recipe)
    paths = output_paths(recipe)
    written: list[Path] = []
    for fmt in recipe["outputs"]["formats"]:
        path = paths[fmt]
        if fmt == "gif":
            save_gif(frames, path, int(recipe["fps"]))
        elif fmt == "mp4":
            save_mp4(frames, path, int(recipe["fps"]))
        elif fmt == "poster":
            path.parent.mkdir(parents=True, exist_ok=True)
            frames[0].save(path)
        written.append(path)
    return written


def render_preview_frame(recipe: dict[str, Any]) -> Image.Image:
    return build_frames(recipe)[0]
