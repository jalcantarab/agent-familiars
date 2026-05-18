#!/usr/bin/env python3
"""Rotate an installed Codex pet to another spritesheet variant."""

from __future__ import annotations

import argparse
import json
import os
import random
import shutil
import sys
from datetime import datetime
from pathlib import Path

from PIL import Image

EXPECTED_SIZE = (1536, 1872)
DAYPARTS = {
    "morning": range(5, 12),
    "focus": range(12, 18),
    "evening": range(18, 23),
    "night": list(range(0, 5)) + [23],
}


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def default_dest() -> Path:
    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        return Path(codex_home).expanduser() / "pets"
    return Path.home() / ".codex" / "pets"


def validate_spritesheet(path: Path) -> None:
    if not path.is_file():
        fail(f"missing spritesheet variant: {path}")
    with Image.open(path) as image:
        if image.size != EXPECTED_SIZE:
            fail(
                f"{path} is {image.size[0]}x{image.size[1]}; "
                f"expected {EXPECTED_SIZE[0]}x{EXPECTED_SIZE[1]}"
            )
        if "A" not in image.getbands():
            fail(f"{path} has no alpha channel")


def variant_files(variant_dir: Path) -> list[Path]:
    if not variant_dir.is_dir():
        fail(f"variant directory does not exist: {variant_dir}")
    variants = sorted(path for path in variant_dir.iterdir() if path.suffix.lower() == ".webp")
    if not variants:
        fail(f"no .webp variants found in {variant_dir}")
    return variants


def state_path(pet_dir: Path) -> Path:
    return pet_dir / ".rotation-state.json"


def load_state(path: Path) -> dict[str, object]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_state(path: Path, state: dict[str, object]) -> None:
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def daypart_name(hour: int) -> str:
    for name, hours in DAYPARTS.items():
        if hour in hours:
            return name
    return "focus"


def choose_variant(args: argparse.Namespace, pet_dir: Path) -> Path:
    if args.variant:
        return Path(args.variant).expanduser().resolve()

    variants = variant_files(Path(args.variant_dir).expanduser().resolve())

    if args.mode == "random":
        return random.choice(variants)

    if args.mode == "daypart":
        wanted = daypart_name(datetime.now().hour)
        by_stem = {path.stem: path for path in variants}
        if wanted in by_stem:
            return by_stem[wanted]
        for path in variants:
            if path.stem.startswith(wanted):
                return path
        return variants[0]

    state = load_state(state_path(pet_dir))
    last = str(state.get("lastVariant", ""))
    stems = [path.stem for path in variants]
    try:
        next_index = (stems.index(last) + 1) % len(variants)
    except ValueError:
        next_index = 0
    return variants[next_index]


def rotate(args: argparse.Namespace) -> None:
    dest_root = Path(args.dest).expanduser()
    pet_dir = dest_root / args.pet_id
    manifest_path = pet_dir / "pet.json"
    if not manifest_path.is_file():
        fail(f"{pet_dir} is not an installed pet folder")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    sheet_name = manifest.get("spritesheetPath")
    if not isinstance(sheet_name, str) or not sheet_name:
        fail(f"{manifest_path} is missing spritesheetPath")
    installed_sheet = pet_dir / sheet_name

    variant = choose_variant(args, pet_dir)
    validate_spritesheet(variant)

    if args.dry_run:
        print(f"would rotate {args.pet_id} to {variant}")
        return

    if args.backup and installed_sheet.is_file():
        backup_dir = pet_dir / ".rotation-backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        shutil.copy2(installed_sheet, backup_dir / f"{timestamp}-{installed_sheet.name}")

    temp_path = installed_sheet.with_suffix(installed_sheet.suffix + ".tmp")
    shutil.copy2(variant, temp_path)
    temp_path.replace(installed_sheet)

    save_state(
        state_path(pet_dir),
        {
            "lastVariant": variant.stem,
            "lastVariantPath": str(variant),
            "updatedAt": datetime.now().isoformat(timespec="seconds"),
        },
    )
    print(f"rotated {args.pet_id} -> {variant.stem}")
    print("Next: refresh custom pets or wake the pet in Codex if the change is not visible.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pet_id", help="installed pet id, such as signal-surface")
    parser.add_argument("--variant", help="specific spritesheet.webp variant to install")
    parser.add_argument("--variant-dir", help="directory of .webp variants")
    parser.add_argument(
        "--mode",
        choices=("sequence", "daypart", "random"),
        default="sequence",
        help="selection mode when --variant-dir is used",
    )
    parser.add_argument(
        "--dest",
        default=str(default_dest()),
        help="installed Codex pets directory; defaults to ${CODEX_HOME:-~/.codex}/pets",
    )
    parser.add_argument("--backup", action="store_true", help="save the current installed sheet first")
    parser.add_argument("--dry-run", action="store_true", help="show the selected variant without copying")
    args = parser.parse_args()

    if not args.variant and not args.variant_dir:
        fail("pass --variant or --variant-dir")
    if args.variant and args.variant_dir:
        fail("pass only one of --variant or --variant-dir")

    rotate(args)


if __name__ == "__main__":
    main()
