# Install Guide

Codex scans custom pets from:

```text
${CODEX_HOME:-~/.codex}/pets/<pet-id>/
```

Each pet is a folder with this shape:

```text
pets/<pet-id>/
├── pet.json
└── spritesheet.webp
```

## Fast Install

From a clone, install the CLI once:

```bash
python -m pip install -e .
familiars list packs
```

Then install one familiar:

```bash
familiars install zentri
```

The repository script remains available when you want a one-file installer:

```bash
python3 scripts/install_pet.py zentri
```

Not sure which pet to install first? Start with
[Choosing A Familiar](CHOOSING_A_FAMILIAR.md).

Install a curated developer starter pack:

```bash
familiars install --pack starter
```

Install the complete first-50 set:

```bash
familiars install --pack first-50
```

Install the state-instrument set:

```bash
familiars install --pack state-instruments
```

List available pets:

```bash
familiars list pets
```

Install from GitHub without cloning:

```bash
curl -fsSL https://raw.githubusercontent.com/jalcantarab/agent-familiars/main/scripts/install_pet.py | python3 - zentri
```

Then open Codex Desktop:

```text
Settings -> Personalization -> Pets -> Refresh custom pets -> select the pet
```

You can wake or tuck away the pet from the Pets settings panel, the command
palette, or the `/pet` composer command.

## Ask Codex To Install One

Use a prompt like this:

```text
Go to https://github.com/jalcantarab/agent-familiars and install the Terminal
Ghost pet into my local Codex pets folder. Use the repository install script if
available. Then tell me to refresh custom pets in Codex.
```

Useful pet ids:

- `zentri`
- `signal-surface`
- `intent-compass`
- `thread-totem`
- `pocket-oracle`
- `loop-loom`
- `tide-stone`
- `merge-mammoth`
- `ci-phoenix`
- `patch-panda`
- `product-crane`
- `test-tortoise`
- `diff-dragon`
- `queue-crab`
- `context-cat`
- `prompt-parrot`
- `build-bot`
- `pixel-penguin`
- `container-hermit`
- `cluster-puffer`
- `release-rocket`
- `incident-axolotl`
- `search-salmon`
- `docs-jelly`
- `schema-snail`
- `refactor-rabbit`
- `roadmap-raven`
- `meeting-moth`
- `approval-alpaca`
- `sandbox-seal`
- `notebook-newt`
- `security-sentinel`
- `migration-mantis`
- `demo-dolphin`
- `terminal-ghost`
- `review-owl`
- `bug-hunter`
- `rubber-duck-2-0`
- `token-vampire`

## Manual Install

From a clone:

```bash
mkdir -p ~/.codex/pets
cp -R pets/zentri ~/.codex/pets/
```

Swap `zentri` for any folder name under `pets`.

## Full Catalog Install

Install every currently installable pet in the catalog:

```bash
python3 scripts/install_pet.py --all
```

## Uninstall

Remove the pet folder from `~/.codex/pets` and refresh custom pets in Codex.
