# Stakeholder Weather Vane

A product stakeholder-weather pet that shows shifting opinions without naming
any company, team, or stakeholder.

![Stakeholder Weather Vane idle animation](preview/idle.gif)

## Animation Catalog

| Idle | Running Right | Running Left |
| --- | --- | --- |
| <img src="preview/idle.gif" alt="Stakeholder Weather Vane idle animation" width="112"> | <img src="preview/running-right.gif" alt="Stakeholder Weather Vane running right animation" width="112"> | <img src="preview/running-left.gif" alt="Stakeholder Weather Vane running left animation" width="112"> |

| Waving | Jumping | Failed |
| --- | --- | --- |
| <img src="preview/waving.gif" alt="Stakeholder Weather Vane waving animation" width="112"> | <img src="preview/jumping.gif" alt="Stakeholder Weather Vane jumping animation" width="112"> | <img src="preview/failed.gif" alt="Stakeholder Weather Vane failed animation" width="112"> |

| Waiting | Running | Review |
| --- | --- | --- |
| <img src="preview/waiting.gif" alt="Stakeholder Weather Vane waiting animation" width="112"> | <img src="preview/running.gif" alt="Stakeholder Weather Vane running animation" width="112"> | <img src="preview/review.gif" alt="Stakeholder Weather Vane review animation" width="112"> |

The full Codex install asset is [`spritesheet.webp`](spritesheet.webp). GIF previews are rendered from the committed spritesheet for GitHub review.

## Install

```bash
mkdir -p ~/.codex/pets
cp -R pets/stakeholder-weather-vane ~/.codex/pets/
```

Then refresh custom pets in Codex and select `Stakeholder Weather Vane`.

## Motion Notes

- `idle`: makes one tiny forecast twitch on its bearing.
- `running-right` / `running-left`: scoots while the vane leans into pressure.
- `waving`: turns the vane in a polite half-nod.
- `jumping`: gets lifted by a small gust and wobbles back into place.
- `failed`: flattens into contradictory pressure without detached effects.
- `waiting`: holds an awkward diagonal until the direction is supplied.
- `running`: tests a few candidate bearings before settling.
- `review`: holds one clean forecast direction.

## Source

- Origin: original pet generated for Familiars.
- Author: Jorge Alcantara / Zentrik.
- License: MIT for this pet bundle in this repository.

## Preview

Full contact sheet: [preview/contact-sheet.png](preview/contact-sheet.png)
