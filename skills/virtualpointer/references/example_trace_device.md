---
description: "Complete publishable Verse device: enables Virtual Pointer for every player, listens to PointerSelect and reports the world objects under the pointer"
metadata:
  label: "Example trace device"
---

# Example: screenspace_trace_device

Complete Verse device that turns on Virtual Pointer mode for every player, subscribes to `PointerSelect`, and reports world objects that intersect the pointer trace. Uses only `TouchMapping` + `PointerSelect`, so it is **publishable**.

Place under `Verse/VirtualPointer/screenspace_trace_device.verse` — never at `Content/Verse/` root. Same file as `verse_template_apply("vp_screenspace_trace")`.

Fixes vs Epic's doc sample: the doc omits `using { /Verse.org/SceneGraph }` (so `collision_point` / `FindSweepHits` are unknown), declares `MaybeInputCancelableBegin` twice (once inside `OnBegin`), and never calls `StartSubscription`. This version compiles: it subscribes existing players plus `PlayerAddedEvent`, keeps cancelables per player, and cleans up in `OnEnd`.

```verse
using { /Fortnite.com/Devices }
using { /Fortnite.com/Playspaces }
using { /Verse.org/Simulation }
using { /Verse.org/SceneGraph }
using { /Verse.org/Input }
using { /Verse.org/Input/UI }
using { /Verse.org/SpatialMath }
using { /UnrealEngine.com/Temporary/Diagnostics }

screenspace_trace_device := class(creative_device):

    # How far (cm) to sweep along the pointer ray.
    @editable
    MaxTraceDistance : float = 50000.0

    var SubsByPlayer : [player][]cancelable = map{}

    OnBegin<override>()<suspends>:void =
        Playspace := GetPlayspace()
        for (Player : Playspace.GetPlayers()):
            StartSubscription(Player)
        Playspace.PlayerAddedEvent().Subscribe(StartSubscription)

    OnEnd<override>():void =
        for (Player -> Subs : SubsByPlayer):
            for (Sub : Subs):
                Sub.Cancel()
            if (PlayerInput := GetPlayerInput[Player]):
                PlayerInput.RemoveInputMapping(TouchMapping)
        set SubsByPlayer = map{}

    StartSubscription(Player : player):void =
        if (PlayerInput := GetPlayerInput[Player]):
            PlayerInput.AddInputMapping(TouchMapping)
            BeginSub := PlayerInput.GetInputEvents(PointerSelect).BeginDetectEvent.Subscribe(PlayerClicked)
            if (set SubsByPlayer[Player] = array{BeginSub}) {}

    PlayerClicked(Arg : tuple(player, vector3)):void =
        Player := Arg(0)
        ClickPos := Arg(1)

        Ray := TraceFromClick(Player, ClickPos.Left, ClickPos.Up)
        Displacement := Ray.Direction * MaxTraceDistance
        StartTransform := transform{Translation := Ray.Origin}
        CollisionShape := collision_point{}

        Hits := for:
            Hit : GetSimulationEntity[].FindSweepHits(Displacement, StartTransform, CollisionShape)
        do:
            Hit

        if (FirstHit := Hits[0]):
            Print("HIT something at {FirstHit.ContactPosition}!")
        else:
            Print("MISS")

    TraceFromClick(Player : player, ClickX : float, ClickY : float)<reads>:deproject_results =
        Player.DeprojectViewportToWorld(vector3{Left := ClickX, Up := ClickY, Forward := 0.0})
```

After writing: `workspace_list_verse_errors`, then place the device. If players must walk while the pointer is on, call `Player.GetFortCharacter[].ReleaseFromStasis()` after `AddInputMapping` (see `enable_disable.md`).
