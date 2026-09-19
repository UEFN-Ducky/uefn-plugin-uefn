---
description: "Native Creative device workflows — inspect/set ToyOptions, place-in-level golden path, and Fortnite Audio Player for SFX/horns"
metadata:
  order: 4
  label: "Creative devices"
  default_enabled: false
  load_condition: "Configuring a native Creative device (granter, button, spawner, teleporter, audio player…) or placing devices / horns / SFX in the level"
---

## Native Creative devices (Epic `ValkyrieToolset.DeviceToolset`)

Epic-built devices: item granters, conditional buttons, player spawners,
teleporters, timers, **Audio Players**, etc.

**Prefer nested Epic UEFN MCP** (`skill_read_subskill("uefn", "epic_mcp")`):

```
unreal__describe_toolset({ "toolset_name": "ValkyrieToolset.DeviceToolset" })
unreal__call_tool({
  "toolset_name": "ValkyrieToolset.DeviceToolset",
  "tool_name": "PlaceDevice",   # or ListDeviceAssets / GetDeviceProperties / SetDeviceProperty
  "arguments": { … }            # XYZ location/rotation; omit Scale — use refPath objects from prior Epic returns
})
```

The old Ducky Creative-device find/inspect/set tools were pruned and no longer exist.
Call `unreal__describe_toolset` first to read the exact argument names — never invent them.
If `ducky_get_status.epic_mcp_online` is false or an Epic call errors twice, degrade:
`spawn_actor(asset_path=…, location=…, label=…, folder=…)` places props and Verse devices
and you finish the task — never "offline → stop".

Prefer **Fortnite Creative devices** from `/Game/Creative` (or
`/Game/Creative/Devices`) for gameplay devices. Confirm Blueprint with
`search_assets` → Epic `PlaceDevice` (or Ducky `spawn_actor(…_C)` for props only —
skip `StaticMesh` / `/BakeData/` / `/HLOD/` / `SM_*` hits; never spawn a mesh “and fix later”).

**Never scale Fortnite Creative devices (HARD).** Actor `scale` / `set_actor_scale3d`
/ Epic ActorTools scale / `PlaceDevice` Scale **breaks** buttons, triggers, volumes,
barriers, pads, granters, Island Settings. Place with location + rotation only —
**omit Scale**. To resize, `GetDeviceProperties` then `SetDeviceProperty` (Details
`Width` / `Height` / `Depth` / zone / tiles). Location and rotation via
`set_actor_transform` are fine. Scale is for props, meshes, and custom assets only.

**SERIAL:** one heavy MCP call → wait → next (never same-turn multi spawn/wire).
See SERIAL: one mutating/editor call per assistant message..

| Job | Tool |
|-----|------|
| Discover assets | Epic `ListDeviceAssets` |
| Place | Epic `PlaceDevice` |
| Read ToyOptions | Epic `ListDeviceProperties` / `GetDeviceProperties` |
| Write | Epic `SetDeviceProperty` |
| Event graph | Epic `ListEventBindings` / `AddEventBinding` / … |

**Do not** use VerseDevice `@editable` tools for ToyOptions (e.g. granter item list).

**Island Settings:** same Epic DeviceToolset path; load
`skill_read_subskill("islandsettings", "session_setup")`.
Rule: `MaxPlayers = N` requires **N Player Spawn Pads**.

## Verse `*_device` name ≠ placeable Blueprint

`teleporter_device`, `button_device`, `item_granter_device`, … are **Verse API types** (digests / `@editable` typing). They are **not** `spawn_actor` class names.

| Job | Tool |
|-----|------|
| Learn API / events | `search_verse_digest(query="teleporter")` → `get_verse_api(name="teleporter_device")` |
| Place in level | Epic `ValkyrieToolset.DeviceToolset` `ListDeviceAssets` → `PlaceDevice`; offline fallback: `search_assets(search="…", directory="/Game/Creative")` → `spawn_actor(asset_path="…_C")` |

**Props / Prefabs / full Creative catalog** (walls, Sets, Content Drawer map): not this
file — `skill_read_subskill("leveldesign", "content_catalog")`. Device **API types** are
all listed via digests: `list_verse_types(digest="fortnite", kind="class", name_filter="_device")`.

## Place devices in the level (golden path)

When the user says **place / add / put** triggers, granters, teleporters, spawn pads — **do it immediately** with defaults. Prefer Epic DeviceToolset:

```
unreal__describe_toolset({ "toolset_name": "ValkyrieToolset.DeviceToolset" })
unreal__call_tool({
  "toolset_name": "ValkyrieToolset.DeviceToolset",
  "tool_name": "ListDeviceAssets",
  "arguments": {}
})
unreal__call_tool({
  "toolset_name": "ValkyrieToolset.DeviceToolset",
  "tool_name": "PlaceDevice",
  "arguments": { … }   # assetPath refPath + location/rotation XYZ — omit Scale
})
```

Props-only fallback (not Creative ToyOptions): `search_assets` under `/Game/Creative` → spawn only `BlueprintGeneratedClass` `_C` paths (`spawn_actor(asset_path="…_C", label=…, folder=…)`). Skip mesh / BakeData / HLOD hits. Never `spawn_actor(actor_class="*_device")`.
Use separate `set_actor_label` / `set_actor_folder` only when renaming an existing actor.
Nested folders by area/system (`Hub/Spawners`, `Hub/Teleporters`, `Area1/Combat`).

**Granters:** Epic `ListDeviceAssets` → pick the Item Granter asset → `PlaceDevice` → `SetDeviceProperty` per option. Offline fallback: `search_assets(search="Item_Granter", directory="/Game/Creative")` → `spawn_actor(asset_path="…BP_Creative_Item_Granter…_C", …)` (full `_C` suffix from the search hit).

**Teleporter (built-in Creative device):**

```
search_verse_digest(query="teleporter")   # optional — confirms teleporter_device API
unreal__describe_toolset(toolset_name="ValkyrieToolset.DeviceToolset")   # exact argument names — never invent them
unreal__call_tool(toolset_name="ValkyrieToolset.DeviceToolset", tool_name="ListDeviceAssets", arguments={})
# → Creative Teleporter device asset (not Athena B_Teleporter gadgets)
unreal__call_tool(toolset_name="ValkyrieToolset.DeviceToolset", tool_name="PlaceDevice",       arguments={…})  # ONE call, wait
unreal__call_tool(toolset_name="ValkyrieToolset.DeviceToolset", tool_name="SetDeviceProperty", arguments={…})  # one property per call
save_current_level()
```

Offline fallback only (`epic_mcp_online` false or Epic errored twice):
`search_assets(search="Teleporter", directory="/Game/Creative", limit=10)` →
`spawn_actor(asset_path="…/BP_Creative_Device_Teleporter.BP_Creative_Device_Teleporter_C", location=[x, y, z], select=false, label="Hub_TP_Area1", folder="Hub/Teleporters")`
→ `save_current_level()`. Bare `search="Teleporter"` without `directory="/Game/Creative"` hits Athena gadgets — wrong family.

### Audio Player (horns / wave SFX / alarms) — hard rule

Gameplay SFX = Fortnite Creative **Audio Player** only (`audio_player_device` in
Verse). **Never** Speakers, prop “horn” meshes, or Scene Graph `sound_component`
as the primary path.

```
unreal__describe_toolset(toolset_name="ValkyrieToolset.DeviceToolset")   # exact argument names — never invent them
unreal__call_tool(toolset_name="ValkyrieToolset.DeviceToolset", tool_name="ListDeviceAssets", arguments={})
# pick the Creative Audio Player device (not a prop kit / Speakers)
unreal__call_tool(toolset_name="ValkyrieToolset.DeviceToolset", tool_name="PlaceDevice",       arguments={…})  # ONE call, wait
unreal__call_tool(toolset_name="ValkyrieToolset.DeviceToolset", tool_name="SetDeviceProperty", arguments={…})  # sound / play options, one at a time
# wire to Verse ONE field per turn (workspace_compile_verse must have succeeded first):
wire_verse_device_ref(actor_path="<VerseDevice>", field="HordeHornAudio", target_path="<AudioLabel>")
save_current_level()   # once, at the end of the batch
```

Offline fallback only: `search_assets(search="Audio", directory="/Game/Creative", limit=15)` →
`spawn_actor(asset_path="<AudioPlayer>_C", location=[x,y,z], select=false, label="Hub_Horn", folder="Hub/Audio")`.

Never `spawn_actor(actor_class="audio_player_device")`.

### First Person Camera + Unarmed (v42.20 FPS melee)

Verse type `gameplay_camera_first_person_device`. Place it like any other
Creative device: `ListDeviceAssets` → pick the **First Person Camera** asset →
`PlaceDevice` (location/rotation only — **never scale**). Never
`spawn_actor(actor_class="gameplay_camera_first_person_device")`.

Punch / unarmed melee is **not** a device and **not** a custom montage. Grant
`Unarmed_Creative_V1_Common{}` via `AddItemDistribute` (`skill_read_subskill("scenegraph", "itemization")`).

### Player Movement Device caps (v42.20)

ToyOptions via `GetDeviceProperties` / `SetDeviceProperty` — **never scale**
the device. New maxima (values above the old caps are at-own-risk):

| ToyOption | Old cap | 42.20 max |
|-----------|---------|-----------|
| Sprint Maximum Speed | 2,000 | **11,000** |
| Tactical Sprint Speed Multiplier | 5 | **20** |
| Maximum Acceleration | 1,000 | **10,000** |

`ListDeviceAssets` once for the Content Drawer **Player Movement Device** `*_C`.
The Verse type `movement_modulator_device` is the speed modulator — do **not**
assume it is the Player Movement Device until the asset name matches.

**Wire to Verse device:** after placement, wait → `inspect_verse_device` →
`wire_verse_device_ref(actor_path="MyDevice", field="SomeTriggerField", target_path="MyTrigger_1")` —
**one field per turn**.
