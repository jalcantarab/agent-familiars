# Production Status

This file tracks which pets are actually installable and which are still
briefs. A pet is not "done" until it has a validated `pet.json`, a validated
`spritesheet.webp`, and visual QA has accepted the contact sheet.

## Target

The first production target is the full first-50 set from
`catalog/first-50-motion.json`.

Current public state:

- Installable pets: 66
- Motion briefs: 50
- Flagship production briefs: 10
- Missing installable first-50 pets: 0
- Product-folklore extras: 10
- State-instrument familiars: 6

## Quality Bar

Every generated pet must preserve its own motion language:

- no generic jumps
- no generic waves
- no generic sadness
- no forced leg running for pets without a leg-running body
- no detached effects, UI marks, text, symbols, dust, shadows, or guide marks
- waiting, running, failed, and review must be visually distinct from idle

The strongest rows for real agent work are:

- `waiting`: asks for human input or approval
- `running`: shows active task work
- `review`: inspects or presents the result
- `failed`: shows the character-specific failure mode

## Production Pipeline

For each new pet:

1. Prepare hatch-pet run folder and prompts.
2. Inject the character-specific motion brief into every row prompt.
3. Generate and approve base image.
4. Generate and approve row strips.
5. Derive `running-left` only when mirroring is visually safe.
6. Extract frames.
7. Inspect frames.
8. Compose atlas.
9. Validate atlas.
10. Create contact sheet and previews.
11. Run visual QA.
12. Package into `pets/<pet-id>/`.
13. Update `catalog/pets.json`, `NOTICE.md`, and pet README.
14. Install locally and test in Codex.

## Flagship Completion

| Rank | Pet | Repo Status | Production Status |
| --- | --- | --- | --- |
| 1 | Zentri | Installable | Done |
| 2 | Terminal Ghost | Installable | Done |
| 3 | Review Owl | Installable | Done |
| 4 | Bug Hunter | Installable | Done |
| 5 | Rubber Duck 2.0 | Installable | Done |
| 6 | Token Vampire | Installable | Done |
| 7 | Merge Mammoth | Installable | Done; generated atlas passed frame inspection, atlas validation, and visual QA |
| 8 | CI Phoenix | Installable | Done; generated atlas passed frame inspection, atlas validation, and visual QA |
| 9 | Patch Panda | Installable | Done; generated atlas passed frame inspection, atlas validation, and visual QA |
| 10 | Product Crane | Installable | Done; generated atlas passed frame inspection, atlas validation, and visual QA |

## Product Trope Pack

The product-trope pack is installable and visually QA accepted:

- `no-knight`
- `feature-hydra`
- `mvp-bonsai`
- `backlog-archaeologist`
- `signal-heron`
- `priority-sphinx`
- `alignment-magnet`
- `stakeholder-weather-vane`
- `tradeoff-scale`
- `launch-lantern`

These pets live outside the original first-50 developer-workflow list and are
tracked as product-community companions.

## First-50 Completion

The complete first-50 motion set is installable. The final completion batch
added:

- `pixel-penguin`
- `container-hermit`
- `cluster-puffer`
- `search-salmon`
- `schema-snail`
- `roadmap-raven`
- `meeting-moth`
- `notebook-newt`
- `migration-mantis`
- `demo-dolphin`

## Local Production Scratch Space

Temporary run folders live under:

```text
/tmp/agent-familiars-work/<pet-id>/
```

Finished, accepted assets are copied into:

```text
pets/<pet-id>/
```

Temporary run folders are not part of the public repository.
