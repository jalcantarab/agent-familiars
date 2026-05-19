# Choosing A Familiar

Start with the familiar you would not mind seeing for a whole work session.
The right choice is usually about screen mood first, then job fit.

## Quick Picks

| If you want... | Start with | Why |
| --- | --- | --- |
| a calm status object | [Signal Surface](../pets/signal-surface) | It communicates state through color and scan motion without feeling like a character. |
| a little direction and decision energy | [Intent Compass](../pets/intent-compass) | The needle makes working, waiting, review, and failure easy to read. |
| the quietest companion | [Tide Stone](../pets/tide-stone) | It stays soft and ambient while still changing clearly by state. |
| product humor | [No Knight](../pets/no-knight) | The shield makes scope control visible and funny. |
| product discovery calm | [Signal Heron](../pets/signal-heron) | It is still, patient, and built around signal instead of noise. |
| developer workflow charm | [Merge Mammoth](../pets/merge-mammoth) | It is a friendly default for long coding sessions and conflict-heavy work. |
| failure recovery energy | [CI Phoenix](../pets/ci-phoenix) | It makes failure feel recoverable, which is exactly the point of CI. |
| the project signature | [Zentri](../pets/zentri) | It is the folded-paper reference familiar and the cleanest brand example. |

## Choose By Screen Mood

### Quiet And Useful

Pick these when you want the pet to behave more like a tiny instrument than a
mascot.

- [Signal Surface](../pets/signal-surface): most neutral, most status-like.
- [Tide Stone](../pets/tide-stone): softest and least analytic.
- [Thread Totem](../pets/thread-totem): small ritual object with obvious pause,
  flow, alignment, and tangle states.

Install the full set:

```bash
python3 scripts/install_pet.py --pack state-instruments
```

### Product Folklore

Pick these when you want the familiar to have a point of view about product
work.

- [No Knight](../pets/no-knight): roadmap boundaries and PM comedy.
- [Signal Heron](../pets/signal-heron): customer signal, research, and waiting
  well.
- [Launch Lantern](../pets/launch-lantern): launch readiness without panic.
- [Tradeoff Scale](../pets/tradeoff-scale): visible product weight and judgment.
- [RICE Centurion](../pets/rice-centurion): prioritization scoring with a
  slightly over-serious tablet ritual.
- [Queue Quixote](../pets/queue-quixote): backlog courage with a built-in
  reality check.

Install the pack:

```bash
python3 scripts/install_pet.py --pack product-tropes
```

### Developer Workflow

Pick these when the pet should feel tied to engineering work.

- [Merge Mammoth](../pets/merge-mammoth): merge conflict patience.
- [CI Phoenix](../pets/ci-phoenix): failed checks, rebuilds, and recovery.
- [Trace Manta](../pets/trace-manta): observability and live motion.
- [Design Finch](../pets/design-finch): UI polish and precise review.

Install the starter pack:

```bash
python3 scripts/install_pet.py --pack starter
```

## Choose By Personality

- Minimal: Signal Surface.
- Meditative: Tide Stone or Signal Heron.
- Opinionated: No Knight.
- Craft-focused: Design Finch or Loop Loom.
- Resilient: CI Phoenix.
- Gentle and useful: Merge Mammoth.
- Signature: Zentri.

## A Practical Rule

If you are unsure, install `state-instruments` first. They are the least likely
to distract a user who simply wants Codex state changes to be easier to notice.
Then add one character familiar for taste.

To preview a choice before installing it, render a small local sequence:

```bash
python scripts/render_sequence.py --pet signal-surface --preset readme
python scripts/render_sequence.py --pack product-tropes --preset comparison --outputs poster
```
