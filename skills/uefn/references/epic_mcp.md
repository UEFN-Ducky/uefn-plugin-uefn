---
description: "Nested Epic UEFN MCP — Settings label, 43.00 Editor Settings (Start/Stop, config setup), three bridge tools, key toolsets (56 toolsets / 826 tools in 43.00, renamed from 42.40 — full catalog in epic_toolsets)"
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

**NEVER `execute_python` to spawn / place / assign materials.** That is not Epic MCP.
5+ editor ops → `ProgrammaticToolset` `execute_tool_script` (sandboxed tool calls),
not `EditorLevelLibrary.spawn_actor_from_object` in the Ducky listener.

**Check every result (HARD):** Epic tools can report failure in the payload with no
exception — anything not an explicit success is a stop. Save before and after bulk
edits. Safety, recovery, wrong-editor-on-:8000 → `epic_mcp_ops`.

## Where it shows in the app

Settings → **MCPs** → nested row **UEFN MCP (Epic)**  
- slug / id: `unreal-mcp`  
- transport: http → `http://127.0.0.1:8000/mcp`  
- prefix on the IDE bridge: `unreal__*`

If you only see a title-cased **Unreal-Mcp** as Custom, refresh/update the app — the catalog label is **UEFN MCP (Epic)**.

### In UEFN (43.00)

- MCP settings moved from Project Settings to **Editor Settings** — no per-project enable any more; one setting covers every island.
- Editor Settings has **Start / Stop** MCP controls and a **config setup button** that writes the client config for supported models (same as `ModelContextProtocol.GenerateClientConfig`).
- Fixed: MCP did not start by default when the editor launched. Before 43.00 a dead `:8000` right after launch was this bug; in 43.00 check Editor Settings → MCP → Start.
- The server now sends **server instructions** on `initialize`, and tools can return **image content** (e.g. `SceneCaptureToolset.Capture`, `EditorAppToolset.CaptureViewport`) instead of a file path only.

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
| Creative / Verse devices | `ValkyrieFortniteToolset.DeviceToolset` | `ListDeviceAssets`, `PlaceDevice`, `ListDeviceProperties`, `GetDeviceProperties` / `SetDeviceProperty` (Verse `creative_device` settings), event bindings. **Classic (Blueprint) devices (43.00):** `ListClassicDeviceOptions(devicePath)` → `SetClassicDeviceOption(devicePath, optionName, value)`, validated like the Details panel (inactive options and bad values are rejected); `GetClassicDeviceOptionValues` when `allowedValues` was left out |
| Scene Graph entities | `ValkyrieToolset.EntityToolset` | `FindEntities`, `CreateEntity`, `AddComponent`, `SetEntityTransform`, `RenameEntity`, `ReparentEntity`, `DeleteEntity`, … |
| Prefabs (43.00) | `ValkyrieToolset.PrefabToolset` | `CreatePrefab`, `CreatePrefabFromEntities`, `GetPrefabOverrides`, `ApplyPrefabEdits`, `ResetPrefabInstance`, `BreakPrefabInstance` |
| Verse files / build (in-editor) | `VerseToolset.VerseToolset` | `FileTree`, `ListFiles`, `ReadFile`, `WriteFile`, `Replace`, `BuildAll`, … |
| PIC / live session | `ValkyrieFortniteToolset.SessionToolset` | `StartSession`, `PushChanges`, `StartGame`, `StopGame`, `GetSessionStatus`, `GetVerseOutput`, … |
| Player state (43.00) | `FortGameplayToolset.FortPlayerToolset` | `GetLocalPlayerState` |
| Editor app / PIE-ish | `EditorToolset.EditorAppToolset` | viewport, selection, pivot, notifications, … (CVar tools removed in 43.00) |
| Screenshots (43.00) | `SceneCaptureToolset.SceneCaptureToolset` | `ListModes` / `DescribeMode`, `Capture`, `CaptureActiveEditorView`, `CaptureGameViewport` — returns image content |
| Actors / levels / assets | `EditorToolset.ActorToolset`, `EditorToolset.LevelToolset`, `EditorToolset.AssetToolset` | Fortnite catalog props: **`LevelToolset.AddToSceneFromClass`** with `actorType.refPath` = Content Drawer `Package.Asset_C` (+ `name`, `xform`). **Never** `AddToSceneFromAsset` on `/Game/Creative` (creates `FortStaticMeshActor`, cook-fails). Skip `StaticMesh` / `/BakeData/` / `/HLOD/` / `SM_*` / `…/Meshes/`. The 42.40 snake_case names no longer exist (rename table: `epic_toolsets`). |
| Materials | `EditorToolset.MaterialToolset` (+ `MaterialInstanceToolset`, `CurveAtlasToolset`) | Epic material graph when preferred |
| PCG (43.00) | `PCGToolset.PCGToolset`, `PCGToolset.PCGSpatialToolset` | `CreateGraph`, `AddNode`, `ConnectNodePins`, `SpawnGraphInstance`, `ExecuteGraphInstance`; `RunPCGInstantGraph` must be called directly, not from `execute_tool_script` |
| Sequencer (43.00) | `animation_toolset.toolsets.*` (7 toolsets) | cinematics, keyframes, control rig, outliner, conditions, custom bindings, FBX import/export |
| Audio (43.00) | `EditorToolset.SoundWaveToolset`, `MetaSoundToolset.MetaSoundAuthoringToolset` | `ImportFile` → preset builders → `BuildToAsset` |
| Profiling (43.00) | `SpatialProfilerToolset.ProfilerToolset`, `InsightsToolset.*` | needs a running session; see `profiling` |
| Niagara | `NiagaraToolsets.NiagaraToolset_System` (+ Component / Assets / Info) | Epic Niagara assembly |
| UMG | `UMGToolSet.UMGToolSet`, `MVVMToolset.MVVMToolset`, `VerseFieldsToolset.VerseFieldsToolset`, `WidgetAnimationToolset.WidgetAnimationToolset`, `WidgetStaticAnalysisToolset` (`DescribeWidget`, `GetWidgetTreeDepth`), `UMGToolSet.UMGDebugToolSet` | widget tree + MVVM; 42.30 Verse `event` fields (verse `umg_verse_field_events`). What to build: Epic's Verse UI Kit rules — verse `verse_ui_kit` (custom kit buttons only; `AssetToolset.SaveAsset(assetPath)` per asset) |
| Logs | `ConsoleToolset.LogsToolset` (was `EditorToolset.LogsToolset`) | `GetLogEntries(category, pattern, maxEntries)`, `GetLogCategories`, `Get/SetVerbosity` — compile results, Content Pre-Checks |
| Data / curve tables | `EditorToolset.DataTableToolset`, `EditorToolset.CurveTableToolset` | `GetSchema`, `GetRows`, `SetRows`, `AddRows`, `ImportFile`… |
| Meshes / textures / primitives | `EditorToolset.StaticMeshToolset`, `.SkeletalMeshToolset`, `.TextureToolset`, `.PrimitiveToolset` | inspect / edit mesh, bones, sockets, collision complexity, import/export textures |
| Physics assets | `PhysicsToolsets.PhysicsAssetToolset` | create and edit Physics Assets |
| Gameplay tags | `GameplayTagsToolset.GameplayTagsToolset` | `ListTags`, `GetTagInfo`, `FindReferencersByTag` |
| Python enablement | `ValkyrieToolset.ValkyriePythonToolset` | `IsPythonReadyForMainProject`, `EnablePythonForMainProject` (Python-backed toolsets load after this) |
| Batched calls (v42.10+) | `editor_toolset.toolsets.programmatic.ProgrammaticToolset` | `get_execution_environment` (call once first, read its `instructions`), then `execute_tool_script(script)` — a sandboxed Python script defining `run() -> dict` that calls other toolsets (faster in 43.00) |
| Exec Python (43.00) | `editor_toolset.toolsets.python_scripting.PythonScriptingTools` | `execute_python`, `read_me`, `search_symbols`, `get_symbol`, `grep_stubs` — **last resort**, see `epic_mcp_ops` |

Always `describe_toolset` before first call in a session if arguments are unclear — property names and `refPath` shapes are Epic-owned (43.00 arguments are camelCase: `actorType`, `assetPath`, `folderPath`). Every 43.00 toolset with exact tool names and the 42.40 renames: `skill_read_subskill("uefn", "epic_toolsets")`. 42.30 fixed dialogue popups stalling MCP progress; keep `dismiss_uefn_modal` for anything that still blocks.

**Never scale Fortnite Creative devices.** `PlaceDevice` takes location + rotation —
omit Scale. Resize volumes/triggers/barriers via `SetDeviceProperty` (Details
Width/Height/zone/tiles). Actor scale is for props and custom assets only.

**Batching (v42.10+):** `editor_toolset.toolsets.programmatic.ProgrammaticToolset`
runs a small sandboxed Python script that calls other registered toolsets — tool
orchestration, not general Python. Workflow, in order:

1. `unreal__call_tool(toolset_name="editor_toolset.toolsets.programmatic.ProgrammaticToolset", tool_name="get_execution_environment", arguments={})` once per session; read `instructions` and `supported_modules`.
2. `unreal__describe_toolset` for every toolset the script will call, so argument names and output schemas are exact.
3. `unreal__call_tool(..., tool_name="execute_tool_script", arguments={"script": "<python defining run() -> dict>"})`.

Use it when a task needs 5+ placements, property sets, or entity edits; the SERIAL
rule still applies to the single script call (one per turn), the batching happens
inside the editor. The script may only import the modules the environment lists; it
raises on disallowed imports or a missing `run()`.

**Fortnite catalog batch (HARD):** inside `run()`, place props with
`execute_tool("EditorToolset.LevelToolset.AddToSceneFromClass", …)`
and `actorType.refPath` = `Package.Asset_C`, then
`execute_tool("EditorToolset.LevelToolset.SetActorFolder", {actor, folderPath})`. Devices:
`ValkyrieFortniteToolset.DeviceToolset.PlaceDevice` (no Scale). **Never** call
`AddToSceneFromAsset` for `/Game/Creative`.

**Instance arrays (HARD):** `ObjectToolset.SetProperties` cannot replace
`perInstanceSMData` or `perInstanceSMCustomData` in one write. Unreal raises
`ArrayAdd: elements changed alongside the size change; insertion points are
ambiguous` when the array length and the element transforms change together.
Set the array to `[]`, then set the new instances. Ducky's Epic proxy does
that split on `unreal__call_tool`, including scripts passed to
`execute_tool_script`.

## Coordinates

Epic toolsets use **XYZ** (`xform.location {x, y, z}`). UEFN SpatialMath / many Ducky helpers use **LUF**. Do not paste LUF vectors into Epic `arguments`.

## What stays on Ducky (listener second — Epic cannot / offline)

Only when Epic is offline **or** the job is Ducky-only:

- Offline Verse on disk: `workspace_*`, digests (`search_verse_digest`, …)  
- VerseDevice `@editable` wiring: `inspect_verse_device`, `wire_verse_device_ref`, …  
- Prefab helpers: `create_empty_prefab`, `instantiate_prefab`, …  
- Screenshots / Meshy / Blender / Store plugins, level-design spatial helpers  
- `spawn_actor` for leftover `_C` props Epic cannot place (never a `StaticMesh` / BakeData / HLOD hit)  

The old Ducky Creative-device find/inspect/set, PIE, and entity/component tools were
pruned and no longer exist — never call them. Creative devices → `ValkyrieFortniteToolset.DeviceToolset`;
entities/components → `ValkyrieToolset.EntityToolset`; PIC/session → `ValkyrieFortniteToolset.SessionToolset`.
