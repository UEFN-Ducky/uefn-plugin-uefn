# SETUP: Pinch (touch) / scroll wheel (mouse) / right stick (gamepad) to grow or shrink a Scene Graph entity.
# 1. Place Actors -> Entities -> entity; add a mesh_component (e.g. Cube).
# 2. Place this device and set PropToScale to that entity in Details.
# EXPERIMENTAL: PointerZoom cannot be published yet. Remove this device before publishing.
using { /Verse.org/Simulation }
using { /Verse.org/SceneGraph }
using { /Verse.org/SpatialMath }
using { /Verse.org/Input }
using { /Verse.org/Input/UI }
using { /Fortnite.com/Game }
using { /Fortnite.com/Devices }
using { /Fortnite.com/Playspaces }
using { /UnrealEngine.com/Temporary/Diagnostics }

pinch_scale_device := class(creative_device):

    # Log what the pinch is doing.
    @editable
    var PrintPinchToLog : logic = true

    # The pinch fires many times per gesture; this logs every one (noisy).
    @editable
    var PrintEveryPinchUpdate : logic = false

    # Pinches smaller than this are ignored (filters resting-finger jitter).
    @editable
    var MinPinchAmount : float = 0.001

    # Bigger = the prop reacts more per pinch.
    @editable
    var ScaleSensitivity : float = 2.0

    @editable
    var MinScale : float = 0.25

    @editable
    var MaxScale : float = 5.0

    # The Scene Graph entity to resize. Assign in the editor.
    @editable
    var PropToScale : entity = entity{}

    # Accumulated multiplier. 1.0 = the prop's original size.
    var CurrentScale : float = 1.0

    # Authored scale captured at start so proportions are preserved.
    var BaseScale : vector3 = vector3{Forward := 1.0, Left := 1.0, Up := 1.0}

    var SubsByPlayer : [player][]cancelable = map{}

    OnBegin<override>()<suspends>:void =
        set BaseScale = PropToScale.GetGlobalTransform().Scale
        Playspace := GetPlayspace()
        for (Player : Playspace.GetPlayers()):
            EnableFor(Player)
        Playspace.PlayerAddedEvent().Subscribe(EnableFor)

    OnEnd<override>():void =
        for (Player -> Subs : SubsByPlayer):
            for (Sub : Subs):
                Sub.Cancel()
            if (PlayerInput := GetPlayerInput[Player]):
                PlayerInput.RemoveInputMapping(TouchMapping)
        set SubsByPlayer = map{}

    EnableFor(Player : player):void =
        if (PlayerInput := GetPlayerInput[Player]):
            # TouchMapping registers the gesture so PointerZoom actually fires.
            PlayerInput.AddInputMapping(TouchMapping)
            ZoomEvents := PlayerInput.GetInputEvents(PointerZoom)
            BeginSub := ZoomEvents.BeginDetectEvent.Subscribe(OnZoomBegin)
            OngoingSub := ZoomEvents.DetectionOngoingEvent.Subscribe(OnZoomOngoing)
            TriggerSub := ZoomEvents.TriggerActivationEvent.Subscribe(OnZoomTrigger)
            EndSub := ZoomEvents.EndDetectEvent.Subscribe(OnZoomEnd)
            if (set SubsByPlayer[Player] = array{BeginSub, OngoingSub, TriggerSub, EndSub}) {}
            Print("pinch_scale_device: input enabled")

    # Payload: (player, vector3) - Forward carries the pinch magnitude.
    OnZoomBegin(Arg : tuple(player, vector3)):void =
        if (PrintPinchToLog?):
            Print("pinch_scale_device: begin | mag={Arg(1).Forward}")

    # Payload: (player, vector3, elapsed seconds). Which live phase fires depends on platform; handle both.
    OnZoomOngoing(Arg : tuple(player, vector3, float)):void =
        ApplyPinch(Arg(1).Forward, "ongoing")

    # Payload: (player, vector3)
    OnZoomTrigger(Arg : tuple(player, vector3)):void =
        ApplyPinch(Arg(1).Forward, "trigger")

    # Payload: (player, elapsed seconds)
    OnZoomEnd(Arg : tuple(player, float)):void =
        if (PrintPinchToLog?):
            Print("pinch_scale_device: end | scale={CurrentScale}")

    ApplyPinch(Forward : float, Source : string):void =
        if (Forward > MinPinchAmount or Forward < -MinPinchAmount):
            # Exp keeps scaling smooth and symmetric; negated so pinch direction matches expectation.
            Proposed := CurrentScale * Exp(-Forward * ScaleSensitivity)
            set CurrentScale = Max(MinScale, Min(MaxScale, Proposed))
            ApplyScale()
            if (PrintPinchToLog?, PrintEveryPinchUpdate?):
                Print("pinch_scale_device: {Source} | mag={Forward} scale={CurrentScale}")

    # Push CurrentScale onto the prop, leaving position and rotation untouched.
    ApplyScale():void =
        T := PropToScale.GetGlobalTransform()
        NewScale := vector3:
            Forward := BaseScale.Forward * CurrentScale
            Left := BaseScale.Left * CurrentScale
            Up := BaseScale.Up * CurrentScale
        PropToScale.SetGlobalTransform(transform{Translation := T.Translation, Rotation := T.Rotation, Scale := NewScale})
