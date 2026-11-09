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
   - Add a straight **lead-in** point ~9 m out on the same axis, so the road enters square instead of bending at the kerb.
   - Join each mouth to the junction point with a segment that has **no** `SplineMeshes`. That segment only joins
     the graph and draws nothing.
   - Check that a flood fill over points and segments finds exactly **one** connected piece.
5. **Tangent sign:** per segment, `TangentLen` = +L at the start if the point's forward faces along A→B, else -L.
   At the end it is -L when forward faces along A→B, else +L. This lets any point face either way.

Baking those roads into the terrain:
- The temporary `SplineComponent` must use the **same tangents** as the pasted segments:
  `set_tangents_at_spline_point(j, fwd*L_prev, fwd*L_next)`, where fwd is the point's Rotation vector including pitch.
  With automatic tangents the bed and the road sag differently on slopes, and dirt shows through the asphalt.
- Bake the bed **~45 cm below** the road surface, with the flat width equal to the road half width. Landscape grass
  is taller than a road mesh: if the bed sits right at road height, grass grows through the asphalt.
- Bake a flat pad under each junction last: two straight splines along its X and Y axes at the node height.

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
  - Each arm road starts at its end with a 9 m straight lead-in, plus a mesh-less link to the piece's point.
  - Follow each freeway outward through every junction inside the footprint, join those roads into one arm, and
    end it at the first junction outside. Then drop the other roads inside. Dropping every road that touches the
    footprint cuts the freeway off just beyond the piece.
  - Choose the site by relief: a 470 m cloverleaf on 90 m of relief makes cliffs whatever you do; 36 m blends in.
- **Bridge (overpass):**
  - Take the crossing road off the junction and leave the freeway running through as a plain point.
  - Lay the crossing road as one straight spline with segments of exactly the tile lengths: `Bridge_Ramp40m`, then
    n × `Bridge_Straight20m`, then `Bridge_Ramp40m` with its connections reversed so the ramp's x=0 sits on the ground.
  - Keep every point at ground height: the meshes carry the rise.
- **Flat pads: `editor_apply_spline` blends only at the spline's sides, never at its two ends.** A flat strip ends in a
  vertical wall. Extend each pad strip 150 m past the pad, with its end points at real ground height, so it ramps down.
  A wider side falloff alone does not help, and re-baking over an old cliff keeps the cliff: re-import the clean
  heightmap first.

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
  recipe in section 3 (a piece on the node, a mouth point and a lead-in for each arm), never a bare shared point and never overlapping roads.
