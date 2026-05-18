# Brand-Safe Reference Lines

This project can make pets that feel familiar to modern engineering and product
teams without borrowing company brands. The useful reference is the work rhythm:
deploy previews, issue triage, design systems, checkout flows, observability,
AI evals, and incident response.

The public rule is simple:

```text
Reference workflows, not marks.
```

## Brand-Safety Rules

- Use original pet names, silhouettes, palettes, and motion language.
- Do not use company names, product names, logos, wordmarks, slogans, UI
  screenshots, official mascot shapes, icon geometry, or exact brand palettes
  unless the asset is licensed or co-created.
- Avoid one-to-one public mappings from a pet to a company. Public copy should
  describe the workflow category.
- Avoid animals or objects that are already strongly tied to a famous tool in
  that category. Use a lateral metaphor instead.
- Keep humor affectionate and work-native. Do not parody a company's failure
  mode or make the pet look like a degraded version of a protected mascot.
- If a generated row starts to resemble a known logo, mascot, product UI, or
  trade dress, reject that row and repair the visual lock before packaging.

## Risk Model

| Level | Use | Example Direction |
| --- | --- | --- |
| Green | Workflow semantics, generic shapes, original character behavior. | A deploy pet that rides an abstract edge line. |
| Yellow | Category cues that might drift toward a familiar product mark. | A design pet with vector handles or a chat pet with color bands. |
| Red | Protected assets or likely confusion. | Logos, mascot lookalikes, product names in pet IDs, exact UI, exact color systems. |

Yellow ideas are still usable, but only after the forbidden details are written
into the generation prompt and checked in visual QA.

## Selected Mix

The first brand-safe reference set should cover the tools and rituals that
software teams already spend time in every day:

| Priority | Public Line | Audience Read | Safety Constraint | Signature Motion |
| --- | --- | --- | --- | --- |
| 1 | Edge Finch | Preview deploys, edge runtimes, design-engineering loops. | No triangle marks, deployment platform names, or black-white logo lockups. | Glides along an invisible edge, then folds one wing into a preview flap. |
| 2 | Issue Lynx | Fast issue triage, planning, and backlog grooming. | No issue-tool logos, exact app colors, or UI cards. | Stalks a priority trail, pauses, then pounces on a single decision point. |
| 3 | Vector Finch | Design systems, prototyping, and visual QA. | No multicolor app-logo layout, product UI, or component-library marks. | Wing tips behave like bezier handles attached to the body. |
| 4 | Block Badger | Docs, specs, internal knowledge bases, and block editing. | No cube marks, wordmarks, or app-specific black-and-white icon language. | Reorders its own fur panels like content blocks. |
| 5 | Branch Beagle | Repos, PRs, code review, and branch hygiene. | No cat/octopus hybrid, tanuki, bucket icons, or host-specific marks. | Sniffs a branching trail and settles on the review path. |
| 6 | Worker Wisp | Serverless functions and edge workers. | No cloud marks, lambda glyphs, orange-cloud palettes, or product names. | Flickers between body-contained nodes, never leaving detached effects. |
| 7 | Action Axolotl | CI steps, automation, and job orchestration. | No check-run logos, circular CI marks, or pipeline UI. | Frills tick through steps like a living job runner. |
| 8 | Checkout Gecko | Checkout, payments, commerce, and reconciliation. | No card-network marks, shopping bags, payment logos, or stripe patterns. | Smooth body slide from cart-like anticipation to settled confirmation. |
| 9 | Trace Manta | Observability, traces, spans, and performance reviews. | No dog mascots, honeycomb grids, or vendor color systems. | Fin ripples form attached span waves across the body. |
| 10 | Model Moth | AI model work, prompt iteration, and eval culture. | No AI-lab logos, blossoms, dots, spirals, or branded model names. | Wings fold through evaluation bands and return to a quiet baseline. |
| 11 | Channel Chameleon | Team chat, threads, async collaboration, and workflow automation. | No hash-logo shapes, exact four-color mark palettes, or chat UI. | Tail curls into a thread and body bands shift in muted channel cadence. |
| 12 | Roadmap Raven | Product strategy, prioritization, and launch planning. | No PM-tool marks, roadmap UI, or product-board screenshots. | Wing feathers reorder into a visible priority sequence. |

These twelve should be the first production candidates because they are obvious
to the people who live in the workflows, but they do not need protected marks to
be recognizable.

## Production Prompt Add-On

Use this block when generating any brand-safe reference pet:

```text
Brand-safe constraints:
This must be an original workflow metaphor, not a company mascot, logo, product
UI, app icon, wordmark, screenshot, or parody. Do not use exact brand colors,
protected mascot silhouettes, recognizable icon geometry, slogans, company
names, product names, UI cards, screenshots, or detached symbols. The pet should
feel familiar because of its work behavior and motion, not because it copies a
brand asset.
```

## QA Add-On

Before packaging a brand-safe reference pet, answer these checks:

1. Would the pet still read if every company and product name were removed?
2. Is the silhouette original at tiny desktop size?
3. Are the colors generic enough to avoid looking like a house palette?
4. Are all workflow cues embodied in the pet rather than floating as logos,
   icons, UI cards, text labels, or badges?
5. Would an employee or fan of the adjacent tool category see it as a respectful
   work joke, not as an unofficial brand asset?

If any answer is weak, repair the prompt or row before adding the pet to the
catalog.
