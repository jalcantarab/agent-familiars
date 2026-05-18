# Intent Compass

A small brass-and-cyan compass that behaves like it wants to find the right
direction. It is useful at a glance: green/cyan means work is moving, amber
means a choice is waiting, blue-white means review, and red means the bearing
has gone wrong.

![Intent Compass idle animation](preview/idle.gif)

## Animation Catalog

| Idle | Running Right | Running Left |
| --- | --- | --- |
| <img src="preview/idle.gif" alt="Intent Compass idle animation" width="112"> | <img src="preview/running-right.gif" alt="Intent Compass running right animation" width="112"> | <img src="preview/running-left.gif" alt="Intent Compass running left animation" width="112"> |

| Waving | Jumping | Failed |
| --- | --- | --- |
| <img src="preview/waving.gif" alt="Intent Compass waving animation" width="112"> | <img src="preview/jumping.gif" alt="Intent Compass jumping animation" width="112"> | <img src="preview/failed.gif" alt="Intent Compass failed animation" width="112"> |

| Waiting | Running | Review |
| --- | --- | --- |
| <img src="preview/waiting.gif" alt="Intent Compass waiting animation" width="112"> | <img src="preview/running.gif" alt="Intent Compass running animation" width="112"> | <img src="preview/review.gif" alt="Intent Compass review animation" width="112"> |

The full Codex install asset is [`spritesheet.webp`](spritesheet.webp). GIF previews are rendered from the committed spritesheet for GitHub review.

## Install

```bash
mkdir -p ~/.codex/pets
cp -R pets/intent-compass ~/.codex/pets/
```

Then refresh custom pets in Codex and select `Intent Compass`.

## Motion Notes

- `idle`: keeps a calm north bearing with a soft cyan lens pulse.
- `running-right` / `running-left`: locks the needle toward the travel side.
- `waving`: sweeps the needle like a small greeting.
- `jumping`: lifts while the center jewel brightens.
- `failed`: splits the needle into conflicting red and amber bearings.
- `waiting`: trembles between choices in an amber arc.
- `running`: spins through active search.
- `review`: scans the lens and settles into a clean evaluation bearing.

## Source

- Origin: original state-instrument pet generated for Familiars.
- Author: Jorge Alcantara / Zentrik.
- License: MIT for this pet bundle in this repository.
- Generator: [`scripts/generate_state_instruments.py`](../../scripts/generate_state_instruments.py).

## Preview

Full contact sheet: [preview/contact-sheet.png](preview/contact-sheet.png)
