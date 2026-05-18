# React Gecko

A frontend state gecko whose sticky toes and color patches make component state transitions visible.

![React Gecko idle animation](preview/idle.gif)

## Animation Catalog

| Idle | Running Right | Running Left |
| --- | --- | --- |
| <img src="preview/idle.gif" alt="React Gecko idle animation" width="112"> | <img src="preview/running-right.gif" alt="React Gecko running right animation" width="112"> | <img src="preview/running-left.gif" alt="React Gecko running left animation" width="112"> |

| Waving | Jumping | Failed |
| --- | --- | --- |
| <img src="preview/waving.gif" alt="React Gecko waving animation" width="112"> | <img src="preview/jumping.gif" alt="React Gecko jumping animation" width="112"> | <img src="preview/failed.gif" alt="React Gecko failed animation" width="112"> |

| Waiting | Running | Review |
| --- | --- | --- |
| <img src="preview/waiting.gif" alt="React Gecko waiting animation" width="112"> | <img src="preview/running.gif" alt="React Gecko running animation" width="112"> | <img src="preview/review.gif" alt="React Gecko review animation" width="112"> |

The full Codex install asset is [`spritesheet.webp`](spritesheet.webp). GIF previews are rendered from the committed spritesheet for GitHub review.

## Install

```bash
mkdir -p ~/.codex/pets
cp -R pets/react-gecko ~/.codex/pets/
```

Then refresh custom pets in Codex and select `React Gecko`.

## Motion Notes

- `idle`: holds a quiet wall-crawl pose with tiny toe, tail, and patch micro-motion.
- `running-right` / `running-left`: wall-crawls through sticky-toe placements.
- `waving`: greets by lifting a sticky toe or forelimb.
- `jumping`: toe-pops upward while the tail counterbalances.
- `failed`: flattens as state escapes, with dropped tail and splayed toes.
- `waiting`: freezes with one sticky toe lifted, waiting for state input.
- `running`: reorders body patches like component state transitions while braced in place.
- `review`: tilts its head at a component boundary while the toes brace.

## Source

- Origin: original pet generated for Familiars.
- Author: Jorge Alcantara / Zentrik.
- License: MIT for this pet bundle in this repository.

## Preview

Full contact sheet: [preview/contact-sheet.png](preview/contact-sheet.png)
