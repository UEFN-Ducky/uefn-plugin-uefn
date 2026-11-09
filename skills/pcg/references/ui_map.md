---
description: "Where everything is in UEFN PCG Mode: mode menu, Shift+7, the Spline / Paint / Volume / Query / Manual rail, every tool button, the settings panel sections, Accept / Cancel bar, Details buttons, with position hints as window fractions"
metadata:
  order: 1
  label: "PCG Mode UI map"
  default_enabled: false
  load_condition: "You need to find, click or point at a button, tab, section or setting in UEFN PCG Mode"
---

## PCG Mode UI map

### Open it

Toolbar, top left: the **mode dropdown** (reads *Selection Mode*) → **PCG**, or press **Shift+7**.
The menu order is Selection, Landscape, Foliage, Modeling, Animation, Fortnite Tools, PCG (Shift+1 to Shift+7).
The dropdown then reads *PCG Mode*, and a tool panel opens at the left, pushing the viewport right.
Leave by choosing **Selection** in the same dropdown.

### Layout

| Area | Where | Contains |
|---|---|---|
| Mode dropdown | toolbar, far left | Selection Mode / PCG Mode |
| Category rail | thin icon column, far left edge | Spline, Paint, Volume, Query, Manual |
| Tool buttons | top of the panel, two columns | changes per category, below |
| Settings | panel below the buttons, scrolls | sections below |
| Accept / Cancel | floating bar, bottom centre of viewport | ends the draw. **Accept is grey until something is drawn** |
| Outliner / Details | right side | new actor `PCG <Tool> Actor`; its settings after Accept |

### Tools per category

| Rail | Top row | Tools | Graph asset |
|---|---|---|---|
| Spline | Draw Spline | SpacingTool | `/PCG/EdMode/DrawSpline/SpacingTool` |
| | | SplineMeshTool | `/PCG/EdMode/DrawSpline/SplineMeshTool` |
| | | LinearGrammarTool | `/PCG/EdMode/DrawSpline/LinearGrammarTool` |
| | | SpacingTool_Custom | not under `/PCG/EdMode` |
| | Draw Spline Surface | AreaTool | `/PCG/EdMode/DrawSplineSurface/AreaTool` |
| Paint | Paint | PlaceTool | `/PCG/EdMode/Paint/PlaceTool` |
| | | ScatterTool | not found under `/PCG/EdMode/Paint` |
| | | LayeredPlaceTool | `/PCG/EdMode/Paint/LayeredPlaceTool` |
| Volume | Volume | ScatterTool | `/PCG/EdMode/Volume/ScatterTool` |
| | | BiomeVolume | not under `/PCG/EdMode` |

Two different tools are called ScatterTool: one under Paint, one under Volume. Say which.

### Settings sections, top to bottom

Tool Graph dropdown → **Parameters Overrides** (Sampling, Filtering on area tools, Spawning, Global Transform,
Random Transform, Projection) → Data Instance, Actor Label, Component Name, Actor Class to Spawn →
**Spline** or **Paint** → **Raycast** → **Draw Target**. The order differs slightly per tool, and the panel
scrolls: expect to scroll to reach Raycast. Spline Mesh shows Spawning first, then Sampling.

### Position hints (fractions of the UEFN window)

Measured from a 1920×1080 maximised editor with the default layout. **Hints only: docking, window size and
monitor scale move them.** Capture first and read the real position (`agent_driving`).

| Control | nx | ny |
|---|---|---|
| Mode dropdown | 0.069 | 0.056 |
| Menu entry PCG (dropdown open) | 0.069 | 0.168 |
| Rail: Spline | 0.015 | 0.100 |
| Rail: Paint | 0.015 | 0.143 |
| Rail: Volume | 0.015 | 0.185 |
| Rail: Query | 0.015 | 0.226 |
| Rail: Manual | 0.015 | 0.268 |
| Top row left (Draw Spline / Paint / Volume) | 0.088 | 0.093 |
| Top row right (Draw Spline Surface) | 0.203 | 0.093 |
| Tool row 1 left (SpacingTool, PlaceTool, Volume ScatterTool) | 0.088 | 0.125 |
| Tool row 1 right (LinearGrammarTool, LayeredPlaceTool, BiomeVolume) | 0.203 | 0.125 |
| Tool row 2 left (SplineMeshTool, Paint ScatterTool) | 0.088 | 0.147 |
| Tool row 2 right (SpacingTool_Custom) | 0.203 | 0.147 |
| Accept (with panel open) | 0.474 | 0.847 |
| Cancel (with panel open) | 0.504 | 0.847 |

Accept and Cancel sit at the bottom centre of the *viewport*, so they shift with its width.

### Details panel after Accept

Select the `PCG <Tool> Actor`, then **PCGToolComponent** in the component tree. Details shows Graph,
Parameters Overrides, and in the **PCG** section the buttons **Generate**, **Cleanup**, **Clear PCG Link**,
then Settings → Seed.
