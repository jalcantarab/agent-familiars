"""Command line interface for Familiars."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from .pet_assets import (
    CATALOG,
    PACKS,
    PETS,
    ROOT,
    PetAssetError,
    atlas,
    catalog,
    display_name,
    install_packs,
    manifest,
    pack_pet_ids,
    pet_entry,
    pet_folder,
    pet_ids,
    spritesheet_path,
)
from .sequence_presets import (
    SequencePresetError,
    presets,
    profiles,
    themes,
)
from .sequence_renderer import SequenceRenderError, render_outputs, render_preview_frame
from .sequence_schema import (
    SequenceSchemaError,
    load_recipe,
    normalize_recipe,
    recipe_from_pack,
    recipe_from_pet,
)


DEFAULT_REPO = "jalcantarab/agent-familiars"
DEFAULT_REF = "main"
EXPECTED_SPRITESHEET_SIZE = (1536, 1872)


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def default_dest() -> Path:
    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        return Path(codex_home).expanduser() / "pets"
    return Path.home() / ".codex" / "pets"


def raw_base(repo: str, ref: str) -> str:
    return f"https://raw.githubusercontent.com/{repo}/{ref}"


def fetch_url(url: str) -> bytes:
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        fail(f"could not download {url}: HTTP {exc.code}")
    except urllib.error.URLError as exc:
        fail(f"could not download {url}: {exc.reason}")


def load_remote_json(repo: str, ref: str, path: str) -> Any:
    return json.loads(fetch_url(f"{raw_base(repo, ref)}/{path}").decode("utf-8"))


def parse_outputs(value: str | None) -> list[str] | None:
    if value is None:
        return None
    formats = [item.strip() for item in value.split(",") if item.strip()]
    return formats or None


def pretty_path(path: Path) -> str:
    resolved = path.resolve()
    for base in (Path.cwd().resolve(), ROOT):
        try:
            return str(resolved.relative_to(base))
        except ValueError:
            continue
    return str(path)


def cmd_list(args: argparse.Namespace) -> None:
    if args.kind == "pets":
        for pet_id in pet_ids():
            entry = pet_entry(pet_id)
            license_value = entry.get("license", "unknown")
            print(f"{pet_id:22} {entry.get('displayName', pet_id)} ({license_value})")
        return

    if args.kind == "packs":
        for name, values in sorted(install_packs().items()):
            print(f"{name:18} {len(values)} pets")
        return

    if args.kind == "presets":
        for name, preset in sorted(presets().items()):
            print(f"{name:14} {preset.get('description', '')}")
        return

    if args.kind == "themes":
        for name, theme in sorted(themes().items()):
            print(f"{name:16} {theme.get('description', '')}")
        return

    if args.kind == "profiles":
        for name, profile in sorted(profiles().items()):
            print(f"{name:22} {profile.get('subtitle', '')}")
        return

    fail(f"unknown list kind {args.kind!r}")


def resolve_requested_pet_ids(
    requested_ids: list[str],
    requested_packs: list[str],
    install_all: bool,
    available_ids: list[str],
    packs: dict[str, list[str]],
) -> list[str]:
    requested: list[str] = []
    for pack in requested_packs:
        if pack not in packs:
            fail(f"unknown pack {pack!r}; choose one of: {', '.join(sorted(packs))}")
        requested.extend(packs[pack])

    if install_all:
        requested.extend(available_ids)
    requested.extend(requested_ids)

    if not requested:
        fail("pass one or more pet ids, --pack starter, --pack first-50, or --all")

    available = set(available_ids)
    resolved = []
    seen = set()
    for pet_id in requested:
        if pet_id not in available:
            fail(f"unknown pet id {pet_id!r}; run `familiars list pets` to see available pets")
        if pet_id not in seen:
            seen.add(pet_id)
            resolved.append(pet_id)
    return resolved


def install_local(pet_id: str, dest_root: Path) -> Path:
    source_dir = pet_folder(pet_id)
    dest_dir = dest_root / pet_id
    dest_dir.mkdir(parents=True, exist_ok=True)
    for filename in ("pet.json", "spritesheet.webp"):
        source = source_dir / filename
        if not source.is_file():
            fail(f"{source_dir} is missing {filename}")
        shutil.copy2(source, dest_dir / filename)
    return dest_dir


def install_github(pet: dict[str, object], repo: str, ref: str, dest_root: Path) -> Path:
    pet_id = str(pet["id"])
    folder = str(pet["folder"])
    dest_dir = dest_root / pet_id
    dest_dir.mkdir(parents=True, exist_ok=True)
    for filename in ("pet.json", "spritesheet.webp"):
        url = f"{raw_base(repo, ref)}/{folder}/{filename}"
        (dest_dir / filename).write_bytes(fetch_url(url))
    return dest_dir


def validate_install(dest_dir: Path) -> None:
    manifest_path = dest_dir / "pet.json"
    sheet_path = dest_dir / "spritesheet.webp"
    if not manifest_path.is_file() or not sheet_path.is_file():
        fail(f"{dest_dir} did not receive both pet.json and spritesheet.webp")

    pet_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for key in ("id", "displayName", "description", "spritesheetPath"):
        if not isinstance(pet_manifest.get(key), str) or not pet_manifest[key].strip():
            fail(f"{manifest_path} is missing non-empty {key}")

    referenced_sheet = dest_dir / pet_manifest["spritesheetPath"]
    if not referenced_sheet.is_file():
        fail(f"{manifest_path} references missing spritesheet {pet_manifest['spritesheetPath']}")


def cmd_install(args: argparse.Namespace) -> None:
    dest_root = Path(args.dest).expanduser()
    dest_root.mkdir(parents=True, exist_ok=True)

    if args.source == "github":
        remote_catalog = load_remote_json(args.repo, args.ref, "catalog/pets.json")
        remote_packs = load_remote_json(args.repo, args.ref, "catalog/packs.json")
        if not isinstance(remote_catalog, list) or not isinstance(remote_packs, dict):
            fail("remote catalog data has an unexpected shape")
        available_ids = [str(entry["id"]) for entry in remote_catalog]
        packs = {
            str(name): list(values)
            for name, values in remote_packs.items()
            if isinstance(values, list) and all(isinstance(item, str) for item in values)
        }
        remote_by_id = {str(entry["id"]): entry for entry in remote_catalog}
        selected = resolve_requested_pet_ids(args.pet_ids, args.pack, args.all, available_ids, packs)
        installed = [
            (pet_id, remote_by_id[pet_id].get("displayName", pet_id), install_github(remote_by_id[pet_id], args.repo, args.ref, dest_root))
            for pet_id in selected
        ]
    else:
        selected = resolve_requested_pet_ids(args.pet_ids, args.pack, args.all, pet_ids(), install_packs())
        installed = [(pet_id, display_name(pet_id), install_local(pet_id, dest_root)) for pet_id in selected]

    for _pet_id, _display_name, dest_dir in installed:
        validate_install(dest_dir)
    for pet_id, pet_name, dest_dir in installed:
        print(f"installed {pet_name} ({pet_id}) -> {dest_dir}")
    print("\nNext: open Codex Settings -> Personalization -> Pets -> Refresh custom pets.")


def resolve_recipe_path(value: str) -> Path:
    raw_path = Path(value).expanduser()
    candidates = [raw_path]
    if not raw_path.is_absolute():
        candidates.extend(
            [
                Path.cwd() / raw_path,
                ROOT / raw_path,
                ROOT / "examples" / "sequences" / raw_path,
            ]
        )
        if raw_path.suffix != ".json":
            candidates.extend(
                [
                    Path.cwd() / f"{value}.json",
                    ROOT / f"{value}.json",
                    ROOT / "examples" / "sequences" / f"{value}.json",
                ]
            )

    for candidate in candidates:
        if candidate.is_file():
            return candidate
    fail(f"recipe not found: {value}")


def recipe_from_render_args(args: argparse.Namespace) -> dict[str, object]:
    if args.recipe:
        raw = load_recipe(resolve_recipe_path(args.recipe))
    elif args.pet:
        pet_entry(args.pet)
        raw = recipe_from_pet(args.pet, args.preset, args.theme, args.title)
    elif args.pack:
        pack_pet_ids(args.pack)
        raw = recipe_from_pack(args.pack, args.preset, args.theme, args.title)
    else:
        fail("pass --recipe, --pet, or --pack")

    output_dir = Path(args.output_dir).expanduser() if args.output_dir else Path.cwd() / "output" / "sequences"
    return normalize_recipe(
        raw,
        output_dir=output_dir,
        outputs=parse_outputs(args.outputs),
        preset_name=args.preset_override,
        theme_name=args.theme_override,
    )


def cmd_render(args: argparse.Namespace) -> None:
    recipe = recipe_from_render_args(args)
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
        print(f"wrote {pretty_path(path)}")


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


def check_assets() -> None:
    if not CATALOG.is_file() or not PACKS.is_file() or not PETS.is_dir():
        fail(f"data root is incomplete: {ROOT}")
    for pet_id in pet_ids():
        pet_manifest = manifest(pet_id)
        if not isinstance(pet_manifest.get("displayName"), str):
            fail(f"{pet_id}: pet.json missing displayName")
        if spritesheet_path(pet_id).suffix != ".webp":
            fail(f"{pet_id}: spritesheet must be a .webp file")
        if atlas(pet_id).size != EXPECTED_SPRITESHEET_SIZE:
            fail(f"{pet_id}: spritesheet must be {EXPECTED_SPRITESHEET_SIZE[0]}x{EXPECTED_SPRITESHEET_SIZE[1]}")


def check_examples() -> int:
    examples = ROOT / "examples" / "sequences"
    if not examples.is_dir():
        fail("missing examples/sequences")
    checked = 0
    for path in sorted(examples.glob("*.json")):
        recipe = normalize_recipe(load_recipe(path), output_dir=Path.cwd() / "output" / "sequences")
        render_preview_frame(recipe)
        checked += 1
    if checked == 0:
        fail("no example sequence recipes found")
    return checked


def cmd_validate(_args: argparse.Namespace) -> None:
    check_assets()
    check_profiles()
    example_count = check_examples()
    print(
        "familiars ok: "
        f"{len(catalog())} pets, "
        f"{len(install_packs())} packs, "
        f"{len(presets())} presets, "
        f"{len(themes())} themes, "
        f"{example_count} sequence examples"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="familiars", description="Install, inspect, and render Familiars.")
    subcommands = parser.add_subparsers(dest="command", required=True)

    list_parser = subcommands.add_parser("list", help="List packaged Familiars data.")
    list_parser.add_argument("kind", choices=("pets", "packs", "presets", "themes", "profiles"))
    list_parser.set_defaults(func=cmd_list)

    install_parser = subcommands.add_parser("install", help="Install pets into a local Codex pets directory.")
    install_parser.add_argument("pet_ids", nargs="*", help="pet id(s) to install, such as zentri")
    install_parser.add_argument("--all", action="store_true", help="install every pet in the catalog")
    install_parser.add_argument("--pack", action="append", default=[], help="install a curated pack; can be passed more than once")
    install_parser.add_argument(
        "--dest",
        default=str(default_dest()),
        help="destination pets directory; defaults to ${CODEX_HOME:-~/.codex}/pets",
    )
    install_parser.add_argument(
        "--source",
        choices=("local", "github"),
        default="local",
        help="install from packaged/source data or from GitHub",
    )
    install_parser.add_argument("--repo", default=DEFAULT_REPO, help="GitHub owner/repo for --source github")
    install_parser.add_argument("--ref", default=DEFAULT_REF, help="Git ref for --source github")
    install_parser.set_defaults(func=cmd_install)

    render_parser = subcommands.add_parser("render", help="Render a sequence GIF, MP4, or poster.")
    render_parser.add_argument("--recipe", help="Path or example name for a sequence recipe JSON file.")
    render_parser.add_argument("--pet", help="Render a preset sequence for one pet id.")
    render_parser.add_argument("--pack", help="Render a preset sequence for a known install pack.")
    render_parser.add_argument("--preset", default="spotlight", help="Preset for --pet or --pack.")
    render_parser.add_argument("--theme", help="Theme for --pet or --pack.")
    render_parser.add_argument("--title", help="Override generated recipe title.")
    render_parser.add_argument("--preset-override", help="Override the recipe preset.")
    render_parser.add_argument("--theme-override", help="Override the recipe theme.")
    render_parser.add_argument("--outputs", help="Comma-separated output formats: gif,mp4,poster.")
    render_parser.add_argument("--output-dir", help="Output directory; defaults to ./output/sequences.")
    render_parser.add_argument("--dry-run", action="store_true", help="Print normalized recipe without rendering.")
    render_parser.set_defaults(func=cmd_render)

    validate_parser = subcommands.add_parser("validate", help="Validate packaged catalog data and sequence examples.")
    validate_parser.set_defaults(func=cmd_validate)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except (
        json.JSONDecodeError,
        KeyError,
        PetAssetError,
        SequencePresetError,
        SequenceRenderError,
        SequenceSchemaError,
        ValueError,
    ) as exc:
        fail(str(exc))


if __name__ == "__main__":
    main()
