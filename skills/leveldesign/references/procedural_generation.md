---
description: "Procedural generation in UEFN: PCG in UEFN 43.00 (MCP PCGToolset create/edit graphs, PCG Library examples, reusable PCG tools, forests/cities/POIs, seeds) vs algorithmic placement, seeded patterns, collision-checked spawning, cleanup and perf budgets"
metadata:
  order: 2
  label: "Procedural generation"
  default_enabled: false
  load_condition: "User asks for procedural/PCG generation, a PCG graph, PCG in UEFN, the MCP PCGToolset, the PCG Library, scattering many props, random layouts, forests, cities, POIs, seeds, mazes, dungeons, or generated arenas"
---

## Procedural generation — two routes

### Route A: PCG graphs (UEFN 43.00+)

PCG (Procedural Content Generation Framework) is in UEFN from 43.00: graph-based,
deterministic placement (seed + noise, not AI) for forests, cities, POIs, scatter.

- **PCG Library (reuse first):** ~95 example graphs live at `/PCGPrimitives/Examples/**`. They include
  `Forest/Forest_Square_200m` (+ edits: road, clearing, texture-driven scale/variety, undergrowth),
  `City/City_Generator_Steps_1..7`, `Road/*`, `Park/Square_Park_100m`, `Industrial/Cable_Generator*` and
  44 `Basics/Basics_*`. If one fits, `SpawnGraphInstance` it with `jsonParams` overrides; if one is close,
  duplicate it (`EditorToolset.AssetToolset.Duplicate`; PCGToolset has no DuplicateGraph although Epic's
  skill names one) and edit the copy. Author from scratch only when nothing is close.
- **Reusable PCG tools:** save a graph (plus its parameters) as an asset in the project
  and reuse it across islands — one graph, many instances with different params/seeds.
- **Graph editing IS exposed** through Epic MCP `PCGToolset.PCGToolset` (30 tools),
  called with `unreal__call_tool("PCGToolset.PCGToolset", "<tool>", {...})`. Read the
  argument names from `unreal__describe_toolset` once; don't guess them.
- **Epic's PCG agent skills ship in the editor.** Before any PCG work:
  `unreal__call_tool("ToolsetRegistry.AgentSkillToolset", "GetSkills", {"skillPaths": [
  "/PCGToolset/Skills/Skill_PCGGraphGeneration.Skill_PCGGraphGeneration_C"]})` and follow it.
  Others (`ListSkills` shows all): `Skill_InstantLevelOperations` (fire-and-forget ops),
  `Skill_PCGAssetZoo`, `Skill_PCGBiomeCore` (+`Refinement` = zero-points debug checklist),
  `Skill_PCGInstancingOnMeshActor` (greeble, only on request), `Skill_PCGMeshPartition` (PCG terrain),
  `Skill_PCGShapeGrammarDefinition` (layouts along splines).
- **Refs are objects:** `{"graph": {"refPath": "/<root>/F/G.G"}}`; node refs are `"<graph path>:<nodeName>"`.

**Create a forest graph (golden path):**

1. **Learn:** `GetGraphStructure` on 2–3 matching examples (always some `Basics_*`). Then
   `GetGraphSchema` on each **primitive** subgraph you may use (`/PCGPrimitives/Primitives/<Cat>/<Name>`:
   Create, Fill, Assign, Filter, Spawn, Transform, Place, Compose, Subdivide, Trace, Write…).
   Epic: **always prefer primitives**. Use native nodes (`ListNativeNodes` → `GetNativeNodeSchema`) only when no
   primitive does the job or the user asks for them.
2. **Build:** `CreateGraph{name, path: get_project_info().content_root + "<Folder>"}` (e.g.
   `/295f941d-…/PCGResearch`). Always pass `path`: the default `/Game/PCG` and `/<island name>/…` fail with
   "outside this project's valid asset roots". → `AddSubgraphNode` / `AddNode` per step, with all params set in
   the same call (`jsonParams` is a JSON *string*, keys are the camelCase names `GetGraphStructure` shows, e.g.
   `pointsPerSquaredMeter`, `samplingSeed`) → `ConnectNodePins(from,"Out",to,"PrimaryInput")` →
   `SetGraphParams` for knobs a user tunes (density, spacing, seed, mesh set) → `SetGraphDescription`; tidy
   with `RepositionNode`, `AddCommentBox`, `SetNodeComment`.
   **Graph params need wiring:** each param = a native **Get Graph Parameter** node (`PropertyPath` = param name)
   connected to the *matching parameter pin* of the target node (every node param has a same-named pin). Never
   wire it into `In`/`PrimaryInput`, and never bind it via UpdateNode JSON (unsupported). Expose assets always.
   **Asset arrays:** `type:"SoftObjectPath", containerType:"Array"`. `Object`/`SoftObject` arrays become
   `PropertyBagMissingObject` and reject every instance override. Check `GetGraphSchema` (items must be titled
   `/Script/CoreUObject.Object`). Pattern: `Basics_WireParameterToAssetArrayPin`.
   **Attribute names:** set `OutputAttributeName`; downstream `InputSource` = `PCGBegin(name)PCGEnd`
   (an unnamed output is `None`).
3. **Place + run:** `SpawnGraphInstance{graph, name, transform (scale {25,25,10} default), jsonParams}`.
   Use the **returned** actor ref (its name gets a random suffix). Then `ExecuteGraphInstance{pCGVolume}`:
   `[]` means success. A seed is a node param (`samplingSeed`, `seed`) unless you exposed it with SetGraphParams;
   only exposed params can be set with `SetGraphInstanceParams`.
4. **Inspect / fix:** `GetGraphStructure`, `GetNodeInfo`, `GetNodeDataView` (points a
   node produced), `ListGraphInstances`, `GetGraphInstanceParams`; edit with
   `UpdateNode`, `DisconnectNodePins`, `RemoveNode`, `RemoveGraphParams`,
   `ResetGraphInstanceParams`, then execute again.
   `GetNodeDataView` fails on its first call ("…produced no data on pin 'Out'") because that call only arms
   inspection. Execute again, then read it (`attributeName:"$Position"`, count the `element_N` keys).
   Inspection is per graph *asset*. With several volumes on one graph, Execute/DataView one actor at a time
   or the editor freezes.
   **Execute returned warnings/errors → do NOT auto-fix** (Epic: the messages are unreliable and lead to wrong
   edits). Report them, suggest fixes, and wait for the user.
5. **Splines:** `DrawSpline{actorLabel, actorTag, bRedraw, bClosedSpline}` **waits for the human** to draw in the
   viewport. Use it only when the user is at the editor and asked to draw; otherwise build splines with
   `Create_Spline_Shape` / `Create_Spline_line` primitives.
6. **One-shot spatial graph:** `PCGToolset.PCGSpatialToolset.RunPCGInstantGraph` —
   call it **directly**, not from `execute_tool_script`.
   Instant graphs are `/PCGPrimitives/Instants/Instant_*` (`Input_*` are helpers). Read one with
   `GetGraphStructure`, then call `RunPCGInstantGraph(graph, {Param: Value})`. Chain them one after another.
   **Ask the user before any delete operation.**

Rules: say the seed in your summary. Use counts as feedback (ExecuteGraphInstance messages + GetNodeDataView
counts); Epic says take no screenshot loop unless asked. Take one screenshot at the end. Build the whole graph in one
`editor_toolset.toolsets.programmatic.ProgrammaticToolset.execute_tool_script` (tool names fully qualified,
`PCGToolset.PCGToolset.AddSubgraphNode`; args as `json.dumps`). Call `CreateGraph` directly first.
One graph per session unless asked; a graph needs ≥1 Spawn node to show anything.
Cleanup: `EditorToolset.LevelToolset.RemoveFromScene{actor: volume}` removes its spawned instances too;
`EditorToolset.AssetToolset.Delete{path}` removes the graph.
Older Ducky tools `pcg_get_graph_info` / `pcg_generate(force=true)` still regenerate an existing PCGComponent.

**Tested recipe (43.00): 20 m square of cubes with density + seed + spacing**

| node | subgraph | jsonParams |
|---|---|---|
| Shape | `/PCGPrimitives/Primitives/Create/Create_Spline_Shape.Create_Spline_Shape` | `{"width":2000,"length":2000,"linear":true}` |
| Fill | `…/Fill/Fill_Areas_Randomly.Fill_Areas_Randomly` | `{"pointsPerSquaredMeter":0.5,"samplingSeed":1234,"samplingPointExtents":{"x":50,"y":50,"z":50},"outputPointsExtents":{"x":50,"y":50,"z":50},"rotationRange":{"pitch":0,"yaw":180,"roll":0}}` |
| Assign | `…/Assign/Assign_Assets.Assign_Assets` | `{"assets":[{"refPath":"/PCG/DebugObjects/PCG_Cube.PCG_Cube"}],"matchScaleToInputBounds":true}` |
| NoOverlap | `…/Filter/Filter_Points_Overlapping.Filter_Points_Overlapping` | `{}` (spacing = point extents) |
| Spawn | `…/Spawn/Spawn_Assets.Spawn_Assets` | `{"seed":5641}` |

Wire Out→PrimaryInput in that order → SpawnGraphInstance at origin → Execute → **200 points, 115 spawned after the
overlap filter**. `UpdateNode{Fill, {"pointsPerSquaredMeter":0.1}}` → Execute → **40**.

### Route B: algorithmic placement

Two sub-routes:

**B1 — Precise (a few props):** compute positions, then `spawn_actor` per actor
with `check_area_clear` / `snap_actor_to_ground` / folders. Five or more actors →
B2's batch script instead.

**B2 — Large (cities, forests, thousands of props):** compute every position offline
into a plan file (seeded), then place it with **one Epic `execute_tool_script` per
batch of ~500–800 actors** (thousands of actors in a handful of batches). The script
tools read files only under `%LOCALAPPDATA%/UnrealEditorFortnite/Saved/`, so stage the
plan there. Greybox alternatives: `blockout_layout` / `area_create` / `pcg_generate` /
`foliage_scatter` with Content Drawer `_C` `sources=` from `foliage_list_sources`
(skip mesh / BakeData / HLOD hits). Never an `execute_python` spawn loop (freezes UEFN).
Cities, towns, villages, colonies, bases, ruins (any theme): `urban_procedural_city`.

Non-negotiables:

- **Deterministic seed.** Derive every position from an explicit seed the user
  can re-run (say the seed in your summary). Same seed → same level.
- **Validate the plan before placing** (overlaps, walkable gaps, budget). A bad
  plan means a new seed, not hand fixes in the level.
- **Clear the site first.** `check_area_clear` on the full footprint before bulk
  place.
- **Tag the generation**: every spawned actor gets a folder like
  `Generated/<name>_<seed>/...` + labels. Regenerate = census that folder, check
  nothing else references its actors (`get_verse_editables`, Verse tags), delete
  them with Epic `unreal__*` actor tools, then place the new seed. Foliage:
  `foliage_clear_generated` then re-scatter. Never regenerate on top of a
  previous run.
- **Count check:** actors placed per kind = plan count.
- **Never revive `spawn_actor_batch` / `batch_commands`.**

### Pattern cookbook (positions you compute)

- **Grid + jitter** — rows/cols at `spacing`, each offset by ±jitter (< 40% of
  spacing keeps rows readable). Streets/orchards/crates.
- **Scatter with min-distance** — random points, reject any closer than
  `min_dist` to an accepted point (track accepted list), then
  place survivors (B2 batch script; `spawn_actor` only for a handful).
- **Radial** — N points on a circle (angle = i·2π/N): arena cover, stone
  circles, spawn rings.
- **Path/corridor** — walk a polyline; place segments every `step`.
- **Rooms + corridors (dungeon)** — non-overlapping rectangles padded by wall
  thickness; door gaps ≥ 256 uu.
- **Maze** — generate on paper first (recursive backtracker on a cell grid,
  cell = 512 uu), then place wall pieces.

### Budgets & performance

- Set a **hard actor budget before generating** (density × area). Hundreds of
  actors: fine. Thousands of individual small props: editor pain — prefer bigger
  combined meshes or lower density.
- Spawn in modest passes and screenshot between passes when iterating by hand;
  for one-shot greybox, `blockout_layout` / `area_create` plus one screenshot
  is enough. Never a Python spawn loop.
- **Profile what PCG makes:** generate, then profile (uefn `profiling_mcp`: Timing Insights / Memory Snapshot /
  Spatial Profiler). If it is over budget, lower density or raise spacing with `SetGraphInstanceParams` (keep them
  exposed as graph params), run `ExecuteGraphInstance`, and profile again. Check the count with GetNodeDataView
  before raising density.

### Verify a generation

1. `get_level_bounds` — footprint sane, no runaway outliers.
2. Screenshot from 2–3 cameras plus one top-down.
3. Spot-check walkable gaps (≥ 256 uu where players pass).
4. `save_current_level()`.
