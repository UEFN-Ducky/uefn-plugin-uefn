---
description: "Health and damage pipeline (43.00, Experimental — blocks publishing) — /UnrealEngine.com/HealthPipeline + /Fortnite.com/FortHealthPipeline: health_component on any Scene Graph entity, custom health pools (health_pool_entry + health_pool_tag), Fortnite pools fort_health / fort_shield / fort_overshield, per-hit rules with health_adjustment_modifier stacks (event / pool / component layers), damage types (damage_tag subclasses), dealing damage or healing from Verse with damage_event / healing_event + SendUp, who hit me (OnReceive), OnDamaged / OnHealed / OnDied, a compiled destructible prop, the known issues, and when to use the classic fort_character damage API instead"
metadata:
  order: 13
  label: "Health & damage pipeline (43.00, Experimental)"
  default_enabled: false
  load_condition: "Destructible props or objects that take weapon damage, custom health pools / armor / barriers / stacking shields, damage types with resistances or immunities, damage over time, lifesteal, damage amplification, damaging or healing Scene Graph entities, health_component, damage_event, HealthPipeline, FortHealthPipeline"
---

## Health & damage pipeline (43.00)

> **Experimental — islands that use it can't be published yet.** Every name warns 2304
> "… is experimental, and its use will prevent you from publishing your project". It
> becomes publishable when it leaves Experimental. For a publishable island, use the classic
> `fort_character` API (`sys_damage_health`).

What it gives you: your own health pools instead of working around Overshield / Shield /
Health; your own rules on every hit; damage and healing for **anything in the scene**, not
just players. Fortnite characters use the same pipeline, so most Fortnite weapons, abilities
and explosions follow your rules. Built-in weapon damage now hits Scene Graph entities, and
damage you deal from Verse behaves like built-in damage. All names below are from the 43.00
digests. The destructible prop compiled with 0 errors in UEFN 43.00 (Nov 1 2026).

```verse
using { /UnrealEngine.com/HealthPipeline }     # your entities: components, pools, events, modifiers
using { /Fortnite.com/FortHealthPipeline }     # Fortnite pools: fort_health / fort_shield / fort_overshield
```

### The pieces

| Piece | What it is |
|-------|-----------|
| `health_component` | `class<final_super>(component)` on any entity. Ordered `HealthPools`; `GetHealthPools()`, `GetHealthPool[PoolTagType]`, `AddHealthPool(P)`, `RemoveHealthPool(P)`; `DamageModifiers` / `HealingModifiers`; `OnDamaged` / `OnHealed : listenable(health_adjustment_result)`, `OnDied : listenable(tuple())`; `IsAlive[]` |
| `health_pool_entry{MaxValue, CurrentValue, Tag}` | One pool. `Tag` is its identity (an instance of your `health_pool_tag` subclass), fixed at setup. Its own `DamageModifiers` / `HealingModifiers`; override `CanProcessAdjustment` to make it refuse some entries ("shields refuse penetrating") |
| `fort_health{}` / `fort_shield{}` / `fort_overshield{}` | Fortnite pool presets (tags `fort_health_tag`, `fort_shield_tag`, `fort_overshield_tag`) |
| `health_pool_tag` / `damage_tag` / `healing_tag` | Subclass with `class(health_pool_tag){}` for a pool identity, `class(damage_tag){}` for a damage type (fire, poison, penetrating) |
| `damage_event` / `healing_event` | Scene events you build and deliver with `Target.SendUp(Event)`: `Context := health_adjustment_context{Instigator, Contributors}`, `Entries := array{health_adjustment_entry{HealthDelta, Categories}}`, optional `Modifiers`; after sending, `Event.Result:?health_adjustment_result` |
| `health_adjustment_result` | `Results:[]health_adjustment_result_entry{HealthDelta, PoolTag, Categories}` per pool touched, `Excess:[]health_adjustment_entry` that no pool absorbed |
| `health_adjustment_modifier` | Your per-hit rule: override `Evaluate(InValue:health_adjustment_entry)<reads>:health_adjustment_entry` and return a new entry; `Context`, `Target`, `Pool` describe the hit being evaluated |

**How a hit is processed** (digest docs): pools in order; for each pool and entry, three
modifier **layers** each fold to one factor — the event's `Modifiers`, the pool's stack,
the component's stack — and the factors **multiply**. A factor of `0` from any layer nullifies
the entry (immunity), a negative one flips damage into healing. The pool absorbs what it can;
the rest unwinds and continues to the next pool; what's left lands in `Result.Excess`.
Example: 70 damage against a 50-point shield with a 2× pool rule and a 3× event rule →
420 applied, the shield absorbs 50, 370 unwinds to about 61.7 for the next pool.

### Example — destructible prop (compiled, 43.00)

Put `destructible_component` on an entity with a `mesh_component`. Weapons, explosions and
`DealFire` all damage it, non-fire hits are halved, and it disappears at 0.

```verse
using { /Verse.org/Simulation }
using { /Verse.org/SceneGraph }
using { /UnrealEngine.com/HealthPipeline }
using { /Fortnite.com/FortHealthPipeline }

crate_hp_tag := class(health_pool_tag){}     # identity of our own pool
fire_tag := class(damage_tag){}               # a damage type

# Per-hit rule: halve every hit except fire.
armor_modifier := class(health_adjustment_modifier):
    Evaluate<override>(InValue:health_adjustment_entry)<reads>:health_adjustment_entry =
        Fire := for (C : InValue.Categories, fire_tag[C]) { C }
        if (Fire.Length > 0):
            InValue
        else:
            health_adjustment_entry{HealthDelta := InValue.HealthDelta * 0.5, Categories := InValue.Categories}

# Add to an entity with a mesh; weapons, explosions and Verse damage break it.
destructible_component<public> := class<final_super>(component):
    @editable MaxHealth:float = 150.0
    var LastAttacker:?agent = false

    OnBeginSimulation<override>():void =
        (super:)OnBeginSimulation()
        Health := GetOrAddHealth()
        if (Health.GetHealthPools().Length = 0):
            Health.AddHealthPool(health_pool_entry{MaxValue := MaxHealth, CurrentValue := MaxHealth, Tag := crate_hp_tag{}})
        Health.DamageModifiers.AddModifier(armor_modifier{}, Health.DamageModifiers.LastPosition)
        Health.OnDamaged.Subscribe(OnDamaged)
        Health.OnDied.Subscribe(OnDied)

    GetOrAddHealth():health_component =
        if (Existing := Entity.GetComponent[health_component]):
            Existing
        else:
            New := health_component{Entity := Entity}
            Entity.AddComponents(array{New})
            New

    # See who hit us; return false so the health_component still processes the hit.
    OnReceive<override>(SceneEvent:scene_event):logic =
        if (Damage := damage_event[SceneEvent], Agent := Damage.Context.Instigator?.GetComponent[possessable_component].Agent?):
            set LastAttacker = option{Agent}
        false

    OnDamaged(Result:health_adjustment_result):void =
        for (R : Result.Results):
            Print("crate took {R.HealthDelta}")

    OnDied():void =
        Entity.RemoveFromParent()

# Deal fire damage from Verse; same path as weapon damage. SendUp is no_rollback.
DealFire(Target:entity, Amount:float, Instigator:?entity):?health_adjustment_result =
    Event := damage_event:
        Context := health_adjustment_context{Instigator := Instigator}
        Entries := array{health_adjustment_entry{HealthDelta := Amount, Categories := array{fire_tag{}}}}
    Target.SendUp(Event)
    Event.Result

# Read a Fortnite pool on anything that has one.
ReadShield(Target:entity)<decides><transacts>:float =
    Health := Target.GetComponent[health_component]
    Health.GetHealthPool[fort_shield_tag].CurrentValue
```

- The `health_component` can also be added in the editor (`+ Component` → Health), with pools
  set in Details. The code above keeps those and only adds a pool when there is none.
- Fortnite-style stack instead of a custom pool:
  `AddHealthPool(fort_shield{MaxValue := 50.0, CurrentValue := 50.0})`, then `fort_health{…}`.
  Pools take damage **in the order added**.
- `OnReceive` sees the `damage_event` before the `health_component` processes it. Return
  **`false`** or the hit is consumed and never damages the entity.
- A tutorial-style wobble on hit: `keyframed_movement_component` + `oneshot_keyframed_movement_playback_mode{}`
  from an `OnDamaged.Await()` loop (scenegraph `movement_transforms`).

### Recipes

| Build | How |
|-------|-----|
| Armor / barrier | A pool with its own `Tag`, added **before** health; `CanProcessAdjustment` refuses entries it shouldn't block |
| Damage types, resistances, immunities | Tag entries (`Categories := array{fire_tag{}}`); a pool or component modifier returns `HealthDelta * 0.5` (resist) or `0.0` (immune) for that tag |
| Damage over time | A `<suspends>` loop that sends small `damage_event`s every 0.5 s and races a stop event (`async`) |
| Lifesteal | In `OnDamaged`, sum `Result.Results` deltas and send a `healing_event` to the instigator's entity |
| Damage amplification | An event-layer modifier: set `Event.Modifiers` on the sender's `damage_event` (a "berserk" buff) |

### Traps

- **`SendUp` is `no_rollback`.** A `<transacts>` / `<decides>` sender, or a send inside `if (…)`,
  is error 3512. Use a plain function and call it on its own line.
- **Experimental:** keep pipeline code in its own folder so you can strip it before publishing.
- A zero-delta entry produces **no result entry** (known issue below). Don't count on
  `Results.Length` for a zero hit.
- The offline LSP flags `Health.OnDamaged.Await()` / `OnDied.Await()` as "Unknown member
  `Await`"; the build accepts it (`compile_errors`).

### Known issues (43.00 release notes)

- Rockets ricochet off entities without dealing direct-hit damage.
- Weapons that fire lightweight projectiles (for example Ares' Modular Warforged Assault
  Rifle) don't damage entities.
- Non-ballistic weapons that don't damage entities: Arc-Lightning Gun, Flare Gun, Primal Flame
  Bow, Primal Stink Bow, Pumpkin Launcher, Ripsaw Launcher.
- Lingering area damage (fire, gas) applies once on entry, not continuously.
- Physics object collisions don't damage entities.
- Fortnite healing items (Slurp Bazooka, Chill Bronco) can't heal entities.
- Hit impact effects are inconsistent on entities.
- Team, friendly-fire and self filtering don't apply to entities. Filter in your own modifier
  or `OnReceive`.
- A health adjustment entry with a zero delta produces no result entry.
- Abilities with a wedge target query don't find Scene Graph entities without an actor, so wedge
  abilities don't damage them (fixed in 43.10).

### This page or the classic one?

| Need | Use |
|------|-----|
| Publish now; players only; read or set health and shield; who eliminated whom | `sys_damage_health` (`fort_character` `Damage`, `SetHealth`, `DamagedEvent`, `EliminatedEvent`) |
| Props or entities that take weapon damage, custom pools, per-hit rules, damage types | this page (Experimental) |
