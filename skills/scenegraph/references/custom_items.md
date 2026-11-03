---
description: "Custom Scene Graph items that can do anything — BUILD them over Epic MCP (PrefabToolset CreatePrefab + EntityToolset AddComponent/SetComponentProperty, message text from Verse, category via Python), itemization shell + Verse components for equipped logic, KFM spin, categories/stack/rarity, world loot, and creative_device grant/equip/clear/has"
metadata:
  order: 8
  label: "Custom Scene Graph items"
  default_enabled: false
  load_condition: "Making / creating / adding a custom item (any non-weapon item Entity Prefab), custom inventory pickup mesh/icon, item name/description text, item Categories (currency/resource/ammo), stacking/rarity, spinning or bobbing dropped items with keyframed_movement, detecting IsEquipped / ChangeEquippedEvent, Verse components that run while held, or granting custom Scene Graph items (not Armory weapons)"
---

# Custom Scene Graph items (do anything)

Custom non-weapon items are **Entity Prefabs**: an itemization **shell** plus
**your Verse components** for all gameplay. There is no separate “custom item
device type.” Behavior = whatever you attach and run while the entity is
simulating / equipped. Always confirm members with `get_verse_api` /
`search_verse_digest` before shipping.

**Asked for a custom item → build it.** Every step is an MCP call (43.00):
create the prefab, add the components, set text / category / icon / mesh,
save, place, grant. Never answer with "open the prefab and add components in
the Details panel" — that was the old limit and is gone. The recipe is
**Build it over MCP** below.

**UEFN + Scene Graph only** — not Fortnite Creative 1.0. Custom items require
the Scene Graph / inventory stack; they do not exist as Classic Creative
devices.

Not Creative Item Granters / Item Spawners. Not Armory weapon templates
(`custom_weapons`).

## Choose the path

| Goal | Load |
|------|------|
| Stock Fortnite gun / item grant | `skill_read_subskill("scenegraph", "itemization")` |
| **Fully custom non-weapon item (mesh/icon + Verse logic)** | **this file** |
| Template ability (Spicy Sprint / AbilityElements / IA_Sprint) | `skill_read_subskill("scenegraph", "template_abilities")` |
| Custom Armory firearm (AR/pistol/shotgun/SMG) | `skill_read_subskill("scenegraph", "custom_weapons")` |
| Soft persist bags + Creative Item Granter | `skill_read_subskill("verse", "sys_inventory")` |

**No Verse required for loot on the ground.** Place the prefab; the player
picks it up. Verse is for grant / equip / equipped gameplay / KFM drivers /
anything else you invent.

## Mental model — shell + behavior

```
Entity Prefab (item entity)
├── itemization shell (required builtins)
│   ├── item_component          (+ optional Categories)
│   ├── fort_item_pickup_interactable_component
│   ├── description_component   (Name / Description / ShortDescription)
│   ├── icon_component          (Icon:texture)
│   └── mesh_component          (dropped look; Collidable = false)
├── optional builtins
│   ├── rarity_component
│   ├── basic_stackable_component
│   └── keyframed_movement_component   (visuals while dropped)
└── YOUR Verse components          ← this is "do anything"
    ├── equipped detect / while-held loops
    ├── buttons, VFX, damage, economy hooks, …
    └── KFM drivers, tags, child entities
```

**Do not** put `fort_inventory_component` / `fort_inventory_*` on the item.
Tutorials often add “Fort Inventory” in the Add Component list and call it
"fundamental" — the digest says otherwise: `fort_inventory_component` is
`class<epic_internal>(inventory_component)`, "a shared class for all Fortnite
inventories". These are **player inventory** subclasses under
`/Fortnite.com/Itemization` (they define hotbars/tabs the *agent* owns), not
item shells:

| Player inventory type (do NOT put on the item) |
|------------------------------------------------|
| `fort_inventory_component` (base) |
| `fort_inventory_weapon_hotbar_component` |
| `fort_inventory_build_hotbar_component` |
| `fort_inventory_harvest_tool_component` |
| `fort_inventory_trap_component` |
| `fort_inventory_resources_component` |
| `fort_inventory_ammo_component` |
| `fort_inventory_currencies_component` |

Tab placement for *your* item uses `item_component.Categories` (below).

## Project gates

1. **Project Settings → Inventory system / Custom Items in Inventory** = true.
   Enabling inventory often flips related **experimental** Scene Graph options —
   publish-risk until Epic stabilizes. Check without the UI: the island's
   `<Project>.uefnproject` (`workspace_read_file`) has
   `dataSets.experimental.sceneGraph.bIsSceneGraphSystemAllowed` and
   `dataSets.experimental.inventory.bIsCustomInventoryAllowed` — both `true`.
   If either is false, tell the user to switch it on (Project → Project
   Settings); don't edit the file while UEFN has the project open.
2. Island **itemization inventory configuration** must be set or HUD stays empty
   after pickup/grant — `skill_read_subskill("islandsettings", "recipes")`.
   Check over MCP with Python: the `FortMinigameSettingsBuilding` actor's
   `get_custom_inventory_configuration()` (BR style =
   `/Itemization/BRStyle/ItemizationConfiguration_BRStyle`).
3. Expect the **new inventory UI** (BR-style tabs) when Custom Items are on —
   that HUD is what surfaces custom currencies / resources / ammo / world items.

## Build it over MCP (verified 43.00)

Verified Nov 2 2026 on UEFN 43.00: every step below ran through Epic's MCP; the
saved prefab kept all five components, the text, the category, the icon, a KFM
component and a Verse spin component, and a Verse grant of the prefab compiled.

Calls are nested Epic MCP — `unreal__call_tool({"toolset_name": T, "tool_name":
N, "arguments": A})` (`skill_read_subskill("uefn", "epic_mcp")`). One mutating
call per message.

| Short | `toolset_name` |
|-------|----------------|
| Prefab | `ValkyrieToolset.PrefabToolset` |
| Entity | `ValkyrieToolset.EntityToolset` |
| Verse | `VerseToolset.VerseToolset` |
| Python | `editor_toolset.toolsets.python_scripting.PythonScriptingTools` (`read_me` once, then `execute_python`) |

| # | Call | Notes |
|---|------|-------|
| 1 | Prefab `CreatePrefab` `{"folderPath": "Items", "assetName": "EP_Cat"}` | Returns `rootEntity` (`/<Proj>/Items/EP_Cat.Default__EP_Cat_C`) and `generatedClass` (`…EP_Cat_C`). The root entity **is** the item: add components to it, no child entity. |
| 2 | Entity `AddComponent` `{"entity": {"refPath": "<rootEntity>"}, "componentClass": {"refPath": "<class>"}}` per class below | Each result gives the component path (`…:item_component_0`) the next steps use. One component per type (subclasses count). |
| 3 | Text: Verse messages (below), then Entity `SetComponentProperty` on the description component — `Name`, `Description`, `Short Description` = `"{\"refPath\":\"<message object>\"}"` | A plain `"\"Cat\""` fails: "is not a valid object path". |
| 4 | Category: Python (below) | Entity `SetComponentProperty` and Object `SetProperties` both refuse Fortnite's category objects ("refused by the project's asset reference policy"). |
| 5 | Entity `SetComponentProperty` on the mesh component: `Collidable` = `"false"` | Collision on a pickup bumps / launches the player. |
| 6 | Entity `SetComponentProperty` on `icon_component`: `Icon` = `"{\"refPath\":\"/<Proj>/Items/T_Cat.T_Cat\"}"` | The texture **asset** path. The `/<Proj>/_Verse/Assets.…` object is only the holder and is refused. Reading `Icon` back shows the holder — normal. |
| 7 | Prefab `ApplyPrefabEdits` `{"prefab": {"refPath": "/<Proj>/Items/EP_Cat.EP_Cat"}}`, then `save_asset` on the prefab | Nothing auto-saves; placed copies update only after `ApplyPrefabEdits`. |
| 8 | Entity `CreateEntity` `{"entityClass": {"refPath": "<generatedClass>"}, "transform": {…}, "name": "Cat"}`, then `save_current_level` | A pickup in the level (XYZ, Unreal axes; scale here sizes the pickup). Confirm with `FindEntities` `{"nameFilter": "Cat"}`. |
| 9 | Verse `BuildAll`, then grant from Verse (below) | `EP_Cat{}` exists in Verse only after a build. |

Component classes (`componentClass.refPath`, 43.00):

| Component | Class path |
|-----------|-----------|
| `item_component` | `/ItemizationCore/_Verse/VNI/ItemizationCoreRuntime.item_component` |
| `fort_item_pickup_interactable_component` | `/Itemization/_Verse/VNI/ItemizationRuntime.fort_item_pickup_interactable_component` |
| `description_component` | `/VersePresentation/_Verse/VNI/VersePresentation.description_component` |
| `icon_component` | `/EntityFramework/_Verse/VNI/Entity.icon_component` |
| Mesh: stock cube | `/VerseEngineAssets/_Verse/VNI/VerseEngineAssets.BasicShapes_cube` |
| Mesh: your mesh | `/<Proj>/_Verse/Assets.<Folder>-<SM_Name>` (after a Verse build) |
| `rarity_component` (optional) | `/EntityFramework/_Verse/VNI/Entity.rarity_component` |
| `basic_stackable_component` (optional) | `/EntityFramework/_Verse/VNI/Entity.basic_stackable_component` |
| `keyframed_movement_component` (spin/bob) | `/EntityFramework/_Verse/VNI/Component.KeyframedMovement_keyframed_movement_component` |
| Your Verse component | `/<Proj>/_Verse.Verse-<Module>-<class_name>` (after a Verse build) |

Anything else: Entity `ListComponentClasses` `{"nameFilter": "<part>"}` returns
the exact path. A failed `AddComponent` means a wrong path, not a missing
feature.

### Item text (message fields)

`description_component` fields are `message` objects, so the words live in
Verse. Write them, build, then point the fields at the compiled objects:

```verse
# Content/Verse/Items/item_text.verse
CatItemName<localizes><public>:message = "Cat"
CatItemDescription<localizes><public>:message = "A very good cat."
CatItemShort<localizes><public>:message = "Cat"
```

After `BuildAll` returns no errors, find the object paths (Python):

```python
out = []
for o in unreal.ObjectIterator(unreal.Object):
    try:
        p = o.get_path_name()
    except Exception:
        continue
    if '__verse_0x' in p and p.endswith(('_CatItemName', '_CatItemDescription', '_CatItemShort')):
        out.append(p)
print(out)
```

They look like `/<Proj>/_Verse.Default__Verse-Items:__verse_0x08ACF0AF_CatItemName`
(`Verse-Items` = the file's folder under `Content/`). Short copy is the
interact prompt before pickup.

### Category (Python)

```python
ic = unreal.load_object(None, '/<Proj>/Items/EP_Cat.Default__EP_Cat_C:item_component_0')
cat = unreal.load_object(None, '/Itemization/_Verse/VNI/ItemizationRuntime.Default__FortniteItemCategories:__verse_0x6B87E434_WorldItem')
ic.modify()
ic.set_editor_property('__verse_0x2B30D9D0_Categories', [cat])
print(ic.get_editor_property('__verse_0x2B30D9D0_Categories'))
```

Then `ApplyPrefabEdits` + save; the category survives the save (verified).
Category objects (`/Itemization/_Verse/VNI/ItemizationRuntime.Default__FortniteItemCategories:` + suffix):

| Category | Suffix |
|----------|--------|
| `WorldItem` | `__verse_0x6B87E434_WorldItem` |
| `Currency` | `__verse_0x6FE7F353_Currency` |
| `Resource` | `__verse_0x97E36786_Resource` |
| `Ammo`, `Trap`, `WeaponMelee`, `WeaponRanged` | the same `ObjectIterator` loop; the path ends `_Ammo` etc. |

If the hashed property name ever changes, the refusal from Entity
`SetComponentProperty` names it ("referenced by property
'__verse_0x…_Categories'").

**Rarity** is refused the same way; set it with the same Python on
`rarity_component_0`: property `__verse_0x4FECCAB7_RarityPrivate`, value
`/Itemization/_Verse/VNI/ItemizationRuntime.Default__FortniteRarities:__verse_0x9E895CDA_Common`
(other rarities: the `ObjectIterator` loop, path ends `_Uncommon`, `_Rare`, …).
The saved prefab passes content validation with both.

### By hand (only when a call above errors twice)

Content Drawer → right-click → **Entity Prefab Definition**; in the prefab
outliner the **simulation entity** is the world shell and your item entity is
the child that gets components; Details → Add Component; Categories → add
element; **Save**. Say which call failed and with what error.

### Required shell (UI → digest)

| UI label (tutorial) | Digest component | Role |
|---------------------|------------------|------|
| Item | `item_component` | Marks entity as an item. Add a **Categories** element in Details when you need a tab. |
| Fort item pickup | `fort_item_pickup_interactable_component` | World pickup/drop. **Do not skip** — tutorials forget this and pickups break. Needs sibling `item_component` + `mesh_component`. Gated FN ≥ 4040. |
| Item details | `description_component` | `Name`, `Description`, `ShortDescription` (`message`). Short copy is the interact / hover prompt before pickup. |
| Item icon | `icon_component` | `Icon:texture` — transparent PNG so rarity color shows through. |
| Mesh | `mesh_component` | **Dropped** appearance only for now (held mesh not reliable). **Collidable = false**. |

### Categories (inventory tabs)

`using { /Fortnite.com/Itemization/FortniteItemCategories }` — set on
`item_component.Categories` (over MCP: **Category (Python)** above; by hand:
Details → Categories → add element):

| Category | Typical tab / use |
|----------|-------------------|
| `WorldItem` | Generic world / custom item |
| `Currency` | Currency tab |
| `Resource` | Resources tab |
| `Ammo` | Ammo tab |
| `Trap` | Traps |
| `WeaponMelee` / `WeaponRanged` | Weapon tabs (prefer Armory templates for real guns → `custom_weapons`) |

Currency/resource/ammo-only items belong on those categories so they land in
the matching inventory UI tab, not the weapon hotbar.

### Optional builtins (digest-confirmed)

| Component | API notes |
|-----------|-----------|
| `rarity_component` | `var Rarity:rarity` — one rarity per entity. Instances in `/Fortnite.com/Itemization/FortniteRarities` (`Common` … `Exotic`). Gated FN ≥ 4000. |
| `basic_stackable_component` | Extends `stackable_component`: `StackSize`, `MaxStackSize`, `SetStackSize`, `SetMaxStackSize`, `Split`, `CanMergeInto`, `MergeInto`, stack change events. Set `split_prefab_type` to your prefab class. Grant with `?AllowMergeItems := true`. Gated FN ≥ 4000. |
| `keyframed_movement_component` | Dropped spin / bob / scale — drive from a Verse component (`movement_transforms`). |

## Custom mesh / icon pipeline

1. Import texture + static mesh under the **project** mount
   (`get_project_info().content_root` — never invent `/Game/...` creates):
   Epic `EditorToolset.TextureToolset` / `EditorToolset.StaticMeshToolset`
   import tools (`describe_toolset` for the names), or the `modeling` skill.
2. **Verse `BuildAll`** so the Assets digest exposes the mesh as a component
   class — without it the mesh is not attachable (and the UI picker is empty).
   Find it: Entity `ListComponentClasses` `{"nameFilter": "SM_Cat"}` →
   `/<Proj>/_Verse/Assets.<Folder>-SM_Cat`.
3. Mesh: Entity `RemoveComponent` the cube class, then `AddComponent` your mesh
   class (one mesh per entity; an in-place swap fails). Icon: step 6 above with
   the texture's asset path.
4. Size: the placement scale (step 8) or a child mesh entity. Weird hitbox
   after import → re-import / rescale.
5. Collidable **off** on the new mesh component — collision bumps / launches
   the player.

Cross-links: `modeling`, `materials`; optional `blender` / meshy.

**43.00 prefab classes:** a prefab whose parent is a class other than `entity` (a template
such as `held_item_template` or `assault_rifle_template`, or your own entity subclass) is
generated as a **subclass of that parent** in the Assets digest, so `parent[E]` casts and
parent fields work. Built-in entity classes are no longer `<final>`; you may subclass
them in Verse. Plain entity prefabs still derive from `entity`. Need a hold stance for
the item → `held_items` (pose modifier). Since 43.00 editables on Verse class objects stay
independent per prefab instance, and assigning a device to an optional `@editable` on a
Verse component no longer crashes UEFN.

## World use

- Save the Entity Prefab, then place it: Entity `CreateEntity` with the
  prefab's `generatedClass` (step 8) + `save_current_level`. Ducky's
  `instantiate_prefab` is the fallback.
- **Creative Item Granters / Item Spawners do not accept custom Entity Prefab
  items yet** — world place or Verse grant only.
- Experimental bugs to expect (do not thrash the prefab trying to “fix” them):
  - Mesh **scale resets** after reassignment
  - Dropped item **flies / launches** oddly
  - **Icon breaks** after drop → re-pickup
  - Interact volume / hitbox feels wrong until re-import
- Prefer third-person / free camera for look checks.

## Dropped visuals (KFM)

Same Scene Graph motion path as any entity —
`skill_read_subskill("scenegraph", "movement_transforms")`.

The keys are built in Verse, so the whole spin is two `AddComponent` calls and
one number — no keyframe array to fill in the Details panel (compiled and
attached over MCP on 43.00):

1. Write this component (`Content/Verse/Items/item_spin_component.verse`) and
   Verse `BuildAll`:

```verse
using { /Verse.org/SceneGraph }
using { /Verse.org/SceneGraph/KeyframedMovement }
using { /Verse.org/SpatialMath }
using { /Verse.org/Simulation }

# Spins a dropped item in place. Needs keyframed_movement_component on the same entity.
item_spin_component := class<final_super>(component):
    @editable
    SecondsPerTurn : float = 2.0

    OnBeginSimulation<override>():void =
        (super:)OnBeginSimulation()
        if (KFM := Entity.GetComponent[keyframed_movement_component]):
            Quarter := keyframed_movement_delta:
                Transform := transform:
                    Translation := vector3{}
                    Rotation := MakeRotationFromYawPitchRollDegrees(90.0, 0.0, 0.0)
                    Scale := vector3{}
                Duration := SecondsPerTurn / 4.0
                Easing := linear_easing_function{}
            KFM.SetKeyframes(array{Quarter, Quarter, Quarter, Quarter}, loop_keyframed_movement_playback_mode{})
            KFM.Play()

    OnEndSimulation<override>():void =
        if (KFM := Entity.GetComponent[keyframed_movement_component]):
            KFM.Stop()
        (super:)OnEndSimulation()
```

2. Entity `AddComponent` the KFM class
   (`/EntityFramework/_Verse/VNI/Component.KeyframedMovement_keyframed_movement_component`)
   — builtin, `<final>`, never subclassed.
3. Entity `AddComponent` `/<Proj>/_Verse.Verse-Items-item_spin_component`
   (exact path: `ListComponentClasses` `{"nameFilter": "item_spin"}`), then
   `SetComponentProperty` `SecondsPerTurn` = `"3.0"` if wanted.
4. `ApplyPrefabEdits` + save.

Rules: **four 90° keys** — one 360° key is no rotation, and keys above 90°
fail in practice too. `Scale := vector3{}` in every delta (scale is
added). Bob = one translation key with `pingpong`; designer-tuned keys →
`keyframed_path_component` in `movement_transforms`. `Stop()` in
`OnEndSimulation` — Scene Graph leaks crash sessions.

Playback: `oneshot_`, `loop_`, `pingpong_keyframed_movement_playback_mode`.
`SetKeyframes` does **not** autoplay — call `Play()`. Pick up → drop again
should keep spinning if the driver restarts on simulate.

## Do anything — Verse behavior on the item

Attach one or more **project Verse components** to the item entity. That is the
entire custom-ability surface: print, spawn VFX, open UI, spend currency, deal
damage, enable a button device via events, a while-held loop that waits (below),
tags for FindDescendant queries, child entities for lights/meshes. Attach them
over MCP like any component (`ListComponentClasses` after a build →
`AddComponent`).

Lifecycle: subscribe in `OnBeginSimulation`, cancel in `OnEndSimulation`
(`verse_authoring`). Components simulate in editor and play — guard with
equipped checks if logic should only run when held.

### Equipped detect (digest names)

On `item_component`:

| API | Notes |
|-----|-------|
| `IsEquipped[]` | Failable succeeds when equipped |
| `ChangeEquippedEvent` | `listenable(change_equipped_result)` |
| `Equip()` / `Unequip()` | `result(...)` — not failable `if` |
| `Drop[]` / `PickUp[Inventory]` | World ↔ inventory |
| `ChangeInventoryEvent` | Inventory moves |

On `change_equipped_result` (event payload):

| Field | Type |
|-------|------|
| `ItemComponent` | `item_component` |
| `IsItemEquipped` | `logic` — this is the tutorial’s “Is Item Equipped” name |

Prefer `ChangeEquippedEvent` over polling. Polling recipe (tutorial style) must
break on `not IsSimulating[]` (on **this** `component`) to avoid memory leaks /
crashes when the item leaves the scene:

```verse
using { /UnrealEngine.com/Itemization }
using { /Verse.org/SceneGraph }
using { /Verse.org/Simulation }
using { /UnrealEngine.com/Temporary/Diagnostics }

# Event-driven gate (preferred). A spawn task cannot be cancelled (task has no
# Cancel()), so the background loop races a stop signal instead.
custom_item_behavior_component := class<final_super>(component):
    var MaybeEquipSub : ?cancelable = false
    StopHolding : event() = event(){}

    OnBeginSimulation<override>():void =
        (super:)OnBeginSimulation()
        if (IC := Entity.GetComponent[item_component]):
            set MaybeEquipSub = option{ IC.ChangeEquippedEvent.Subscribe(OnEquipChanged) }
            if (IC.IsEquipped[]):
                StartHolding()

    OnEndSimulation<override>():void =
        StopHolding.Signal()
        if (Sub := MaybeEquipSub?):
            Sub.Cancel()
        set MaybeEquipSub = false
        (super:)OnEndSimulation()

    OnEquipChanged(Result:change_equipped_result):void =
        if (Result.IsItemEquipped = true):
            Print("Item is equipped")
            StartHolding()   # enable buttons / VFX / abilities here
        else:
            Print("Item is not equipped")
            StopHolding.Signal()    # disable the same logic here

    StartHolding():void =
        StopHolding.Signal()            # end any previous holder first
        spawn{ HoldUntilStopped() }

    HoldUntilStopped()<suspends>:void =
        race:
            StopHolding.Await()         # first to finish wins; the loop is cancelled
            WhileEquipped()

    WhileEquipped()<suspends>:void =
        # ~10 Hz is enough for held-item logic; TickEvents.Subscribe does not compile in creator code.
        loop:
            if (not IsSimulating[]):
                break
            if (IC := Entity.GetComponent[item_component], IC.IsEquipped[]):
                # … your custom item logic …
                Sleep(0.1)
            else:
                break
```

`using { /UnrealEngine.com/Itemization }` is required for `item_component`.
Build / push Verse before the custom component appears in the prefab’s Add
Component list. The **gate** is `ChangeEquippedEvent` + `IsItemEquipped` (or
`IsEquipped[]`); cancellation is `race` against an `event()`, never `Cancel()` on
a `spawn` result.

### Agent-side inventory reactions

For systems outside the item (shops, quests, HUD): subscribe on the player’s
`inventory_component` to `AddItemEvent` / `RemoveItemEvent` / `EquipItemEvent` /
`UnequipItemEvent` — see `itemization`. Find inventory with
`Agent.FindDescendantComponents(inventory_component)`. 42.30 fixed
`RemoveItemEvent`'s `RemovedAmount` (it was always 0) and equipping from Verse
no longer leaves the player unable to aim or shoot.

## Verse grant / equip / clear / has

Same parenting check as `custom_weapons`. Items are found **by prefab type**
(`FindDescendantEntities(EP_Cat)`) — no tag to add to the prefab. Compiled on
43.00 against an MCP-built prefab:

```verse
using { /Fortnite.com/Devices }
using { /UnrealEngine.com/Itemization }
using { /Verse.org/SceneGraph }
using { /Verse.org/Simulation }
using { /UnrealEngine.com/Temporary/Diagnostics }
# The prefab's Assets module: copy the "Module import path" line above EP_Cat in
# <Project>-Assets.digest.verse, e.g. using { /yourname@fortnite.com/MyIsland/Items }

custom_item_controller_device := class(creative_device):
    @editable GrantButton : button_device = button_device{}
    @editable EquipButton : button_device = button_device{}
    @editable HasButton : button_device = button_device{}
    @editable ClearButton : button_device = button_device{}

    OnBegin<override>()<suspends>:void =
        GrantButton.InteractedWithEvent.Subscribe(OnGrant)
        EquipButton.InteractedWithEvent.Subscribe(OnEquip)
        HasButton.InteractedWithEvent.Subscribe(OnHas)
        ClearButton.InteractedWithEvent.Subscribe(OnClear)

    FirstInventory(Agent:agent)<transacts><decides>:inventory_component =
        (for (Inv : Agent.FindDescendantComponents(inventory_component)) do Inv)[0]

    # One fresh prefab per grant, never shared between players.
    OnGrant(Agent:agent):void =
        if (Inventory := FirstInventory[Agent]):
            Item := EP_Cat{}
            Inventory.AddItemDistribute(Item)   # ?AllowMergeItems := true if stackable
            # The result has no Ok/Err patterns — decide by parenting.
            if (IC := Item.GetComponent[item_component]):
                if (IC.GetParentInventory[]):
                    IC.Equip()
                else if (IC.PickUp[Inventory]):
                    IC.Equip()
                else:
                    Item.RemoveFromParent()

    OnEquip(Agent:agent):void =
        for (Held : Agent.FindDescendantEntities(EP_Cat)):
            if (IC := Held.GetComponent[item_component]):
                IC.Equip()

    OnHas(Agent:agent):void =
        Owned := for (Held : Agent.FindDescendantEntities(EP_Cat)) do Held
        if (Owned.Length > 0):
            Print("Player has {Owned.Length} of the item")
        else:
            Print("Player does not have the item")

    OnClear(Agent:agent):void =
        if (Inventory := FirstInventory[Agent]):
            for (Held : Agent.FindDescendantEntities(EP_Cat)):
                Inventory.RemoveItem(Held)
```

Rules:

- Construct a **fresh** prefab `{}` per grant — never reuse across players.
- On add failure: `RemoveFromParent()`.
- `EP_Cat` is the prefab's asset name; `get_verse_api({"name": "EP_Cat"})`
  after a build. The full module path in `using` compiled without a `<public>`
  folder declaration (43.00); a 3593 error → `custom_weapons`.
- No inventory yet right after join → retry later (a button press is late
  enough); a join-time grant polls like `custom_weapons`.
- **Footgun:** bulk-granting many stock weapons + custom items in one tight
  loop has produced infinite-loop Verse errors. Grant one item per interaction.
- Wire buttons with `wire_verse_device_ref` — **one field per turn**
  (SERIAL: one mutating/editor call per assistant message.).

## Recipe checklist (full custom item)

All of it over MCP (**Build it over MCP**), in this order:

1. Gates: `.uefnproject` flags + island inventory config.
2. Verse: item text file (+ `item_spin_component`, behavior components) →
   `BuildAll` clean.
3. `CreatePrefab` → `AddComponent` the shell (+ KFM, spin, behavior).
4. Text refPaths, Collidable off, icon asset path, category / rarity (Python).
5. `ApplyPrefabEdits` + `save_asset`.
6. `CreateEntity` the `generatedClass` in the level + `save_current_level`;
   grant device if wanted.
7. Report what was built (prefab path, components, where it is placed), then
   one live run: pickup → equip → behavior → drop.

## Limits and pitfalls

- UEFN / Scene Graph only — not Creative 1.0.
- Experimental: drop flies, icon breaks on re-pickup, mesh scale resets, weird
  interact hitbox after import.
- A plain item shows its mesh only when dropped. For a **held** look, create
  the prefab from `held_item_template` (`CreatePrefab` `parentClass`
  `/Armory/_Verse/VNI/ArmoryRuntime.held_item_template`) — it arrives with
  item, pickup, description, icon, rarity, mesh, pose and held components
  already on it (`held_items`).
- Creative granters / spawners cannot host custom Entity Prefab items yet.
- `fort_inventory_*` on the item is wrong — use `Categories` instead.
- KFM yaw steps above ~90° often fail; use multiple smaller deltas.
- Always `Stop()` KFM / cancel subs / break on `not IsSimulating[]` in
  `OnEndSimulation` — leaks crash sessions.
- Epic may ship more ability comps later — digests beat tutorials.

## Failure table

| Symptom | Cause |
|---------|-------|
| You were about to tell the user to add components in the UI | Wrong — Entity `AddComponent` on the prefab's `rootEntity` works (**Build it over MCP**) |
| `SetComponentProperty` `Name` → "not a valid object path" | Text is a `message` object — Verse `<localizes>` message + its refPath |
| Categories / Rarity → "refused by the project's asset reference policy" | Use the Python step |
| `Icon` → "is the holder … not something it can point at" | Pass the texture asset path, not the `_Verse/Assets` object |
| `AddComponent` refused / class not found | Wrong path — `ListComponentClasses`; your own class needs a clean `BuildAll` first |
| Every new level entity (even a plain `entity`) "has been destroyed" right after `CreateEntity`; `FindEntities` returns nothing | Editor level state broken — seen after failed Launch Session attempts. Prefab assets still work; save, restart UEFN, then place |
| Mesh not in mesh_component picker | Assets digest stale — Verse build / push |
| Player bumps / launches the pickup | Mesh Collidable still true |
| Cannot pick up | Forgot `fort_item_pickup_interactable_component`, or missing `item_component` / `mesh_component` |
| Pickup works but HUD empty | Island inventory configuration missing |
| Item in wrong inventory tab | Missing / wrong `Categories` (or wrongly added `fort_inventory_*` on the item) |
| Component missing from Add Component | Verse not built / not pushed |
| Spin never starts | Forgot `Play()` after `SetKeyframes` |
| Spin / poll loop after despawn | Missing `OnEndSimulation` `Stop()` / `not IsSimulating[]` break |
| Logic runs when on ground | Forgot equipped gate (`IsItemEquipped` / `IsEquipped[]`) |
| Drop flies / icon broken / scale wrong | Known experimental bugs — re-place / re-import; do not over-tune |
| Grant crashes / infinite loop | Bulk grant loop — grant one at a time |
| Item left in world after failed grant | Forgot `RemoveFromParent` on add failure |
| Stacks never merge | Missing `basic_stackable_component` or `?AllowMergeItems := true` |

## Related skills / MCP (no new item tools)

| Need | Skill | Tools |
|------|-------|-------|
| This path | scenegraph `custom_items` | Epic `PrefabToolset` + `EntityToolset` + `VerseToolset` (+ `PythonScriptingTools` for category/rarity), Verse digests |
| Stock FN guns / items | scenegraph `itemization` | same |
| Custom Armory firearms | scenegraph `custom_weapons` | same |
| KFM / transforms / TickEvents | `movement_transforms`, `verse_authoring` | same |
| Soft inventory / shops | verse `sys_inventory` / `sys_economy` | device wire / granter fields |
| Mesh / mats / Niagara | modeling, materials, vfx | domain MCP tools |
| Tags / hierarchy | scenegraph `verse_authoring` | digests |
