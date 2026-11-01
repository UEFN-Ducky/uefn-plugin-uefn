# SETUP: Assign this class on prey NPCDefs via set_npc_definition_behavior.
# Duplicate react/die clips into this folder, then swap the Sleep fallbacks for Play(AS_…).
# 43.00: movement and focus go through npc_actions_component (GetNavigatable / GetFocusInterface are deprecated).
using { /Fortnite.com/AI }
using { /Fortnite.com/Animation/PlayAnimation }
using { /Fortnite.com/Characters }
using { /UnrealEngine.com/Temporary/SpatialMath }
using { /Verse.org/Random }
using { /Verse.org/SceneGraph }
using { /Verse.org/Simulation }

prey_ai_state := enum:
    Exploring
    Following
    Fleeing
    PlayingDead

prey_npc_behavior<public> := class(npc_behavior):
    @editable ExploreMinRadius : float = 500.0
    @editable ExploreMaxRadius : float = 600.0
    @editable ExploreReachRadius : float = 80.0
    @editable PlayerDetectRange : float = 400.0
    @editable HunterDetectRange : float = 900.0
    @editable FollowMinSeconds : float = 4.0
    @editable FollowMaxSeconds : float = 6.0
    @editable FollowReachRadius : float = 120.0
    @editable FleeDistance : float = 800.0
    @editable FleeReachRadius : float = 100.0
    @editable FleeSpeedMultiplier : float = 1.75
    @editable AfterCatchIgnoreSeconds : float = 5.0
    @editable PlayDeadSeconds : float = 3.5
    @editable SenseInterval : float = 0.2

    var CurrentState : prey_ai_state = prey_ai_state.Exploring
    var StateLocked : logic = false
    var FollowTarget : ?fort_character = false
    var FollowUntilTime : float = 0.0
    var IgnoreHuntersUntil : float = -999.0
    var PlayDeadClaimed : logic = false
    var SelfAgent : ?agent = false

    OnBegin<override>()<suspends> : void =
        if:
            Agent := GetAgent[]
            Char := Agent.GetFortCharacter[]
            Actions := GetEntity[].GetComponent[npc_actions_component]
            Anim := Char.GetPlayAnimationController[]
        then:
            set SelfAgent = option{Agent}
            RegisterPreyAgent(Agent)
            race:
                SenseLoop(Agent, Char)
                BehaviorLoop(Char, Actions, Anim)
                WaitUntilInactive(Char)
            UnregisterPreyAgent(Agent)
            Actions.StopNavigation()

    OnEnd<override>() : void =
        if (Agent := SelfAgent?):
            UnregisterPreyAgent(Agent)

    WaitUntilInactive(Char : fort_character)<suspends> : void =
        loop:
            Sleep(0.25)
            if (not Char.IsActive[]):
                break

    SenseLoop(Agent : agent, Char : fort_character)<suspends> : void =
        loop:
            Sleep(SenseInterval)
            if (not Char.IsActive[]):
                break
            Now := GetSimulationElapsedTime()
            Downed := IsPreyDownedAt(Agent, Now)
            if (Downed = false):
                set PlayDeadClaimed = false
            if (CurrentState = prey_ai_state.PlayingDead):
            else if (Downed = true, PlayDeadClaimed = false):
                set PlayDeadClaimed = true
                set StateLocked = false
                set CurrentState = prey_ai_state.PlayingDead
            else if (StateLocked = false):
                UpdateDesiredState(Agent, Char)

    UpdateDesiredState(Agent : agent, Char : fort_character) : void =
        Now := GetSimulationElapsedTime()
        if (IsPreyDownedAt(Agent, Now) = true, PlayDeadClaimed = false):
            set PlayDeadClaimed = true
            set CurrentState = prey_ai_state.PlayingDead
            return
        if (CurrentState = prey_ai_state.PlayingDead):
            return

        if (Now < IgnoreHuntersUntil):
            if (CurrentState = prey_ai_state.Fleeing):
                set CurrentState = prey_ai_state.Exploring
        else if (CurrentState <> prey_ai_state.Fleeing):
            if (Hunter := FindNearestHunter(Char, HunterDetectRange)?):
                set FollowTarget = option{Hunter}
                set CurrentState = prey_ai_state.Fleeing
                return

        if (CurrentState = prey_ai_state.Following):
            if (Target := FollowTarget?):
                if (Target.IsActive[]):
                    Dist := Distance(Char.GetTransform().Translation, Target.GetTransform().Translation)
                    if (Dist > PlayerDetectRange * 1.5, Now >= FollowUntilTime):
                        set FollowTarget = false
                        set CurrentState = prey_ai_state.Exploring
                    return
                else:
                    set FollowTarget = false
                    set CurrentState = prey_ai_state.Exploring
                    return

        if (Player := FindNearestPlayer(Self, Char, PlayerDetectRange)?):
            set FollowTarget = option{Player}
            set FollowUntilTime = Now + GetRandomFloat(FollowMinSeconds, FollowMaxSeconds)
            set CurrentState = prey_ai_state.Following
            return

        if (CurrentState <> prey_ai_state.Fleeing):
            set CurrentState = prey_ai_state.Exploring

    BehaviorLoop(Char : fort_character, Actions : npc_actions_component, Anim : play_animation_controller)<suspends> : void =
        loop:
            if (not Char.IsActive[]):
                break
            case (CurrentState):
                prey_ai_state.Exploring => ExploreOnce(Char, Actions)
                prey_ai_state.Following => FollowOnce(Char, Actions)
                prey_ai_state.Fleeing => FleeOnce(Char, Actions)
                prey_ai_state.PlayingDead => PlayDeadOnce(Char, Actions, Anim)

    ExploreOnce(Char : fort_character, Actions : npc_actions_component)<suspends> : void =
        Dest := NPCRandomPointAround(Char.GetTransform().Translation, ExploreMinRadius, ExploreMaxRadius)
        set Actions.MovementSpeedMultiplier = 1.0
        race:
            Actions.NavigateTo(MakeNavigationTarget(Dest), ?MovementType := movement_type.Walking, ?ReachRadius := ExploreReachRadius)
            WaitWhileState(prey_ai_state.Exploring)

    FollowOnce(Char : fort_character, Actions : npc_actions_component)<suspends> : void =
        if (Target := FollowTarget?, Target.IsActive[]):
            TargetPos := Target.GetTransform().Translation
            if (TargetAgent := Target.GetAgent[], TargetEntity := Target.GetEntity[]):
                race:
                    Actions.NavigateTo(MakeNavigationTarget(TargetAgent), ?MovementType := movement_type.Running, ?ReachRadius := FollowReachRadius)
                    Actions.Focus(TargetEntity, ?LockFocus := true)
                    WaitWhileState(prey_ai_state.Following)
            else:
                race:
                    Actions.NavigateTo(MakeNavigationTarget(TargetPos), ?MovementType := movement_type.Running, ?ReachRadius := FollowReachRadius)
                    Actions.Focus(FromVector3(TargetPos), ?LockFocus := true)
                    WaitWhileState(prey_ai_state.Following)
        else:
            set FollowTarget = false
            set CurrentState = prey_ai_state.Exploring
            Sleep(0.1)

    FleeOnce(Char : fort_character, Actions : npc_actions_component)<suspends> : void =
        set StateLocked = true
        Actions.StopNavigation()
        SelfPos := Char.GetTransform().Translation
        var ThreatPos : vector3 = SelfPos
        if (Target := FollowTarget?):
            set ThreatPos = Target.GetTransform().Translation
        else if (Hunter := FindNearestHunter(Char, HunterDetectRange * 2.0)?):
            set ThreatPos = Hunter.GetTransform().Translation
        FleeDest := NPCFleePointFrom(SelfPos, ThreatPos, FleeDistance)
        set Actions.MovementSpeedMultiplier = FleeSpeedMultiplier
        race:
            Actions.NavigateTo(MakeNavigationTarget(FleeDest), ?MovementType := movement_type.Running, ?ReachRadius := FleeReachRadius)
            Actions.Focus(FromVector3(ThreatPos), ?LockFocus := true)
            WaitWhileState(prey_ai_state.Fleeing)
            Sleep(3.5)
        set Actions.MovementSpeedMultiplier = 1.0
        set FollowTarget = false
        if (CurrentState = prey_ai_state.Fleeing):
            set CurrentState = prey_ai_state.Exploring
        set StateLocked = false

    PlayDeadOnce(Char : fort_character, Actions : npc_actions_component, Anim : play_animation_controller)<suspends> : void =
        set StateLocked = true
        Actions.StopNavigation()
        set Actions.MovementSpeedMultiplier = 1.0
        set FollowTarget = false
        # ponytail: Sleep until you duplicate a die clip into this folder and Play it here.
        Sleep(PlayDeadSeconds)
        set IgnoreHuntersUntil = GetSimulationElapsedTime() + AfterCatchIgnoreSeconds
        set CurrentState = prey_ai_state.Exploring
        set StateLocked = false

    WaitWhileState(Wanted : prey_ai_state)<suspends> : void =
        loop:
            Sleep(0.15)
            if (CurrentState <> Wanted):
                break
