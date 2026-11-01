# 43.00: movement and focus go through npc_actions_component (GetNavigatable / GetFocusInterface are deprecated).
using { /Fortnite.com/AI }
using { /Verse.org/SceneGraph }
using { /Fortnite.com/Animation/PlayAnimation }
using { /Fortnite.com/Characters }
using { /UnrealEngine.com/Temporary/SpatialMath }
using { /Verse.org/Random }
using { /Verse.org/Simulation }

# Hunt cats, attack on catch, leave that cat alone, hunt another.
# AS_DogReact_Attack is the bite/play clip duplicated into this folder.

dog_ai_state := enum:
    Hunting
    Attacking
    GivingUp

dog_npc_behavior<public> := class(npc_behavior):

    @editable HuntRange : float = 2500.0
    @editable CatchRadius : float = 160.0
    @editable ChaseSecondsMin : float = 6.0
    @editable ChaseSecondsMax : float = 10.0
    @editable GiveUpSeconds : float = 2.5
    @editable CatDownedSeconds : float = 10.0
    @editable AttackHoldSeconds : float = 1.2
    @editable SprintSpeedMultiplier : float = 1.65
    @editable SenseInterval : float = 0.2

    var CurrentState : dog_ai_state = dog_ai_state.Hunting
    var Prey : ?fort_character = false
    var ChaseUntilTime : float = 0.0
    var SelfAgent : ?agent = false

    OnBegin<override>()<suspends> : void =
        if:
            Agent := GetAgent[]
            Char := Agent.GetFortCharacter[]
            Actions := GetEntity[].GetComponent[npc_actions_component]
            Anim := Char.GetPlayAnimationController[]
        then:
            set SelfAgent = option{Agent}
            RegisterDogAgent(Agent)
            race:
                SenseLoop(Agent, Char)
                BehaviorLoop(Char, Actions, Anim)
                WaitUntilInactive(Char)
            UnregisterDogAgent(Agent)
            Actions.StopNavigation()

    OnEnd<override>() : void =
        if (Agent := SelfAgent?):
            UnregisterDogAgent(Agent)

    WaitUntilInactive(Char : fort_character)<suspends> : void =
        loop:
            Sleep(0.25)
            if (not Char.IsActive[]):
                break

    PlayAttack(Anim : play_animation_controller)<suspends> : void =
        Inst := Anim.Play(AS_DogReact_Attack, ?PlayCount := 1.0, ?BlendInTime := 0.08, ?BlendOutTime := 0.12)
        race:
            Inst.Await()
            Sleep(AttackHoldSeconds)
        Inst.Stop()

    SenseLoop(Agent : agent, Char : fort_character)<suspends> : void =
        loop:
            Sleep(SenseInterval)
            if (not Char.IsActive[]):
                break
            UpdateDesiredState(Agent, Char)

    UpdateDesiredState(Agent : agent, Char : fort_character) : void =
        Now := GetSimulationElapsedTime()
        DownedAgents := GetDownedAgents()
        DownedUntils := GetDownedUntilTimes()

        if (CurrentState = dog_ai_state.GivingUp):
            return

        if (CurrentState = dog_ai_state.Attacking):
            return

        if (Target := Prey?):
            if (Target.IsActive[]):
                if (PreyAgent := Target.GetAgent[]):
                    PreyDowned := IsCatDownedInLists(PreyAgent, Now, DownedAgents, DownedUntils)
                    if (PreyDowned = true):
                        set CurrentState = dog_ai_state.GivingUp
                        return
                Dist := Distance(Char.GetTransform().Translation, Target.GetTransform().Translation)
                if (Dist <= CatchRadius):
                    set CurrentState = dog_ai_state.Attacking
                    return
                if (Now >= ChaseUntilTime):
                    set CurrentState = dog_ai_state.GivingUp
                    return
                return
            else:
                set Prey = false

        MaybeCat := DogFindNearestCat(Agent, Char, HuntRange, Now)
        if (Cat := MaybeCat?):
            set Prey = option{Cat}
            set ChaseUntilTime = Now + GetRandomFloat(ChaseSecondsMin, ChaseSecondsMax)
            set CurrentState = dog_ai_state.Hunting
        else:
            set Prey = false

    BehaviorLoop(Char : fort_character, Actions : npc_actions_component, Anim : play_animation_controller)<suspends> : void =
        loop:
            if (not Char.IsActive[]):
                break
            case (CurrentState):
                dog_ai_state.Hunting => HuntOnce(Char, Actions)
                dog_ai_state.Attacking => AttackOnce(Char, Actions, Anim)
                dog_ai_state.GivingUp => GiveUpOnce(Char, Actions)

    HuntOnce(Char : fort_character, Actions : npc_actions_component)<suspends> : void =
        if (Target := Prey?):
            if (Target.IsActive[]):
                set Actions.MovementSpeedMultiplier = SprintSpeedMultiplier
                TargetPos := Target.GetTransform().Translation
                if (TargetAgent := Target.GetAgent[], TargetEntity := Target.GetEntity[]):
                    race:
                        Actions.NavigateTo(MakeNavigationTarget(TargetAgent), ?MovementType := movement_type.Running, ?ReachRadius := CatchRadius)
                        Actions.Focus(TargetEntity, ?LockFocus := true)
                        WaitWhileDogState(dog_ai_state.Hunting)
                else:
                    race:
                        Actions.NavigateTo(MakeNavigationTarget(TargetPos), ?MovementType := movement_type.Running, ?ReachRadius := CatchRadius)
                        Actions.Focus(FromVector3(TargetPos), ?LockFocus := true)
                        WaitWhileDogState(dog_ai_state.Hunting)
                set Actions.MovementSpeedMultiplier = 1.0
            else:
                set Prey = false
                Sleep(0.2)
        else:
            set Actions.MovementSpeedMultiplier = 1.0
            Dest := CatRandomPointAround(Char.GetTransform().Translation, 400.0, 700.0)
            race:
                Actions.NavigateTo(MakeNavigationTarget(Dest), ?MovementType := movement_type.Walking, ?ReachRadius := 100.0)
                Sleep(2.5)
                WaitWhileDogState(dog_ai_state.Hunting)

    AttackOnce(Char : fort_character, Actions : npc_actions_component, Anim : play_animation_controller)<suspends> : void =
        Actions.StopNavigation()
        set Actions.MovementSpeedMultiplier = 1.0
        Now := GetSimulationElapsedTime()
        if (Target := Prey?):
            if (TargetAgent := Target.GetAgent[]):
                MarkCatDowned(TargetAgent, Now + CatDownedSeconds)
                if (TargetEntity := Target.GetEntity[]):
                    race:
                        Actions.Focus(TargetEntity, ?LockFocus := true)
                        PlayAttack(Anim)
                else:
                    PlayAttack(Anim)
            else:
                PlayAttack(Anim)
        else:
            PlayAttack(Anim)
        set CurrentState = dog_ai_state.GivingUp

    GiveUpOnce(Char : fort_character, Actions : npc_actions_component)<suspends> : void =
        Actions.StopNavigation()
        set Actions.MovementSpeedMultiplier = 1.0
        OldPrey := Prey
        set Prey = false
        Sleep(GiveUpSeconds)
        Now := GetSimulationElapsedTime()
        if (Agent := SelfAgent?):
            if (Old := OldPrey?):
                MaybeOther := DogFindNearestCatExcluding(Agent, Char, HuntRange, Old, Now)
                if (Cat := MaybeOther?):
                    set Prey = option{Cat}
            else:
                MaybeAny := DogFindNearestCat(Agent, Char, HuntRange, Now)
                if (Cat3 := MaybeAny?):
                    set Prey = option{Cat3}
            if (P := Prey?):
                set ChaseUntilTime = Now + GetRandomFloat(ChaseSecondsMin, ChaseSecondsMax)
            else:
                Dest := CatRandomPointAround(Char.GetTransform().Translation, 500.0, 900.0)
                race:
                    Actions.NavigateTo(MakeNavigationTarget(Dest), ?MovementType := movement_type.Walking, ?ReachRadius := 100.0)
                    Sleep(2.0)
        set CurrentState = dog_ai_state.Hunting

    WaitWhileDogState(Wanted : dog_ai_state)<suspends> : void =
        loop:
            Sleep(0.15)
            if (CurrentState <> Wanted):
                break
