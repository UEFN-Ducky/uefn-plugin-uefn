---
description: "Developer touchscreen layouts (v42.40) — move, restyle, re-icon or hide Fortnite's default touch buttons with a UMG layout (Canvas root + Touch Control Layout Override widgets = DeveloperLayoutButtonProxy) on a HUD Controller device; Apply Canvas Transform for icon-only overrides; hiding buttons from Verse by removing input mappings or cancelling subscriptions; 42.40 fixes"
metadata:
  label: "Touch layout override (HUD Controller, v42.40)"
---

# Developer touchscreen layouts

Fortnite's default touch buttons (Jump, Shoot, Crouch, Reload, Sprint, vehicle
controls, Backpack, Map Ping, Toggle Map …) can be moved, restyled, given a new icon or
hidden per island. This is separate from the player's own layout customization. Not
Virtual Pointer input — that is the rest of this skill.

## Build the layout (UMG)

1. Create a User Widget with a **Canvas** root (`create_widget_blueprint`,
   `build_widget_tree` — `umg_mcp_tools` in the verse skill).
2. Add one **Touch Control Layout Override** per button you change. The UMG class is
   `DeveloperLayoutButtonProxy` (`/Script/CRD_HUDController.DeveloperLayoutButtonProxy`,
   palette category *HUD Layout*). Buttons you don't add keep their default place.
3. Position and size each one with its canvas slot — the device reads the slot anchors.
4. Place a **HUD Controller** device, set **Override Touch Layout** to the widget, enable it.
   Another HUD Controller with another widget = another layout; enable the one you want
   (e.g. per game mode). No active override → the default Fortnite layout.

Properties (read live from the 42.40 class with `ObjectTools.list_properties`; set them
with `set_widget_property`):

| Property | Default | Meaning |
| --- | --- | --- |
| `action` | `Jump` | Which button: `Jump`, `Shoot`, `Crouch`, `Reload`, `SecondaryAbility`, `Sprint`, `VehicleBoost`, `VehicleHorn`, `VehicleJump`, `VehicleReverse`, `VehicleSecondaryAbility`, `VehicleSprint`, `VehicleSwitchSeat`, `VehicleThrottle`, `Backpack`, `MapPing`, `ToggleAutofire`, `ToggleMap`, `MoveStick`, `Interact`, `AlternateUse` |
| `bHideFromLayout` | false | Hide the button. Touch players can't use a hidden action — never hide one the game needs |
| `bOverrideIcon` + `iconBrush` | false | Replace the icon; the brush tint is the color override |
| `bApplyCanvasTransform` | **true** | **New in 42.40.** Uncheck for an *icon-only* override: position and size are ignored, so each player's own button layout stays where they put it |

## Hide buttons from Verse

The engine hides a default button whose action the island doesn't use (compiled 42.40):

```verse
using { /Fortnite.com/Input }
using { /Verse.org/Input }
using { /Verse.org/Simulation }

touch_buttons := class:
    var MaybeReloadSub:?cancelable = false

    OnReload(Args:tuple(player, logic)):void = {}

    # Removing a mapping context hides every touch button in it; adding it shows them again.
    HideWeaponButtons(Player:player):void =
        if (PlayerInput := GetPlayerInput[Player]):
            PlayerInput.RemoveInputMapping(Character.RangedWeaponMapping)

    ShowWeaponButtons(Player:player):void =
        if (PlayerInput := GetPlayerInput[Player]):
            PlayerInput.AddInputMapping(Character.RangedWeaponMapping)

    # A button shows while something subscribes to its action, and hides when that is cancelled.
    ShowReload(Player:player):void =
        if (PlayerInput := GetPlayerInput[Player]):
            Sub := PlayerInput.GetInputEvents(Character.Reload).TriggerActivationEvent.Subscribe(OnReload)
            set MaybeReloadSub = option{Sub}

    HideReload():void =
        if (Sub := MaybeReloadSub?):
            Sub.Cancel()
            set MaybeReloadSub = false
```

`TraversalMapping` (movement, jump) and `RangedWeaponMapping` (weapons) live in
`/Fortnite.com/Input` `Character`. Re-adding a mapping or re-subscribing restores the
buttons without duplicates; any `input_events` event (`BeginDetectEvent`,
`DetectionOngoingEvent`, `EndDetectEvent`, `CancelActivationEvent`) counts as using
the action.

## 42.40 fixes

- Items that turn Jump / Sprint into **Up** / **Boost** (e.g. the Mandalorian Jetpack)
  now work with an override layout.
- The Shoot button appears when the override references an empty widget.
- Carry / Drop can be overridden and removed.
- Overridden Sprint, Shoot, Reload and Crouch no longer capture touches — touches pass
  through to the controls behind them.

Test on a phone: Mobile Preview + UE Remote (SKILL.md "Testing on mobile").
