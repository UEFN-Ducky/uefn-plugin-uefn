---
description: "Custom Scene Graph Armory weapons — Entity Prefab templates (AR/pistol/shotgun/SMG), fort_trace_weapon_component ranges (ShotAmmoCost 0 = no ammo), rarity, mesh/collision/pivot, skins as prefabs, upgrades from base values, and Verse grant/equip/clear/mutate/has by prefab type. Owned persist + collectible + canvas shop → verse sys_owned_weapons"
metadata:
  order: 7
  label: "Custom Armory weapons"
  default_enabled: false
  load_condition: "Creating a custom player weapon prefab, Armory assault_rifle_template / pistol / shotgun / SMG, fort_trace_weapon_component, infinite ammo / no reload, weapon rarity, weapon skins, upgrading weapon stats, granting or clearing custom guns in inventory, SetDamage/SetFireRate on custom weapons"
---

# Custom Armory weapons (Scene Graph)

Custom player firearms are **Entity Prefabs** from `/Fortnite.com/Armory`, not
hand-rolled raycasts and not stock `/Fortnite.com/Weapons` classes. The UI may
say “forge”; digests say `fort_trace_weapon_component`. Always confirm members
with `get_verse_api` / `search_verse_digest` before shipping.

## Choose the path

| Goal | Load |
|------|------|
| Stock Fortnite gun grant / pickup | `skill_read_subskill("scenegraph", "itemization")` |
| **Custom mesh + tunable AR/pistol/shotgun/SMG** | **this file** |
| Custom non-weapon item (pickup / icon / mesh) | `skill_read_subskill("scenegraph", "custom_items")` |
| Something the player **holds** that is not a gun (torch, lantern, tool) — 42.30 `held_item_template` | `skill_read_subskill("scenegraph", "held_items")` |
| Soft persist bags + Creative Item Granter | `skill_read_subskill("verse", "sys_inventory")` |
| Owned guns (persist, load on join, collectible pickup, canvas shop, rejoin) | `skill_read_subskill("verse", "sys_owned_weapons")` |
| NPC combat / projectiles | Store `npc-ai` / `sys_npc_ai` |
| Cosmetic weapon on NPC skeleton | `skill_read_subskill("animation", "npc_items")` |

This file authors the prefab and the grant API. Save / load / pickup / shop /
rejoin is **one** Verse loop: `sys_owned_weapons` — it persists **ownership**
on the player table and grants a fresh prefab each session.

## Project gates

1. **Project Settings → Beta**: **Scene Graph System** = true and **Custom
   Items in Inventory** = true (same family as custom items).
2. Optional / experimental: **Scene Graph Animation** — skeletal meshes in
   Scene Graph + Verse play API for bolt/slide motion. Same publish risk as
   other experimental Scene Graph animation — islands using it may not publish;
   prefer **static** meshes unless you need weapon animation.
3. Island **itemization inventory configuration** must be set or the hotbar
   stays empty after a successful grant — see
   `skill_read_subskill("islandsettings", "recipes")` (same gotcha as
   `itemization`).

## Author the prefab

Content Drawer → right-click → **Entity Prefab** → in the template picker
search **template** → pick one of four Armory templates. Name it with the `EP_`
prefix (`EP_CustomAR`) in **one** prefab folder (`Content/Verse/ArmoryWeapons/`
or `Content/SceneGraph/CustomWeapons/`):

| Template (digest) | Typical use |
|-------------------|-------------|
| `assault_rifle_template` | AR / custom rifle |
| `pistol_template` | Sidearm |
| `shotgun_template` | Shotgun |
| `sub_machine_gun_template` | SMG |
| `held_item_template` (42.30) | Not a weapon — a held prop (torch by default) → `held_items` |

These four are the only Armory weapon templates in the 42.40 digest. A bow,
sniper or minigun is one of them re-meshed and re-tuned. Templates already ship
a full fire/reload loop — you tune and re-skin them.

**Build Verse** after creating or renaming a prefab: only then is it a class in
Assets.digest (`EP_CustomAR<scoped {…}> := class<final><concrete>(entity)`).
Verse in another folder reaches it only after the prefab folder is declared
`<public>` — `sys_owned_weapons` → "Reach the prefab from any folder".

### Component tour (UI → digest)

**Pickup** — `fort_item_pickup_interactable_component`
(`/Fortnite.com/Itemization`, extends `basic_interactable_component`).
Gated `@available {MinUploadedAtFNVersion := 4040}`. Owning entity must have
`item_component` **and** `mesh_component`. Fields from
`basic_interactable_component`:

- `CanInteractMessage` / `CannotInteractMessage`
- `Cooldown` / `CooldownPerAgent`
- `SuccessLimit` / `InteractableDuration`
- `Enable()` / `Disable()` (and item-interaction enable helpers)

**Weapon settings** — `fort_trace_weapon_component` (`/Fortnite.com/Armory`).
Every property has a matching `Set*` Verse API. Ranges are the digest's
`@editable_number` limits — the Details panel clamps to them, so Verse should
too:

| UI group | Property | Range / meaning |
|----------|----------|-----------------|
| Damage | `Damage` | 0–1000 |
| | `EnvironmentalDamageMultiplier` | 0–10 |
| | `RangeDamageMultiplier` | `[]fort_range_damage_multiplier` falloff |
| Shots | `MaxRange` | ≥ 0 |
| | `FireRate` | 0–**25** (typing 100 clamps) |
| | `ReloadTime` | 0–10 s — 0 is an instant reload |
| Spread | `ExpansionRateMultiplierPerShot`, `CooldownRateMultiplierOverTime`, `Idle` / `Moving` / `Crouching` / `Sliding` / `Sprinting` / `AimDownSight` `SpreadMultiplier` | 0–10 each |
| Recoil | `RecoilMultiplier`, `AimDownSightRecoilMultiplier` | 0–10 |
| Ammo | `MagazineCapacity` | 1–1000 |
| | `ShotAmmoCost` | 0–10 ammo per shot — **0 = never uses ammo, never reloads** (infinite magazine) |
| Visuals | `MuzzleFlash`, `MuzzleOffset`, `BulletTracer` (Niagara), `EjectionPortOffset`, `BulletShells` | |
| Sounds | `WeaponFireSound`, `EquipSound` (UI “clip”), ADS start/end, reload start/insert/end, `OutOfAmmoSound` | `[]sound_wave` |
| Aim (42.30) | `AllowAimDownSightsInAir`, `AllowAimDownSightsDuringReload` | `logic` |

There is no separate reserve-ammo setter on this component.

**Base weapon** — `fort_weapon_component`: `IsHolstered`, `HolsterChangedEvent`.

**Presentation** — `rarity_component` (`Common`, `Uncommon`, `Rare`, `Epic`,
`Legendary`, `Mythic`, `Exotic` from `/Fortnite.com/Itemization/FortniteRarities`),
`description_component` (display name + flavor), `icon_component` (hotbar).
Icon tips: Texture Source Actions to resize; use a **transparent PNG** so
rarity color shows through behind the art.

**Item categories** — `WeaponRanged` on `item_component.Categories`
(`/Fortnite.com/Itemization/FortniteItemCategories`). The templates leave it
empty and still work; set it when inventory tabs matter. `WeaponMelee` exists
but is undemonstrated — treat as unknown.

**Mesh flags** — after assigning your mesh: Enabled / Collidable / Visible (and
related mesh flags). Transform component: leave default.

## Custom mesh pipeline

1. **Sources:** Sketchfab, Fortnite Porting → Blender, Meshy, etc.
2. Prefer a **static** mesh for non-animated guns. Sculpted/skeletal only if you
   enable experimental Scene Graph Animation.
3. **Pivot on the grip** in Blender (grip = where the hand attaches).
4. Optional: join multi-part meshes (gun + prop); export FBX as mesh with
   **Apply Transform**.
5. **Textures:** Fortnite Porting often lands textures under a Texture Paints /
   cache folder — copy that path from the file explorer and import into a
   project `Textures` folder.
6. Create materials (packed ORM/specular maps → pin **G / R / B** into the
   matching material inputs; set material **Usage** for static mesh /
   instance / skeletal as needed). Cross-link materials skill for graph details.
7. Assign materials **per mesh material slot** (e.g. slot 0 = gun body, slot 1 =
   prop / gnome).
8. **Collision (Epic docs criteria):** Collision Preset → **Overlap All**;
   generate collision if missing (e.g. simplified box); delete stray hulls;
   customize as needed. Pivot must stay on the grip.
9. Wrong pivot after import: place the static mesh in the level → **Modeling
   Mode → XForm → Edit Pivot → Accept**. New instances use the new pivot.
10. **Prefab mesh swap (hard rule):** the template mesh slot is not swappable
    in place. **Delete** the stock mesh component, **add** a new
    `mesh_component` (asset-generated — needs a project mesh asset). The mesh
    class only appears after **Assets digest / Verse compile**. If the picker
    is empty, compile Verse and try again.

Cross-links: `modeling`, `materials`, optional `blender` / meshy; Niagara
muzzle/tracer → `vfx`.

## Skins = more prefabs

Verse has no material setter for a held weapon (`SetMaterial` is only on
`creative_prop`). A skin is a **duplicate prefab** whose mesh already carries
the skin material: duplicate `EP_CustomAR` → `EP_CustomAR_Gold` → swap the
material → build Verse → register it next to the base prefab
(`sys_owned_weapons` registry). One skin prefab per weapon family covers every
`WeaponId` that shares that family.

## World use and variants

- **Session loot:** drag the saved prefab into the level — players pick it up
  through `fort_item_pickup_interactable_component`. Nothing is saved.
- **Owned (saved) gun:** a Creative **Collectible Object**
  (`collectible_object_device`) + `sys_owned_weapons` — the pickup records
  ownership and grants a fresh prefab.
- **Item Granter / Item Spawner / Save Point** do not handle custom Armory
  prefabs (Save Point restored them as a grey, invisible template in 41.00).
  Grants are Verse.
- Verify look in **free camera** (third person) before trusting first person —
  first person is often bugged for custom Armory meshes.
- Scene Graph is modular: **Alt+drag** placed instances and tune FireRate /
  MagazineCapacity / Recoil on the **instance** (does not rewrite the prefab
  asset). Respect the ranges above.
- Players can hold **multiple copies** in one inventory.

## Upgrades (stats from Verse)

Apply stats to a **fresh** prefab instance before it is added, computed from
the prefab's authored base values. Re-applying to a gun that already has
upgrades compounds them. Clamp to the ranges above — Verse otherwise sets
values the Details panel would refuse.

```verse
using { /Fortnite.com/Armory }
using { /Verse.org/SceneGraph }

# The trace component can sit on a child entity of the prefab.
ResolveFortTraceWeapon<public>(Weapon : entity)<transacts> : ?fort_trace_weapon_component =
    if (Trace := Weapon.GetComponent[fort_trace_weapon_component]):
        return option{Trace}
    Traces := for (T : Weapon.FindDescendantComponents(fort_trace_weapon_component)) do T
    if (First := Traces[0]):
        return option{First}
    false

ApplyDamageLevel<public>(Weapon : entity, Level : int) : void =
    if (Trace := ResolveFortTraceWeapon(Weapon)?):
        Trace.SetDamage(Min(Trace.Damage * (1.0 + 0.1 * (Level * 1.0)), 1000.0))
```

Persist the **level**, not the stat (`sys_owned_weapons`).

## Verse controller (`creative_device`)

Not an entity component — a placed Creative Verse device with button
`@editable`s.

Modules (typical):

```verse
using { /Fortnite.com/Devices }
using { /Fortnite.com/Characters }
using { /Fortnite.com/Armory }
using { /Fortnite.com/Itemization }
using { /UnrealEngine.com/Itemization }
using { /Verse.org/SceneGraph }
using { /Verse.org/Simulation }
using { /UnrealEngine.com/Temporary/Diagnostics }
using { ArmoryWeapons }   # your public prefab folder module
```

After Verse build, the prefab is a concrete entity class in Assets.digest
(e.g. `GnomeGun{}` — name follows your asset). Construct a **fresh** instance
per grant; never reuse one entity across players.

**Find held guns by prefab type, not tags.** A dynamic cast `GnomeGun[Item]`
recognises the gun anywhere in the inventory (`Inventory.FindItems()` walks
the sub-inventories). Tags are only worth adding to group many prefabs into one
family query (`FindDescendantEntitiesWithTag`, `verse_authoring`).

### Editables

- Five `button_device`s: Grant, ChangeStats, Equip, Has, Clear
- Grant-time `Damage` / `FireRate`
- Change-to `Damage` / `FireRate` (second pair)
- Per-player `[player]logic` map for holster-watch once

Wire in `OnBegin`: subscribe all buttons + `PlayerRemovedEvent`; remove the
player from the watch map on leave (avoids leaks). Guard holster-watch spawn
so it does not run twice (known double-print bug).

### Five operations

1. **Grant** — wait until `inventory_component` exists (descendant of the
   agent, up to 5s) → construct a **fresh** prefab → optional
   `SetDamage` / `SetFireRate` → `AddItemDistribute` → **then**
   `item_component.GetParentInventory[]` + `Equip()`, else
   `PickUp[Inventory]` + `Equip()`, else `RemoveFromParent()`.
   `AddResult.Ok` / `GetSuccess[]` is **not** parented — do not `case` the
   distribute result and Equip only on Ok. Owned persist/pickup/rejoin uses
   this same parent/equip: verse `sys_owned_weapons`.
2. **Change stats** — every held `GnomeGun` →
   `SetDamage` / `SetFireRate` from change-to editables.
3. **Equip** — held `GnomeGun` → `Equip()`.
4. **Has** — any held `GnomeGun` → `Print` true/false.
5. **Clear** — each held `GnomeGun` → `RemoveItem` on **its own** parent
   inventory (`GetParentInventory[]`), not the first inventory found.

Tip: **Ctrl+click** a component type in the Verse editor to jump to its digest
API (all Scene Graph setters for the weapon live there).

### Compiling skeleton (confirm names before ship)

Replace `GnomeGun` with your Assets.digest class after compile. Do **not**
`case` `AddItemDistribute` to decide Equip.

```verse
using { /Fortnite.com/Devices }
using { /Fortnite.com/Characters }
using { /Fortnite.com/Armory }
using { /Fortnite.com/Itemization }
using { /UnrealEngine.com/Itemization }
using { /Verse.org/SceneGraph }
using { /Verse.org/Simulation }
using { /UnrealEngine.com/Temporary/Diagnostics }
using { ArmoryWeapons }

# Epic-style helper — inventory lives on a descendant of the agent.
GetFirstInventory(Agent:agent)<transacts><decides>:inventory_component =
    (for (Inv : Agent.FindDescendantComponents(inventory_component)) do Inv)[0]

# Every held GnomeGun, across the agent's sub-inventories.
HeldGnomeGuns(Agent:agent)<transacts>:[]entity =
    if (Inventory := GetFirstInventory[Agent]):
        for (Item : Inventory.FindItems(), GnomeGun[Item]) do Item
    else:
        array{}

custom_weapon_controller_device := class(creative_device):
    @editable GrantButton : button_device = button_device{}
    @editable ChangeButton : button_device = button_device{}
    @editable EquipButton : button_device = button_device{}
    @editable HasButton : button_device = button_device{}
    @editable ClearButton : button_device = button_device{}

    @editable GrantDamage : float = 30.0
    @editable GrantFireRate : float = 8.0
    @editable ChangeToDamage : float = 60.0
    @editable ChangeToFireRate : float = 16.0

    var IsWatching : [player]logic = map{}

    OnBegin<override>()<suspends>:void =
        GrantButton.InteractedWithEvent.Subscribe(OnGrant)
        ChangeButton.InteractedWithEvent.Subscribe(OnChangeStats)
        EquipButton.InteractedWithEvent.Subscribe(OnEquip)
        HasButton.InteractedWithEvent.Subscribe(OnHas)
        ClearButton.InteractedWithEvent.Subscribe(OnClear)
        GetPlayspace().PlayerRemovedEvent().Subscribe(OnPlayerRemoved)

    OnPlayerRemoved(Player:player):void =
        if (set IsWatching[Player] = false) {}

    OnGrant(Agent:agent):void =
        spawn{ GrantGun(Agent) }

    GrantGun(Agent:agent)<suspends>:void =
        var Tries : int = 0
        loop:
            if (GetFirstInventory[Agent]):
                break
            if (Tries >= 50):
                return
            set Tries += 1
            Sleep(0.1)
        if (Inventory := GetFirstInventory[Agent], Player := player[Agent]):
            # Fresh prefab instance — name from Assets.digest after Verse compile.
            Gun := GnomeGun{}
            if (Trace := Gun.GetComponent[fort_trace_weapon_component]):
                Trace.SetDamage(GrantDamage)
                Trace.SetFireRate(GrantFireRate)
            if (IC := Gun.GetComponent[item_component]):
                Inventory.AddItemDistribute(Gun)
                if (IC.GetParentInventory[]):
                    IC.Equip()
                else if (IC.PickUp[Inventory]):
                    IC.Equip()
                else:
                    Gun.RemoveFromParent()
                    return
                if (not IsWatching[Player]? or IsWatching[Player] = false):
                    if (set IsWatching[Player] = true) {}
                    spawn{ WatchHolster(Agent) }
            else:
                Gun.RemoveFromParent()

    OnChangeStats(Agent:agent):void =
        for (Gun : HeldGnomeGuns(Agent)):
            if (Trace := Gun.GetComponent[fort_trace_weapon_component]):
                Trace.SetDamage(ChangeToDamage)
                Trace.SetFireRate(ChangeToFireRate)

    OnEquip(Agent:agent):void =
        for (Gun : HeldGnomeGuns(Agent)):
            if (IC := Gun.GetComponent[item_component]):
                IC.Equip()

    OnHas(Agent:agent):void =
        if (HeldGnomeGuns(Agent).Length > 0):
            Print("Player has custom gun in inventory")
        else:
            Print("Player does not have custom gun")

    OnClear(Agent:agent):void =
        for (Gun : HeldGnomeGuns(Agent)):
            if (IC := Gun.GetComponent[item_component], Parent := IC.GetParentInventory[]):
                Parent.RemoveItem(Gun)

    # One watcher per player. Every pass waits, so holding no gun never spins the loop
    # (a loop that does not wait hits the computation limit); it ends when the player
    # leaves, because OnPlayerRemoved clears IsWatching.
    WatchHolster(Agent:agent)<suspends>:void =
        loop:
            if (Player := player[Agent], not IsWatching[Player]?):
                break
            if (Gun := HeldGnomeGuns(Agent)[0], Weapon := Gun.GetComponent[fort_weapon_component]):
                Changed := race:
                    block:
                        Weapon.HolsterChangedEvent.Await()
                        true
                    block:
                        Sleep(1.0)              # re-check IsWatching at least once a second
                        false
                if (Changed?):
                    if (Weapon.IsHolstered = true):
                        Print("Gun holstered")
                    else:
                        Print("Gun unholstered")
            else:
                Sleep(0.5)                      # no gun held: wait, then look again
            Sleep(0.1)
```

Notes:

- `GnomeGun` is a placeholder for your compiled prefab class — verify with
  `get_verse_api({"name": "GnomeGun"})` (or your asset name).
- Script error 3593 on `GnomeGun` / `using { ArmoryWeapons }` = the prefab
  folder is still internal — declare it `<public>` (`sys_owned_weapons`).
- `AddItemDistribute` / `RemoveItem` return `result` and are **not** failable
  `if` wrappers — ignore Ok/Err for Armory parent/equip. After distribute,
  `GetParentInventory[]` then `Equip()`, else `PickUp[Inventory]` then
  `Equip()`, else `RemoveFromParent()`. Owned loop:
  `skill_read_subskill("verse", "sys_owned_weapons")`.
- Holster watch: once per player via `IsWatching`; clean on `PlayerRemoved`.
- Wire buttons with `wire_verse_device_ref` after placing the device —
  **one field per turn** (SERIAL: one mutating/editor call per assistant message.).
  Never same-turn multi-wire.

## Limits and pitfalls

- First-person view often broken; verify in free camera / third person.
- Muzzle / ejection / FX offsets are hard to visualize in the prefab editor.
- Recoil feel can be subtle even at high multipliers.
- Pickup interaction can feel iffy.
- Scene Graph Animation for weapon skeletal motion is experimental / publish-risk.
- UI “forge” names ≠ digest `fort_trace_*` — trust digests.

## Failure table

| Symptom | Cause |
|---------|-------|
| Mesh not in mesh_component picker | Assets digest stale — compile Verse |
| Prefab class unknown in Verse | Created/renamed after the last Verse build — build, `search_verse_digest("EP_")` |
| Script error 3593 on the prefab | Prefab folder module is internal — declare it `<public>` (`sys_owned_weapons`) |
| Gun floats beside the hand | Pivot not on the grip — Edit Pivot / Blender |
| Cannot pick up a placed prefab | Missing `fort_item_pickup_interactable_component`, `item_component` or `mesh_component` |
| Grant “works” but no hotbar icon | Island inventory configuration missing (BR-style) |
| Change/Clear hits nothing | Cast against the wrong class — a skin prefab is its own class |
| Gun left in world after failed grant | Forgot `RemoveFromParent` when PickUp also fails |
| Picked collectible / granted, cannot shoot | Used `AddResult.Ok` only — missing `PickUp`+`Equip`; or collectible look-only with no `sys_owned_weapons` grant |
| Never reloads / never runs dry | `ShotAmmoCost` is 0 — set 1+ for normal ammo use |
| Holster prints twice | Watch loop spawned twice — use `IsWatching` map |
| FireRate stuck at 25 | Digest / editor limit |
| First person looks wrong | Known limit — use third person |
| Island won’t publish after weapon anim | Experimental Scene Graph Animation enabled |
| Picked up loot is gone after rejoin | Placed prefab is session loot — owned guns are `collectible_object_device` + persist (`sys_owned_weapons`) |
| Grey / invisible custom gun after load | Save Point device restored it — persist + fresh grant only |
| Upgrade stacked / didn’t save | Mutated the held entity — persist the level, grant fresh (`sys_owned_weapons`) |

## Related skills / MCP (no new weapon tools)

| Need | Skill | Tools |
|------|-------|-------|
| This path | scenegraph `custom_weapons` | entity/prefab tools + Verse digests |
| Persist / load / collectible / canvas shop / rejoin | verse `sys_owned_weapons` | — |
| Custom non-weapon items | scenegraph `custom_items` | same |
| Stock FN guns | scenegraph `itemization` | same |
| Soft inventory / shops | verse `sys_inventory` / `sys_economy` | device wire / granter fields |
| Folder modules (E3593) | verse `modules`, `compile_errors` | — |
| Mesh / mats / Niagara | modeling, materials, vfx | domain MCP tools |
| Tags / hierarchy | scenegraph `verse_authoring` | digests |
| Weapon inspect / melee clip on player | animation `player_animation` | `set_anim_additive_type`, etc. |
| NPC combat (not player Armory) | Store `npc-ai` / verse `sys_npc_ai` | digests |
| Flamethrower / hand-rolled fire loops | out of scope — sequel content, not Armory templates | — |
