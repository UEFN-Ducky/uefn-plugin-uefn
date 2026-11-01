---
description: "PointerZoom (publishable from 43.00; Experimental on 42.x): pinch, mouse wheel and right-stick zoom, the 43.00 50x touch value change, logging it and scaling a Scene Graph entity with pinch"
metadata:
  label: "Pinch zoom"
---

# PointerZoom — pinch, scroll, right-stick zoom / scale

`PointerZoom` is an `input_action(vector3)` in `/Verse.org/Input/UI` (FN ≥ 4120). **43.00: out of Experimental, so islands that use it can be published.** On a 42.x island it is still `@experimental` and blocks publishing.

**43.00 breaking change:** touch pinch values are now **50× larger** to match mouse wheel and gamepad. Any threshold or sensitivity tuned on 42.x touch is now 50× too sensitive on phones. Divide sensitivities by 50 and multiply dead-zones by 50, then retune on a device (Mobile Preview / UE Remote). Mouse and gamepad values didn't change.

Pinch is a continuous input for camera zoom and object scaling. The pinch magnitude arrives in the payload's `vector3.Forward`.

| Device | Control | Value | Center |
|--------|---------|-------|--------|
| Touch | Two fingers together / apart | Speed of pinch, now on roughly the same scale as wheel and stick (50× the 42.x value); `0` = no change | Midpoint between the fingers |
| Mouse + keyboard | Scroll wheel | `-1` to `1` by direction; freewheel mode behaves more like a stick | Current pointer position |
| Controller | Right stick Up = zoom in, Down = zoom out | Deflection from neutral `-1`…`1` | Virtual Pointer position |

## Subscribe (zoom logging)

```verse
using { /Verse.org/Input }
using { /Verse.org/Input/UI }
using { /Verse.org/SpatialMath }
using { /Verse.org/Simulation }

EnableCursorZoom(Player : player):void =
    if (PlayerInput := GetPlayerInput[Player]):
        PlayerInput.AddInputMapping(TouchMapping)
        ZoomEvents := PlayerInput.GetInputEvents(PointerZoom)
        BeginSub := ZoomEvents.BeginDetectEvent.Subscribe(OnPinchBegin)
        OngoingSub := ZoomEvents.DetectionOngoingEvent.Subscribe(OnPinchOngoing)
        TriggerSub := ZoomEvents.TriggerActivationEvent.Subscribe(OnPinchTrigger)
        EndSub := ZoomEvents.EndDetectEvent.Subscribe(OnPinchEnd)
        # keep BeginSub/OngoingSub/TriggerSub/EndSub in a [player][]cancelable map

OnPinchBegin(Arg : tuple(player, vector3)):void =
    Print("PINCH begin | Fwd={Arg(1).Forward}")

OnPinchOngoing(Arg : tuple(player, vector3, float)):void =
    Print("PINCH ongoing | Fwd={Arg(1).Forward}")

OnPinchTrigger(Arg : tuple(player, vector3)):void =
    Print("PINCH trigger | Fwd={Arg(1).Forward}")

OnPinchEnd(Arg : tuple(player, float)):void =
    Print("PINCH end")
```

Which live phase fires (`DetectionOngoing` vs `TriggerActivation`) depends on platform/input, so route **both** into the same apply function.

## Resizing a Scene Graph entity (pinch-to-scale)

1. Place Actors → Entities → `entity`.
2. `+ Component` → `mesh_component` (e.g. Cube).
3. Place the device; set `PropToScale` to that entity in Details.

Core of the device (full file: `verse_template_apply("vp_pinch_scale")`):

```verse
using { /Verse.org/SceneGraph }
using { /Verse.org/SpatialMath }

@editable
var PropToScale : entity = entity{}
@editable
var ScaleSensitivity : float = 2.0      # 42.x touch value; on 43.00 touch start near 0.04
@editable
var MinScale : float = 0.25
@editable
var MaxScale : float = 5.0
@editable
var MinPinchAmount : float = 0.001      # 42.x touch dead-zone; on 43.00 start near 0.05

var CurrentScale : float = 1.0
var BaseScale : vector3 = vector3{Forward := 1.0, Left := 1.0, Up := 1.0}

OnBegin<override>()<suspends>:void =
    set BaseScale = PropToScale.GetGlobalTransform().Scale
    # ... EnableFor each player + PlayerAddedEvent

OnZoomOngoing(Arg : tuple(player, vector3, float)):void =
    ApplyPinch(Arg(1).Forward)

OnZoomTrigger(Arg : tuple(player, vector3)):void =
    ApplyPinch(Arg(1).Forward)

ApplyPinch(Forward : float):void =
    if (Forward > MinPinchAmount or Forward < -MinPinchAmount):
        # Exp keeps scaling smooth and symmetric; negated so pinch direction matches expectation.
        Proposed := CurrentScale * Exp(-Forward * ScaleSensitivity)
        set CurrentScale = Max(MinScale, Min(MaxScale, Proposed))
        T := PropToScale.GetGlobalTransform()
        NewScale := vector3{
            Forward := BaseScale.Forward * CurrentScale
            Left := BaseScale.Left * CurrentScale
            Up := BaseScale.Up * CurrentScale
        }
        PropToScale.SetGlobalTransform(transform{Translation := T.Translation, Rotation := T.Rotation, Scale := NewScale})
```

Digest: `(InEntity:entity).GetGlobalTransform()<transacts>:transform` and `SetGlobalTransform(NewGlobalTransform:transform)<transacts>:void` in `/Verse.org/SceneGraph`; `Exp(X:float)<reads>:float`, `Min/Max(X:float, Y:float)`.

## Cleanup

Cancel all four subscriptions per player in `OnEnd` and `RemoveInputMapping(TouchMapping)`.

Never dump the device at `Content/Verse/` root — `Verse/VirtualPointer/pinch_scale_device.verse`.
