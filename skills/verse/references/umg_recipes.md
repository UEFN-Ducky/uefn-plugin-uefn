---
description: "Finished UMG builds the Verse UI Kit way — kit composites first, then HUD message, float binding, custom button menu with Back, shop frame with paged rows; custom buttons only"
metadata:
  order: 73
  label: "UMG recipes"
  default_enabled: false
  load_condition: "Building a finished UMG menu, HUD, or shop frame"
---

## UMG recipes

**First choice: a kit composite.** The Verse UI Kit's `Widgets/Composites/` has a dialog, settings panel, item card, menu, list and grid, each with a `UW_*_Example` screen and a `*_example.verse` driver. Copy the nearest one into your folder and change it (`verse_ui_kit`). Build from the recipes below only when nothing fits, or the project has no kit yet.

Rules for every recipe:

- Every clickable is a custom button — a kit button, or a UMG `CustomButton` when there is no kit. Never `LoudButton` / `QuietButton` / `RegularButton`, never Verse `button_loud` / `button_quiet` / `button_regular`.
- Every interactive screen focuses its first control on open, reaches every control by gamepad and arrow keys, and closes on Back (`umg_navigation`).
- Repeating rows are one small row widget built on a kit button, repeated in the screen. Do not hand-place twelve unique buttons when the data is a list.
- Names follow `verse_ui_kit` — Naming (`UW_<Category>_<Name>`, `Role_Type` tree names, `Is…` / `…Text` / `On…` fields).

The Verse type is the Assets digest name after the asset exists. Do not write `card_widget_bp := class`.

### 1 — HUD message

`add_verse_field` name `BannerText`, type `message`. Bind that field to the text of a `Text` widget (`Banner_Text`). No click, no focus. `ui_input_mode.None`. One instance per player. A short notice is a kit toast instead (`ui_feedback_toast{}.ShowSuccessToast`).

### 2 — Slider or progress

`add_verse_field` name `ProgressValue`, type `float`, default `0`. Bind to `RenderOpacity` or a material scalar (`Conv_SetScalarParameter`) when the palette has no `ProgressBar` / `Slider`. Device: `set Widget.ProgressValue = 0.5`.

### 3 — Custom Button menu

Structure verified live (42.30) — names here follow the kit's naming:

```
CanvasPanel Root_Canvas
  Overlay Menu_Overlay      anchors 0.5,0.5  offsets ±220 x ±70  z_order 10
    Image Fill_Image        brush_material = UI-domain unlit material instance
    CustomButton Play_Button
      Text Play_Text        label (UEFN_TextBlock_C, localizable text)
  UW_Shared_CloseButton Close   (kit) — or a CustomButton Close_Button without the kit
```

- `Anim_Highlight` on `Fill_Image`, Opacity, keys at 0 (0.45) and 0.35 (1).
- `Anim_Loop` on `Fill_Image`, Transform `ScaleX` and `ScaleY`, keys at 0 (1), 0.4 (1.06), 0.8 (1).
- `add_verse_field` `IsIntroActive` type `logic` (the tool stores `bool`). Bind to `Fill_Image.RenderOpacity` when the intro should fade the fill.
- `add_verse_field` `OnPlayClicked` and `OnCloseClicked`, type `event` (42.30). `bind_widget_event` `Play_Button` `OnButtonClicked` → `OnPlayClicked`. With the kit close button, bind both of its inner buttons to `OnCloseClicked` (`verse_ui_kit` — Input). Check `compiled`.
- Desired Focus Widget = `Play_Button` (`umg_navigation`).
- Verse: with the kit, `Helper.SubscribeToEvent(Player, Widget.OnPlayClicked, OnPlayClicked)`; without it on 43.00, `Sub := Widget.OnPlayClicked.Subscribe(OnPlayClicked)` (cancel on close); on 42.x, where event fields have no `Subscribe`, `loop: Widget.OnPlayClicked.Await()` in one spawned watcher per widget (`umg_verse_field_events`).
- Highlight graph: `umg_animations`. Device: `umg_widget` template. Volume opens it. Add with `ui_input_mode.All`, then focus. Remove on Back and on leave.

### 4 — Shop frame

Parent screen `UW_Shop_Screen`: frame, header, a details pane (`UW_Shop_OfferDetails`) and a fixed number of offer rows (`UW_Shop_OfferRow`, one small widget built on a kit button). Each row's title and price are fields on the **screen** bound to that row (`Row1TitleText`, `Row1PriceText`, …) — never values typed onto the nested instance. One shared `OnRowClicked(int)` event, each row sending its own number from 1.

More offers than rows: page them. `OnNavigatePage(int)` sends `-1` / `+1` (shoulder buttons through `PrevTab_Action` / `NextTab_Action`), Verse refills the row fields, and empty rows collapse through a `IsRow<N>Visible` bool bound to `Visibility`. Refocus after every page change (`FocusWidgetForPlayer`). Do not pre-place every offer.
