# Loop Loom

A small loom that makes agent work feel tactile. Instead of running or smiling,
it moves a shuttle, tightens threads, pauses at an edge, or knots when something
has gone wrong.

![Loop Loom idle animation](preview/idle.gif)

## Animation Catalog

| Idle | Running Right | Running Left |
| --- | --- | --- |
| <img src="preview/idle.gif" alt="Loop Loom idle animation" width="112"> | <img src="preview/running-right.gif" alt="Loop Loom running right animation" width="112"> | <img src="preview/running-left.gif" alt="Loop Loom running left animation" width="112"> |

| Waving | Jumping | Failed |
| --- | --- | --- |
| <img src="preview/waving.gif" alt="Loop Loom waving animation" width="112"> | <img src="preview/jumping.gif" alt="Loop Loom jumping animation" width="112"> | <img src="preview/failed.gif" alt="Loop Loom failed animation" width="112"> |

| Waiting | Running | Review |
| --- | --- | --- |
| <img src="preview/waiting.gif" alt="Loop Loom waiting animation" width="112"> | <img src="preview/running.gif" alt="Loop Loom running animation" width="112"> | <img src="preview/review.gif" alt="Loop Loom review animation" width="112"> |

The full Codex install asset is [`spritesheet.webp`](spritesheet.webp). GIF previews are rendered from the committed spritesheet for GitHub review.

## Install

```bash
mkdir -p ~/.codex/pets
cp -R pets/loop-loom ~/.codex/pets/
```

Then refresh custom pets in Codex and select `Loop Loom`.

## Motion Notes

- `idle`: threads sway with a soft woven pulse.
- `running-right` / `running-left`: the shuttle crosses in the requested direction.
- `waving`: a woven loop lifts like a small signal.
- `jumping`: the frame hops while the threads stay taut.
- `failed`: a red knot appears where the loop jams.
- `waiting`: the shuttle pauses at the edge in amber.
- `running`: the shuttle weaves through active thread lanes.
- `review`: the woven strip tightens into a clean pattern.

## Source

- Origin: original state-instrument pet generated for Familiars.
- Author: Jorge Alcantara / Zentrik.
- License: MIT for this pet bundle in this repository.
- Generator: [`scripts/generate_state_instruments.py`](../../scripts/generate_state_instruments.py).

## Preview

Full contact sheet: [preview/contact-sheet.png](preview/contact-sheet.png)
