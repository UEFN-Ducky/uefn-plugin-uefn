---
description: "LEGO® Brick Editor (v42.40) — the UEFN editor mode for building brick-by-brick LEGO static meshes: Brick Gallery, colors, Snap / Kragle / Separate, 16-unit snapping, no scaling or material changes, memory and triangle rules, what agents can and can't do with MCP, 42.40: 50 new bricks, brick-type categories, LOD, primitive bricks change type when Kragled"
metadata:
  order: 15
  label: "LEGO Brick Editor (v42.40)"
  default_enabled: false
  load_condition: "LEGO islands, the LEGO Brick Editor, building with LEGO bricks, Kragle / kragled meshes, Separate, brick colors or the brick index"
---

# LEGO® Brick Editor

An editor **mode** (toolbar *Selection Mode* → **LEGO® Brick Editor**, or **Shift+6**)
for building your own LEGO static meshes from a fixed gallery of bricks. Works on islands
made from a LEGO template (Project Browser → Brand Templates). Practice island: the
**LEGO Brick Editor Template** (four building challenges).

## What agents can do

The mode is driven by hand in its left-hand panel; no MCP tool or Epic toolset drives
it (42.40 toolsets checked live). Agents can:

- explain the steps below and what to click;
- place a **kragled** mesh like any static mesh (`spawn_actor` with its asset path, or
  a `mesh_component` in Scene Graph) and read it with `get_static_mesh_info`;
- never scale it or swap its material — project validators reject both.

## The panel

| Section | What it does |
| --- | --- |
| Tools | **Snap** (bricks snap with the chosen Snap Mode), **Kragle** (glue the selected bricks into one optimized static mesh), **Separate** (unglue a kragled mesh back into bricks to edit it) |
| Brick Color | Active color, **Read Brick Color** (copy from a selected brick), **Apply Brick Color** (paint the selection). A placed brick's color is also in Details |
| Brick Search and Index | Every available brick; search by name. **42.40:** the library is grouped into categories by brick type |

Rules: only the preset LEGO colors, no material changes, **no scaling** (studs and tubes
must line up). Duplicate a selection with **Ctrl+D**. Double-click selects a brick and
everything stud-connected to it.

## Building

1. Pick a color, drag a brick from the gallery into the viewport, repeat.
2. Set UEFN **Snapping Location to 16** — bricks snap in multiples of 16 on the stud grid.
   While the mode is on, the usual Snap toggle, Snap to Grid, preset angles and scale
   ratios are unavailable; the magnet icon / Mesh Element Selection settings hold
   *Click to End Drag*, *Enable Edge Snapping*, *Max Snapping Distance*, *Single Field
   Placement*.
3. Rotate with the mode's own gizmo (90° steps; the yellow diamond shows the pivot at the
   nearest connection point). Gizmos outside the mode don't keep LEGO connectivity.
4. Bricks only connect on top of each other and can't intersect. Can't snap → check for
   something in the way, or leave and re-enter the mode.

## Kragle and Separate

- Kragle the selection (snapped or just nearby) into one static mesh; meshes collect in
  the Content Browser. Big structures take a while.
- Kragle in pieces: walls, floors, roofs as reusable meshes. A kragled mesh repeated
  costs nothing extra; one huge kragle costs more memory than loose bricks and hides
  interior triangles it thinks you can't see — don't kragle spaces players walk inside
  as one mesh.
- Kragling on top of an existing kragled mesh updates **every** instance of it.
- Undo returns the bricks but not the mesh changes.
- Pivot = bottom center. Changing the pivot (Modeling Mode → Edit Pivot) or the collision
  is allowed but lost on re-kragle; keep LEGO/LEGO interpenetration detection intact.
- To recolor a kragled build: Separate, recolor, Kragle again.
- **42.40:** a primitive brick pulled straight from the library turns into a different
  brick type once it is Kragled; a wider LOD system renders large builds faster.

## Limits

- Not usable with the **Assembly** device (that needs geometry collections; kragled
  builds are static meshes) and not destructible — for "breaks on hit" use the Adventure
  Template's approach (hide the prop, spawn studs).
- Kragled meshes work in Building Prop / Building Static Mesh actors and Scene Graph
  `mesh_component`s (same rules; overlap isn't validated there yet).
- Gallery items from the existing LEGO content gallery don't connect to editor bricks.
- Known issues: slow viewport while dragging complex builds (precise collision — it can be
  turned off in the toolbar, at the risk of invalid placements); the overlap validator can
  flag kragled meshes whose simplified collision cuts through empty space — split the mesh.
- Brick-built data is editor-only but makes files bigger on disk.

**42.40:** 50 new bricks (decorative and small-scale detail pieces).
