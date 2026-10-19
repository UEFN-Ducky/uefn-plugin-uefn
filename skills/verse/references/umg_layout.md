---
description: "UMG composition — kit widgets in your own screen, StackBox/Overlay layout (no Vertical/HorizontalBox), Z bands, named layers, safe zone and sizes, custom button hierarchy"
metadata:
  order: 69
  label: "UMG layout"
  default_enabled: false
  load_condition: "Composing a UMG screen, Z-order bands, or a custom button hierarchy"
---

## UMG layout

A screen is your own widget that lays out the Verse UI Kit's widgets (`verse_ui_kit`). Never build inside the kit folder or edit a kit widget to fit one screen.

Containers: `StackBox` (set `Orientation`), `Overlay`, `SizeBox`, `ScaleBox`, `ScrollBox`, `WrapBox`, `GridPanel`. UEFN has no Vertical/HorizontalBox. Put labels beside label-free controls (checkbox, toggle, radio) in a horizontal `StackBox`.

The factory inserts one root `CanvasPanel`; `build_widget_tree` reuses it when the spec root is `CanvasPanel`. Name it `Root_Canvas` (role first, type second — `verse_ui_kit` Naming).

Z bands:

| Band | z_order |
|------|---------|
| Background | 0 |
| Content | 10 |
| Chrome | 20 |
| Modal | 30 |

Named layers swap by `visibility` or by adding and removing that child. Do not rebuild the whole tree to hide a pane.

Nested User Widgets for a card, a header, a details pane (`umg_compose`). Repeated buttons are one small widget built on a kit button, repeated — one edit restyles every copy.

Safe zone and sizes: keep important UI about 5 % in from each screen edge, touch targets at least ~64 px, body text about 24 px or larger. A centered card uses a point anchor at 0.5, 0.5 with offsets that are the card size.

### Custom Button hierarchy

Every button is a custom one: a kit button (`UW_Button_Basic`, …) styled through its named slots, or — only when the project has no kit — a UEFN `CustomButton` with your own art:

```
CanvasPanel  Root_Canvas
  Overlay    Play_Overlay        z 10
    Image    Fill_Image          material brush (fill / stroke)
    CustomButton Play_Button     hit target (focusable as it comes — never override IsFocusable)
      Text   Play_Text           label (UEFN_TextBlock_C, localizable)
```

The label is a `Text` widget inside the Custom Button (`umg_palette`). Never the preset `LoudButton` / `QuietButton` / `RegularButton`.

One full-screen hit target per layer.
