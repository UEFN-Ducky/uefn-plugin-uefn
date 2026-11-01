---
description: "Character damage, healing, health/shield and elimination in Verse — the healthful / damageable / healable / shieldable interfaces on fort_character, DamagedEvent/HealedEvent/EliminatedEvent payloads, who-hit-whom, self-damage filter, shield-or-health hit race, stasis freeze, respawn via player_spawner_device"
metadata:
  order: 12
  label: "Damage, health, shields & elimination"
  default_enabled: false
  load_condition: "Applying or reacting to damage/healing, reading or setting health/shield, detecting eliminations and the eliminator, freezing players (stasis), or respawning players"
---

## Damage, health, shields & elimination

> **Snippets here are fragments.** The `using` block in this file's first code
> block applies to all of them — copy those imports (or start from the matching
> `verse_template_apply` pack) when pasting into a real `.verse` file.

> **43.00:** custom health pools, per-hit rules, damage types and **damage on Scene Graph
> entities and props** (weapons hit them) live in the new health and damage pipeline:
> `sys_health_pipeline`. It is Experimental (blocks publishing). This page's
> `fort_character` API stays the publishable path for player health and eliminations.

`fort_character` is an **interface** that composes the gameplay interfaces below
(digest: `fort_character := interface<unique>(positional, healable, healthful,
damageable, shieldable, game_action_instigator, game_action_causer)`). Get one
from an agent with `Agent.GetFortCharacter[]` (`<transacts><decides>`), inside a
failure context.

```verse
using { /Fortnite.com/Characters }
using { /Fortnite.com/Devices }
using { /Fortnite.com/Playspaces }
using { /Verse.org/Simulation }
using { /Fortnite.com/Game }
```

### The API (digest-verified)

| Interface | Members | Effects |
|-----------|---------|---------|
| `healthful` | `GetHealth()`, `SetHealth(Health : float)`, `GetMaxHealth()`, `SetMaxHealth(MaxHealth : float)` | all `<transacts>` |
| `shieldable` | `GetShield()`, `SetShield(Shield : float)`, `GetMaxShield()`, `SetMaxShield(MaxShield : float)`, `DamagedShieldEvent()`, `HealedShieldEvent()` | getters/setters `<transacts>`; events are `()` methods |
| `damageable` | `Damage(Amount : float)`, `Damage(Args : damage_args)`, `DamagedEvent() : listenable(damage_result)` | `Damage` has **no effect specifier** → call it in straight-line code, never in an `if` head |
| `healable` | `Heal(Amount : float)`, `Heal(Args : healing_args)`, `HealedEvent() : listenable(healing_result)` | same as `Damage` |
| `fort_character` | `EliminatedEvent() : listenable(elimination_result)`, `IsActive[]`, `GetAgent[]`, `PutInStasis(Args)`, `ReleaseFromStasis()`, `Hide()`, `Show()`, `TeleportTo[…]` | events are `()` methods |

Payload structs (all fields plain reads):

- `damage_result` / `healing_result`: `Target`, `Amount : float`,
  `Instigator : ?game_action_instigator`, `Source : ?game_action_causer`.
- `damage_args` / `healing_args`: `Amount : float`, optional `Instigator`, `Source`.
- `elimination_result`: `EliminatedCharacter : fort_character`,
  `EliminatingCharacter : ?fort_character` (`false` for environmental deaths).

The events on `fort_character` are **methods**: `FC.DamagedEvent().Subscribe(…)`,
not `FC.DamagedEvent.Subscribe(…)`.

### Apply damage / heal / set health

```verse
HitPlayer(Agent : agent, Amount : float) : void =
    if (FC := Agent.GetFortCharacter[]):
        FC.Damage(Amount)                       # straight-line: Damage is no_rollback

HealToFull(Agent : agent) : void =
    if (FC := Agent.GetFortCharacter[]):
        FC.SetHealth(FC.GetMaxHealth())         # both <transacts>
        FC.SetShield(FC.GetMaxShield())

# Attributed damage: the victim's DamagedEvent will report who did it.
HitWithAttribution(Victim : agent, Attacker : agent, Amount : float) : void =
    if (VictimFC := Victim.GetFortCharacter[], AttackerFC := Attacker.GetFortCharacter[]):
        VictimFC.Damage(damage_args{Amount := Amount, Instigator := option{AttackerFC}})
```

### React to damage and read who hit whom

Subscribe once per character (on join), keep the `cancelable`, and cancel on
leave — every `.Subscribe` returns one.

```verse
using { /Fortnite.com/Devices }
using { /Fortnite.com/Characters }
damage_tracker_device := class(creative_device):
    var Subs <private> : [agent][]cancelable = map{}

    OnBegin<override>()<suspends> : void =
        Playspace := GetPlayspace()
        for (Player : Playspace.GetPlayers()):
            Watch(Player)
        Playspace.PlayerAddedEvent().Subscribe(Watch)
        Playspace.PlayerRemovedEvent().Subscribe(Unwatch)

    Watch(Player : player) : void =
        if (FC := Player.GetFortCharacter[]):
            DamageSub := FC.DamagedEvent().Subscribe(OnDamaged)
            ElimSub := FC.EliminatedEvent().Subscribe(OnEliminated)
            if (set Subs[Player] = array{DamageSub, ElimSub}) {}

    Unwatch(Player : player) : void =
        if (List := Subs[Player]):
            for (Sub : List):
                Sub.Cancel()
        var Next : [agent][]cancelable = map{}
        for (K -> V : Subs, K <> Player):
            if (set Next[K] = V) {}
        set Subs = Next

    OnDamaged(Result : damage_result) : void =
        # Instigator is ?game_action_instigator; fort_character implements it, so cast.
        if (Inst := Result.Instigator?, AttackerFC := fort_character[Inst], Attacker := AttackerFC.GetAgent[]):
            Print("hit for {Result.Amount} by an agent")
        else:
            Print("hit for {Result.Amount} (environment)")

    OnEliminated(Result : elimination_result) : void =
        if (KillerFC := Result.EliminatingCharacter?, Killer := KillerFC.GetAgent[]):
            Print("eliminated by a character")
        else:
            Print("eliminated by the environment")
```

**Self-damage** (own rockets, falls with the player as instigator) reports the
victim as its own instigator. Ignore it before awarding anything:

```verse
OnDamaged(Result : damage_result) : void =
    if:
        VictimFC := fort_character[Result.Target]
        Inst := Result.Instigator?
        AttackerFC := fort_character[Inst]
        AttackerFC <> VictimFC                  # not self-damage
        Attacker := AttackerFC.GetAgent[]
    then:
        AwardHit(Attacker, Result.Amount)
```

**Any hit, shield or health.** Damage that only removes shield fires
`DamagedShieldEvent`, not `DamagedEvent`. To wait for "was hit at all", race both
(both send `damage_result`):

```verse
WaitForHit(FC : fort_character)<suspends> : damage_result =
    race:
        FC.DamagedEvent().Await()
        FC.DamagedShieldEvent().Await()
```

**Stop on elimination.** A per-player effect (burning, a countdown, a carried
item) races `FC.EliminatedEvent().Await()` so it ends when the player goes down,
plus the leave signal (`async`, stop events).

`player_manager` (Player Core template) already fans `EliminatedEvent` out as
`elimination_event(EliminatedPlayer : agent, EliminatingPlayer : ?agent)`; use
`SubscribeElimination` there instead of re-subscribing per system.

### Respawn

Players respawn through placed `player_spawner_device`s. `SpawnedEvent` carries
the **agent** (not `player`):

```verse
using { /Fortnite.com/Characters }
@editable Spawners : []player_spawner_device = array{}

OnBegin<override>()<suspends> : void =
    for (Spawner : Spawners):
        Spawner.SpawnedEvent.Subscribe(OnSpawned)     # event field, payload agent

OnSpawned(NewAgent : agent) : void =
    if (FC := NewAgent.GetFortCharacter[]):
        FC.SetMaxHealth(150.0)
        FC.SetHealth(150.0)
```

To force a respawn from Verse, eliminate the character (`FC.Damage(FC.GetHealth())`)
and let the spawner rules place them again; `TeleportTo[]` moves a live character
without a respawn.

### Freeze a player (stasis)

```verse
FreezeFor(Agent : agent, Seconds : float)<suspends> : void =
    if (FC := Agent.GetFortCharacter[]):
        FC.PutInStasis(stasis_args{AllowTurning := true, AllowFalling := false, AllowEmotes := false})
        defer:
            FC.ReleaseFromStasis()          # runs even if the task is cancelled
        Sleep(Seconds)
```

`PutInStasis` / `ReleaseFromStasis` are `<transacts>`. Release in `defer` so a
cancelled or raced task never leaves the player frozen.

### Gotchas

- `Damage` / `Heal` have no effect specifier: never inside `if (…)` heads or a
  `<transacts>` helper — call them from a handler or `<suspends>` body.
- `GetFortCharacter[]` fails for players not yet spawned; guard every use.
- Health values are floats (`100.0`), and `SetHealth` clamps to max — call
  `SetMaxHealth` first when raising both.
- There is no `SetVulnerability` on `fort_character` in this digest; use a
  `mutator_zone_device` or Island Settings for invulnerability.
