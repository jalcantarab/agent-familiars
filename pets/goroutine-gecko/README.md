# Goroutine Gecko

A service-concurrency gecko whose sticky toes and staggered spots keep parallel work coordinated.

![Goroutine Gecko idle animation](preview/idle.gif)

## Animation Catalog

| Idle | Running Right | Running Left |
| --- | --- | --- |
| <img src="preview/idle.gif" alt="Goroutine Gecko idle animation" width="112"> | <img src="preview/running-right.gif" alt="Goroutine Gecko running right animation" width="112"> | <img src="preview/running-left.gif" alt="Goroutine Gecko running left animation" width="112"> |

| Waving | Jumping | Failed |
| --- | --- | --- |
| <img src="preview/waving.gif" alt="Goroutine Gecko waving animation" width="112"> | <img src="preview/jumping.gif" alt="Goroutine Gecko jumping animation" width="112"> | <img src="preview/failed.gif" alt="Goroutine Gecko failed animation" width="112"> |

| Waiting | Running | Review |
| --- | --- | --- |
| <img src="preview/waiting.gif" alt="Goroutine Gecko waiting animation" width="112"> | <img src="preview/running.gif" alt="Goroutine Gecko running animation" width="112"> | <img src="preview/review.gif" alt="Goroutine Gecko review animation" width="112"> |

The full Codex install asset is [`spritesheet.webp`](spritesheet.webp). GIF previews are rendered from the committed spritesheet for GitHub review.

## Install

```bash
mkdir -p ~/.codex/pets
cp -R pets/goroutine-gecko ~/.codex/pets/
```

Then refresh custom pets in Codex and select `Goroutine Gecko`.

## Motion Notes

- `idle`: waits in a calm scheduler pose with tiny toe and tail timing.
- `running-right` / `running-left`: moves through coordinated sticky-toe footfalls.
- `waving`: greets with a raised sticky toe and balanced tail.
- `jumping`: pops upward through sequential toe lift and tail balance.
- `failed`: splays toes in mismatched timing while the tail drops out of sync.
- `waiting`: freezes with one toe raised and the tail held like a paused channel.
- `running`: taps through parallel service checks while body spots pulse in staggered lanes.
- `review`: pivots between body spots to check handoff order.

## Source

- Origin: original pet generated for Familiars.
- Author: Jorge Alcantara / Zentrik.
- License: MIT for this pet bundle in this repository.

## Preview

Full contact sheet: [preview/contact-sheet.png](preview/contact-sheet.png)
