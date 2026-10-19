---
description: "Detect swipes and taps with Virtual Pointer (touch, mouse drag or left stick): gesture phases, distance threshold, direction and per-player state"
metadata:
  label: "Swipe"
---

# Swipe / tap detection with Virtual Pointer

Detect when the player swipes a finger in a direction, or takes the equivalent action with mouse drag or gamepad left-stick drag. Uses only `TouchMapping` + `PointerSelect`, so it is **publishable**.

## Gesture phases

| Phase | Event | Payload | Do |
|-------|-------|---------|----|
| 1 | `BeginDetectEvent` | `tuple(player, vector3)` | Cache start position |
| 2 | `TriggerActivationEvent` | `tuple(player, vector3)` | Fires repeatedly while held — update current position |
| 3 | `EndDetectEvent` | `tuple(player, float)` | Pointer up; compute delta, classify, fire swipe or tap |

`EndDetectEvent` carries **no position**, only elapsed seconds — that is why phases 1–2 cache it.

## Threshold

Distance is compared **squared, in screen-cm²**. `MinSwipeDistanceSq = 0.25` = 0.5 cm. Below it is a tap.

## Direction classification

`Left` grows rightward, `Up` grows upward. `Abs` compiles (it is a compiler intrinsic the digest does not list); the template keeps a tiny local helper so the file is self-contained:

```verse
ClassifySwipe(DeltaLeft : float, DeltaUp : float):swipe_direction =
    AbsLeft := AbsF(DeltaLeft)
    AbsUp := AbsF(DeltaUp)
    if (AbsLeft >= AbsUp):
        if (DeltaLeft > 0.0) then swipe_direction.Right else swipe_direction.Left
    else:
        if (DeltaUp > 0.0) then swipe_direction.Up else swipe_direction.Down

AbsF(X : float):float =
    if (X < 0.0) then -X else X
```

## Device (per-player state)

Epic's sample keeps one `StartPos` on the device, which breaks with two players gesturing at once. Keep state per player:

```verse
using { /Fortnite.com/Devices }
using { /Fortnite.com/Playspaces }
using { /Verse.org/Simulation }
using { /Verse.org/Input }
using { /Verse.org/Input/UI }
using { /Verse.org/SpatialMath }
using { /UnrealEngine.com/Temporary/Diagnostics }

swipe_direction := enum:
    None
    Up
    Down
    Left
    Right

swipe_result := struct:
    StartPosition : vector3
    EndPosition : vector3
    Direction : vector3        # Left/Up only, Forward = 0
    SwipeDistSq : float        # screen-cm²
    Duration : float           # seconds
    Cardinal : swipe_direction

swipe_detector_device := class(creative_device):

    @editable
    MinSwipeDistanceSq : float = 0.25

    var StartByPlayer : [player]vector3 = map{}
    var CurrentByPlayer : [player]vector3 = map{}
    var TrackingByPlayer : [player]logic = map{}
    var SubsByPlayer : [player][]cancelable = map{}

    OnBegin<override>()<suspends>:void =
        Playspace := GetPlayspace()
        for (Player : Playspace.GetPlayers()):
            SubscribeInput(Player)
        Playspace.PlayerAddedEvent().Subscribe(SubscribeInput)

    OnEnd<override>():void =
        for (Player -> Subs : SubsByPlayer):
            for (Sub : Subs):
                Sub.Cancel()
            if (PlayerInput := GetPlayerInput[Player]):
                PlayerInput.RemoveInputMapping(TouchMapping)
        set SubsByPlayer = map{}

    SubscribeInput(Player : player):void =
        if (PlayerInput := GetPlayerInput[Player]):
            PlayerInput.AddInputMapping(TouchMapping)
            Events := PlayerInput.GetInputEvents(PointerSelect)
            BeginSub := Events.BeginDetectEvent.Subscribe(OnPointerDown)
            MoveSub := Events.TriggerActivationEvent.Subscribe(OnPointerMove)
            EndSub := Events.EndDetectEvent.Subscribe(OnPointerUp)
            if (set SubsByPlayer[Player] = array{BeginSub, MoveSub, EndSub}) {}

    OnPointerDown(Arg : tuple(player, vector3)):void =
        Player := Arg(0)
        if (set StartByPlayer[Player] = Arg(1)) {}
        if (set CurrentByPlayer[Player] = Arg(1)) {}
        if (set TrackingByPlayer[Player] = true) {}

    OnPointerMove(Arg : tuple(player, vector3)):void =
        Player := Arg(0)
        if (TrackingByPlayer[Player]?):
            if (set CurrentByPlayer[Player] = Arg(1)) {}

    OnPointerUp(Arg : tuple(player, float)):void =
        Player := Arg(0)
        if (TrackingByPlayer[Player]?, Start := StartByPlayer[Player], Current := CurrentByPlayer[Player]):
            if (set TrackingByPlayer[Player] = false) {}
            DeltaLeft := Current.Left - Start.Left
            DeltaUp := Current.Up - Start.Up
            DistSq := (DeltaLeft * DeltaLeft) + (DeltaUp * DeltaUp)
            if (DistSq >= MinSwipeDistanceSq):
                HandleSwipe(Player, swipe_result{
                    StartPosition := Start
                    EndPosition := Current
                    Direction := vector3{Forward := 0.0, Left := DeltaLeft, Up := DeltaUp}
                    SwipeDistSq := DistSq
                    Duration := Arg(1)
                    Cardinal := ClassifySwipe(DeltaLeft, DeltaUp)
                })
            else:
                HandleTap(Player, Start)

    HandleSwipe(Player : player, Result : swipe_result):void =
        Print("SWIPE {SwipeDirectionToString(Result.Cardinal)} DistSq:{Result.SwipeDistSq} {Result.Duration}s")

    HandleTap(Player : player, Position : vector3):void =
        Print("TAP at ({Position.Left}, {Position.Up})")

    # ClassifySwipe / AbsF as above; SwipeDirectionToString via case (Dir): swipe_direction.Up => "Up" …
```

Full compiling file: `verse_template_apply("vp_swipe_detector")` → `Verse/VirtualPointer/swipe_detector_device.verse`.

## Notes

- The same path works for touch swipe, mouse drag, and gamepad pointer drag.
- Does not fire while Fortnite menus are open.
- Combine with `screenspace_trace.md` to swipe-select world objects (deproject `Start` and `Current`).
