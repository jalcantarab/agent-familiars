# Design Finch

A UI QA finch that measures spacing and nudges alignment with tiny precise hops.

![Design Finch idle animation](preview/idle.gif)

## Animation Catalog

| Idle | Running Right | Running Left |
| --- | --- | --- |
| <img src="preview/idle.gif" alt="Design Finch idle animation" width="112"> | <img src="preview/running-right.gif" alt="Design Finch running right animation" width="112"> | <img src="preview/running-left.gif" alt="Design Finch running left animation" width="112"> |

| Waving | Jumping | Failed |
| --- | --- | --- |
| <img src="preview/waving.gif" alt="Design Finch waving animation" width="112"> | <img src="preview/jumping.gif" alt="Design Finch jumping animation" width="112"> | <img src="preview/failed.gif" alt="Design Finch failed animation" width="112"> |

| Waiting | Running | Review |
| --- | --- | --- |
| <img src="preview/waiting.gif" alt="Design Finch waiting animation" width="112"> | <img src="preview/running.gif" alt="Design Finch running animation" width="112"> | <img src="preview/review.gif" alt="Design Finch review animation" width="112"> |

The full Codex install asset is [`spritesheet.webp`](spritesheet.webp). GIF previews are rendered from the committed spritesheet for GitHub review.

## Install

```bash
mkdir -p ~/.codex/pets
cp -R pets/design-finch ~/.codex/pets/
```

Then refresh custom pets in Codex and select `Design Finch`.

## Motion Notes

- `idle`: breathes with tiny feather and beak micro-motion.
- `running-right` / `running-left`: hops precisely between layout breakpoints.
- `waving`: greets through a small wing lift.
- `jumping`: performs a tight breakpoint hop with wings tucked, then balances.
- `failed`: fluffs unevenly like broken spacing.
- `waiting`: balances on one foot, waiting for the visual decision.
- `running`: measures invisible spacing with wing tips while the beak nudges alignment.
- `review`: points its beak along an invisible baseline in a held inspection stance.

## Source

- Origin: original pet generated for Familiars.
- Author: Jorge Alcantara / Zentrik.
- License: MIT for this pet bundle in this repository.

## Preview

Full contact sheet: [preview/contact-sheet.png](preview/contact-sheet.png)
