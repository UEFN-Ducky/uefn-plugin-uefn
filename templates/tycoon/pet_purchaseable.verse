# SETUP: Follow pet. One active pet per plot (ActivePetIndex). The pet is a Scene Graph
# entity with a tycoon_reveal_component (TypeIndex 6, ItemIndex = this pet's index in
# Pets) and a keyframed_movement_component. It walks on the ground: keep the root
# unrotated and its feet at plot height; turn a child mesh entity to face if you need to.
# It follows with short keyframe segments re-aimed every FollowSeconds, never MoveTo.
using { /Verse.org/Simulation }
using { /Verse.org/SceneGraph }
using { /Verse.org/SceneGraph/KeyframedMovement }
using { /Verse.org/SpatialMath }
using { /Fortnite.com/Devices }
using { /Fortnite.com/Characters }

pet_purchaseable <public> := class<concrete>(purchaseable):
    @editable FollowSeconds <public> : float = 0.15
    @editable FollowSpeed <public> : float = 600.0
    @editable FollowGap <public> : float = 150.0

    Activate<override>()<suspends> : void =
        if (Plot := OwnerPlot?):
            set Plot.ActivePetIndex = ItemIndex
        ShowReveals()
        Gen := RunId
        loop:
            if (RunId <> Gen):
                break
            if (IsOwned = false):
                break
            FollowOwner()
            Sleep(FollowSeconds)

    # Each segment covers 1.5 steps, so the next one starts before the last ends.
    FollowOwner<public>() : void =
        if:
            Plot := OwnerPlot?
            Plot.ActivePetIndex = ItemIndex
            Agent := Plot.ClaimedBy?
            Char := Agent.GetFortCharacter[]
            OwnerEntity := Char.GetEntity[]
        then:
            Goal := OwnerEntity.GetGlobalTransform().Translation
            SegmentSeconds := FollowSeconds * 1.5
            for (Pet : Plot.RevealEntities(PackedKey()), KFM := Pet.GetComponent[keyframed_movement_component]):
                Here := Pet.GetGlobalTransform().Translation
                Flat := vector3{Forward := Goal.Forward - Here.Forward, Left := Goal.Left - Here.Left, Up := 0.0}
                Away := Flat.Length()
                if (Away > FollowGap):
                    Travel := Min(FollowSpeed * SegmentSeconds, Away - FollowGap)
                    Step := keyframed_movement_delta:
                        Transform := transform:
                            Translation := Flat * (Travel / Away)
                            Rotation := IdentityRotation()
                            Scale := vector3{}
                        Duration := SegmentSeconds
                        Easing := linear_easing_function{}
                    KFM.SetKeyframes(array{Step}, oneshot_keyframed_movement_playback_mode{})
                    KFM.Play()
