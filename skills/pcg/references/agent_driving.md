---
description: "How a Ducky agent operates UEFN PCG Mode: capture-first clicking with uefn_window_capture and uefn_window_click, spotlighting controls for the person with ducky_ui_show, what clicks can and can't draw, MCP inspection of the tool graphs, and the traps"
metadata:
  order: 5
  label: "Driving PCG Mode as an agent"
  default_enabled: false
  load_condition: "An agent needs to click through PCG Mode in UEFN, or show the person where to click in it"
---

## Driving PCG Mode as an agent

### Pick the method

| Goal | Method |
|---|---|
| Person asks where something is, or will do it themselves | **Spotlight**: `ducky_ui_show` with `window="uefn"` |
| Open a tool, set up clicks, draw with clicks | **Click**: `uefn_window_click` |
| Exact placement with numbers, no human | Skip the UI: PCG graphs in leveldesign `procedural_generation` |

### Click loop

`uefn_window_click` is a real pointer: it raises UEFN over the person's other windows and moves their cursor.
Do it when they asked for it, not as a background step.

1. `uefn_window_list` → take `hwnd`. **Empty `rect` means minimized: stop.** A click there returns `ok:true` and
   does nothing, and capture fails with "window has no on-screen rect". Have the window restored first.
2. Clear the selection (`select_actors` with nothing, or Epic equivalent). See SKILL rule 1.
3. `uefn_window_capture(hwnd)` → **look at the picture** and work out the control's position as `x/width, y/height`.
   Other windows covering UEFN show in the capture: capture again after the first click has raised it.
4. `uefn_window_click(hwnd, nx, ny)` with one control per click.
5. Capture again and confirm the change before the next click. Dropdowns need one click to open, a new capture,
   one click to choose.

Use the `ui_map` fractions only to know where to look. **Never click from the table without a capture.**

**Keyboard:** `uefn_window_key` sends a single key, so **Shift+7 and Shift+F2 can't be sent**. Use the mode dropdown.
Typing into a number field is key by key: click it, send digits, then `Enter`.

### What clicks can draw

`uefn_window_click` only clicks: it has no drag.

| Works by clicks | Needs a drag (the person does it) |
|---|---|
| Spline tools with **Draw Mode = Auto Click Tangent** | Free Draw and Tangent Drag |
| Area Tool with Auto Click Tangent | Volume box (drag + mouse height) |
| PlaceTool single drops | Scatter strokes, Place drag rows |

Click points in the viewport area of the capture, then Accept. Each one lands where the raycast hits, so check the
capture for the sky or a prop under the point.

`PCGToolset.DrawSpline` (`actorLabel`, `actorTag`, `bRedraw`, `bClosedSpline`) also waits for a human to draw.

### Walkthrough for the person

One `ducky_ui_show` call, all steps in `steps`, with `window="uefn"`, each `box` as `{x, y, w, h}` window fractions
from a fresh capture, `click: true` on steps they must press:

```json
{"window": "uefn", "steps": [
  {"box": {"x": 0.03, "y": 0.04, "w": 0.08, "h": 0.03}, "title": "Open modes", "body": "Click here, then **PCG**.", "click": true},
  {"box": {"x": 0.03, "y": 0.11, "w": 0.12, "h": 0.03}, "title": "Spacing Tool", "body": "Places objects along a line.", "click": true},
  {"box": {"x": 0.44, "y": 0.83, "w": 0.09, "h": 0.04}, "title": "Accept", "body": "Press when the line looks right."}
]}
```

The panel only appears after PCG Mode opens, so if later boxes depend on it, click into the mode first, capture,
then build the steps.

### Reading the tools through MCP

The tools are PCG graphs and can be inspected: `search_assets(directory="/PCG/EdMode/", class_name="PCGGraph")`
lists them, `PCGToolset.GetGraphStructure {"graph": {"refPath": "/PCG/EdMode/DrawSpline/SpacingTool.SpacingTool"}}`
reads one (its description is "Distribute assets along a spline.").

Before customizing one, duplicate it into the project (`EditorToolset.AssetToolset.Duplicate`) under
`get_project_info().content_root`. Never edit `/PCG/EdMode` assets.

### Check the result

Count the new actor and its ISM in the Outliner, then a screenshot. Actor label is `PCG <Tool> Actor`. Tell the
person the seed if you set one.
