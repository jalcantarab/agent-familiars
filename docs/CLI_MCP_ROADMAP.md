# CLI And MCP Status

Familiars now ships the reusable sequence core as both a CLI and a local MCP
server. The project still keeps the original roadmap here because it explains
why the interfaces are shaped the way they are and what should stay true as the
tools grow.

Current public surface:

- `familiars` CLI for listing, installing, validating, and rendering.
- `familiars-mcp` local server for agent access to catalog, install, and render
  utilities.
- Shared recipe schemas and renderer limits used by both surfaces.
- Package data that includes catalog files, installable pets, examples,
  licenses, and brand assets.

## Phase 1: Harden The Core

Status: shipped in `v0.1.0`.

Goal: make the renderer safe and predictable enough for public automation.

Scope:

- add explicit render limits for dimensions, frame count, FPS, scene count, and
  pets per scene
- sanitize recipe slugs before using them in generated file names
- add an output-directory policy that can be permissive for the local CLI and
  strict for MCP tools
- move pack definitions from installer code into catalog data
- keep existing clone-based commands working
- expand validation so bad catalog profiles, packs, and sequence examples fail
  before release

Definition of done:

```bash
python scripts/validate_pets.py
python scripts/validate_design_specs.py
python scripts/validate_docs.py
python scripts/check_release_readiness.py
python scripts/render_brand_assets.py --check
python scripts/render_readme_cards.py --check
python scripts/render_previews.py --all --check
python scripts/render_sequence.py --check
python scripts/render_reel.py --check
PYTHONPYCACHEPREFIX=/tmp/agent-familiars-pycache python -m py_compile setup.py scripts/check_release_readiness.py scripts/install_pet.py scripts/render_brand_assets.py scripts/render_readme_cards.py scripts/render_previews.py scripts/render_sequence.py scripts/render_reel.py scripts/smoke_mcp_client.py scripts/validate_pets.py scripts/validate_design_specs.py scripts/validate_docs.py scripts/generate_signal_surface.py scripts/generate_state_instruments.py scripts/rotate_installed_pet_variant.py familiars/__init__.py familiars/cli.py familiars/limits.py familiars/mcp_server.py familiars/pet_assets.py familiars/sequence_presets.py familiars/sequence_schema.py familiars/sequence_renderer.py
```

## Phase 2: Ship An Installable CLI

Status: shipped in `v0.1.0`.

Goal: make Familiars useful from a normal terminal without asking people to run
repo-local scripts directly.

Scope:

- add Python package metadata
- include catalog, installable pet assets, docs, examples, licenses, and brand
  assets as package data
- expose a `familiars` console command
- keep the existing scripts as thin compatibility wrappers
- support:
  - `familiars list pets`
  - `familiars list packs`
  - `familiars list presets`
  - `familiars list themes`
  - `familiars install zentri`
  - `familiars install --pack starter`
  - `familiars render --pet no-knight --preset spotlight`
  - `familiars render --pack state-instruments --preset comparison`
  - `familiars render --recipe examples/sequences/no-knight-spotlight.json`
  - `familiars validate`

Definition of done:

```bash
python -m pip install -e .
familiars list packs
familiars render --pet no-knight --preset spotlight --outputs poster --output-dir /tmp/familiars-cli-smoke
familiars install zentri --dest /tmp/familiars-install-smoke --source local
familiars validate
PYTHONPYCACHEPREFIX=/tmp/agent-familiars-pycache python -m py_compile familiars/cli.py
python -m pip wheel . --no-deps -w /tmp/agent-familiars-wheelhouse
```

## Phase 3: Ship A Local MCP Server

Status: shipped in `v0.1.0`.

Goal: let agents discover pets, create sequence recipes, render previews, and
install familiars through a controlled tool surface.

Start with stdio transport. It is the simplest local contract and works well
for desktop agent clients. Streamable HTTP can come later if the tool becomes a
shared service.

Tools:

- `render_sequence`
- `render_pet_sequence`
- `render_pack_sequence`
- `validate_sequence_recipe`
- `install_familiar`
- `create_sequence_recipe`

Resources:

- `familiars://catalog/pets`
- `familiars://catalog/packs`
- `familiars://sequence/presets`
- `familiars://sequence/themes`
- `familiars://pet/{pet_id}/profile`
- `familiars://pet/{pet_id}/manifest`
- `familiars://example/sequences/{name}`

Prompts:

- `choose_familiar`
- `create_familiar_sequence`
- `review_pet_motion`
- `draft_pet_brief`

Definition of done:

```bash
python -m pip install -e ".[mcp]"
python -c "from familiars.mcp_server import build_server; build_server(); print('mcp ok')"
python scripts/smoke_mcp_client.py
python scripts/render_sequence.py --check
PYTHONPYCACHEPREFIX=/tmp/agent-familiars-pycache python -m py_compile familiars/mcp_server.py
```

The MCP server must default to a safe output root, must not write outside that
root unless explicitly configured by the user, and must return plain paths plus
human-readable summaries instead of dumping large binary payloads into tool
responses.

## Next Directions

The CLI and MCP server are intentionally small. The next useful layer is a
simple UI that reuses the same recipe shape:

1. choose a pet or pack
2. pick a preset and theme
3. edit captions or beats
4. render poster first
5. export GIF or MP4 when the composition works

Other likely follow-ups:

- saved user presets
- richer caption timing
- batch comparison cards for external pet submissions
- optional branded outro cards for generated social clips

These should only land when they make the renderer easier to use. A tool about
tiny companions does not need a giant cockpit.
