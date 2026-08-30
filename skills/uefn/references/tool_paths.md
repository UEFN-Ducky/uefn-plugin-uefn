---
description: "Decision table — Verse device vs native Creative device vs plain actor, and which read/write tools each takes"
metadata:
  order: 1
  label: "Tool paths"
  default_enabled: false
  load_condition: "Unsure whether a placed thing is a Verse device, Creative device, or plain actor — or which inspect/set tool applies"
---

## Which tool path? (read first)

**Creative devices + census:** use nested Epic UEFN MCP — `skill_read_subskill("uefn", "epic_mcp")`.
`unreal__call_tool` → `ValkyrieToolset.DeviceToolset` (`ListDeviceAssets`, `PlaceDevice`,
`GetDeviceProperties`, `SetDeviceProperty`, …). Do **not** call pruned Ducky
`find_devices` / `inspect_creative_device` / `set_creative_device_fields`.

UEFN still has **two** device shapes. Using the wrong path fails silently.

| You see in level | Path | Read | Write (one op per call) |
|------------------|------|------|-------------------------|
| Native Creative (granter, button, spawner, `Device_*_C`) | Epic `DeviceToolset` | `GetDeviceProperties` / `ListDeviceProperties` via `unreal__call_tool` | `SetDeviceProperty` via `unreal__call_tool` |
| Custom Verse (`VerseDevice_C`) | Ducky VerseDevice | `inspect_verse_device` | `wire_verse_device_ref`, `set_verse_editable`, … |
| Static mesh / prop / Fort actor | Ducky actors **or** Epic `ActorTools` / `SceneTools` | `get_all_actors` or Epic describe | `set_actor_properties` / Epic |

**Decision:** Epic DeviceToolset for Creative; `inspect_verse_device` only for project Verse scripts.
