---
description: "Scene Graph cameras — perspective / orthographic / physical camera components, FieldOfView in radians, camera_director_component.AddCamera, Pre / Post / Presentation modifier layers, camera modifiers as small pieces you stack in order (attach to entity, boom arm, offset, collision push, dampen translation / rotation, set translation / rotation, panning and dolly framing), recipes for orbit, fixed angle and fixed point cameras, user-written modifiers (run on the server), transitions and blends"
metadata:
  order: 11
  label: "Cameras & camera modifiers"
  default_enabled: false
  load_condition: "Scene Graph cameras, camera components, orbit camera, fixed angle or fixed point camera, top-down or isometric camera, boom arm, camera modifier, camera shake, camera director, camera transitions/blends, camera framing a target, AddModifier errors, fort_orbit_camera_modifier / FieldOfViewDegrees / GlobalModifierPosition unknown identifier, following a custom entity with a camera, or a custom camera rig instead of the Fortnite gameplay camera"
---

## Scene Graph cameras & camera modifiers

> **Check the digest before you build.** `get_verse_api("camera_component")`,
> `search_verse_digest("camera_modifier")`. A name with an `@experimental` line above it
> emits `Script warning 2304`, and an island that uses it cannot be published; tell the
> user that *before* building a camera rig. If the line is gone, it can be published.
> A name on this page that is not in the digest does not exist in the installed build:
> `verse_digest_changes("camera")` shows what replaced it.

```verse
using { /Verse.org/SceneGraph }        # camera components, modifier stack
using { /Verse.org/Simulation }        # required for @editable in a component file
using { /Verse.org/SpatialMath }       # vector3 / rotation (LUF)
using { /Fortnite.com/SceneGraphCameras }   # fort_* camera modifiers
```

### Rules that hold everywhere

- **Radians everywhere**: `FieldOfView`, rotation offsets, cone angles, blends. `Deg * PiFloat / 180.0`, or `MakeRotationFromYawPitchRollRadians`.
- **Modifiers run in the order you add them.** `AddModifier(Modifier)` takes the modifier only. To change the order, add them in the order you want.
- `CameraModifiers` is a field on `camera_component` itself; the director has three more layer stacks (below).
- Names that no longer exist (error 3506): `FieldOfViewDegrees`, `GlobalModifierPosition`, `VisualModifierPosition`, `FirstPosition`, `LastPosition`, a second `Position` argument on `AddModifier`, `fort_orbit_camera_modifier`, `fort_fixed_angle_camera_modifier`, `fort_fixed_point_camera_modifier`. Build those three cameras from the pieces below.

> [!WARNING] Interaction
> Interactive objects can be harder to interact with while a Scene Graph camera is active.
> Place a **Third Person Controls** device alongside your camera.

### The camera components

`camera_component` is abstract: you never place it, you query with it and place one of
these concrete subclasses:

| Component | Use | Key field |
|---|---|---|
| `perspective_camera_component` | normal gameplay camera | `var FieldOfView : float` (**radians**) |
| `orthographic_camera_component` | 2D / isometric / map views | `OrthographicProjectionWidth` |
| `physical_camera_component` | cinematic / physically accurate | `var Body : camera_body` + `var Lens : camera_lens` (sensor mm, `FocalLengthMillimeters`, `FStop`, `SqueezeFactor`, `BladeCount`); pick a sensor and lens preset in Details, swap `Body`/`Lens` at runtime with `set` |
| `camera_director_component` | picks the active camera and blends | `AddCamera` (below) |

On the base class (so on all of them): `var NearClippingPlaneDistance : float`
and `var FarClippingPlaneDistance : float`, both `@editable`; `<= 0.0` / `Inf` means
"use defaults".

One component per class per entity, as everywhere in Scene Graph, so a rig that
needs two views needs two child entities.

```verse
set Cam.FieldOfView = 90.0 * PiFloat / 180.0      # 90 degrees in radians
```

Epic's **Scene Graph feature example** has a camera section with commented Verse:
perspective / orthographic / physical camera entities, a camera shown while inside a
Volume device (and restored on exit), swapping a physical camera's body and lens during
play, a director cycling cameras with a per-switch blend, and a custom blend style +
duration. Point users there for reference rigs.

### Making a camera the player's view — `camera_director_component`

```verse
# AddCamera IS <decides> -> square brackets.
# AddCamera<native><public>(Camera:camera_component, Priority:rational)<transacts><decides>:cancelable
if:
    Director := (for (D : Player.FindDescendantComponents(camera_director_component)) do D)[0]
    Cam := (for (C : RigRoot.FindDescendantComponents(perspective_camera_component)) do C)[0]
    Handle := Director.AddCamera[Cam, 100]
then:
    Print("custom camera active")
```

Highest `Priority` wins. The returned `cancelable` is how you give the view back:
hold it per player and `Cancel()` it on leave/teardown. If the director is not found on a
play server, keep `using { /Fortnite.com/SceneGraphCameras }` in the file.

### Camera modifiers and layers

A modifier changes the final `camera_state` (render location/rotation, projection,
body/lens, clip planes) without moving any camera entity.

Every `camera_component` has `CameraModifiers : modifier_stack(camera_state)` (the
**Main** layer, runs with that camera). The `camera_director_component` adds three
layer stacks:

| Layer (on the director) | Runs | Use for |
|---|---|---|
| `PreCameraModifiers` | before any camera component evaluates | shared defaults for the whole camera system |
| *Main*: the active camera's `CameraModifiers` | the highest-priority camera | the rig itself (attach, boom arm, offset) |
| `PostCameraModifiers` | after Pre + Main, **on the blended state** (once, not per blending camera) | collision, weapon recoil: the gameplay camera |
| `PresentationCameraModifiers` | last | cosmetic only: camera shake that must not move aim |

Nested directors: every director's Pre layer runs outermost first, then the innermost
active camera + Main, then all Post, then all Presentation.

The stack API (same on every layer):

```verse
# AddModifier has NO <decides> -> PARENTHESES, not brackets. Returns cancelable.
# AddModifier<public>(Modifier:modifier(t))<transacts>:cancelable
Handle := Cam.CameraModifiers.AddModifier(Follow)             # runs first
Shake := Director.PresentationCameraModifiers.AddModifier(MyShake)
...
Handle.Cancel()                                   # removes it from the stack
```

Calling it `AddModifier[...]` is the mistake to avoid: `Script error 3511` (square
brackets on a non-`decides` function) and then `3513`.

### The pieces (`/Fortnite.com/SceneGraphCameras`)

Each piece does one job. Set them up in the Details panel (so they ship in a prefab) or
create them at runtime. Fields marked `var` can be retuned live with `set`.

| Modifier | Job | Fields |
|---|---|---|
| `fort_attach_to_entity_camera_modifier` | follow a target entity | `var TargetEntity`, `var ShouldFollowTranslation`, `var ShouldFollowOrientation` |
| `fort_boom_arm_camera_modifier` | swing around the pivot with the player's look input | `var BoomOffset : vector3` (rotation happens at the base, before the offset), `IsRotationAdditive`, `AutoRotateSettings` (`fort_auto_rotate_camera_modifier_settings`: `IsEnabled`, `Direction`, `WaitTime`, `DisableThreshold`, yaw / pitch), `BoomLengthInterpolationSettings`, max forward / backward interpolation factors |
| `fort_offset_camera_modifier` | shift or turn the camera | `var TranslationOffset`, `var RotationOffset`, `OffsetSpace` (`fort_camera_offset_space.CameraSpace` / `PivotSpace` / `GlobalSpace`) |
| `fort_collision_push_camera_modifier` | keep the camera out of walls | `var IgnoreEntities`, `var IgnoreEntitiesAndDescendants`, `var SafeLocationOffset`, `var CollisionSphereRadius`, push / pull interpolation settings |
| `fort_dampen_translation_camera_modifier` | smooth movement, per axis | `var ForwardDampingFactor`, `var LeftDampingFactor`, `var UpDampingFactor`, `DampenSpace` (0.0 = no damping on that axis) |
| `fort_dampen_rotation_camera_modifier` | smooth turning, per axis | `var YawDampingFactor`, `var PitchDampingFactor`, `var RollDampingFactor` |
| `fort_set_translation_camera_modifier` | put the camera at a global position (replaces, does not offset) | `var Translation` |
| `fort_set_rotation_camera_modifier` | point the camera in a global direction (replaces) | `var Rotation` |
| `fort_panning_framing_camera_modifier` | keep targets in frame by turning in place | `var TargetEntities : [entity]float` (entity to weight), `CanYaw`, `CanPitch`, framing position, dead zone and damping fields |
| `fort_dolly_framing_camera_modifier` | keep targets in frame by sliding sideways (and up / down) | the same framing fields, `CanMoveHorizontally`, `CanMoveVertically` |

Interpolation settings are subclasses of `fort_camera_value_interpolation_settings`
(critical damper, IIR, double IIR, acceleration / deceleration, pop). Read the exact fields
with `get_verse_api("<name>")`.

### Recipes: orbit, fixed angle, fixed point (compiled)

```verse
# Orbit: follow the target, swing around it with the player's look input, stay out of walls.
MakeOrbitCamera(Cam : camera_component, Target : entity, BoomLength : float, Height : float) : []cancelable =
    Follow := fort_attach_to_entity_camera_modifier{}
    set Follow.TargetEntity = Target
    set Follow.ShouldFollowTranslation = true
    set Follow.ShouldFollowOrientation = false
    Boom := fort_boom_arm_camera_modifier{}
    set Boom.BoomOffset = vector3{Forward := -BoomLength, Up := Height}
    Push := fort_collision_push_camera_modifier{}
    set Push.IgnoreEntitiesAndDescendants = array{Target}
    Stack := Cam.CameraModifiers
    array{Stack.AddModifier(Follow), Stack.AddModifier(Boom), Stack.AddModifier(Push)}

# Fixed angle: follow the target, keep one viewing angle, sit back from it, smooth the move.
MakeFixedAngleCamera(Cam : camera_component, Target : entity, Look : rotation, Back : float) : []cancelable =
    Follow := fort_attach_to_entity_camera_modifier{}
    set Follow.TargetEntity = Target
    set Follow.ShouldFollowOrientation = false
    Aim := fort_set_rotation_camera_modifier{}
    set Aim.Rotation = Look
    Away := fort_offset_camera_modifier{OffsetSpace := fort_camera_offset_space.CameraSpace}
    set Away.TranslationOffset = vector3{Forward := -Back}
    Smooth := fort_dampen_translation_camera_modifier{}
    set Smooth.ForwardDampingFactor = 5.0
    set Smooth.LeftDampingFactor = 5.0
    set Smooth.UpDampingFactor = 5.0
    Stack := Cam.CameraModifiers
    array{Stack.AddModifier(Follow), Stack.AddModifier(Aim), Stack.AddModifier(Away), Stack.AddModifier(Smooth)}

# Fixed point: the camera stays where it is placed and turns to keep the target in frame.
MakeFixedPointCamera(Cam : camera_component, Target : entity) : cancelable =
    Frame := fort_panning_framing_camera_modifier{}
    if (set Frame.TargetEntities[Target] = 1.0) {}
    Cam.CameraModifiers.AddModifier(Frame)
```

Keep every returned `cancelable`: cancelling one removes that piece, which is how you
swap one camera mode for another. Don't name a local `Distance`: it clashes with the
SpatialMath function (3588 / 3532). These compile against the digest; tune the numbers in
a live session.

`vector3` / `rotation` here are `/Verse.org/SpatialMath` (Forward/Left/Up), not
the Temporary XYZ family. Mixing them is `movement_transforms`' classic bug.

### User-written modifiers

Implement `modifier(camera_state)` and override `Evaluate`. Fields of `camera_state` are
not `var`: build a new state with field overrides **first**, then the `CloneCameraState`
constructor call (the other order is `Script error 3690`):

```verse
raise_camera_modifier := class(modifier(camera_state)):
    var HeightCentimeters : float = 50.0
    Evaluate<override>(InValue:camera_state)<reads>:camera_state =
        camera_state:
            RenderLocation := InValue.RenderLocation + vector3{Up := HeightCentimeters}
            CloneCameraState<constructor>(InValue)

# Director.PostCameraModifiers.AddModifier(raise_camera_modifier{})
```

Subclassing `camera_modifier` is the other form; the offline check flags its `Evaluate`
override as inaccessible (3593), so compile it in UEFN before relying on it.

> [!NOTE] One user-written modifier moves the whole camera to the server
> Verse does not run on the client yet. As soon as a stack holds one modifier that is not
> Epic's, the whole camera system runs on the server and replicates the result, so the
> delay hits every modifier in the stack. If a camera must feel immediate, use only the
> `fort_*` pieces.

### Transitions and blends

Subclassing a **concrete** camera component in creator Verse is legal — verified
by compile — so transitions are authored by overriding on your own subclass:

```verse
my_cam := class<final_super>(perspective_camera_component):
    GetEnterTransition<override>(SourceCamera : camera_component)<transacts><decides> : camera_transition =
        camera_transition{Blend := camera_mode_blend_smoothstep{}, Duration := 0.5}

    GetExitTransition<override>(DestinationCamera : camera_component)<transacts><decides> : camera_transition =
        camera_transition{Blend := camera_mode_blend_pop{}, Duration := 0.0}
```

Both hooks are `<transacts><decides>`. Blends (all `<concrete>`, all Experimental):
`camera_mode_blend_pop{}` (instant cut), `_linear`, `_smoothstep`, `_smootherstep`,
`_orbit{DrivingBlend := …}`. `camera_transition_initial_orientation` picks what the
new camera inherits: `PreviousYawPitch`, `PreviousAbsoluteTarget`,
`PreviousRelativeTarget`.

### Recipes from Epic's feature example

Four behaviors from Epic's updated Scene Graph feature example, rewritten as
components and **compiled in UEFN** (0 errors, 2304 warnings only). They share
this header and helper:

```verse
using { /Fortnite.com/Devices }
using { /Fortnite.com/SceneGraphCameras }   # keep it: without it the director may not be found on a play server
using { /Verse.org/SceneGraph }
using { /Verse.org/Simulation }

# The player's camera director lives on the player entity (agent is an entity).
GetDirector(Agent:agent)<transacts><decides>:camera_director_component =
    Agent.GetComponent[camera_director_component]
```

#### 1. Show a camera while a player is inside a Volume device

**Use when:** a room, cutscene spot or security-cam zone should take over the view on
entry and give it back on exit. Put the component on the camera entity (it needs a
`perspective_camera_component`) and wire `Volume`.

```verse
volume_camera_component := class<final_super>(component):
    @editable
    Volume : volume_device = volume_device{}
    @editable
    Priority : rational = 100

    var Claims : [agent]cancelable = map{}
    var Subs : []cancelable = array{}

    OnBeginSimulation<override>():void =
        (super:)OnBeginSimulation()
        set Subs = array:
            Volume.AgentEntersEvent.Subscribe(OnEnter)
            Volume.AgentExitsEvent.Subscribe(OnExit)

    OnEnter(Agent:agent):void =
        if:
            not Claims[Agent]
            Cam := Entity.GetComponent[perspective_camera_component]
            Director := GetDirector[Agent]
            Handle := Director.AddCamera[Cam, Priority]
            set Claims[Agent] = Handle

    OnExit(Agent:agent):void =
        if (Handle := Claims[Agent]):
            Handle.Cancel()                     # the previous camera takes over again
            var Kept : [agent]cancelable = map{}
            for (A -> H : Claims, A <> Agent):
                if (set Kept[A] = H) {}
            set Claims = Kept

    OnEndSimulation<override>():void =
        for (S : Subs) do S.Cancel()
        for (H : Claims) do H.Cancel()
        set Claims = map{}
        (super:)OnEndSimulation()
```

**Trap:** "restore" is just `Cancel()` on the `AddCamera` handle. The director falls back
to the next-highest priority. Never re-`AddCamera` the old camera, which stacks a
duplicate claim. `set Map[K] = V` is failable, so wrap it in `if` ("This map access can fail" otherwise).

#### 2. Swap a physical camera's body and lens during play

**Use when:** a cinematic or photo-mode camera switches between wide and portrait looks.
The component sits on an entity with a `physical_camera_component`. Pick the starting
sensor and lens from the Cine Camera presets in Details. There are no preset names in
Verse, so runtime swaps set the millimetre values.

```verse
lens_swap_component := class<final_super>(component):
    @editable
    SwapButton : button_device = button_device{}

    var Wide : logic = false

    OnBeginSimulation<override>():void =
        (super:)OnBeginSimulation()
        SwapButton.InteractedWithEvent.Subscribe(OnSwap)

    OnSwap(Agent:agent):void =
        if (Cam := Entity.GetComponent[physical_camera_component]):
            set Wide = if (Wide?) then false else true
            FocalLength := if (Wide?) then 18.0 else 85.0
            SensorWidth := if (Wide?) then 36.0 else 24.89   # full frame vs Super 35
            set Cam.Lens = camera_lens:
                FocalLengthMillimeters := FocalLength
                FStop := if (Wide?) then 8.0 else 1.8
                CloneCameraLens<constructor>(Cam.Lens)
            set Cam.Body = camera_body:
                SensorWidthMillimeters := SensorWidth
                CloneCameraBody<constructor>(Cam.Body)
```

**Trap:** `camera_lens` / `camera_body` fields are not `var`. Build a new object, with the
field overrides **before** the `Clone…<constructor>` call (3690 otherwise), and `set` the
whole `Lens` / `Body`. The clone keeps every value you didn't override.

#### 4. Choose the blend style and duration (used by recipe 3)

**Use when:** the default switch is wrong, for example a hard cut where you want a slow
ease. Place this subclass instead of a plain `perspective_camera_component`. Its
`EnterTransition` is editable in Details and settable from Verse.

```verse
tuned_blend_camera := class<final_super>(perspective_camera_component):
    @editable
    var EnterTransition : camera_transition = camera_transition{Blend := camera_mode_blend_smoothstep{}, Duration := 0.75}

    GetEnterTransition<override>(SourceCamera:camera_component)<transacts><decides>:camera_transition =
        EnterTransition
```

Blends: `camera_mode_blend_pop{}` (cut, use `Duration := 0.0`), `_linear{}`,
`_smoothstep{}`, `_smootherstep{}`, `_orbit{DrivingBlend := …}`. Duration is in seconds.
**Trap:** the **entering** camera's `GetEnterTransition` decides the blend. To control
how you leave a camera, override `GetExitTransition` on that camera instead.

#### 3. A director that cycles a list of cameras, with a per-switch blend

**Use when:** a spectator, replay or showcase steps through several angles. Each entry
of `Cameras` is an entity holding a `tuned_blend_camera` (recipe 4). Wire a trigger
for "next".

```verse
camera_cycler_component := class<final_super>(component):
    @editable
    NextTrigger : trigger_device = trigger_device{}
    @editable
    Cameras : []entity = array{}                  # each holds a tuned_blend_camera
    @editable
    SwitchDurations : []float = array{0.0, 0.5, 1.5}

    var Index : int = 0
    var Active : ?cancelable = false

    OnBeginSimulation<override>():void =
        (super:)OnBeginSimulation()
        NextTrigger.TriggeredEvent.Subscribe(OnNext)

    OnNext(MaybeAgent:?agent):void =
        if:
            Agent := MaybeAgent?
            Director := GetDirector[Agent]
            CamEntity := Cameras[Index]
            Cam := CamEntity.GetComponent[tuned_blend_camera]
        then:
            Duration := if (D := SwitchDurations[Index]) then D else 0.5
            Blend:camera_mode_blend = if (Duration <= 0.0) then camera_mode_blend_pop{} else camera_mode_blend_smootherstep{}
            set Cam.EnterTransition = camera_transition{Blend := Blend, Duration := Duration}
            if (Old := Active?) then Old.Cancel()
            if (Handle := Director.AddCamera[Cam, 100]):
                set Active = option{Handle}
            set Index = Mod[Index + 1, Cameras.Length] or 0
```

**Trap:** set the incoming camera's transition **before** `AddCamera`, because the blend is
read when the switch happens. Cancel the previous handle so only one cycled camera holds
priority. This sample tracks one viewer; for several players, keep a
`[agent]cancelable` map as in recipe 1.

### Custom meshes on a camera rig (or any entity)

`mesh_component` is `class<final_super><epic_internal>(component, enableable)` —
**you cannot subclass it in creator Verse.** Importing a mesh generates the
subclass for you in the project's Assets digest, e.g.
`SM_Hat01_Cap := class<final>(mesh_component)` under a `<scoped {…}>` module.
So "custom mesh" means: import the asset, then reference the generated class.

```
list_verse_types(digest="assets", name_filter="SM_")   # find the generated classes
get_verse_api("<ClassName>")                            # confirm module + members
```

Add it to an entity as an asset component through Epic `EntityToolset.AddComponent`
(`editor_tools` covers class resolution); in Verse you query it with
`Entity.GetComponent[mesh_component]` and toggle it via `enableable`.

### Verify

1. `workspace_compile_verse` — expect **0 errors** and only 2304 warnings. The
   offline LSP alone will not prove a camera rig builds.
2. Launch a session; the rig camera should take over on join (`Print` in the
   `AddCamera` success branch).
3. Retune `BoomOffset` and the damping factors live and re-enter the session rather
   than guessing numbers.

### Don'ts

- Don't call `AddModifier[...]` with brackets — no `<decides>` (error 3511/3513).
- Don't call `AddCamera(...)` with parens — it **is** `<decides>`. Error 3511 covers
  both directions (compile-verified): "uses parentheses to call a function that has
  the 'decides' effect" and "uses square brackets to call a function that does not".
- Don't use degrees anywhere, or any name listed as gone under "Rules that hold everywhere".
- Don't put a cosmetic shake in `PostCameraModifiers` — it moves aim; use
  `PresentationCameraModifiers`. Collision/recoil go in Post (runs once on the blend).
- In a custom `Evaluate`, field overrides go **before** `CloneCameraState<constructor>(InValue)` (3690).
- Don't subclass `mesh_component`, and don't invent mesh class names — read them
  from the Assets digest.
- Don't promise publishing while the digest marks these names `@experimental`.
- Audio follows the active camera: sound is spatialized
  around the Scene Graph camera, not the player character — don't add listener workarounds.
- Keep `using { /Fortnite.com/SceneGraphCameras }` in every camera file.
- Don't place two components of the same camera class on one entity.

### Related

- Full player controller recipe → `skill_read_subskill("scenegraph", "custom_player_controller")`
- Component lifecycle → `verse_authoring`
- Why the rig doesn't move → `movement_transforms`
- Component catalog → `components`
