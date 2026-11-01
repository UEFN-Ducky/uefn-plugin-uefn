---
description: "Full Scene Graph builtin component catalog — mesh/asset vs plain, BasicShapes, lights (one per entity), KFM, interactable (no button_component), itemization components, project Verse class paths, 43.00 hold interactions (OnStarted at hold start, completion in SucceededEvent, Cooldown with duration), entity damage"
metadata:
  order: 3
  label: "Component catalog"
  default_enabled: false
  load_condition: "Attaching or explaining entity components, mesh/light/sound/particle assets, interactables, hold to interact, long press, OnStarted (rolled back / runs too early), SucceededEvent, interaction cooldown, keyframed movement, or project Verse component class paths"
---

## Scene Graph component catalog

Always probe the live build first:

```
scene_graph_capabilities({})
unreal__describe_toolset({"toolset_name": "ValkyrieToolset.EntityToolset"})   # component/class listing + AddComponent live here
```

Kinds reported by the EntityToolset component listing:

| Kind | Meaning |
|------|---------|
| `builtin` | Engine aliases (`mesh_component`, …) |
| `project` | Your Verse `*_component` classes after Verse build |
| `asset_generated` | Digest classes for project meshes/particles/sounds |

**One component per subclass _group_**, not per class — re-adding returns the
existing one. The digest's own example is lights: `spot_`, `sphere_`, `rect_`,
`capsule_` and `directional_light_component` all derive from `light_component`,
so an entity can hold **one light in total**. Two lights = two entities.

**Property names** are case-sensitive Verse digest names (`Visible`, `Collidable`).
Check with `get_verse_api({"name": "<component>"})`. Never pass mangled
`__verse_0x...` names to tools.

There is **no** Scene Graph `button_component`. Player interaction uses
`interactable_component` / `basic_interactable_component`. Creative
`button_device` is a **device**, not an entity component — wire it with device
tools, not Scene Graph.

#### Interactables in 43.00 (behavior change)

- **Hold interactions:** on a `basic_interactable_component` with an
  `InteractableDuration`, `OnStarted` now runs **when the hold starts** and
  `StartedEvent` fires once per hold. (Before 43.00 it ran when the hold finished, the
  base call rejected it and your override was rolled back.) **Completion logic belongs
  in `SucceededEvent`** — if you moved it into `OnStarted` or forced `Succeed[]` from
  there as a workaround, it now fires at the *start* of the hold: move it and delete the
  workaround.
- `Cooldown` now runs when an `InteractableDuration` is also set (was skipped).
- `interaction_component.Disable()` no longer leaves an interaction prompt visible.
- With a Scene Graph camera active, interacting can be harder (known issue) — add a
  **Third Person Controls** device next to the camera (`cameras`).

```verse
# 43.00 pattern: start feedback in StartedEvent, the reward in SucceededEvent.
Interactable.StartedEvent.Subscribe(OnHoldStarted)       # e.g. play a charge VFX
Interactable.SucceededEvent.Subscribe(OnHoldCompleted)   # grant / open / score here
Interactable.CanceledEvent.Subscribe(OnHoldCanceled)     # stop the VFX
```

#### Other 43.00 component changes

- **Adding a component that already belongs to another entity logs a warning** (an
  error in a future release). Call `Component.RemoveFromEntity()` first, or construct a new
  component — never share one instance between entities.
- Component queries (`FindEntitiesWithComponent`, `FindDescendantComponents`,
  `FindComponents`) no longer miss components added/removed during lifetime functions
  (`OnAddedToScene`, `OnBeginSimulation`, …) — drop retry/Sleep-then-requery workarounds.
- `Enable()` on `sound_component` / `particle_system_component` no longer starts playback
  when AutoPlay is off — call `Play()` explicitly.
- `description_component` text from the server is no longer ignored.
- `SetPresentableToPlayers` behaves consistently across entities with the same component.
- Socket-attached objects (weapons) no longer twitch on clients.
- Built-in Fortnite damage now hits Scene Graph entities (health pipeline — verse
  `sys_health_pipeline`).
- **Handles:** `entity_handle` (`GetEntity[]`), `component_handle(t)` (`GetComponent[]`),
  `mesh_part_handle`; overlap/sweep hits carry `SourceMeshHandle` / `TargetMeshHandle`.
  `mesh_component.CanAffectNavigation` (server-only). Recipe: `movement_transforms` →
  Scene Graph handles.
- `fort_trace_weapon_component.BeginFire()` / `EndFire()` / `IsFiring[]` fire a weapon from
  Verse (`custom_weapons`).

---

### Plain vs asset components

| Kind | Examples | `asset_path` |
|------|----------|--------------|
| **Plain** | transform, mass, lights, KFM, interactable, camera, … | Omit |
| **Asset** | mesh, particle, sound | **Required** — PROJECT mount only (`/MyProject/...`). Never `/Game/...` Fortnite content |

Asset attach creates a **subclass** of the base (e.g.
`SolarSystem-Meshes-SM_Body_Earth` under `mesh_component`). Read/remove by
base alias still works.

That `asset_path` requirement is about the **editor tool**. In Verse you can
skip assets entirely for prototyping: `/UnrealEngine.com/BasicShapes` provides
`cube`, `sphere`, `plane`, `cone` and `cylinder`, each a `mesh_component`
subclass — `Ent.AddComponents(array{sphere{Entity := Ent}})`.

---

### Builtin catalog (from `scene_graph_capabilities`)

#### Pose / physics

| Alias | Role |
|-------|------|
| `transform_component` | Local/global pose. **Required** for mesh placement and any KFM/orbit pivot. Empty pivots report `local_transform_error`. Verse `SetLocalTransform` creates one on demand. |

#### Render / audio / FX (asset)

| Alias | Role |
|-------|------|
| `mesh_component` | Render mesh. Needs PROJECT `asset_path` from the editor tool (or a `BasicShapes` subclass in Verse). It is `class<final_super><epic_internal>` — **creator Verse cannot subclass it**; importing a mesh generates the subclass for you in the project Assets digest (e.g. `SM_Hat01_Cap := class<final>(mesh_component)`), so find custom meshes with `list_verse_types(digest="assets")` and never invent a class name. **Depends on `transform_component`** to be positioned at all. Digest props: `Visible`, `Collidable`, `Queryable`; it is also `enableable` (`Enable()`, `Disable()`, `IsEnabled[]`); overlap events `EntityEnteredEvent` / `EntityExitedEvent`. |
| `particle_system_component` | Particle / Niagara system — PROJECT asset. |
| `sound_component` | Sound — PROJECT asset. |

#### Motion

| Alias | Role |
|-------|------|
| `keyframed_movement_component` | Timed transform animation (orbits, doors, movers). `using { /Verse.org/SceneGraph/KeyframedMovement }`. `SetKeyframes` **rebases onto the current transform and does not autoplay** — then `Play()`. Translation/Scale on deltas are **additive** (`0` = no change). Modes: `oneshot_` / `loop_` / `pingpong_keyframed_movement_playback_mode`. `<final>` — compose, never subclass. Prefer over per-tick `SetGlobalTransform`. **Never** `creative_prop` `animation_controller` for entities. Full API: `movement_transforms`. |

#### Lights

| Alias | Role |
|-------|------|
| `light_component` | Base light |
| `spot_light_component` | Spot |
| `sphere_light_component` | Point / sphere |
| `rect_light_component` | Rect |
| `capsule_light_component` | Capsule |
| `directional_light_component` | Directional |

#### Camera / interaction / gameplay tags

| Alias | Role |
|-------|------|
| `camera_component` | Scene Graph camera — `<abstract>`, place `perspective_` / `orthographic_` / `physical_camera_component` or `camera_director_component`. **Experimental.** `Director.AddCamera[Cam, Priority]` IS `<decides>` (brackets); `Cam.CameraModifiers.AddModifier(Mod, 0)` is NOT (parens). **43.00:** angles in radians (`FieldOfView`, not `FieldOfViewDegrees`); `GlobalModifierPosition`/`VisualModifierPosition` removed — use the director's `PreCameraModifiers` / `PostCameraModifiers` / `PresentationCameraModifiers`; user-written `camera_modifier`s run on the server; play-server known issue. Fortnite modifiers `fort_orbit_camera_modifier` / `fort_fixed_angle_` / `fort_fixed_point_` live in `/Fortnite.com/SceneGraphCameras` (42.00+). Full tables: `skill_read_subskill("scenegraph", "cameras")`. **Transitions (working from v42.10):** override `GetEnterTransition(SourceCamera)` / `GetExitTransition(DestinationCamera)` (both `<transacts><decides>`) on your `camera_component` subclass and return `camera_transition{Blend := camera_mode_blend_smoothstep{}, Duration := 0.5}`. Blends: `camera_mode_blend_pop{}` (instant **cut**), `_linear`, `_smoothstep`, `_smootherstep`, `_orbit{DrivingBlend := …}`. All `<concrete>`, all Experimental (blocks publishing). |
| `interactable_component` | Player interaction surface (not a UI button). `StartedEvent` / `SucceededEvent` / `CanceledEvent`; override `OnStarted` (`<protected>`, `<transacts><decides>`) for custom start behavior |
| `basic_interactable_component` | Composable interactable: `Cooldown`, `CooldownPerAgent`, `SuccessLimit`, `InteractableDuration`, `Succeed[Agent]`, `Cancel[Agent]`. 43.00: `OnStarted` at hold **start** — completion logic in `SucceededEvent` (see above) |
| `possessable_component` | Possession |
| `icon_component` | Editor / UI icon |
| `rarity_component` | Rarity metadata — instances in `/Fortnite.com/Itemization/FortniteRarities` |
| `basic_stackable_component` | Stacking. Merge API: `CanMergeInto[]`, `MergeInto[]`, `AllowMergeInto[]`, `OnMergeInto` |

#### Itemization (`/UnrealEngine.com/Itemization`, `/Fortnite.com/Itemization`)

| Alias | Role |
|-------|------|
| `item_component` | Marks an entity as an item. `GetParentInventory[]`, `IsEquipped[]`, `Equip`, `Unequip`, `Drop[]`, `PickUp[Inventory]`, `Categories`. |
| `inventory_component` | Holds items. `AddItemDistribute` is the grant call; also `AddItem`, `RemoveItem`, `GetItems`, `FindItems`, `GetEquippedItems`, add/remove/equip events. On a player it sits on a **subentity** of the agent. |
| `fort_item_pickup_interactable_component` | World pickup. Owning entity needs `item_component` + `mesh_component`; exposes `GetInteractorInventory(Agent)`. Gated `MinUploadedAtFNVersion := 4040`. Fields from `basic_interactable_component`: `CanInteractMessage`, `CannotInteractMessage`, `Cooldown`, `CooldownPerAgent`, `SuccessLimit`, `InteractableDuration`, `Enable`/`Disable`. |
| `fort_inventory_component` (+ `fort_inventory_*` subclasses) | **Player inventory** types (weapon hotbar, resources, currencies, ammo, …) — not components for custom item prefabs. Custom items use `item_component` (+ optional `Categories`). |
| `fort_item_owner_pose_modifier_component` | 43.00, `/Fortnite.com/Itemization`: hold pose while equipped (fire torch default, flashlight, map, small/large consumable); `SetEquippedPose(option{fort_character_pose_modifier_map{}})`. Ships on `held_item_template` → `held_items` |
| `fort_item_ability_component` | Template abilities on an item (`ItemAbilities` / `ItemEquippedAbilities`, InputTrigger, TargetQuery, AbilityElements). Out of Experimental since 42.40 (publishable). Recipes: `template_abilities`; Verse-authored abilities: `custom_abilities`. |

#### Armory (`/Fortnite.com/Armory`)

| Alias | Role |
|-------|------|
| `fort_trace_weapon_component` | Tunable hitscan weapon (damage, fire rate, spread, recoil, magazine, FX, sounds). All have `Set*` Verse APIs — confirm with `get_verse_api`. |
| `fort_weapon_component` | Base weapon: `IsHolstered`, `HolsterChangedEvent`. |

Custom Armory Entity Prefabs (templates, mesh swap, grant/equip/clear):
`skill_read_subskill("scenegraph", "custom_weapons")`.

Custom non-weapon Entity Prefabs (pickup / description / icon / mesh, KFM spin,
equipped detect): `skill_read_subskill("scenegraph", "custom_items")`.

Template abilities (`fort_template_ability`, status-effect AbilityElements):
`skill_read_subskill("scenegraph", "template_abilities")`.

Recipes and the granting component: `skill_read_subskill("scenegraph", "itemization")`.

Digest may also expose related types (e.g. camera director) — confirm with
`get_verse_api` / `search_verse_digest` before use.

---

### Project Verse components

Custom `*_component` classes appear only **after** Verse compiles. Writing one:
`verse_authoring` (lifecycle, stopping work in `OnEndSimulation`, interfaces for
behaviour several components share).

Resolution order in EntityToolset `AddComponent`:

1. Builtin alias (`mesh_component`, …)
2. Short Verse class name (when listed by the EntityToolset component listing (`unreal__describe_toolset` for the exact tool name))
3. Full object path — often:  
   `/<Project>/_Verse.Verse-<Module>-<class_name>`  
   Example: `/catland/_Verse.Verse-SolarOrbits-constant_rotation_component`

If short name fails, call the EntityToolset component listing (`unreal__describe_toolset` for the exact tool name) (and `reload_listener`
if the list is stale after a Verse relink) — do not invent paths and do not
walk `ObjectIterator` via `execute_python` (freezes the editor).

After EntityToolset `AddComponent`, check `class_path`. A `VERSE_DEAD_*` class under
`/Engine/Transient` is a stale VM class: `reload_listener` → destroy and
recreate the entity → attach again. Details:
`skill_read_subskill("uefn", "verse_build_lifecycle")`.

---

### Mesh attachment recipe

```
unreal__call_tool({
  "toolset_name": "ValkyrieToolset.EntityToolset",
  "tool_name": "AddComponent",
  "arguments": {"entity": "Body_Earth", "component_class": "mesh_component", "asset_path": "/MyProject/Meshes/SM_Body_Earth"}
})
# a mesh with no transform_component is not positioned at all
unreal__call_tool({"toolset_name": "ValkyrieToolset.EntityToolset", "tool_name": "AddComponent", "arguments": {"entity": "Pivot_Earth", "component_class": "transform_component"}})
# argument names: read them from unreal__describe_toolset first — never invent them
```

Put FBX axis offsets on a **child** mesh entity (`SetLocalTransform`); keep the
orbit/heading root clean for KFM yaw. Motion troubleshooting:
`skill_read_subskill("scenegraph", "movement_transforms")`.
