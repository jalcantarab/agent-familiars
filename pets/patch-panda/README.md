# Patch Panda

A meticulous panda that applies tiny repair patches with careful tactile paw
work.

![Patch Panda idle animation](preview/idle.gif)

## Animation Catalog

| Idle | Running Right | Running Left |
| --- | --- | --- |
| <img src="preview/idle.gif" alt="Patch Panda idle animation" width="112"> | <img src="preview/running-right.gif" alt="Patch Panda running right animation" width="112"> | <img src="preview/running-left.gif" alt="Patch Panda running left animation" width="112"> |

| Waving | Jumping | Failed |
| --- | --- | --- |
| <img src="preview/waving.gif" alt="Patch Panda waving animation" width="112"> | <img src="preview/jumping.gif" alt="Patch Panda jumping animation" width="112"> | <img src="preview/failed.gif" alt="Patch Panda failed animation" width="112"> |

| Waiting | Running | Review |
| --- | --- | --- |
| <img src="preview/waiting.gif" alt="Patch Panda waiting animation" width="112"> | <img src="preview/running.gif" alt="Patch Panda running animation" width="112"> | <img src="preview/review.gif" alt="Patch Panda review animation" width="112"> |

The full Codex install asset is [`spritesheet.webp`](spritesheet.webp). GIF previews are rendered from the committed spritesheet for GitHub review.

## Install

```bash
mkdir -p ~/.codex/pets
cp -R pets/patch-panda ~/.codex/pets/
```

Then refresh custom pets in Codex and select `Patch Panda`.

## Motion Notes

- `waiting`: offers a held patch and asks where it should go.
- `running`: presses, smooths, and checks an attached patch.
- `review`: leans close to inspect the patch edge.
- `failed`: keeps the peeled patch attached while slumping in repair frustration.

## Source

- Origin: original pet generated for Familiars.
- Author: Jorge Alcantara / Zentrik.
- License: MIT for this pet bundle in this repository.

## Preview

Full contact sheet: [preview/contact-sheet.png](preview/contact-sheet.png)
