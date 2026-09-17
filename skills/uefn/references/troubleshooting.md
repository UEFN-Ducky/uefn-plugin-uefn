---
description: "Symptom→fix table for listener/wiring failures — STOP stays true, hash-not-in-cache, hung tools, wrong tool family"
metadata:
  order: 7
  label: "Troubleshooting"
  default_enabled: false
  load_condition: "A listener/wiring call failed, STOP stays true, or tools hang"
---

**Tool order (HARD):** 1) Official UEFN MCP first (`ducky_get_status` → `epic_mcp_online` → nested `unreal__*`). 2) Ducky listener second. 3) `execute_python` LAST — never a placement path, even if Epic and listener failed. Map: `skill_read_subskill("uefn", "epic_mcp")`.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Device "not found" after a Fort class filter | `get_all_actors(label_filter="<part of its label>", limit=500)` or `list_verse_devices()` |
| Empty Verse editables / STOP true / `readable: false` | Confirm `@editable` in the `.verse`. `workspace_compile_verse` once, wait, `get_verse_editables` on **this same device**, wire once. Still not readable: `reload_listener` once, then stop. Never ask the user to Build Verse or paste T3D. `skill_read_subskill("uefn", "verse_editable_internals")` |
| `workspace_compile_verse` → `[WinError 10054]` | Build **started**. Wait minutes; poll `list_verse_types`. Never retry. |
| `Script error 9002: Unable to import resolve` / `9000: previous link task did not complete successfully` | Digest deadlock. Comment out problem Verse → rebuild → confirm digest fresh → uncomment → rebuild. Never patch the digest. |
| Epic `ValkyrieToolset.EntityToolset` add-component returns `VERSE_DEAD_*` / `/Engine/Transient` | Stale class after VM relink. `reload_listener` → destroy + recreate the entity via EntityToolset → attach again. |
| Tools hang after `reload_listener` | Stay on `workspace_*` / `ducky_get_status`. Do not hammer. **Never restart UEFN.** |
| UEFN Save/Yes popup; Epic MCP / `execute_python` hang | Call **`dismiss_uefn_modal`** (Ducky host). Do not retry Python or `unreal__*` — the Slate thread is blocked. |
| Partial wires after a crash | `inspect_verse_device` → list empty vs set → wire remaining fields **one at a time** |
| Horn / SFX is Speakers or a prop mesh | Delete wrong actor; place Creative **Audio Player** (`creative_devices`); wire `audio_player_device` fields |
| `STALE REFLECTION` / field in source but not readable | The compiled class lacks the field: (a) build not landed, (b) not `@editable`, (c) stale Python wrapper. **Do not hammer `wire_verse_*`.** Compile once, wait (`WinError 10054` = started), poll `list_verse_types`, `get_verse_editables` on the **same** device, wire once. **Never place a second copy. Never remove or retype the `@editable`.** |
| New `@editable` missing on device Script | `workspace_list_verse_errors` until Problems is clean → `workspace_compile_verse` once (wait; 10054 = started) → re-inspect the same device → wire. Still not readable = build did not land (errors / still linking) — fix and wait; placing another device never adds a hash. |
| MCP bridge dies: `Request already responded to` | Cancel race — restart Ducky/MCP bridge (launcher patches idempotent respond); do not parallel long tools |
| ToyOptions error on Verse device | Wrong path — use Verse tools |
| @editable ref won't set on granter | Wrong path — use Creative tools |

Never loop retries more than twice. The only human asks left are things only
they can do (Epic MCP setup when `epic_mcp_online` is false). Do not ask them
to Build Verse, paste T3D, drag Details refs, or restart UEFN. `reload_listener`
**once** if the listener is stale; if still stuck stay on `workspace_*`.
**Never restart UEFN.**

## Moved or renamed assets (v42.10+)

Non-private assets, and every asset referenced from compiled Verse, now leave a **redirector** when moved or renamed, so `using` paths and `@editable` refs keep resolving. Run `fixup_redirectors` after a batch of moves before a Verse build; if the Assets digest still shows the old name, rebuild once and re-search.
