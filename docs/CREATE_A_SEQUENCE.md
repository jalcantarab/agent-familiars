# Create A Sequence

Sequences are reusable mini-showcases for Familiars. They turn committed pet
spritesheets into GIFs, MP4s, and posters without asking you to edit the
handcrafted reel renderer.

Use sequences when you want to:

- show one familiar across its best states
- compare a small pack side by side
- create a README card, issue-comment preview, or lightweight social clip
- test whether a pet's state language is readable outside Codex

Use [Create A Reel](CREATE_A_REEL.md) when you need a bespoke scene with custom
transitions, choreography, or committed launch assets.

## Quick Start

Render a character-specific spotlight:

```bash
familiars render --pet no-knight --preset spotlight
```

Render a pack comparison:

```bash
familiars render --pack state-instruments --preset comparison
```

Render from a recipe:

```bash
familiars render --recipe examples/sequences/no-knight-spotlight.json
```

Outputs go to `output/sequences` by default. That folder is intentionally ignored
by Git so people can experiment freely without adding generated media by
accident.

The repo script still works from a clone:

```bash
python scripts/render_sequence.py --pet no-knight --preset spotlight
```

## Choose A Preset

List presets:

```bash
familiars list presets
```

Built-in presets:

| Preset | Use |
| --- | --- |
| `spotlight` | one familiar with its best character-specific beats |
| `readme` | smaller spotlight for documentation pages |
| `all-states` | one familiar cycling through every Codex pet row |
| `comparison` | several familiars side by side |
| `social` | larger MP4/poster export with restrained repo provenance |
| `clean` | neutral no-brand output for someone else's docs |

The default presets do not force the Zentrik mark into every output. The `social`
preset and `repo-dark` theme include restrained provenance because those assets
are intended to point back to this repository.

## Choose A Theme

List themes:

```bash
familiars list themes
```

Themes define the visual system: background, grid, accent, text, captions, and
optional provenance. Keep themes calm. The familiar should carry the moment.

## Pet Profiles

Every catalog pet has a profile in [catalog/pet-profiles.json](../catalog/pet-profiles.json).
Profiles define:

- `title`: display name used in generated sequences
- `subtitle`: short role or personality line
- `best`: the most useful states and captions for the pet

That means this command:

```bash
familiars render --pet signal-surface
```

uses Signal Surface's own language: calm signal, input glow, work moving, clean
scan, fault bloom. It does not fall back to the same generic captions used by
every other pet.

## Recipes

A recipe is a JSON file with a small, stable shape:

```json
{
  "version": 1,
  "title": "No Knight",
  "subtitle": "the roadmap guardian",
  "preset": "spotlight",
  "theme": "familiars-dark",
  "slug": "no-knight-spotlight-sequence",
  "outputs": {
    "formats": ["gif", "poster"],
    "dir": "output/sequences"
  },
  "scenes": [
    {
      "pet": "no-knight",
      "beats": "profile.best"
    }
  ]
}
```

`beats` can be:

- `profile.best`: the pet-specific default
- `all-states`: every Codex state row in atlas order
- a list of `{ "state": "...", "caption": "..." }` objects
- a named list added to that pet's profile later

Scenes may use one `pet` or several `pets`. A multi-pet scene automatically uses
the comparison layout unless you set another supported layout in the future.

## Useful Commands

Render only a poster while iterating:

```bash
familiars render --pet intent-compass --outputs poster
```

Send output somewhere temporary:

```bash
familiars render --pet tide-stone --output-dir /tmp/familiars-sequences
```

Override a recipe's theme:

```bash
familiars render \
  --recipe examples/sequences/zentri-readme.json \
  --theme-override review-light
```

Validate the committed examples:

```bash
familiars validate
```

## Design Rules

- Let each pet keep its own state language. No Knight can say `NO`; Signal
  Surface should glow, scan, and fault; Tide Stone should stay quiet.
- Keep captions short enough to read in a README thumbnail.
- Prefer one clear beat per state over a crowded explanation.
- Use `all-states` for QA and `profile.best` for public examples.
- Use `poster` while iterating. Render GIF or MP4 only when the layout works.
- Keep generated experiments under `output/sequences` until they are worth
  committing as curated assets.

## Future Surface

The renderer is intentionally data-first. The same recipe shape can support a
CLI, MCP tool, API endpoint, or small UI later:

- a user chooses a pet or pack
- the tool loads the profile and preset
- the user changes a few labels, colors, or output formats
- the renderer exports media from the same normalized recipe

That keeps today's repo workflow useful while leaving room for friendlier
interfaces when the collection grows.
