---
description: "UEFN PCG Mode spline tools: Spacing Tool, Spline Mesh Tool and Area Tool, with every sampling, transform, projection, draw mode, raycast and draw target setting, shared by all spline tools"
metadata:
  order: 2
  label: "Spline tools"
  default_enabled: false
  load_condition: "Using the PCG Spacing, Spline Mesh or Area tool, or setting PCG spline draw mode, raycast rules, draw target, snap to surface or random transforms"
---

## Spline tools

### Spacing Tool: objects spaced along a line

Rock lines, posts, lamp rows. **Spawning → Static Meshes → +**, pick a mesh. Each element has a **Weight**:
with several meshes, a higher weight appears more often.

| Sampling | Effect |
|---|---|
| Count | Number of objects |
| Use Distance Sampling Mode + Distance | Spacing in units instead of a count |
| Fit to Curve | Stretches spacing so the last object lands on the spline's end |
| Start Offset / End Offset | Moves the first / last. Negative does nothing (can't leave the spline) |
| Max Random Offset | Jitter from the sample point |
| Sampling Seed | Which random result |

### Spline Mesh Tool: bends a mesh along the line

Roads, fences, rails. Deforms and connects the mesh instead of spacing copies. Free Draw works well for roads.

| Setting | Effect |
|---|---|
| Mesh | Mesh to bend. One mesh, not an array. Both rows start unticked |
| Mesh Forward Axis | Which axis runs along the spline. **Looks wonky → try each axis**; none work → fix the pivot in Modeling mode |
| Resample Spline + Resample Distance | **Needed for tiles.** Off: one mesh stretched per spline segment. On, with the tile's length (1000 for 10 m): the tile repeats at real size along a smooth curve |
| Fit to Curve | Mesh ends exactly at the spline's end |

### Area Tool: fills the inside of a closed shape

Rail **Spline → Draw Spline Surface → AreaTool**. Draw around the area. It closes itself, so there's no Closed Spline row.
BiomeSplineTool sits next to it; it wasn't in the source tutorial, so read its graph first.

| Sampling | Effect |
|---|---|
| Points Per Squared Meter | Density. **Keep it low** (0.1 is safe) unless spawning grass |
| Uniformity | High = on a grid, low = random |
| Point Size | Rarely needs changing |
| Sampling Seed | Random result |

| Filtering | Effect |
|---|---|
| Probability Filter | Percent of points kept (100 = all) |
| Use Fixed Count Filter + Fixed Count Filter | Exact number of objects |
| Filter Seed | Random result of the filter |
| Edge Falloff Size / Power / Filter | Thins points near the spline edge |
| Remove Overlapping Points, Use Mesh Bounds | Spacing by object size |

### Transforms and projection (every tool)

| Section | Effect |
|---|---|
| Global Transform | Same offset, rotation, scale on all points. Absolute Global Rotation ignores the point's own. On Spline Mesh, Global Scale Factor Y is the road width (3 = three times wider) |
| Random Transform | Min/Max per point. 360 on rotation = fully random. **Uniform Random Scale Factor** on = even scale; off = each axis apart |
| Snap to Surface | Drops each point to the nearest surface. **Needed for roads on hills**: without it the mesh runs straight between points and goes underground |
| Snap to Surface Max Distance | How far it searches. **0 = no snap**; raise it until points land |
| Align to Surface | Rotates to the surface. **Overrides your rotations**, so usually leave it off |

**Order trap:** snapping runs after the transforms. Points buried under the ground won't snap up, so add a
positive Z in Global Position Offset to lift them above the surface first. Rotation can't be applied after
snapping in the prebuilt tools; that takes a custom graph.

### Spline settings (every spline tool)

| Setting | Effect |
|---|---|
| Closed Spline | Joins last point to first |
| Draw Mode | **Free Draw**: hold and drag. **Click Auto Tangent**: each click adds a point, tangents automatic (best for agents). **Tangent Drag**: click and drag sets each tangent |
| Min Point Spacing | Free Draw only, default 200. Higher = smoother, less sensitive. The row disappears in Click Auto Tangent |

### Raycast: what a click hits

**Raycast Rules** rows: Landscape, Meshes, Ignore PCG Components, each with an on/off. **Hit Ground Planes** is
separate. Landscape off → the ray hits whatever else is on, such as the ground plane.

### Draw Target: where the point goes

| Setting | Values |
|---|---|
| Offset Mode | Hit Location (default), Explicit (fixed offset), Distance (along the hit normal) |
| Normal Mode | Hit Normal (default), World Up, Align to Previous, Explicit. Matters because a mesh faces the spline's direction |
