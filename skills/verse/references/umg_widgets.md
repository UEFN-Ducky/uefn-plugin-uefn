---
description: "UMG User Widgets in UEFN — Epic's Verse UI Kit first, kit screens vs Verse canvas, creating UW_* widgets, Assets digest lookup, AddWidget/RemoveWidget, per-player traps, myths vs the live digest"
metadata:
  order: 60
  label: "UMG User Widgets — proper Verse usage"
  default_enabled: false
  load_condition: "Creating or driving a UMG User Widget / Widget Blueprint from Verse — designer UI, Verse fields, or when deciding UMG vs canvas"
---

## UMG User Widgets — proper Verse usage

**Start with `verse_ui_kit`.** Epic's Verse UI Kit is the default for every UEFN screen: kit widgets inside your own `UW_*` screen, driven by the kit's `ui_helper_function_library`. Its rules (custom kit buttons only, focus, Back, naming, no hidden values, styling through slots) apply to everything below. This page and the other `umg_*` pages are the layer-by-layer detail, and the path when a project has no kit yet.

A Widget Blueprint is a nested tree plus slots, brushes, animations, and Verse fields. Author those with the tools in `umg_mcp_tools`. The Verse type is the Assets digest name after the asset exists. Do not invent `MyUMGWidget := class` or `card_widget_bp := class`.

Load the reference for the layer you are writing:

| Layer | Reference |
|-------|-----------|
| Kit rules, recipes, naming | `verse_ui_kit` |
| Which class | `umg_palette` |
| Anchors, ZOrder | `umg_slots` |
| Brush, visibility, transform | `umg_style` |
| Hierarchy | `umg_layout` |
| UI materials | `umg_ui_materials` |
| Highlight / loop keys | `umg_animations` |
| Fields | `umg_verse_fields` |
| Clicks | `umg_verse_field_events` |
| Bindings | `umg_view_bindings` |
| Gamepad | `umg_navigation` |
| Nested widgets | `umg_compose` |
| Finished builds | `umg_recipes` |

### Kit screen vs Verse canvas

| Choose | When |
|--------|------|
| **Kit screen `UW_*`** (`verse_ui_kit`) | Default for every menu, shop, settings, dialog, list, grid, HUD and toast |
| **UMG with Custom Buttons** | The project has no Verse UI Kit yet — same rules, your own image slots |
| **Verse canvas** (`ui`) | Only when the screen must be built in code: a data-sized cell board (`sys_minigame_overlay`) or a template pack's `*_canvas_builder` |

Every clickable is a custom button: a kit button, a UMG `CustomButton`, or (canvas only) the chrome-less Verse `button`. Never Loud/Quiet/Regular buttons. Repeating rows are one small row widget built on a kit button, repeated in the screen — never N unique hand-placed buttons.

All of them end the same way: `GetPlayerUI[Player].AddWidget(...)` (the kit's `Helper.ShowFullScreen` does it for you).

### Create the widget asset

**Via tools:** `list_widget_classes` → `build_widget_tree` (omit `folder` so the listener pins `{content_root}/UI`). Then animations, fields, and bindings from `umg_mcp_tools`. Read back with `get_widget_blueprint_info`. Verse cannot call `PlayAnimation` by name — key the animation and bind it (`umg_animations`).

**Preview in editor (v42.20):** interact with the widget in the UMG designer —
do not Launch Session just to check animation / button text. Multiple in-world
instances of the same `UW_*` class now all show Verse-bound values.

### Never guess the Verse type — use the Assets digest

After the widget exists and Verse digests refresh:

```
list_verse_types(digest="assets", name_filter="UW_")
get_verse_api("UW_Hud_Screen")   # exact members = Verse fields + events
```

If the name is not in the Assets digest, it does not exist for Verse yet — do not invent a stub class. A widget in another folder module is `FolderName.UW_X`; `using` that folder fails with 3593 until it is declared public (`verse_ui_kit` — Verse modules).

### Show / hide on a player

With the kit, use the driver pattern in `verse_ui_kit` (`Helper.ShowFullScreen`, `Helper.FocusWidgetForPlayer`, `Helper.ClearAllForPlayer`). Without it:

```verse
using { /Fortnite.com/UI }
using { /UnrealEngine.com/Temporary/UI }
using { /Verse.org/Simulation }

# UW_Hud_Screen comes from the Assets digest — not a hand-written empty class
var Widgets : [player]UW_Hud_Screen = map{}

ShowFor(Player : player) : void =
    if (PlayerUI := GetPlayerUI[Player]):
        Widget := UW_Hud_Screen{}          # a fresh widget each time, per player
        if (set Widgets[Player] = Widget) {}
        # HUD: ui_input_mode.None — menus that need clicks: .All, then focus (umg_navigation)
        PlayerUI.AddWidget(Widget, player_ui_slot{ InputMode := ui_input_mode.None })

HideFor(Player : player) : void =
    if (PlayerUI := GetPlayerUI[Player], Widget := Widgets[Player]):
        PlayerUI.RemoveWidget(Widget)
```

You can also call `PlayerUI.AddWidget(Widget)` with the default slot. Wrapping the UMG widget in a Verse `canvas` is **optional** — only do it when you need Verse-side `canvas_slot` positioning on top of the UMG layout.

### Per-player trap

One shared `var MyWidget : UW_X = UW_X{}` on a device is a **single instance**. If two players both `AddWidget` the same instance, behavior is wrong. For multiplayer:

- Prefer **one widget instance per player** (map `[player]UW_X`, created in `ShowFor`), or
- Keep a single spectator/shared HUD only when that is intentional.

### Drive data and clicks

| Need | Subskill |
|------|----------|
| `set Widget.IsToggleButton1Active = true` / materials / messages | `umg_verse_fields` |
| Button clicks (kit `Helper.SubscribeToEvent`, or an Await loop) | `verse_ui_kit`, `umg_verse_field_events` |
| View Bindings / ToText / textures | `umg_view_bindings` |
| UI materials / MI_* | `umg_ui_materials` |
| Tree, slots, animations, fields | `umg_mcp_tools` |
| A finished menu or shop | `verse_ui_kit` recipes, then `umg_recipes` |

Template scaffold: `verse_template_apply("umg_widget")`.

### Myths table (common wrong example vs live digest)

Agents keep meeting a "display UMG from Verse" snippet that is partly obsolete. Correct against the digest — do not repeat the myths:

| Myth / bad pattern | Truth (verified) |
|--------------------|------------------|
| `MyUMGWidget := class:` empty placeholder + `@editable myUMGWidget : ?MyUMGWidget` | **Wrong.** Type is the real `UW_*` from Assets digest. Instantiate with `UW_X{}`. |
| "Verse cannot get a named button from a UMG widget" | **Obsolete since 39.40.** Use **Verse field events** on the widget (`event()` fields bound to the Custom Button's `OnButtonClicked`; creatable by tool since 42.30). |
| A parent listens to a child widget's Verse event | **No.** Bind the child's inner native button (`ToggleButton1.Main_Button.OnButtonClicked`) to a shared int event on your screen (`verse_ui_kit` — Clicks). |
| `Widget.OnCloseClicked.Subscribe(...)` on a UMG event field | **No `Subscribe`.** Use the kit's `Helper.SubscribeToEvent`, or `Await` in a loop (`umg_verse_field_events`). |
| Must wrap UMG in a Verse `canvas` to show it | **Optional.** `player_ui.AddWidget(Widget)` / `AddWidget(Widget, player_ui_slot{…})` is enough. |
| `canvas.GetSlots()` / `canvas.SetSlot(...)` | **Do not exist.** Digest: `canvas` has `Slots` (init), `AddWidget(Slot)`, `RemoveWidget(Widget)` only. |
| `SizeToContent` / `ZOrder` on `canvas_slot` | **Real** — both exist on `canvas_slot` in UnrealEngine digest. |
| Verse can call UMG `PlayAnimation` by name | **Not exposed.** Key tracks with `add_animation_keys` and trigger them from a Verse field binding. |
| ScrollBox offset scrubbing from Verse | Limited — you can place scroll widgets; do not assume a Verse "set scroll offset" API without checking digests. |

### Folder layout

Put widgets and their Verse driver in your own UI folder (`UI/<Category>/`), never inside the kit folder. Never dump `umg_display_device.verse` at `Content/Verse/` root — see `modules`.
