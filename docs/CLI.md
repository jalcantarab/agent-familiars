# CLI

The `familiars` command gives the repository a normal terminal surface for
installing pets and rendering small showcase assets.

## Install

From a clone:

```bash
python -m pip install -e .
```

Then check the bundled data:

```bash
familiars validate
```

The packaged CLI can run from outside the repository. Wheels include the
catalogs, examples, docs, brand assets, licenses, and each pet's installable
`pet.json` plus `spritesheet.webp`. Preview GIFs and showcase reels stay in the
repository so the package does not carry review media users do not need at
runtime.

## List

```bash
familiars list pets
familiars list packs
familiars list presets
familiars list themes
familiars list profiles
```

## Install Pets

```bash
familiars install zentri
familiars install --pack starter
familiars install --pack state-instruments
familiars install --pack first-50
```

By default, installs go to `${CODEX_HOME:-~/.codex}/pets`.

Use a temporary directory for smoke tests:

```bash
familiars install zentri --dest /tmp/familiars-install-smoke
```

Install directly from GitHub instead of the packaged data:

```bash
familiars install zentri --source github --repo jalcantarab/agent-familiars --ref main
```

## Render Sequences

```bash
familiars render --pet no-knight --preset spotlight
familiars render --pack state-instruments --preset comparison
familiars render --recipe examples/sequences/no-knight-spotlight.json
```

Render only a poster while iterating:

```bash
familiars render --pet intent-compass --outputs poster
```

Send output somewhere explicit:

```bash
familiars render --pet tide-stone --output-dir /tmp/familiars-sequences
```

Dry-run prints the normalized recipe without writing media:

```bash
familiars render --pet signal-surface --dry-run
```

For the recipe shape and animation guidance, see
[Create A Sequence](CREATE_A_SEQUENCE.md).

For agent integrations, see [MCP Server](MCP.md).
