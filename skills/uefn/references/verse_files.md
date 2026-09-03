---
description: "Edit Verse source on disk — workspace tool table, offline golden path, a worked device-class example"
metadata:
  order: 0
  label: "Verse files (offline)"
  default_enabled: false
  load_condition: "Creating or editing .verse files, or unsure what works while the listener/UEFN is offline"
---

## Verse source edits — do this first, listener not required

When the user asks to change **behavior** (trigger on enter, grant item, spawn NPC, subscribe to events, game logic), that lives in **`Verse/**/*.verse` on disk**. Edit it **immediately** with workspace tools. Do **not** ask for Outliner labels, do **not** wait for the UEFN listener, do **not** say you need UEFN open first.

| Task | Tools | Needs listener? | Needs UEFN app? |
|------|-------|-----------------|-----------------|
| Find / read / write `.verse` | `workspace_list_dir` → `workspace_read_file` → `workspace_write_file` | **No** | **No** |
| Problems panel / syntax scan | `workspace_list_verse_errors()` (verse-lsp; updates editor Problems). Call with **no args** — incremental, re-checks only changed files. **Never `full=true`** to re-confirm (rescans all files, ~1 min); use `rescan=false` to just re-read. | **No** | **No** |
| Full compile in editor | `workspace_compile_verse` | **No** (uses Verse Workflow Server) | **Yes** (UEFN running) |
| Wire `@editable` device refs in level | `workspace_compile_verse` succeeded → `list_verse_devices` → `inspect_verse_device` → `wire_verse_device_ref` (one per field) | **Yes** | **Yes** |
| Place new device actor in level | `spawn_actor(..., label=..., folder=...)` once per device | **Yes** | **Yes** |

**Decision rule:** code/logic change → **edit files now**. Level placement or Details-panel wiring → listener tools when online.

### HARD RULE — never dump at Verse root

New `.verse` files go in a **system folder**, not `Verse/<file>.verse`.

1. `workspace_list_dir("Verse")` — reuse `Economy/`, `Shop/`, `PlayerCore/`, … if present.
2. Prefer `verse_template_apply(id)` (UEFN Verse plugin) — creates the pack folder.
3. Hand-write: `workspace_write_file("Verse/<System>/<Name>.verse", …)` — parents are created automatically.
4. Only `module_declarations.verse` (+ tiny shared helpers) stay at Verse root.
5. Details: `skill_read_subskill("verse", "modules")`.

## Golden path (offline OK)

```
workspace_list_dir("Verse")
# pick / create a system folder — never write at Verse root
workspace_write_file("Verse/Granting/trigger_granter_device.verse", content="...")
workspace_list_verse_errors()
```

Editing an existing file:

```
workspace_list_dir("Verse")
workspace_read_file("Verse/Granting/trigger_granter_device.verse")
# ... edit full file ...
workspace_write_file("Verse/Granting/trigger_granter_device.verse", content="...")
workspace_list_verse_errors()
```

Use `workspace_open_verse_file` only when the user explicitly wants the editor focused — routine `workspace_write_file` does **not** open a tab.

## Example: trigger → grant + spawn NPC (Verse class)

Custom `creative_device` subclasses wire devices in **source** via `@editable` fields and `Subscribe` — no listener needed to write this (path example: `Verse/<System>/trigger_granter_device.verse`, e.g. `Verse/Granting/`):

```verse
using { /Fortnite.com/Devices }
using { /Verse.org/Simulation }

trigger_granter_device := class(creative_device):
    @editable Trigger: trigger_device = trigger_device{}
    @editable Granter: item_granter_device = item_granter_device{}
    @editable NPCSpawner: npc_spawner_device = npc_spawner_device{}

    OnBegin<override>()<suspends>:void =
        Trigger.TriggeredEvent.Subscribe(OnTriggered)

    OnTriggered(Agent : ?agent):void =
        if (A := Agent?):
            Granter.GrantItem(A)
            NPCSpawner.Spawn()
```

After saving the file: `workspace_list_verse_errors` → `workspace_compile_verse` (must succeed; the offline LSP does **not** catch effect/module/ambiguity errors — only the real build does) → when UEFN is open, wire the three fields yourself with `wire_verse_device_ref` (one per turn). Never ask the user to drag Details refs. The **logic** is already done in source.

## Anti-patterns

| Wrong | Right |
|-------|-------|
| `workspace_write_file("Verse/MyDevice.verse", …)` at root | `Verse/<System>/my_device.verse` or `verse_template_apply` |
| "Deploy the listener first so I can wire the trigger" | `workspace_read_file` the Verse class now |
| Ask for Outliner labels before reading `Verse/` | `workspace_list_dir("Verse")` and search filenames |
| `execute_python` for file text | `workspace_write_file` only |
| `workspace_list_verse_errors(full=true)` over and over | Plain call (incremental) or `rescan=false`; the result already lists every broken file |
| Re-scan to "make sure" after you already have the error list | Go fix the file it named — the list is complete |
| Block the turn with clarifying questions | Pick the obvious `.verse` path, edit, one-line assumptions |
