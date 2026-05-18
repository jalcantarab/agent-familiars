# Maintainer Workflow

This repository is small, but `main` should still be boring.

## Branch Model

- `main` is the public release branch.
- Do not push directly to `main`.
- Use short-lived branches for all changes.
- If the checkout has unrelated local work, use
  `docs/git-worktree-isolated-branching.md` instead of switching branches in
  place.

```bash
git switch -c jab/<short-topic>
```

Good branch names:

- `jab/repair-no-knight`
- `jab/preview-checks`
- `jab/update-attribution`
- `jab/install-pack-smoke`

Delete branches after merge. Keeping old branches around is not archival. It is
clutter with a commit hash.

## Pull Request Gates

Every PR into `main` should pass:

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
```

For asset or pack changes, also run a local install smoke test:

```bash
python3 scripts/install_pet.py --pack product-tropes --dest /tmp/agent-familiars-install-smoke --source local
python3 scripts/install_pet.py --pack starter --dest /tmp/agent-familiars-starter-smoke --source local
python3 scripts/install_pet.py --pack first-50 --dest /tmp/agent-familiars-first-50-smoke --source local
```

PRs that change pet artwork should include a contact sheet or preview note.
PRs that import third-party assets must update `NOTICE.md`, `catalog/pets.json`,
`catalog/packs.json` when needed, and the relevant license file under
`licenses/`.

Any time a PR touches release assets or docs, run a targeted public-safety scan:

```bash
rg -n --hidden -S "(api[_-]?key|secret|password|Authorization:|Bearer |client_secret|private_key|BEGIN (RSA|OPENSSH|PRIVATE)|sk-[A-Za-z0-9]{20,}|ghp_|github_pat_|xox[baprs]-|refresh_token|access_token|/Users/)" . -g '!.git/**'
```

The scan may find policy docs or examples that mention these words. Actual
credential values, local machine paths, unpublished company material, and
temporary working notes should not be present.

## Issue Triage

Keep public intake boring and useful. The first release should use issues, not a
project board or open-ended discussions.

- `bug`: installer, validation, packaging, broken links, or renderer failures.
- `enhancement`: CLI, MCP, installer, renderer, docs, or catalog improvements.
- `pet-request`: new original or clearly licensed pet ideas.
- `pet-polish`: existing pet motion, readability, or personality problems.
- `documentation`: missing or confusing docs.
- `good first issue`: small fixes with a clear expected result.
- `help wanted`: useful work that is already scoped but not owner-bound.

Convert vague issues into one of those shapes before doing deeper work. If a
report is really about taste, ask for the state, the expected feeling, and a
screenshot or contact sheet. "Make it better" is an emotion, not a ticket.

## GitHub Protection Settings

Configure `main` with branch protection:

- require pull requests before merging
- require the `Validate` workflow to pass
- require branches to be up to date before merge
- require conversation resolution
- block force pushes
- block branch deletion
- allow squash merge, disable merge commits if the history starts getting noisy

Leave Discussions and Projects disabled unless the issue volume demands them.
They are useful later; early on they are extra rooms to sweep.

One maintainer can still move quickly through a PR. The point is to leave a
reviewable trail and avoid accidental pushes to the public branch.

## Release Flow

1. Merge a focused PR into `main`.
2. Confirm the GitHub `Validate` workflow passes on `main`.
3. Run the install smoke test from a fresh clone or archive.
4. Do not force-move published release tags.
5. Tag later public releases as `v0.x.y` and bump `pyproject.toml` in the same
   PR that updates the changelog.
6. Keep release notes short: added pets, changed packs, installer changes,
   attribution changes.

This project does not deploy a service. Continuous delivery here means the
catalog, installer, and downloadable assets are always in a usable state.

## History Hygiene

Public history should be readable and boring. If a change needs experimentation,
do it on a short-lived branch and squash before merge.
