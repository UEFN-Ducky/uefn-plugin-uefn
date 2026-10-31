---
description: "Reusable Verse design patterns mapped to our architecture — player registry and per-player data, cross-system links (?option slots, Subscribe hooks), per-player slot index, object and entity pools, stop events for per-player loops, interfaces as mixins, generic containers, prefab registries, phase machines — each with 'use ours' where a pack already does it"
metadata:
  order: 8
  label: "Design patterns — modular systems on our packs"
  default_enabled: false
  load_condition: "Designing how systems talk to each other, giving each player their own slot/lane/plot/seat, pooling objects or entities, stopping per-player loops, sharing behaviour across classes, or adapting a pattern from a tutorial to our player_manager architecture"
---

## Design patterns — modular systems on our packs

Every pattern here keeps systems separate: a system owns its folder and state,
talks to others only through `player_manager` slots, hooks and events, and can be
removed without breaking the rest. Tutorials often solve the same problems with a
global or a copy of the player list; use ours instead.

| Need | Use ours | Not |
|------|----------|-----|
| Per-player data and join/leave | `player_manager` + `game_player` (`sys_architecture`, `sys_player_data`) | a `[agent]my_player` map in every device; a session `weak_map` global with a dummy fallback; joining only through tagged spawn pads |
| One system using another (currency, XP, playtime) | `?option` provider slots: `if (Wallet := PlayerManager.GetCurrencyProvider()?):` | importing the other pack's internals; a mode-local copy |
| Reacting to join / leave / elimination | `SubscribePlayerConnected`, `SubscribePlayerRemoved`, `SubscribeElimination` | each device subscribing to the playspace itself |
| A lane, plot, seat, camera or HUD per player | `PlayerManager.GetPlayerSlot[Agent]` | scanning for "a free one" in every system |
| Reusing short-lived objects | pools (below) | spawn and dispose in bursts |
| A loop that belongs to one player | stop event raced inside the loop (`async`) | a spawned loop nobody can stop |
| Behaviour shared by unrelated classes | an interface (`classes`) | copying the code into each class |
| WeaponId / item id → prefab | one registry file (`sys_owned_weapons`) | prefab names scattered across systems |
| Game phases | phase functions chained by events (`sys_rounds_timers`) | flags checked in a tick loop |

### Per-player slot index

`player_manager` gives every player the lowest free slot number (0, 1, 2, …) on
join and frees it on leave. Systems keep **arrays of devices** and index them by
slot instead of each running their own allocation:

```verse
using { /Fortnite.com/Devices }
using { /Verse.org/Simulation }

@editable PlayerManager : player_manager = player_manager{}
@editable Teleporters : []teleporter_device = array{}       # one per slot, in order

SendToLane(Agent : agent) : void =
    if:
        Slot := PlayerManager.GetPlayerSlot[Agent]
        Teleporter := Teleporters[Slot]
    then:
        Teleporter.Teleport(Agent)
```

Size device arrays to Island Settings `MaxPlayers`. A system that needs its own
slot space (a 4-seat minigame inside a 16-player island) keeps an `[agent]int`
allocated lowest-free from its own seats and freed when the player leaves the
minigame — never resets shared state when one player starts (`runtime_pitfalls`).

### Pools

**Entities** (effects, debris, projectiles, streamed pieces): build the pool once,
hide on expiry, re-show and move on reuse, remove only on teardown
(`runtime_pitfalls` §4, scenegraph `movement_transforms`).

**Any object** (devices, widgets, prefab instances): a generic pool marks each entry
taken or free. Generic classes go in a Content-level folder that sorts first,
helpers below them (`classes`, 3502).

```verse
# Content/Archetypes/pool.verse
pooled_obj<public>(t : type) := class:
    Obj<public> : t
    Index<public> : int
    var Available<public> : logic = true

pool<public>(t : type) := class:
    Objects<public> : []pooled_obj(t) = array{}

    # First free entry, marked taken. Fails when none is free.
    Fetch<public>()<transacts><decides> : pooled_obj(t) =
        Free := for (Candidate : Objects, Candidate.Available?) do Candidate   # not `Entry`: a name is never reused (3532)
        Entry := Free[0]
        set Entry.Available = false
        Entry

    Release<public>(Entry : pooled_obj(t)) : void =
        set Entry.Available = true

GeneratePool<public>(Items : []t where t : type)<transacts> : pool(t) =
    pool(t){Objects := for (I -> Item : Items) do pooled_obj(t){Obj := Item, Index := I}}
```

Release every fetched entry on the owner's leave or elimination, or the pool
drains.

### Interfaces as mixins

A class has one parent but any number of interfaces, so behaviour that cuts across
families lives in an interface: `clickable`, `sizable`, `stoppable`. Scene Graph
components must inherit `component`, so an interface is how a component gets
shared behaviour. Qualify clashing names with `(iface:)`. → `classes`

### Generic containers

A data structure used with several types (scoreboard, pool, ring buffer) is a
generic class: `scoreboard(key_type : subtype(comparable), score_type : type) :=
class`. Keep it in the folder that sorts first, helpers below (`classes`, 3502).

### Callbacks and wrappers

Pass behaviour as a function value instead of a `case` over every caller:
comparators for sorting, `Subscribe*` hooks, wrappers that give different setters
one shape. → `functions`
