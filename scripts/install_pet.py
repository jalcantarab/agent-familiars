#!/usr/bin/env python3
"""Install Familiars pets into a local Codex pets directory."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import urllib.error
import urllib.request
from pathlib import Path


DEFAULT_REPO = "jalcantarab/agent-familiars"
DEFAULT_REF = "main"
PACKS_PATH = "catalog/packs.json"


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def default_dest() -> Path:
    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        return Path(codex_home).expanduser() / "pets"
    return Path.home() / ".codex" / "pets"


def find_repo_root() -> Path | None:
    candidates = [Path.cwd()]
    file_path = Path(__file__)
    if file_path.name != "<stdin>":
        candidates.append(file_path.resolve().parent)

    for candidate in candidates:
        for path in [candidate, *candidate.parents]:
            if (path / "catalog" / "pets.json").is_file() and (path / "pets").is_dir():
                return path
    return None


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


def load_catalog(source: str, repo_root: Path | None, repo: str, ref: str) -> list[dict[str, object]]:
    if source == "local":
        if repo_root is None:
            fail("local source requested, but this script is not running inside a clone")
        return json.loads((repo_root / "catalog" / "pets.json").read_text(encoding="utf-8"))

    if source == "auto" and repo_root is not None:
        return json.loads((repo_root / "catalog" / "pets.json").read_text(encoding="utf-8"))

    catalog_url = f"{raw_base(repo, ref)}/catalog/pets.json"
    return json.loads(fetch_url(catalog_url).decode("utf-8"))


def load_packs(source: str, repo_root: Path | None, repo: str, ref: str) -> dict[str, list[str]]:
    if source == "local":
        if repo_root is None:
            fail("local source requested, but this script is not running inside a clone")
        return parse_packs((repo_root / PACKS_PATH).read_text(encoding="utf-8"))

    if source == "auto" and repo_root is not None:
        return parse_packs((repo_root / PACKS_PATH).read_text(encoding="utf-8"))

    packs_url = f"{raw_base(repo, ref)}/{PACKS_PATH}"
    return parse_packs(fetch_url(packs_url).decode("utf-8"))


def parse_packs(raw: str) -> dict[str, list[str]]:
    data = json.loads(raw)
    if not isinstance(data, dict):
        fail(f"{PACKS_PATH} must contain a JSON object")
    packs: dict[str, list[str]] = {}
    for name, values in data.items():
        if not isinstance(name, str) or not name:
            fail(f"{PACKS_PATH} contains an invalid pack name")
        if not isinstance(values, list) or not all(isinstance(item, str) for item in values):
            fail(f"pack {name!r} must be an array of pet ids")
        packs[name] = list(values)
    return packs


def resolve_pet_ids(args: argparse.Namespace, catalog: list[dict[str, object]], packs: dict[str, list[str]]) -> list[str]:
    ids = [str(pet["id"]) for pet in catalog]
    requested: list[str] = []

    for pack in args.pack:
        if pack not in packs:
            fail(f"unknown pack {pack!r}; choose one of: {', '.join(sorted(packs))}")
        requested.extend(packs[pack])

    if args.all:
        requested.extend(ids)

    requested.extend(args.pet_ids)

    if not requested:
        fail("pass one or more pet ids, --pack starter, --pack first-50, --all, --list, or --list-packs")

    seen = set()
    resolved = []
    for pet_id in requested:
        if pet_id not in ids:
            fail(f"unknown pet id {pet_id!r}; run with --list to see available pets")
        if pet_id not in seen:
            seen.add(pet_id)
            resolved.append(pet_id)
    return resolved


def install_local(pet: dict[str, object], repo_root: Path, dest_root: Path) -> Path:
    pet_id = str(pet["id"])
    folder = str(pet["folder"])
    source_dir = repo_root / folder
    if not source_dir.is_dir():
        fail(f"missing local pet folder: {source_dir}")

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
    base = raw_base(repo, ref)
    dest_dir = dest_root / pet_id
    dest_dir.mkdir(parents=True, exist_ok=True)

    for filename in ("pet.json", "spritesheet.webp"):
        url = f"{base}/{folder}/{filename}"
        (dest_dir / filename).write_bytes(fetch_url(url))
    return dest_dir


def validate_install(dest_dir: Path) -> None:
    manifest_path = dest_dir / "pet.json"
    sheet_path = dest_dir / "spritesheet.webp"
    if not manifest_path.is_file() or not sheet_path.is_file():
        fail(f"{dest_dir} did not receive both pet.json and spritesheet.webp")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for key in ("id", "displayName", "description", "spritesheetPath"):
        if not isinstance(manifest.get(key), str) or not manifest[key].strip():
            fail(f"{manifest_path} is missing non-empty {key}")

    referenced_sheet = dest_dir / manifest["spritesheetPath"]
    if not referenced_sheet.is_file():
        fail(f"{manifest_path} references missing spritesheet {manifest['spritesheetPath']}")


def print_list(catalog: list[dict[str, object]]) -> None:
    for pet in catalog:
        license_value = pet.get("license", "unknown")
        print(f"{pet['id']:18} {pet.get('displayName', pet['id'])} ({license_value})")


def print_packs(packs: dict[str, list[str]]) -> None:
    for name, pet_ids in sorted(packs.items()):
        print(f"{name:18} {len(pet_ids)} pets")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pet_ids", nargs="*", help="pet id(s) to install, such as zentri")
    parser.add_argument("--all", action="store_true", help="install every pet in the catalog")
    parser.add_argument(
        "--pack",
        action="append",
        default=[],
        help="install a curated pack; can be passed more than once",
    )
    parser.add_argument("--list", action="store_true", help="list available pets and exit")
    parser.add_argument("--list-packs", action="store_true", help="list available packs and exit")
    parser.add_argument(
        "--dest",
        default=str(default_dest()),
        help="destination pets directory; defaults to ${CODEX_HOME:-~/.codex}/pets",
    )
    parser.add_argument(
        "--source",
        choices=("auto", "local", "github"),
        default="auto",
        help="read pets from the local clone when available, otherwise GitHub",
    )
    parser.add_argument("--repo", default=DEFAULT_REPO, help="GitHub owner/repo for --source github")
    parser.add_argument("--ref", default=DEFAULT_REF, help="Git ref for --source github")
    args = parser.parse_args()

    repo_root = find_repo_root()
    catalog = load_catalog(args.source, repo_root, args.repo, args.ref)
    packs = load_packs(args.source, repo_root, args.repo, args.ref)
    catalog_by_id = {str(pet["id"]): pet for pet in catalog}

    if args.list:
        print_list(catalog)
        return
    if args.list_packs:
        print_packs(packs)
        return

    pet_ids = resolve_pet_ids(args, catalog, packs)
    dest_root = Path(args.dest).expanduser()
    dest_root.mkdir(parents=True, exist_ok=True)

    use_local = args.source != "github" and repo_root is not None
    installed = []
    for pet_id in pet_ids:
        pet = catalog_by_id[pet_id]
        if use_local:
            dest_dir = install_local(pet, repo_root, dest_root)
        else:
            dest_dir = install_github(pet, args.repo, args.ref, dest_root)
        validate_install(dest_dir)
        installed.append((pet_id, pet.get("displayName", pet_id), dest_dir))

    for pet_id, display_name, dest_dir in installed:
        print(f"installed {display_name} ({pet_id}) -> {dest_dir}")

    print("\nNext: open Codex Settings -> Personalization -> Pets -> Refresh custom pets.")


if __name__ == "__main__":
    main()
