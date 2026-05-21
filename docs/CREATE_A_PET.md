# Create A Pet

This guide is for people who want to make a Codex pet that feels like a small
character, not just a static mascot.

Zentri, the folded-paper crane inspired by [Zentrik](https://zentrik.ai), is the
reference example in this repository: one clear silhouette, one restrained
accent color, and state animations that come from the character's body.

For the full production workflow, read
[PET_CREATION_PLAYBOOK.md](PET_CREATION_PLAYBOOK.md). For adjacent tools and
cross-agent pet projects, read [ECOSYSTEM_TOOLS.md](ECOSYSTEM_TOOLS.md).

## Proposing A Pet

If you have an idea but are not ready to draw the atlas, you can open a Pet
Request issue. A strong proposal focuses on how the character acts during work,
not just how it looks.

**Good example:**
- **Concept:** Backlog Archaeologist. A scholarly fossil explorer for old tickets.
- **Motion language:**
  - `idle`: brush-tail makes one careful stroke across the fossil shell
  - `waiting`: holds up a fossil slab, asking if the old ticket still matters
  - `running`: brush-tail clears a sediment layer to reveal an artifact
  - `review`: polishes the fossil shell and nods through its goggles
  - `failed`: sediment layers slide over its head, burying the decision
- **Rights:** Original idea, no company marks or copyrighted characters, safe for MIT.

If you want to build the pet yourself, continue below.

## 1. Write The Character Brief

Start with the smallest useful description:

```text
Name: Zentri
Identity: folded-paper crane for product and agent workflows
Visual lock: white paper facets, charcoal crease lines, cyan intent accent
Motion language: paper folds, precise balancing, economical wing gestures
Avoid: readable logos, UI screenshots, text, detached effects, heavy glow
```

For a new pet, define:

- what the pet is
- who it helps
- what makes it visually recognizable at `192x208`
- how it moves when it works, waits, reviews, and fails
- what must never appear in the sprite

Pets do not have to be creatures. A useful surface, tool, instrument, or small
object can work when the state grammar is clear. For example, Signal Surface
uses color, scan direction, and internal motion instead of limbs or facial
expressions. The [State Instruments](STATE_INSTRUMENTS.md) pack shows the same
idea with more familiar-like objects: compass, totem, oracle, loom, and stone.

## 2. Define State-Specific Motion

Codex expects nine rows:

```text
idle
running-right
running-left
waving
jumping
failed
waiting
running
review
```

Do not reuse one generic jump, wave, or sad pose. A ghost should not run like a
dog. A heavy pet should not bounce like a small toy. A paper pet should move
through folds, not feathers.

Use [ANIMATION_BIBLE.md](ANIMATION_BIBLE.md) as the quality bar.

Good row prompts name the mechanics explicitly:

```text
State: waiting
Character-specific motion: the folded-paper crane extends one tabbed wing
toward the viewer, head tilted, asking for prioritization input.
Tiny-size read: one extended wing tab plus a clear head tilt.
Reject: generic idle, text, punctuation, floating UI, or detached glow.
```

## 3. Generate And Package

The final pet folder should look like this:

```text
pets/<pet-id>/
├── pet.json
├── preview/
│   ├── idle.gif
│   └── contact-sheet.png
└── spritesheet.webp
```

The `pet.json` file should point to `spritesheet.webp`:

```json
{
  "id": "zentri",
  "displayName": "Zentri",
  "description": "A folded-paper crane companion for product and agent workflows.",
  "spritesheetPath": "spritesheet.webp"
}
```

## 4. Validate

Run:

```bash
python scripts/validate_pets.py
python scripts/validate_design_specs.py
python scripts/render_previews.py --all --check
python scripts/render_sequence.py --check
python scripts/validate_docs.py
python scripts/check_release_readiness.py
python scripts/render_brand_assets.py --check
python scripts/render_readme_cards.py --check
PYTHONPYCACHEPREFIX=/tmp/agent-familiars-pycache python -m py_compile setup.py scripts/check_release_readiness.py scripts/install_pet.py scripts/render_brand_assets.py scripts/render_readme_cards.py scripts/render_previews.py scripts/render_sequence.py scripts/render_reel.py scripts/smoke_mcp_client.py scripts/validate_pets.py scripts/validate_design_specs.py scripts/validate_docs.py scripts/generate_signal_surface.py scripts/generate_state_instruments.py scripts/rotate_installed_pet_variant.py familiars/__init__.py familiars/cli.py familiars/limits.py familiars/mcp_server.py familiars/pet_assets.py familiars/sequence_presets.py familiars/sequence_schema.py familiars/sequence_renderer.py
```

Render or refresh preview GIFs from the spritesheet when needed:

```bash
python scripts/render_previews.py <pet-id> --force
```

The top-level showcase reel is also generated from committed spritesheets:

```bash
python scripts/render_reel.py
```

For a quick local GIF or poster from a finished pet, use a sequence:

```bash
python scripts/render_sequence.py --pet <pet-id> --preset spotlight
```

For visual QA, inspect `preview/contact-sheet.png` and the state preview loops.
Each pet README should include the full nine-state animation catalog so people
can judge the pet without installing it first. Reject rows with identity drift,
copied guide marks, white backgrounds, shadows, detached effects, cropped poses,
or motion that does not match the state.

## 5. Share It

Add attribution and license details before opening a PR:

- `catalog/pets.json`
- `catalog/packs.json` when pack membership changes
- `NOTICE.md`
- `licenses/<source>.txt` when needed

Then install locally and test in Codex:

```bash
python3 scripts/install_pet.py <pet-id>
```
