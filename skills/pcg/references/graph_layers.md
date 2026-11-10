---
description: "Building layered PCG graphs in UEFN by tool call (Epic PCGToolset): the data-flow order that works, surface and spline sampling, Transform Points, Bounds Modifier, Self Pruning, Difference (Binary) between layers and roads, district masks, graph parameters and instances, mesh weights, collision, the UEFN 43 traps, and the Road Network plugin's layer plans"
metadata:
  order: 7
  label: "Graph layers"
  default_enabled: false
  load_condition: "Building or editing a PCG graph by tool call: forests, rocks, grass, street trees, lamps, buildings along roads, several layers that must not overlap, or a Road Network PCG layer plan"
---

# Layered PCG graphs by tool call

PCG is **data transformation, not visual scripting**: points flow through nodes and each node filters or
changes them. Most broken graphs have the right nodes in the wrong order.

## The layer chain (every layer, in this order)

| # | Node | Why here |
|---|---|---|
| 1 | **Get Landscape Data** (scatter) / **Get Spline Data** (along roads) | The surface or path. The volume's bounds must overlap the landscape or nothing generates. |
| 2 | **Surface Sampler** / **Spline Sampler** | Makes the points. Surface: `pointsPerSquaredMeter` (density), `pointExtents` (bigger extents = fewer points), `looseness` 0..1 (0 = grid, values above 1 change nothing), `bUnbounded` (whole landscape, avoid). Spline: mode **Distance**, `distanceIncrement` cm. |
| 3 | **Transform Points** | Random yaw 0..360, scale range (min..max per axis, `bUniformScale`), **offset z negative** so roots and bases sink in (-10..-15 cm trees, -20..-100 rocks). `bAbsoluteRotation` keeps things upright on slopes. |
| 4 | **Bounds Modifier** (mode Scale) | The bounds are what pruning and differences see, not the mesh. Shrink to the trunk for trees (0.3–0.4), 0.6–0.8 for rocks. Lower values = more points, too low = overlaps. |
| 5 | District / area mask | See below. |
| 6 | **Difference** (Density Function **Binary**) | Removes points overlapping another set: the roads, or the *Bounds Modifier output* of a layer placed earlier (never its spawner: the spawner is visual only). One Difference per other set; chain them. |
| 7 | **Self Pruning** (`LargeToSmall`) | No overlaps inside the layer. Only works after 3 and 4: pruning before the transform prunes the wrong sizes. Prune early in the layer (after bounds) to keep point counts down. |
| 8 | **Static Mesh Spawner** | Weighted selector: one entry per mesh, `weight` = how often (5:2:1). Collision **NoCollision** for grass, saplings and any dense scatter (collision on dense scatter freezes the editor and stops players). Every material on a spawned mesh needs **Used with Instanced Static Meshes** (and Nanite if the mesh is Nanite): without it the instances draw the grey checker. FBX-imported materials are flat colours with the flag off; give the meshes instances of a world-aligned PBR master instead (City Builder: `road_network_kit_materials`). Through PCGToolset the selector is `{"meshSelector": {"meshes": ["/Path/SM_X.SM_X"]}}` (the default simple selector; `meshEntries` is refused). |

Difference before or after Self Pruning: before keeps more points, after keeps fewer. Either is valid;
be consistent. A Difference whose density function still shows Minimum after setting Binary: toggle the node
off and on (E) or re-set it with `UpdateNode`.

## Layers that respect each other

Place in order: trees → rocks (Difference vs trees) → grass (Difference vs trees and rocks) → street trees →
lamps (Difference vs street trees) → buildings. Every layer also subtracts the **roads**:

- **Get Spline Data** `{actorFilter: AllWorldActors, actorSelection: ByTag, actorSelectionTag: <tag>, bSelectMultiple: true}`.
  Tag the road actors first (`Tags` array). `bSelectMultiple` or only the first spline comes in.
- **Spline Sampler** Distance 200 → **Bounds Modifier** Scale `y 0.42`: landscape-spline samples carry the
  road width in their scale (scale.Y ≈ width / 2.4), so the true half-width ≈ scale.Y × bounds.Y × 0.42.
- Grow that by the clearance (another Bounds Modifier) and feed it to each layer's Difference `Differences` pin.
- Spline-only points (a PCG path) are 2 cm thin: give them width with Bounds Modifier and put them on the
  ground with **Projection** (`Projection Target` = Get Landscape Data, positions only) before using them.

## Along roads (street trees, lamps, buildings)

Spline Sampler (Distance = spacing) → **Transform Points absolute scale 1** (drop the road-width scale) →
two Transform Points with offset y = ±setback and yaw −90 / +90 (mesh front is +X, so it faces the road) →
**Merge Points** → **Projection** onto the landscape → zero pitch/roll (Attribute Maths Op Subtract
`$Rotation.Pitch` − itself) so they stand upright → Transform/Bounds/Difference/Prune/Spawn as above.
Junctions: landscape-spline junction pieces are control-point meshes, not actors; build their zones from
the road data (Create Points with ±radius bounds) and Difference them out.

## District masks

**Create Points** (World space, the outline corners) → **Create Polygon 2D** → **Intersection** (keep inside)
or **Difference** Binary (keep outside) against the layer's points **with tall bounds** (Bounds Modifier Set
z ±100000). A Polygon2D as Bounding Shape on a sampler returns 0 points in UEFN (it lies at z = 0). A ring band
(normal city between downtown and housing) = Intersection with the outer ring, then Difference the inner ring.

## Parameters (control from the level)

- Graph Settings → Graph Parameters → add one (float for multipliers, **SoftObjectPath Array** for mesh sets,
  Integer32 seed). In the graph: **Get Graph Parameter** → the *same-named pin* of the target node, never `In`.
- Scale multiplier: **Attribute Maths Op** Multiply, InA = `$Scale`, InB = the parameter, Output = `$Scale`.
- Mesh + weight from the level: a struct `{Mesh: StaticMesh object ref, Weight: float}` array parameter →
  **Match And Set Attributes** (match weight attribute = `Weight`) → spawner selector **By Attribute**, attribute
  `Mesh`. Names must match exactly.
- Expose anything else the same way (points per m², extents, looseness, unbounded as bool).
- **Graph instances** (Save Instance on the component) work like material instances: one graph, presets per
  instance (a forest instance, a rocks-only instance). `SpawnGraphInstance` + `SetGraphInstanceParams`.
- Debug: select a node + D shows its points (white = density 1), A inspects attributes and the point count.
  By tool: `GetNodeDataView` (call twice: the first arms inspection). If debug shows nothing, select the volume's
  PCG component once.

## Build it by tool (UEFN 43, Epic PCGToolset)

1. `unreal__describe_toolset("PCGToolset.PCGToolset")` once: read the argument names, never guess.
2. Tag the road actors (`<net>_roads`; the City network uses `CityRoads`).
3. `CreateGraph{name, path: <content_root>/WorldGen/PCG}`. The default `/Game/PCG` fails.
4. `AddNode` per node **in plan order** with all its settings in `jsonParams` (a JSON string, camelCase keys),
   `ConnectNodePins` per wire (`Out` → `In` / `Spline` / `Surface` / `Source` / `Differences` /
   `Primary Source` / `Projection Target`). Implicit converters (e.g. ToPoint after Intersection) are added for you.
5. `SetGraphParams` for the plan's params and wire each through a Get Graph Parameter node.
6. `SpawnGraphInstance{graph, name, transform: plan volume, jsonParams}` → use the returned actor ref →
   `ExecuteGraphInstance` (`[]` = success). Read counts with GetNodeDataView; report warnings, don't auto-fix.
7. Build the whole graph in one `ProgrammaticToolset.execute_tool_script` (5+ calls). Never touch the terrain.

## UEFN 43 traps (tested)

| Trap | Do this |
|---|---|
| `Place_OnSpline` primitive gives nothing on landscape splines (its Filter Data drops them) | Native **Spline Sampler** on Get Spline Data |
| Transform Points *relative* scale on spline samples does nothing | Absolute scale 1, then **Bounds Modifier** mode Scale |
| World Volumetric Query finds no road hits in the editor | Distance / Difference against sampled road points |
| Polygon 2D as Bounding Shape → 0 points | Intersection with tall-bounds points |
| Several volumes on one graph: Execute/DataView all at once freezes the editor | One actor at a time |
| Dense scatter with collision | NoCollision on grass / saplings / bushes |

## Road Network plugin

`road_network_pcg_plan(net_id)` returns this whole graph for a world's layers (nodes in order with settings,
wires, params, road tag, volume); `road_network_pcg_place(net_id, confirm=true)` starts a chat that builds it.
Layers live in the Road Network panel's PCG tab (`road_network_pcg_layer_save`).

## Linear Grammar tool (PCG Mode, spline)

Modules get symbols (A, B, or longer like BL); `Use Mesh Bounds as Module` separates them; untick `Scalable`
for fences. Syntax: `A,B` sequence · `A*` repeat to fill · `A+` at least once then fill · `[A]3` exactly 3 ·
`{A:1,B:3}` weighted random pick · `[A,B]*` repeat a group. Recipes: centred gate `A*,B,A*`; clean ends with
random middle `B,{A:1,C:2}*,B`; one hero `C*,[A],C*`; corners and tiles `[B],[A]3,[B]`; symmetry `A,B,C,B,A`;
rhythm `[A,A,B]*`.
