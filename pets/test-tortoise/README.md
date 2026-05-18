# Test Tortoise

A slow reliable test-runner tortoise whose shell panels move through a tidy
test matrix.

![Test Tortoise idle animation](preview/idle.gif)

## Animation Catalog

| Idle | Running Right | Running Left |
| --- | --- | --- |
| <img src="preview/idle.gif" alt="Test Tortoise idle animation" width="112"> | <img src="preview/running-right.gif" alt="Test Tortoise running right animation" width="112"> | <img src="preview/running-left.gif" alt="Test Tortoise running left animation" width="112"> |

| Waving | Jumping | Failed |
| --- | --- | --- |
| <img src="preview/waving.gif" alt="Test Tortoise waving animation" width="112"> | <img src="preview/jumping.gif" alt="Test Tortoise jumping animation" width="112"> | <img src="preview/failed.gif" alt="Test Tortoise failed animation" width="112"> |

| Waiting | Running | Review |
| --- | --- | --- |
| <img src="preview/waiting.gif" alt="Test Tortoise waiting animation" width="112"> | <img src="preview/running.gif" alt="Test Tortoise running animation" width="112"> | <img src="preview/review.gif" alt="Test Tortoise review animation" width="112"> |

The full Codex install asset is [`spritesheet.webp`](spritesheet.webp). GIF previews are rendered from the committed spritesheet for GitHub review.

## Install

```bash
mkdir -p ~/.codex/pets
cp -R pets/test-tortoise ~/.codex/pets/
```

Then refresh custom pets in Codex and select `Test Tortoise`.

## Motion Notes

- `waiting`: extends its head and holds, asking for the next test target.
- `running`: ticks attached shell panels through a test-matrix loop.
- `review`: peers over the shell rim at final results.
- `failed`: retracts halfway while the shell dips.

## Source

- Origin: original pet generated for Familiars.
- Author: Jorge Alcantara / Zentrik.
- License: MIT for this pet bundle in this repository.

## Preview

Full contact sheet: [preview/contact-sheet.png](preview/contact-sheet.png)
