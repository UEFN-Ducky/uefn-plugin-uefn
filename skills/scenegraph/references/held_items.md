---
description: "Held items (v42.30, 43.00 poses) — /Fortnite.com/Armory held_item_template: carryable non-weapon prefabs (torch by default → lantern, tool, banner, prop), fort_item_owner_pose_modifier_component hold poses (torch, flashlight, map, small/large consumable), Entity Prefab setup, reskin, Verse grant/equip, ADS toggles on weapons"
metadata:
  order: 8
  label: "Held items + hold poses (42.30, 43.00)"
  default_enabled: false
  load_condition: "Something the player carries or holds that is not a weapon (torch, lantern, flashlight, tool, banner, sign, bucket, prop in hand), held_item_template, Custom Weapons: Held Items, reskinning the torch, how the character holds the item (hold pose, stance, animation while equipped, fort_item_owner_pose_modifier_component, SetEquippedPose)"
---

# Held items (v42.30)

42.30 adds a fourth kind of Armory prefab: a **carryable item that is not a
weapon**. `held_item_template` (`/Fortnite.com/Armory`,
`@available {MinUploadedAtFNVersion := 4230}`) is a ready-to-customize Entity
Prefab — it ships with a **torch** mesh and icon. Reskin it into a lantern, a
tool, a banner, a flashlight, any prop the player equips and holds.

It sits next to the weapon templates (`pistol_template`, `assault_rifle_template`,
`shotgun_template`, `sub_machine_gun_template` — `custom_weapons`) and follows
the same workflow. Verified: `held_item_template{}` + `AddItemDistribute` +
`Equip()` compiles in 42.30 (Tycoony, Oct 1 2026). 42.40 adds the template's mesh class
to the digest: `torch_mesh := class<final>(mesh_component)` (`/Fortnite.com/Armory`,
4240) — the default torch; swap the mesh in the prefab, don't subclass it.

## Pick the right path

| Goal | Use |
| --- | --- |
| Hold a prop / tool / light in hand | **this file** |
| A gun with fire/reload | `custom_weapons` |
| An item with your own behavior (no hold pose needed) | `custom_items` |
| Change how the character holds it (43.00) | **Hold pose** below |
| Stock Fortnite items | `itemization` |

## Project gates

Same as custom weapons: **Project Settings → Custom Items in Inventory** = true,
and an island **itemization inventory configuration** (else the hotbar stays
empty — `islandsettings` `recipes`).

## Author the prefab

1. Content Drawer → right-click → **Entity Prefab** → switch **template** →
   **Held Item** (`held_item_template`). Name it (e.g. `Lantern`).
2. In the prefab editor swap the mesh (child mesh entity — keep pivot/axis fixes
   on the child, `movement_transforms`) and the icon on the item's description /
   icon components. Keep `item_component` and the pickup component.
3. Save. After a Verse build the prefab is a class in the Assets digest —
   `list_verse_types(digest="assets", name_filter="Lantern")` — use that name in Verse.

`create_empty_prefab` / `create_prefab_from_entities` cannot make a template prefab (they
lose the template's components). Once the project has **one** Held Item prefab, make every
other held item from it with `duplicate_prefab(source_prefab="/MyIsland/Prefabs/Lantern.Lantern",
prefab_name="Flashlight")`: the copy keeps all the template's components. Find the source
with `search_assets`, then swap the copy's mesh and icon in the prefab editor
(`open_asset_in_uefn`). Only the very first one needs the Content Drawer step above; ask the
person for that one click instead of saying it can't be done.

## Hold pose (43.00)

`held_item_template` now ships a **`fort_item_owner_pose_modifier_component`**
(`/Fortnite.com/Itemization`, `class<final>`, not experimental). It sets the stance
the character uses while the item is equipped. Default: **fire torch**. Pick the pose
in the prefab editor (component → `EquippedPose`) or change it at runtime:

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
only these five. Compiled 0 errors / 0 warnings in 43.00.

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
            # 43.00: Lantern is a subclass of held_item_template, so held_item_template[E] casts work.
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

## Also new in 42.30 (weapons)

`fort_trace_weapon_component` gained two editable toggles with setters:
`AllowAimDownSightsInAir` / `SetAllowAimDownSightsInAir(Val:logic)` and
`AllowAimDownSightsDuringReload` / `SetAllowAimDownSightsDuringReload(Val:logic)`.

42.30 fixes that matter here: equipping an item from Verse no longer leaves the
player unable to aim or shoot, and `RemoveItemEvent`'s `RemovedAmount` is no
longer always 0.
