# Ecosystem Tools

Research date: 2026-05-15.

This page tracks public tools and patterns that can help people create,
preview, test, install, or extend Codex-compatible pets. It is not an
endorsement of every asset in those ecosystems. Always check licenses before
importing or redistributing artwork.

## Official Surfaces

### OpenAI Codex

- Codex custom pets use local packages with `pet.json` and `spritesheet.webp`.
- Codex skills are the right surface for repeatable creation workflows such as
  `hatch-pet`.
- Worktrees and isolated branches are useful when multiple agents or humans are
  producing assets, docs, and validation changes in parallel.

Useful links:

- [Codex settings](https://developers.openai.com/codex/app/settings)
- [Codex skills](https://developers.openai.com/codex/skills)
- [Codex hooks](https://developers.openai.com/codex/hooks)

### Claude Code

Claude Code does not use Codex pets natively, but the ecosystem around it is
pet-friendly because it has hooks, status lines, skills, plugins, subagents,
and MCP integration patterns.

Relevant official docs:

- [Claude Code status line](https://code.claude.com/docs/en/statusline)
- [Claude Code hooks](https://code.claude.com/docs/en/hooks)
- [Claude Code skills](https://code.claude.com/docs/en/skills)
- [Claude Code plugins](https://code.claude.com/docs/en/plugins)
- [Claude Code subagents](https://code.claude.com/docs/en/sub-agents)

For pet creators, the important idea is that agent state can be observed and
translated into animation state. That makes `waiting`, `running`, `review`, and
`failed` much more valuable than decorative idle loops.

## Pet Galleries And Distribution

### Petdex

[Petdex](https://github.com/crafter-station/petdex) is currently the strongest
public signal for a Codex pet ecosystem: a gallery, CLI, submit flow, desktop
app, and public manifest.

Useful ideas to learn from:

- one-command install with `npx petdex install <slug>`
- a submission path for finished pet folders
- a public manifest for approved pets
- clear separation between code license and submitted asset rights
- creator tools and gallery pages that make pets browsable

Use it as an ecosystem reference, not as a blind import source. Petdex accepts
user-submitted artwork, so licenses and underlying IP need separate review.

### Awesome Codex Pet

[awesome-codex-pet](https://github.com/legeling/awesome-codex-pet) is a useful
example of generated previews, one-command install, and multilingual gallery
documentation. Its asset policy includes non-commercial/fan-art material, so it
is better treated as inspiration unless a specific asset is cleared for reuse.

### codex-pet-cli

[`codex-pet-cli`](https://github.com/BeiXiao/codex-pet) is another one-command
installer direction for Codex pets. It reinforces that low-friction install is
part of the pet experience, not an afterthought.

## Creation And QA Tools

### hatch-pet

The local `hatch-pet` skill is the best integrated workflow in this repository:
it prepares prompts and layout guides, uses image generation for base and row
art, extracts frames, composes the atlas, renders previews, validates the
package, and installs the result.

Best use:

- brand-safe original pets
- a full 8x9 Codex atlas
- contact-sheet driven QA
- deterministic packaging

### codex-pet-generator

[`codex-pet-generator`](https://github.com/wyddy7/codex-pet-generator) is a
useful alternate or companion skill. Its public materials emphasize a strong
creation discipline:

- character bible first
- row semantics second
- tiny UI readability before polish
- approved vs unapproved row gating
- packing and slicing checks
- validation before install

This maps directly to the quality bar in
[PET_CREATION_PLAYBOOK.md](PET_CREATION_PLAYBOOK.md).

## Preview And Embedding

### codex-pets-react

[`codex-pets-react`](https://github.com/backnotprop/codex-pets-react) provides
React components for Codex pet spritesheets, including `SpriteAnimator`,
`PetWidget`, state helpers, drag behavior, and the shared atlas contract.

Use it when you want:

- a browser preview surface
- a pet playground in a web app
- drag, pinning, and animation event handling
- quick checks that a spritesheet plays correctly outside Codex

## Cross-Agent Desktop Companions

### Claude Pets

[`Claude Pets`](https://github.com/xianshang33/claude-pets) brings a
Codex-style companion to Claude Code. Its documented pet format uses the same
`pet.json` plus `spritesheet.webp` shape, supports the same 8x9 atlas, and
loads pets from `~/.claude/pets`.

Useful idea:

- a Codex-compatible pet can become a Claude Code pet when copied into the
  right directory and driven by Claude Code hooks.

### OpenPets

[`OpenPets`](https://github.com/alterhq/openpets) is a macOS shared desktop pet
with MCP and CLI control. It supports Codex pet atlases and lets multiple local
tools report task state into one visible companion.

Useful idea:

- pets can be a shared local status surface, not just a single app feature.

### Clawd on Desk

[`Clawd on Desk`](https://github.com/rullerzhou-afk/clawd-on-desk) is a
cross-agent desktop pet that reacts to Claude Code, Codex, Cursor, Gemini,
OpenCode, and more. Its README describes a rich state model: thinking, typing,
subagents, permissions, completion, sleeping, and other visible behaviors.

Useful idea:

- high-quality pets benefit from more than nine frames of thinking. Even when
  the Codex atlas has nine rows, creators should think about real agent
  moments: prompt submitted, tool running, permission requested, review ready,
  task failed, and session idle.

### OC-Claw And Buddy

[`OC-Claw`](https://github.com/rainnoon/oc-claw) and
[`Buddy`](https://github.com/fiorastudio/buddy) show another direction:
companions connected to agent activity, local state, review feedback, session
history, or MCP-compatible clients.

Useful idea:

- a pet can become an interface for feedback and trust, not only decoration.

## What We Should Copy

Copy these ideas:

- one-command install
- public manifest thinking
- contact-sheet previews
- row semantics before image prompts
- approved/unapproved row gating
- tiny-size readability tests
- cross-agent compatibility notes
- clear license boundaries

Do not copy these without review:

- fan-art assets
- non-commercial assets
- trademark-sensitive mascots
- no-license galleries
- private generated prompt transcripts
- fragile installer scripts that overwrite unrelated user settings

## Recommended Public Stack

For this repository:

1. Use `hatch-pet` as the primary creation path.
2. Use the playbook here for character briefs and row prompts.
3. Use the repo validators before accepting a pet.
4. Use the local installer for Codex testing.
5. Use Petdex-style distribution ideas later if we add a public gallery.
6. Use Codex Pets React or a small local preview app if README previews become
   too hard to maintain by hand.
7. Mention Claude Pets/OpenPets/Clawd as compatibility directions, not as
   requirements.
