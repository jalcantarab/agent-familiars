# Familiars Lab

Familiars Lab is a local browser playground for the packaged pet catalog. It
lets you assemble up to six familiars, play every real Codex pet state, try
curated packs and sequence themes, and export the result as a validated
Familiars recipe.

## Start The Lab

From an installed package or editable clone:

```bash
familiars lab
```

The command serves the lab on `http://127.0.0.1:8765/` and opens it in the
default browser. Stop it with `Ctrl-C`.

Use another port or keep the browser closed:

```bash
familiars lab --port 8877 --no-open
```

The server binds to localhost by default, has no telemetry, and does not load
scripts, fonts, or pet assets from third-party services.

## Play With A Scene

- Pick familiars from the library or use `Surprise me` to draw from the current
  pack.
- Change the full council with the nine-state strip.
- Select one familiar to give it a different state.
- Click a familiar on stage for a small wave.
- Use `Run ritual` for a short hello, jump, work, and review choreography.
- Change the stage theme without changing the underlying pets.

The lab uses the committed `1536x1872` atlases directly. Nothing is converted
or re-encoded for browser playback.

## Export A Recipe

`Export recipe` sends the small JSON recipe back to the local server for
validation with the same schema and Pillow renderer used by the CLI. A download
only starts after the renderer can produce a preview frame.

Render the exported file:

```bash
familiars render --recipe familiars-lab-council.json
```

The recipe remains normal Familiars data, so it can also be edited by hand,
used through the MCP server, or committed as a curated example later.

## Safety Boundaries

- The lab accepts recipe requests up to 64 KiB.
- Scenes use the renderer's six-pet limit.
- Pet image routes only serve ids from the packaged catalog.
- The browser surface has a same-origin content security policy.
- Cross-origin browser POST requests are rejected.
- Recipe validation renders in memory and does not write sequence output.

The lab is intentionally a director for existing Familiars, not a second pet
format or a background service.
