#!/usr/bin/env python3
"""Validate Familiars bundles and catalog metadata."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
PETS = ROOT / "pets"
CATALOG = ROOT / "catalog" / "pets.json"
PACKS = ROOT / "catalog" / "packs.json"
NOTICE = ROOT / "NOTICE.md"
EXPECTED_SIZE = (1536, 1872)
REQUIRED_CATALOG_FIELDS = (
    "id",
    "displayName",
    "folder",
    "origin",
    "author",
    "sourceUrl",
    "license",
    "tags",
)
ALLOWED_ORIGINS = {"original", "imported"}
ALLOWED_LICENSES = {"MIT", "CC BY 4.0"}
ORIGINAL_SOURCE_URL = "https://github.com/jalcantarab/agent-familiars"
IMPORTED_LICENSE_FILES = {
    ("https://github.com/gennadi-kuzmin/awesome-codex-pets", "MIT"): (
        ROOT / "licenses" / "gennadi-kuzmin-awesome-codex-pets-MIT.txt"
    ),
    ("https://github.com/mertcreates/codex-paws", "CC BY 4.0"): (
        ROOT / "licenses" / "mertcreates-codex-paws-CC-BY-4.0.md"
    ),
    ("https://github.com/xixu-me/codex-pets", "MIT"): (
        ROOT / "licenses" / "xixu-me-codex-pets-MIT.txt"
    ),
}


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"missing {path.relative_to(ROOT)}")
    except json.JSONDecodeError as exc:
        fail(f"{path.relative_to(ROOT)} is not valid JSON: {exc}")


def validate_pet(folder: Path) -> dict[str, object]:
    manifest_path = folder / "pet.json"
    if not manifest_path.is_file():
        fail(f"{folder.relative_to(ROOT)}: missing pet.json")

    manifest = load_json(manifest_path)
    if not isinstance(manifest, dict):
        fail(f"{manifest_path.relative_to(ROOT)} must be a JSON object")

    for key in ("id", "displayName", "description", "spritesheetPath"):
        if not isinstance(manifest.get(key), str) or not manifest[key].strip():
            fail(f"{folder.relative_to(ROOT)}: pet.json missing non-empty {key}")

    if manifest["id"] != folder.name:
        fail(f"{folder.relative_to(ROOT)}: pet.json id must match folder name")

    sheet_path = folder / manifest["spritesheetPath"]
    if not sheet_path.is_file():
        fail(f"{folder.relative_to(ROOT)}: missing spritesheet {manifest['spritesheetPath']}")

    with Image.open(sheet_path) as image:
        if image.size != EXPECTED_SIZE:
            fail(
                f"{folder.relative_to(ROOT)}: expected {EXPECTED_SIZE[0]}x{EXPECTED_SIZE[1]}, "
                f"got {image.size[0]}x{image.size[1]}"
            )
        if "A" not in image.getbands():
            fail(f"{folder.relative_to(ROOT)}: spritesheet has no alpha channel")

    readme = folder / "README.md"
    if not readme.is_file():
        fail(f"{folder.relative_to(ROOT)}: missing README.md")
    if "License:" not in readme.read_text(encoding="utf-8"):
        fail(f"{folder.relative_to(ROOT)}: README.md missing License attribution")

    return {
        "id": manifest["id"],
        "displayName": manifest["displayName"],
        "folder": str(folder.relative_to(ROOT)),
    }


def validate_catalog(pets: list[dict[str, object]]) -> list[dict[str, object]]:
    raw_catalog = load_json(CATALOG)
    if not isinstance(raw_catalog, list):
        fail("catalog/pets.json must be an array")
    try:
        notice_text = NOTICE.read_text(encoding="utf-8")
    except FileNotFoundError:
        fail("missing NOTICE.md")

    catalog: list[dict[str, object]] = []
    seen_ids: set[str] = set()
    pet_ids = {str(pet["id"]) for pet in pets}
    pet_folders = {str(pet["folder"]) for pet in pets}

    for index, entry in enumerate(raw_catalog, start=1):
        if not isinstance(entry, dict):
            fail(f"catalog/pets.json[{index}] must be an object")
        catalog.append(entry)

        for field in REQUIRED_CATALOG_FIELDS:
            value = entry.get(field)
            if field == "tags":
                if not isinstance(value, list) or not value or not all(isinstance(tag, str) and tag for tag in value):
                    fail(f"catalog entry {index} has invalid tags")
            elif not isinstance(value, str) or not value.strip():
                fail(f"catalog entry {index} missing non-empty {field}")

        pet_id = str(entry["id"])
        if pet_id in seen_ids:
            fail(f"catalog/pets.json contains duplicate id {pet_id!r}")
        seen_ids.add(pet_id)

        origin = str(entry["origin"])
        license_name = str(entry["license"])
        source_url = str(entry["sourceUrl"])

        if origin not in ALLOWED_ORIGINS:
            fail(f"catalog entry {pet_id}: origin must be original or imported")
        if license_name not in ALLOWED_LICENSES:
            fail(
                f"catalog entry {pet_id}: license must be one of "
                f"{sorted(ALLOWED_LICENSES)}"
            )
        if origin == "original":
            if license_name != "MIT":
                fail(f"catalog entry {pet_id}: original pets must use MIT")
            if source_url != ORIGINAL_SOURCE_URL:
                fail(
                    f"catalog entry {pet_id}: original pets must use sourceUrl "
                    f"{ORIGINAL_SOURCE_URL!r}"
                )
        else:
            if source_url == ORIGINAL_SOURCE_URL:
                fail(f"catalog entry {pet_id}: imported pets need an upstream sourceUrl")
            license_file = IMPORTED_LICENSE_FILES.get((source_url, license_name))
            if license_file is None:
                fail(
                    f"catalog entry {pet_id}: imported source/license pair needs "
                    "an explicit license file mapping"
                )
            if not license_file.is_file():
                fail(
                    f"catalog entry {pet_id}: missing imported license file "
                    f"{license_file.relative_to(ROOT)}"
                )

        folder = str(entry["folder"])
        if not folder.startswith("pets/"):
            fail(f"catalog entry {pet_id}: folder must start with pets/")
        if folder not in pet_folders:
            fail(f"catalog entry {pet_id}: folder {folder!r} does not exist as a valid pet")
        if pet_id not in pet_ids:
            fail(f"catalog entry {pet_id}: id does not match a valid pet manifest")
        if folder not in notice_text:
            fail(f"catalog entry {pet_id}: folder missing from NOTICE.md")

    missing_from_catalog = sorted(pet_ids - seen_ids)
    if missing_from_catalog:
        fail(f"valid pet folders missing from catalog/pets.json: {missing_from_catalog}")

    return catalog


def validate_packs(catalog: list[dict[str, object]]) -> dict[str, list[str]]:
    raw_packs = load_json(PACKS)
    if not isinstance(raw_packs, dict):
        fail("catalog/packs.json must be an object")

    catalog_ids = {str(entry["id"]) for entry in catalog}
    packs: dict[str, list[str]] = {}
    for name, values in raw_packs.items():
        if not isinstance(name, str) or not name:
            fail("catalog/packs.json contains an invalid pack name")
        if not isinstance(values, list) or not values:
            fail(f"pack {name!r} must be a non-empty array")
        if not all(isinstance(item, str) and item for item in values):
            fail(f"pack {name!r} must contain pet ids")
        missing = sorted(set(values) - catalog_ids)
        if missing:
            fail(f"pack {name!r} references unknown pet ids: {', '.join(missing)}")
        duplicates = sorted({pet_id for pet_id in values if values.count(pet_id) > 1})
        if duplicates:
            fail(f"pack {name!r} contains duplicate pet ids: {', '.join(duplicates)}")
        packs[name] = list(values)
    return packs


def main() -> None:
    if not PETS.is_dir():
        fail("missing pets directory")

    results = []
    for folder in sorted(path for path in PETS.iterdir() if path.is_dir()):
        results.append(validate_pet(folder))

    catalog = validate_catalog(results)
    packs = validate_packs(catalog)
    print(
        json.dumps(
            {"ok": True, "pets": results, "catalogEntries": len(catalog), "packs": sorted(packs)},
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
