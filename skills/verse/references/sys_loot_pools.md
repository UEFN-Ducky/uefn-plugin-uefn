---
description: "Loot pools — /UnrealEngine.com/LootPools + /Fortnite.com/LootPools: weighted loot tables that return item entities (weighted_loot_pool, weighted_loot_entry_item, weighted_loot_entry_pool for nested tables, MaxSelectionCount), how many items per roll (loot_roll_calculator_fixed), weights that depend on who opens it (loot_weight_calculator), Fortnite's own chest / rare chest / ammo box / supply drop / food box loot (fort_loot_pool_*), lootable_component / basic_lootable_component on an entity, and a compiled chest-button device"
metadata:
  order: 14
  label: "Loot pools (weighted loot tables)"
  default_enabled: false
  load_condition: "Loot tables, loot pools, drop chances, weighted or rare drops, chests that give random items, enemies that drop loot, loot boxes, supply drops, fishing rewards, random item rewards, LootPools, loot_pool, weighted_loot_pool, SelectLoot, fort_loot_pool_chest"
---

## Loot pools — weighted loot tables

A loot pool picks **item entities** by weight. You ask it for loot, it returns new entities,
you add them to the scene. Never build a random item picker by hand or with Item Granter
devices when a pool does it.

> Read the API from the digest before you write: `get_verse_api("weighted_loot_pool")`,
> `get_verse_api("loot_context")`. An `@experimental` line above a name in the digest means
> islands that use it cannot be published yet; if that line is gone, they can.

```verse
using { /Fortnite.com/Devices }
using { /Fortnite.com/Characters }
using { /Fortnite.com/LootPools }        # fort_loot_pool_chest and the other Fortnite pools
using { /UnrealEngine.com/LootPools }    # loot_pool, weighted_loot_pool, entries, calculators
using { /Verse.org/Simulation }
using { /Verse.org/SceneGraph }
```

### The parts

| Type | What it is |
|------|------------|
| `loot_pool` | Base class. `SelectLoot[Context]` returns `[]entity`; fails when it cannot pick. |
| `weighted_loot_pool` | Picks from `Options` by weight. `RollCalculator` = how many picks per call (default 1). |
| `weighted_loot_entry_item` | One option: `EntityType` (an item or any entity class) is created when picked. |
| `weighted_loot_entry_pool` | One option that rolls another `Pool` (nested tables). |
| `WeightCalculator` | On every entry. `loot_weight_calculator_fixed{Weight := 10.0}`; default weight is 1.0. Weight 0.0 or less is never picked. |
| `MaxSelectionCount` | On every entry: `option{1}` = at most once per call; `false` = no limit. |
| `loot_roll_calculator_fixed{Rolls := 3}` | Three picks per call. |
| `loot_context{Instigator := option{Entity}}` | Who the loot is for. Calculators receive it. |
| `fort_loot_pool_chest`, `fort_loot_pool_chest_rare`, `fort_loot_pool_ammo_box`, `fort_loot_pool_ammo_box_rare`, `fort_loot_pool_supply_drop`, `fort_loot_pool_food_box` | Fortnite's own loot. Use alone or as an entry in your table. |
| `basic_lootable_component` | Put on an entity; set `SourceLootPools` in the Details panel; call `SelectLoot[option{Entity}]`. |

Weights are relative. If they add up to 100 they read as percentages (10 / 50 / 40).

### A button that gives loot (compiled)

Each row of `Options` is filled in the Details panel: pick the item entity type and its weight.

```verse
# One row of the loot table.
loot_option := class<concrete>:
    @editable
    ItemType : castable_concrete_subtype(entity) = entity

    @editable
    Weight : type{_X : float where 0.0 <= _X, _X <= Inf} = 1.0

loot_button_device := class(creative_device):

    @editable
    RollButton : button_device = button_device{}

    @editable
    Options : []loot_option = array{}

    # Items handed out per press.
    @editable
    Rolls : type{_X : int where 0 <= _X} = 1

    var Pool : loot_pool = weighted_loot_pool{}

    OnBegin<override>()<suspends> : void =
        Entries := for (Option : Options):
            weighted_loot_entry_item:
                EntityType := Option.ItemType
                WeightCalculator := loot_weight_calculator_fixed{Weight := Option.Weight}
        set Pool = weighted_loot_pool:
            RollCalculator := loot_roll_calculator_fixed{Rolls := Rolls}
            Options := Entries
        RollButton.InteractedWithEvent.Subscribe(OnRoll)

    OnRoll(Agent : agent) : void =
        if:
            Character := Agent.GetFortCharacter[]
            Holder := Character.GetEntity[]
            Sim := Holder.GetSimulationEntity[]
            Loot := Pool.SelectLoot[loot_context{Instigator := option{Holder}}]
        then:
            Sim.AddEntities(Loot)                       # loot is not in the world until added
            for (Item : Loot):
                Item.SetGlobalTransform(Holder.GetGlobalTransform())
```

`Weight` and `Rolls` use the same number types as the calculators' fields; a plain `float`
or `int` field does not fit them.

### Nested tables, once-per-drop rewards, Fortnite loot

```verse
MakeNestedPool(Common : []weighted_loot_entry, Rare : []weighted_loot_entry) : loot_pool =
    weighted_loot_pool:
        Options := Common + array:
            weighted_loot_entry_pool:
                Pool := weighted_loot_pool{Options := Rare}
                WeightCalculator := loot_weight_calculator_fixed{Weight := 5.0}
                MaxSelectionCount := option{1}          # at most one rare roll per call
            weighted_loot_entry_pool:
                Pool := fort_loot_pool_chest{}          # Fortnite's chest loot as one option
```

### Loot that depends on who opens it

Subclass the calculator; `GetWeight` runs once per `SelectLoot` call.

```verse
vip_weight := class(loot_weight_calculator):
    Vips : []entity = array{}
    GetWeight<override>(Context : loot_context)<transacts> : float =
        if (Who := Context.Instigator?, Vips.Find[Who]):
            10.0
        else:
            1.0
```

`loot_roll_calculator` works the same way with `GetRollCount`.

### Rules

- `SelectLoot[...]` is failable: call it with square brackets inside `if`.
- The returned entities exist but are **not in the scene**: `AddEntities` them, then place them.
- A weighted pool with no `Options` fails. An entry whose loot cannot be made adds nothing but still uses a roll.
- Custom items and weapons are entities too: put their prefab class in `EntityType`. → scenegraph `custom_items`, `custom_weapons`.
- Our inventory and economy packs stay the owner of what a player holds; a pool only decides **what drops**.
