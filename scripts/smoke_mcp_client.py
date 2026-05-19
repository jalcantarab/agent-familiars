#!/usr/bin/env python3
"""Smoke test the Familiars MCP server through a real stdio client session."""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_TOOLS = {
    "validate_sequence_recipe",
    "create_sequence_recipe",
    "render_sequence",
    "render_pet_sequence",
    "render_pack_sequence",
    "install_familiar",
    "validate_familiars",
}
EXPECTED_RESOURCES = {
    "familiars://catalog/pets",
    "familiars://catalog/packs",
    "familiars://sequence/presets",
    "familiars://sequence/themes",
}
EXPECTED_PROMPTS = {
    "choose_familiar",
    "create_familiar_sequence",
    "review_pet_motion",
    "draft_pet_brief",
}


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def decode_tool_json(result: Any, tool_name: str) -> dict[str, Any]:
    if getattr(result, "isError", False):
        fail(f"{tool_name} returned an MCP error: {result.content}")
    if not getattr(result, "content", None):
        fail(f"{tool_name} returned no content")
    text = getattr(result.content[0], "text", "")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        fail(f"{tool_name} returned non-JSON text: {exc}")
    if not isinstance(payload, dict):
        fail(f"{tool_name} returned {type(payload).__name__}, expected object")
    return payload


def assert_contains(label: str, found: set[str], expected: set[str]) -> None:
    missing = sorted(expected - found)
    if missing:
        fail(f"{label} missing: {', '.join(missing)}")


async def run_smoke() -> None:
    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
    except ImportError as exc:
        raise SystemExit('Install MCP support with `python -m pip install -e ".[mcp]"`.') from exc

    with tempfile.TemporaryDirectory(prefix="familiars-mcp-smoke-") as temp_dir:
        temp = Path(temp_dir)
        output_root = temp / "outputs"
        install_root = temp / "codex-pets"
        env = os.environ.copy()
        env["FAMILIARS_MCP_OUTPUT_ROOT"] = str(output_root)

        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "familiars.mcp_server"],
            env=env,
            cwd=ROOT,
        )

        async with stdio_client(params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                init = await session.initialize()
                server_name = getattr(getattr(init, "serverInfo", None), "name", "")
                if server_name != "Familiars":
                    fail(f"unexpected MCP server name: {server_name!r}")

                tools = await session.list_tools()
                assert_contains("MCP tools", {tool.name for tool in tools.tools}, EXPECTED_TOOLS)

                resources = await session.list_resources()
                assert_contains(
                    "MCP resources",
                    {str(resource.uri) for resource in resources.resources},
                    EXPECTED_RESOURCES,
                )

                prompts = await session.list_prompts()
                assert_contains("MCP prompts", {prompt.name for prompt in prompts.prompts}, EXPECTED_PROMPTS)

                packs_resource = await session.read_resource("familiars://catalog/packs")
                packs_text = getattr(packs_resource.contents[0], "text", "")
                packs = json.loads(packs_text)
                if not isinstance(packs, dict) or "product-tropes" not in packs:
                    fail("catalog packs resource should include product-tropes")

                pets_resource = await session.read_resource("familiars://catalog/pets")
                pets_text = getattr(pets_resource.contents[0], "text", "")
                pets = json.loads(pets_text)
                if not isinstance(pets, list):
                    fail("catalog pets resource should be a list")

                validation = decode_tool_json(await session.call_tool("validate_familiars", {}), "validate_familiars")
                if validation.get("pets") != len(pets) or validation.get("packs") != len(packs):
                    fail(f"unexpected validation summary: {validation}")

                recipe = decode_tool_json(
                    await session.call_tool(
                        "create_sequence_recipe",
                        {"pet_id": "signal-surface", "preset": "spotlight"},
                    ),
                    "create_sequence_recipe",
                )
                if recipe.get("slug") != "signal-surface-spotlight":
                    fail(f"unexpected recipe slug: {recipe.get('slug')!r}")

                rendered = decode_tool_json(
                    await session.call_tool(
                        "render_pet_sequence",
                        {"pet_id": "signal-surface", "preset": "spotlight", "outputs": "poster"},
                    ),
                    "render_pet_sequence",
                )
                rendered_outputs = [Path(path) for path in rendered.get("outputs", [])]
                if len(rendered_outputs) != 1 or not rendered_outputs[0].is_file():
                    fail(f"render_pet_sequence did not write one poster: {rendered}")
                try:
                    rendered_outputs[0].resolve().relative_to(output_root.resolve())
                except ValueError:
                    fail(f"rendered output escaped MCP output root: {rendered_outputs[0]}")

                installed = decode_tool_json(
                    await session.call_tool(
                        "install_familiar",
                        {"pet_ids_csv": "zentri", "dest": str(install_root)},
                    ),
                    "install_familiar",
                )
                installed_items = installed.get("installed", [])
                if len(installed_items) != 1:
                    fail(f"install_familiar returned unexpected payload: {installed}")
                if not (install_root / "zentri" / "pet.json").is_file():
                    fail("install_familiar did not copy zentri/pet.json")
                if not (install_root / "zentri" / "spritesheet.webp").is_file():
                    fail("install_familiar did not copy zentri/spritesheet.webp")

                unsafe_recipe = json.dumps(
                    {
                        "title": "Unsafe Output",
                        "outputs": ["poster"],
                        "scenes": [{"pet": "zentri"}],
                    }
                )
                unsafe = await session.call_tool(
                    "render_sequence",
                    {"recipe_json": unsafe_recipe, "output_dir": "../outside"},
                )
                if not getattr(unsafe, "isError", False):
                    fail("render_sequence should reject output paths outside the MCP output root")

    print("mcp client smoke ok")


def main() -> None:
    try:
        import anyio
    except ImportError as exc:
        raise SystemExit('Install MCP support with `python -m pip install -e ".[mcp]"`.') from exc

    anyio.run(run_smoke)


if __name__ == "__main__":
    main()
