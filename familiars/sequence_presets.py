"""Sequence renderer presets, themes, and pet profiles."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from .pet_assets import ROOT


PRESETS = ROOT / "catalog" / "sequence-presets.json"
THEMES = ROOT / "catalog" / "sequence-themes.json"
PROFILES = ROOT / "catalog" / "pet-profiles.json"


class SequencePresetError(ValueError):
    """Raised when sequence configuration data is invalid."""


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SequencePresetError(f"missing {path.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise SequencePresetError(f"{path.relative_to(ROOT)} is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise SequencePresetError(f"{path.relative_to(ROOT)} must be a JSON object")
    return data


@lru_cache(maxsize=1)
def presets() -> dict[str, dict[str, Any]]:
    return _validate_named_objects(load_json(PRESETS), "preset")


@lru_cache(maxsize=1)
def themes() -> dict[str, dict[str, Any]]:
    return _validate_named_objects(load_json(THEMES), "theme")


@lru_cache(maxsize=1)
def profiles() -> dict[str, dict[str, Any]]:
    return _validate_named_objects(load_json(PROFILES), "profile")


def _validate_named_objects(data: dict[str, Any], label: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for key, value in data.items():
        if not isinstance(key, str) or not key:
            raise SequencePresetError(f"{label} keys must be non-empty strings")
        if not isinstance(value, dict):
            raise SequencePresetError(f"{label} {key!r} must be an object")
        result[key] = value
    return result


def preset(name: str) -> dict[str, Any]:
    try:
        return presets()[name]
    except KeyError as exc:
        raise SequencePresetError(f"unknown preset {name!r}; choose {', '.join(sorted(presets()))}") from exc


def theme(name: str) -> dict[str, Any]:
    try:
        return themes()[name]
    except KeyError as exc:
        raise SequencePresetError(f"unknown theme {name!r}; choose {', '.join(sorted(themes()))}") from exc


def profile(pet_id: str) -> dict[str, Any]:
    return profiles().get(pet_id, {})
