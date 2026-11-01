---
description: "PointerSelect screen-space coordinates: units and axes, subscribing after TouchMapping, the input events it fires and cleanup"
metadata:
  label: "PointerSelect"
---

# PointerSelect — screen-space coordinates

`PointerSelect` is an `input_action(vector3)` in `/Verse.org/Input/UI` (FN ≥ 4100, **publishable**). The `vector3` carries the screen-space pointer position.

## Screen coordinate system

- Units: **centimeters**.
- `Left`: horizontal, positive **rightward** from the top-left corner.
- `Up`: vertical, positive **upward** (points below the top edge are negative).
- `Forward`: unused (0).

## Subscribe after enabling TouchMapping

```verse
using { /Verse.org/Input }
using { /Verse.org/Input/UI }
using { /Verse.org/SpatialMath }
using { /Verse.org/Simulation }

var SubsByPlayer : [player][]cancelable = map{}

StartSubscription(Player : player):void =
    if (PlayerInput := GetPlayerInput[Player]):
        PlayerInput.AddInputMapping(TouchMapping)
        BeginSub := PlayerInput.GetInputEvents(PointerSelect).BeginDetectEvent.Subscribe(PlayerClicked)
        if (set SubsByPlayer[Player] = array{BeginSub}) {}

PlayerClicked(Arg : tuple(player, vector3)):void =
    Player := Arg(0)
    ClickPos := Arg(1)
    # ClickPos.Left / ClickPos.Up are screen-space cm
```

## Event surface (`input_events(vector3)`)

| Event | Handler signature | When |
|-------|-------------------|------|
| `BeginDetectEvent` | `(Arg : tuple(player, vector3))` | Pointer down. Always paired with EndDetect. |
| `DetectionOngoingEvent` | `(Arg : tuple(player, vector3, float))` | Held, not yet triggered. `float` = elapsed seconds. |
| `TriggerActivationEvent` | `(Arg : tuple(player, vector3))` | Fired. Repeats while held — use it for pointer move / drag. |
| `CancelActivationEvent` | `(Arg : tuple(player, vector3, float))` | Canceled before activation. |
| `EndDetectEvent` | `(Arg : tuple(player, float))` | Pointer up. `float` = elapsed seconds. **No position** — cache from Begin/Trigger. |

Flow: `BeginDetect → DetectionOngoing → TriggerActivation → EndDetect` (or `CancelActivation → EndDetect`).

Tap vs drag: Begin caches the start position, Trigger updates the current position, End compares them (see `swipe.md`).

## Cleanup

Keep every `cancelable` per player and `.Cancel()` them in `OnEnd` / when leaving the mode, then `RemoveInputMapping(TouchMapping)` if exiting Virtual Pointer.

## Next steps

- World hit-test: `screenspace_trace.md` (`DeprojectViewportToWorld` + `FindSweepHits`).
- Swipes / taps: `swipe.md`.
- Pinch: `pinch_zoom.md` (`PointerZoom`, publishable from 43.00).
- Template: `verse_template_apply("vp_screenspace_trace")`.
