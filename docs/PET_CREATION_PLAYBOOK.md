# Pet Creation Playbook

This is the deeper guide for making pets that feel delightful in real use, not
just attractive in a large preview.

The short version:

1. Write the character bible first.
2. Define the motion language before prompting images.
3. Generate and approve one row at a time.
4. Reject rows that do not read at desktop pet size.
5. Validate the final package before installing or sharing.

## The Mental Model

A great pet is a tiny state machine with personality. That personality can come
from a creature, but it can also come from an object with a disciplined state
grammar: a surface that changes color, a lantern that protects a flame, or a
tool whose material reacts to the work. The state-instrument pets lean into
that middle ground: companion objects that are useful first, but still have a
little ceremony.

The Codex-compatible package format gives you nine rows:

| Row | State | What It Should Communicate |
| --- | --- | --- |
| 0 | `idle` | calm baseline and reduced-motion first frame |
| 1 | `running-right` | directional drag or rightward travel |
| 2 | `running-left` | directional drag or leftward travel |
| 3 | `waving` | attention, greeting, beckon, salute, or callout |
| 4 | `jumping` | hover or click delight |
| 5 | `failed` | blocked, cancelled, wrong, tangled, or broken |
| 6 | `waiting` | needs human input, approval, or direction |
| 7 | `running` | active work, processing, scanning, or execution |
| 8 | `review` | inspecting, evaluating, or presenting a result |

The core mistake is prompting nine generic animations. Instead, each row should
answer a character question:

```text
How does this specific body move when it works, waits, reviews, and fails?
```

## Character Bible

Before image generation, write a compact bible:

```text
Name:
Audience moment:
Character core:
Visual lock:
Motion language:
Primary tool or appendage:
Tiny-size read:
Forbidden details:
License/source:
```

Example:

```text
Name: Zentri
Audience moment: product work moving from intent to implementation
Character core: alert folded-paper crane
Visual lock: white origami facets, charcoal crease lines, cyan accent fold
Motion language: crease tension, precise refolding, economical wing gestures
Primary tool or appendage: folded wing and long neck
Tiny-size read: crane silhouette plus cyan decision accent
Forbidden details: readable logos, UI screenshots, text, detached glow
License/source: original asset in this repository
```

## Prompt Anatomy

Use this structure for the base image:

```text
Create one clean full-body reference sprite for <pet name>.

Identity:
<one-sentence character lock>

Visual lock:
<shape, palette, material, face, props, proportions>

Motion readiness:
<what parts need to animate clearly across rows>

Style:
compact pet-safe sprite, readable at 192x208, crisp silhouette, stable palette,
simple face, clean edges for alpha extraction.

Background:
perfectly flat chroma-key background, no shadow, no scenery, no text, no
checkerboard, no glow, no detached effects.
```

Use this structure for each row:

```text
Create one horizontal animation strip for <pet id>, state <state>.

Use the canonical base only for identity. Output exactly <frame count> complete
poses in one row on a flat chroma-key background.

Identity lock:
<same silhouette, face, palette, proportions, props, material>

Character-specific motion:
<state-specific animation brief>

Tiny-size read:
<the one or two silhouette beats that must still read when small>

Reject conditions:
no text, guide marks, shadows, speed lines, dust, detached effects, anatomy
drift, prop drift, scale drift, copied UI, or chroma-key colors inside the pet.
```

## State Prompts

Use these questions before writing each row prompt.

### `idle`

- What is the pet's quiet resting personality?
- What is the smallest visible loop: blink, breath, weight shift, material sway?
- Does the first frame work as a static reduced-motion pet?

Avoid: busy acting, waving, working, reviewing, or changing props.

### `running-right` And `running-left`

- Does this pet walk, glide, roll, scuttle, hop, swim, flutter, snap, or drift?
- What body part leads the direction?
- Can the row loop without feeling like a one-way dash?

Avoid: forcing legs onto no-leg pets, speed lines, dust, and full-sheet motion
trails. Mirror only when side-specific markings and props still make sense.

### `waving`

- What does this character use to get attention?
- Is the gesture a wave, wing fold, antenna flick, trunk curl, salute, nod, or
  beckon?
- Does the gesture read without wave marks or symbols?

Avoid: subtle finger-only motion, floating lines, and generic hello poses.

### `jumping`

- What is this pet's physical relationship to lift?
- Does it hop, pop, spring, bob, flutter, compress, or almost refuse to leave
  the ground?
- What is the anticipation and recovery?

Avoid: making heavy pets athletic, adding floor shadows, dust, or landing marks.

### `failed`

- What does failure do to this character's body or tool?
- Does it tangle, slump, dim, fold, jam, deflate, recoil, or close?
- Can you read the failure from silhouette and posture?

Avoid: generic sadness, red X symbols, detached tears, or random bug imagery.

### `waiting`

- How does the pet ask the human for input?
- Does it offer something, hold a decision pose, stare, tilt, tap, or pause?
- Is it clearly different from idle and review?

Avoid: neutral standing loops and punctuation bubbles.

### `running`

- What does this pet look like while doing its job?
- Does it scan, sort, type, repair, compile, inspect, warm up, trace, or process?
- What is the repeated work loop?

Avoid: literal foot-running unless the pet's job is actually motion.

### `review`

- What is the pet's inspection behavior?
- Which sense organ, tool, posture, or prop sharpens?
- Does it feel decisive or evaluative?

Avoid: adding new tiny props that vanish at pet size.

## QA Ladder

Review rows in this order:

1. **Semantic read:** the row clearly says the intended state.
2. **Tiny-size read:** the action still reads when mentally shrunk.
3. **Loop closure:** the final frame returns cleanly to the first.
4. **Identity lock:** same species/object, face, proportions, palette, material.
5. **Scale and baseline:** no unintended growth, shrinking, or vertical popping.
6. **Anatomy and props:** no extra limbs, merged parts, drifting props, or blobs.
7. **Packing safety:** no body parts cross frame cuts or touch cell edges.
8. **Alpha safety:** no white backgrounds, shadows, glows, guide marks, or debris.

Do not debate polish until semantic read passes.

## Repair Prompts

When a row fails, repair the smallest scope. Do not regenerate the whole pet.

Use a repair note like this:

```text
Repair only the <state> row for <pet id>.

Keep:
<identity lock>

Fix:
<one or two concrete failures>

Preserve:
same frame count, same chroma-key background, same pet size, same palette,
same prop design, no new detached effects.

Reject:
<specific failure pattern from QA>
```

Examples:

- "The running row became generic jogging. Make it a trunk-led heavy trudge."
- "The waiting row looks like idle. Have the pet offer the decision object to
  the viewer."
- "The failed row uses floating symbols. Replace them with body collapse."
- "The row is pretty large but unreadable small. Increase silhouette contrast,
  not detail density."

## Useful Tool Stack

Use only what helps the pet reach the quality bar.

| Need | Good Tooling |
| --- | --- |
| Full Codex pet generation | the local `hatch-pet` skill |
| Alternate skill workflow | [`wyddy7/codex-pet-generator`](https://github.com/wyddy7/codex-pet-generator) for character bible, row semantics, approval gating, packing, and validation |
| Gallery and distribution | [`petdex`](https://github.com/crafter-station/petdex), which provides a gallery, CLI install, submit flow, and public manifest |
| React preview/playground | [`codex-pets-react`](https://github.com/backnotprop/codex-pets-react), with `SpriteAnimator`, `PetWidget`, and a shared atlas contract |
| Claude Code desktop testing | [`Claude Pets`](https://github.com/xianshang33/claude-pets), which reads Codex-compatible pets from `~/.claude/pets` |
| Shared local desktop pet | [`OpenPets`](https://github.com/alterhq/openpets), which exposes MCP/CLI control and supports Codex pet atlases |
| Agent-state desktop companion | [`Clawd on Desk`](https://github.com/rullerzhou-afk/clawd-on-desk), which maps agent hooks and sessions into visible desktop states |

## Cross-Agent Design

Codex-compatible pets can be useful outside Codex when another tool can play
the same atlas. Recent community tools use pets for:

- visible long-running task progress
- permission or approval prompts
- waiting-for-human states
- completion and review moments
- failure or retry loops
- multi-session or subagent activity

That means a stronger pet should not optimize only for "cute idle." It should
have especially clear `waiting`, `running`, `review`, and `failed` rows.

## Public Sharing Rules

Before sharing a pet:

- install it locally and test it in Codex
- validate `pet.json` and `spritesheet.webp`
- keep license and source attribution clear
- avoid non-commercial, no-license, fan-art, or trademark-sensitive assets
- include a short motion-language note so others understand the design intent

The repo's north star is simple: share pets people can actually use, learn
from, improve, and remix safely.
