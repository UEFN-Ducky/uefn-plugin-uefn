---
description: "Step-by-step recipes to physically build with UEFN PCG Mode by mouse, each run and checked: curved roads with width classes (alley, street, highway), posts and fences, rock lines, filled areas, hand-placed objects, scatter strokes, volume fills, Blueprint prop rows, with the exact settings"
metadata:
  order: 2
  label: "Build recipes"
  default_enabled: false
  load_condition: "Building something real with PCG Mode: a road, highway, alley, fence, rail, rock line, row of lamps, forest patch, scatter, or filled volume"
---

## Build recipes

Use the helper and loop from `agent_driving`. Find every control by its label in a fresh capture.

Each recipe says what was run by mouse on UEFN. Test meshes were a 10 m road tile and a boulder.

### Every recipe starts

1. Deselect (`Escape`), frame the area.
2. Mode dropdown → **PCG**. Rail → category. Top row → the group button (this **already starts** its first tool and
   creates the actor).
3. Another tool in the group: press its button. Settings return to defaults on every new tool.
4. Draw Mode is remembered per group: the Draw Spline tools kept Click Auto Tangent while AreaTool was still on
   Free Draw. Read it every time.

### Road, highway, alley. Run: PASS

Spline → Draw Spline → **SplineMeshTool**.

1. Spawning → tick **Mesh** → dropdown → search the road tile → pick it.
2. Draw Mode → Click Auto Tangent. Click along the route: the curve passes smoothly through the points.
3. Sampling → tick **Resample Spline** and its value box; tick **Resample Distance** and type the tile's length
   (1000 for a 10 m tile). Without this each spline segment is one mesh stretched end to end with sharp corners.
4. Projection → tick **Snap to Surface** and its value box; tick **Snap to Surface Max Distance** → `5000`. Without
   this the road runs straight between points, through hills, and whole sections disappear underground.
5. Width: Global Transform → tick **Global Scale Factor** → second field (Y). `3` gave a highway three times as wide;
   under 1 for an alley. Keep X at 1 so the tile length still matches Resample Distance.
6. Sideways or stretched: Spawning → tick **Mesh Forward Axis** and try X, Y, Z. X was right for the test tile.
7. Accept → `Escape`.

Result: 5 clicked points, one continuous curved road over a hill, about 340 m long. Corner, T and cross tiles are
separate meshes: place those as single objects with PlaceTool where roads meet.

### Posts, lamps, fence. Run: PASS

Spline → Draw Spline → **SpacingTool**.

1. Spawning → tick Static Meshes → **+** → pick mesh.
2. Click the line. For an enclosure tick **Closed Spline**: the last point joins the first and objects go all round.
3. Sampling → tick **Use Distance Sampling Mode** and its value; tick **Distance** → gap in cm. 3000 gave a dense
   band of large objects, 6000 clear gaps. Count is ignored in this mode.
4. Tick **Fit to Curve** and its value: the gap stretches so the last object sits on the last point.
5. Accept → `Escape`.

A continuous fence or rail is the Road recipe with a fence section as the mesh.

### Rock line with variety. Run: PASS

SpacingTool as above, with a count instead of a distance.

1. Sampling → tick **Count** → type the number. 10 became exactly 4.
2. Random Transform → tick **Random Rotation Max** → third field `360`; tick **Random Scale Min** → `0.3` and
   **Random Scale Max** → `2` in the first field (Uniform stays on by default, so one field scales all axes).
3. Global Transform → **Global Scale Factor** for overall size. It multiplies with the random scale: 8 × 2 made
   house-sized boulders. Check after Accept, which can re-roll the random result.

### Filled area. Run: PASS

Spline → **Draw Spline Surface** → AreaTool.

1. Draw Mode → Click Auto Tangent. Click round the outline: 4 points closed themselves.
2. Spawning → mesh. Default 0.1 points/m² packed the outline solid.
3. Sampling → tick **Points Per Squared Meter** → `0.02` gave visible gaps.
4. Filtering, either: tick **Use Fixed Count Filter** and its value, tick **Fixed Count Filter** → exact number
   (12 left about a dozen); or tick **Probability Filter** → percent kept (30 kept about a third).
5. Random Transform and Projection as above.

Density is per square metre and outlines here are big: an 80 m square at 0.1 is over 600 objects. Start low.

### Hand-place objects. Run: PASS (placement; Accept not pressed)

Paint → **Paint** → PlaceTool. Spawning → mesh (add more with **+**; each click picks one by Weight). Click where
each should stand. Three clicks gave three rocks at the clicked spots.

### Scatter stroke. Run: PASS

Paint → Paint → **ScatterTool**. Spawning → mesh. Then `PStroke`: a relative drag left a trail of rocks along its
path. A teleported drag leaves one rock. Brush → Size widens the band (not run).

### Fill a box. Run: PASS, with a catch

Volume → **Volume** → ScatterTool.

1. Draw the box (`agent_driving`), then read Transform and Brush Settings in Details.
2. Spawning → mesh. Objects appear on every surface inside the box.
3. In the test the box sat above the ground and only rooftops inside it got rocks. Fix the height by typing in
   Details, or tick **Sample Landscape Only** (not run) to keep props clear.

### Row of Fortnite Blueprint props. Not run

Build a placeholder row, then swap. See `after_placing`. Prefer a static mesh when the prop needs no Blueprint
behaviour: it stays linked to the tool and costs less.

### After any build

`FindActors {"filter": {"name": "Tool Actor"}}`, a capture from a closer camera, then report tool, mesh, count or
density and seed. Saving is one save of the level, when the person wants it kept.
