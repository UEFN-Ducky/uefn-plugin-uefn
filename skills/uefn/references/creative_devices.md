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
  "arguments": { … }            # XYZ; use refPath objects from prior Epic returns
})
```

Pruned Ducky tools (`find_devices`, `inspect_creative_device`,
`set_creative_device_fields`) must **not** be used when Epic is the path.

Prefer **Fortnite Creative devices** from `/Game/Creative` (or
`/Game/Creative/Devices`) for gameplay devices. Confirm Blueprint with
`search_assets` → Epic `PlaceDevice` (or Ducky `spawn_actor(…_C)` for props only).

**SERIAL:** one heavy MCP call → wait → next (never same-turn multi spawn/wire).
See `skill_read_subskill("uefn", "batch_commands")`.

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
| Place in level | `search_assets(search="…", directory="/Game/Creative")` → `spawn_actor(asset_path="…_C")` |

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
  "arguments": { … }   # assetPath refPath + transform XYZ from describe schema
})
```

Props-only fallback (not Creative ToyOptions): `search_assets` → `spawn_actor(asset_path="…_C", label=…, folder=…)`.
Never `spawn_actor(actor_class="*_device")`.
Use separate `set_actor_label` / `set_actor_folder` only when renaming an existing actor.
Nested folders by area/system (`Hub/Spawners`, `Hub/Teleporters`, `Area1/Combat`).

**Granters:** `search_assets(search="Item_Granter", directory="/Game/Creative")` → spawn `BP_Creative_Item_Granter` (use full `.…_C` suffix from search result).

**Teleporter (built-in Creative device):**

```
search_verse_digest(query="teleporter")   # optional — confirms teleporter_device API
search_assets(search="Teleporter", directory="/Game/Creative", limit=10)
# → BP_Creative_Device_Teleporter (not Athena B_Teleporter gadgets)
spawn_actor(
  asset_path="/Game/Creative/Devices/Teleporter/BP_Creative_Device_Teleporter.BP_Creative_Device_Teleporter_C",
  location=[x, y, z],
  select=false,
  label="Hub_TP_Area1",
  folder="Hub/Teleporters",
)
inspect_creative_device / set_creative_device_fields as needed
save_current_level()
```

Bare `search="Teleporter"` without `directory="/Game/Creative"` hits Athena gadgets — wrong family.

### Audio Player (horns / wave SFX / alarms) — hard rule

Gameplay SFX = Fortnite Creative **Audio Player** only (`audio_player_device` in
Verse). **Never** Speakers, prop “horn” meshes, or Scene Graph `sound_component`
as the primary path.

```
search_assets(search="Audio", directory="/Game/Creative", limit=15)
# pick Creative Audio Player BP (not a prop kit / Speakers) — use …_C from hit
spawn_actor(
  asset_path="<AudioPlayer>_C",
  location=[x,y,z],
  select=false,
  label="Hub_Horn",
  folder="Hub/Audio",
)  # ONE call, wait
inspect_creative_device / set_creative_device_fields (sound / play options)  # one at a time
# wire to Verse ONE field per turn:
wire_verse_device_ref(actor_path="<VerseDevice>", field="HordeHornAudio", target_path="<AudioLabel>")
```

Never `spawn_actor(actor_class="audio_player_device")`.

**Wire to Verse device:** after placement, wait → `inspect_verse_device` →
`wire_verse_device_ref(actor_path="MyDevice", field="SomeTriggerField", target_path="MyTrigger_1")` —
**one field per turn**.
