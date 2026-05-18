# MCP Server

Familiars includes a local MCP server for agents that can inspect the catalog,
create sequence recipes, render small showcase assets, and install selected
pets into Codex.

Install the optional MCP dependencies from a clone:

```bash
python -m pip install -e ".[mcp]"
```

Run the server over stdio:

```bash
familiars-mcp
```

This is not a hosted service. Your agent client starts `familiars-mcp` as a
local subprocess and speaks MCP over that process's standard input and standard
output. The server reads the packaged Familiars catalog from the installed
Python package or local checkout, writes generated media to local disk, and can
copy selected pets into your local Codex pets folder.

Most agent clients expect a command configuration. Use the executable from the
same environment where you installed the package:

```json
{
  "command": "familiars-mcp"
}
```

## Safety

Rendered files stay inside a controlled output root. By default that root is:

```text
./output/mcp-sequences
```

Override it when you want all agent-rendered media somewhere explicit:

```bash
FAMILIARS_MCP_OUTPUT_ROOT=/tmp/familiars-mcp familiars-mcp
```

The server rejects recipe output paths that try to write outside that root. Tool
responses return paths and summaries, not binary media payloads.

## Tools

- `validate_sequence_recipe`: validate a recipe JSON string and render one
  preview frame in memory.
- `create_sequence_recipe`: create a normalized recipe for one pet or pack.
- `render_sequence`: render a provided recipe JSON string.
- `render_pet_sequence`: render a preset sequence for one pet.
- `render_pack_sequence`: render a preset sequence for one pack.
- `install_familiar`: install one or more pets into the local Codex pets folder.
- `validate_familiars`: validate packaged catalog, pack, profile, and example
  sequence data.

## Resources

- `familiars://catalog/pets`
- `familiars://catalog/packs`
- `familiars://sequence/presets`
- `familiars://sequence/themes`
- `familiars://pet/{pet_id}/profile`
- `familiars://pet/{pet_id}/manifest`
- `familiars://example/sequences/{name}`

## Prompts

- `choose_familiar`
- `create_familiar_sequence`
- `review_pet_motion`
- `draft_pet_brief`

For the plain terminal surface, see [CLI](CLI.md).

## Smoke Test

From a clone with the MCP extra installed, run:

```bash
python scripts/smoke_mcp_client.py
```

The smoke test launches the real stdio server, connects with the Python MCP
client, lists tools/resources/prompts, reads the pack catalog, validates the
catalog, renders one poster inside a temporary output root, installs one
familiar into a temporary Codex pets directory, and confirms unsafe output paths
are rejected.
