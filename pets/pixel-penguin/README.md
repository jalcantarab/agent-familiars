# Pixel Penguin

A blocky server-room penguin whose square waddle and belly panels announce quiet system checks.

![Pixel Penguin idle animation](preview/idle.gif)

## Animation Catalog

| Idle | Running Right | Running Left |

| --- | --- | --- |

| <img src="preview/idle.gif" alt="Pixel Penguin idle animation" width="112"> | <img src="preview/running-right.gif" alt="Pixel Penguin running-right animation" width="112"> | <img src="preview/running-left.gif" alt="Pixel Penguin running-left animation" width="112"> |


| Waving | Jumping | Failed |

| --- | --- | --- |

| <img src="preview/waving.gif" alt="Pixel Penguin waving animation" width="112"> | <img src="preview/jumping.gif" alt="Pixel Penguin jumping animation" width="112"> | <img src="preview/failed.gif" alt="Pixel Penguin failed animation" width="112"> |


| Waiting | Running | Review |

| --- | --- | --- |

| <img src="preview/waiting.gif" alt="Pixel Penguin waiting animation" width="112"> | <img src="preview/running.gif" alt="Pixel Penguin running animation" width="112"> | <img src="preview/review.gif" alt="Pixel Penguin review animation" width="112"> |


The full Codex install asset is [`spritesheet.webp`](spritesheet.webp). GIF previews are rendered from the committed spritesheet for GitHub review.

## Install

```bash
mkdir -p ~/.codex/pets
cp -R pets/pixel-penguin ~/.codex/pets/
```

Then refresh custom pets in Codex and select `Pixel Penguin`.

## Motion Notes

- `idle`: holds a square, readable stance while the belly panel blinks in a slow server cadence.

- `running-right`: waddles right in pixel-step increments with flippers tucked close.

- `running-left`: waddles left in the same square cadence, led by the belly panel.

- `waving`: raises one flipper as a clipped terminal-room acknowledgement.

- `jumping`: does a tiny belly-hop; flippers stay close and the body lands square.

- `failed`: slides into a compact seated slump while the belly panel dims.

- `waiting`: stands upright with tucked flippers, holding a root-prompt stillness.

- `running`: alternates flipper taps while belly panels tick through server checks.

- `review`: leans forward and points one flipper at its config-like belly panel.

## Source

- Origin: original pet generated for Familiars.

- Author: Jorge Alcantara / Zentrik.

- License: MIT for this pet bundle in this repository.

## Preview

Full contact sheet: [preview/contact-sheet.png](preview/contact-sheet.png)
