---
description: "How Verse @editable fields are stored and wired — mangled names, Script object, wrapper outering, SavedActor, recovery when inspect looks empty"
metadata:
  order: 4
  label: "Verse @editable internals"
  default_enabled: false
  load_condition: "Wiring or inspecting a VerseDevice_C @editable, get_verse_editables STOP, readable false, or a device-ref array (npc_spawner_device, button_device, …)"
---

**Tool order (HARD):** 1) Official UEFN MCP first (`ducky_get_status` → `epic_mcp_online` → nested `unreal__*`). 2) Ducky listener second. 3) `execute_python` LAST — never a placement path, even if Epic and listener failed. Map: `skill_read_subskill("uefn", "epic_mcp")`.

## Verse `@editable` internals

You always edit these yourself. Never ask the user to Build Verse, paste a T3D
export, or drag refs in Details.

### Storage names

UEFN stores each `@editable` on the device **Script** object as:

```
__verse_0x<8 hex>_<FieldName>
```

The 8 hex digits are UE `FCrc::StrCrc32` of the field name (each char widened
to 4 little-endian bytes), printed byte-swapped. **The hash depends only on the
field name** — `PlayerManager` is `__verse_0x8E1BF1DC_PlayerManager` in every
project. Example: `CatSpawners` → `__verse_0xDE71A4D4_CatSpawners`.

Probing the plain Verse name (`CatSpawners`, `catSpawners`) correctly returns
"not found". That is **not** evidence the field is missing.

`wire_verse_*` computes that name and probes the live Script. `get_verse_editables`
always returns `mangled_name` (computed) plus `readable`. `STOP` is advisory.

### Script object

On a `VerseDevice_C` actor:

```
script = actor.get_editor_property("Script")
```

Class name looks like `Verse-<Module>-<class>_0` (e.g.
`Verse-NPCCore-catdog_spawn_controller_0`). Wrappers and mangled properties live
**here**, not on the actor.

### Device-ref wrappers

Creative-device refs (`npc_spawner_device`, `button_device`, `player_spawner_device`,
`creative_prop`, …) are wrapper UObjects:

```
wrapper = unreal.new_object(wrapper_cls, script)   # outer = Script, NOT the actor
wrapper.set_editor_property("SavedActor", target_actor)
script.set_editor_property(mangled_name, wrapper)  # or the array of wrappers
```

| Rule | Wrong | Right |
|------|-------|-------|
| Outer | actor | Script object |
| Link | guess | `SavedActor` (see `list_verse_reference_types`) |
| Save mark | wrapper subobject | Script + mangled field name |

Outering the wrapper to the actor silently fails. Marking wrapper subobjects for
save triggers `AddToSaveContext failed to find object`. The `wire_verse_*` tools
do this correctly — prefer them over hand-rolled `execute_python`.

Verse-to-Verse refs (`?player_manager`) skip wrappers: assign the target's
**Script** object via `set_verse_editable`.

### Value fields

`int` / `float` / `string` / `logic` / `[]int` / `[]float` use the same mangled
rule and the same tools as device refs. There is no extra "scalar slot"
treatment — arrays are not harder to wire than scalars.

| Job | Call |
|-----|------|
| String | `set_verse_editable(device, "BaseName", value="North")` |
| Int | `set_verse_editable(device, "HouseCost", value=750)` |
| Array | `set_verse_editable(device, "WallCosts", value=[150, 400])` |

### When `readable` is false

The computed name is not readable on this Script. Three real causes:

- (a) Verse build for this edit has not landed — `workspace_compile_verse` once, wait (10054 = started), re-inspect the **SAME** device
- (b) the field is not `@editable` in source (`var <private>`, packed at runtime, etc.)
- (c) the Python wrapper is stale — `reload_listener` **once**

Ladder: `get_verse_editables(same device)` → readable? wire once → not readable? confirm `@editable` in `.verse`, compile once, wait, re-inspect same device → still not readable after the wait: `reload_listener` once → stop and report.

Never a second device. Never a Verse refactor. Never restart UEFN. One-object
`execute_python` that reads/writes `script.get_editor_property(mangled)` is
allowed. Do **not** `os.walk` / `rglob` / scan `.uasset` for `__verse_0x`.

**STALE REFLECTION** is the same three causes. The host auto-retries `wire_*`
**once**. A second identical STALE: check compile output, re-inspect the
**same** device. Never loop `wire_verse_device_array`. `get_verse_editables`
verifies; it is not a prerequisite once `readable` is true.

| Job | Fix |
|-----|-----|
| Field never resolves | compile / wait / re-inspect **this** device. **Not** editing the class. |

### First array item vs rewrite (HARD)

One Verse class = one placed device unless the design needs more. A new
`@editable []` does **not** mean spawn another device.

| Job | Call on the **existing** label |
|-----|--------------------------------|
| First item (list empty) | `wire_verse_device_array(device, field, target_paths=[first])` |
| Rewrite the list | `wire_verse_device_array(device, field, target_paths=[…full list…], replace=true)` |
| Clear the list | `wire_verse_device_array(device, field, target_paths=[], replace=true)` |

Default without `replace` **appends**. A rewrite without `replace=true` stacks
duplicates on the same device — still not a reason to spawn `_v2`.

Asking the user to paste T3D is never a step.
