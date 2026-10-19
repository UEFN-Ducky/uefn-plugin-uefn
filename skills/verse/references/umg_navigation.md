---
description: "UMG gamepad, keyboard and touch the Verse UI Kit way — Desired Focus Widget, FocusWidgetForPlayer after showing, MenuNavigationMapping, Back through UW_Shared_CloseButton, refocus after page/tab changes, collapse empty rows, InputMode rules"
metadata:
  order: 71
  label: "UMG navigation"
  default_enabled: false
  load_condition: "Gamepad or controller focus on a UMG menu or Custom Button, Back to close, or menu navigation input"
---

## UMG navigation

Every interactive screen works on gamepad, keyboard and mouse: focus lands on its first control when it opens (or the safest default, such as Cancel on a destructive confirm), every control is reachable by gamepad and arrow keys, focus is always visible, and Back closes the screen. Full rules: `verse_ui_kit` — Input.

### Focus

1. Set the screen's **Desired Focus Widget** (Class Defaults) to its first control: `set_widget_property(widget_path, "<package>.Default__<Name>_C", {"DesiredFocusWidget": {"widgetName": "<first control>"}})` on the class default object (verified in UEFN 42.30: survives compile, save and reload). Older Ducky builds: Epic's `ObjectTools` call in `verse_ui_kit` — Editor steps. Can't set it → list it as a manual step.
2. Show the screen, **then** focus it: kit `Helper.FocusWidgetForPlayer(Player, Widget)` after the widget is on screen. Without the kit, `PlayerUI.SetFocus(Widget)` after `AddWidget`.
3. After anything that changes which controls exist (tab, page, filter), focus again — or focus can sit on a control that just disappeared.
4. Focus order follows reading order. Hover and gamepad focus look the same (the kit's shared highlight does both; without the kit, bind `OnButtonHighlight` / `OnButtonUnhighlight` to the same highlight animation — `umg_animations`).

Kit buttons and UEFN Custom Buttons are focusable as they come. Never override `IsFocusable` on a button: it saves and compiles but fails asset validation. Never use the preset Loud/Quiet/Regular buttons to get focus — every button is a custom one.

### Input modes and mappings

| Screen | Input |
|--------|-------|
| Menu, shop, dialog | `player_ui_slot{ InputMode := ui_input_mode.All }` + `Helper.AddInputMappingToPlayer(Player, UI.MenuNavigationMapping)`; `Helper.ClearAllForPlayer` turns it off |
| HUD, toast | `ui_input_mode.None` — never steals input or blocks clicks |
| UI during gameplay | gameplay input (`Character.*` mappings), not menu navigation |

A modal with zero focusable widgets must use `ui_input_mode.None` — `.All` with nothing to focus soft-locks the gamepad. If you freeze the player (`Helper.HoldPlayerStill`), release them (`Helper.ReleasePlayer`) on every way out.

### Back

Put the kit's `UW_Shared_CloseButton` in the screen and bind both its inner buttons to the screen's `OnCloseClicked` event: `<Child>.Close_Button.Root_Button.OnButtonClicked` (mouse, touch, A) and `<Child>.CloseAction_Button.OnButtonClicked` (Back). The Back prompt only fires while focus is inside that widget. A close button added beside the screen from Verse needs a Verse listener on the release of Back: `Helper.SubscribeToEvent(Player, PlayerInput.GetInputEvents(UI.Back).EndDetectEvent, OnBack)` inside `if (PlayerInput := GetPlayerInput[Player]):`.

### Rows, tabs, pages

- Tab rows and pagers send `-1` / `+1` through `OnNavigateTab(int)` / `OnNavigatePage(int)`, with `PrevTab_Action` / `NextTab_Action` ActionWidgets for the shoulder buttons.
- Collapse empty rows so navigation skips them: a bool field bound to `Visibility` (default conversion: `true` shows, `false` collapses). Never leave a focusable control with no visible content.
- Set explicit navigation (up / down / left / right) only when the controls are not in one stack the designer can wrap.
- Input prompts use ActionWidgets so the glyph matches the player's device. Touch: `Helper.WatchInputMethodForPlayer` reports input-method changes (an `IsMobile` field).

One widget instance per player. Focus the instance you just added, not a shared widget.
