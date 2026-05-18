# Latency Lemur

A performance lemur whose striped tail behaves like a tiny timing graph.

![Latency Lemur idle animation](preview/idle.gif)

## Animation Catalog

| Idle | Running Right | Running Left |
| --- | --- | --- |
| <img src="preview/idle.gif" alt="Latency Lemur idle animation" width="112"> | <img src="preview/running-right.gif" alt="Latency Lemur running right animation" width="112"> | <img src="preview/running-left.gif" alt="Latency Lemur running left animation" width="112"> |

| Waving | Jumping | Failed |
| --- | --- | --- |
| <img src="preview/waving.gif" alt="Latency Lemur waving animation" width="112"> | <img src="preview/jumping.gif" alt="Latency Lemur jumping animation" width="112"> | <img src="preview/failed.gif" alt="Latency Lemur failed animation" width="112"> |

| Waiting | Running | Review |
| --- | --- | --- |
| <img src="preview/waiting.gif" alt="Latency Lemur waiting animation" width="112"> | <img src="preview/running.gif" alt="Latency Lemur running animation" width="112"> | <img src="preview/review.gif" alt="Latency Lemur review animation" width="112"> |

The full Codex install asset is [`spritesheet.webp`](spritesheet.webp). GIF previews are rendered from the committed spritesheet for GitHub review.

## Install

```bash
mkdir -p ~/.codex/pets
cp -R pets/latency-lemur ~/.codex/pets/
```

Then refresh custom pets in Codex and select `Latency Lemur`.

## Motion Notes

- `idle`: holds an alert pose while the tail keeps a quiet measurement rhythm.
- `running-right` / `running-left`: hops with the striped tail acting as the timing trace.
- `waving`: gives a small lemur-hand hello while the tail stays visible.
- `jumping`: snaps into a vertical reaction hop with a tail-spike silhouette.
- `failed`: lets the timing tail droop into a long slow curve.
- `waiting`: freezes at a mid-height tail reading and waits for input.
- `running`: ticks the tail through low, high, and tail-latency-like heights.
- `review`: leans forward with the tail held straight as a measured baseline.

## Source

- Origin: original pet generated for Familiars.
- Author: Jorge Alcantara / Zentrik.
- License: MIT for this pet bundle in this repository.

## Preview

Full contact sheet: [preview/contact-sheet.png](preview/contact-sheet.png)
