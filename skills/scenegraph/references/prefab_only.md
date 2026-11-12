---
description: "Prefab-only hard rules — never mutate level instances; edit prefab contents over MCP (PrefabToolset rootEntity + EntityToolset, ApplyPrefabEdits); banned create_prefab_from_entities on instances; transform+KFM orbits; Verse module collisions"
metadata:
  order: 4
  label: "Prefab-only editing"
  default_enabled: false
  load_condition: "Editing EntityPrefabs, solar-system / orbit hierarchies, avoiding level-instance overrides, or packaging entities into prefabs"
---

## Prefab-only editing (hard rules)

**Edit the EntityPrefab asset — never the placed level instance as the source of truth.**

Mutating a level `EntityProxyActor` / prefab instance creates **instance overrides**
(or wrecks the tree). Do not move `Body_*`, attach meshes, or add Verse components
on the level copy as the primary workflow for prefab-owned content.

### Prefab changes

- **Live edit for entity prefab assets:** saving a change to a prefab asset updates every
  instance in the running session — edit the asset, not the instances, and watch it apply.
- Editor no longer wraps entities in proxy actors; "level instance" below means the placed
  prefab entity.
- Prefabs whose parent is a template/class subclass it in Verse (`custom_weapons`).
- Asset redirectors work with Verse and prefabs: rename/move an asset or run Fix Up
  Redirectors and references in prefabs stay valid (UEFN keeps a redirector still in use).
- Undoing a deleted component no longer breaks Live Edit.
- The **Scene Graph feature example** is the reference: the UFO keeps its whole
  abduction beam in one component, the beam is its own prefab nested under the UFO, and the
  prefab-spawn sample uses an `@editable` entity for the spawn point. Nest reusable parts as
  their own prefabs the same way.

### Editing the prefab asset over MCP

The prefab asset is editable directly — no prefab editor tab, no UI:

1. `ValkyrieToolset.PrefabToolset` `GetPrefab` `{"prefab": {"refPath":
   "/<Proj>/Prefabs/EP_X.EP_X"}}` (or `CreatePrefab`) → `rootEntity`
   (`/<Proj>/Prefabs/EP_X.Default__EP_X_C`).
2. `ValkyrieToolset.EntityToolset` on that root: `FindEntities` with
   `rootEntity` (children), `GetComponents`, `AddComponent`,
   `RemoveComponent`, `SetComponentProperty`, `CreateEntity` with
   `parentEntity` (required inside a prefab), `SetEntityTransform` (relative
   to the prefab root).
3. `PrefabToolset` `ApplyPrefabEdits` (placed copies update only after this;
   not undoable), then `save_asset` on the prefab yourself.

- A prefab made from a template (`CreatePrefab` `parentClass`, e.g.
  `held_item_template`) already carries the template's components — set
  values, don't re-add them.
- Do **not** “fix it on the level instance instead” when the user asked for
  prefab-only edits. Instance drift: `PrefabToolset` `GetPrefabOverrides` /
  `ResetPrefabInstance`.
- Never tell the user to open the prefab and edit it in the Details panel
  unless an MCP call above failed twice — then name the call and its error.

### Banned / dangerous ops

| Never | Why |
|-------|-----|
| `create_prefab_from_entities` on an already-placed `EP_*` instance | Can collapse children into an empty shell (lost hierarchy). |
| Moving/editing `Body_*` / pivots only on the level instance | Instance overrides; other instances and the asset diverge. |
| Treating level EntityToolset `FindEntities` results as the prefab asset | You are editing the instance, not the definition. |

### Allowed packaging

- `create_empty_prefab` — blank asset under the project mount; nothing placed.
- `create_prefab_from_entities` — only on **loose** level entities (not an existing
  prefab instance), into a **new** `prefab_name` (path must not already exist).
  Sources become an instance of the new prefab.
- `instantiate_prefab` — place always-on copies in the level (Content Browser drag
  equivalent). Call `save_current_level` after place.

### Place vs runtime spawn

| Goal | Path |
|------|------|
| Always-on / match-start | Prefab asset + `instantiate_prefab` + `save_current_level` |
| Runtime spawn/despawn | Verse `P_*{}` + `Sim.AddEntities` / `RemoveFromParent` after Verse rebuild |

### Presentable-to-players

`SetPresentableToPlayers(Players:?[]player)` (and `GetPresentableToPlayers`)
works on **named child entities inside a prefab**, including runtime-spawned
prefabs. False / empty option = presentable to everyone; an array = only those
players (empty array = nobody). Dynamically spawned prefab children are
client-relevant **only when relevant** — they are not always added to the
client sim, so visibility is not a substitute for not spawning them.

---

## Orbit / motion recipe (prefab hierarchy)

Typical solar-system style tree (owned by the prefab):

```
EP_SolarSystem
  Sun                    (mesh)
  Pivot_Earth            (transform + constant_rotation / KFM)
    Body_Earth           (mesh + local Forward offset = orbit radius)
    Earth_Anchor
      Pivot_Luna         (transform + KFM)
        Body_Luna        (mesh + offset)
```

Rules:

1. **Pivots need `transform_component`.** Without it, EntityToolset `FindEntities` shows
   `local_transform_error` and KFM cannot orbit children.
2. Put orbital radius on the **body** local translation; rotate the **pivot**.
3. Motion = `keyframed_movement_component`. The class is `<final>`, so a
   project `constant_rotation_component` **holds** one — it cannot extend it.
   Loop yaw with `loop_keyframed_movement_playback_mode`. Translation/Scale
   deltas additive (`0` = no change).
4. In Verse, before KFM: if no transform, call `SetLocalTransform` (creates
   `transform_component` on demand). Position the entity **before**
   `SetKeyframes` — it rebases onto the current transform — and remember
   `SetKeyframes` does not autoplay, so call `Play()`.
5. Attach custom Verse comps to the **prefab asset** after a Verse build —
   EntityToolset `AddComponent` on the prefab's entity
   (`/<Proj>/_Verse.Verse-<Module>-<class_name>`). Runtime AddComponents from a
   root component is OK if the root component lives on the prefab definition.
6. Components simulate in the editor as well as in play. If the orbit is still,
   walk the checklist in
   `skill_read_subskill("scenegraph", "movement_transforms")` and confirm in
   PIE / Launch Session.

---

## Verse module name collision

Do **not** put gameplay Verse under `Content/Verse/<Name>/` when
`Content/<Name>/` already owns Assets module `<Name>` (e.g. content folder
`SolarSystem` → Assets `SolarSystem` module). The Verse types may not resolve as
editor/project components.

Use a distinct folder/module (e.g. `Content/Verse/SolarOrbits/`).

Project component object path after compile often looks like:

`/<Project>/_Verse.Verse-<Module>-<class_name>`

---

## Checklist before claiming “prefab updated”

1. Changes are on the EntityPrefab asset (or explicitly applied to source), not
   only a level override.
2. `ApplyPrefabEdits` ran and the prefab asset is saved (`save_asset`).
3. If Verse comps were added: Verse build succeeded; class visible to attach.
4. Pivots that move have `transform_component`, and KFM had `Play()` called.
5. User verified in **PIE / Launch Session** for runtime motion.
