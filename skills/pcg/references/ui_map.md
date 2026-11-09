---
description: "Where everything is in UEFN PCG Mode, checked live: mode menu, Shift+7, the Spline / Paint / Volume / Query / Manual rail, every tool button per group, each tool's settings sections in order, Accept / Cancel bar, Details panel and reference pixel positions"
metadata:
  order: 3
  label: "PCG Mode UI map"
  default_enabled: false
  load_condition: "You need to find, click or point at a button, tab, section or setting in UEFN PCG Mode"
---

## PCG Mode UI map

### Open it

Toolbar, top left: the **mode dropdown** shows the current mode (*Selection Mode*, *Landscape Mode*, *PCG Mode*). The menu
lists Selection, Landscape, Foliage, Modeling, Animation, Fortnite Tools, PCG (Shift+1 to Shift+7). A tool panel opens at the
left. Leave by choosing another mode.

### Layout

| Area | Where |
|---|---|
| Category rail | Far left column: **Spline, Paint, Volume, Query, Manual** |
| Group buttons | Top of the panel |
| Tool buttons | Below them, two columns |
| Settings | Below, scrolls. A scrollbar appears when it overflows and narrows the columns |
| Accept / Cancel bar | Bottom centre of the viewport. Label reads DrawSpline, PaintTool or Volume |
| Details | Right side, shows the new actor as soon as a tool starts |

### Tools

Pressing a group button immediately starts its first tool.

| Rail | Group | Tools (button text) | Graph |
|---|---|---|---|
| Spline | Draw Spline | **SpacingTool** (starts first) | `/PCG/EdMode/DrawSpline/SpacingTool` |
| | | SplineMeshTool | `/PCG/EdMode/DrawSpline/SplineMeshTool` |
| | | LinearGrammarTool | `/PCG/EdMode/DrawSpline/LinearGrammarTool` |
| | | SpacingTool_Custom | not under `/PCG/EdMode` |
| | Draw Spline Surface (`Draw Spline...`) | **AreaTool** (starts first) | `/PCG/EdMode/DrawSplineSurface/AreaTool` |
| | | BiomeSplineTool (`BiomeSpline...`) | not under `/PCG/EdMode` |
| Paint | Paint | **PlaceTool** (starts first) | `/PCG/EdMode/Paint/PlaceTool` |
| | | LayeredPlaceTool | `/PCG/EdMode/Paint/LayeredPlaceTool` |
| | | ScatterTool | not found under `/PCG/EdMode/Paint` |
| Volume | Volume | **ScatterTool** (starts first) | `/PCG/EdMode/Volume/ScatterTool` |
| | | BiomeVolume | not under `/PCG/EdMode` |

Two tools are called ScatterTool. Name the category too.

### Settings order per tool

Each starts with **PCG → Tool Graph** and **Parameters Overrides**.

| Tool | Overrides, in order | Then |
|---|---|---|
| SpacingTool | Sampling, Spawning, Global Transform, Random Transform, Projection | Data Instance, Actor Label, Component Name, Actor Class to Spawn, Spline, Raycast, Draw Target |
| SplineMeshTool | **Spawning, Sampling**, Global Transform, Projection | Same |
| AreaTool | Sampling, Filtering, Spawning, Global Transform, Random Transform, Projection | Same, no Closed Spline row |
| PlaceTool | Spawning, Global Transform, Random Transform, Debug | Data Instance, labels, **Paint**, Raycast, **Brush** |
| Volume ScatterTool | Sampling, Filtering, Spawning, Global Transform, Random Transform, Projection, Debug | Data Instance, Actor Label, Actor Class, Raycast only |

Rows are grey until the checkbox at their left is ticked. Closed sections open on the small arrow. Open/closed state persists
between tools; values don't.

**Spline** rows: Closed Spline, Draw Mode (menu order: Tangent Drag, Click Auto Tangent, Free Draw), Min Point Spacing (Free Draw
only, default 200), Spline Name.
**Raycast:** Raycast Rules (3 elements: Landscape, Meshes, Ignore PCG Components), Hit Ground Planes.
**Draw Target:** Offset Mode (Hit Location), Normal Mode (Hit Normal).
**Paint:** Brush Mode (Sphere), Erase Points Of..., Rotate Yaw Step (10), Min Point Spacing (50).
**Brush:** Size (0.25), Strength (1.0), Falloff (0.0), Advanced.

### Reference pixels

Window 1821×1032, Tool panel docked left, **PCG Mode already open**. A guide for where to look. Read real positions from
your own capture.

| Control | x, y |
|---|---|
| Mode dropdown | 173, 81 (193, 81 when the label is longer) |
| Rail Spline / Paint / Volume / Query / Manual | 39, 145 / 205 / 265 / 325 / 385 |
| Group left / right | 142, 135 / 276, 135 |
| Tool row 1 left / right | 142, 180 / 276, 180 |
| Tool row 2 left / right | 142, 213 / 276, 213 |
| Accept / Cancel (spline) | 804, 959 / 878, 959 |
| Accept / Cancel (paint) | 798, 959 / 872, 959 |
| Accept / Cancel (volume) | 792, 959 / 866, 959 |

Menu items under the dropdown: Landscape 196, 137; PCG 177, 242. The toolbar shifts left in PCG Mode.

### Details after Accept

Component tree: `DefaultSceneRoot`, `SplineComponent_0`, `ISM_<mesh>_0`, `PCGToolComponent`. Select **PCGToolComponent** for Graph,
Parameters Overrides, the **PCG** buttons Generate / Cleanup / Clear PCG Link, and Settings → Seed (42).
Volume actors instead have `BrushComponent` and `PCGComponentBase`, plus Transform and **Brush Settings X/Y/Z** for exact size.
