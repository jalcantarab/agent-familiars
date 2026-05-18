"""Local MCP server for Familiars."""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from typing import Any

from .cli import default_dest, parse_outputs
from .pet_assets import ROOT, display_name, install_packs, manifest, pack_pet_ids, pet_folder, pet_ids
from .sequence_presets import presets, profiles, themes
from .sequence_renderer import render_outputs, render_preview_frame
from .sequence_schema import load_recipe, normalize_recipe, recipe_from_pack, recipe_from_pet


MCP_INSTALL_HINT = 'Install MCP support with `python -m pip install -e ".[mcp]"`.'


def output_root() -> Path:
    configured = os.environ.get("FAMILIARS_MCP_OUTPUT_ROOT")
    if configured:
        return Path(configured).expanduser().resolve()
    return (Path.cwd() / "output" / "mcp-sequences").resolve()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def json_text(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True)


def normalize_for_mcp(
    raw: dict[str, Any],
    *,
    output_dir: str | None = None,
    outputs: str | None = None,
    preset_name: str | None = None,
    theme_name: str | None = None,
) -> dict[str, Any]:
    return normalize_recipe(
        raw,
        output_dir=Path(output_dir).expanduser() if output_dir else None,
        outputs=parse_outputs(outputs),
        preset_name=preset_name,
        theme_name=theme_name,
        output_root=output_root(),
        allow_output_outside_root=False,
    )


def serializable_recipe(recipe: dict[str, Any]) -> dict[str, Any]:
    printable = dict(recipe)
    printable["outputs"] = {
        "formats": recipe["outputs"]["formats"],
        "dir": str(recipe["outputs"]["dir"]),
    }
    return printable


def render_summary(recipe: dict[str, Any]) -> dict[str, Any]:
    written = render_outputs(recipe)
    return {
        "title": recipe["title"],
        "slug": recipe["slug"],
        "outputs": [str(path) for path in written],
        "outputRoot": str(output_root()),
    }


def install_local_pet(pet_id: str, destination: Path) -> Path:
    source_dir = pet_folder(pet_id)
    dest_dir = destination / pet_id
    dest_dir.mkdir(parents=True, exist_ok=True)
    for filename in ("pet.json", "spritesheet.webp"):
        source = source_dir / filename
        if not source.is_file():
            raise ValueError(f"{source_dir} is missing {filename}")
        shutil.copy2(source, dest_dir / filename)
    return dest_dir


def validate_installed_pet(dest_dir: Path) -> None:
    manifest_path = dest_dir / "pet.json"
    sheet_path = dest_dir / "spritesheet.webp"
    if not manifest_path.is_file() or not sheet_path.is_file():
        raise ValueError(f"{dest_dir} did not receive both pet.json and spritesheet.webp")
    pet_manifest = read_json(manifest_path)
    if not isinstance(pet_manifest, dict):
        raise ValueError(f"{manifest_path} must be a JSON object")
    for key in ("id", "displayName", "description", "spritesheetPath"):
        if not isinstance(pet_manifest.get(key), str) or not pet_manifest[key].strip():
            raise ValueError(f"{manifest_path} is missing non-empty {key}")
    if not (dest_dir / pet_manifest["spritesheetPath"]).is_file():
        raise ValueError(f"{manifest_path} references missing spritesheet {pet_manifest['spritesheetPath']}")


def build_server() -> Any:
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:
        raise RuntimeError(MCP_INSTALL_HINT) from exc

    mcp = FastMCP(
        "Familiars",
        instructions=(
            "Explore installable Codex pets, create sequence recipes, render "
            "small showcase assets, and install selected familiars locally."
        ),
    )

    @mcp.resource("familiars://catalog/pets")
    def catalog_pets() -> str:
        """Return the packaged pet catalog."""
        return (ROOT / "catalog" / "pets.json").read_text(encoding="utf-8")

    @mcp.resource("familiars://catalog/packs")
    def catalog_packs() -> str:
        """Return curated pack definitions."""
        return (ROOT / "catalog" / "packs.json").read_text(encoding="utf-8")

    @mcp.resource("familiars://sequence/presets")
    def sequence_presets() -> str:
        """Return built-in sequence presets."""
        return json_text(presets())

    @mcp.resource("familiars://sequence/themes")
    def sequence_themes() -> str:
        """Return built-in sequence themes."""
        return json_text(themes())

    @mcp.resource("familiars://pet/{pet_id}/profile")
    def pet_profile(pet_id: str) -> str:
        """Return one pet's sequence profile."""
        return json_text(profiles().get(pet_id, {}))

    @mcp.resource("familiars://pet/{pet_id}/manifest")
    def pet_manifest(pet_id: str) -> str:
        """Return one pet's Codex pet manifest."""
        return json_text(manifest(pet_id))

    @mcp.resource("familiars://example/sequences/{name}")
    def example_sequence(name: str) -> str:
        """Return a committed sequence example by file name or slug."""
        safe_name = Path(name).name
        if not safe_name.endswith(".json"):
            safe_name = f"{safe_name}.json"
        path = ROOT / "examples" / "sequences" / safe_name
        if not path.is_file():
            raise ValueError(f"unknown sequence example {name!r}")
        return path.read_text(encoding="utf-8")

    @mcp.tool()
    def validate_sequence_recipe(recipe_json: str) -> dict[str, Any]:
        """Validate a sequence recipe JSON string without writing output."""
        raw = json.loads(recipe_json)
        if not isinstance(raw, dict):
            raise ValueError("recipe must be a JSON object")
        recipe = normalize_for_mcp(raw)
        render_preview_frame(recipe)
        return {
            "ok": True,
            "recipe": serializable_recipe(recipe),
        }

    @mcp.tool()
    def create_sequence_recipe(
        pet_id: str = "",
        pack: str = "",
        preset: str = "",
        theme: str = "",
        title: str = "",
    ) -> dict[str, Any]:
        """Create a normalized sequence recipe for one pet or one pack."""
        if pet_id and pack:
            raise ValueError("pass either pet_id or pack, not both")
        if pet_id:
            raw = recipe_from_pet(pet_id, preset or "spotlight", theme or None, title or None)
        elif pack:
            raw = recipe_from_pack(pack, preset or "comparison", theme or None, title or None)
        else:
            raise ValueError("pass pet_id or pack")
        return serializable_recipe(normalize_for_mcp(raw))

    @mcp.tool()
    def render_sequence(
        recipe_json: str,
        output_dir: str = "",
        outputs: str = "",
        preset_override: str = "",
        theme_override: str = "",
    ) -> dict[str, Any]:
        """Render a sequence recipe JSON string inside the MCP output root."""
        raw = json.loads(recipe_json)
        if not isinstance(raw, dict):
            raise ValueError("recipe must be a JSON object")
        recipe = normalize_for_mcp(
            raw,
            output_dir=output_dir or None,
            outputs=outputs or None,
            preset_name=preset_override or None,
            theme_name=theme_override or None,
        )
        return render_summary(recipe)

    @mcp.tool()
    def render_pet_sequence(
        pet_id: str,
        preset: str = "spotlight",
        theme: str = "",
        title: str = "",
        output_dir: str = "",
        outputs: str = "poster",
    ) -> dict[str, Any]:
        """Render a preset sequence for one familiar."""
        raw = recipe_from_pet(pet_id, preset, theme or None, title or None)
        recipe = normalize_for_mcp(raw, output_dir=output_dir or None, outputs=outputs or None)
        return render_summary(recipe)

    @mcp.tool()
    def render_pack_sequence(
        pack: str,
        preset: str = "comparison",
        theme: str = "",
        title: str = "",
        output_dir: str = "",
        outputs: str = "poster",
    ) -> dict[str, Any]:
        """Render a preset sequence for one familiar pack."""
        raw = recipe_from_pack(pack, preset, theme or None, title or None)
        recipe = normalize_for_mcp(raw, output_dir=output_dir or None, outputs=outputs or None)
        return render_summary(recipe)

    @mcp.tool()
    def install_familiar(
        pet_ids_csv: str = "",
        pack: str = "",
        install_all: bool = False,
        dest: str = "",
    ) -> dict[str, Any]:
        """Install one or more familiars into a local Codex pets directory."""
        requested = [item.strip() for item in pet_ids_csv.split(",") if item.strip()]
        if pack:
            requested.extend(pack_pet_ids(pack))
        if install_all:
            requested.extend(pet_ids())
        if not requested:
            raise ValueError("pass pet_ids_csv, pack, or install_all")

        destination = Path(dest).expanduser() if dest else default_dest()
        destination.mkdir(parents=True, exist_ok=True)

        installed = []
        seen = set()
        for pet_id in requested:
            if pet_id in seen:
                continue
            seen.add(pet_id)
            path = install_local_pet(pet_id, destination)
            validate_installed_pet(path)
            installed.append({"id": pet_id, "displayName": display_name(pet_id), "path": str(path)})

        return {
            "installed": installed,
            "next": "Open Codex Settings -> Personalization -> Pets -> Refresh custom pets.",
        }

    @mcp.tool()
    def validate_familiars() -> dict[str, Any]:
        """Validate packaged catalog, pack, profile, and example sequence data."""
        for pet_id in pet_ids():
            manifest(pet_id)
            normalize_for_mcp(recipe_from_pet(pet_id, "spotlight"))
        for pack in install_packs():
            pack_pet_ids(pack)
        examples = sorted((ROOT / "examples" / "sequences").glob("*.json"))
        for path in examples:
            recipe = normalize_for_mcp(load_recipe(path))
            render_preview_frame(recipe)
        return {
            "ok": True,
            "pets": len(pet_ids()),
            "packs": len(install_packs()),
            "presets": len(presets()),
            "themes": len(themes()),
            "sequenceExamples": len(examples),
            "outputRoot": str(output_root()),
        }

    @mcp.prompt()
    def choose_familiar() -> str:
        """Help a user choose a familiar."""
        return (
            "Ask what the user wants near them during agent work: quiet status, "
            "product humor, review help, failure recovery, or a signature pet. "
            "Then suggest one or two Familiars by id and explain the state "
            "language briefly."
        )

    @mcp.prompt()
    def create_familiar_sequence(pet_id: str = "", pack: str = "") -> str:
        """Guide a user through creating a familiar sequence."""
        subject = f"pet `{pet_id}`" if pet_id else f"pack `{pack}`" if pack else "a pet or pack"
        return (
            f"Create a concise sequence for {subject}. Prefer `profile.best`, "
            "keep captions short, render a poster first, then render GIF or MP4 "
            "only after the layout reads clearly."
        )

    @mcp.prompt()
    def review_pet_motion(pet_id: str) -> str:
        """Guide a motion review for one pet."""
        return (
            f"Review `{pet_id}` across idle, waiting, running, failed, and review. "
            "Look for character consistency, readable state changes, no generic "
            "movement, and one memorable beat that belongs only to this familiar."
        )

    @mcp.prompt()
    def draft_pet_brief(pet_id: str = "") -> str:
        """Draft a pet creation brief."""
        subject = f" for `{pet_id}`" if pet_id else ""
        return (
            f"Draft a compact Familiar brief{subject}: personality, silhouette, "
            "state-specific behavior, what should make a user smile, and what "
            "must stay restrained so it remains pleasant during long work."
        )

    return mcp


def main() -> None:
    try:
        build_server().run()
    except RuntimeError as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    main()
