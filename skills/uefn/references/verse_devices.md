---
description: "Placed Verse device workflows — inspect/set fields, arrays, spawning a compiled class into the level"
metadata:
  order: 3
  label: "Verse devices"
  default_enabled: false
  load_condition: "Inspecting, wiring, or placing a Verse (verse_script) device in the level"
---

## Verse script devices (`verse_script`)

Custom Verse classes placed in the world (`VerseDevice_C` — the label is whatever the Outliner shows).

| Job | Tool |
|-----|------|
| Discover | `list_verse_devices` once — label + `script_class` (do **not** inspect-loop) |
| Read | `inspect_verse_device("<label>")` — **only the device you are about to write** |
| Wire one ref | `wire_verse_device_ref` — **one field per call; wait before next** |
| Set scalar | `set_verse_editable` — **one field per call** |
| Wallet rows | `set_currency_config_entries` |
| Resize `[]struct` array | `resize_verse_array` |
| Fill array row | `patch_verse_array_entry` |
| Wire an array | `wire_verse_device_array` — **all targets in one call** (`target_paths=[...]`) |
| Spawn | `spawn_actor(..., label=..., folder=...)` once per device (same tick) |
| Save | `save_current_level` once when done |

**SERIAL:** never multiple wire/spawn/save in the same assistant turn —
SERIAL: one mutating/editor call per assistant message..

**Census first (HARD):** `list_verse_devices` for this class. If a placement
already exists, **reuse it**. Never spawn `_v2` / `_Test` / a second
`VerseDevice_C` to get hashes or to rewrite a field.

**First array item** (field empty) — same device, one call:

```
wire_verse_device_array("EditableWiringTest", "TestProps", target_paths=["WireProp_01"])
```

**Rewrite the list** — same device, `replace=true` with the **full** new list:

```
wire_verse_device_array("EditableWiringTest", "TestProps", target_paths=["WireProp_01", "WireProp_02"], replace=true)
```

Without `replace=true` the call **appends** (duplicates). Clear with
`replace=true` and empty `target_paths`. Details:
`skill_read_subskill("uefn", "verse_editable_internals")`.

**Spawn only when no instance exists:** `workspace_write_file` → `workspace_list_verse_errors` → `workspace_compile_verse` (must succeed — otherwise fields have no compiled hash, "STALE REFLECTION") →
pick `asset_path` from `verse_classes` (or `search_assets` on `/<Project>/_Verse` — never bare `/_Verse` or `/Game`) →
`spawn_actor(..., label=..., folder=...)` **once** → wait →
`wire_verse_device_ref` / `wire_verse_device_array` **one field per turn**
(plain Verse names; first item = `target_paths=[one]`; rewrite = `replace=true`) →
`get_verse_editables` to **verify** → `save_current_level`. Never guess
`VerseDeviceBlueprint` or `/Game/Creative/Devices/...` paths. STALE REFLECTION
means the live Script still has no readable hash after resolve — not a cue to
wait-and-hope. Host already retried once; check compile output, re-inspect the
**same** device. Never place a second copy.

`workspace_compile_verse` returns `verse_classes` (compiled `/<Project>/_Verse` asset paths) — use one directly as `asset_path`. Never search bare `/_Verse` or `/Game` for a project Verse class. If spawn fails, compile **once** and wait for the build to finish (`[WinError 10054]` means it started — never retry). Poll `list_verse_types` / `verse_classes`; never ask the user to Build Verse unless the wait already finished and the class is still missing. See `skill_read_subskill("uefn", "verse_build_lifecycle")`.

**Do not** census the level with `inspect_verse_device`. `list_verse_devices` already
returns `script_class`. Field names live in that class's `.verse` on disk.

**Do not** use Epic DeviceToolset `SetDeviceProperty` for @editable Script fields — that is the Creative-device path.

Storage is `__verse_0x<HASH>_<Field>` on the Script object (hash = CRC32 of the
field name, identical in every project). Wrappers outer to
**Script** (not the actor) and hold `SavedActor`. `STOP` / `readable: false`
means the compiled class lacks that field — compile once, wait, re-inspect.
Never ask the user to paste T3D.
Details: `skill_read_subskill("uefn", "verse_editable_internals")`.

**Do not** use `batch_commands`, `bulk_*`, `setup_verse_device`, or
`spawn_actor_batch` — removed (freeze UEFN).

**Audio `@editable audio_player_device`:** place Creative Audio Player first —
`skill_read_subskill("uefn", "creative_devices")` — then wire one field per turn.
