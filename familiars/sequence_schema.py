"""Normalize and validate reusable Familiars sequence recipes."""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any

from . import pet_assets
from .limits import (
    ALLOWED_LAYOUTS,
    ALLOWED_OUTPUT_FORMATS,
    DEFAULT_OUTPUT_ROOT,
    MAX_BEAT_SECONDS,
    MAX_FPS,
    MAX_HEIGHT,
    MAX_PETS_PER_SCENE,
    MAX_PIXELS,
    MAX_SCENES,
    MAX_WIDTH,
)
from .pet_assets import ROOT, STATE_CAPTIONS, STATE_ORDER
from .sequence_presets import preset as load_preset
from .sequence_presets import profile as load_profile
from .sequence_presets import theme as load_theme


class SequenceSchemaError(ValueError):
    """Raised when a sequence recipe cannot be rendered safely."""


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "familiars-sequence"


def load_recipe(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SequenceSchemaError(f"missing recipe {path}") from exc
    except json.JSONDecodeError as exc:
        raise SequenceSchemaError(f"{path} is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise SequenceSchemaError(f"{path} must contain a JSON object")
    return data


def merge_dicts(*values: dict[str, Any] | None) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for value in values:
        if not value:
            continue
        for key, item in value.items():
            if isinstance(item, dict) and isinstance(result.get(key), dict):
                result[key] = merge_dicts(result[key], item)
            else:
                result[key] = copy.deepcopy(item)
    return result


def normalize_recipe(
    raw: dict[str, Any],
    *,
    output_dir: Path | None = None,
    outputs: list[str] | None = None,
    preset_name: str | None = None,
    theme_name: str | None = None,
    output_root: Path | None = None,
    allow_output_outside_root: bool = True,
) -> dict[str, Any]:
    recipe_preset_name = preset_name or _string(raw.get("preset"), "preset", default="spotlight")
    preset = load_preset(recipe_preset_name)
    recipe_theme_name = theme_name or _string(raw.get("theme"), "theme", default=_string(preset.get("theme"), "preset.theme", default="familiars-dark"))
    theme = load_theme(recipe_theme_name)

    title = _string(raw.get("title"), "title", default=_string(preset.get("title"), "preset.title", default="Familiars"))
    slug = slugify(_string(raw.get("slug"), "slug", default=title))
    width = _bounded_int(raw.get("width", preset.get("width", 640)), "width", MAX_WIDTH)
    height = _bounded_int(raw.get("height", preset.get("height", 360)), "height", MAX_HEIGHT)
    if width * height > MAX_PIXELS:
        raise SequenceSchemaError(f"width * height must be at most {MAX_PIXELS:,} pixels")
    fps = _bounded_int(raw.get("fps", preset.get("fps", 12)), "fps", MAX_FPS)
    beat_seconds = _bounded_number(raw.get("beatSeconds", preset.get("beatSeconds", 0.9)), "beatSeconds", MAX_BEAT_SECONDS)

    normalized_outputs = _normalize_outputs(
        raw.get("outputs", preset.get("outputs", ["gif", "poster"])),
        override_dir=output_dir,
        override_formats=outputs,
        output_root=output_root or DEFAULT_OUTPUT_ROOT,
        allow_output_outside_root=allow_output_outside_root,
    )

    brand = merge_dicts(theme.get("brand") if isinstance(theme.get("brand"), dict) else None, preset.get("brand") if isinstance(preset.get("brand"), dict) else None, raw.get("brand") if isinstance(raw.get("brand"), dict) else None)
    captions = merge_dicts(theme.get("captions") if isinstance(theme.get("captions"), dict) else None, preset.get("captions") if isinstance(preset.get("captions"), dict) else None, raw.get("captions") if isinstance(raw.get("captions"), dict) else None)

    scenes_raw = raw.get("scenes")
    if scenes_raw is None:
        raise SequenceSchemaError("recipe missing scenes")
    if not isinstance(scenes_raw, list) or not scenes_raw:
        raise SequenceSchemaError("scenes must be a non-empty array")
    if len(scenes_raw) > MAX_SCENES:
        raise SequenceSchemaError(f"scenes may contain at most {MAX_SCENES} entries")

    normalized_scenes = [
        _normalize_scene(
            scene,
            index=index,
            default_layout=_string(preset.get("layout"), "preset.layout", default="spotlight"),
            default_beats=preset.get("beats", "profile.best"),
            default_beat_seconds=beat_seconds,
        )
        for index, scene in enumerate(scenes_raw, start=1)
    ]

    return {
        "version": 1,
        "title": title,
        "subtitle": _optional_string(raw.get("subtitle"), "subtitle"),
        "slug": slug,
        "preset": recipe_preset_name,
        "theme": recipe_theme_name,
        "width": width,
        "height": height,
        "fps": fps,
        "beatSeconds": beat_seconds,
        "outputs": normalized_outputs,
        "themeData": theme,
        "brand": brand,
        "captions": captions,
        "scenes": normalized_scenes,
    }


def recipe_from_pet(pet_id: str, preset_name: str, theme_name: str | None = None, title: str | None = None) -> dict[str, Any]:
    pet_assets.pet_entry(pet_id)
    return {
        "version": 1,
        "title": title or pet_assets.display_name(pet_id),
        "preset": preset_name,
        **({"theme": theme_name} if theme_name else {}),
        "slug": slugify(f"{pet_id}-{preset_name}"),
        "scenes": [{"pet": pet_id, "beats": "profile.best"}],
    }


def recipe_from_pack(pack: str, preset_name: str, theme_name: str | None = None, title: str | None = None) -> dict[str, Any]:
    ids = pet_assets.pack_pet_ids(pack)
    if preset_name == "comparison":
        scenes: list[dict[str, Any]] = [{"layout": "comparison", "pets": ids[:6], "beats": "all-states"}]
    else:
        scenes = [{"pet": pet_id, "beats": "profile.best"} for pet_id in ids[:8]]
    return {
        "version": 1,
        "title": title or pack.replace("-", " ").title(),
        "preset": preset_name,
        **({"theme": theme_name} if theme_name else {}),
        "slug": slugify(f"{pack}-{preset_name}"),
        "scenes": scenes,
    }


def _normalize_outputs(
    raw: Any,
    *,
    override_dir: Path | None,
    override_formats: list[str] | None,
    output_root: Path,
    allow_output_outside_root: bool,
) -> dict[str, Any]:
    default_directory = "output/sequences"
    if isinstance(raw, list):
        formats = raw
        directory = default_directory
    elif isinstance(raw, dict):
        formats = raw.get("formats", ["gif", "poster"])
        directory = raw.get("dir", default_directory)
    else:
        raise SequenceSchemaError("outputs must be an array or object")

    if override_formats is not None:
        formats = override_formats
    if not isinstance(formats, list) or not formats:
        raise SequenceSchemaError("outputs.formats must be a non-empty array")
    normalized_formats = []
    for item in formats:
        if not isinstance(item, str):
            raise SequenceSchemaError("outputs.formats must contain strings")
        if item not in ALLOWED_OUTPUT_FORMATS:
            raise SequenceSchemaError(f"unsupported output format {item!r}; choose {', '.join(sorted(ALLOWED_OUTPUT_FORMATS))}")
        if item not in normalized_formats:
            normalized_formats.append(item)

    root = output_root.expanduser().resolve()
    output_dir = override_dir if override_dir is not None else Path(_string(directory, "outputs.dir", default=default_directory))
    output_dir = output_dir.expanduser()
    if not allow_output_outside_root and override_dir is None and str(output_dir) == default_directory:
        resolved_output_dir = root
    elif output_dir.is_absolute():
        resolved_output_dir = output_dir.resolve()
    else:
        base = ROOT if allow_output_outside_root else root
        resolved_output_dir = (base / output_dir).resolve()

    if not allow_output_outside_root:
        try:
            resolved_output_dir.relative_to(root)
        except ValueError as exc:
            raise SequenceSchemaError(f"outputs.dir must stay inside {root}") from exc

    return {"formats": normalized_formats, "dir": resolved_output_dir}


def _normalize_scene(raw: Any, *, index: int, default_layout: str, default_beats: Any, default_beat_seconds: float) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise SequenceSchemaError(f"scene {index} must be an object")
    layout = _string(raw.get("layout"), f"scene {index}.layout", default=default_layout)
    if layout not in ALLOWED_LAYOUTS:
        raise SequenceSchemaError(f"scene {index}.layout must be one of {', '.join(sorted(ALLOWED_LAYOUTS))}")
    beat_seconds = _bounded_number(raw.get("beatSeconds", default_beat_seconds), f"scene {index}.beatSeconds", MAX_BEAT_SECONDS)
    scene_title = _optional_string(raw.get("title"), f"scene {index}.title")
    scene_subtitle = _optional_string(raw.get("subtitle"), f"scene {index}.subtitle")
    scene_beats = raw.get("beats", default_beats)

    pets: list[Any]
    if "pet" in raw:
        pets = [raw["pet"]]
    elif "pets" in raw:
        pets_raw = raw["pets"]
        if not isinstance(pets_raw, list) or not pets_raw:
            raise SequenceSchemaError(f"scene {index}.pets must be a non-empty array")
        pets = pets_raw
    else:
        raise SequenceSchemaError(f"scene {index} must include pet or pets")
    if len(pets) > MAX_PETS_PER_SCENE:
        raise SequenceSchemaError(f"scene {index}.pets may contain at most {MAX_PETS_PER_SCENE} entries")

    entries = [_normalize_pet_sequence(item, scene_beats, f"scene {index}") for item in pets]
    if len(entries) > 1 and layout == "spotlight":
        layout = "comparison"

    return {
        "layout": layout,
        "title": scene_title,
        "subtitle": scene_subtitle,
        "beatSeconds": beat_seconds,
        "pets": entries,
    }


def _normalize_pet_sequence(raw: Any, inherited_beats: Any, label: str) -> dict[str, Any]:
    if isinstance(raw, str):
        pet_id = raw
        beats_spec = inherited_beats
        title = None
        subtitle = None
    elif isinstance(raw, dict):
        pet_id = _string(raw.get("pet", raw.get("id")), f"{label}.pet")
        beats_spec = raw.get("beats", inherited_beats)
        title = _optional_string(raw.get("title"), f"{label}.{pet_id}.title")
        subtitle = _optional_string(raw.get("subtitle"), f"{label}.{pet_id}.subtitle")
    else:
        raise SequenceSchemaError(f"{label}.pets entries must be strings or objects")

    pet_assets.pet_entry(pet_id)
    profile = load_profile(pet_id)
    return {
        "pet": pet_id,
        "title": title or _optional_string(profile.get("title"), f"profile.{pet_id}.title") or pet_assets.display_name(pet_id),
        "subtitle": subtitle or _optional_string(profile.get("subtitle"), f"profile.{pet_id}.subtitle"),
        "beats": _resolve_beats(pet_id, beats_spec),
    }


def _resolve_beats(pet_id: str, spec: Any) -> list[dict[str, Any]]:
    profile = load_profile(pet_id)
    if spec is None or spec == "profile.best":
        spec = profile.get("best") or _default_best_beats()
    elif spec == "all-states":
        spec = [{"state": state, "caption": STATE_CAPTIONS[state]} for state in STATE_ORDER]
    elif isinstance(spec, str):
        named = profile.get(spec)
        if named is None:
            raise SequenceSchemaError(f"{pet_id}: unknown beat preset {spec!r}")
        spec = named

    if not isinstance(spec, list) or not spec:
        raise SequenceSchemaError(f"{pet_id}: beats must resolve to a non-empty array")

    beats = []
    for index, beat in enumerate(spec, start=1):
        if not isinstance(beat, dict):
            raise SequenceSchemaError(f"{pet_id}: beat {index} must be an object")
        state = _string(beat.get("state"), f"{pet_id}.beats[{index}].state")
        if state not in STATE_ORDER:
            raise SequenceSchemaError(f"{pet_id}: beat {index} uses unknown state {state!r}")
        caption = _string(beat.get("caption"), f"{pet_id}.beats[{index}].caption", default=STATE_CAPTIONS[state])
        duration = _optional_positive_number(beat.get("duration"), f"{pet_id}.beats[{index}].duration")
        beats.append({"state": state, "caption": caption, **({"duration": duration} if duration else {})})
    return beats


def _default_best_beats() -> list[dict[str, str]]:
    return [
        {"state": "idle", "caption": "calm baseline"},
        {"state": "waiting", "caption": "waiting for input"},
        {"state": "running", "caption": "working"},
        {"state": "review", "caption": "reviewing"},
        {"state": "failed", "caption": "needs recovery"},
    ]


def _string(value: Any, label: str, default: str | None = None) -> str:
    if value is None:
        if default is not None:
            return default
        raise SequenceSchemaError(f"{label} must be a string")
    if not isinstance(value, str) or not value.strip():
        raise SequenceSchemaError(f"{label} must be a non-empty string")
    return value.strip()


def _optional_string(value: Any, label: str) -> str | None:
    if value is None:
        return None
    return _string(value, label)


def _positive_int(value: Any, label: str) -> int:
    if not isinstance(value, int) or value <= 0:
        raise SequenceSchemaError(f"{label} must be a positive integer")
    return value


def _bounded_int(value: Any, label: str, maximum: int) -> int:
    result = _positive_int(value, label)
    if result > maximum:
        raise SequenceSchemaError(f"{label} must be at most {maximum}")
    return result


def _positive_number(value: Any, label: str) -> float:
    if not isinstance(value, (int, float)) or value <= 0:
        raise SequenceSchemaError(f"{label} must be a positive number")
    return float(value)


def _bounded_number(value: Any, label: str, maximum: float) -> float:
    result = _positive_number(value, label)
    if result > maximum:
        raise SequenceSchemaError(f"{label} must be at most {maximum:g}")
    return result


def _optional_positive_number(value: Any, label: str) -> float | None:
    if value is None:
        return None
    return _positive_number(value, label)
