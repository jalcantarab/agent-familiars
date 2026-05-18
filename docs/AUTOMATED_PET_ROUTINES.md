# Automated Pet Routines

Codex pets are file-based. An installed custom pet has a `pet.json` manifest and
one `spritesheet.webp` atlas. Codex reads the standard nine rows from that atlas:
`idle`, `running-right`, `running-left`, `waving`, `jumping`, `failed`,
`waiting`, `running`, and `review`.

That gives us a simple automation surface: a Codex automation can copy a
different valid atlas into the installed pet folder, review pet quality, or
refresh generated showcase assets. It should not depend on private app state or
pretend that Codex exposes custom live pet events.

## Fastest Useful Experiment

Use a local variant lab outside the repository:

```text
~/.codex/familiars-variants/signal-surface/
  morning.webp
  focus.webp
```

`morning.webp` can be the normal installed atlas. `focus.webp` can be a cleaner
high-focus colorway of the same pet. Keep these variants local until one is good
enough to publish as a real pet or documented example.

To switch without any Familiars helper script, give a Codex automation this
shape:

```text
Switch the installed Signal Surface familiar to the local focus variant using
normal agent file operations, not the repository rotation script.

Source:
~/.codex/familiars-variants/signal-surface/focus.webp

Destination:
~/.codex/pets/signal-surface/spritesheet.webp

Before copying, create a timestamped backup under:
~/.codex/pets/signal-surface/.agent-variant-backups/

Copy through a temporary file and then replace the destination atomically.
Verify that the destination checksum matches the focus variant checksum and that
the destination remains a WebP file. Report the selected variant and whether
Codex needs a manual pet refresh. Do not modify tracked repository files.
```

This is the most direct test of "Codex uses its own agent abilities to switch a
pet." No Python is required for the switch. The helper script exists for
repeatable public workflows where validation and daypart selection should be
less dependent on prompt wording.

## What Automations Are Good At

### Switch A Local Variant

Use this for one installed pet with several local moods:

- `morning.webp`: calm start, lower contrast
- `focus.webp`: sharper color, clearer active states
- `evening.webp`: dimmer, less distracting
- `night.webp`: reduced brightness

Best for: Signal Surface, Tide Stone, Intent Compass, and other pets where a
colorway or prop change is meaningful without creating another catalog entry.

### Review A Pet Lab

Ask Codex to inspect a local folder of candidate atlases, compare them against
the committed pet, and report which rows are hard to read at small size.

Good checks:

- the same identity is visible in every row
- unused cells remain transparent
- state rows do different work instead of repeating a generic bounce
- waiting and review read clearly without needing text
- the atlas still has the Codex size and alpha channel

This can be a paused weekly automation. It should report, not auto-commit.

### Refresh Showcase Assets

Ask Codex to regenerate previews or reels after a pet changes. This belongs in a
branch or PR workflow because it can touch tracked media files.

Good prompt constraint:

```text
Create a branch first. Regenerate only the preview or reel assets required by
the changed pets. Run validation. Open a PR. Do not push directly to main.
```

For lightweight local previews, prefer sequences:

```bash
python scripts/render_sequence.py --pet signal-surface --preset spotlight --outputs poster
python scripts/render_sequence.py --pack state-instruments --preset comparison --outputs poster
```

Sequence outputs go to `output/sequences` by default and are not tracked. Commit
only the few generated media files that are intentionally part of the public
showcase.

## Helper Script Path

For repeatable local switching, use:

```bash
python3 scripts/rotate_installed_pet_variant.py signal-surface \
  --variant-dir ~/.codex/familiars-variants/signal-surface \
  --mode daypart
```

Expected daypart names are:

- `morning.webp`
- `focus.webp`
- `evening.webp`
- `night.webp`

The script validates atlas size and alpha before replacing the installed copy.
Use the script when you want deterministic behavior. Use the agent-native prompt
when you want to test what a plain Codex automation can do by itself.

## Current Limits

Reliable:

- copying a valid local `spritesheet.webp` over an installed pet
- installing separate pet IDs such as `tide-stone` and `tide-stone-night`
- validating pets, previews, reels, and docs in scheduled jobs
- creating local sequence GIFs and posters from committed spritesheets
- asking Codex to review local variant folders and summarize what changed

Not stable enough for public workflows:

- editing Codex internal app state to force-select a pet
- depending on a live event hook for "only switch during review"
- adding custom runtime states beyond the nine atlas rows

Design around the stable layer. If a state needs to feel smarter, encode that in
the row itself: color, posture, props, scan direction, tempo, facial expression,
or a visible state surface.

## Recommended Local Automations

### Signal Surface Variant Switch

Create this as paused first. Run it manually when you want to test a variant.
After it proves useful, make it hourly or daypart-based.

Task:

```text
Switch Signal Surface to the current local variant. Use normal file operations,
create a backup, replace atomically, verify checksum equality, and report the
result. Do not modify tracked repository files.
```

### Familiars Pet Lab Review

Create this as a paused weekly review.

Task:

```text
Review the Familiars repository and any local variant lab. Run non-mutating
checks, summarize stale previews or weak pet rows, and recommend the next
smallest repair. Do not modify tracked files unless asked.
```

### Showcase Refresh

Use this only after a branch exists.

Task:

```text
Regenerate the required preview GIFs or reels for the changed pets, run
validation, and prepare a PR summary.
```

## Publication Rule

Do not publish every local variant. Publish only one of these:

- a final replacement sprite for an existing pet
- a clearly different pet ID with a reason to exist
- a documented example that helps people learn how variant automation works

The repo should stay small enough to browse and strong enough to trust.
