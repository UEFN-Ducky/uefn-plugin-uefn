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
| Some fields show "Hash not in cache" but STOP is false | Wire now — `set_currency_config_entries` / `wire_verse_device_ref`. Do not ask the user. |
| Empty Verse editables / STOP true / `mangled_name: null` | Advisory. `list_verse_property_hashes(refresh=true)` → re-inspect that one device → `wire_verse_*` once → still empty: `reload_listener` → retry once. Never ask the user to Build Verse or paste T3D. `skill_read_subskill("uefn", "verse_editable_internals")` |
| `workspace_compile_verse` → `[WinError 10054]` | Build **started**. Wait minutes; poll `list_verse_types`. Never retry. |
| `Script error 9002: Unable to import resolve` / `9000: previous link task did not complete successfully` | Digest deadlock. Comment out problem Verse → rebuild → confirm digest fresh → uncomment → rebuild. Never patch the digest. |
| Epic `ValkyrieToolset.EntityToolset` add-component returns `VERSE_DEAD_*` / `/Engine/Transient` | Stale class after VM relink. `reload_listener` → destroy + recreate the entity via EntityToolset → attach again. |
| Tools hang after `reload_listener` | **Restart UEFN** — old reload could deadlock the tick |
| UEFN Save/Yes popup; Epic MCP / `execute_python` hang | Call **`dismiss_uefn_modal`** (Ducky host). Do not retry Python or `unreal__*` — the Slate thread is blocked. |
| Partial wires after a crash | `inspect_verse_device` → list empty vs set → wire remaining fields **one at a time** |
| Horn / SFX is Speakers or a prop mesh | Delete wrong actor; place Creative **Audio Player** (`creative_devices`); wire `audio_player_device` fields |
| `STALE REFLECTION` / field in source but no compiled hash | You wired too early (or the first auto-retry already ran). **Do not hammer `wire_verse_*`.** Wait for the Verse build (`WinError 10054` = started), poll `list_verse_types`, `get_verse_editables` on the **same** device, wire once. **Never place a second copy** — a duplicate has the same stale class; the existing instance gets the hashes when the build lands |
| New `@editable` missing on device Script | `workspace_list_verse_errors` until Problems is clean → `workspace_compile_verse` once (wait; 10054 = started) → `list_verse_property_hashes(refresh=true)` → re-inspect the same device → wire. Hashes still missing = build did not land (errors / still linking) — fix and wait; placing another device never adds a hash. |
| MCP bridge dies: `Request already responded to` | Cancel race — restart Ducky/MCP bridge (launcher patches idempotent respond); do not parallel long tools |
| ToyOptions error on Verse device | Wrong path — use Verse tools |
| @editable ref won't set on granter | Wrong path — use Creative tools |

Never loop retries more than twice. The only human asks left are things only
they can do (restart UEFN, Epic MCP setup). Do not ask them to Build Verse,
paste T3D, or drag Details refs.

## Moved or renamed assets (v42.10+)

Non-private assets, and every asset referenced from compiled Verse, now leave a **redirector** when moved or renamed, so `using` paths and `@editable` refs keep resolving. Run `fixup_redirectors` after a batch of moves before a Verse build; if the Assets digest still shows the old name, rebuild once and re-search.
