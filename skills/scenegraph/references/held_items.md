---
description: "Held items (poses) — /Fortnite.com/Armory held_item_template: carryable non-weapon prefabs (torch by default → lantern, tool, banner, prop), fort_item_owner_pose_modifier_component hold poses (torch, flashlight, map, small/large consumable), Entity Prefab setup, reskin, Verse grant/equip, ADS toggles on weapons"
metadata:
  order: 8
  label: "Held items + hold poses"
  default_enabled: false
  load_condition: "Something the player carries or holds that is not a weapon (torch, lantern, flashlight, tool, banner, sign, bucket, prop in hand), held_item_template, Custom Weapons: Held Items, reskinning the torch, how the character holds the item (hold pose, stance, animation while equipped, fort_item_owner_pose_modifier_component, SetEquippedPose)"
---

# Held items

Epic added a fourth kind of Armory prefab: a **carryable item that is not a
weapon**. `held_item_template` (`/Fortnite.com/Armory`,
`@available`) is a ready-to-customize Entity
Prefab — it ships with a **torch** mesh and icon. Reskin it into a lantern, a
tool, a banner, a flashlight, any prop the player equips and holds.

It sits next to the weapon templates (`pistol_template`, `assault_rifle_template`,
`shotgun_template`, `sub_machine_gun_template` — `custom_weapons`) and follows
the same workflow. Verified: `held_item_template{}` + `AddItemDistribute` +
`Equip()` compiles (Tycoony, Oct 1 2026). Epic added the template's mesh class
to the digest: `torch_mesh := class<final>(mesh_component)` (`/Fortnite.com/Armory`)
— the default torch; swap the mesh in the prefab, don't subclass it.

## Pick the right path

| Goal | Use |
| --- | --- |
| Hold a prop / tool / light in hand | **this file** |
| A gun with fire/reload | `custom_weapons` |
| An item with your own behavior (no hold pose needed) | `custom_items` |
| Change how the character holds it | **Hold pose** below |
| Stock Fortnite items | `itemization` |

## Project gates

Same as custom weapons: **Project Settings → Custom Items in Inventory** = true,
and an island **itemization inventory configuration** (else the hotbar stays
empty — `islandsettings` `recipes`).

## Author the prefab

1. `ValkyrieToolset.PrefabToolset` `CreatePrefab` `{"folderPath": "Prefabs",
   "assetName": "Lantern", "parentClass": {"refPath":
   "/Armory/_Verse/VNI/ArmoryRuntime.held_item_template"}}`. Verified: the
   new prefab already has `item_component`, the pickup, description, icon,
   rarity, `torch_mesh`, `fort_item_owner_pose_modifier_component` and
   `fort_held_item_component` on its `rootEntity` — nothing to add.
2. Swap the mesh and set icon / text with EntityToolset on that `rootEntity`
   (`RemoveComponent` `torch_mesh` → `AddComponent` your mesh class; pivot/axis
   fixes on a child mesh entity, `movement_transforms`). Text, icon, rarity:
   same calls as `custom_items` **Build it over MCP**. Keep `item_component`
   and the pickup component.
3. `ApplyPrefabEdits` + `save_asset`. After a Verse build the prefab is a class
   in the Assets digest — `list_verse_types(digest="assets",
   name_filter="Lantern")` — use that name in Verse.

`create_empty_prefab` / `create_prefab_from_entities` cannot make a template prefab (they
lose the template's components) — use `CreatePrefab` with `parentClass`. Copies of an
existing one: `duplicate_prefab(source_prefab="/MyIsland/Prefabs/Lantern.Lantern",
prefab_name="Flashlight")` keeps all the template's components.

## Hold pose

`held_item_template` now ships a **`fort_item_owner_pose_modifier_component`**
(`/Fortnite.com/Itemization`, `class<final>`, not experimental). It sets the stance
the character uses while the item is equipped. Default: **fire torch**. Pick the pose
on the prefab's pose component (`EquippedPose`) or change it at runtime:

| Pose class (`/Fortnite.com/Itemization`) | Hold like |
| --- | --- |
| `fort_character_pose_modifier_fire_torch` | torch (default) |
| `fort_character_pose_modifier_flashlight` | flashlight / lantern pointed ahead |
| `fort_character_pose_modifier_map` | map / paper read with both hands |
| `fort_character_pose_modifier_consumable_small` | small consumable |
| `fort_character_pose_modifier_consumable_large` | large consumable |

```verse
using { /Fortnite.com/Armory }
using { /Fortnite.com/Itemization }      # pose component + pose classes

SetHoldPose(Item:entity):void =
    if (Pose := Item.GetComponent[fort_item_owner_pose_modifier_component]):
        Pose.SetEquippedPose(option{fort_character_pose_modifier_flashlight{}})
        # Pose.SetEquippedPose(false)   # clear: no pose override
```

`EquippedPose` is `var<private>` (read it, don't `set` it) — always go through
`SetEquippedPose(?fort_character_pose_modifier)`. The pose classes are `<final>`;
the base `fort_character_pose_modifier` is `epic_internal`, so no custom poses —
only these five. Compiled 0 errors / 0 warnings.

## Grant and equip from Verse

```verse
using { /Fortnite.com/Armory }
using { /Fortnite.com/Devices }
using { /UnrealEngine.com/Itemization }
using { /Verse.org/SceneGraph }
using { /Verse.org/Simulation }

# Inventory lives on a descendant of the agent.
GetHeldInventory(Agent:agent)<transacts><decides>:inventory_component =
    (for (Inv : Agent.FindDescendantComponents(inventory_component)) do Inv)[0]

held_item_granter_device := class(creative_device):
    @editable GrantButton : button_device = button_device{}

    OnBegin<override>()<suspends>:void =
        GrantButton.InteractedWithEvent.Subscribe(OnGrant)

    OnGrant(Agent:agent):void =
        if (Inventory := GetHeldInventory[Agent]):
            # Your prefab from the Held Item template (Assets.digest name), e.g. Lantern{}.
            # Lantern is a subclass of held_item_template, so held_item_template[E] casts work.
            Item := held_item_template{}
            if (IC := Item.GetComponent[item_component]):
                Inventory.AddItemDistribute(Item)
                if (IC.GetParentInventory[]):
                    IC.Equip()
                else if (IC.PickUp[Inventory]):
                    IC.Equip()
                else:
                    Item.RemoveFromParent()
            else:
                Item.RemoveFromParent()
```

Do not `case` the `AddItemDistribute` result to decide Equip — check
`GetParentInventory[]`, else `PickUp[Inventory]`, else clean up (same as
`custom_weapons`). On join, poll until the inventory exists (`custom_weapons`).

## Also new (weapons)

`fort_trace_weapon_component` gained two editable toggles with setters:
`AllowAimDownSightsInAir` / `SetAllowAimDownSightsInAir(Val:logic)` and
`AllowAimDownSightsDuringReload` / `SetAllowAimDownSightsDuringReload(Val:logic)`.

Fixes that matter here: equipping an item from Verse no longer leaves the
player unable to aim or shoot, and `RemoveItemEvent`'s `RemovedAmount` is no
longer always 0.
