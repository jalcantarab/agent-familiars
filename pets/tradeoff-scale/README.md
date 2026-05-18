# Tradeoff Scale

A tradeoff companion that makes product choices feel like balancing real weight
instead of listing pros and cons.

![Tradeoff Scale idle animation](preview/idle.gif)

## Animation Catalog

| Idle | Running Right | Running Left |
| --- | --- | --- |
| <img src="preview/idle.gif" alt="Tradeoff Scale idle animation" width="112"> | <img src="preview/running-right.gif" alt="Tradeoff Scale running right animation" width="112"> | <img src="preview/running-left.gif" alt="Tradeoff Scale running left animation" width="112"> |

| Waving | Jumping | Failed |
| --- | --- | --- |
| <img src="preview/waving.gif" alt="Tradeoff Scale waving animation" width="112"> | <img src="preview/jumping.gif" alt="Tradeoff Scale jumping animation" width="112"> | <img src="preview/failed.gif" alt="Tradeoff Scale failed animation" width="112"> |

| Waiting | Running | Review |
| --- | --- | --- |
| <img src="preview/waiting.gif" alt="Tradeoff Scale waiting animation" width="112"> | <img src="preview/running.gif" alt="Tradeoff Scale running animation" width="112"> | <img src="preview/review.gif" alt="Tradeoff Scale review animation" width="112"> |

The full Codex install asset is [`spritesheet.webp`](spritesheet.webp). GIF previews are rendered from the committed spritesheet for GitHub review.

## Install

```bash
mkdir -p ~/.codex/pets
cp -R pets/tradeoff-scale ~/.codex/pets/
```

Then refresh custom pets in Codex and select `Tradeoff Scale`.

## Motion Notes

- `idle`: lets the pans breathe in opposite directions.
- `running-right` / `running-left`: moves with the leading pan carrying weight.
- `waving`: lifts one pan like a tiny courtroom greeting.
- `jumping`: performs a careful low hop while the pans swing through level.
- `failed`: sinks both pans at once and bends the beam without falling apart.
- `waiting`: holds two uneven options until the tradeoff is accepted.
- `running`: shifts counterweight pan-to-pan until the beam becomes level.
- `review`: settles into a level beam with one crisp pivot beat.

## Source

- Origin: original pet generated for Familiars.
- Author: Jorge Alcantara / Zentrik.
- License: MIT for this pet bundle in this repository.

## Preview

Full contact sheet: [preview/contact-sheet.png](preview/contact-sheet.png)
