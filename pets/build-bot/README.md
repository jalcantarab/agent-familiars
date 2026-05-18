# Build Bot

A tiny build robot whose chest panel and antenna show build progress, input,
and failure.

![Build Bot idle animation](preview/idle.gif)

## Animation Catalog

| Idle | Running Right | Running Left |
| --- | --- | --- |
| <img src="preview/idle.gif" alt="Build Bot idle animation" width="112"> | <img src="preview/running-right.gif" alt="Build Bot running right animation" width="112"> | <img src="preview/running-left.gif" alt="Build Bot running left animation" width="112"> |

| Waving | Jumping | Failed |
| --- | --- | --- |
| <img src="preview/waving.gif" alt="Build Bot waving animation" width="112"> | <img src="preview/jumping.gif" alt="Build Bot jumping animation" width="112"> | <img src="preview/failed.gif" alt="Build Bot failed animation" width="112"> |

| Waiting | Running | Review |
| --- | --- | --- |
| <img src="preview/waiting.gif" alt="Build Bot waiting animation" width="112"> | <img src="preview/running.gif" alt="Build Bot running animation" width="112"> | <img src="preview/review.gif" alt="Build Bot review animation" width="112"> |

The full Codex install asset is [`spritesheet.webp`](spritesheet.webp). GIF previews are rendered from the committed spritesheet for GitHub review.

## Install

```bash
mkdir -p ~/.codex/pets
cp -R pets/build-bot ~/.codex/pets/
```

Then refresh custom pets in Codex and select `Build Bot`.

## Motion Notes

- `waiting`: freezes with one antenna upright and the chest panel paused mid-fill.
- `running`: fills chest-panel bars while its arms lock and release.
- `review`: leans its head lens forward while arms brace at its sides.
- `failed`: dims the chest panel while one arm hangs loose.

## Source

- Origin: original pet generated for Familiars.
- Author: Jorge Alcantara / Zentrik.
- License: MIT for this pet bundle in this repository.

## Preview

Full contact sheet: [preview/contact-sheet.png](preview/contact-sheet.png)
