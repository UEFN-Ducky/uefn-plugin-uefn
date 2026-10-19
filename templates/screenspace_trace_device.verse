# SETUP: Place this creative_device in the level. Every player enters Virtual Pointer mode on join
# (TouchMapping) and is immobilized. PointerSelect + TouchMapping are publishable.
# Tap / click / left-stick select -> deproject the screen point -> sweep a ray into the world.
using { /Fortnite.com/Devices }
using { /Fortnite.com/Playspaces }
using { /Verse.org/Simulation }
using { /Verse.org/SceneGraph }
using { /Verse.org/Input }
using { /Verse.org/Input/UI }
using { /Verse.org/SpatialMath }
using { /UnrealEngine.com/Temporary/Diagnostics }

screenspace_trace_device := class(creative_device):

    # How far (cm) to sweep along the pointer ray. Tune for your island scale.
    @editable
    MaxTraceDistance : float = 50000.0

    var SubsByPlayer : [player][]cancelable = map{}

    OnBegin<override>()<suspends>:void =
        Playspace := GetPlayspace()
        for (Player : Playspace.GetPlayers()):
            StartSubscription(Player)
        Playspace.PlayerAddedEvent().Subscribe(StartSubscription)

    # Cancel subscriptions and leave Virtual Pointer mode.
    OnEnd<override>():void =
        for (Player -> Subs : SubsByPlayer):
            for (Sub : Subs):
                Sub.Cancel()
            if (PlayerInput := GetPlayerInput[Player]):
                PlayerInput.RemoveInputMapping(TouchMapping)
        set SubsByPlayer = map{}

    StartSubscription(Player : player):void =
        if (PlayerInput := GetPlayerInput[Player]):
            # TouchMapping puts the player in Virtual Pointer mode (movement disabled).
            PlayerInput.AddInputMapping(TouchMapping)
            BeginSub := PlayerInput.GetInputEvents(PointerSelect).BeginDetectEvent.Subscribe(PlayerClicked)
            if (set SubsByPlayer[Player] = array{BeginSub}) {}
            Print("screenspace_trace_device: Virtual Pointer enabled")

    # BeginDetectEvent payload: (player, screen position vector3 - Left/Up in cm, Forward unused)
    PlayerClicked(Arg : tuple(player, vector3)):void =
        Player := Arg(0)
        ClickPos := Arg(1)

        Ray := TraceFromClick(Player, ClickPos.Left, ClickPos.Up)
        RayOrigin := Ray.Origin
        RayDir := Ray.Direction

        # Sweep: ray direction * max distance
        Displacement := RayDir * MaxTraceDistance

        # Start at the ray origin (camera eye point - see deproject_results docs)
        StartTransform := transform{Translation := RayOrigin}

        # Point trace along the ray
        CollisionShape := collision_point{}

        Hits := for:
            Hit : GetSimulationEntity[].FindSweepHits(Displacement, StartTransform, CollisionShape)
        do:
            Hit

        if (FirstHit := Hits[0]):
            Print("HIT something at {FirstHit.ContactPosition}")
        else:
            Print("MISS")

    # Screen (cm) -> world ray. Only Left/Up are used; Forward is ignored.
    TraceFromClick(Player : player, ClickX : float, ClickY : float)<reads>:deproject_results =
        Player.DeprojectViewportToWorld(vector3{Left := ClickX, Up := ClickY, Forward := 0.0})
