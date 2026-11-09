---
description: "How a Ducky agent physically operates UEFN PCG Mode with the real mouse: the tested hover-click and drag PowerShell helper, why uefn_window_click fails on menus, typing into asset pickers, drawing splines, paint and volumes, Cancel and cleanup, spotlighting controls with ducky_ui_show, and every trap found in live testing"
metadata:
  order: 1
  label: "Driving PCG Mode with the mouse"
  default_enabled: false
  load_condition: "An agent needs to click, drag or draw in UEFN PCG Mode, build something with the PCG tools by mouse, or show the person where to click"
---

## Driving PCG Mode with the mouse

Everything on this page was run against UEFN 43.00 and worked unless marked **untested**.

### Pick the method

| Goal | Method |
|---|---|
| Build with PCG Mode | The helper below, then a recipe from `build_recipes` |
| Person asks where something is | `ducky_ui_show` with `window="uefn"` |
| Exact placement from numbers, no viewport | PCG graphs in leveldesign `procedural_generation` |

This moves the person's real cursor and raises UEFN over their windows. Do it when they asked for it, and tell
them before you start. They should not touch the mouse during a run.

### The trap that breaks everything: Slate needs a hover

`uefn_window_click` sends move-and-press as one input event. Slate never sees the pointer arrive, so:

| Target | `uefn_window_click` | Hover first (helper) |
|---|---|---|
| Opening a toolbar dropdown | Works | Works |
| **Item inside a menu** | **Closes the menu, picks nothing, returns `ok:true`** | Works |
| Viewport spline points | Works | Works |
| Panels, checkboxes, tool buttons | Use the helper | Works |

Always use the helper for UI. `ok:true` from a click proves nothing: compare captures.

It also has no drag, sends only single keys (no Shift+7, Shift+F2) and silently does nothing on a minimized window.

### Helper

Terminals close when idle, so paste this at the start of every terminal command that uses it. Set `$L,$T` from
`uefn_window_list` (`rect.left`, `rect.top`). The coordinates you pass are **pixels in the capture image**, which is
1:1 with the window.

```powershell
$sig='[DllImport("user32.dll")] public static extern bool SetCursorPos(int x,int y); [DllImport("user32.dll")] public static extern void mouse_event(uint f,uint x,uint y,uint d,UIntPtr e);'
$M=Add-Type -MemberDefinition $sig -Name PcgPtr -Namespace Ducky -PassThru -ErrorAction SilentlyContinue; if(-not $M){$M=[Ducky.PcgPtr]}
Add-Type -AssemblyName System.Windows.Forms
$L=1396; $T=0   # from uefn_window_list
function PMove($x,$y){[void]$M::SetCursorPos($L+$x,$T+$y)}
function PHover($x,$y){PMove ($x-3) $y; Start-Sleep -Milliseconds 150; PMove $x $y; Start-Sleep -Milliseconds 250}
function PDown{$M::mouse_event(2,0,0,0,[UIntPtr]::Zero)}
function PUp{$M::mouse_event(4,0,0,0,[UIntPtr]::Zero)}
function PClick($x,$y){PHover $x $y; PDown; Start-Sleep -Milliseconds 60; PUp}
function PDrag($pts){PHover $pts[0][0] $pts[0][1]; PDown; Start-Sleep -Milliseconds 120
  for($i=1;$i -lt $pts.Count;$i++){$a=$pts[$i-1];$b=$pts[$i]
    for($s=1;$s -le 12;$s++){PMove ([int]($a[0]+($b[0]-$a[0])*$s/12)) ([int]($a[1]+($b[1]-$a[1])*$s/12)); Start-Sleep -Milliseconds 25}}
  Start-Sleep -Milliseconds 120; PUp}
function PType($t){[System.Windows.Forms.SendKeys]::SendWait($t)}   # escape + ^ % ~ ( ) { }
```

Never name a function `Mv`: it is PowerShell's alias for Move-Item and wins over your function.

### Before the first click

1. `uefn_window_list`. **Empty `rect` = minimized.** Restore it:
   `ShowWindow(hwnd, 9)` from the same PowerShell, adding that P/Invoke.
2. Other windows may cover UEFN. `uefn_window_click` on an **empty toolbar spot** raises it (cooldown applies, so
   don't repeat it). Avoid the title bar.
3. `get_selected_actors`; if anything is selected, `select_actors(actor_paths=[])`.
4. Frame the area: `set_viewport_camera`. Points land where the raycast hits under the pointer, so pick a view where
   the target ground is visible and clear of the left panel and the Accept bar.
5. Note the current mode and put it back when you finish.

### The loop

`uefn_window_capture` → read the pixel position from the image → run helper → move pointer away
(`PMove` to the status bar, so tooltips don't cover what you need) → capture → confirm the change.

**One UI change, one fresh capture.** Rows move constantly: expanding Spawning, adding a mesh, or changing Draw Mode
(Click Auto Tangent removes the Min Point Spacing row) all shift everything below.

Timing that worked: 1 s after a checkbox or expander, 2 s after opening a tool, 3 s after opening an asset picker and
3 s after typing into it, 2 s after Accept or Cancel.

### Set a mesh

1. Expand **Spawning**, tick the **Static Meshes** row checkbox, press its **+**.
2. A `Index [0]` block appears with a mesh dropdown (shows `N..e`) and a Weight field.
3. `PClick` the dropdown, wait 3 s, `PType "name"`, wait 3 s, capture, `PClick` the result row.

The search box takes focus by itself. The picker opens about 240 px below and 100 px right of its dropdown. Rocks appear
as a preview as soon as a mesh is set, before Accept.

### Draw

| Gesture | How | Result |
|---|---|---|
| Click Auto Tangent | One `PClick` (or plain `uefn_window_click`) per point | Points landed within 2 px. **Use this for every shape** |
| Free Draw | `PDrag` | Works, but a scripted drag kept only the two end points, so it comes out straight |
| PlaceTool | One click per object | Exact |
| Volume | `PDrag` corner to corner, release, `PMove` upward in steps, `PDown`/`PUp` | Box drawn. Footprint then height |

Volume sequence that worked:

```powershell
PDrag @(@(1000,900),@(1130,880)); Start-Sleep -Milliseconds 800
for($i=1;$i -le 10;$i++){PMove 1130 (880-8*$i); Start-Sleep -Milliseconds 40}
Start-Sleep -Milliseconds 500; PDown; Start-Sleep -Milliseconds 60; PUp
```

Tangent Drag, Paint ScatterTool strokes and LayeredPlaceTool: **untested by mouse**.

### Finish

- **Accept** commits and leaves the tool. The actor **stays selected**, so run `select_actors(actor_paths=[])` before the
  next tool or it lands inside that actor.
- **Cancel** removes the draft actor and everything it spawned, including painted objects.
- Spline tools: Accept is grey until there's a spline. Paint and Volume: Accept is lit from the start, so it can commit
  an empty tool.
- Check: `get_all_actors(label_filter="PCG")`. The Spacing actor's internal name is `PCGToolWorkingActor`, its label
  `PCG Spacing Tool Actor`. Details shows `ISM_<mesh>_0` under it when meshes spawned.
- Leave PCG Mode via the mode dropdown → restore the earlier mode.
- Test actors you made: `delete_actors`. First use also adds a `PCGWorldActor` to the level; it's Epic's and stays.

### Spotlight for the person

One `ducky_ui_show` call with `window="uefn"`, all steps in `steps`, `box` as `{x, y, w, h}` window fractions from a
fresh capture, `click: true` where they must press. A panel only exists after its mode is open, so enter PCG Mode first,
capture, then build the boxes.

### Read a tool graph

`search_assets(directory="/PCG/EdMode/", class_name="PCGGraph")`, then
`PCGToolset.GetGraphStructure {"graph": {"refPath": "/PCG/EdMode/DrawSpline/SpacingTool.SpacingTool"}}`.
To change one, `EditorToolset.AssetToolset.Duplicate` it under `get_project_info().content_root`. Never edit `/PCG/EdMode`.
`PCGToolset.DrawSpline` waits for a human to draw.
