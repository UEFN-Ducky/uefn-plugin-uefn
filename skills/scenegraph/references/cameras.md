---
description: "Scene Graph cameras (43.00) — perspective/orthographic/physical camera components, FieldOfView in radians, camera_director_component.AddCamera, Pre/Post/Presentation modifier layers, user-written camera_modifier (runs on the server), fort_orbit / fort_fixed_angle / fort_fixed_point modifiers, transitions and blends, play-server known issue; all Experimental (blocks publishing)"
metadata:
  order: 11
  label: "Cameras & camera modifiers"
  default_enabled: false
  load_condition: "Scene Graph cameras, camera components, orbit camera, camera modifier, camera shake, camera director, camera transitions/blends, FieldOfViewDegrees / GlobalModifierPosition / VisualModifierPosition errors, camera not activating on a play server, following a custom entity with a camera, or a custom camera rig instead of the Fortnite gameplay camera"
---

## Scene Graph cameras & camera modifiers

> **Snippets here are fragments.** The `using` block in this file's first code
> block applies to all of them.

> **Everything on this page is `@experimental` and blocks publishing.** Every
> symbol below emits `Script warning 2304` and a project that uses one cannot be
> published. Say that to the user *before* building a camera rig.

```verse
using { /Verse.org/SceneGraph }        # camera components, modifier stack, positions
using { /Verse.org/Simulation }        # required for @editable in a component file
using { /Verse.org/SpatialMath }       # vector3 / rotation (LUF)
using { /Fortnite.com/SceneGraphCameras }   # fort_* camera modifiers
```

Everything here was read from the **43.00** digests and **compile-checked in UEFN
43.00** (0 errors, warnings 2304 only).

### 43.00 breaking changes (read first)

| Old (≤ 42.40) | 43.00 |
|---|---|
| `perspective_camera_component.FieldOfViewDegrees` | **`FieldOfView`**, in **radians** (horizontal, for 16:9; Hor+ scaling on wider screens) |
| any camera angle in degrees | **radians everywhere** — FOV, `RotationOffset`, blends. `Deg * PiFloat / 180.0`, or `MakeRotationFromYawPitchRollRadians` |
| `GlobalModifierPosition` / `VisualModifierPosition` | **removed** (3506). Pick a layer stack on the director instead (below); `Position` is now just your own `rational` order inside that stack |
| `has_camera_modifier` interface | removed; `CameraModifiers` is a field on `camera_component` itself |
| `camera_state` `<epic_internal>` | public: **user-written modifiers work** (below) |
| `camera_body` / `camera_lens` `<final>` | not final; `CloneCameraBody` / `CloneCameraLens` / `CloneCameraState` constructors |

> [!WARNING] Known issue (43.00, fixed in 43.10)
> Scene Graph cameras **do not activate on play servers** — `Player.GetComponent[camera_director_component]`
> fails there (UEFN edit sessions are fine). Workaround, **private versions only**: add
> `using { /Fortnite.com/SceneGraphCameras }` to any Verse file in the project. Keep that
> `using` in every camera file anyway — it is harmless after 43.10.

> [!WARNING] Known issue: interaction
> Interactive objects can be harder to interact with while a Scene Graph camera is active.
> Workaround: place a **Third Person Controls** device alongside your camera.

### The camera components

`camera_component` is `class<final_super><abstract>(component)` (43.00; the `has_camera_modifier` interface is gone)
— abstract, so you never place it directly; you query with it and you place one of
these concrete subclasses (all `@available {MinUploadedAtFNVersion := 4110}`):

| Component | Use | Key field |
|---|---|---|
| `perspective_camera_component` | normal gameplay camera | `var FieldOfView : float` (**radians**) |
| `orthographic_camera_component` | 2D / isometric / map views | `OrthographicProjectionWidth` |
| `physical_camera_component` | cinematic / physically accurate | `var Body : camera_body` + `var Lens : camera_lens` (sensor mm, `FocalLengthMillimeters`, `FStop`, `SqueezeFactor`, `BladeCount`). 43.00 adds **body and lens presets matching the UE Cine Camera** in Details — pick a sensor and lens there; swap `Body`/`Lens` at runtime with `set` |
| `camera_director_component` | picks the active camera and blends | `AddCamera` (below) |

On the base class (so on all of them): `var NearClippingPlaneDistance : float`
and `var FarClippingPlaneDistance : float` — both `@editable`; the docs' rule is
`<= 0.0` / `Inf` means "use defaults".

One component per class per entity, as everywhere in Scene Graph — so a rig that
needs two views needs two child entities.

```verse
set Cam.FieldOfView = 90.0 * PiFloat / 180.0      # 90° -> radians (43.00)
```

The updated **Scene Graph feature example** (43.00) has a camera section with
commented Verse: perspective / orthographic / physical camera entities, a camera shown
while inside a Volume device (and restored on exit), swapping a physical camera's body
and lens during play, a director cycling cameras with a per-switch blend, and a custom
blend style + duration. Point users there for reference rigs.

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

Highest `Priority` wins. The returned `cancelable` is how you give the view back
— hold it per player and `Cancel()` it on leave/teardown.

### Camera modifiers and the 43.00 layers

A modifier mutates the final `camera_state` (render location/rotation, projection,
body/lens, clip planes) without moving any camera entity.

Every `camera_component` has `CameraModifiers : modifier_stack(camera_state)` (the
**Main** layer, runs with that camera). The `camera_director_component` adds three
layer stacks (`@available 4230`):

| Layer (on the director) | Runs | Use for |
|---|---|---|
| `PreCameraModifiers` | before any camera component evaluates | shared defaults for the whole camera system |
| *Main* — active camera's `CameraModifiers` | the highest-priority camera | the rig itself (orbit, fixed angle) |
| `PostCameraModifiers` | after Pre + Main, **on the blended state** (once, not per blending camera) | collision, weapon recoil — the gameplay camera |
| `PresentationCameraModifiers` | last | cosmetic only: camera shake that must not move aim |

Nested directors: every director's Pre layer runs outermost first, then the innermost
active camera + Main, then all Post, then all Presentation.

The stack API (same on every layer):

```verse
# AddModifier has NO <decides> -> PARENTHESES, not brackets. Returns cancelable.
# AddModifier<public>(Modifier:modifier(t), Position:rational)<transacts>:cancelable
Handle := Cam.CameraModifiers.AddModifier(Orbit, 0)          # Position = your own order
Shake := Director.PresentationCameraModifiers.AddModifier(MyShake, 0)
...
Handle.Cancel()                                   # removes it from the stack
```

Calling it `AddModifier[...]` is the mistake to avoid: it yields
`Script error 3511` (square brackets on a non-`decides` function) and then `3513`.
`GlobalModifierPosition` / `VisualModifierPosition` are **gone in 43.00**
(`3506 Unknown identifier`) — choose the layer stack instead and pass any `rational`.
Within a stack, modifiers evaluate in position order; same position = most recently
added evaluates last. `FirstPosition` / `LastPosition` are readable on the stack.

#### User-written modifiers (43.00)

`camera_state` is now public, so subclass `camera_modifier` and override `Evaluate`.
Fields are not `var`: build a new state with field overrides **first**, then the
`CloneCameraState` constructor call (the other order is `Script error 3690`):

```verse
raise_camera_modifier := class(camera_modifier):
    var HeightCentimeters : float = 50.0
    Evaluate<override>(InValue:camera_state)<reads>:camera_state =
        camera_state:
            RenderLocation := InValue.RenderLocation + vector3{Up := HeightCentimeters}
            CloneCameraState<constructor>(InValue)

# Director.PostCameraModifiers.AddModifier(raise_camera_modifier{}, 0)
```

> [!NOTE] Runs on the server
> Verse doesn't run on the client yet, so a camera with a **user-written** modifier is
> evaluated on the server and its state replicated to the client. Expect latency —
> keep per-frame modifiers simple, prefer the built-in `fort_*` modifiers for
> responsive follow cameras.

#### `fort_orbit_camera_modifier` (`/Fortnite.com/SceneGraphCameras`)

`class<concrete>(camera_modifier)`, `@available {MinUploadedAtFNVersion := 4200}`
— i.e. **42.00+**, and Experimental. `TargetEntity` is not a `var`, so it is set
at construction; everything else is a `var` you can retune live.

```verse
Orbit := fort_orbit_camera_modifier:
    TargetEntity := RigRoot                       # entity the camera orbits
set Orbit.CameraDistanceCentimeters = 450.0       # boom length along forward
set Orbit.CameraHeightCentimeters = 120.0         # pivot height above the entity root
set Orbit.EnableCollision = true                  # camera-to-world collision avoidance
set Orbit.CollisionSphereRadiusCentimeters = 20.0
```

Full field list (all cm / all `var` unless noted):

| Field | Meaning |
|---|---|
| `TargetEntity : entity` (not `var`) | entity the camera is attached to |
| `BoomArmOffsetCentimeters : vector3` | boom offset relative to the entity |
| `BoomArmMaxForwardInterpolationFactor` / `...BackwardInterpolationFactor` | boom interpolation clamps |
| `ForwardDampingFactor`, `LateralDampingFactor`, `VerticalDampingFactor` | per-axis follow damping |
| `EnableCollision : logic`, `CollisionSphereRadiusCentimeters` | collision avoidance |
| `CameraDistanceCentimeters` | camera → orbit pivot along forward |
| `CameraHeightCentimeters` | pivot height above the entity root |
| `PositionOffsetCentimeters : vector3` | offset applied after the boom arm |
| `RotationOffset : rotation` | orientation offset — **radians** in 43.00, e.g. `MakeRotationFromYawPitchRollRadians(0.0, -0.3, 0.0)` |

Siblings in the same module, same version gate and shape:

- **`fort_fixed_angle_camera_modifier`** — `TargetEntity`, `CameraDistanceCentimeters`,
  `PositionOffsetCentimeters`, `RotationOffset`, the three damping factors,
  `EnableCollision`, `CollisionSphereRadiusCentimeters`,
  `CollisionSafePositionOffsetCentimeters`. Fixed-angle chase / isometric follow.
- **`fort_fixed_point_camera_modifier`** — `RotationOffset` (+ its own fields);
  a camera pinned to a point that looks around.

`vector3` / `rotation` here are `/Verse.org/SpatialMath` (Forward/Left/Up) — not
the Temporary XYZ family. Mixing them is `movement_transforms`' classic bug.

### Transitions and blends (working from 42.10, unchanged in 43.00)

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

### Recipes from the 43.00 feature example

Four behaviors from Epic's updated Scene Graph feature example, rewritten as
components and **compiled in UEFN 43.00** (0 errors, 2304 warnings only). They share
this header and helper:

```verse
using { /Fortnite.com/Devices }
using { /Fortnite.com/SceneGraphCameras }   # also the 43.00 play-server workaround (fixed 43.10)
using { /Verse.org/SceneGraph }
using { /Verse.org/Simulation }

# The player's camera director lives on the player entity (agent is an entity).
GetDirector(Agent:agent)<transacts><decides>:camera_director_component =
    Agent.GetComponent[camera_director_component]
```

> [!WARNING] Play servers (43.00)
> Every recipe below calls `GetDirector[Agent]`, which **fails on play servers in 43.00**,
> so nothing happens there. Keep the `using { /Fortnite.com/SceneGraphCameras }` line in
> the file (private versions; fixed in 43.10). UEFN edit sessions are unaffected.

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
3. Retune `CameraDistanceCentimeters` / `CameraHeightCentimeters` live and
   re-enter the session rather than guessing numbers.

### Don'ts

- Don't call `AddModifier[...]` with brackets — no `<decides>` (error 3511/3513).
- Don't call `AddCamera(...)` with parens — it **is** `<decides>`. Error 3511 covers
  both directions (compile-verified): "uses parentheses to call a function that has
  the 'decides' effect" and "uses square brackets to call a function that does not".
- Don't use `FieldOfViewDegrees`, degrees anywhere, or `GlobalModifierPosition` /
  `VisualModifierPosition` — all gone in 43.00 (radians, `FieldOfView`, layer stacks).
- Don't put a cosmetic shake in `PostCameraModifiers` — it moves aim; use
  `PresentationCameraModifiers`. Collision/recoil go in Post (runs once on the blend).
- In a custom `Evaluate`, field overrides go **before** `CloneCameraState<constructor>(InValue)` (3690).
- Don't subclass `mesh_component`, and don't invent mesh class names — read them
  from the Assets digest.
- Don't promise publishing: every symbol on this page is Experimental.
- Audio follows the active camera (fixed in 42.40 and again in 43.00): sound is spatialized
  around the Scene Graph camera, not the player character — don't add listener workarounds.
- Don't ship a play-server build relying on cameras without the
  `using { /Fortnite.com/SceneGraphCameras }` workaround until 43.10.
- Don't place two components of the same camera class on one entity.

### Related

- Full player controller recipe → `skill_read_subskill("scenegraph", "custom_player_controller")`
- Component lifecycle → `verse_authoring`
- Why the rig doesn't move → `movement_transforms`
- Component catalog → `components`
