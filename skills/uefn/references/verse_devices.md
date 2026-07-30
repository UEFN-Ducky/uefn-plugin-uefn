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
| Discover | `find_devices` → confirm `kind: verse_script` |
| Read | `inspect_verse_device("<label>")` — **always before write** |
| Wire one ref | `wire_verse_device_ref` — **one field per call** |
| Set scalar | `set_verse_editable` — **one field per call** |
| Wallet rows | `set_currency_config_entries` |
| Resize `[]struct` array | `resize_verse_array` |
| Fill array row | `patch_verse_array_entry` |
| Wire one array target | `wire_verse_device_array` — **one target per call** |
| Spawn | `spawn_actor` → `set_actor_label` (once per device) |
| Save | `save_current_level` once when done |

**Spawn new device:** `workspace_write_file` → `workspace_compile_verse` → `search_assets(directory="/_Verse")` for `asset_path` → `spawn_actor` → `set_actor_label` → `wire_verse_device_ref` per field → `save_current_level`. Never guess `VerseDeviceBlueprint` or `/Game/Creative/Devices/...` paths.

`workspace_compile_verse` returns `verse_classes` (compiled `/_Verse` asset paths) — use one directly as `asset_path`. If spawn fails, compile and retry **yourself** — never ask the user to Build Verse.

**Do not** use `inspect_creative_device` / `set_creative_device_fields` for @editable Script fields.

**Do not** use `batch_commands`, `bulk_*`, or `setup_verse_device` — removed (freeze UEFN).
