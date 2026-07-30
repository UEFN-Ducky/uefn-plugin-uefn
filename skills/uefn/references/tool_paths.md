---
description: "Decision table — Verse device vs native Creative device vs plain actor, and which read/write tools each takes"
metadata:
  order: 1
  label: "Tool paths"
  default_enabled: false
  load_condition: "Unsure whether a placed thing is a Verse device, Creative device, or plain actor — or which inspect/set tool applies"
---

## Which tool path? (read first)

UEFN has **two different** device APIs. Using the wrong one fails silently or returns empty editables.

| You see in level | `find_devices` → `kind` | Read | Write (one op per call) |
|------------------|-------------------------|------|-------------------------|
| Custom Verse (your project's own device classes, `VerseDevice_C`) | `verse_script` | `inspect_verse_device` | `wire_verse_device_ref`, `set_verse_editable`, `resize_verse_array`, `patch_verse_array_entry` |
| Native Creative (item granter, conditional button, spawner, `Device_*_C`) | `creative_device` | `inspect_creative_device` | `set_creative_device_fields` |
| Static mesh / prop / Fort actor | (not in `find_devices`) | `get_all_actors` | `set_actor_properties` |

**Decision:** `find_devices(label_filter="wallet")` → check `kind` on each hit → open the matching inspect tool.
