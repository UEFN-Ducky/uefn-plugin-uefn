---
description: "How a Ducky agent physically operates UEFN PCG Mode with the real mouse: the tested hover-click, typed-value and relative-drag PowerShell helper, why uefn_window_click fails on menus and why teleported drags draw nothing, asset pickers, splines, paint strokes and volumes, Cancel and cleanup, Epic toolset fallbacks, spotlighting controls with ducky_ui_show"
metadata:
  order: 1
  label: "Driving PCG Mode with the mouse"
  default_enabled: false
  load_condition: "An agent needs to click, drag, type or draw in UEFN PCG Mode, build something with the PCG tools by mouse, or show the person where to click"
---

## Driving PCG Mode with the mouse

Everything on this page was run against UEFN and worked unless marked **untested**.

### Pick the method

| Goal | Method |
|---|---|
| Build with PCG Mode | The helper below, then a recipe from `build_recipes` |
| Person asks where something is | `ducky_ui_show` with `window="uefn"` |
| Exact placement from numbers, no viewport | PCG graphs in leveldesign `procedural_generation` |

This moves the person's real cursor and raises UEFN over their windows. Do it when they asked for it, and tell
them before you start. They should not touch the mouse during a run.

### Two traps that break everything

**1. Slate needs a hover.** `uefn_window_click` sends move-and-press as one event, so Slate never sees the pointer
arrive. Opening a dropdown works; **clicking an item inside a menu closes it, picks nothing and returns `ok:true`**.
Use `PClick` (hover, then press) for all UI. `ok:true` proves nothing: compare captures.

**2. A drag needs real mouse movement.** While a button is held, the viewport tools ignore a cursor that is teleported
with `SetCursorPos`: only the press and release points register. Free Draw gives a straight two-point line and a Paint
stroke leaves one object, at any speed. Send relative movement (`mouse_event` MOVE) instead: `PStroke` below.

`uefn_window_click` also has no drag, and does nothing on a minimized window. `uefn_window_key` sends single keys only
(no Shift+7), but `Escape` works and is how you deselect.

### Helper

Terminals close when idle, so paste this at the start of every terminal command that uses it. Set `$L,$T` from
`uefn_window_list` (`rect.left`, `rect.top`). Coordinates are **pixels in the capture image**, 1:1 with the window.

```powershell
$sig='[DllImport("user32.dll")] public static extern bool SetCursorPos(int x,int y); [DllImport("user32.dll")] public static extern void mouse_event(uint f,int x,int y,uint d,UIntPtr e);'
$M=Add-Type -MemberDefinition $sig -Name PcgPtr -Namespace Ducky -PassThru -ErrorAction SilentlyContinue; if(-not $M){$M=[Ducky.PcgPtr]}
Add-Type -AssemblyName System.Windows.Forms
$L=1396; $T=0   # from uefn_window_list
function PMove($x,$y){[void]$M::SetCursorPos($L+$x,$T+$y)}
function PHover($x,$y){PMove ($x-3) $y; Start-Sleep -Milliseconds 150; PMove $x $y; Start-Sleep -Milliseconds 250}
function PDown{$M::mouse_event(2,0,0,0,[UIntPtr]::Zero)}
function PUp{$M::mouse_event(4,0,0,0,[UIntPtr]::Zero)}
function PClick($x,$y){PHover $x $y; PDown; Start-Sleep -Milliseconds 60; PUp}
function PType($t){[System.Windows.Forms.SendKeys]::SendWait($t)}   # escape + ^ % ~ ( ) { }
function PSet($x,$y,$v){PClick $x $y; Start-Sleep -Milliseconds 600; PType "^a"; Start-Sleep -Milliseconds 200; PType "$v{ENTER}"; Start-Sleep -Seconds 1}
function PRel($dx,$dy,$steps,$ms){$ux=[int]($dx/$steps);$uy=[int]($dy/$steps); for($s=1;$s -le $steps;$s++){$M::mouse_event(1,$ux,$uy,0,[UIntPtr]::Zero); Start-Sleep -Milliseconds $ms}}
function PStroke($x,$y,$segs){PHover $x $y; PDown; Start-Sleep -Milliseconds 200; foreach($g in $segs){PRel $g[0] $g[1] 20 40}; Start-Sleep -Milliseconds 200; PUp}
function PAway{PMove 900 1015; Start-Sleep -Milliseconds 700}
```

`PStroke 400 560 @(@(60,40),@(80,-20))` presses at 400,560 and drags by +60,+40 then +80,-20. A single segment needs
the comma: `@(,@(140,100))`. Never name a function `Mv`: it is PowerShell's alias for Move-Item.

### Before the first click

1. `uefn_window_list`. **Empty `rect` = minimized.** Restore with `ShowWindow(hwnd, 9)` from the same PowerShell.
2. Other windows may cover UEFN. `uefn_window_click` on an **empty toolbar spot** raises it. Avoid the title bar.
3. Deselect: `uefn_window_key(hwnd, "Escape")`, or `select_actors(actor_paths=[])`. Details must read
   "Select an object to view details".
4. **Never click the viewport in Landscape Mode's Sculpt tab**: it sculpts the terrain. Switch mode first.
5. Frame the area. Points land where the ray hits under the pointer, so pick a view where the target ground is
   visible and clear of the left panel and the Accept bar.
6. Note the current mode and put it back when you finish.

### The loop

`uefn_window_capture` → read the pixel position from the image → run helper → `PAway` (so tooltips don't cover what
you need) → capture → confirm the change.

**One UI change, one fresh capture.** Rows move constantly: expanding a section, adding a mesh, or changing Draw Mode
shifts everything below. Columns move sideways too: when the panel gets a scrollbar the **+** button sits at about
x 245, without one at about x 260. A click that misses does nothing and the next ones land in the wrong place.

Waits that worked: 1 s after a checkbox or expander, 2 s after opening a tool, 3 s after opening an asset picker and
3 s after typing into it, 3 s after a value that regenerates, 2 s after Accept or Cancel.

### Set a value

Each row under Parameters Overrides has a checkbox at its far left: tick it first or the value is ignored. A yes/no
row has a second checkbox for the value itself. Number: `PSet x y 1000`. A vector has three fields (X, Y, Z).

### Set a mesh

1. Expand **Spawning**, tick the **Static Meshes** row checkbox, press its **+** (check the array reads `1 Array`).
2. A `Index [0]` block appears with a mesh dropdown and a Weight field.
3. `PClick` the dropdown, wait 3 s, `PType "name"`, wait 3 s, **capture**, `PClick` the result row.

The search box takes focus by itself. The picker opens below the dropdown, or **above it** when the dropdown is low
in the panel. Spline Mesh Tool has one Mesh row with its dropdown directly on it, no **+**.

### Draw

| Gesture | How | Result |
|---|---|---|
| Click Auto Tangent | One `PClick` per point | Points landed within 2 px, smooth curve through them. **Best for roads** |
| Free Draw, Paint strokes | `PStroke` (relative drag) | Paint Scatter left a trail of objects along the stroke |
| PlaceTool | One click per object | Exact |
| Volume | `PStroke` corner to corner, then `PRel 0 -80 10 40`, then `PDown`/`PUp` | Box drawn. Footprint, then height |

Check a new volume's Transform and **Brush Settings X/Y/Z** in Details: the box can end up above the ground, and then
it only spawns on roofs that reach into it. Type exact numbers there.

Free Draw splines and Tangent Drag with `PStroke`, and LayeredPlaceTool: **untested**.

### Finish

- **Accept** commits and leaves the tool. The actor **stays selected**: press `Escape` before the next tool or it
  lands inside that actor.
- **Cancel** removes the draft actor and everything it spawned.
- Spline tools: Accept is grey until there's a spline. Paint and Volume: Accept is lit from the start.
- Accept can re-roll random transforms: check the result after it, not only the preview.
- Leave PCG Mode via the mode dropdown → restore the earlier mode.

### Check and clean up (Epic toolsets)

| Job | Call |
|---|---|
| List what the tools made | `EditorToolset.LevelToolset.FindActors {"filter": {"name": "Tool Actor"}}` (labels `PCG <Tool> Actor`, names `PCGToolWorkingActor_N`, with bounds) |
| Remove one | `EditorToolset.LevelToolset.RemoveFromScene {"actor": {"refPath": "<actorPath>"}}` |
| Find a mesh | `EditorToolset.AssetToolset.FindAssets {"filter": {"folderPath": "/<project>/", "name": "road", "assetType": {"refPath": "/Script/Engine.StaticMesh"}}}` |

Never call `ListFolders` on the project root with `bRecursive` true: it returns close to a megabyte. First use of PCG
Mode adds a `PCGWorldActor` to the level; it's Epic's and stays.

### Spotlight for the person

One `ducky_ui_show` call with `window="uefn"`, all steps in `steps`, `box` as `{x, y, w, h}` window fractions from a
fresh capture, `click: true` where they must press. A panel only exists after its mode is open.

### Read a tool graph

`PCGToolset.GetGraphStructure {"graph": {"refPath": "/PCG/EdMode/DrawSpline/SpacingTool.SpacingTool"}}`.
To change one, `EditorToolset.AssetToolset.Duplicate` it under the project's content root. Never edit `/PCG/EdMode`.
