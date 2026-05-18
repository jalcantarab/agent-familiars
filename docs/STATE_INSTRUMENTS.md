# State Instruments

State instruments are familiar-adjacent pets for people who want Codex to feel
alive without adding a full character to the screen.

They sit between `Signal Surface` and the more creature-like familiars: useful
objects with a little ritual, clear color semantics, and motion that explains
what is happening without asking the user to decode a generic hop.

## Install

```bash
python3 scripts/install_pet.py --pack state-instruments
```

Or without cloning:

```bash
curl -fsSL https://raw.githubusercontent.com/jalcantarab/agent-familiars/main/scripts/install_pet.py | python3 - --pack state-instruments
```

Then refresh custom pets in Codex and select the one that fits your screen.
For a broader recommendation path, see
[Choosing A Familiar](CHOOSING_A_FAMILIAR.md).

## The Set

| Familiar | State Read |
| --- | --- |
| [Signal Surface](../pets/signal-surface) | clean surface, color, scan direction |
| [Intent Compass](../pets/intent-compass) | direction, indecision, review bearing |
| [Thread Totem](../pets/thread-totem) | paused, flowing, aligned, or tangled beads |
| [Pocket Oracle](../pets/pocket-oracle) | aperture opens, clouds, scans, and waits |
| [Loop Loom](../pets/loop-loom) | shuttle movement, edge pauses, woven review |
| [Tide Stone](../pets/tide-stone) | calm tide, amber pool, clear lens, red fault |

## Shared State Grammar

- `idle`: low-distraction cyan breathing.
- `running-right` / `running-left`: visible directional bias.
- `waving`: a small in-object signal, not loose marks around the pet.
- `jumping`: a contained lift or internal brightening.
- `failed`: red/coral failure shown through fracture, tangle, split, or jam.
- `waiting`: amber pause that clearly asks for input.
- `running`: cyan/green active movement inside the object.
- `review`: blue-white clarity, alignment, scan, or settled evaluation.

The point is not to turn every pet into a dashboard. The point is to make a
small companion whose behavior is obvious while the user is busy.
