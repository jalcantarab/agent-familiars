# Cluster Puffer

A scheduler puffer whose body spots inflate in balanced groups instead of copying any cluster logo.

![Cluster Puffer idle animation](preview/idle.gif)

## Animation Catalog

| Idle | Running Right | Running Left |

| --- | --- | --- |

| <img src="preview/idle.gif" alt="Cluster Puffer idle animation" width="112"> | <img src="preview/running-right.gif" alt="Cluster Puffer running-right animation" width="112"> | <img src="preview/running-left.gif" alt="Cluster Puffer running-left animation" width="112"> |


| Waving | Jumping | Failed |

| --- | --- | --- |

| <img src="preview/waving.gif" alt="Cluster Puffer waving animation" width="112"> | <img src="preview/jumping.gif" alt="Cluster Puffer jumping animation" width="112"> | <img src="preview/failed.gif" alt="Cluster Puffer failed animation" width="112"> |


| Waiting | Running | Review |

| --- | --- | --- |

| <img src="preview/waiting.gif" alt="Cluster Puffer waiting animation" width="112"> | <img src="preview/running.gif" alt="Cluster Puffer running animation" width="112"> | <img src="preview/review.gif" alt="Cluster Puffer review animation" width="112"> |


The full Codex install asset is [`spritesheet.webp`](spritesheet.webp). GIF previews are rendered from the committed spritesheet for GitHub review.

## Install

```bash
mkdir -p ~/.codex/pets
cp -R pets/cluster-puffer ~/.codex/pets/
```

Then refresh custom pets in Codex and select `Cluster Puffer`.

## Motion Notes

- `idle`: drifts in place with balanced node-spots breathing evenly.

- `running-right`: drifts right with tiny fin corrections like load being rebalanced.

- `running-left`: drifts left with the same controlled scheduler corrections.

- `waving`: tilts a fin in a small hello while the spots stay balanced.

- `jumping`: inflates, rises gently, then deflates back to baseline.

- `failed`: becomes lopsided as one group of spots over-inflates and fins tuck close.

- `waiting`: holds three half-inflated spots, visibly asking where capacity should go.

- `running`: pulses spots in balanced groups as if placing work across nodes.

- `review`: rolls slightly to expose one balanced spot group for inspection.

## Source

- Origin: original pet generated for Familiars.

- Author: Jorge Alcantara / Zentrik.

- License: MIT for this pet bundle in this repository.

## Preview

Full contact sheet: [preview/contact-sheet.png](preview/contact-sheet.png)
