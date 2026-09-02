---
description: "Nested Epic UEFN MCP — Settings label, three bridge tools, Valkyrie + editor toolsets"
metadata:
  order: 0
  label: "Epic UEFN MCP"
  default_enabled: true
  load_condition: "Any editor Verse/device/entity/PIC work, or when Settings → MCPs / unreal__* / UEFN MCP is mentioned"
---

# Epic UEFN MCP (nested under Ducky)

## Prefer Epic first (HARD)

When `ducky_get_status.epic_mcp_online` is true, **always** use `unreal__*` for
anything Epic covers (devices, entities, PIC, in-editor Verse, actors/assets,
Epic material / Niagara / UMG toolsets). Do **not** reach for the Ducky listener
for those jobs. Listener is second — only Epic-offline gaps and Ducky-only work
below.

## Where it shows in the app

Settings → **MCPs** → nested row **UEFN MCP (Epic)**  
- slug / id: `unreal-mcp`  
- transport: http → `http://127.0.0.1:8000/mcp`  
- prefix on the IDE bridge: `unreal__*`

If you only see a title-cased **Unreal-Mcp** as Custom, refresh/update the app — the catalog label is **UEFN MCP (Epic)**.

Check health: `ducky_get_status` → `epic_mcp_online` (a TCP probe, not a session guarantee). If an `unreal__*` call errors or the tools are missing: retry once, then degrade to the closest Ducky tool (`spawn_actor` for props/Verse devices, `workspace_*`, `wire_verse_*`) and finish the task — never "offline → stop". Mention `epic_mcp_setup_steps` in one line after the work is done.

## Only three MCP tools exist

Epic does **not** expose flat `unreal__<tool>` names. Every editor Epic call is:

1. `unreal__list_toolsets` — discover toolset names  
2. `unreal__describe_toolset({ "toolset_name": "<name>" })` — schemas  
3. `unreal__call_tool({ "toolset_name": "<name>", "tool_name": "<Tool>", "arguments": {…} })`

`tool_name` is the short name from describe (e.g. `PlaceDevice`, `CreateEntity`, `BuildAll`). Prefer short names; if Epic rejects, retry with the fully qualified name from describe.

**SERIAL:** one `unreal__call_tool` (or other heavy editor op) per assistant turn.

## Key toolsets (UEFN)

| Job | toolset_name | Example tools |
|-----|--------------|---------------|
| Creative / Verse devices | `ValkyrieToolset.DeviceToolset` | `ListDeviceAssets`, `PlaceDevice`, `ListDeviceProperties`, `GetDeviceProperties`, `SetDeviceProperty`, event bindings |
| Scene Graph entities | `ValkyrieToolset.EntityToolset` | `FindEntities`, `CreateEntity`, `AddComponent`, `SetEntityTransform`, `DeleteEntity`, … |
| Verse files / build (in-editor) | `ValkyrieToolset.VerseToolset` | `ListFiles`, `ReadFile`, `WriteFile`, `Replace`, `BuildAll`, … |
| PIC / live session | `ValkyrieToolset.SessionToolset` | `StartSession`, `PushChanges`, `StartGame`, `StopGame`, `GetSessionStatus`, … |
| Editor app / PIE-ish | `EditorToolset.EditorAppToolset` | viewport, selection, notifications, … |
| Actors / levels / assets | `editor_toolset.toolsets.actor.ActorTools`, `.scene.SceneTools`, `.asset.AssetTools`, … | place/inspect actors, levels |
| Materials | `editor_toolset.toolsets.material.MaterialTools` (+ `material_instance`) | Epic material graph when preferred |
| Niagara | `NiagaraToolsets.NiagaraToolset_System` (+ Component / Assets / Info) | Epic Niagara assembly |
| UMG | `UMGToolSet.UMGToolSet`, `MVVMToolset.MVVMToolset`, `VerseFieldsToolset.VerseFieldsToolset` | widget tree + MVVM |

Always `describe_toolset` before first call in a session if arguments are unclear — property names and `refPath` shapes are Epic-owned.

## Coordinates

Epic Python toolsets use **XYZ**. UEFN SpatialMath / many Ducky helpers use **LUF**. Do not paste LUF vectors into Epic `arguments`.

## What stays on Ducky (listener second — Epic cannot / offline)

Only when Epic is offline **or** the job is Ducky-only:

- Offline Verse on disk: `workspace_*`, digests (`search_verse_digest`, …)  
- VerseDevice `@editable` wiring: `inspect_verse_device`, `wire_verse_device_ref`, …  
- Prefab helpers: `create_empty_prefab`, `instantiate_prefab`, …  
- Screenshots / Meshy / Blender / Store plugins, level-design spatial helpers  
- `spawn_actor` for props/meshes Epic cannot place  

The old Ducky Creative-device find/inspect/set, PIE, and entity/component tools were
pruned and no longer exist — never call them. Creative devices → `ValkyrieToolset.DeviceToolset`;
entities/components → `ValkyrieToolset.EntityToolset`; PIC/session → `ValkyrieToolset.SessionToolset`.
