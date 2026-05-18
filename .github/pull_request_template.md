## What changed

-

## Branch hygiene

- [ ] This targets `main` through a PR; no direct push to `main` is needed.

## Pet checklist

- [ ] New or changed pets include `pet.json` and `spritesheet.webp`.
- [ ] Attribution and license details are updated in `NOTICE.md`, `catalog/pets.json`, and `catalog/packs.json` when needed.
- [ ] No non-commercial, fan-art, trademark-sensitive, or unlicensed assets were added.
- [ ] Contact sheet or preview output was reviewed when pet artwork changed.

## Validation

- [ ] `python scripts/validate_pets.py`
- [ ] `python scripts/validate_design_specs.py`
- [ ] `python scripts/validate_docs.py`
- [ ] `python scripts/check_release_readiness.py`
- [ ] `python scripts/render_brand_assets.py --check`
- [ ] `python scripts/render_readme_cards.py --check`
- [ ] `python scripts/render_previews.py --all --check`
- [ ] `python scripts/render_sequence.py --check`
- [ ] `python scripts/render_reel.py --check`
- [ ] `PYTHONPYCACHEPREFIX=/tmp/agent-familiars-pycache python -m py_compile setup.py scripts/check_release_readiness.py scripts/install_pet.py scripts/render_brand_assets.py scripts/render_readme_cards.py scripts/render_previews.py scripts/render_sequence.py scripts/render_reel.py scripts/smoke_mcp_client.py scripts/validate_pets.py scripts/validate_design_specs.py scripts/validate_docs.py scripts/generate_signal_surface.py scripts/generate_state_instruments.py scripts/rotate_installed_pet_variant.py familiars/__init__.py familiars/cli.py familiars/limits.py familiars/mcp_server.py familiars/pet_assets.py familiars/sequence_presets.py familiars/sequence_schema.py familiars/sequence_renderer.py`
- [ ] `python -m pip install -e . && familiars validate`
- [ ] `python -m pip install -e ".[mcp]" && python -c "from familiars.mcp_server import build_server; build_server(); print('mcp ok')"`
- [ ] `python scripts/smoke_mcp_client.py`
- [ ] `python -m pip wheel . --no-deps -w /tmp/agent-familiars-wheelhouse`

## Install Smoke Test

- [ ] `python scripts/install_pet.py --pack product-tropes --dest /tmp/agent-familiars-install-smoke --source local`
- [ ] `python scripts/install_pet.py --pack starter --dest /tmp/agent-familiars-starter-smoke --source local`
- [ ] `python scripts/install_pet.py --pack state-instruments --dest /tmp/agent-familiars-state-smoke --source local`
- [ ] `python scripts/install_pet.py --pack first-50 --dest /tmp/agent-familiars-first-50-smoke --source local`

## Notes

-
