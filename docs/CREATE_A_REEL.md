# Create A Reel

Familiars includes the same reel renderer used for the README and showcase
assets. A good reel should feel like a tiny scene, not a grid dump.

The renderer uses committed pet spritesheets plus the Familiars visual system:
dark grid, cyan accent motion, restrained text, the Familiars wordmark
treatment, and a small `zentrik.ai` mark from [assets/brand](../assets/brand).

If you only need a reusable GIF, poster, or pack comparison, start with
[Create A Sequence](CREATE_A_SEQUENCE.md). Sequences are recipe-driven and do
not require editing Python. Reels are for deliberate choreography and committed
showcase assets.

## Quick Start

List the built-in reel families:

```bash
python scripts/render_reel.py --list
```

Render one family while iterating:

```bash
python scripts/render_reel.py --only hero
```

Render everything:

```bash
python scripts/render_reel.py
```

Outputs are written to [assets/showcase](../assets/showcase):

- `*.gif` for README moments and direct links
- `*.mp4` for places where video is cleaner than GIF
- `*-poster.png` for README cards, quick visual checks, and thumbnails

MP4 output requires `ffmpeg`. GIF and poster output require Pillow.

## Existing Recipes

| Reel | Command | Best For |
| --- | --- | --- |
| Main reel | `python scripts/render_reel.py --only hero` | Repo header and broad collection preview |
| Team rally | `python scripts/render_reel.py --only team` | Showing several pets acting together |
| Calm team rally | `python scripts/render_reel.py --only team-calm` | Slower demos and posts |
| Product review council | `python scripts/render_reel.py --only council` | Product-community context |
| No Knight spotlight | `python scripts/render_reel.py --only knight` | A focused character joke |

## Make Your Own

Start with a tiny storyboard before changing code:

```text
Title: Familiars Team Rally
Purpose: show several pets acting like a small product team
Pets: zentri, signal-heron, no-knight, launch-lantern, merge-mammoth
One readable gag: No Knight keeps the shield text
Motion system: shared orbit, each pet keeps its own state animation
Text budget: title only, plus one character-specific joke
Output: GIF under 5 MB, MP4 for richer motion
```

Then edit [scripts/render_reel.py](../scripts/render_reel.py):

1. Pick pets and states with `Scene(...)` or `TeamMember(...)`.
2. Use `draw_background`, `draw_title`, `draw_logo`, and `draw_pet` so the reel
   stays in the Familiars visual system.
3. Add a `build_<name>_frames(...)` function that returns a list of frames.
4. Add GIF, MP4, and poster `OutputSpec` entries in `render_all(...)`.
5. Add the new family to `render_named(...)` and `REEL_DESCRIPTIONS`.
6. Render with `python scripts/render_reel.py --only <name>`.
7. Run `python scripts/render_reel.py --check`,
   `python scripts/render_sequence.py --check`, and
   `python scripts/validate_docs.py`. If the reel is committed for a public
   release, also run `python scripts/check_release_readiness.py` and
   `python scripts/render_brand_assets.py --check`. If the README chooser
   changes, run `python scripts/render_readme_cards.py --check`.

## Craft Rules

- Keep text scarce. One title is enough; one short character joke can be great.
- Let the pet motion explain the concept. Labels are a last resort.
- Give each transition a reason: paper folds, shield stamps, ash reforms,
  glow warms, traces connect, or review marks settle.
- Keep the frame readable at README size. If a detail only works fullscreen, it
  probably does not belong in the GIF.
- Use compact generated GIFs for the chooser and posters for heavier showcase
  cards. Several large GIFs at the top of one page will compete to load.
- Avoid brand clutter. The small `zentrik.ai` mark should feel like provenance,
  not a banner ad.
- Keep GitHub GIFs under 5 MB. Prefer MP4 for longer motion.

## Ask Codex

This prompt works well from a clone:

```text
Using this repository, create a Familiars-style showcase reel for
<pet-a>, <pet-b>, and <pet-c>. Keep the existing visual system, use minimal
text, add one character-specific transition, render GIF, MP4, and poster outputs
under assets/showcase, then run the reel and docs checks.
```

For a no-code sequence, ask for this instead:

```text
Using this repository, create a Familiars sequence recipe for <pet-or-pack>.
Use the built-in pet profile beats where possible, render a poster first for
review, then render the requested GIF or MP4 under output/sequences.
```

## Brand Notes

The included Zentrik marks are part of this repository's Familiars examples and
showcase assets. Use them to create Familiars showcase material from this repo.
Do not present the marks as your own brand, imply endorsement of unrelated
projects, or copy them into unrelated asset packs.
