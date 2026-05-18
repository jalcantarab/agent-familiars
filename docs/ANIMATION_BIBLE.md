# Animation Bible

Familiars should feel like a collection of small characters with jobs, not
a folder of interchangeable sprite loops.

## Core Rule

Every pet needs a motion language that comes from its body, work metaphor, and
personality.

Bad:

- all pets jump by moving straight up and down
- all pets wave with a generic raised arm
- all pets run with mammal legs
- all working states look like typing
- review is just idle with smaller eyes

Good:

- no-leg pets drift, glide, float, swim, roll, or snap between positions
- heavy pets compress and lag before they move
- careful pets have smaller, slower, more precise loops
- review states focus the pet's signature sense organ or tool
- waiting states clearly ask for human input without punctuation or UI symbols

## The Nine Codex States

| State | Purpose | Non-generic requirement |
| --- | --- | --- |
| `idle` | Calm baseline and reduced-motion first frame. | Must show the pet's resting personality, not generic breathing. |
| `running-right` | Directional movement to the right. | Must match the pet's actual body mechanics. |
| `running-left` | Directional movement to the left. | Must match `running-right` without side-specific artifacts. |
| `waving` | Friendly attention gesture. | Must use the pet's own appendage or body feature. |
| `jumping` | Hover/click delight. | Must answer how this character lifts, pops, glides, or refuses to jump. |
| `failed` | Blocked/error state. | Must show a character-specific collapse, dim, tangle, droop, or recoil. |
| `waiting` | Needs user input. | Must face or offer a decision to the user through posture. |
| `running` | Active work, not directional running. | Must show the pet doing its job metaphor. |
| `review` | Inspection or completion review. | Must sharpen the pet's inspection behavior beyond idle. |

## Top-10 Direction

The top ten are defined in `catalog/flagship-10.json`. These should be treated
as launch-quality briefs before any new sprite generation starts.

The current top ten:

1. Zentri
2. Terminal Ghost
3. Review Owl
4. Bug Hunter
5. Rubber Duck 2.0
6. Token Vampire
7. Merge Mammoth
8. CI Phoenix
9. Patch Panda
10. Product Crane

## First-50 Motion DNA

The broader first-50 motion language is defined in
`catalog/first-50-motion.json`. Each candidate has at least:

- locomotion
- hover or jump behavior
- active work loop
- waiting posture
- failed reaction
- review behavior

This file is a design constraint, not a final prompt. When a pet graduates to
production, expand it into a full nine-state spec and generate the atlas from
that character-specific motion language.

## Production Acceptance

Before a pet is accepted:

- all nine rows must preserve identity and scale
- no state should introduce floating UI, punctuation, loose icons, loose dust,
  or non-removable shadows
- no state should copy another pet's distinctive motion
- no-leg pets must not fake a normal leg run
- heavy pets must not move like light pets
- review must look meaningfully different from idle
- waiting must look like input is needed
- failure must look like this character failed, not a generic sad face
