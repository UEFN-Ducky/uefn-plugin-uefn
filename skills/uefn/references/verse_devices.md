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
| Discover | `find_devices` once — `kind` + `script_class` (do **not** inspect-loop) |
| Read | `inspect_verse_device("<label>")` — **only the device you are about to write** |
| Wire one ref | `wire_verse_device_ref` — **one field per call; wait before next** |
| Set scalar | `set_verse_editable` — **one field per call** |
| Wallet rows | `set_currency_config_entries` |
| Resize `[]struct` array | `resize_verse_array` |
| Fill array row | `patch_verse_array_entry` |
| Wire one array target | `wire_verse_device_array` — **one target per call** |
| Spawn | `spawn_actor(..., label=..., folder=...)` once per device (same tick) |
| Save | `save_current_level` once when done |

**SERIAL:** never multiple wire/spawn/save in the same assistant turn —
`skill_read_subskill("uefn", "batch_commands")`.

**Spawn new device:** `workspace_write_file` → `workspace_compile_verse` →
`search_assets(directory="/_Verse")` for `asset_path` →
`spawn_actor(..., label=..., folder=...)` → wait →
`wire_verse_device_ref` **one field per turn** →
`save_current_level`. Never guess `VerseDeviceBlueprint` or
`/Game/Creative/Devices/...` paths.

`workspace_compile_verse` returns `verse_classes` (compiled `/_Verse` asset paths) — use one directly as `asset_path`. If spawn fails, compile **once** and wait for the build to finish (`[WinError 10054]` means it started — never retry). Poll `list_verse_types` / `verse_classes`; never ask the user to Build Verse unless the wait already finished and the class is still missing. See `skill_read_subskill("uefn", "verse_build_lifecycle")`.

**Do not** census the level with `inspect_verse_device`. `find_devices` already
returns `script_class`. Field names live in that class's `.verse` on disk.

**Do not** use `inspect_creative_device` / `set_creative_device_fields` for @editable Script fields.

Storage is `__verse_0x<HASH>_<Field>` on the Script object. Wrappers outer to
**Script** (not the actor) and hold `SavedActor`. `STOP` / `mangled_name: null`
is a cache miss — resolve then wire. Never ask the user to paste T3D.
Details: `skill_read_subskill("uefn", "verse_editable_internals")`.

**Do not** use `batch_commands`, `bulk_*`, `setup_verse_device`, or
`spawn_actor_batch` — removed (freeze UEFN).

**Audio `@editable audio_player_device`:** place Creative Audio Player first —
`skill_read_subskill("uefn", "creative_devices")` — then wire one field per turn.
