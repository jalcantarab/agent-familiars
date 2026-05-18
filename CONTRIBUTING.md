# Contributing

Familiars collects installable Codex pets that are fun, useful, and safe to
redistribute.

## Setup

```bash
git clone https://github.com/jalcantarab/agent-familiars.git
cd agent-familiars
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

Install one pet locally:

```bash
python3 scripts/install_pet.py zentri
```

## Branch And PR Flow

Use a short-lived branch. Do not push directly to `main`.

```bash
git switch -c jab/<short-topic>
```

Open a PR into `main` and keep it focused. A good PR usually does one of these:

- adds or repairs one pet
- improves installation or validation tooling
- improves attribution, licensing, or documentation
- expands a planned pet brief

Use `jab/` for public work in this repository. The branch name should tell a
reviewer what changed without making them solve a riddle.

## Issues

Use the issue form that matches the work:

- Bug report: installation, validation, packaging, or broken output.
- Feature request: CLI, MCP, renderer, installer, catalog, or docs ideas.
- Pet request: a new original or clearly licensed familiar concept.
- Pet polish: an existing pet whose motion, readability, or personality needs
  another pass.

Discussions and project boards are intentionally not required for the first
public release. Issues are enough until the volume proves otherwise.

## Adding A Pet

Each pet folder must contain:

```text
pets/<pet-id>/
├── pet.json
└── spritesheet.webp
```

The atlas must be `1536x1872`, transparent-capable, and arranged as 8 columns
by 9 rows of `192x208` cells.

Update these files when adding a pet:

- `catalog/pets.json`
- `NOTICE.md`
- a license file under `licenses/` when importing third-party assets

## Licensing Expectations

Original contributions should use MIT unless maintainers agree to another
license before merge.

Imported assets must have a source URL, creator or author name, explicit
license, and a copied license text when the license is not already covered by
the root MIT license.

Do not submit pets based on copyrighted characters, fan art, brand mascots,
company logos, product marks, non-commercial licenses, no-derivatives licenses,
or assets without a clear license.

Good pets have one clear job and a motion language that belongs to that job.
Generic waving is not a personality. It is a screensaver with paws.

## Validation

Run:

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
python -m pip install -e ".[mcp]"
python scripts/smoke_mcp_client.py
python -m pip install -e .
familiars validate
```

If `python3` does not have Pillow installed locally, use the Python interpreter
that has the repository dependencies available.

Maintainer release and branch-protection guidance lives in
[docs/MAINTAINER_WORKFLOW.md](docs/MAINTAINER_WORKFLOW.md).
