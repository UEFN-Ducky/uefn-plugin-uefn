---
description: "UEFN PCG Mode Paint tools (Place, Scatter, Layered Place) and Volume tools (Scatter, Biome Volume): how to use them, brush settings, drawing a volume, Sample Landscape Only and Sample Complex Collision"
metadata:
  order: 3
  label: "Paint and Volume tools"
  default_enabled: false
  load_condition: "Using PCG Paint, Place Tool, Paint Scatter, Layered Place, PCG Volume, Volume Scatter or Biome Volume in PCG Mode"
---

## Paint tools

Rail **Paint**. Add a mesh under Spawning, then work in the viewport. **Accept** when finished.

| Tool | Use |
|---|---|
| **PlaceTool** | Each click drops one object, hold and drag for a row. With several meshes each click picks one at random. The quickest way to hand-place trees and rocks |
| **ScatterTool** | Paints a random cluster under the brush. Good for filling around an area |
| **LayeredPlaceTool** | Listed in the panel, not covered in the source tutorial. Read it with `GetGraphStructure` on `/PCG/EdMode/Paint/LayeredPlaceTool.LayeredPlaceTool` before relying on it |

| Paint setting | Effect |
|---|---|
| Brush Mode | Sphere by default. Little visible effect on PlaceTool |
| Brush section: Size, Strength, Falloff | Defaults 0.25, 1.0, 0.0. **Size matters on ScatterTool**: bigger brush, wider scatter |
| Min Point Spacing | Gap between points while dragging (50 default) |
| Rotate Yaw Step Size | 10 default |
| Erase Points Of Selected Data Instance | Paint-erase on the selected layer. On by default |
| Data Instance | `PaintLayer` holds what you painted |

Global Transform, Random Transform, Projection and Raycast work as in `spline_tools`.

## Volume tools

Rail **Volume**. **ScatterTool** fills a box with points on whatever is inside it. **BiomeVolume** was not covered
in the source tutorial; read its graph before relying on it.

**Draw a volume:** press at the first corner → drag out the footprint → release → move the mouse up to set the height →
click to lock it → **Accept**. Exact numbers afterwards: Details → Transform and **Brush Settings X/Y/Z**.

| Setting | Effect |
|---|---|
| Points Per Squared Meter | 0.1 is a safe start |
| Point Size, Uniformity, Sampling Seed | As in Area Tool |
| Sample Landscape Only | Ignores cubes and props, only the landscape gets points |
| Sample Complex Collision | Projects onto meshes using complex collision |

The volume spawns on surfaces inside it, including placed meshes. Objects not appearing → make sure the box
actually overlaps the ground; move it down if needed. Filtering, Spawning, transforms and Projection work as in
`spline_tools`.
