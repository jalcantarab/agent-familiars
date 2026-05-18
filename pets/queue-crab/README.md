# Queue Crab

A sideways job-queue crab whose claws track pending work and pull tasks into
motion.

![Queue Crab idle animation](preview/idle.gif)

## Animation Catalog

| Idle | Running Right | Running Left |
| --- | --- | --- |
| <img src="preview/idle.gif" alt="Queue Crab idle animation" width="112"> | <img src="preview/running-right.gif" alt="Queue Crab running right animation" width="112"> | <img src="preview/running-left.gif" alt="Queue Crab running left animation" width="112"> |

| Waving | Jumping | Failed |
| --- | --- | --- |
| <img src="preview/waving.gif" alt="Queue Crab waving animation" width="112"> | <img src="preview/jumping.gif" alt="Queue Crab jumping animation" width="112"> | <img src="preview/failed.gif" alt="Queue Crab failed animation" width="112"> |

| Waiting | Running | Review |
| --- | --- | --- |
| <img src="preview/waiting.gif" alt="Queue Crab waiting animation" width="112"> | <img src="preview/running.gif" alt="Queue Crab running animation" width="112"> | <img src="preview/review.gif" alt="Queue Crab review animation" width="112"> |

The full Codex install asset is [`spritesheet.webp`](spritesheet.webp). GIF previews are rendered from the committed spritesheet for GitHub review.

## Install

```bash
mkdir -p ~/.codex/pets
cp -R pets/queue-crab ~/.codex/pets/
```

Then refresh custom pets in Codex and select `Queue Crab`.

## Motion Notes

- `waiting`: holds both claws at different heights like paused queue slots.
- `running`: alternates claws open and closed to pull the next task.
- `review`: pinches one invisible item while eyestalks inspect it.
- `failed`: droops its claws and collapses the sideways queue posture.

## Source

- Origin: original pet generated for Familiars.
- Author: Jorge Alcantara / Zentrik.
- License: MIT for this pet bundle in this repository.

## Preview

Full contact sheet: [preview/contact-sheet.png](preview/contact-sheet.png)
