---
description: "Interactive UI menus — Verse UI Kit screens first; code-built canvas modals, shops, collect screens with ui_input_mode.All, open/close, Back, ButtonToAgent map (custom buttons only → sys_custom_buttons)"
metadata:
  order: 37
  label: "Game systems — UI menus & modals (UIMenuController)"
  default_enabled: false
  load_condition: "Building interactive Verse UI — shops, collect popups, pickers, tabbed menus with button clicks and ui_input_mode.All"
---

## UI menus & modals — UIMenuController

> **Snippets here are fragments.** The `using` block in this file's first code
> block applies to all of them — copy those imports (or start from the matching
> `verse_template_apply` pack) when pasting into a real `.verse` file.

**Menus are Verse UI Kit screens first** (`verse_ui_kit`): kit composites
(dialog, settings panel, menu, list, grid) in UMG, driven by the kit's
`ui_helper_function_library` — focus, menu navigation, Back and cleanup come
with it. This file is the code-built canvas version, for when a menu must be
built in Verse.

Interactive screens **capture** player input. Layouts come from
`sys_canvas_cookbook` (modal, shop list, tabs). Show/hide wiring mirrors
`sys_hud_template` but uses `ui_input_mode.All`.

**Buttons are always custom:** load **`sys_custom_buttons` first** — the
chrome-less native `button` + `SetFocus`. Never stock `button_loud` /
`button_quiet` / `button_regular`, not even for a plain text CTA.
Repeating rows are one card widget in a stack.

### Modal recipe

1. Build canvas: full-screen dim `color_block` + centered panel + title/body +
   action buttons (cookbook **modal**). Prefer `MakeUiLabelButton` /
   `MakeUiButton` from `sys_custom_buttons` (or project `ui_buttons.verse`).
2. Show — **SetFocus before AddWidget** (required for controller):

```verse
ShowMenu(Agent : agent) : void =
    if (Player := player[Agent], PlayerUI := GetPlayerUI[Player]):
        set MenuCanvas = BuildMenuCanvas()
        PlayerUI.SetFocus(ConfirmButton)   # or ConfirmUi.Btn — BEFORE AddWidget
        PlayerUI.AddWidget(MenuCanvas, player_ui_slot{ InputMode := ui_input_mode.All })
        # map buttons → agent so click handlers know who clicked
        if (set ButtonToAgent[ConfirmButton] = Agent) {}
```

3. Close (restore control):

```verse
CloseMenu(Agent : agent) : void =
    if (Player := player[Agent], PlayerUI := GetPlayerUI[Player]):
        PlayerUI.RemoveWidget(MenuCanvas)
        set MenuCanvas = canvas{}
```

Never leave `.All` widgets up after the menu is done — the player stays trapped.
Modal with **no** focusable buttons → `InputMode.None` (else gamepad soft-lock).

### Buttons

Always the chrome-less native `button` — see **`sys_custom_buttons`**. A plain
text CTA is its Recipe A label button:

```verse
ConfirmUi := MakeUiLabelButton(PrimaryStyle(), "CONFIRM")
set ConfirmButton = ConfirmUi.Btn                 # var ConfirmButton : button
ConfirmButton.OnClick().Subscribe(OnConfirmClicked)
# still: PlayerUI.SetFocus(ConfirmButton) before AddWidget

OnConfirmClicked(WM : widget_message) : void =
    if (Agent := ButtonToAgent[ConfirmButton]):
        HandleConfirm(Agent)
        CloseMenu(Agent)
```

Keep `var ButtonToAgent : [button]agent = map{}`. Rebuild with `if (set …) {}` —
avoid `ConcatenateMaps` on button keys (widens to `widget`).

**Back closes the menu** like a kit screen: inside
`if (PlayerInput := GetPlayerInput[Player]):` listen to the release of Back
(`PlayerInput.GetInputEvents(UI.Back).EndDetectEvent`, kit
`Helper.SubscribeToEvent` — `verse_ui_kit` Input) and call `CloseMenu`.

### Shop menu

Cookbook **panel + vertical shop lines**. Each buy button →
`GetGamePlayer` → `EconomyManager` check/charge → granter → `SyncShopUI` /
close. HUD feedback via `hud_message_device` optional (`sys_economy`).

### Collect / offline popup

Show calculated earnings text; Confirm credits `EconomyManager` then closes.
Used after offline calc (`sys_generators` offline section). Do **not** auto-grant
if you want an explicit Collect click.

### Input-mode / picker menus

Same modal pattern; on choice call another controller (e.g. camera input mode).
Optional open hotkey via `input_trigger_device` (`sys_input_devices`) while the
menu itself stays `.All`.

### Passive HUD vs menu

| | HUD (`sys_hud_template`) | Menu (this file) |
|--|--------------------------|------------------|
| InputMode | `.None` | `.All` (+ `SetFocus`) |
| Buttons | none | `sys_custom_buttons` (custom only) |
| Lifetime | often whole session | open → act → close |

### Gotchas

- Visibility checklist still applies (`sys_canvas_cookbook`).
- Stacking two `.All` menus without removing the first confuses input.
- Look up buyer with `GetGamePlayer` — never assume the click agent is registered.
- Gamepad dead without `SetFocus` — see `sys_custom_buttons`.
