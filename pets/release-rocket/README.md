# Release Rocket

A controlled deployment rocket whose fins and attached flame announce launch readiness without panic.

![Release Rocket idle animation](preview/idle.gif)

## Animation Catalog

| Idle | Running Right | Running Left |

| --- | --- | --- |

| <img src="preview/idle.gif" alt="Release Rocket idle animation" width="112"> | <img src="preview/running-right.gif" alt="Release Rocket running-right animation" width="112"> | <img src="preview/running-left.gif" alt="Release Rocket running-left animation" width="112"> |


| Waving | Jumping | Failed |

| --- | --- | --- |

| <img src="preview/waving.gif" alt="Release Rocket waving animation" width="112"> | <img src="preview/jumping.gif" alt="Release Rocket jumping animation" width="112"> | <img src="preview/failed.gif" alt="Release Rocket failed animation" width="112"> |


| Waiting | Running | Review |

| --- | --- | --- |

| <img src="preview/waiting.gif" alt="Release Rocket waiting animation" width="112"> | <img src="preview/running.gif" alt="Release Rocket running animation" width="112"> | <img src="preview/review.gif" alt="Release Rocket review animation" width="112"> |


The full Codex install asset is [`spritesheet.webp`](spritesheet.webp). GIF previews are rendered from the committed spritesheet for GitHub review.

## Install

```bash
mkdir -p ~/.codex/pets
cp -R pets/release-rocket ~/.codex/pets/
```

Then refresh custom pets in Codex and select `Release Rocket`.

## Motion Notes

- `idle`: hovers with a small attached flame pulse and locked fins.

- `running-right`: slides right with fins steering and flame tucked close to the body.

- `running-left`: slides left with the same controlled hover cadence.

- `waving`: tilts a fin in a restrained pre-launch salute.

- `jumping`: compresses down, rises on an attached flame shape, and settles.

- `failed`: nose dips while the flame shrinks into the rocket body.

- `waiting`: holds a launchpad posture, nose angled toward the user for go/no-go.

- `running`: cycles fin checks and attached flame pulses like a release checklist.

- `review`: tilts into final inspection with both fins locked.

## Source

- Origin: original pet generated for Familiars.

- Author: Jorge Alcantara / Zentrik.

- License: MIT for this pet bundle in this repository.

## Preview

Full contact sheet: [preview/contact-sheet.png](preview/contact-sheet.png)
