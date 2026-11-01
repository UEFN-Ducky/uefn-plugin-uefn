---
description: "UMG Widget Animations — create, bind, opacity color and transform keys, highlight and loop playback"
metadata:
  order: 70
  label: "UMG widget animations"
  default_enabled: false
  load_condition: "Authoring a UMG Widget Animation, highlight, loop, or color keyframes"
---

## Widget Animations

These are `UWidgetAnimation` tracks, not `play_animation_device`. Verse cannot call `PlayAnimation` by name. Playback is a View Binding (`umg_view_bindings`) or a Verse `logic` / float field the binding watches. Preview in the UMG editor (42.20). Do not Launch Session to check a button animation.

Kit buttons already carry the kit's shared highlight, so hover and gamepad focus look the same. Animate your own screen's widgets (or the images you put in a kit widget's named slots), never the kit widgets themselves.

### Tools

1. `create_widget_animation(widget_path, animation_name, length_seconds)`
2. `add_animation_keys(...)` binds the widget, adds the track, and keys it.
3. `list_widget_animations` / `get_widget_blueprint_info` → `animations[].tracks[].key_count`

`track_type`:

| track_type | Track | Channel |
|------------|-------|---------|
| `Opacity` | `RenderOpacity` | one float channel |
| `Color` | `ColorAndOpacity` | `R` `G` `B` `A` |
| `Transform` | `RenderTransform` | `TranslationX` `TranslationY` `ScaleX` `ScaleY` `ShearX` `ShearY` `Angle` |

Keys are `{time, value}` in seconds. Two keys minimum (start pose, end pose). A hover wobble uses three keys (1 → 1.06 → 1). Material-parameter channels on the brush are not a MovieScene track here. Drive `ColorFill` / `ColorShadow` / `ColorStroke` with a Verse float or color field and a conversion (`umg_ui_materials`).

### Custom Button graph

| Widget event | Binding |
|--------------|---------|
| `OnButtonHighlight` | Play `Anim_Highlight` forward, and play `Anim_Loop` looped (template uses 999 loops, speed 1.0) |
| `OnButtonUnhighlight` | Reverse `Anim_Highlight`, stop `Anim_Loop` |
| `OnButtonClicked` | Signal the screen's click event, e.g. `OnPlayClicked` (`umg_verse_field_events`; `OnClicked` fails to compile in 42.30) |

`bind_widget_event` writes the event → Verse field link. Queue Play / Queue Stop pins (forward, reverse, loop count, speed) are View Binding pins. When that destination is not a field path, keep the animation keys in the asset and trigger them by the field the binding already watches (`IsIntroActive` bool). Auto Play only for motion that starts on construct. Keyframes the tools can't reach are a manual step for the user (Animations panel).

### Play on show (pop-up in, hold, out)

One float Verse field drives it, e.g. `PopupState`: a View Binding with a condition plays the
animation forward at `1.0` and reverse at `2.0`. Give the field the play value as its default (or
`set` it right after `AddWidget`) so the animation starts the moment the widget is shown:

```verse
Popup := UW_FindShopkeeperPopup{}          # Assets digest name
PlayerUI.AddWidget(Popup)
set Popup.PopupState = 1.0                 # slide in
Sleep(AnimSeconds + HoldSeconds)
set Popup.PopupState = 2.0                 # reverse out
Sleep(AnimSeconds)
PlayerUI.RemoveWidget(Popup)
```

A new field is missing from Verse until the Assets digest regenerates: build once after making
the field, then build Verse again (`umg_verse_fields`).

### Widgets placed in the level

In-game UI widgets can be dragged into the scene and scaled with the transform. A widget whose
animation starts at opacity 0 is invisible to click on: put an Overlay at the root with a
1920 × 1080 Image behind the content, then set that Image's alpha to 0 once it's placed. Auto Play
(or the field's default) runs a looping animation (letter-by-letter title, flashing sale text) with
no Verse.

`Anim_Highlight` opacity 0.45 → 1 over 0.35s and `Anim_Loop` scale 1 → 1.06 → 1 over 0.8s is the verified shape (`umg_recipes` recipe 3).
