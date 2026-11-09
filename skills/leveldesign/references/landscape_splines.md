---
description: "UEFN landscape spline road design rules: how few control points to use (ends, junctions, curves, slope changes only), road meshes and their axis, road materials that actually show on spline meshes, which edit layer shapes the terrain, and the tested generate-and-paste recipe for whole road networks"
metadata:
  order: 7
  label: "Landscape spline roads"
  default_enabled: false
  load_condition: "Building roads, paths, rivers or rails with Landscape Splines (Landscape Mode > Manage > Splines), generating a road network from a plan, or roads that look wrong, show grey, float, sink or slow the editor"
---

## Landscape spline roads — design rules

Tested in UEFN 43.00 on a 3.9 km island with ~90 km of road.

### 1. Control points: as few as possible (HARD)

A segment between two control points is a smooth curve, and its mesh repeats along it by itself. Points are
only for **shape**, never for spacing.

| Put a point | Why |
|---|---|
| Both ends of a road | Required |
| Every junction where another road joins | Roads meet at a shared point |
| Curves: one per 15-20° of turn | A 90° corner = 4-6 points; tangents round it in between |
| Where the ground slope changes | Only if the straight segment would sink into or float above the terrain by more than ~30 cm |

**Never** a fixed spacing (every 10-20 m). A straight flat road is **two points**. Dense points cost a lot: one
traced city with a point every 15-20 m came to 7,626 points, 8,809 mesh components and 4 MB clipboard pastes.

Thinning recipe: Douglas-Peucker the road polyline in plan (0.5-1 m tolerance), then sample the ground along
each remaining segment and split it only at the worst spot while it is off by more than the limit.
Tangent length on both connections of a segment = the segment's length (`TangentLen=+L` / `-L`).

### 2. Terrain: which layer the road shapes

The landscape has a base edit layer (usually **Layer**) and a reserved **Splines** layer
(`LandscapeEditLayerSplines`, "This layer is reserved for Landscape Splines"). Control points and segments with
**Raise Terrain / Lower Terrain** on always write into that reserved Splines layer.

| Want | Do |
|---|---|
| Road drapes on the ground, terrain untouched | Raise/Lower Terrain **off** on points and segments |
| Road shapes the terrain (flattened road bed) through the Splines layer | Raise/Lower **on**, Side Falloff 5-15 m, End Falloff 10-20 m |
| Road shapes the **base Layer** itself | Splines keep Raise/Lower **off**; bake each road into the base layer with `Landscape.editor_apply_spline(spline_component, start_width, end_width, start_side_falloff, end_side_falloff, ..., raise_heights=True, lower_heights=True, edit_layer_name="Layer")` |

Ask the person which one before shaping terrain: it changes the heightmap under every road.

**Bake into the base Layer (tested recipe):**

1. `editor_apply_spline` needs a plain `SplineComponent`. Add one temporary actor with Epic
   `EditorToolset.LevelToolset.AddToSceneFromClass` (`actorType={refPath:"/Script/Engine.Actor"}`), then
   `EditorToolset.ActorToolset.AddComponent` (`componentType={refPath:"/Script/Engine.SplineComponent"}`).
   Python spawning and `SubobjectDataSubsystem` are blocked in Ducky.
2. Per road: `sc.set_spline_points([Vector(x,y,ground_z)...], WORLD, True)` (closed loops: `set_closed_loop(True)`),
   then `landscape.editor_apply_spline(sc, half_width+100, half_width+100, falloff, falloff, 0, 0, subdivisions, True, True, None, "Layer")`.
   Widths are **half** widths. Subdivisions about one per 10 m (4-60). About 1,100 roads bake in under a second.
3. Bake small roads first and freeways last: a later bake wins where roads cross.
4. Collision updates one Python call later. Trace the result in a **separate** call; in the same call it still
   reads the old heights.
5. Delete the temporary actor, then paste the spline actor with Raise/Lower **off** and the point Z set to the baked heights.

Checked on 60 random roads: the centre matches the spline Z to about 1 cm and the bed is flat across its width.
The only outliers are crossings at different heights.

Heights: set each control point Z to the ground, not above it. If the terrain is flattened to the road, lift the
mesh with **Mesh Vertical Offset** (10-20 cm) instead of the point, so grass cannot poke through.

### 3. Road meshes

- The tile's **length must run along X**; landscape splines and PCG Spline Mesh both lay a mesh along X by default.
  A tile with its length on Y stands on its edge like a wall. Check every new road from a **low oblique** camera:
  from straight above, a sideways road looks like a thin correct line.
- `bScaleToWidth=False` keeps the modelled width. Give the control point `Width` = half the road width.
- Kit FBX in metres import 100× small: convert to cm first (Blender headless, scale 100, export
  axis_forward -Y, up Z, FBX_SCALE_NONE). `EditorToolset.StaticMeshToolset.GetBounds` must show real cm.

### 4. Materials that show

- Spline meshes render the grey default unless every material on the mesh has **Used with Spline Meshes** on
  (`material.set_editor_property('used_with_spline_meshes', True)` + recompile). `MaterialEditingLibrary.set_material_usage`
  did not stick.
- A mesh with **no UV layer** cannot show its baked textures: use flat colour/roughness materials or re-export with UVs.
- Assign mesh slot materials with `EditorToolset.StaticMeshToolset.SetMaterial` (Python material assignment is
  blocked in Ducky).

### 5. Generate and paste a whole network

1. Build the road polylines (from a traced plan, a layout, or a graph), thin them by rule 1.
2. Write the clipboard text:
   - `BEGIN_SPLINES`, then `SPLINE LOCATION: X=0 Y=0 Z=0` with **absolute** point locations.
   - Per point: `Begin Object Class=/Script/Landscape.LandscapeSplineControlPoint Name="LandscapeSplineControlPoint_N"`,
     `Location`, `Rotation=(Pitch,Yaw,Roll=0)`, `Width`, `SideFalloff`, `EndFalloff`, `bRaiseTerrain`, `bLowerTerrain`, `End Object`.
   - Per segment: `Connections(0)=(ControlPoint="/Script/Landscape.LandscapeSplineControlPoint'LandscapeSplineControlPoint_A'",TangentLen=L)`,
     `Connections(1)=(...'_B'...,TangentLen=-L)`,
     `SplineMeshes(0)=(Mesh="/Script/Engine.StaticMesh'/<mount>/.../SM_Road.SM_Road'",bScaleToWidth=False)`, the same two flags.
   - `END_SPLINES`. Names only, no `ExportPath`.
3. Put it on the clipboard as UTF-16 (`subprocess.run(['clip'], input=text.encode('utf-16le'))` from the listener).
4. Landscape Mode > Manage > **Splines**, hover the viewport, Ctrl+V. Each paste makes one `LandscapeSplineActor`.
   Paste one road class at a time.
5. Check: count `SplineMeshComponent`s per actor, then a top-down and a **low oblique** capture.

Copy an existing spline to learn the exact format: select its points or segments (Splines tool > Points /
Segments), Ctrl+C over the viewport, read the clipboard.

### Traps

- The viewport only redraws after UEFN has focus and the mouse moves over it.
- Do not click the viewport while Landscape **Sculpt** is active: it sculpts.
- Ground heights from Python: `unreal.SystemLibrary.line_trace_single(world, (x,y,60000), (x,y,-20000), TRACE_TYPE_QUERY1, False, ignore, NONE, True)`.
  Traces hit cars, props, buildings and road meshes too. Keep only the landscape: if the hit actor's class
  is not a `Landscape*`, add it to `ignore` and trace again. `line_trace_multi` stops at the first blocking
  hit, so it does not help here.
- Traced plans often draw roads through a spot the person wants kept (a cinema, a plaza). Clip every polyline
  at that keep-out box, then join the new dead ends to a ring road with short spokes.
- At a junction, a shared control point can only face one road, so the other roads bend near it. Leave
  crossing roads as separate overlapping points unless the roads continue straight through.
- Junctions: crossing roads overlap; place Cross/T tiles or end both roads on a shared point.
