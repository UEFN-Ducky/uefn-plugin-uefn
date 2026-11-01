---
description: "NPC AI in Verse — npc_behavior templates on npc_actions_component (43.00: NavigateTo / Focus / Idle / StopNavigation / MovementSpeedMultiplier; GetNavigatable, GetFocusInterface, GetFortLeashable, movement_types deprecated), guard_actions_component Tether / RoamAround, nearest-player lookup, spread/strafe movement, centralized damage, Scene Graph projectiles, and wave spawn managers"
metadata:
  order: 40
  label: "Game systems — NPC AI (npc_behavior)"
  default_enabled: false
  load_condition: "Writing npc_behavior subclasses, enemy AI loops, melee/ranged combat, Scene Graph projectiles, or npc_spawner wave managers"
---

## NPC AI — `npc_behavior` patterns

> **Talking NPCs (42.30):** an NPC with a Persona Modifier answers players by voice and can drive gameplay through structured output — `sys_conversations` (template `llm_npc`).

> **Snippets here are fragments.** The `using` block in this file's first code
> block applies to all of them — copy those imports (or start from the matching
> `verse_template_apply` pack) when pasting into a real `.verse` file.

The code below is verified against the **43.00** digests (the chaser and guard
behaviors compiled with 0 errors on Nov 1 2026) — copy names and signatures as-is
(`npc_behavior`, `npc_actions_component`, `guard_actions_component`, `PlayAndAwait`,
`npc_spawner_device`, `Distance`); do NOT re-check them one by one.

> **43.00 deprecated the old NPC interfaces.** Use `npc_actions_component` (from
> `Char.GetEntity[].GetComponent[npc_actions_component]`) instead of:
>
> | Deprecated | Use |
> |-----------|-----|
> | `Char.GetNavigatable[]` → `NavigateTo` / `StopNavigation` / `Wait` / `SetMovementSpeedMultiplier` / `GetCurrentDestination` | `Actions.NavigateTo(…)` (returns `result(navigation_action_success_type, navigation_action_error_type)`, not the `navigation_result` enum) / `StopNavigation()` / `Idle(?Duration)` / `set Actions.MovementSpeedMultiplier = 1.2` (0.5–2) / `GetCurrentDestination[]` (`/Verse.org/SpatialMath` vector) |
> | `Char.GetFocusInterface[]` → `MaintainFocus(Pos or Agent)` (never ended) | `Actions.Focus(Entity or /Verse.org/SpatialMath vector3, ?LockFocus := true)`; `LockFocus := false` ends once facing |
> | `Char.GetFortLeashable[]` → `SetLeashPosition` / `SetLeashAgent` / `ClearLeash` | guards: `guard_actions_component.Tether(Entity or vector3, Radius)` / `Untether()` |
> | `movement_types.Running` | `movement_type.Running` (also `Walking`, `Sprinting`) |
>
> Old code still compiles with deprecation warnings; write new code on the component. Digest-check only APIs you add that are not shown here (e.g.
foliage/grass queries), then write and let `workspace_list_verse_errors` catch
drift. Pair this with the **animation** pack's `npc_characters` reference for
character definitions and AnimPresets — Verse owns behavior; content owns mesh/anim.

### Hard constraints (read first)

| Trap | Rule |
|------|------|
| `npc_behavior` calling `GetPlayspace()` | **Fails / unavailable.** Use `Behavior.GetEntity[]` → `GetPlayspaceForEntity[]` → `GetPlayers()`. |
| Module-scope mutable singletons for AI state | Illegal under `<transacts>` in many contexts. Session `weak_map(session, []agent)` registries for NPC-to-NPC awareness are OK if you **fetch the arrays in a void context** then pass them into a `<transacts>` checker — see `skill_read_subskill("animation", "npc_ecosystem")`. Never this pattern on persist maps. |
| Asking a human to hook NPCDef / AnimPreset / anim slots | **Forbidden.** `create_npc_character_definition`, `create_anim_preset`, `create_character_blueprint`, `set_npc_spawner_definition`. Reaction clips: duplicate into the Verse module folder and hardcode the ids. |
| Behaviors calling `fort_character.Damage` | **Never.** One shared helpers module owns damage (`ApplyHitDamage` / melee / AOE / projectile). Behaviors only call those helpers after a real hit. |
| `SpawnProp` walls vs SG projectile sweeps | `FindSweepHits` only sees **Scene Graph** colliders (`Queryable`). Creative props are invisible to SG queries — walls/cover must be SG entities if projectiles should block. |

---

## 1. Behavior skeleton

Every enemy type is a `class(npc_behavior)` with `@editable` tuning and an
`OnBegin` loop. Guard the interfaces once, then tick until the character dies:

```verse
using { /Verse.org/Assets }
using { /Fortnite.com/Characters }
using { /Fortnite.com/AI }
using { /Fortnite.com/Animation/PlayAnimation }   # GetPlayAnimationController (without it: 3506)
using { /UnrealEngine.com/Temporary/SpatialMath }
using { /Verse.org/Random }
using { /Verse.org/SceneGraph }
using { /Verse.org/SceneGraph/KeyframedMovement }
using { /Verse.org/Simulation }
melee_enemy_behavior<public> := class(npc_behavior):
    @editable AttackAnim:?animation_sequence = false
    @editable HitRange:float = 220.0
    @editable HitDamage:float = 18.0
    @editable HitCooldown:float = 1.3
    @editable MaxChaseRange:float = 7500.0
    @editable SpreadDist:float = 260.0
    @editable EnableSidestep:logic = false
    @editable SidestepChance:int = 35

    OnBegin<override>()<suspends>:void =
        if:
            Agent := GetAgent[]
            Char := Agent.GetFortCharacter[]
            Actions := Char.GetEntity[].GetComponent[npc_actions_component]
            Anim := Char.GetPlayAnimationController[]
        then:
            loop:
                Sleep(0.1)
                if (not Char.IsActive[]):
                    break
                if (Target := FindNearestPlayer(Self, Char, MaxChaseRange)?):
                    # chase / attack — see sections below
                else:
                    Actions.Idle(?Duration := 1.0)
```

**What you almost always need:**

- `Actions.NavigateTo(MakeNavigationTarget(Agent or Position), ?MovementType := movement_type.Running, ?ReachRadius := …)`; read failure with `if (NavError := Result.GetError[])`. Never name the binding `Err`: it clashes with Verse's `Err` function (3588/3532).
- `Actions.Focus(TargetEntity, ?LockFocus := true)`: async and never ends while locked, so race it.
- `Char.GetPlayAnimationController[]` → `PlayAndAwait(Clip)` for attack swings (not deprecated).
- Guards: `Ent.GetComponent[guard_actions_component]` adds `Tether`, `Untether`, `RoamAround`, `MoveInRangeToAttack`, `Attack(Target)`, `Crouch`, `Jump`, `Slide`.

### Complete chaser (compiled, 43.00)

```verse
using { /Fortnite.com/AI }
using { /Fortnite.com/Characters }
using { /Fortnite.com/Playspaces }
using { /UnrealEngine.com/Temporary/SpatialMath }
using { /Verse.org/SceneGraph }
using { /Verse.org/Simulation }

chaser_behavior<public> := class(npc_behavior):
    @editable ChaseRange:float = 5000.0
    @editable SpeedMultiplier:float = 1.2

    OnBegin<override>()<suspends>:void =
        if:
            Char := GetAgent[].GetFortCharacter[]
            Actions := Char.GetEntity[].GetComponent[npc_actions_component]
        then:
            set Actions.MovementSpeedMultiplier = SpeedMultiplier
            loop:
                if (not Char.IsActive[]):
                    break
                if (Target := NearestPlayer(Char)?, TargetEnt := Target.GetFortCharacter[].GetEntity[]):
                    race:
                        ChaseOnce(Actions, Target)
                        Actions.Focus(TargetEnt, ?LockFocus := true)   # never ends: race it
                        Sleep(0.5)                                     # re-target twice a second
                else:
                    Actions.Idle(?Duration := 1.0)

    ChaseOnce(Actions:npc_actions_component, Target:agent)<suspends>:void =
        Result := Actions.NavigateTo(MakeNavigationTarget(Target), ?MovementType := movement_type.Running, ?ReachRadius := 150.0)
        if (NavError := Result.GetError[], NavError = navigation_action_error_type.Unreachable):
            Actions.StopNavigation()

    NearestPlayer(Char:fort_character)<transacts>:?player =
        var Best:?player = false
        var BestDist:float = ChaseRange
        if (Ent := GetEntity[], PS := Ent.GetPlayspaceForEntity[]):
            SelfPos := Char.GetTransform().Translation
            for (P : PS.GetPlayers(), PC := P.GetFortCharacter[], PC.IsActive[]):
                D := Distance(SelfPos, PC.GetTransform().Translation)
                if (D < BestDist):
                    set Best = option{P}
                    set BestDist = D
        Best

# Guards: tether to a player and roam inside the radius.
guard_roam_behavior<public> := class(npc_behavior):
    @editable TetherRadius:float = 1500.0

    OnBegin<override>()<suspends>:void =
        if:
            Ent := GetAgent[].GetFortCharacter[].GetEntity[]
            Guard := Ent.GetComponent[guard_actions_component]
            Ps := Ent.GetPlayspaceForEntity[]
            Anchor := Ps.GetPlayers()[0].GetFortCharacter[].GetEntity[]
        then:
            Guard.Tether(Anchor, TetherRadius)
            Guard.RoamAround(?MovementType := movement_type.Walking)
```

Passing a target **entity** to `Focus` and an **agent** to `MakeNavigationTarget` keeps the
file on `/UnrealEngine.com/Temporary/SpatialMath` (fort_character positions). Position
overloads of `Focus`, `Tether` and `GetCurrentDestination` take `/Verse.org/SpatialMath`
vectors, so convert or put that code in its own file.

### Nearest-player helper (no wired manager required)

```verse
FindNearestPlayer<public>(Behavior:npc_behavior, FortChar:fort_character, DetectionRange:float)<transacts>:?fort_character =
    var Best:?fort_character = false
    var BestDist:float = DetectionRange
    if (Ent := Behavior.GetEntity[], PS := Ent.GetPlayspaceForEntity[]):
        SelfPos := FortChar.GetTransform().Translation
        for (Player : PS.GetPlayers(), PlayerChar := Player.GetFortCharacter[]):
            if:
                PlayerChar.IsActive[]
                not PlayerChar = FortChar
                D := Distance(SelfPos, PlayerChar.GetTransform().Translation)
                D < BestDist
            then:
                set Best = option{PlayerChar}
                set BestDist = D
    Best
```

Look-at for focus: aim at the **target position** — do not invent global yaw
hacks. If a mesh faces the wrong way, fix the character asset axis, not every
behavior's look offset.

---

## 2. Movement idioms — race focus + navigate

Chase and fight while facing the player. Cap each hop with `Sleep` so the loop
can re-target:

```verse
if (TargetEnt := TargetChar.GetEntity[]):   # GetEntity[] can fail: bind it in an if (bare: 3512)
    race:
        Actions.NavigateTo(MakeNavigationTarget(Approach), ?MovementType := movement_type.Running, ?ReachRadius := 150.0)
        Actions.Focus(TargetEnt, ?LockFocus := true)
        Sleep(0.55)
```

### Spread ring (packs fan out instead of stacking)

Approach a ring around the player with a random side offset:

```verse
# PreferDist = desired stand-off; SideMin/SideMax = lateral scatter on a random side.
# vector3 here is /UnrealEngine.com/Temporary/SpatialMath (fort_character positions).
SpreadApproachPoint(SelfPos : vector3, TargetPos : vector3, PreferDist : float, SideMin : float, SideMax : float) : vector3 =
    Away := SelfPos - TargetPos
    Len := Max(Sqrt(Away.X * Away.X + Away.Y * Away.Y), 1.0)
    RingDir := vector3{X := Away.X / Len, Y := Away.Y / Len, Z := 0.0}
    Lateral := vector3{X := -RingDir.Y, Y := RingDir.X, Z := 0.0}
    Side := GetRandomFloat(SideMin, SideMax) * (if (GetRandomInt(0, 1) = 0) then -1.0 else 1.0)
    TargetPos + RingDir * PreferDist + Lateral * Side
```

### Sidestep hop

Optional checkbox + percent chance: jump left/right while still facing the fight.
Gate with `EnableSidestep` then `GetRandomInt(1, 100) <= ChancePercent`.

---

## 3. Centralized damage (one helpers file)

**Behaviors must never call `Target.Damage`.** Put all hit application in one
module so print tags, VFX, and balance stay consistent:

```verse
ApplyHitDamage(Target:fort_character, Amount:float, Tag:string):void =
    if (Target.IsActive[]):
        Print("{Tag} dmg={Amount}")
        Target.Damage(Amount)

# Melee: only damage if STILL inside HitRange after the swing finishes
MeleeHit(Attacker:fort_character, Target:fort_character, HitRange:float, Amount:float):logic =
    Dist := Distance(Attacker.GetTransform().Translation, Target.GetTransform().Translation)
    if (Dist <= HitRange):
        ApplyHitDamage(Target, Amount, "MELEE HIT")
        return true
    false

# AOE: every active player within Radius of Center
AOEHit(Behavior:npc_behavior, Center:vector3, Radius:float, Amount:float):void =
    if (Ent := Behavior.GetEntity[], PS := Ent.GetPlayspaceForEntity[]):
        for (Player : PS.GetPlayers(), PChar := Player.GetFortCharacter[]):
            if (PChar.IsActive[], Distance(Center, PChar.GetTransform().Translation) <= Radius):
                ApplyHitDamage(PChar, Amount, "AOE HIT")
```

Melee attack block pattern:

```verse
race:
    Actions.Focus(TargetEnt, ?LockFocus := true)
    block:
        if (Clip := AttackAnim?):
            Anim.PlayAndAwait(Clip)
        MeleeHit(Char, Target, HitRange, HitDamage)
        Sleep(HitCooldown)
```

---

## 4. Scene Graph projectile (ranged)

Creative `SpawnProp` arrows do **not** collide with SG walls. Use an entity +
mesh component + keyframed motion:

1. Spawn `entity{}`, add a **`transform_component`** (without one the mesh is
   not positioned at all), then `sphere` (or a mesh) with `Collidable = true`,
   `Queryable = true`, `Visible = true`.
2. Add `keyframed_movement_component`, `Sim.AddEntities`, `SetGlobalTransform` at muzzle.
3. **Pre-sweep** walls: `FindSweepHits` along the flight path; clamp end position to first hit past a min clearance.
4. Build one `keyframed_movement_delta` (translation delta, duration = distance/speed, linear easing), `SetKeyframes` + `Play`. `SetKeyframes` rebases onto the entity's **current** transform and does not autoplay — so muzzle placement must happen before it, and `Play()` is mandatory.
5. Per-frame check via `TickEvents.PrePhysics` on the component that owns the shot: read the transform; if within `HitRadius` of the aim point → `ApplyHitDamage` and stop; optional shoot-down (player holding fire + aim ray near projectile); finish on `FinishedEvent`. Cancel the subscription when the shot ends.
6. Cleanup: cancel trail VFX handles, `RemoveFromParent()`.

```verse
using { /UnrealEngine.com/BasicShapes }   # cube / sphere / plane / cone / cylinder

ArrowEnt := entity{}
Xform := transform_component{Entity := ArrowEnt}
Mesh := sphere{Entity := ArrowEnt}
set Mesh.Collidable = true
set Mesh.Queryable = true
set Mesh.Visible = true
MoveComp := keyframed_movement_component{Entity := ArrowEnt}
ArrowEnt.AddComponents(array{Xform, Mesh, MoveComp})
if (Sim := GetSimulationEntity[]):
    Sim.AddEntities(array{ArrowEnt})
# SetGlobalTransform → FindSweepHits pre-sweep → SetKeyframes → Play → PrePhysics hit check → RemoveFromParent
```

Lifecycle, `TickEvents` and transform rules:
`skill_read_subskill("scenegraph", "movement_transforms")`.

**Shoot-down trap:** Fortnite guns cannot damage SG spheres. Track "fire held"
via an `input_trigger_device` (see `sys_input_devices`) into a `weak_map(player, logic)`,
then each frame: if fire held AND aim ray within `ShootDownRadius` of the projectile → destroy + VFX.

**Do not drive the flight with `loop` + `Sleep(0.0)`.** That is not a frame hook
— it stutters and can read a transform the physics step has not applied yet.
Keyframed movement plays in the Pre-Physics phase, so check hits from
`TickEvents.PrePhysics` and cancel the subscription in `OnEndSimulation`.

**Walls:** dungeon / cover colliders must be Scene Graph entities with Queryable
collision, or every shot flies through.

---

## 5. Archetype variants (same skeleton, different params)

| Archetype | Prefer range | Attack |
|-----------|--------------|--------|
| Melee | close `HitRange` | anim + `MeleeHit` |
| Ranged / archer | keep `PreferMin`–`PreferMax`; back off if too close | anim + SG projectile |
| Charger | large chase; slam at `SlamRange` | optional wind-up `Sleep` then `MeleeHit` |
| Exploder | close then AOE | `AOEHit` at self / fuse point |

Reuse spread/strafe helpers; only ranges, damage, cooldown, and the attack call differ.

---

## 6. Wave spawn manager (`creative_device`)

Wire one `npc_spawner_device` per character definition (see animation
`npc_characters`). The manager counts alive and spawns waves:

```verse
using { /Fortnite.com/Devices }
enemy_spawn_manager := class(creative_device):
    @editable SpawnerA:?npc_spawner_device = false
    # … more optional spawners …
    @editable SpawnInterval:float = 8.0
    @editable MaxAlive:int = 40
    @editable SeedWaveOnStart:logic = true
    @editable AutoSpawn:logic = true
    var AliveCount:int = 0

    OnBegin<override>()<suspends>:void =
        # Subscribe SpawnedEvent / EliminatedEvent on every wired spawner
        # AliveCount += 1 on spawn; Max(0, AliveCount - 1) on eliminate
        if (SeedWaveOnStart?):
            SpawnAllTypes()
        if (AutoSpawn?):
            loop:
                Sleep(SpawnInterval)
                if (AliveCount < MaxAlive):
                    SpawnAllTypes()

    TrySpawn(Maybe:?npc_spawner_device):void =
        if (AliveCount < MaxAlive, S := Maybe?):
            S.Spawn()
```

Event / `Spawn()` signatures are as shown — re-check in the digest only if the
error list flags one. Each spawner in the level points at one
`NPCCharacterDefinition` asset.

---

## Checklist — new enemy type

1. Content via **tools**: mesh + physics + AnimPreset + character BP + `NPCCharacterDefinition` (`npc_characters`). Never Details.
2. Verse: `verse_template_apply("npc_core")` then customize class names/clips for this island. Multi-species patterns: `skill_read_subskill("animation", "npc_ecosystem")`. Apply `npc_ecosystem` only if they asked for that cat+dog example.
3. Reaction/attack clips: duplicate into the behavior folder; reference by name. Do not fill NPCDef Details.
4. Place `npc_spawner_device` → `set_npc_spawner_definition` → `wire_verse_device_ref` into spawn manager.
5. `workspace_list_verse_errors` → fix until clean.
6. PIE: confirm chase, hit prints, elimination counting.

**MetaHuman enemies:** assemble with UEFN Export and finish mesh / physics /
AnimPreset / spawn wiring via `skill_read_subskill("metahuman", "npc_spawn")`
*before* writing `npc_behavior` — Verse owns the AI loop; the metahuman pack
owns Creator → assemble → definition.

Optional deep-dives (load only if stuck — this file is sufficient for standard NPC AI): `sys_spawning` (prop pools / teleport), `sys_input_devices` (shoot-down fire held), `async` (`race` / `Sleep`), `devices` (`@editable` / `OnBegin`), metahuman `npc_spawn`.
