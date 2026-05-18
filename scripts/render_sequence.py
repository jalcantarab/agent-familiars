#!/usr/bin/env python3
"""Render reusable Familiars sequence recipes."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from familiars.pet_assets import (  # noqa: E402
    PetAssetError,
    install_packs,
    pack_pet_ids,
    pet_entry,
    pet_ids,
)
from familiars.sequence_presets import (  # noqa: E402
    SequencePresetError,
    presets,
    profiles,
    themes,
)
from familiars.sequence_renderer import (  # noqa: E402
    SequenceRenderError,
    render_outputs,
    render_preview_frame,
)
from familiars.sequence_schema import (  # noqa: E402
    SequenceSchemaError,
    load_recipe,
    normalize_recipe,
    recipe_from_pack,
    recipe_from_pet,
)


EXAMPLES = ROOT / "examples" / "sequences"


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_outputs(value: str | None) -> list[str] | None:
    if value is None:
        return None
    formats = [item.strip() for item in value.split(",") if item.strip()]
    return formats or None


def recipe_from_args(args: argparse.Namespace) -> dict[str, object]:
    if args.recipe:
        raw = load_recipe(Path(args.recipe).expanduser())
    elif args.pet:
        pet_entry(args.pet)
        raw = recipe_from_pet(args.pet, args.preset, args.theme, args.title)
    elif args.pack:
        pack_pet_ids(args.pack)
        raw = recipe_from_pack(args.pack, args.preset, args.theme, args.title)
    else:
        fail("pass --recipe, --pet, --pack, --check, or a list flag")

    return normalize_recipe(
        raw,
        output_dir=Path(args.output_dir).expanduser() if args.output_dir else None,
        outputs=parse_outputs(args.outputs),
        preset_name=args.preset_override,
        theme_name=args.theme_override,
    )


def check_profiles() -> None:
    known_pets = set(pet_ids())
    configured_profiles = set(profiles())
    missing = sorted(known_pets - configured_profiles)
    extra = sorted(configured_profiles - known_pets)
    if missing:
        fail(f"missing pet profiles: {', '.join(missing)}")
    if extra:
        fail(f"pet profiles without catalog entries: {', '.join(extra)}")

    for pet_id in sorted(known_pets):
        normalize_recipe(recipe_from_pet(pet_id, "spotlight"))
    for pack in sorted(install_packs()):
        pack_pet_ids(pack)


def check_hardening() -> None:
    base_recipe = {"title": "Hardening Check", "scenes": [{"pet": "zentri"}]}

    slugged = normalize_recipe({**base_recipe, "slug": "../../bad name"})
    if slugged["slug"] != "bad-name":
        fail("recipe slug sanitization failed")

    def expect_error(label: str, raw: dict[str, object], **kwargs: object) -> None:
        try:
            normalize_recipe(raw, **kwargs)
        except SequenceSchemaError:
            return
        fail(f"expected sequence schema error for {label}")

    expect_error("oversized width", {**base_recipe, "width": 9999})
    expect_error("invalid layout", {"title": "Bad Layout", "scenes": [{"pet": "zentri", "layout": "spiral"}]})
    expect_error(
        "unsafe output directory",
        {**base_recipe, "outputs": {"formats": ["poster"], "dir": "../outside"}},
        output_root=ROOT / "output" / "safe-sequences",
        allow_output_outside_root=False,
    )

    too_many_frames = normalize_recipe(
        {
            "title": "Too Many Frames",
            "fps": 30,
            "beatSeconds": 10,
            "outputs": ["poster"],
            "scenes": [{"pet": "zentri"} for _index in range(7)],
        }
    )
    try:
        render_preview_frame(too_many_frames)
    except SequenceRenderError:
        return
    fail("expected sequence render error for excessive frame count")


def check_examples() -> None:
    check_profiles()
    check_hardening()
    if not EXAMPLES.is_dir():
        fail("missing examples/sequences")
    checked = 0
    for path in sorted(EXAMPLES.glob("*.json")):
        recipe = normalize_recipe(load_recipe(path))
        render_preview_frame(recipe)
        checked += 1
    if checked == 0:
        fail("no example sequence recipes found")
    print(f"sequence recipes ok: {checked} examples, {len(profiles())} pet profiles")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recipe", help="Path to a sequence recipe JSON file.")
    parser.add_argument("--pet", help="Render a preset sequence for one pet id.")
    parser.add_argument("--pack", help="Render a preset sequence for a known install pack.")
    parser.add_argument("--preset", default="spotlight", help="Preset for --pet or --pack.")
    parser.add_argument("--theme", help="Theme for --pet or --pack.")
    parser.add_argument("--title", help="Override generated recipe title.")
    parser.add_argument("--preset-override", help="Override the recipe preset.")
    parser.add_argument("--theme-override", help="Override the recipe theme.")
    parser.add_argument("--outputs", help="Comma-separated output formats: gif,mp4,poster.")
    parser.add_argument("--output-dir", help="Output directory; defaults to output/sequences.")
    parser.add_argument("--dry-run", action="store_true", help="Print normalized recipe without rendering.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate sequence configs, example recipes, and one rendered frame per example.",
    )
    parser.add_argument("--list-presets", action="store_true", help="List built-in presets.")
    parser.add_argument("--list-themes", action="store_true", help="List built-in themes.")
    parser.add_argument("--list-profiles", action="store_true", help="List pet profiles with custom beat defaults.")
    parser.add_argument("--list-pets", action="store_true", help="List available pet ids.")
    args = parser.parse_args()

    try:
        if args.list_presets:
            for name, preset in sorted(presets().items()):
                print(f"{name:14} {preset.get('description', '')}")
            return
        if args.list_themes:
            for name, theme in sorted(themes().items()):
                print(f"{name:16} {theme.get('description', '')}")
            return
        if args.list_profiles:
            for name, profile in sorted(profiles().items()):
                print(f"{name:22} {profile.get('subtitle', '')}")
            return
        if args.list_pets:
            for pet_id in pet_ids():
                print(pet_id)
            return
        if args.check:
            check_examples()
            return

        recipe = recipe_from_args(args)
        if args.dry_run:
            printable = dict(recipe)
            printable["outputs"] = {
                "formats": recipe["outputs"]["formats"],
                "dir": str(recipe["outputs"]["dir"]),
            }
            print(json.dumps(printable, indent=2))
            return

        written = render_outputs(recipe)
        for path in written:
            try:
                print(f"wrote {path.relative_to(ROOT)}")
            except ValueError:
                print(f"wrote {path}")
    except (
        PetAssetError,
        SequencePresetError,
        SequenceRenderError,
        SequenceSchemaError,
        ValueError,
    ) as exc:
        fail(str(exc))


if __name__ == "__main__":
    main()
