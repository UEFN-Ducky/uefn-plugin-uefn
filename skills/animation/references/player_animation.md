---
description: "Play custom AnimSequences on the PLAYER character via fort_character.GetPlayAnimationController — full body or UpperBody layer, additive overlay (Layered Control Rig + AdditiveAnimType Local Space), a per-player emote toggle device, Fortnite Body/Face/MetaHuman face rigs and additive Sequencer layering, the Player Reference + Cinematic Sequence route, stasis, teleport, blend times, and hard limits"
metadata:
  label: "Player animation"
  default_enabled: false
  load_condition: "Playing a custom animation on the player character, additive/overlay player anims, GetPlayAnimationController, Layered Control Rig, AdditiveAnimType Local Space, player stasis during a clip, giant/tiny player, weapon inspect, melee on the player, custom emotes or an emote button, arms-only animation while running, Player Reference device animation, Fortnite body/face rigs"
---

# Player animation — anim controller + additive overlay

Players are not Animated Mesh devices. As of the Play Animation Controller
shipping for players, you play clips through Verse on `fort_character`. That is
the default. The Player Reference + Cinematic Sequence route (below) is for full
sequences on the player's look; the chair device trick is legacy.

Confirm signatures with `search_verse_digest` / `get_verse_api` before shipping —
names evolve. Module: `/Fortnite.com/Animation/PlayAnimation`.

## Full override vs additive overlay

Same Verse call either way. The **only** difference is the AnimSequence asset:

| Clip setting | What the player sees |
|--------------|----------------------|
| Additive Anim Type = **No Additive** (default) | Clip **replaces** Fortnite body animation |
| Additive Anim Type = **Local Space** | Clip **layers on top of** Fortnite locomotion (arms, scale, deltas) |

Flip it with MCP:

```
set_anim_additive_type({"anim_paths": ["/YourProject/Anims/AS_ArmUp"],
    "additive_type": "local_space"})
get_anim_sequence_info({"anim_path": "/YourProject/Anims/AS_ArmUp"})   # verify additive_anim_type
```

Editor fallback (Property Matrix exposes a field the Details panel hides):
Content Drawer → select AnimSequence(s) → right-click → **Asset Actions →
Edit Selection in Property Matrix** → **Additive Anim Type → Local Space** → Save.

Without that flip, an "arm wave" clip still overrides the whole body.

## The Verse device (override or additive)

```verse
using { /Fortnite.com/Devices }
using { /Verse.org/Simulation }
using { /UnrealEngine.com/Temporary/Diagnostics }
using { /Fortnite.com/Characters }
using { /Fortnite.com/Animation/PlayAnimation }
using { /UnrealEngine.com/Temporary/SpatialMath }
using { /Fortnite.com/Playspaces }
using { /Verse.org/Assets }

# Clip identifier comes from Assets.digest after a successful Verse compile.
# Path Content/Animations/SillyDance1 → Animations.SillyDance1 (project mount).
player_anim_device := class(creative_device):

    @editable
    Trigger : trigger_device = trigger_device{}

    # Point this at your retargeted / baked AnimSequence in Details. An @editable asset
    # field is an option: `= external {}` is only legal inside digests (error 3558).
    @editable
    Clip : ?animation_sequence = false

    OnBegin<override>()<suspends>:void =
        Trigger.TriggeredEvent.Subscribe(OnTriggered)

    OnTriggered(MaybeAgent : ?agent):void =
        if (Agent := MaybeAgent?):
            spawn{ PlayOnAgent(Agent) }

    PlayOnAgent(Agent : agent)<suspends>:void =
        if:
            Sequence := Clip?
            FortCharacter := Agent.GetFortCharacter[]
            AnimController := FortCharacter.GetPlayAnimationController[]
        then:
            # Hold the INSTANCE — do not re-fetch the controller to Stop.
            Instance := AnimController.Play(
                Sequence,
                ?BlendInTime := 0.25,
                ?BlendOutTime := 0.25,
                ?PlayRate := 1.0
                # ?PlayCount := 1.0
                # ?StartPositionSeconds := 0.0
            )
            Result := Instance.Await()   # Completed | Interrupted | Error
            # Or: Instance.Stop() after Sleep(...), or PlayAndAwait(Clip, ...)
```

`Play` returns `play_animation_instance` immediately. Prefer `Instance.Await()` /
`PlayAndAwait` over "Sleep then re-get controller and Stop" — the instance is
the handle for `Stop`, `IsPlaying[]`, `CompletedEvent`, `InterruptedEvent`,
`BlendedInEvent`, `BlendingOutEvent`.

Optional named args on `Play` / `PlayAndAwait`:

| Arg | Meaning |
|-----|---------|
| `?BlendInTime` / `?BlendOutTime` | Seconds — snappy clips still want a short blend |
| `?PlayRate` | Speed; scale it with the player's speed (`GetLinearVelocity`) so a run cycle matches the run |
| `?PlayCount` | How many times to play |
| `?StartPositionSeconds` | Start mid-clip |
| `?Layer` | `play_animation_layer.FullBody` (default, whole skeleton) or `.UpperBody` (upper body only while the character moves, so the legs keep running) |

`IsPlaying[]` and `GetState()` on the instance tell you whether it is still running — use
them for a toggle instead of a separate `logic` map.

Place the device, wire the trigger in Details, launch a session, walk onto the
trigger. Compile Verse first or the Assets digest identifier / `@editable`
`animation_sequence` slot will look broken.

## Stasis (freeze the player for the clip)

For dances / cutscenes where the player must not walk away:

```verse
PlayOnAgent(Agent : agent)<suspends>:void =
    if:
        FortCharacter := Agent.GetFortCharacter[]
        AnimController := FortCharacter.GetPlayAnimationController[]
    then:
        FortCharacter.PutInStasis(
            stasis_args{
                AllowEmotes := false
                AllowTurning := false
                AllowFalling := false
            }
        )
        Instance := AnimController.Play(Clip, ?BlendInTime := 0.25, ?BlendOutTime := 0.25)
        Instance.Await()
        # Always release on every exit path (Await returns on Interrupted/Error too).
        FortCharacter.ReleaseFromStasis()
```

Verse has no `defer`. If you `race` the play against a cancel event, call
`ReleaseFromStasis()` in **every** branch that leaves the freeze, or the player
stays locked.

## Emote button (toggle, every player)

One input trigger starts the clip for whoever presses it and stops it on the next press.
`UpperBodyOnly` plays it on the `UpperBody` layer so the player keeps walking (no stasis).
Type-checked against the digests.

```verse
using { /Fortnite.com/Devices }
using { /Fortnite.com/Characters }
using { /Fortnite.com/Animation/PlayAnimation }
using { /Fortnite.com/Playspaces }
using { /Verse.org/Simulation }
using { /Verse.org/Assets }

emote_toggle_device := class(creative_device):

    @editable
    EmoteButton : input_trigger_device = input_trigger_device{}

    @editable
    Emote : ?animation_sequence = false

    # True: arms only, the player keeps walking (UpperBody layer). False: whole body, player frozen.
    @editable
    UpperBodyOnly : logic = false

    # How many times the clip plays; a big number keeps it going until the button is pressed again.
    @editable
    PlayCount : float = 1.0

    var Playing : [agent]play_animation_instance = map{}

    OnBegin<override>()<suspends>:void =
        EmoteButton.PressedEvent.Subscribe(OnPressed)
        GetPlayspace().PlayerRemovedEvent().Subscribe(OnPlayerRemoved)

    OnPressed(Agent:agent):void =
        if (Instance := Playing[Agent], Instance.IsPlaying[]):
            Instance.Stop()
        else:
            spawn{ PlayEmote(Agent) }

    OnPlayerRemoved(Player:player):void =
        if (Instance := Playing[Player]):
            Instance.Stop()
        Forget(Player)

    PlayEmote(Agent:agent)<suspends>:void =
        if:
            Clip := Emote?
            Character := Agent.GetFortCharacter[]
            not Character.IsInAir[]
            Controller := Character.GetPlayAnimationController[]
        then:
            Layer := if (UpperBodyOnly?) then play_animation_layer.UpperBody else play_animation_layer.FullBody
            if (not UpperBodyOnly?):
                Character.PutInStasis(stasis_args{AllowTurning := false, AllowFalling := false, AllowEmotes := false})
            Instance := Controller.Play(Clip, ?Layer := Layer, ?PlayCount := PlayCount,
                ?BlendInTime := 0.2, ?BlendOutTime := 0.2)
            if (set Playing[Agent] = Instance) {}
            Instance.Await()   # Completed, Interrupted (emote / fire / Stop) or Error
            if (not UpperBodyOnly?):
                Character.ReleaseFromStasis()
            Forget(Agent)

    # Rebuild the map without Agent (Verse maps have no remove).
    Forget(Agent:agent):void =
        var Kept : [agent]play_animation_instance = map{}
        for (Key -> Value : Playing, Key <> Agent):
            if (set Kept[Key] = Value) {}
        set Playing = Kept
```

- `not Character.IsInAir[]` refuses the emote mid-jump: with `AllowFalling := false` a
  frozen player would hang in the air.
- Input trigger: Interact (or any key), **Consume Input** on. It registers every player
  by default.
- Hide the Verse device in game (Visible in Game off).

## Teleport (frame the player for a cutscene)

```verse
@editable
TeleportLocation : vector3 = vector3{}

@editable
YawDegrees : float = 0.0
@editable
PitchDegrees : float = 0.0
@editable
RollDegrees : float = 0.0

# Inside PlayOnAgent, before Play:
if (FortCharacter.TeleportTo[TeleportLocation, MakeRotationFromYawPitchRollDegrees(YawDegrees, PitchDegrees, RollDegrees)]):
```

`TeleportTo` is `<decides>` — put it in an `if`. Place the XYZ carefully (under
the floor is a common first-try miss). Useful with stasis + a full-override clip
for scripted beats.

## Assets digest — why the clip name is "undefined"

Every AnimSequence under your project Content is exposed to Verse through
`Assets.digest.verse` after a **successful** Verse compile:

1. Clip lives under a Content folder (e.g. `Animations/SillyDance1`).
2. `using { /Verse.org/Assets }` in the device file.
3. Fix any Verse errors, then compile — the identifier appears
   (`Animations.SillyDance1` or whatever the folder path maps to).
4. Or skip the bare identifier and assign the clip on an
   `@editable Clip : animation_sequence` in the device Details panel.

A broken Verse build is the usual reason the name never shows up.

## Authoring an additive overlay (Layered Control Rig)

Pipeline:

1. Content Drawer → **Cinematics → Level Sequence**. Open it.
2. Place / find **M_Medium_Base** (Fortnite player skeleton — invisible mesh,
   bones are there). Add it to the sequence (Add → track for that skeletal mesh).
3. Optional: delete the default Animation track.
4. **+ → Control Rig**. Turn **Filter by Asset Skeleton OFF**, turn
   **Layered ON**, then pick **FX Control Rig** (bones visible) or **Body Rig**.
5. Layered Control Rigs are **naturally additive** and non-destructive: values
   are deltas from the underlying pose. Rotation/translation **0** and scale
   **1** mean "no change". Editing a layered rig on top of a dance clip does
   not rewrite the dance.
6. Key everything at the start. Move **only** the bones you want to overlay
   (e.g. raise an arm for a wave, scale root for giant/tiny). Key the return.
7. Right-click the skeleton track → **Bake Animation Sequence**. Save.
8. Flip additive: `set_anim_additive_type({"anim_paths": [".../AS_ArmUp"],
   "additive_type": "local_space"})` (or Property Matrix → Local Space).
9. Play with the Verse device above — Fortnite walk/run continues underneath.

### Giant / tiny / horror proportions

Same pipeline: key **root** (or pelvis / arms / head) **scale** on the layered
rig, bake, set Local Space, play. Visual only — see Limits.

### Getting Fortnite Control Rigs into a project

Project Browser → **Feature Examples → Animation** → create it → Content Drawer →
right-click the **Fortnite** folder → **Migrate** → pick your island's `Content` folder.
An empty Fortnite folder after migrating means UEFN needs a reopen. You get:

| Rig | Use |
|-----|-----|
| **Body Rig** | Body controls. Global control → **FK/IK switches** per arm, leg and spine (rotate circles vs drag a box) |
| **Face Rig** | Classic Fortnite faces |
| **MetaHuman Face Rig** | MetaHuman skins; use it for those, the classic face rig stops working on them |

### Layering a clip in Sequencer (base + additive + face)

1. Bind the mesh (M_Medium_Base, a Player Reference, or a placed mannequin); **+ → Control
   Rig**, skeleton filter **off**, **Body Rig**.
2. Right-click the Body Rig track → **Import Sequence** (load the AnimSequence into the
   rig) with **Reduce Keys** on. Without it every frame is a key and the editor crawls.
3. **+ → Additive** on the same rig: a second section that adds deltas on top. Key only what
   changes (head up, a hand wave). Realism trick: a breathing idle in the base, the actions in
   the additive layer.
4. **+ Control Rig → Face Rig / MetaHuman Face Rig** for expressions (eyes, brows, jaw).
5. Trim the playback range, then right-click → **Bake Animation Sequence**. Layered rigs
   with thousands of keys are expensive; ship the baked clip and delete the rig tracks.

### Mixamo / FBX full-body clips (usually override)

1. Mixamo: mannequin + clip, **FBX Binary**, **With Skin** (In Place if you will add a
   Transform track later).
2. First import: **Skeleton = None** (creates the Mixamo skeleton; rename it). Later clips:
   Skeleton = that one. Turn on **Use T0 As Reference Pose** or the skeleton's rest pose is
   the clip's first frame (the option has behaved backwards on some builds; flip it if the
   rest pose comes out wrong).
   Shortcut without your own IK rigs: right-click the clip → **Retarget Animations** →
   Source = Mixamo mesh, Target = **M_Medium_Base** (male player body; **F_Medium_Base** for
   the female body — find both with `search_assets`) → Export. The target is invisible in
   the preview (no visual mesh); preview on any other mesh to see it move.
3. IK Rigs: Mixamo mesh, and **M_Medium_Base** for the player (not FN_Mannequin). Auto
   Create Retarget Chains + Auto Create IK on both (`retarget_animation_pipeline` does it
   headlessly, Mixamo preset included).
4. Retargeter: Edit Retarget Pose → raise the target's arms to the Mixamo T-pose, match
   **Target Mesh Scale** so the sizes agree, fix fingers if they read wrong → Asset Browser
   → Export Selected Animations into a `Retargeted` folder (thumbnails look blank; the clips
   are fine).
3. Play via the Verse device. Leave Additive = No Additive for a full dance
   takeover; set Local Space only if the clip was authored as a delta overlay.

Retarget details: `skill_read_subskill("animation", "retargeting")`.

### One clip for a whole player cutscene (run → blast → fall)

When the beat needs several clips and the player has to travel, bake them into **one**
AnimSequence. Then the timing and the travel can't drift apart.

1. Level Sequence → bind an FN Mannequin / M_Medium_Base placed exactly where the player
   will start. Stack the clips on one Animation track and blend them with the ease
   triangles (`anim_authoring` § Blending).
2. Right-click the mesh track → **Bake to Control Rig** → FK Control Rig, **Reduce Keys** on.
3. Move the character by keying the rig's **root** control, not a Transform track. A
   Transform track is not baked into the clip. Key the root at takeoff and landing, and
   delete stray root keys after the landing.
4. Bake Animation Sequence → one clip (e.g. `AS_ExplosionCutscene`) → play it with the
   Verse device above, with stasis. Effects and camera: a Cinematic Sequence started
   from the same trigger (`sequencer_cinematics` § FX and sound tracks).

> Unverified: whether baked root travel moves the player's capsule or only the mesh.
> Check in a session, and `TeleportTo` the landing spot after `Await()` if the capsule
> stays behind.

### Legacy: chair-device `DefaultAnimation` (do not use)

Old tutorials (2024) copy a Chair device as T3D text, add a hidden
`DefaultAnimation="<Copy Reference of an FN-skeleton AnimSequence>"` line (a missing comma
fails validation), and paste it back. Then they seat the player with a trigger. It was an
unreleased property: it isn't shown in Details, it isn't documented, and it can break on
any update. Use `GetPlayAnimationController`. If the person's island already has one of
these chairs, look for the hidden line in the chair's copied text before you change it.

## Player Reference route (a stand-in copy of the player)

The pre-controller method, still useful when the shot needs a full Level Sequence on the
player's look: face rig animation, a camera, several actors, Niagara/audio tracks.

1. **Player Reference device**: Visible in Game on, **Hologram Strength 0** (looks like the
   real player), Show Base off, Activate Sequencer off. *Only Take Animation Pose When
   Rendered* pauses it when nobody is looking; *Use First Local Player Visual If Empty* fills
   it with the local player when nothing is registered.
2. Level Sequence: bind the Player Reference, add the clip (or the rig layers above), press
   **G** and drop it onto the floor.
3. **Cinematic Sequence device**: the sequence, Loop Playback, Visibility **Instigator Only**
   for multiplayer (Everyone for a show).
4. Verse: `PlayerRef.Register(Agent)`, `Enable()`, `TeleportTo[...]` it to the player (about
   **−85 cm Z** so it stands on the floor), `Character.Hide()` + stasis, `Cine.Play(Agent)`. End:
   `Cine.Stop(Agent)`, `PlayerRef.Clear()`, `Disable()`, `Character.Show()`,
   `ReleaseFromStasis()`.
5. Multiplayer: one Player Reference + one Cinematic Sequence (its own copy of the sequence
   asset bound to that reference) **per possible player**, at the same array index; a
   `[]logic` free list, a `[agent]int` slot map, free the slot on `PlayerRemovedEvent`.

Limits: the copy drops **back blings**; long loops can stop early (restart from
`StoppedEvent`); every player needs a pre-placed reference. For a plain emote, use
`GetPlayAnimationController`: no pool, the real character, any number of players.

## Hard limits (do not paper over these)

- **No custom bone masks.** The only split is `?Layer := play_animation_layer.UpperBody`
  (upper body while moving). You cannot say "this bone 100% custom, that bone 100%
  Fortnite".
- **Emoting or firing a weapon resets** the anim controller back to default
  Fortnite animations. Design around it (stasis with `AllowEmotes := false`,
  short clips, or accept the reset).
- **Root / bone scale is visual only.** Hitboxes do not grow or shrink with a
  giant/tiny overlay.
- **Without Local Space**, the clip fully overrides locomotion — that is
  correct for dances, wrong for arm overlays.
- Confirm `GetPlayAnimationController` on this build before promising the
  feature — it was guards/NPCs only for a long time; players are recent.

## Use cases this unlocks

Weapon inspect, melee / punch, immersive interact poses, giant/tiny power-ups,
horror silhouette twists, short emote-like moments without the Emote wheel —
all on the real player character while (for additive) they keep walking.

## Failure table

| Symptom | Cause |
|---------|-------|
| Clip replaces walk instead of overlaying | Additive Anim Type still No Additive — run `set_anim_additive_type` / Property Matrix Local Space |
| Verse can't see the clip name | Assets digest stale — fix Verse errors, compile |
| `GetPlayAnimationController` fails | No `fort_character`, or build predates player support — confirm digest |
| Player stuck after clip | Forgot `ReleaseFromStasis` on an Interrupted / Error / race exit |
| Overlay snaps off mid-play | Player emoted or fired — controller reset (known limit) |
| Want arms-only while the player runs | `?Layer := play_animation_layer.UpperBody`, no stasis |
| Emote button does nothing mid-jump | `IsInAir[]` guard (by design) — or drop it and allow falling in stasis |
| Player Reference copy floats / missing back bling | Offset it about −85 cm Z; back blings are a known Player Reference limit |
| Player Reference loop stops after a while | Restart the Cinematic Sequence from `StoppedEvent` |
| Giant/tiny looks right but collisions wrong | Scale is visual only — hitboxes unchanged |
| Layered rig edits overwrite the dance | Used a non-layered Control Rig — enable **Layered** when adding the rig |
| Property Matrix / tool can't set additive | UEFN build missing the enum — `anim_author_capabilities` → `additive_route`; use the UI hint in the tool response |
