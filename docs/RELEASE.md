# Release Guide

Use this before tagging a release or doing a larger public push. The repository
should be useful, installable, and safe to redistribute before new attention
arrives.

## Release State

- Installable pets are tracked under `pets/` and cataloged in
  `catalog/pets.json`.
- The complete first-50 set is available through `--pack first-50`.
- Product-folklore pets are available through `--pack product-tropes`.
- Reusable sequence recipes are available through the `familiars` CLI and
  `familiars-mcp` server for local GIF, MP4, poster, and pack-comparison
  exports.

## Release Gates

1. Run validation locally and in GitHub Actions.
2. Review licensing and attribution for imported pets.
3. Scan the current tree for credentials, local paths, unpublished company
   material, and temporary working notes.
4. Confirm README, installer, catalog, NOTICE, and docs render correctly on
   GitHub.
5. Confirm issue intake and labels are ready for public reports.
6. Tag the release after `main` is green.

## Repository Hygiene

- `git status --short` is clean before tagging.
- Commit messages are understandable and do not mention credentials, incidents,
  temporary working notes, or unpublished company material.
- No `.env`, cache folders, local generated image folders, logs, temporary
  prompts, screenshots with sensitive data, or machine-specific paths are
  tracked.
- `README.md`, `CHANGELOG.md`, `NOTICE.md`, `LICENSE`, `docs/LICENSING.md`,
  `CONTRIBUTING.md`, `SECURITY.md`, `catalog/pets.json`, and
  `catalog/packs.json` are current.
- `pyproject.toml`, `setup.py`, and `MANIFEST.in` install the CLI and include
  the package data needed to render and install pets from outside the clone.
- `.github/workflows/validate.yml` passes.
- Issue forms exist for bugs, features, new pet requests, and pet polish.

## Assets And Licensing

- Every installable pet has `pet.json`, `spritesheet.webp`, `README.md`, and
  preview media when available.
- Every imported pet has a clear source URL and license in both `NOTICE.md` and
  `catalog/pets.json`.
- Non-commercial, fan-art, trademark-sensitive, or no-license assets are not
  redistributed.
- Zentrik-owned examples are clearly marked as original assets from this
  repository.
- Product-folklore pets are original trope pets, not copies of company mascots,
  logos, slogans, or branded UI.

## Validation

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
python -m pip install -e .
familiars validate
python -m pip install -e ".[mcp]"
python -c "from familiars.mcp_server import build_server; build_server(); print('mcp ok')"
python scripts/smoke_mcp_client.py
python -m pip wheel . --no-deps -w /tmp/agent-familiars-wheelhouse
rg -n --hidden -S "(api[_-]?key|secret|password|Authorization:|Bearer |client_secret|private_key|BEGIN (RSA|OPENSSH|PRIVATE)|sk-[A-Za-z0-9]{20,}|ghp_|github_pat_|xox[baprs]-|refresh_token|access_token|/Users/)" . -g '!.git/**'
```

## Install Smoke Test

```bash
rm -rf /tmp/agent-familiars-install-smoke
python3 scripts/install_pet.py --pack product-tropes --dest /tmp/agent-familiars-install-smoke --source local
test -f /tmp/agent-familiars-install-smoke/signal-heron/pet.json
test -f /tmp/agent-familiars-install-smoke/priority-sphinx/spritesheet.webp

rm -rf /tmp/agent-familiars-starter-smoke
python3 scripts/install_pet.py --pack starter --dest /tmp/agent-familiars-starter-smoke --source local
test -f /tmp/agent-familiars-starter-smoke/signal-surface/pet.json
test -f /tmp/agent-familiars-starter-smoke/release-rocket/pet.json
test -f /tmp/agent-familiars-starter-smoke/security-sentinel/spritesheet.webp

rm -rf /tmp/agent-familiars-state-smoke
python3 scripts/install_pet.py --pack state-instruments --dest /tmp/agent-familiars-state-smoke --source local
test -f /tmp/agent-familiars-state-smoke/intent-compass/pet.json
test -f /tmp/agent-familiars-state-smoke/tide-stone/spritesheet.webp

rm -rf /tmp/agent-familiars-first-50-smoke
python3 scripts/install_pet.py --pack first-50 --dest /tmp/agent-familiars-first-50-smoke --source local
test -f /tmp/agent-familiars-first-50-smoke/pixel-penguin/pet.json
test -f /tmp/agent-familiars-first-50-smoke/demo-dolphin/spritesheet.webp

rm -rf /tmp/agent-familiars-cli-smoke
familiars render --pet no-knight --preset spotlight --outputs poster --output-dir /tmp/agent-familiars-cli-smoke
test -f /tmp/agent-familiars-cli-smoke/no-knight-spotlight-poster.png
```

## Documentation Check

- The README starts with a clear value proposition.
- The README reaches install instructions before the visual tour.
- The README helps first-time visitors choose a familiar before the full
  catalog.
- Embedded README images stay under the docs validator budget.
- Install instructions work from a clone, from the CLI, and from the raw GitHub
  installer.
- Pet creation guidance leads with useful craft.
- Sequence guidance explains reusable GIF/poster generation without requiring
  people to edit the bespoke reel script.
- Product-folklore docs explain the creative standard clearly.
- The README banner is generated from committed spritesheets and checked with
  `python scripts/render_brand_assets.py --check`.

## Versioning

After `v0.1.0` is published, treat tags as immutable. Later releases should bump
`pyproject.toml`, update `CHANGELOG.md`, and create a new tag instead of moving
an existing public tag.

## Issue Intake

- Blank issues are disabled so reports arrive with enough context.
- Bug reports ask for environment, command, pet id, and error output.
- Feature requests ask for the user outcome first, not implementation trivia.
- Pet requests require motion language and rights context.
- Pet polish issues ask which animation states feel wrong and what feeling they
  should create.
- Labels should include `bug`, `enhancement`, `documentation`, `pet-request`,
  `pet-polish`, `good first issue`, `help wanted`, `cli`, `mcp`, `renderer`,
  `installer`, `assets`, `licensing`, and `release-readiness`.
- Discussions and Projects can stay disabled until issue volume makes them
  useful.

## Repository Listing

- Description: `Codex pets for agent work and long-running sessions.`
- Topics: `codex`, `codex-pets`, `ai-agents`, `developer-tools`,
  `product-management`, `sprites`, `open-source`.
- README banner: use `assets/brand/familiars-banner.webp`.
- Social preview: use `assets/brand/social-preview.png`.
- Release notes should lead with the install command, the catalog, and the
  creation guide.
