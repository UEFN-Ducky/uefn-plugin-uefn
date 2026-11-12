---
description: "Which Epic UEFN MCP toolset covers which job, and the gotchas the live descriptions don't tell you — use before unreal__describe_toolset to pick the right one"
metadata:
  order: 2
  label: "Epic toolsets: picking one + gotchas"
  default_enabled: false
  load_condition: "Choosing an Epic toolset or tool name (unreal__call_tool), or the user asks what the UEFN MCP can do — level/actors, assets, Niagara, PCG, Sequencer, profiling/Insights, scene capture, prefabs, physics assets, gameplay tags, logs, data/curve tables, textures, meshes, UMG/MVVM, MetaSound, Python"
---

# Epic UEFN MCP toolsets

The server has three tools: list toolsets, describe a toolset, call a tool (Ducky shows
them with the `unreal__` prefix). The live list and descriptions are the source of truth
for names and arguments; describe a toolset before your first call to it. Object
arguments are `{"refPath": "<path>"}`. The programmatic script runner can't describe
toolsets (that tool sits outside its registry), so describe first, then script.

## Where to look

| Job | Toolset family |
| --- | --- |
| Actors, levels, folders, placing from a class, traces | `EditorToolset` (actor / level) |
| Assets, redirectors, validation, tables, textures, meshes, materials | `EditorToolset` (asset and per-type toolsets) |
| Viewport, selection, camera, notifications | `EditorToolset` editor app |
| Creative devices, sessions, game start/stop, client log, Verse output | `ValkyrieFortniteToolset` |
| Scene Graph entities, components, prefabs | `ValkyrieToolset` |
| Verse files and build | `VerseToolset` |
| Niagara, PCG, physics assets, MetaSound, gameplay tags | their own named toolsets |
| Sequencer, keys, Control Rig | `animation_toolset` (Python-backed) |
| UMG, MVVM bindings, widget animations, widget analysis | UMG / MVVM / widget toolsets |
| Profiling and captures | `SpatialProfilerToolset`, `InsightsToolset`, `SceneCaptureToolset` |
| Editor log | `ConsoleToolset` |

## Gotchas

- **Pictures:** for a picture of the level call Ducky's `take_high_res_screenshot` (works in every
  agent, needs no Epic toolset); `uefn_window_capture` for the editor window itself. Through Epic
  it is the scene capture toolset or the editor app's viewport capture. No toolset is named
  "scene" or "SceneTools": that 42.40 name answers "Toolset … not found".
- **Place Creative content from its class, never from its asset:** placing a `/Game/Creative/**`
  Blueprint from the asset makes a static mesh actor that fails to cook.
- **PCG:** Epic ships a PCG graph skill (read it through the agent skill toolset) and leveldesign
  `procedural_generation` covers ours. Epic's skill names a graph duplicate and a singular param
  setter that don't exist: duplicate through the asset toolset and set params in bulk. Graph refs
  are objects; node refs are `"<graph path>:<nodeName>"`. The instant PCG graph runner must be
  called directly, not from a script.
- **Python-backed toolsets** (Sequencer, Geometry, Python scripting, the script runner) need
  Python enabled for the main project first; enabling is asynchronous, so check again before use.
- **Logs:** the console toolset reads the editor log (compile results, Content Pre-Check, blueprint
  errors); the session toolset reads the launched client's log and Verse `Print` output.
- **Profiling needs a running session.** Discovery is async: list clients or targets (retry once),
  acquire or check you can capture, sample, stop.
- **Verse field types** for UMG bindings are a short list (ask the Verse fields toolset); event
  fields take at most one simple parameter. Details: verse `umg_verse_field_events`.
