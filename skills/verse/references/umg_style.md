---
description: "UMG widget look — style kit widgets through named slots, localizable text, brush, visibility, opacity, render transform, overrides that fail asset validation"
metadata:
  order: 68
  label: "UMG style"
  default_enabled: false
  load_condition: "Setting UMG text, color, brush, visibility, opacity, or render transform"
---

## UMG style

Kit widgets are styled through their named slots: an `Image` with your material instance in each slot, made from `/FNE_UI/Systems/_Materials/Shapes/M_UI_Rectangle` (`verse_ui_kit` — Style recipe). Never restyle a kit widget by editing it, and never set properties on a nested instance.

Widget JSON on `build_widget_tree` `properties`. These are the keys `_apply_widget_props` writes.

| Key | Effect |
|-----|--------|
| `text` | Label of a `Text` widget (palette `UEFN_TextBlock_C`, `umg_palette`), written as localizable `NSLOCTEXT` with a fresh key. A value that is already a text macro (`NSLOCTEXT`, `INVTEXT`, `LOCTABLE`) is written as is |
| `color` | `[R, G, B, A]` on `ColorAndOpacity` |
| `render_opacity` | 0–1 |
| `visibility` | `Visible`, `Collapsed`, `Hidden`, `HitTestInvisible`, `SelfHitTestInvisible` |
| `brush_material` | Material or instance path. Image calls `set_brush_from_material` |
| `brush_texture` | Texture path |

**Text is localizable.** Player-facing text typed in UMG goes in a text block as localizable text. `build_widget_tree` `text` does that; to change it later: `set_widget_property(widget_path, <text widget ref>, {"Text": "NSLOCTEXT(\"\", \"<unique 32-hex key>\", \"Play\")"})`. Verified in UEFN 42.30: the key is saved with the text, so Export Localization finds it. A plain string has no key and is never gathered. A `notes` entry "text: saved as a plain string, not localizable" (or an older Ducky) means set it again this way (`verse_ui_kit` — Editor steps). Text set from Verse is a `<localizes>` message through a `message` field. Never bake words into textures.

Visibility swaps a layer without deleting the tree. `Collapsed` frees layout (and lets navigation skip the row). `Hidden` keeps the slot. `HitTestInvisible` paints and ignores hits.

Render transform is what animations key (`umg_animations`): translation, scale, shear, angle, pivot. Set the rest pose in the tree; key the change on the animation.

**Overrides that fail asset validation** even though they save and compile: `IsFocusable` on buttons, `Margin` on text blocks. Pad the slot instead. Buttons are focusable as they come (`umg_navigation`).

`ToggleWidgetAsVariable` marks a widget Is Variable when a binding must name it. `build_widget_tree` names every node; bindings use that name.
