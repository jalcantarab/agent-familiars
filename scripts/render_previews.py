#!/usr/bin/env python3
"""Render or check GitHub-friendly pet preview GIFs from Codex spritesheets."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
PETS = ROOT / "pets"
CELL_WIDTH = 192
CELL_HEIGHT = 208
COLUMNS = 8
ROWS = [
    ("idle", 6, [280, 110, 110, 140, 140, 320]),
    ("running-right", 8, [120, 120, 120, 120, 120, 120, 120, 220]),
    ("running-left", 8, [120, 120, 120, 120, 120, 120, 120, 220]),
    ("waving", 4, [140, 140, 140, 280]),
    ("jumping", 5, [140, 140, 140, 140, 280]),
    ("failed", 8, [140, 140, 140, 140, 140, 140, 140, 240]),
    ("waiting", 6, [150, 150, 150, 150, 150, 260]),
    ("running", 6, [120, 120, 120, 120, 120, 220]),
    ("review", 6, [150, 150, 150, 150, 150, 280]),
]


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path) -> dict[str, object]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"missing {path.relative_to(ROOT)}")
    except json.JSONDecodeError as exc:
        fail(f"{path.relative_to(ROOT)} is not valid JSON: {exc}")

    if not isinstance(data, dict):
        fail(f"{path.relative_to(ROOT)} must be a JSON object")
    return data


def pet_folders(selected: list[str], all_pets: bool) -> list[Path]:
    if not PETS.is_dir():
        fail("missing pets directory")

    folders = sorted(path for path in PETS.iterdir() if path.is_dir())
    by_id = {path.name: path for path in folders}

    if all_pets:
        return folders
    if selected:
        unknown = sorted(set(selected) - set(by_id))
        if unknown:
            fail(f"unknown pet id(s): {', '.join(unknown)}")
        return [by_id[pet_id] for pet_id in selected]

    fail("pass one or more pet ids, or use --all")


def atlas_path(folder: Path) -> Path:
    manifest = load_json(folder / "pet.json")
    spritesheet = manifest.get("spritesheetPath")
    if not isinstance(spritesheet, str) or not spritesheet:
        fail(f"{folder.relative_to(ROOT)}: pet.json missing spritesheetPath")
    path = folder / spritesheet
    if not path.is_file():
        fail(f"{folder.relative_to(ROOT)}: missing spritesheet {spritesheet}")
    return path


def frames_from_atlas(atlas: Image.Image, row_index: int, count: int) -> list[Image.Image]:
    frames = []
    for column in range(count):
        frames.append(
            atlas.crop(
                (
                    column * CELL_WIDTH,
                    row_index * CELL_HEIGHT,
                    (column + 1) * CELL_WIDTH,
                    (row_index + 1) * CELL_HEIGHT,
                )
            )
        )
    return frames


def save_gif(frames: list[Image.Image], durations: list[int], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        output,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        disposal=2,
        optimize=False,
    )


def visible_frame_count(frames: list[Image.Image]) -> int:
    if not frames:
        return 0

    count = 1
    previous = frames[0]
    for frame in frames[1:]:
        if ImageChops.difference(previous, frame).getbbox() is not None:
            count += 1
            previous = frame
    return count


def checker(size: tuple[int, int], square: int = 16) -> Image.Image:
    image = Image.new("RGB", size, "#ffffff")
    draw = ImageDraw.Draw(image)
    for y in range(0, size[1], square):
        for x in range(0, size[0], square):
            if (x // square + y // square) % 2:
                draw.rectangle((x, y, x + square - 1, y + square - 1), fill="#e8e8e8")
    return image


def save_contact_sheet(atlas: Image.Image, output: Path) -> None:
    scale = 0.5
    label_height = 22
    cell_width = round(CELL_WIDTH * scale)
    cell_height = round(CELL_HEIGHT * scale)
    width = COLUMNS * cell_width
    height = len(ROWS) * (cell_height + label_height)
    sheet = Image.new("RGB", (width, height), "#f7f7f7")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()

    for row_index, (state, used_count, _durations) in enumerate(ROWS):
        y = row_index * (cell_height + label_height)
        draw.rectangle((0, y, width, y + label_height - 1), fill="#111111")
        draw.text((6, y + 5), f"row {row_index}: {state}", fill="#ffffff", font=font)
        draw.text((width - 92, y + 5), f"{used_count} frames", fill="#ffffff", font=font)

        for column in range(COLUMNS):
            crop = atlas.crop(
                (
                    column * CELL_WIDTH,
                    row_index * CELL_HEIGHT,
                    (column + 1) * CELL_WIDTH,
                    (row_index + 1) * CELL_HEIGHT,
                )
            )
            crop = crop.resize((cell_width, cell_height), Image.Resampling.LANCZOS)
            background = checker((cell_width, cell_height))
            background.paste(crop, (0, 0), crop)
            x = column * cell_width
            sheet.paste(background, (x, y + label_height))
            outline = "#18a058" if column < used_count else "#cc3344"
            draw.rectangle(
                (x, y + label_height, x + cell_width - 1, y + label_height + cell_height - 1),
                outline=outline,
            )
            draw.text((x + 4, y + label_height + 4), str(column), fill="#111111", font=font)

    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def render_pet(folder: Path, force: bool) -> list[str]:
    written = []
    preview_dir = folder / "preview"
    with Image.open(atlas_path(folder)) as opened:
        atlas = opened.convert("RGBA")

    for row_index, (state, frame_count, durations) in enumerate(ROWS):
        output = preview_dir / f"{state}.gif"
        if force or not output.exists():
            save_gif(frames_from_atlas(atlas, row_index, frame_count), durations, output)
            written.append(str(output.relative_to(ROOT)))

    contact_sheet = preview_dir / "contact-sheet.png"
    if force or not contact_sheet.exists():
        save_contact_sheet(atlas, contact_sheet)
        written.append(str(contact_sheet.relative_to(ROOT)))

    return written


def valid_preview_size(size: tuple[int, int]) -> bool:
    width, height = size
    return (
        width >= CELL_WIDTH
        and height >= CELL_HEIGHT
        and width % CELL_WIDTH == 0
        and height % CELL_HEIGHT == 0
    )


def check_pet(folder: Path) -> list[str]:
    errors = []
    preview_dir = folder / "preview"
    if not preview_dir.is_dir():
        return [f"{folder.name}: missing preview directory"]
    with Image.open(atlas_path(folder)) as opened:
        atlas = opened.convert("RGBA")

    readme_path = folder / "README.md"
    readme = readme_path.read_text(encoding="utf-8") if readme_path.is_file() else ""
    if "## Animation Catalog" not in readme:
        errors.append(f"{folder.name}: README.md missing Animation Catalog section")

    for state, expected_frames, _durations in ROWS:
        path = preview_dir / f"{state}.gif"
        if not path.is_file():
            errors.append(f"{folder.name}: missing preview/{state}.gif")
            continue
        if f"preview/{state}.gif" not in readme:
            errors.append(f"{folder.name}: README.md missing preview/{state}.gif reference")
        try:
            with Image.open(path) as image:
                frame_count = getattr(image, "n_frames", 1)
                size = image.size
        except Exception as exc:  # noqa: BLE001 - report image decoder detail.
            errors.append(f"{folder.name}: cannot read preview/{state}.gif: {exc}")
            continue
        row_index = next(index for index, row in enumerate(ROWS) if row[0] == state)
        expected_visible_frames = visible_frame_count(frames_from_atlas(atlas, row_index, expected_frames))
        if frame_count != expected_visible_frames:
            errors.append(
                f"{folder.name}: preview/{state}.gif has {frame_count} frames, "
                f"expected {expected_visible_frames}"
            )
        if not valid_preview_size(size):
            errors.append(f"{folder.name}: preview/{state}.gif has unexpected size {size}")

    if not (preview_dir / "contact-sheet.png").is_file():
        errors.append(f"{folder.name}: missing preview/contact-sheet.png")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pet_ids", nargs="*", help="Pet ids to render or check.")
    parser.add_argument("--all", action="store_true", help="Render or check every pet.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing preview files.")
    parser.add_argument("--check", action="store_true", help="Validate preview files without writing.")
    args = parser.parse_args()

    folders = pet_folders(args.pet_ids, args.all)

    if args.check:
        errors = []
        for folder in folders:
            errors.extend(check_pet(folder))
        if errors:
            for error in errors:
                print(f"error: {error}", file=sys.stderr)
            raise SystemExit(1)
        print(f"preview artifacts ok: {len(folders)} pets")
        return

    written = []
    for folder in folders:
        written.extend(render_pet(folder, args.force))

    if written:
        for path in written:
            print(f"wrote {path}")
    else:
        print("preview artifacts already current")


if __name__ == "__main__":
    main()
