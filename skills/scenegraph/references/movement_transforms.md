---
description: "The one motion page: every runtime move of a Scene Graph entity is keyframed_movement_component — editable keyframe path component, bob, spin, one glide (replaces MoveTo), chasing with keyframe segments, the rules that bite (additive scale, chained deltas, 360° keys), full KFM API and easings, local vs global, origins for attaching, LUF axes, why it isn't moving, deep-hierarchy transform bug"
metadata:
  order: 5
  label: "Movement & transforms (keyframes for every move)"
  default_enabled: false
  load_condition: "Anything moves, rotates, bobs, spins, glides, chases or animates at runtime (always keyframes); an entity will not move, rotate, animate or follow something; attaching entities to players/vehicles; orbits and movers; keyframed movement; transforms applying to the wrong axis or not at all"
---

## Movement & transforms

**This is the one motion page, and its rule is hard: every runtime move of a
Scene Graph entity is a keyframe** (`keyframed_movement_component`). Doors,
lifts, platforms, spinners, bobbing pickups, projectiles, a single glide and
chasers are all keyframes. A transform is written **once**, to place something;
origins follow; players ride keyframed platforms. `MoveTo` is never used, and
nothing is animated by writing a transform or `TeleportTo` in a loop.

Why: KFM plays natively in the Pre-Physics phase, outside your Verse, and the
client interpolates it. Epic's keyframed movement page says it avoids the
per-update cost of `TeleportTo()` / `MoveTo()`. One `SetKeyframes` + `Play()`
replaces a loop that would run every frame, so hundreds of movers stay cheap,
and the server also skips entities that aren't moving.

`SetEntityTransform` / `SetLocalTransform` here are **Scene Graph entities**, not
Fortnite Creative devices. Never actor-scale buttons, triggers, or volumes —
those resize via Details Width/Height/zone (`SetDeviceProperty`).

Every signature here is from this build's digests. Re-check with
`get_verse_api({"name": "<identifier>"})` before writing anything unfamiliar.

```verse
using { /Verse.org/SceneGraph }
using { /Verse.org/SceneGraph/KeyframedMovement }
using { /Verse.org/Simulation }
using { /Verse.org/SpatialMath }
using { /Fortnite.com/Characters }   # fort_character / GetFortCharacter[] in the origin recipe below
```

### Pick the right mechanism

| Goal | Use | Not |
|------|-----|-----|
| Place once (spawn, reset, put a thing on a spot) | `SetGlobalTransform` / `SetLocalTransform`, **once** | a loop |
| Door, lift, platform, any authored path | KFM keys in an `@editable` array (`keyframed_path_component` below) | per-frame transform writes |
| Spin, bob, sway forever | KFM `loop` (four 90° keys) / `pingpong` (`StartSpin`, `StartBob`) | a ~10 Hz Verse loop |
| One glide to a point | `GlideTo` / `GlideBy`: one `oneshot` delta, wait its duration | `MoveTo`, a lerp loop |
| Thrown or flying object | one `oneshot` delta over the flight time (npc-ai `projectiles`) | a per-frame position |
| Chasing, homing, steering | `ChaseSegments`: a short KFM segment re-aimed ~10 times a second; steering maths may tick as pure state | per-frame `SetGlobalTransform` |
| A custom player controller reading Move input | `custom_player_controller` — the **only** per-frame transform writer | — |
| Follow / attach to a player, vehicle or other entity | **origin** (`SetOrigin`) | copying the target transform every frame |
| Reparent permanently | `Parent.AddEntities(array{Child})` | `SetOrigin` |
| Carry a player (lift, train, ride) | they stand on a keyframed platform entity; collidable child meshes with `Visible` off keep them on (verse `runtime_pitfalls`) | `TeleportTo` each tick, a moving `chair_device` (`MoveTo`) |
| Hide and show again | `Disable()` / `Enable()` its `mesh_component`s **and** set `Collidable` / `Queryable` (`Disable()` only stops rendering) — `SetShown` in `verse_authoring` | `RemoveFromParent` then re-adding; teleporting it away |

### `transform_component`

`class<final><final_super>(component)` — one per entity, and **required for a
mesh to be positioned at all** (`mesh_component`'s digest lists it as a
dependency).

| Member | Meaning |
|--------|---------|
| `var GlobalTransform:transform` | World-space pose. A value set at construction is **overwritten** by the local calculation. |
| `var LocalTransform:transform` | Pose relative to the parent, or to `Origin` when one is set. |
| `var Origin:?origin` | Alternative origin instead of the parent entity. |

Entity extensions (`/Verse.org/SceneGraph`):

```verse
(InEntity:entity).GetGlobalTransform()<transacts>:transform
(InEntity:entity).GetLocalTransform()<transacts>:transform
(InEntity:entity).SetGlobalTransform(NewGlobalTransform:transform)<transacts>:void
(InEntity:entity).SetLocalTransform(NewLocalTransform:transform)<transacts>:void
(InEntity:entity).SetOrigin(NewOrigin:origin)<transacts>:void
(InEntity:entity).ResetOrigin()<transacts>:void
```

`SetLocalTransform` **creates a `transform_component` on demand**, which is the
one-liner fix for an empty pivot that reports `local_transform_error`:

```verse
Ent.SetLocalTransform(Ent.GetLocalTransform())   # ensure a transform exists
```

### Attaching with an origin

An origin re-bases an entity's local transform onto another entity without
reparenting it — this is how you make something follow a player, a vehicle, or
a moving platform.

```verse
if:
    Character := Agent.GetFortCharacter[]
    CharacterEntity := Character.GetEntity[]
then:
    Held.SetOrigin(entity_origin{Entity := CharacterEntity})
    Held.SetLocalTransform(transform{Translation := vector3{Up := 90.0}})

# later
Held.ResetOrigin()
```

`origin` is an interface with `GetTransform()`; `entity_origin` is the
entity-backed implementation (`Entity` field).

**Do not change the origin and move in the same frame** — that combination
stopped working (Epic bug report still open). Set the origin, let a
frame pass (`Sleep(0.0)` in a `<suspends>` context, or act on the next tick),
then set the transform. The same "too fast" class of bug leaves the mesh behind
while collision moves, so avoid rapid attach/detach/move bursts.

**Move, then query, same frame.** An entity moved with `SetGlobalTransform` /
`SetLocalTransform` is visible to `FindOverlapHits` / `FindSweepHits` **in the same
frame** — query right after the move. Remove any `Sleep(0.0)` you put between a move and
an overlap/sweep query in older builds; it now only costs a frame of latency.

```verse
Entity.SetGlobalTransform(NewTransform)
for (Hit : Entity.FindOverlapHits()):    # sees the new position
    HandleHit(Hit)
```

### Scene Graph handles

A **handle** refers to an entity or component *without granting access to it*; you
resolve it with a failable getter (fails if unset or not accessible). All
`@available`, `/Verse.org/SceneGraph`, not experimental:

| Type | Resolve | Notes |
|---|---|---|
| `entity_handle` | `H.GetEntity[]` | base of the others |
| `component_handle(t)` | `H.GetComponent[]` → `t` | also an `entity_handle` (`GetEntity[]` = owner) |
| `mesh_part_handle` | `GetComponent[]` → `mesh_component` | `component_handle(mesh_component)`; the mesh (and part) at one end of a hit |

`overlap_hit` and `sweep_hit` (and `collision_hit`) gained `SourceMeshHandle` /
`TargetMeshHandle : mesh_part_handle` — which mesh on each side was touched, even inside
a compound hierarchy. `mesh_component` also gained `var CanAffectNavigation : logic`
(server-only, not replicated; the mesh still needs collision that blocks pawns, and NPCs
won't route around meshes with it off).

```verse
# Which meshes did this sweep hit, and whose are they? (compiled 0 errors)
HitMeshes(Mover:entity, Delta:vector3):[]mesh_component =
    for:
        Hit : Mover.FindSweepHits(Delta)
        Mesh := Hit.TargetMeshHandle.GetComponent[]
    do:
        Mesh

HitEntities(Mover:entity):[]entity =
    for:
        Hit : Mover.FindOverlapHits()
        Owner := Hit.TargetMeshHandle.GetEntity[]
    do:
        Owner
```

Handles are `<epic_internal>` classes: you get them from hit results, you never
construct one.

### `keyframed_movement_component`

`class<final><final_super>(component)` — **`<final>`, so it cannot be
subclassed.** A `constant_rotation_component` of your own *holds* a KFM; it
never extends one. Playback happens in the **Pre-Physics** tick phase.

| Member | Notes |
|--------|-------|
| `SetKeyframes(RelativeKeyframes:[]keyframed_movement_delta, PlaybackMode:keyframed_movement_playback_mode)` | Stops any current animation, **rebases the path onto the entity's current transform**, and does **not** start playing. |
| `Play()` / `Pause()` | Pause keeps the position; Play resumes from there. |
| `Stop()` / `Stop(BlendOutTime:float)` | Resets to the initial transform; the next `Play()` starts over. |
| `IsPlaying[]` / `IsPaused[]` / `HasValidAnimation[]` | Failable state checks. |
| `var Duration:?float` | Fails when there is no fixed duration (looping). |
| `PlayedEvent` / `PausedEvent` / `StoppedEvent` / `FinishedEvent` | `listenable(tuple())`. `FinishedEvent` never fires for infinite animations. |
| `KeyframeReachedEvent` | `listenable(tuple(int, logic))` — keyframe index and whether playback is reversed. |

```verse
KFM := keyframed_movement_component{Entity := Ent}
Ent.AddComponents(array{KFM})

KF := keyframed_movement_delta:
    Transform := transform:
        Translation := vector3{Forward := 500.0}   # ADDITIVE delta, not a destination
        Rotation := IdentityRotation()
        Scale := vector3{}                         # 0 = no change (additive)
    Duration := 2.0
    Easing := linear_easing_function{}

Ent.SetGlobalTransform(StartPose)       # position BEFORE SetKeyframes (it rebases)
KFM.SetKeyframes(array{KF}, oneshot_keyframed_movement_playback_mode{})
KFM.Play()                              # nothing moves without this
```

Playback modes: `oneshot_` (play once, stay at the end), `loop_` (repeat from the
start), `pingpong_keyframed_movement_playback_mode` (forward, then back, forever).
Translation and Scale on a delta are **additive**; Rotation is relative.

Easing (`/Verse.org/SceneGraph/KeyframedMovement`, digest — all five are
`<concrete>`, so `{}` works, and none is Experimental, so all publish):

| Class | Motion |
|---|---|
| `linear_easing_function` | constant speed |
| `ease_cubic_bezier_easing_function` | slow start, faster middle, slow end (end a bit slower) |
| `ease_in_cubic_bezier_easing_function` | slow start, speeds up |
| `ease_out_cubic_bezier_easing_function` | fast start, slows down |
| `ease_in_out_cubic_bezier_easing_function` | like `ease_`, symmetric start and end |

The base `cubic_bezier_easing_function` is `<epic_internal>`: you can't build a
custom curve from Verse — pick one of the five.
Never drive Scene Graph entities with `creative_prop` / `animation_controller`
keyframes — different system, different API.

#### Rules that bite

- **Each delta starts where the previous one ended.** Up 500, then Forward 500,
  then Up -500 is an arch that lands 500 forward of the start.
- **Scale is added.** Write `Scale := vector3{}` in **every** delta: `0` keeps the
  size, `1` adds 1 (a scale-1 mesh doubles). Never a negative scale. This is the
  opposite of `SetGlobalTransform`, where Scale is absolute and `vector3{}` makes
  the mesh invisible — write `Scale := vector3{Left := 1.0, Up := 1.0, Forward := 1.0}`
  (or keep the current scale) when you place something.
- **A 360° key is no rotation** (a quaternion can't tell 0° from 360°). A full
  turn is four 90° keys; any single key over 180° turns the short way.
- **Position first.** `SetKeyframes` rebases onto the current transform and
  stops anything playing; move the entity, then `SetKeyframes`, then `Play()`.
- **Keep the mover's root unrotated** when you aim deltas at world points
  (`GlideTo`, `ChaseSegments`): the digest doesn't say whether a rotated
  entity's delta follows its facing. Turn a **child** mesh entity to show the
  heading, as with FBX axis fixes below.
- **Many copies, different timing:** give each instance its own `StartDelay`
  or keys instead of one loop that offsets them.

#### Recipes (type-checked on the digests)

**Designer-authored path** — the keys are an `@editable` array, so they are
typed into the Details panel of the prefab (Transform, Duration, Easing per key)
and every prefab copy can differ. Put a `keyframed_movement_component` and this
component on the same entity:

```verse
mover_playback := enum:
    Loop
    PingPong
    OneShot

ToPlaybackMode(Playback : mover_playback) : keyframed_movement_playback_mode =
    case (Playback):
        mover_playback.Loop => loop_keyframed_movement_playback_mode{}
        mover_playback.PingPong => pingpong_keyframed_movement_playback_mode{}
        mover_playback.OneShot => oneshot_keyframed_movement_playback_mode{}

# Plays the keyframes typed into the Details panel. Needs a keyframed_movement_component
# on the same entity (add it in the prefab next to this component).
keyframed_path_component := class<final_super>(component):
    @editable
    Keyframes : []keyframed_movement_delta = array{}

    @editable
    Playback : mover_playback = mover_playback.Loop

    # Different delays on copies of the same prefab so they don't move in lockstep.
    @editable
    StartDelay : float = 0.0

    OnSimulate<override>()<suspends> : void =
        if (KFM := Entity.GetComponent[keyframed_movement_component]):
            KFM.SetKeyframes(Keyframes, ToPlaybackMode(Playback))
            if (StartDelay > 0.0):
                Sleep(StartDelay)
            KFM.Play()

    OnEndSimulation<override>() : void =
        if (KFM := Entity.GetComponent[keyframed_movement_component]):
            KFM.Stop()
        (super:)OnEndSimulation()
```

**Bob and spin** — no Verse runs after `Play()`:

```verse
# Up and down forever: one key, pingpong.
StartBob(KFM : keyframed_movement_component, Height : float, Seconds : float) : void =
    Bob := keyframed_movement_delta:
        Transform := transform:
            Translation := vector3{Up := Height}
            Rotation := IdentityRotation()
            Scale := vector3{}
        Duration := Seconds
        Easing := ease_in_out_cubic_bezier_easing_function{}
    KFM.SetKeyframes(array{Bob}, pingpong_keyframed_movement_playback_mode{})
    KFM.Play()

# Full turns forever: four 90-degree keys, loop (one 360-degree key is no rotation at all).
StartSpin(KFM : keyframed_movement_component, SecondsPerTurn : float) : void =
    Quarter := keyframed_movement_delta:
        Transform := transform:
            Translation := vector3{}
            Rotation := MakeRotationFromYawPitchRollDegrees(90.0, 0.0, 0.0)
            Scale := vector3{}
        Duration := SecondsPerTurn / 4.0
        Easing := linear_easing_function{}
    KFM.SetKeyframes(array{Quarter, Quarter, Quarter, Quarter}, loop_keyframed_movement_playback_mode{})
    KFM.Play()
```

**One glide** — this replaces `MoveTo` for entities:

```verse
# Glides by Offset over Seconds and returns when it arrives.
GlideBy(KFM : keyframed_movement_component, Offset : vector3, Seconds : float)<suspends> : void =
    Glide := keyframed_movement_delta:
        Transform := transform:
            Translation := Offset
            Rotation := IdentityRotation()
            Scale := vector3{}
        Duration := Seconds
        Easing := ease_in_out_cubic_bezier_easing_function{}
    KFM.SetKeyframes(array{Glide}, oneshot_keyframed_movement_playback_mode{})
    KFM.Play()
    Sleep(Seconds)               # a oneshot lasts Seconds (FinishedEvent.Await() works too, but the LSP flags it)

# Glides to a point in the parent's space (world space under the simulation entity).
GlideTo(Mover : entity, KFM : keyframed_movement_component, Destination : vector3, Seconds : float)<suspends> : void =
    GlideBy(KFM, Destination - Mover.GetLocalTransform().Translation, Seconds)
```

**Chasing** — Verse re-aims ~10 times a second, KFM draws every frame in between.
Run it from the mover's own component `OnSimulate` (cancelled when the mover
leaves the scene) or race it against the round's stop event (verse `async`).
One manager loop can re-aim every chaser in the same pass:

```verse
# Re-aims a short keyframe at the target ten times a second. Each segment covers
# 1.5 steps, so the next one starts before the last ends (no stop-start stutter).
ChaseSegments(Mover : entity, KFM : keyframed_movement_component, Target : entity, Speed : float)<suspends> : void =
    StepSeconds : float = 0.1
    SegmentSeconds : float = StepSeconds * 1.5
    loop:
        Offset := Target.GetGlobalTransform().Translation - Mover.GetGlobalTransform().Translation
        Gap := Offset.Length()
        if (Gap > 1.0):
            Travel := Min(Speed * SegmentSeconds, Gap)
            Segment := keyframed_movement_delta:
                Transform := transform:
                    Translation := Offset * (Travel / Gap)
                    Rotation := IdentityRotation()
                    Scale := vector3{}
                Duration := SegmentSeconds
                Easing := linear_easing_function{}
            KFM.SetKeyframes(array{Segment}, oneshot_keyframed_movement_playback_mode{})
            KFM.Play()
        Sleep(StepSeconds)
```

Never name a local `Distance` in a file that imports `/Verse.org/SpatialMath` —
it clashes with `SpatialMath.Distance` (3532); that's why the snippet says `Gap`.

### Axes and coordinate systems

`vector3` is `Forward` (old X), `Left` (old -Y), `Up` (old Z); `transform` is
`{Translation, Rotation, Scale}`; rotations are quaternions built with
`MakeRotationFromYawPitchRollDegrees` / `MakeRotationDegrees`, combined with `*`.

`/Verse.org/SpatialMath` is the LUF system used by Scene Graph and the editor.
There is a second, legacy XYZ-convention copy of these types in
`/UnrealEngine.com/Temporary/SpatialMath` — `rotation`, `transform` and even
`IdentityRotation()` exist in both. In a file that imports both families,
**qualify the type** the way the digests do —
`(/Verse.org/SpatialMath:)transform` — or transforms come out silently rotated
or offset. Imported FBX assets should be configured so
their Up/Forward match LUF; otherwise put the axis correction on a **child**
mesh entity via `SetLocalTransform` and keep the root's yaw as the real heading.

### When nothing moves — checklist

Components are documented to simulate in the **editor as well as in play**, so a
dead viewport is usually a real bug, not "you forgot to hit Play". Work down
this list, then confirm in PIE / Launch Session before declaring it broken:

1. Is there a `transform_component`? EntityToolset `FindEntities` reporting
   `local_transform_error` means no. Call `SetLocalTransform` or add one.
2. Is the component actually attached? Custom Verse components only appear
   after a successful Verse build — check the EntityToolset component listing (`unreal__describe_toolset` for the exact tool name).
3. Is the work in the right hook? Setup in `OnBeginSimulation`, async and
   per-frame in `OnSimulate` (runs **once** — wrap it in `loop` with
   `Sleep(0.0)`); `TickEvents.Subscribe` is Epic-internal.
4. KFM: did you call `Play()` after `SetKeyframes`? Are the deltas non-zero
   (they are additive, `0` means no change)? Is the `keyframed_movement_component`
   on the **same** entity your component reads it from? Keys set in the Details
   panel but no `SetKeyframes` + `Play()` in Verse = nothing moves.
5. It moves but grows: a delta without `Scale := vector3{}`. It vanished after a
   `SetGlobalTransform`: Scale `vector3{}` there is size zero.
6. Are you moving the right entity? Orbit radius belongs on the **body**'s local
   translation; the **pivot** is what rotates.
7. Did a `<decides>` call fail silently inside an `if`? `GetFortCharacter[]`,
   `GetEntity[]`, `GetSimulationEntity[]` and `GetComponent[]` all fail rather
   than error.

### Known transform bugs worth designing around

- **`GetGlobalTransform` on deep children.** Three or more levels down it can
  return `0,0,0` (it appears to return the local transform). Epic tracks this as
  FORT-1026495, status Backlogged. Prefer `GetLocalTransform` /
  `SetLocalTransform` for children, and parent a spawned entity **directly to
  its intended parent** rather than adding it to `SimulationEntity` first.
- **`-0.0` transform values.** Prefabs or placed objects carrying `-0` instead
  of `0` broke island launch. Write `0.0`.
- **Same-frame origin change plus move** — see the attach section above.
