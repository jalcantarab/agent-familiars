#!/usr/bin/env python3
"""Render compact animated README chooser cards from committed spritesheets."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from familiars.pet_assets import STATE_FRAME_COUNTS, fit_sprite, state_frame  # noqa: E402


OUT_DIR = ROOT / "assets" / "readme"
CARD_WIDTH = 180
CARD_HEIGHT = 130
MAX_CARD_BYTES = 140_000
FRAME_DURATION_MS = 180


@dataclass(frozen=True)
class CardSpec:
    pet_id: str
    state: str
    target_height: int
    center_x: int = CARD_WIDTH // 2
    center_y: int = 73
    tick_offset: int = 0


CARDS = (
    CardSpec("signal-heron", "waiting", 116, center_y=76),
    CardSpec("merge-mammoth", "running", 108, center_y=77, tick_offset=1),
    CardSpec("signal-surface", "idle", 96, center_y=72),
    CardSpec("no-knight", "idle", 112, center_y=75),
    CardSpec("ci-phoenix", "running", 110, center_y=75, tick_offset=2),
    CardSpec("intent-compass", "review", 112, center_y=72),
)


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def card_path(spec: CardSpec) -> Path:
    return OUT_DIR / f"{spec.pet_id}.gif"


def draw_card_background(tick: int) -> Image.Image:
    frame = Image.new("RGB", (CARD_WIDTH, CARD_HEIGHT), "#07111f")
    draw = ImageDraw.Draw(frame, "RGBA")
    grid = (103, 183, 238, 68)
    accent = (33, 231, 220, 225)
    grid_size = 22
    offset = round((tick * 0.18) % grid_size)
    for x in range(-offset, CARD_WIDTH + grid_size, grid_size):
        draw.line((x, 0, x, CARD_HEIGHT), fill=grid, width=1)
    for y in range(-offset, CARD_HEIGHT + grid_size, grid_size):
        draw.line((0, y, CARD_WIDTH, y), fill=grid, width=1)
    draw.rectangle((0, 0, CARD_WIDTH - 1, CARD_HEIGHT - 1), outline=(103, 183, 238, 105), width=1)
    draw.line((0, CARD_HEIGHT - 3, CARD_WIDTH, CARD_HEIGHT - 3), fill=accent, width=3)
    return frame.convert("RGBA")


def render_frame(spec: CardSpec, tick: int) -> Image.Image:
    frame = draw_card_background(tick)
    sprite = fit_sprite(state_frame(spec.pet_id, spec.state, tick + spec.tick_offset), spec.target_height)
    x = round(spec.center_x - sprite.width / 2)
    y = round(spec.center_y - sprite.height / 2)
    frame.alpha_composite(sprite, (x, y))
    return frame.convert("RGB")


def render_card(spec: CardSpec) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frame_count = STATE_FRAME_COUNTS[spec.state]
    frames = [render_frame(spec, tick) for tick in range(frame_count)]
    output = card_path(spec)
    frames[0].save(
        output,
        save_all=True,
        append_images=frames[1:],
        duration=FRAME_DURATION_MS,
        loop=0,
        optimize=True,
        disposal=2,
    )
    print(f"wrote {output.relative_to(ROOT)} ({output.stat().st_size:,} bytes)")


def check_card(spec: CardSpec) -> list[str]:
    errors: list[str] = []
    path = card_path(spec)
    if not path.is_file():
        return [f"missing {path.relative_to(ROOT)}"]
    if path.stat().st_size > MAX_CARD_BYTES:
        errors.append(
            f"{path.relative_to(ROOT)} is {path.stat().st_size:,} bytes; "
            f"keep it under {MAX_CARD_BYTES:,}"
        )
    try:
        with Image.open(path) as image:
            if image.size != (CARD_WIDTH, CARD_HEIGHT):
                errors.append(f"{path.relative_to(ROOT)} has size {image.size}, expected {(CARD_WIDTH, CARD_HEIGHT)}")
            expected_frames = STATE_FRAME_COUNTS[spec.state]
            actual_frames = getattr(image, "n_frames", 1)
            if actual_frames != expected_frames:
                errors.append(
                    f"{path.relative_to(ROOT)} has {actual_frames} frames, expected {expected_frames}"
                )
    except Exception as exc:  # noqa: BLE001 - report image decoder detail.
        errors.append(f"cannot read {path.relative_to(ROOT)}: {exc}")
    return errors


def check_cards() -> None:
    errors: list[str] = []
    for spec in CARDS:
        errors.extend(check_card(spec))
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        raise SystemExit(1)
    total = sum(card_path(spec).stat().st_size for spec in CARDS)
    print(f"README cards ok: {len(CARDS)} GIFs, {total:,} bytes")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify committed README card GIFs.")
    args = parser.parse_args()

    if args.check:
        check_cards()
        return

    for spec in CARDS:
        render_card(spec)


if __name__ == "__main__":
    main()
