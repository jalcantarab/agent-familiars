"""Load Codex pet sprites and catalog metadata."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from PIL import Image


def _has_familiar_data(path: Path) -> bool:
    return (path / "catalog" / "pets.json").is_file() and (path / "pets").is_dir()


def _data_root() -> Path:
    env_root = os.environ.get("FAMILIARS_DATA_ROOT")
    candidates = []
    if env_root:
        candidates.append(Path(env_root).expanduser())
    package_root = Path(__file__).resolve().parent
    candidates.extend([package_root.parent, package_root / "_bundle"])
    for candidate in candidates:
        resolved = candidate.resolve()
        if _has_familiar_data(resolved):
            return resolved
    return package_root.parent.resolve()


ROOT = _data_root()
PETS = ROOT / "pets"
CATALOG = ROOT / "catalog" / "pets.json"
PACKS = ROOT / "catalog" / "packs.json"
CELL_WIDTH = 192
CELL_HEIGHT = 208
STATE_ROWS = [
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
STATE_ORDER = [state for state, _count in STATE_ROWS]
STATE_FRAME_COUNTS = dict(STATE_ROWS)
STATE_INDEX = {state: index for index, (state, _count) in enumerate(STATE_ROWS)}
STATE_CAPTIONS = {
    "idle": "calm baseline",
    "running-right": "moving right",
    "running-left": "moving left",
    "waving": "small signal",
    "jumping": "quick lift",
    "failed": "needs recovery",
    "waiting": "waiting for input",
    "running": "working",
    "review": "reviewing",
}


class PetAssetError(ValueError):
    """Raised when a pet asset or metadata file cannot be used."""


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise PetAssetError(f"missing {path.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise PetAssetError(f"{path.relative_to(ROOT)} is not valid JSON: {exc}") from exc


@lru_cache(maxsize=1)
def catalog() -> dict[str, dict[str, Any]]:
    data = load_json(CATALOG)
    if not isinstance(data, list):
        raise PetAssetError("catalog/pets.json must be an array")
    result: dict[str, dict[str, Any]] = {}
    for entry in data:
        if not isinstance(entry, dict) or not isinstance(entry.get("id"), str):
            raise PetAssetError("catalog/pets.json contains an invalid entry")
        result[entry["id"]] = entry
    return result


def pet_ids() -> list[str]:
    return sorted(catalog())


def pet_entry(pet_id: str) -> dict[str, Any]:
    try:
        return catalog()[pet_id]
    except KeyError as exc:
        raise PetAssetError(f"unknown pet id {pet_id!r}") from exc


def display_name(pet_id: str) -> str:
    entry = pet_entry(pet_id)
    value = entry.get("displayName")
    return value if isinstance(value, str) and value else pet_id


def pet_folder(pet_id: str) -> Path:
    folder = pet_entry(pet_id).get("folder")
    if not isinstance(folder, str) or not folder.startswith("pets/"):
        raise PetAssetError(f"catalog entry {pet_id!r} has invalid folder")
    path = ROOT / folder
    if not path.is_dir():
        raise PetAssetError(f"{folder} does not exist")
    return path


@lru_cache(maxsize=None)
def manifest(pet_id: str) -> dict[str, Any]:
    path = pet_folder(pet_id) / "pet.json"
    data = load_json(path)
    if not isinstance(data, dict):
        raise PetAssetError(f"{path.relative_to(ROOT)} must be a JSON object")
    return data


def spritesheet_path(pet_id: str) -> Path:
    sheet = manifest(pet_id).get("spritesheetPath")
    if not isinstance(sheet, str) or not sheet:
        raise PetAssetError(f"{pet_id}: pet.json missing spritesheetPath")
    path = pet_folder(pet_id) / sheet
    if not path.is_file():
        raise PetAssetError(f"{pet_id}: missing {sheet}")
    return path


@lru_cache(maxsize=None)
def atlas(pet_id: str) -> Image.Image:
    with Image.open(spritesheet_path(pet_id)) as opened:
        return opened.convert("RGBA")


@lru_cache(maxsize=None)
def state_frames(pet_id: str, state: str) -> tuple[Image.Image, ...]:
    if state not in STATE_INDEX:
        raise PetAssetError(f"unknown state {state!r}")
    row = STATE_INDEX[state]
    count = STATE_FRAME_COUNTS[state]
    source = atlas(pet_id)
    return tuple(
        source.crop(
            (
                column * CELL_WIDTH,
                row * CELL_HEIGHT,
                (column + 1) * CELL_WIDTH,
                (row + 1) * CELL_HEIGHT,
            )
        )
        for column in range(count)
    )


def state_frame(pet_id: str, state: str, tick: int) -> Image.Image:
    frames = state_frames(pet_id, state)
    return frames[tick % len(frames)]


def fit_sprite(sprite: Image.Image, target_height: int) -> Image.Image:
    bbox = sprite.getbbox()
    if bbox is None:
        return Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    cropped = sprite.crop(bbox)
    scale = target_height / cropped.height
    width = max(1, round(cropped.width * scale))
    height = max(1, round(cropped.height * scale))
    return cropped.resize((width, height), Image.Resampling.LANCZOS)


@lru_cache(maxsize=1)
def install_packs() -> dict[str, list[str]]:
    packs = load_json(PACKS)
    if not isinstance(packs, dict):
        raise PetAssetError("catalog/packs.json must be an object")
    result: dict[str, list[str]] = {}
    for name, values in packs.items():
        if not isinstance(name, str) or not name:
            raise PetAssetError("catalog/packs.json contains an invalid pack name")
        if not isinstance(values, list) or not all(isinstance(item, str) for item in values):
            raise PetAssetError(f"pack {name!r} must be an array of pet ids")
        result[name] = list(values)
    return result


def pack_pet_ids(pack: str) -> list[str]:
    packs = install_packs()
    if pack not in packs:
        raise PetAssetError(f"unknown pack {pack!r}; choose {', '.join(sorted(packs))}")
    ids = packs[pack]
    missing = [pet_id for pet_id in ids if pet_id not in catalog()]
    if missing:
        raise PetAssetError(f"pack {pack!r} contains unknown pet ids: {', '.join(missing)}")
    return ids
