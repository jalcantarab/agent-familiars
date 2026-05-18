# Pocket Oracle

A little tablet with an inner aperture. It feels more mystical than analytic,
but the states remain legible: amber for waiting, red for trouble, crisp
blue-white for review, and cyan/green for active work.

![Pocket Oracle idle animation](preview/idle.gif)

## Animation Catalog

| Idle | Running Right | Running Left |
| --- | --- | --- |
| <img src="preview/idle.gif" alt="Pocket Oracle idle animation" width="112"> | <img src="preview/running-right.gif" alt="Pocket Oracle running right animation" width="112"> | <img src="preview/running-left.gif" alt="Pocket Oracle running left animation" width="112"> |

| Waving | Jumping | Failed |
| --- | --- | --- |
| <img src="preview/waving.gif" alt="Pocket Oracle waving animation" width="112"> | <img src="preview/jumping.gif" alt="Pocket Oracle jumping animation" width="112"> | <img src="preview/failed.gif" alt="Pocket Oracle failed animation" width="112"> |

| Waiting | Running | Review |
| --- | --- | --- |
| <img src="preview/waiting.gif" alt="Pocket Oracle waiting animation" width="112"> | <img src="preview/running.gif" alt="Pocket Oracle running animation" width="112"> | <img src="preview/review.gif" alt="Pocket Oracle review animation" width="112"> |

The full Codex install asset is [`spritesheet.webp`](spritesheet.webp). GIF previews are rendered from the committed spritesheet for GitHub review.

## Install

```bash
mkdir -p ~/.codex/pets
cp -R pets/pocket-oracle ~/.codex/pets/
```

Then refresh custom pets in Codex and select `Pocket Oracle`.

## Motion Notes

- `idle`: aperture breathes quietly inside the tablet.
- `running-right` / `running-left`: orbiting marks rotate with directional bias.
- `waving`: a top corner folds open as a small hello.
- `jumping`: the aperture lifts into a crescent.
- `failed`: the surface cracks and clouds red.
- `waiting`: the aperture opens wide in amber and holds.
- `running`: abstract marks orbit like a live query.
- `review`: the aperture turns into a scanning lens.

## Source

- Origin: original state-instrument pet generated for Familiars.
- Author: Jorge Alcantara / Zentrik.
- License: MIT for this pet bundle in this repository.
- Generator: [`scripts/generate_state_instruments.py`](../../scripts/generate_state_instruments.py).

## Preview

Full contact sheet: [preview/contact-sheet.png](preview/contact-sheet.png)
