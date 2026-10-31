---
description: "Owned custom firearms — persist on the shared player table, one WeaponId → prefab registry, public prefab folder (E3593), fresh grant + parent/equip, collectible_object_device pickup, canvas shop, rejoin, no Save Point; one sequence"
metadata:
  order: 33
  label: "Game systems — owned custom weapons (persist + collectible + canvas shop)"
  default_enabled: false
  load_condition: "Custom player weapons that save, load on join, collect via collectible_object_device, canvas-shop, upgrade, restore on rejoin, or pick up a collectible and shoot; constructing EP_* from another Verse folder (Script error 3593); Save Point device with custom weapons"
---

## Owned custom weapons — one loop

Prefab authoring (template, mesh, pivot, `fort_trace_weapon_component` ranges):
`skill_read_subskill("scenegraph", "custom_weapons")`. Do not re-author the gun
here. **This file is the save → registry → grant loop** — copy the Verse below.

Canvas chrome: `sys_canvas_cookbook` + `sys_custom_buttons` + `sys_ui_menus`
(`.All`). Wallet spend: `sys_economy`. Persist store: `persistence`.

Soft `ItemId` bags → `sys_inventory`. Stock Fortnite guns → `itemization`.
Non-weapon items → `custom_items`.

### Three layers (do not mix)

| Layer | What it is | Survives leave? |
|-------|------------|-----------------|
| **Catalog** | Designer `WeaponId`, cost, upgrade tracks, which Armory prefab | Asset |
| **Persist** | Owned / Unlocked / `UpgradeLevels` / Equipped, nested on the **one** player `weak_map` | Yes |
| **Session hotbar** | Armory entity on `inventory_component` | **No** — re-grant |

Wallet is another nest on that **same** table. Island cap is **4 persist
`weak_map`s**. Never a second player map for guns. Session scores are session
maps, not persist.

`WeaponId` is the persist key. The prefab is looked up from it in **one**
registry (below); several ids may share one prefab.

Island Settings **must** have BR-style inventory
(`ItemizationConfiguration_BRStyle` —
`skill_read_subskill("islandsettings", "recipes")`) or grant can succeed and
the hotbar stays empty.

### Persist (ADD-ONLY)

```verse
owned_weapon_entry <public> := class<final><persistable>:
    WeaponId <public> : string = ""
    Owned <public> : logic = false
    UpgradeLevels <public> : []int = array{}
    Equipped <public> : logic = false

player_weapon_table <public> := class<final><persistable>:
    Version <public> : int = 1
    UnlockedWeaponIds <public> : []string = array{}
    OwnedWeapons <public> : []owned_weapon_entry = array{}
```

Nest `PlayerWeapons` on the shared player table. Every `Update*` copies **every**
sibling field (`sys_persistence_migration`). Rebuild+`set`. Never mutate in
place; never remove player keys.

`Unlocked` = shop can show Buy. `Owned` = player has it. Both live on this nest.

Persist **ownership**, never the held entity. The gun in the hands is rebuilt
from persist every session — upgrade levels and skins included — so a save
never depends on what the inventory happens to hold when the player leaves.

Persist and grant are **separate**. Persist is for rejoin / shop. Grant is the
gun in the hands. **Never skip grant because a persist `set` failed.**

### Reach the prefab from any folder (HARD)

After a Verse build the prefab is a class in Assets.digest, scoped to the whole
island:

```verse
# Assets.digest (read only) — Content/Verse/ArmoryWeapons/EP_Weapon_Pistol
EP_Weapon_Pistol<scoped {/you@fortnite.com/YourIsland}> := class<final><concrete>(entity):
```

The class is usable anywhere, but Assets.digest generates the **asset folder
modules around it** with no access specifier (`ArmoryWeapons := module:`).
Verse in another folder gets **Script error 3593** until each folder on the
prefab's path is declared `<public>` from your code, in a file of the folder
**that contains it** (`modules`):

```verse
# Content/Verse/module_declarations.verse — prefabs in Content/Verse/ArmoryWeapons/
ArmoryWeapons<public> := module:
```

```verse
# Content/modules.verse — prefabs in Content/SceneGraph/CustomWeapons/
SceneGraph<public> := module:
    CustomWeapons<public> := module:
```

Then any folder can `using { ArmoryWeapons }` (or write
`SceneGraph.CustomWeapons.EP_CustomAR`) and construct `EP_Weapon_Pistol{}` —
shop, HUD, pickup and rejoin code no longer have to sit next to the prefabs.
Never put the declaration inside the prefab folder itself (that declares
`ArmoryWeapons.ArmoryWeapons`). Build Verse after creating or renaming a prefab,
then `search_verse_digest("EP_")` for the exact class and path.

### One registry: WeaponId → prefab

One file names every prefab. Everything else asks it.

```verse
using { /Verse.org/SceneGraph }
using { /Verse.org/Simulation }
using { /UnrealEngine.com/Itemization }
using { ArmoryWeapons }

armory_weapon_class <public> := enum:
    Pistol
    AssaultRifle
    Shotgun
    SMG
    # WeaponId with no prefab yet (typo, or added before its prefab exists).
    None

# The only WeaponId → prefab-family mapping. Add a weapon here only.
ArmoryClassOf<public>(WeaponId : string)<transacts> : armory_weapon_class =
    if (WeaponId = "service_pistol" or WeaponId = "hand_cannon"):
        return armory_weapon_class.Pistol
    if (WeaponId = "vanguard"):
        return armory_weapon_class.AssaultRifle
    if (WeaponId = "breacher"):
        return armory_weapon_class.Shotgun
    if (WeaponId = "shred"):
        return armory_weapon_class.SMG
    armory_weapon_class.None

# A FRESH prefab instance per grant. Constructing is no_rollback: never call
# this inside an if condition — bind the result first.
MakeArmoryClassEntity<public>(Class : armory_weapon_class) : ?entity =
    case (Class):
        armory_weapon_class.Pistol => option{EP_Weapon_Pistol{}}
        armory_weapon_class.AssaultRifle => option{EP_Weapon_AssaultRifle{}}
        armory_weapon_class.Shotgun => option{EP_Weapon_Shotgun{}}
        armory_weapon_class.SMG => option{EP_Weapon_SMG{}}
        armory_weapon_class.None => false

MakeOwnedArmoryGun<public>(WeaponId : string) : ?entity =
    MakeArmoryClassEntity(ArmoryClassOf(WeaponId))

# Is this held entity one of that weapon's prefab family? By type — no tags.
IsArmoryClassEntity<public>(Item : entity, Class : armory_weapon_class)<transacts> : logic =
    case (Class):
        armory_weapon_class.Pistol => if (EP_Weapon_Pistol[Item]) then true else false
        armory_weapon_class.AssaultRifle => if (EP_Weapon_AssaultRifle[Item]) then true else false
        armory_weapon_class.Shotgun => if (EP_Weapon_Shotgun[Item]) then true else false
        armory_weapon_class.SMG => if (EP_Weapon_SMG[Item]) then true else false
        armory_weapon_class.None => false
```

Rename the `EP_Weapon_*` classes to yours from Assets.digest. A skin is a
**second prefab** (duplicate the prefab, swap the mesh material, build) with its
own registry row — Verse has no material setter for a held weapon. Add the skin
class to `IsArmoryClassEntity` too, or switching skins leaves the old one held.

### The grant (only grant — copy this)

Wait until the agent has `inventory_component` (it is on a **descendant**, not
the agent). Clear the old copy, construct a **fresh** prefab, apply saved
upgrades to it, then add. `AddItemDistribute` is **not** enough —
`AddResult.Ok` / `GetSuccess[]` can be true while the gun is still unparented
and unwieldable. Parent then Equip:

```verse
using { /Verse.org/Simulation }
using { /Fortnite.com/Devices }
using { /Fortnite.com/Armory }
using { /Fortnite.com/Itemization }
using { /UnrealEngine.com/Itemization }
using { /Verse.org/SceneGraph }

GetFirstInventory<public>(Agent : agent)<transacts><decides> : inventory_component =
    (for (Inv : Agent.FindDescendantComponents(inventory_component)) do Inv)[0]

WaitForInventory<public>(Agent : agent)<suspends> : logic =
    var Ready : logic = false
    var Tries : int = 0
    loop:
        if (GetFirstInventory[Agent]):
            set Ready = true
            break
        if (Tries >= 50):
            break
        set Tries += 1
        Sleep(0.1)
    Ready

# Remove every held copy of this weapon's family, each from the inventory
# that actually holds it (the weapon hotbar is a sub-inventory).
ClearOwnedGun<public>(Agent : agent, WeaponId : string) : void =
    Class := ArmoryClassOf(WeaponId)
    if (Inventory := GetFirstInventory[Agent]):
        # Collect first, then remove: never change an inventory while iterating it.
        ToRemove := for (Item : Inventory.FindItems(), IsArmoryClassEntity(Item, Class) = true) do Item
        for (Item : ToRemove):
            if (IC := Item.GetComponent[item_component], Parent := IC.GetParentInventory[]):
                Parent.RemoveItem(Item)

# Gun is already constructed and upgraded. Do not case AddItemDistribute.
AddOwnedGun<public>(Inventory : inventory_component, Gun : entity) : void =
    if (IC := Gun.GetComponent[item_component]):
        Inventory.AddItemDistribute(Gun)
        if (IC.GetParentInventory[]):
            IC.Equip()
            return
        if (IC.PickUp[Inventory]):
            IC.Equip()
            return
        Gun.RemoveFromParent()
    else:
        Gun.RemoveFromParent()

GrantOwnedWeapon<public>(Agent : agent, WeaponId : string)<suspends> : void =
    if (WeaponId = ""):
        return
    Ready := WaitForInventory(Agent)
    if (Ready = false):
        return
    ClearOwnedGun(Agent, WeaponId)
    # Bound at statement level: constructing a prefab is no_rollback (E3512 in an if).
    MaybeGun := MakeOwnedArmoryGun(WeaponId)
    if (Gun := MaybeGun?):
        if (Inventory := GetFirstInventory[Agent]):
            # Apply saved UpgradeLevels to Gun here (custom_weapons "Upgrades").
            AddOwnedGun(Inventory, Gun)
        else:
            Gun.RemoveFromParent()
```

Upgrades are applied to the **new** entity before `AddOwnedGun`, computed from
the prefab's authored base values — never `SetDamage` on a held gun and expect
it to save, and never re-apply to an already-upgraded gun (bonuses compound).
`fort_trace_weapon_component` ranges and the base-value rule:
`custom_weapons` → Upgrades.

`item_granter_device` and Item Spawners **cannot** hold a custom Armory prefab.
A stock WID granter is a fallback for `/Fortnite.com/Weapons` classes only —
not `EP_*`. The grant is Verse.

### Join / rejoin (load)

On join (the `player_manager` join hook, after the persist row exists): read
the player's `PlayerWeapons`, then `spawn{ GrantOwnedWeapon(Agent, Id) }` for
each entry you hand out at spawn — the `Equipped` one for a one-gun island,
every `Owned` one for a loadout island. `GrantOwnedWeapon` already waits for the
inventory, so the join hook does not.

If the island drops or clears items on elimination, re-run the same grant from
the respawn event.

### Save Point device — not for custom weapons

The Creative **Save Point** device saves and restores **stock** loadouts. It
does not restore custom Armory weapons correctly: reported on 41.00, a saved
custom AR came back as the bare template — grey, and invisible when held. Owned
custom guns load only through persist + `GrantOwnedWeapon`. If an island also
uses Save Point for stock items, test that it does not hand back a broken copy
of each custom gun next to the fresh grant; drop Save Point if it does.

### Pickup = `collectible_object_device`

The Collectible mesh is **look only**. It does **not** put an Armory gun in
inventory. Wire `@editable Collectible` and subscribe `CollectedEvent`:

```verse
using { /Fortnite.com/Devices }
weapon_collectible_pickup_device := class(creative_device):
    @editable Collectible : collectible_object_device = collectible_object_device{}

    OnBegin<override>()<suspends> : void =
        Collectible.CollectedEvent.Subscribe(OnCollected)

    OnCollected(Agent : agent) : void =
        spawn{ OwnAndGrantWeapon(Agent, WeaponIdPistol) }
```

`OwnAndGrantWeapon` = optional persist write, then **always**
`GrantOwnedWeapon`. Prefer a **typed** device per gun (hardcoded id) over a
new `@editable WeaponId` on an already-placed class — new field names may
never hash. Reuse field name `Collectible` so the existing hash wires.

Do not drag the Armory prefab into the level as loot. Do not put the
collectible in the Item Granter.

A Collectible already taken **this session** will not fire again. Test in a
**new** play session.

### Shop / upgrade / equip

1. Persist Unlock / SetOwned / IncrementUpgrade / SetEquipped (carry-all).
2. Then `GrantOwnedWeapon` — straight from the shop file, once the prefab
   folder is public (above).

Upgrade is persist int++ then a **fresh** grant, not mutate-held.

### Canvas shop

Open with `ui_input_mode.All` (`sys_ui_menus`). Layout from
`sys_canvas_cookbook`; clicks from `sys_custom_buttons`. **Read persist** to
draw rows. Mutate leaves; rebuild only when row count changes
(`sys_hud_template`).

| Mode | Persist | Click |
|------|---------|-------|
| Locked | not Unlocked | hint only |
| Buy | Unlocked, not Owned | spend wallet → SetOwned → SetEquipped → grant |
| Equip | Owned, not Equipped | SetEquipped → grant |
| Equipped | Owned and Equipped | no-op |

Upgrade buttons only if **Owned**. Spend → IncrementUpgrade → SetEquipped →
grant (same `AddOwnedGun` sequence). Stat ranges live in `custom_weapons`.

### Hard don'ts

- A second persist `weak_map` for weapons.
- Saving the held inventory (entities, counts) instead of ownership.
- Dragging the Armory prefab as pickup.
- `item_granter_device` / Item Spawner / `sys_inventory` bags as the owned-gun store.
- Save Point device as the custom-weapon save.
- Button+`GrantItem` as the weapon shop (`sys_economy` is wallet only).
- Mutating the held entity and expecting it to save.
- Gating grant on persist `set` succeeding.
- `case (AddResult)` / `GetSuccess[]` then `Equip()` with no `PickUp`.
- Skipping `WaitForInventory`.
- Calling `MakeOwnedArmoryGun` / `EP_*{}` inside an `if (…)` condition.
- Naming `EP_*` classes anywhere but the registry.
- A "pump" device next to the prefabs to grant for another folder — declare the
  prefab folder `<public>` instead.

### Failure table

| Symptom | Cause |
|---------|-------|
| Script error 3593 on `EP_*` / `using { …Weapons }` | Prefab folder module is internal — declare it `<public>` from its parent folder |
| Unknown identifier `EP_*` | Prefab created/renamed after the last Verse build, or wrong folder path — build, then `search_verse_digest("EP_")` |
| Script error 3512 at the grant | Prefab constructed inside an `if` condition — bind `MakeOwnedArmoryGun` first |
| Picked collectible, cannot shoot | Collectible is look-only; grant missing, unwired, or used `AddResult.Ok` only |
| Grant “works”, empty hotbar | No BR-style `CustomInventoryConfiguration` |
| Persist saved, no gun this session | Grant gated on persist `set` |
| Rejoin has no gun | Join hook never calls `GrantOwnedWeapon` for the saved ids |
| Two copies after a buy / upgrade / skin swap | `ClearOwnedGun` skipped, or the skin class is missing from `IsArmoryClassEntity` |
| Upgrades stack every regrant | Applied to an already-upgraded entity — fresh prefab, base values |
| Grey / invisible custom gun on load | Save Point device restored it — persist + grant only |
| Pickup never fires again | Same session — Collectible already collected |
| `WeaponId` editable will not set | New field never hashed — typed device + hardcoded id |

### Related

| Need | Load |
|------|------|
| Prefab, mesh, stat ranges, upgrades | scenegraph `custom_weapons` |
| Persist nest + carry-all | `persistence` + `sys_persistence_migration` |
| Folder modules / `module_declarations.verse` | `modules`; error codes `compile_errors` |
| Spend | `sys_economy` |
| Island hotbar config | islandsettings `recipes` |
| Canvas / buttons / `.All` | `sys_canvas_cookbook`, `sys_custom_buttons`, `sys_ui_menus` |
