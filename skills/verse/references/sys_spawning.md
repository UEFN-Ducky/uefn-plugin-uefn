---
description: "Spawning at runtime, Scene Graph first — what to spawn with (Entity Prefab vs NPC spawner vs player spawner vs prop), spawning and despawning prefab instances with GetSimulationEntity/AddEntities/RemoveFromParent, pools of prefab instances (hide with mesh_component Disable, reuse), motion for spawned things, wave managers built with for-expressions, NPC spawner events and elimination payloads, reliable player teleport, and creative_prop SpawnProp/MoveTo as the fallback"
metadata:
  order: 26
  label: "Game systems — spawning, pools & waves"
  default_enabled: false
  load_condition: "Spawning anything at runtime (projectiles, pickups, debris, enemies, platforms, waves), pooling spawned objects, moving spawned things, tracking NPC eliminations, or teleporting players reliably"
---

## Spawning at runtime — Scene Graph first

> **Snippets here are fragments.** The `using` block in this file's first code
> block applies to all of them — copy those imports (or start from the matching
> `verse_template_apply` pack) when pasting into a real `.verse` file.

### What to spawn with

| Spawning | Use |
|----------|-----|
| Projectiles, pickups, debris, platforms, streamed pieces, enemies built as objects | **Entity Prefab** instances (`EP_*` / `P_*` from Assets.digest) — this page |
| Fortnite NPCs, guards, creatures, wildlife | `npc_spawner_device` & co — "NPC spawners" below, `sys_npc_ai` |
| Players | `player_spawner_device` (`sys_damage_health`) |
| A prop with no prefab and no entity path | `creative_prop` — "Fallback" at the end |

Always-on scenery is placed once in the editor (`instantiate_prefab`), not spawned
every match. Anything spawned more than a few times a minute comes from a **pool**.

### Spawn and despawn a prefab instance

The prefab's class exists after the next Verse build (scenegraph
`verse_authoring`). Parent it under the simulation entity, then place it:

```verse
using { /Fortnite.com/Devices }
using { /Verse.org/SceneGraph }
using { /Verse.org/SpatialMath }
using { /Verse.org/Simulation }

SpawnCrate(Position : vector3) : void =
    if (Sim := GetSimulationEntity[]):          # creative_device extension, <transacts><decides>
        Crate := EP_Crate{}
        Sim.AddEntities(array{Crate})
        T := Crate.GetGlobalTransform()
        Crate.SetGlobalTransform(transform{Translation := Position, Rotation := T.Rotation, Scale := T.Scale})
```

`Crate.RemoveFromParent()` takes it out of the scene (its components run
`OnEndSimulation`); `AddEntities` can add it back later. Removing and re-adding
in bursts is what a pool avoids.

### Pool of prefab instances

Create the pool once, hide spare instances, hand one out per use, hide it again
when done:

```verse
crate_dropper_device := class(creative_device):
    @editable PoolSize : int = 20
    @editable LifeSeconds : float = 5.0

    var Free : []entity = array{}

    OnBegin<override>()<suspends> : void =
        if (Sim := GetSimulationEntity[]):
            Crates := for (Index := 1..PoolSize) do EP_Crate{}
            Sim.AddEntities(Crates)
            for (Crate : Crates):
                SetShown(Crate, false)
            set Free = Crates

    DropAt(Position : vector3)<suspends> : void =
        if (Crate := Free[0], Rest := Free.RemoveElement[0]):
            set Free = Rest
            T := Crate.GetGlobalTransform()
            Crate.SetGlobalTransform(transform{Translation := Position, Rotation := T.Rotation, Scale := T.Scale})
            SetShown(Crate, true)
            Sleep(LifeSeconds)
            SetShown(Crate, false)
            set Free += array{Crate}            # one append per release, not in a loop

    # Enable / Disable have no effect specifier: straight-line code only.
    SetShown(Crate : entity, Shown : logic) : void =
        for (Mesh : Crate.FindDescendantComponents(mesh_component)):
            if (Shown?):
                Mesh.Enable()
            else:
                Mesh.Disable()
```

- Pool empty → skip the spawn (or grow the pool by a few) rather than block.
- Several players: one pool per system, sized for the worst case, not per player.
- A pool of devices or widgets uses the generic `pool(t)` in `design_patterns`.

### Moving what you spawned

- A thrown, dropped or flying object: one `keyframed_movement_component` delta
  over its flight time (scenegraph `movement_transforms`).
- A platform or door loop: keyframed `loop` / `pingpong` playback.
- Chasing or steering: one manager loop for all instances, pure state per frame,
  visuals pushed ~10 times a second (`runtime_pitfalls`).
- Never `SetGlobalTransform` each tick to animate.

### Wave manager

The manager owns the live list and the wave loop; it stops with the round:

```verse
var ActiveEnemies : []enemy = array{}

RunWaves()<suspends> : void =
    race:
        RoundEndedEvent.Await()
        loop:
            SpawnWave()
            Sleep(WaveInterval)

# Drop eliminated enemies with a for-expression, never += in a loop.
PruneEnemies() : void =
    set ActiveEnemies = for (Enemy : ActiveEnemies, Enemy.IsAlive?) do Enemy
```

Closest target: one pass with `Distance` and a running best, run when targets
change or a few times a second — not every frame for every enemy.

### NPC spawners

Engine NPCs come from `npc_spawner_device` (and guard / creature / wildlife
spawners). Their `EliminatedEvent` sends `device_ai_interaction_result`:

```verse
Spawner.SpawnedEvent.Subscribe(OnNpcSpawned)            # agent
Spawner.EliminatedEvent.Subscribe(OnNpcEliminated)

OnNpcEliminated(Result : device_ai_interaction_result) : void =
    if (Eliminator := Result.Source?):                   # empty for falls, storms
        AwardKill(Eliminator)
    set AliveNpcs -= 1
    if (AliveNpcs <= 0):
        spawn{ StartNextWave() }
```

Behaviour, equipment and Scene Graph NPCs: `sys_npc_ai` and the `npc-ai` skill.

### Placing a player once (teleport with retry)

One-off placement (round start, return to hub) uses `TeleportTo[]`. It can fail
while the destination is blocked or the player is still loading — retry briefly
and confirm arrival:

```verse
TeleportWithRetry(Agent : agent, Position : vector3)<suspends> : void =
    for (Attempt := 1..30):
        if:
            FortCharacter := Agent.GetFortCharacter[]
            FortCharacter.TeleportTo[Position, IdentityRotation()]
            Distance(FortCharacter.GetTransform().Translation, Position) <= 100.0
        then:
            return
        Sleep(0.1)
```

A teleport is for placing a player, never for moving one over time — carry a
player in a moved `chair_device` (`runtime_pitfalls`).

### Fallback: `creative_prop`

Only when there is no prefab and no entity path. `SpawnProp` returns
`tuple(?creative_prop, spawn_prop_result)` and is not failable;
`MoveTo(Position, Rotation, Seconds)<suspends>` glides it:

```verse
SpawnAndDeliver(Agent : agent)<suspends> : void =
    if (Prop := SpawnProp(PropAsset, StartTransform)(0)?):
        defer:
            Prop.Dispose()                      # runs even if the task is cancelled
        Prop.MoveTo(EndPosition, IdentityRotation(), TravelSeconds)
        if (GamePlayer := PlayerManager.GetGamePlayer(Agent)?):
            GamePlayer.Services.EconomyManager.AddCurrency("Coins", Payout)
```

- Pool props the same way as entities (hide, move away, reuse) when they spawn
  often; `Dispose` every prop you spawn or it leaks.
- A pre-placed `@editable creative_prop` moved along nav points: `MoveTo` to each
  point in turn (the call waits for the glide), `break` at the end or on death.

### Gotchas

- Every spawn loop waits and stops with its owner (round, player, device) —
  `async`.
- Prune dead entries from arrays and maps each wave with a for-expression.
- Confirm prefab class names in Assets.digest and spawner events in the digest
  (`devices` "What each event sends") — never guess.
