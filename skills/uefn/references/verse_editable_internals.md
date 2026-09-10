---
description: "How Verse @editable fields are stored and wired — mangled names, Script object, wrapper outering, SavedActor, recovery when inspect looks empty"
metadata:
  order: 4
  label: "Verse @editable internals"
  default_enabled: false
  load_condition: "Wiring or inspecting a VerseDevice_C @editable, get_verse_editables STOP, mangled_name null, or a device-ref array (npc_spawner_device, button_device, …)"
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

Example: `CatSpawners` → `__verse_0xDE71A4D4_CatSpawners`.

Probing the plain Verse name (`CatSpawners`, `catSpawners`) correctly returns
"not found". That is **not** evidence the field is missing.

`wire_verse_*` resolves the mangled name on write from the live Script
(`dir()` + class properties + export-text). `get_verse_editables` /
`inspect_verse_device` return `mangled_name` for **verify**, not as a
prerequisite. `STOP` is advisory.

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

### Recovery when inspect looks empty

`mangled_name: null` / `STOP: true` while the `.verse` clearly has `@editable`
fields is a **cache miss**, not missing compilation.

1. `list_verse_property_hashes(refresh=true)`
2. Re-call `get_verse_editables` / `inspect_verse_device` on **that one** device
3. If `mangled_name` is set, `wire_verse_device_ref` / `wire_verse_device_array` / `set_verse_editable` **once**
4. If a wire still fails: `reload_listener`, retry **once**
5. One-object `execute_python` that reads/writes `script.get_editor_property(mangled)` is allowed. Do **not** `os.walk` / `rglob` / scan `.uasset` for `__verse_0x`.

**STALE REFLECTION means the live Script has no readable hash after resolve**
— not “always wait for a build.” The field is in `.verse`, but
`get_editor_property(__verse_0x…_Field)` still fails on this placed device
(compile not landed, or a real reflection miss). The host auto-retries
`wire_*` **once**. A second identical STALE: check compile output, re-inspect
the **same** device. Never place a second copy (same stale class; the existing
instance gets the hashes when the build lands). Never loop
`wire_verse_device_array`. `get_verse_editables` verifies; it is not a
prerequisite once resolve is complete.

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
