# SETUP: Place this creative_device in the level. Every player enters Virtual Pointer mode on join
# (TouchMapping) and is immobilized. PointerSelect + TouchMapping are publishable.
# Detects swipe / flick gestures (touch drag, mouse drag, left-stick drag) and taps.
#   BeginDetect       -> pointer down, cache start position
#   TriggerActivation -> pointer held / moving, update current position
#   EndDetect         -> pointer up, classify direction and fire HandleSwipe / HandleTap
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

# Data produced when a swipe gesture completes.
swipe_result := struct:
    StartPosition : vector3
    EndPosition : vector3
    # 2D direction (Left/Up components only, Forward = 0)
    Direction : vector3
    # Squared distance of the swipe in screen-cm squared
    SwipeDistSq : float
    # Duration of the swipe in seconds
    Duration : float
    Cardinal : swipe_direction

swipe_detector_device := class(creative_device):

    # Minimum squared distance (screen-cm squared) to count as a swipe instead of a tap.
    # 0.25 = 0.5 cm threshold. Raise for less sensitivity, lower for more.
    @editable
    MinSwipeDistanceSq : float = 0.25

    # Per-player gesture state (one device serves every player).
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
            Print("swipe_detector_device: input subscribed")

    # Phase 1: pointer down -> cache start position. Payload: (player, screen vector3)
    OnPointerDown(Arg : tuple(player, vector3)):void =
        Player := Arg(0)
        Position := Arg(1)
        if (set StartByPlayer[Player] = Position) {}
        if (set CurrentByPlayer[Player] = Position) {}
        if (set TrackingByPlayer[Player] = true) {}

    # Phase 2: fires repeatedly while held -> update current position. Payload: (player, screen vector3)
    OnPointerMove(Arg : tuple(player, vector3)):void =
        Player := Arg(0)
        if (TrackingByPlayer[Player]?):
            if (set CurrentByPlayer[Player] = Arg(1)) {}

    # Phase 3: pointer up -> classify. Payload: (player, elapsed seconds since BeginDetect)
    OnPointerUp(Arg : tuple(player, float)):void =
        Player := Arg(0)
        ElapsedTime := Arg(1)
        if (TrackingByPlayer[Player]?, Start := StartByPlayer[Player], Current := CurrentByPlayer[Player]):
            if (set TrackingByPlayer[Player] = false) {}

            DeltaLeft := Current.Left - Start.Left
            DeltaUp := Current.Up - Start.Up
            DistSq := (DeltaLeft * DeltaLeft) + (DeltaUp * DeltaUp)

            if (DistSq >= MinSwipeDistanceSq):
                Result := swipe_result{
                    StartPosition := Start
                    EndPosition := Current
                    Direction := vector3{Forward := 0.0, Left := DeltaLeft, Up := DeltaUp}
                    SwipeDistSq := DistSq
                    Duration := ElapsedTime
                    Cardinal := ClassifySwipe(DeltaLeft, DeltaUp)
                }
                HandleSwipe(Player, Result)
            else:
                HandleTap(Player, Start)

    # Replace the Print calls with gameplay, or override in a subclass.
    HandleSwipe(Player : player, Result : swipe_result):void =
        DirName := SwipeDirectionToString(Result.Cardinal)
        Print("SWIPE {DirName} | DistSq:{Result.SwipeDistSq} | Duration:{Result.Duration}s")

    HandleTap(Player : player, Position : vector3):void =
        Print("TAP at ({Position.Left}, {Position.Up})")

    # Left is positive rightward; Up is positive upward (screen-cm from the top-left corner).
    ClassifySwipe(DeltaLeft : float, DeltaUp : float):swipe_direction =
        AbsLeft := AbsF(DeltaLeft)
        AbsUp := AbsF(DeltaUp)
        if (AbsLeft >= AbsUp):
            if (DeltaLeft > 0.0):
                swipe_direction.Right
            else:
                swipe_direction.Left
        else:
            if (DeltaUp > 0.0):
                swipe_direction.Up
            else:
                swipe_direction.Down

    AbsF(X : float):float =
        if (X < 0.0) then -X else X

    SwipeDirectionToString(Dir : swipe_direction):string =
        case (Dir):
            swipe_direction.None => "None"
            swipe_direction.Up => "Up"
            swipe_direction.Down => "Down"
            swipe_direction.Left => "Left"
            swipe_direction.Right => "Right"
