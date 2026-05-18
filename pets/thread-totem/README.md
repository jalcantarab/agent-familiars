# Thread Totem

A pocket ritual object for long-running work: beads on a cord that either flow,
pause, align, or tangle. It keeps a familiar feeling without needing a face.

![Thread Totem idle animation](preview/idle.gif)

## Animation Catalog

| Idle | Running Right | Running Left |
| --- | --- | --- |
| <img src="preview/idle.gif" alt="Thread Totem idle animation" width="112"> | <img src="preview/running-right.gif" alt="Thread Totem running right animation" width="112"> | <img src="preview/running-left.gif" alt="Thread Totem running left animation" width="112"> |

| Waving | Jumping | Failed |
| --- | --- | --- |
| <img src="preview/waving.gif" alt="Thread Totem waving animation" width="112"> | <img src="preview/jumping.gif" alt="Thread Totem jumping animation" width="112"> | <img src="preview/failed.gif" alt="Thread Totem failed animation" width="112"> |

| Waiting | Running | Review |
| --- | --- | --- |
| <img src="preview/waiting.gif" alt="Thread Totem waiting animation" width="112"> | <img src="preview/running.gif" alt="Thread Totem running animation" width="112"> | <img src="preview/review.gif" alt="Thread Totem review animation" width="112"> |

The full Codex install asset is [`spritesheet.webp`](spritesheet.webp). GIF previews are rendered from the committed spritesheet for GitHub review.

## Install

```bash
mkdir -p ~/.codex/pets
cp -R pets/thread-totem ~/.codex/pets/
```

Then refresh custom pets in Codex and select `Thread Totem`.

## Motion Notes

- `idle`: beads breathe along a lightly swaying cord.
- `running-right` / `running-left`: the beads lean and drag with directional intent.
- `waving`: the top bead flicks like a polite signal.
- `jumping`: the whole cord lifts as the beads hold formation.
- `failed`: the cord kinks and one bead turns into the problem.
- `waiting`: the amber center bead pauses, visibly asking for input.
- `running`: beads travel upward like work passing through a queue.
- `review`: the cord straightens and the beads align.

## Source

- Origin: original state-instrument pet generated for Familiars.
- Author: Jorge Alcantara / Zentrik.
- License: MIT for this pet bundle in this repository.
- Generator: [`scripts/generate_state_instruments.py`](../../scripts/generate_state_instruments.py).

## Preview

Full contact sheet: [preview/contact-sheet.png](preview/contact-sheet.png)
