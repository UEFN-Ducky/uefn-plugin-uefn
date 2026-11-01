---
description: "Symptom→fix table for listener/wiring failures — STOP stays true, hash-not-in-cache, hung tools, wrong tool family; 43.00 editor changes (Python per project in Editor Preferences, InvalidIslandVersionOnServer, stuck launch with an idle client, ValkyrieMap=, Data Recovery save block, Lore)"
metadata:
  order: 7
  label: "Troubleshooting"
  default_enabled: false
  load_condition: "A listener/wiring call failed, STOP stays true, or tools hang; the Ducky listener / init_unreal.py does not start after 43.00; players can't join with InvalidIslandVersionOnServer; launch stuck waiting for a client; save blocked by Data Recovery"
---

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
| Launch fails at Downloading, "Waiting for client to be ready", **"Failed to connect to beacon"** (BeaconNetDriver ConnectionTimeout 30.00) while other islands launch | Not the network: generated Verse data too big for the server to load in 30 s. Measure `.verse` sizes, shrink to flat `[]int` ≤ ~250 KB, compile, close stale FortniteClient, relaunch. `skill_read_subskill("uefn", "launch_beacon_failure")` |
| Validator **"Vertex count of LOD0 of this Static Mesh's render data is too high (30,000)"** on a Nanite mesh | The Nanite fallback is counted. `EditorToolset.ObjectToolset.SetProperties` NaniteSettings `fallbackTarget: PercentTriangles`, 0.4–0.7 → ≤ 27k. `skill_read_subskill("uefn", "nanite_fallback_vertex_count")` |
| ToyOptions error on Verse device | Wrong path — use Verse tools |
| @editable ref won't set on granter | Wrong path — use Creative tools |

Never loop retries more than twice. The only human asks left are things only
they can do (Epic MCP setup when `epic_mcp_online` is false). Do not ask them
to Build Verse, paste T3D, drag Details refs, or restart UEFN. `reload_listener`
**once** if the listener is stale; if still stuck stay on `workspace_*`.
**Never restart UEFN.**

## Moved or renamed assets (v42.10+)

Non-private assets, and every asset referenced from compiled Verse, now leave a **redirector** when moved or renamed, so `using` paths and `@editable` refs keep resolving. Run `fixup_redirectors` after a batch of moves before a Verse build; if the Assets digest still shows the old name, rebuild once and re-search.

## 43.00 editor changes

Everything 43.00 changed, with its skill page: `skill_read_subskill("uefn", "patch_43_00")`.
Slow island, hitches, memory over budget → `profiling` / `profiling_mcp` / `profiling_fixes`.

| Symptom / change | What to do |
| --- | --- |
| Ducky listener / `Content/Python/init_unreal.py` never runs on this island | 43.00 moved Python to **Editor Preferences** and enables it **per project**. Turn on Python scripting for this project there (Epic MCP: `ValkyrieToolset.ValkyriePythonToolset.EnablePythonForMainProject`, async; check `IsPythonReadyForMainProject`). Never delete `init_unreal.py`. |
| Players permanently can't join: `InvalidIslandVersionOnServer` after the version history changed | Fixed in 43.00 — republish / relaunch on 43.00; no project change needed. |
| Launch session stuck because an idle client never joined | Fixed in 43.00. Still stuck → `launch_beacon_failure`. |
| Need a different startup map | Command line `ValkyrieMap=<map>` overrides the startup map. |
| Save refused after renaming / deleting a Verse class | Data Recovery placeholders block saving until fixed — `verse_build_lifecycle`. |
| Asset rename breaks Verse | Enable Reflect UE Redirectors into Verse Manifest — `verse_build_lifecycle`. |
| Undo still showed "push needed"; entity placement errored in live edit; crash muting voice chat | Fixed in 43.00. Live edit now covers entity prefab assets, snap tools and brush volumes (Blocking / Post Process); Water Body Exclusion Volumes still need Push Changes. |
| Migrated assets missing until restart | Fixed in 43.00 — do not restart UEFN for it. |
| Logs tool | Epic `ConsoleToolset.LogsToolset.GetLogEntries` (renamed from `EditorToolset.LogsToolset`). |

**Lore (43.00):** diff `.uefnproject`, `.verse` and `.uplugin` files in VS Code; the
24-hour check-in reminder is gone (work is backed up automatically); the VS Code
extension is `Lore.vsix` (was `URC.vsix`); Branch Explorer merge/archive display fixes.
Never write or delete `.lore` files.

## 42.40 editor changes

- **Browse To Asset** / **Ctrl+B** on a static mesh selects the mesh's own folder again
  (it opened the Bumpy Bay Prop Gallery).
- **Canceling a publish** works; closing a project no longer logs garbage-collection errors.
- **Entity Prefab Editor** viewports: hidden toolbar tools are in the toolbar menu,
  layout names show, Maximize checkbox follows the viewport.
- **Interchange glTF** skinned meshes: inverse bind matrices resolve, multi-root files import.
- **Lore**: validation fix-up resaves only the affected packages (not every actor); a
  branch archived by someone else no longer shows as active after a revert or a new
  personal branch.
- **VerseVM** session toggle (Verse Reload off while on) — `verse_build_lifecycle`.

## 42.30 editor changes

- **Verse paths** are shown (new projects) in the Content Browser, source control
  dialogs, validation errors, Reference Viewer, asset tooltips and copied asset
  references; Fab and content-pack assets too. Existing projects are unchanged.
  Context menus add **Copy File Path / Copy Package Path / Copy Verse Path**.
  In Verse, keep using the Assets-digest names (`list_verse_types(digest="assets")`).
- **Launch Session** now logs *why* assets need resaving — read it with
  `get_editor_log` / `ConsoleToolset.LogsToolset.GetLogEntries` (43.00 name).
- **Restart session** is faster; **canceling a publish** now works.
- **Content Pre-Checks** flag possible moderation problems during cook — `content_prechecks`.
- Crashes fixed: undoing a deleted Gameplay Effect Component, creating spline meshes,
  copying actors from pre-5.1 editors, landscape brush in a deleted region.
