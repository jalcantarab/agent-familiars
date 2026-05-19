# Product Trope Pets

This pack is for product people who recognize the recurring rituals of product work: protecting focus, cutting scope, pruning to an MVP, excavating old backlog ideas, finding signal, and answering prioritization riddles.

The design rule is stricter than `make it cute`: every pet needs a specific state carrier that tells the user what is happening in that pet's own language.

```text
Personality chooses the gesture. The state carrier tells the event.
```

## Production Rules

- Each pet must have one unmistakable state carrier: shield, feature heads, leaf growth, fossil layers, folded signal posture, tablet, polarity plates, vane, scale pans, contained flame, or quest gear.
- The carrier must belong to the body or held object. Avoid loose UI, floating icons, tiny labels, detached particles, and generic animation beats.
- Waiting should feel like a real product pause: a decision, tradeoff, approval, or signal choice is needed.
- Failure should deform the pet's own carrier: buried shield, regrown heads, overgrowth, fossil strata, noisy heron facets, cracked tablet, over-repelling plates, contradictory pressure, sinking pans, or guttering flame.
- Directional rows can move across the screen, but they should still preserve the pet's personality and state carrier.

## Validated Set

| Pet | Personality | State Carrier | Why It Lands |
| --- | --- | --- | --- |
| No Knight | Ceremonial, stubborn, tender about focus. | Shield-billboard. | Focus protection becomes heroic and absurd. |
| Feature Hydra | Cute, chaotic, hard to scope. | Regrowing feature heads. | Feature creep becomes a body mechanic. |
| MVP Bonsai | Disciplined, bright, quietly ruthless. | Leaf growth and pruning. | Product taste is shown as what gets cut back. |
| Backlog Archaeologist | Curious, skeptical, scholarly. | Fossil shell and brush-tail. | Ancient tickets become archaeological artifacts. |
| Signal Heron | Zen, observant, exacting. | Folded posture and cyan signal accent. | Signal emerges through stillness instead of noise. |
| Priority Sphinx | Ancient, dry, fair. | Abstract tradeoff tablet. | Prioritization becomes a riddle that must be answered. |
| Alignment Magnet | Patient, diplomatic, slightly smug. | Embedded polarity plates. | Alignment becomes a physical field that can converge or repel. |
| Stakeholder Weather Vane | Dry, observant, lightly theatrical. | Attached vane and tail fin. | Opinion shifts become a forecast instead of a meeting complaint. |
| Tradeoff Scale | Measured, exacting, slightly dramatic. | Attached balance pans. | Tradeoffs become real weight instead of a list of wishes. |
| Launch Lantern | Hopeful, careful, ceremonially nervous. | Contained flame. | Readiness becomes a flame that can be tuned, shielded, or gutter. |
| RICE Centurion | Earnest, officious, helpfully clumsy. | Wax-tablet shield with four scoring beads. | Prioritization becomes a little ritual of scoring, jamming, and settling. |
| Queue Quixote | Hopeful, courtly, almost too brave. | Lance with blank queue tickets and token buckler. | Backlog zeal becomes a noble charge that still needs a reality check. |

## Current Status

The twelve pets above have generated `spritesheet.webp` files, pet manifests, preview GIFs, contact sheets, deterministic atlas validation, and final visual QA acceptance. They are installable with:

```bash
python3 scripts/install_pet.py --pack product-tropes
```

The structured production briefs live in `catalog/product-trope-pets.json`.
