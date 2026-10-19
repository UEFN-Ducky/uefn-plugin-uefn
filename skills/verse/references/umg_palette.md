---
description: "UEFN UMG palette — Verse UI Kit widgets first, classes ListWidgetClasses actually returns, slot type, Custom Button events, and classes AddWidget rejects (preset Loud/Quiet/Regular buttons)"
metadata:
  order: 66
  label: "UMG palette"
  default_enabled: false
  load_condition: "Choosing a UMG widget class, or AddWidget rejected a class name"
---

## UMG palette

Call `list_widget_classes` before any class name. `get_widget_class_info` returns the class description. The lists below are what a live UEFN editor returned. A later build can add classes; the tool result wins.

### Verse UI Kit widgets (first choice)

When the project has Epic's Verse UI Kit, `list_widget_classes` also returns its widgets as `UW_*_C` class paths under the kit root (`…/VerseUIKit/Widgets/Buttons/UW_Button_Toggle.UW_Button_Toggle_C`). Pass that full path as the class. Use kit widgets — buttons, inputs, containers, feedback, `UW_Shared_CloseButton`, and the composites — before any raw class below (`verse_ui_kit`).

### Panels

| class | Use |
|-------|-----|
| `CanvasPanel` | Root. Canvas slot: anchors, offsets, alignment, `z_order` |
| `Overlay` | Stacked layers. Overlay slot: padding, alignment |
| `GridPanel` | Fixed grid. Slot: row, column, row_span, column_span |
| `UniformGridPanel` | Equal cells |
| `StackBox` | Vertical or horizontal stack (shop rows) |
| `WrapBox` | Wrapping row |
| `ScrollBox` | Scroll. Slot is padding. There is no Verse scroll-offset API |
| `SizeBox` | Fixed desired size |
| `ScaleBox` | Scale to fit |
| `NamedSlot` | One hole a child User Widget or Verse fills |
| `WidgetSwitcher` | One visible child |
| `UIFrameworkCustomButtonWidget` | Custom Button. Alias `CustomButton`. The only raw button — the kit's buttons are built on it |

### Content

| class | Use |
|-------|-----|
| `Image` | Brush. `properties.brush_material` or `brush_texture` |
| `UEFN_TextBlock_C` | Text Block. Pass class `Text`. Placeholder label: `properties.text`; the real label is localizable `NSLOCTEXT` text (`umg_style`). Other properties (`font`, `colorAndOpacity`, `justification`, `autoWrapText`) via `list_properties` |
| `CommonActionWidget` | Input glyph |
| `ActionWidget` | Input prompt — shows the right glyph for the player's device (kit `PrevTab_Action` / `NextTab_Action`) |
| `DeveloperLayoutButtonProxy` | Editor layout proxy |

Project User Widgets also appear (`UW_Shop_OfferRow_C`). Nest those by class name from `list_widget_classes`.

### Text

The palette text class is `/Game/Valkyrie/UMG/UEFN_TextBlock.UEFN_TextBlock_C`. `Text`, `TextBlock`, and `UEFNTextBlockBase` all resolve to it. AddWidget alone cannot construct it ("classe non prise en charge"), so `add_widget_to_tree` and `build_widget_tree` add a placeholder Image and swap it with `ReplaceWidgetWithTemplate`. The name and slot are kept. Raw toolset calls must do the same two steps.

### AddWidget rejects these

Do not pass them. The tool raises before the editor call:

- Other text classes: `CommonTextBlock`, `RichTextBlock`, `UIFrameworkTextBlock`, `VerseFortniteUIFrameworkTextBlock`. Use `Text`.
- Preset buttons: `LoudButton`, `QuietButton`, `RegularButton`, and `VerseFortniteUIFrameworkButton_Loud` / `_Quiet` / `_Regular`. We never use them — every button is a custom one: a kit button, or `CustomButton` when the project has no kit.

`Button`, `ProgressBar`, and `Slider` were absent from `ListWidgetClasses`. A float Verse field drives a progress-style value when the class is missing (`umg_recipes` recipe 2).

### Custom Button events

`list_bindable_properties` on `UIFrameworkCustomButtonWidget` includes `OnClicked`, `OnPressed`, `OnReleased`, `OnHovered`, `OnUnhovered`, `OnButtonClicked`, `OnButtonHighlight`, `OnButtonUnhighlight`, plus `IsFocusable`, `RenderOpacity`, `RenderTransform`, `ColorAndOpacity`, `Visibility`. In 42.30 only `OnButtonClicked` / `OnButtonHighlight` / `OnButtonUnhighlight` compile as event-binding sources; the others fail with "The property path … is invalid". `IsFocusable` is listed but never override it — that fails asset validation (`umg_style`).

Bind with `bind_widget_event`. Highlight uses `OnButtonHighlight` / `OnButtonUnhighlight`. A kit button's click is its inner Custom Button: bind `<Child>.Main_Button.OnButtonClicked` / `<Child>.Root_Button.OnButtonClicked` (read the path from the child's tree) to a shared int event on your screen (`verse_ui_kit` — Clicks).
