---
description: "UEFN landscape spline road design rules: how few control points to use (ends, junctions, curves, slope changes only), road meshes and their axis, road materials that actually show on spline meshes, live terrain through the Splines edit layer (never bake), and the tested generate-and-paste recipe for whole road networks"
metadata:
  order: 7
  label: "Landscape spline roads"
  default_enabled: false
  load_condition: "Building roads, paths, rivers or rails with Landscape Splines (Landscape Mode > Manage > Splines), generating a road network from a plan, or roads that look wrong, show grey, float, sink or slow the editor"
---

## Landscape spline roads — design rules

Tested in UEFN on a 3.9 km island with ~90 km of road.

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

### 2. Terrain: live splines through the Splines edit layer only (HARD)

The landscape has a base edit layer (usually **Layer**) and a reserved **Splines** layer
(`LandscapeEditLayerSplines`, "This layer is reserved for Landscape Splines"). Control points and segments with
**Raise Terrain / Lower Terrain** on write into that reserved Splines layer, procedurally: move a point by hand
and the ground follows, exactly like a spline drawn in the editor.

| Want | Do |
|---|---|
| Road shapes the terrain (flattened road bed) | Raise/Lower **on** on points and segments, Side Falloff 25-40 m, End Falloff 20 m |
| Road drapes on the ground, terrain untouched | Raise/Lower **off** |

- **Never write the terrain yourself:** no `Landscape.editor_apply_spline`, no road-bed bakes into the base
  Layer, no heightmap imports or despike patches. A bake is baked forever: the roads can no longer be moved,
  and wherever beds overlap or end it leaves cliffs.
- The landscape needs a **Splines** edit layer for live roads to deform anything. With only the base Layer, a
  live paste changes nothing. Add it: Landscape > Manage > Edit Layers, the **+** next to "N Edit Layers" >
  **Landscape Edit Layer Splines** > Select (the picker can open off-screen). Every live spline already in the
  level then writes into it, with no re-paste. Ctrl+clicking a spline point does not create the layer.
- Heights: set each point Z about 40 cm under the road surface and lift the mesh with **Mesh Vertical Offset**
  (50 cm), so the bed sits under the asphalt and grass cannot poke through.

### 3. Junctions: one connected network with real T / + pieces (HARD)

Roads that only overlap at a crossing are not connected. Build the network as **one graph**:

1. **Snap ends:** union every road end within ~12 m of another into one node. Split a road where another road
   ends on its middle. Merge two junctions whose linking road is shorter than their two piece sizes plus 4 m,
   and drop that road; otherwise the pieces overlap.
2. **Pick the piece by degree:** 3 arms = `_T`, 4 or more = `_Cross` of the widest arm's family
   (FourLane / TwoLaneSidewalk / TwoLane). No Y piece exists: a Y uses a T turned to fit. Freeway arms use the
   FourLane piece with MeshScale 1650/1400.
3. **Orient it:**
   - Through road = the two most opposite arms, laid along local X.
   - The kit T has its stem on local **+Y** (TwoLane_T bounds are y -525..825). Flip yaw by 180° when the stem
     arm points to -Y.
   - For a Cross, give each arm the nearest free axis (±X, ±Y).
4. **Paste:**
   - The junction control point carries the piece: `Mesh="/Script/Engine.StaticMesh'…_T.…_T'"`, `MeshScale=(…)`,
     `Width` = half the piece size.
   - Each arm ends at a **mouth** point (centre + axis × half size), rotated along that axis.
   - **No lead-in points.** The road runs from mouth to mouth as ONE segment. Its end tangents (the mouth's
     rotation, TangentLen = the chord) already make it enter each junction square. Add a point between two
     mouths only where the spline drawn mouth to mouth would leave the planned road by more than ~50 cm
     (a real bend) or cut/fill more than ~1.5 m (a slope change).
   - Join each mouth to the junction point with a segment that has **no** `SplineMeshes`. That segment only joins
     the graph and draws nothing.
   - Check that a flood fill over points and segments finds exactly **one** connected piece.
5. **Tangent sign:** per segment, `TangentLen` = +L at the start if the point's forward faces along A→B, else -L.
   At the end it is -L when forward faces along A→B, else +L. This lets any point face either way.

Junction points keep Raise/Lower **on** like the roads, so the Splines layer flattens the ground under the piece
too (give the piece mesh a ~50 cm lift so grass stays under it).

Tested: 1,018 roads and 559 junctions (T 327, Cross 232) in one connected graph, 5,750 points.

**Every junction type: generate a fitted piece per node.** Kit T/Cross pieces only fit 90° junctions of a
single width. For Y, 5-6 way, mixed widths, width changes and cul-de-sacs, build each node's own mesh in UEFN with
GeometryScript. No files are needed:

1. **Layout:** sort the arms by angle. For each pair of neighbouring arms, fit a kerb corner between arm i's left
   edge and arm j's right edge:
   - fillet arc (R = sidewalk width + 2 m, at least 6 m) for 15-165°;
   - straight taper for about 180° (width change);
   - round bulge for reflex angles.
   - Mouth distance = the larger of the two corner tangent points + 4.5 m crosswalk.
   - Cap the mouths at (road length - 12 m)/2; if they don't fit, shrink R and the crosswalk.
2. **Mesh:**
   - Asphalt is a fan from the centre over the boundary (mouth edges + corners).
   - Kerb 30 cm (z 17), pavers (z 16) and outer kerb 20 cm run along each corner, with widths blended between the
     two arms' sidewalk widths.
   - Crosswalk stripes go at each mouth, and skirts run down to -40.
   - The mouth cross-section equals the kit tile's (asphalt half width, sidewalk), so the road tile butts on exactly.
3. **Asset:**
   - `DynamicMesh` + `GeometryScript_Materials.enable_material_i_ds` + `GeometryScript_MeshEdits.append_buffers_to_mesh(dm, buffers, material_id)`
     for each material, then `GeometryScript_NewAssetUtils.create_new_static_mesh_asset_from_mesh`.
   - Rebuild in place later with `GeometryScript_AssetUtils.copy_mesh_to_static_mesh_v2`.
   - **Winding:** an upward face needs **clockwise** order seen from above (x right, y up). Vertical faces are emitted both ways.
   - Give every mesh all material IDs (a 1 cm hidden triangle for any that are missing), so slot index = material.
     Then set materials in the paste text: `MaterialOverrides=("/Script/Engine.Material'…M_Asphalt'", …)` on the junction
     control point. The slots come out unnamed, so Epic SetMaterial (by slot name) cannot target them.
4. **Graph merging:**
   - Merge two junctions only when the link between them is under 15 m, or when it is shorter than both pieces
     and the result has 6 arms or fewer.
   - Unlimited merging cascades into 10-18 arm blobs.
   - Re-check, and hand-fix what is left.

Tested: 564 fitted pieces (287 three-way, 188 four-way, 28 five-way, 14 six-way, 38 corners or width changes,
9 cul-de-sacs). Building all of them takes about 6 s.

**Kit pieces on the network (cloverleaf, loop, bridge):**
- **Cloverleaf / loop:**
  - Put the kit mesh on one control point (`Mesh`, `MeshScale`, Rotation yaw), with no MaterialOverrides because the
    asset already has its materials.
  - Read the mesh's open ends from its vertices: the bbox faces give each end's centre, width and height. The kit
    cloverleaf ends at ±23000 and is 43.2 m wide; scale it 0.764 in XY for a 33 m freeway. The loop's ends are offset
    9.6 m sideways: rotate it so the line between its two ends follows the road.
  - Each arm road starts at its end (no lead-in point; the end tangent keeps it square), plus a mesh-less link to the piece's point.
  - Follow each freeway outward through every junction inside the footprint, join those roads into one arm, and
    end it at the first junction outside. Then drop the other roads inside. Dropping every road that touches the
    footprint cuts the freeway off just beyond the piece.
  - Choose the site by relief: a 470 m cloverleaf on 90 m of relief makes cliffs whatever you do; 36 m blends in.
- **Bridge (overpass):**
  - Take the crossing road off the junction and leave the freeway running through as a plain point.
  - Lay the crossing road as one straight spline with segments of exactly the tile lengths: `Bridge_Ramp40m`, then
    n × `Bridge_Straight20m`, then `Bridge_Ramp40m` with its connections reversed so the ramp's x=0 sits on the ground.
  - Keep every point at ground height: the meshes carry the rise.

### 4. Road meshes

- The tile's **length must run along X**; landscape splines and PCG Spline Mesh both lay a mesh along X by default.
  A tile with its length on Y stands on its edge like a wall. Check every new road from a **low oblique** camera:
  from straight above, a sideways road looks like a thin correct line.
- `bScaleToWidth=False` keeps the modelled width. Give the control point `Width` = half the road width.
- Kit FBX in metres import 100× small: convert to cm first (Blender headless, scale 100, export
  axis_forward -Y, up Z, FBX_SCALE_NONE). `EditorToolset.StaticMeshToolset.GetBounds` must show real cm.

### 5. Materials that show

- Spline meshes render the grey default unless every material on the mesh has **Used with Spline Meshes** on
  (`material.set_editor_property('used_with_spline_meshes', True)` + recompile). `MaterialEditingLibrary.set_material_usage`
  did not stick.
- A mesh with **no UV layer** cannot show its baked textures: use flat colour/roughness materials or re-export with UVs.
- Assign mesh slot materials with `EditorToolset.StaticMeshToolset.SetMaterial` (Python material assignment is
  blocked in Ducky).

### 6. Generate and paste a whole network

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
- A bare shared control point can only face one road, so the other roads bend near it. Use the junction
  recipe in section 3 (a piece on the node and a mouth point for each arm), never a bare shared point and never overlapping roads.
