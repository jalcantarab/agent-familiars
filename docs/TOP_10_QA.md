# Top Ten QA

This is the launch-brief QA record for the pets that should define the
repository's taste level. It verifies design specificity, not finished artwork
for every planned pet.

## What Is Verified

- `catalog/flagship-10.json` contains exactly 10 flagship pets.
- Each flagship pet has all nine Codex states: idle, directional movement,
  waving, jumping, failed, waiting, active work, and review.
- Each state animation is written as character-specific motion, not a reusable
  jump, wave, sad face, or typing loop.
- Each flagship pet also appears in `catalog/first-50-motion.json`.
- Existing seeded pet bundles still pass structural atlas validation.

## Asset Status

| Rank | Pet | Status | QA note |
| --- | --- | --- | --- |
| 1 | Zentri | Seeded | Original Zentrik folded-paper pet is installable; future art passes should preserve crease-led motion. |
| 2 | Terminal Ghost | Seeded | Installable community import; flagship brief sharpens no-leg prompt-snap movement. |
| 3 | Review Owl | Seeded | Installable community import; review state should be the signature head-and-eye moment. |
| 4 | Bug Hunter | Seeded | Installable community import; antennae must carry attention and failure. |
| 5 | Rubber Duck 2.0 | Seeded | Installable community import; motion language should stay squeaky, bobbing, and desk-bound. |
| 6 | Token Vampire | Seeded | Installable community import; cape and token accent should drive every state. |
| 7 | Merge Mammoth | Installable | Generated atlas passed frame inspection, atlas validation, and visual QA; trunk-led states are distinct. |
| 8 | CI Phoenix | Installable | Generated atlas passed QA; repaired waiting row preserved identity and attached-flame cleanup. |
| 9 | Patch Panda | Installable | Generated atlas passed QA; patch and satchel details remain attached across key states. |
| 10 | Product Crane | Installable | Generated atlas passed QA; repaired rows removed UI drift and kept attached paper-tab motion. |

## Top Ten Motion Verdicts

1. Zentri should feel like product intent folded into motion. The important
   detail is that the cyan accent behaves like a decision signal, while the
   body moves through crease tension rather than normal bird acting.
2. Terminal Ghost should never fake legs. Its timing comes from terminal cursor
   cadence, command execution, backspace snaps, and a prompt-like face.
3. Review Owl earns its place only if review is stronger than idle. Head
   rotation, eye narrowing, and page-turn wing restraint are the core.
4. Bug Hunter should read as detective work at pet size. Antennae lead the
   scuttle, and failure is a cold trail rather than generic sadness.
5. Rubber Duck 2.0 should be funny because it listens. The bounce is a rubber
   squeeze-pop, and the review pose is the duck making the user explain again.
6. Token Vampire works because Codex power users know context pressure. It
   should flutter, cloak, and guard its token accent, not run or sparkle.
7. Merge Mammoth is deliberately heavy. The trunk is the interaction tool, and
   its jump is almost a refusal to jump.
8. CI Phoenix is the fail-recover loop. The failed state dims to ash posture,
   and the active state should look like rebuild energy moving through feathers.
9. Patch Panda is soft but precise. Its job is pressing, smoothing, checking,
   and re-seating one attached patch.
10. Product Crane is the PM counterpart to Zentri. It should sort, score, and
    inspect with deliberate paper construction rather than bird naturalism.

## Next QA Gate

When a planned flagship pet gets artwork, it should not be accepted until:

- `python scripts/validate_pets.py` passes.
- `python scripts/validate_design_specs.py` passes.
- A contact sheet confirms identity is stable across all nine rows.
- Review and waiting are visually distinct from idle.
- Directional movement uses the pet's real mechanics.
- Effects remain attached to the sprite and do not create cleanup artifacts.
