# Agent Guidance

This repository is public-facing. Work here should be useful to the broader
Codex community, easy to review, and careful about licensing.

## Working Rules

- Keep changes small and reviewable.
- Do not commit secrets, local machine paths, generated prompt transcripts, API
  keys, `.env` files, cache folders, or private research notes.
- Do not import pet assets unless the license allows redistribution in this
  repository. Record attribution in `NOTICE.md` and `catalog/pets.json`.
- Treat planned pets as briefs until they have a valid `pet.json`,
  `spritesheet.webp`, and QA output.
- Prefer public, product-neutral language in docs. It is fine to use Zentri and
  Zentrik as examples, but keep repository docs free of unpublished company
  material.
- For brand-adjacent reference pets, use workflow categories and original
  motion metaphors. Do not commit company-target mappings, logo lookalikes,
  official mascot silhouettes, exact brand palettes, screenshots, slogans, or
  product names as pet IDs.
- Generated assets may be refreshed when the script scope has been inspected and
  the output is intentionally reviewed. Avoid broad formatting, cache churn, or
  unrelated generated artifacts.

## Branches

Use short-lived branches for meaningful changes. Do not push directly to
`main`; all public-branch changes should go through a PR.
Use `docs/git-worktree-isolated-branching.md` when a clean branch is needed from
a mixed checkout.

```bash
git switch -c jab/<short-topic>
```

Examples:

- `jab/install-script`
- `jab/pet-docs`
- `jab/add-review-owl-previews`

## Commits

Use concise, human-readable commit messages:

```text
Add public pet installer flow
Document pet creation checklist
Validate imported pet attributions
```

Avoid noisy commits that only contain cache files, temporary outputs, or local
tool state.

## Pull Requests

Before opening a PR:

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

For a new or changed pet, include:

- install path: `pets/<pet-id>/pet.json`
- atlas path: `pets/<pet-id>/spritesheet.webp`
- attribution and license updates
- contact sheet or preview when available
- a short note describing the pet's motion language

Maintainer workflow details live in
`docs/MAINTAINER_WORKFLOW.md`.

## Pet Quality Bar

Every accepted pet should be readable at desktop pet size, emotionally clear
across states, and safe to redistribute. Avoid fan art, trademark-sensitive
characters, non-commercial assets, and unlicensed personal pet packs.
