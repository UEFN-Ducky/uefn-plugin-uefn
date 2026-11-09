---
description: "Step-by-step recipes to physically build with UEFN PCG Mode by mouse: rock lines, roads, fences and rails, posts and lamps, filled areas, hand-placed trees and rocks, volume fills, Blueprint prop rows, with the exact settings and checks for each"
metadata:
  order: 2
  label: "Build recipes"
  default_enabled: false
  load_condition: "Building something real with PCG Mode: a road, fence, rail, rock line, row of lamps, forest patch, scatter, or filled volume"
---

## Build recipes

Use the helper and loop from `agent_driving`. Find every control by its label in a fresh capture.

**Partly tested** names which steps ran by mouse; the rest follow the tutorial. **Same steps, untested** means the tool
opened and its panel was read but the recipe's result was not produced.

### Every recipe starts

1. `select_actors(actor_paths=[])`, frame the area with `set_viewport_camera`.
2. Mode dropdown → **PCG**. Rail → category. Top row → the group button (this **already starts** its first tool and
   creates the actor).
3. Different tool in the group: Cancel first, then press it. Settings return to defaults on every new tool. Draw Mode
   can carry over between tools in a group: read it, don't assume.

### Rock line. Partly tested (steps 2, 7 with a Free Draw line; step 1 and 3 drew and were canceled)

Spline → **Draw Spline** → SpacingTool.

1. Draw Mode → **Click Auto Tangent**.
2. Spawning → tick Static Meshes → **+** → pick mesh.
3. Click the points along the line.
4. Sampling → tick the row you change → **Count**, or **Use Distance Sampling Mode** + **Distance**.
5. Random Transform → tick Random Rotation Max → Z `360`; tick Random Scale Min/Max → e.g. `0.8` / `1.3`.
6. Projection → tick Snap to Surface and raise its Max Distance if rocks float.
7. Accept → deselect.

Result in the test, steps 4 to 6 skipped: 8 boulders (default count), one ISM.

### Road. Same steps, untested

Spline → Draw Spline → **SplineMeshTool**.

1. Spawning has **Mesh** (one mesh, no array) and **Mesh Forward Axis**. Tick each one's checkbox.
2. Mesh → search `road` → pick a straight piece.
3. Draw Mode → Click Auto Tangent. Click along the route.
4. Check the preview. Stretched or sideways → Mesh Forward Axis: try X, then Y, then Z.
5. Sampling → Resample Spline + Distance for smoother corners; Fit to Curve so it ends at the last point.
6. Projection → Snap to Surface so it follows the ground.

### Fence or rail. Same steps, untested

Same as Road with a fence or rail section. For separate upright posts, use the Rock line recipe with Random Transform off
and **Use Distance Sampling Mode** at the post gap, plus **Fit to Curve**. Tick **Closed Spline** for a full enclosure.

### Filled area. Same steps, untested

Spline → **Draw Spline Surface** → AreaTool.

1. Draw Mode → Click Auto Tangent. Click round the outline, 4+ points. The shape closes itself (no Closed Spline row).
2. Sampling → **Points Per Squared Meter** `0.1` to start, Uniformity low for natural spread.
3. Filtering → **Probability Filter** to thin, or **Use Fixed Count Filter** for an exact number. **Edge Falloff** thins borders.
4. Spawning, Random Transform as above.
5. Projection → Snap to Surface. Points under the ground need a positive Global Position Offset Z first.

Watch the count: density is per square metre, and this island is big. Raise it in small steps.

### Hand-place trees or rocks. Partly tested (placement ran; Accept not pressed)

Paint → **Paint** → PlaceTool.

1. Spawning → tick Static Meshes → **+** → pick mesh. Add more with **+**; each click picks one by Weight.
2. Click where each should stand. Accept.

Three clicks gave three rocks at the clicked spots.

### Fill a box. Partly tested (step 1 only; canceled before spawning)

Volume → **Volume** → ScatterTool.

1. Draw the box (`agent_driving`). Details → **Brush Settings X/Y/Z** and Transform Location give exact numbers; edit
   them for precise sizing.
2. Sampling → Points Per Squared Meter `0.1`.
3. Spawning → mesh. **Sample Landscape Only** if props inside must stay clear.
4. Accept. The box must overlap the surface.

### Row of Fortnite Blueprint props

Build the placeholder row, then swap. See `after_placing`. Prefer a static mesh of the same prop when it doesn't need
Blueprint behaviour: it stays linked to the tool and costs less.

### After any build

`get_all_actors(label_filter="PCG")`, a capture from a closer camera, then report tool, mesh, count or density and seed.
Saving is one `save_current_level`, when the person wants it kept.
