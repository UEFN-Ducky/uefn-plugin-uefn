---
source_plugin_id: metahuman
name: metahuman
description: "MetaHuman for UEFN — create and edit in MetaHuman Creator, Mesh to MetaHuman, assemble with UEFN Export, import/migrate from UE, wire NPC Spawner, face/body animation, LOD/groom performance"
license: MIT
metadata:
  label: UEFN MetaHuman
  version: 7
  managed_by: uefn-ducky
  author: UEFN-Ducky
  copyright: Copyright 2026 Mindful Path Company, LLC
  allow_redistribute: true
---

# MetaHuman for UEFN — create, assemble, spawn

**CRITICAL — editor mutations are SERIAL:** one heavy MCP call (`spawn_actor`,
`wire_verse_device_ref`, `save_current_level`, …) → wait → next. Never parallel
or same-turn multi. Details: SERIAL: one mutating/editor call per assistant message..

MetaHumans are **high-fidelity digital human NPCs** in UEFN. Author in the
in-editor **MetaHuman Creator** (cloud Creator / Quixel Bridge for *new*
characters is obsolete), assemble with the **UEFN Export** pipeline, then
attach to an **NPC Spawner**. Do not use the full-UE Cinematic/Optimized
assemble path for Fortnite islands.

## Decision tree

| Goal | Path |
|------|------|
| New face/body from presets | Creator → edit → Assemble **UEFN Export** → NPC |
| Scan / custom head or body mesh | Mesh to MetaHuman → Creator refine → Assemble UEFN |
| Already have a MetaHuman in a UE project | Re-assemble with UEFN Export **or** migrate UEFN-built assets |
| Stylized / non-human / old UE4 pack | **Not** MetaHuman — use `skill_read_subskill("animation", "npc_characters")` |
| Face performance capture | MetaHuman Animator / Live Link / audio — see `animator_face` |
| Body locomotion for the NPC | MH IK Retargeter + `skill_read_subskill("animation", "retargeting")` |
| Custom anims + Verse AI (turn / chase / act) | `npc_spawn` + animation `retargeting` / `anim_authoring` + verse `sys_npc_ai` |

## MCP tools (this plugin)

| Kind | Tools |
|------|-------|
| **PROBE** | `metahuman_capabilities` — always first before assemble |
| **READ** | `metahuman_list`, `metahuman_get_info`, `metahuman_can_assemble` |
| **ASSEMBLE** | `metahuman_assemble_uefn` — only when capabilities.available |

Creator sculpt, Influence Circle, wardrobe, and Mesh-to-MH landmark UI are
**editor steps** — this skill documents them; tools do not fake those UIs.
If `metahuman_capabilities` says `available: false`, use Assembly → UEFN Export
in the editor (`skill_read_subskill("metahuman", "assemble_uefn_export")`).

## Golden path (preset character)

1. Enable **MetaHuman Creator** (+ **Animator** if capturing). Install
   **MetaHuman Creator Core Data** in Epic Launcher options — without it, skin
   editing is disabled.
2. Content Browser → right-click → **MetaHuman → MetaHuman Character**.
3. Edit body / head / materials / wardrobe — see `creator_edit`.
4. Assembly: **Create Full Rig** → download texture sources → **Assemble** with
   pipeline **UEFN Export** (not UE Optimized). See `assemble_uefn_export`.
5. Optional: `metahuman_list` / `metahuman_get_info` to verify
   `Content/MetaHumans/<Name>/` Blueprint + meshes.
6. Build `NPCCharacterDefinition` + place `npc_spawner_device` — see `npc_spawn`
   and animation `npc_characters`.
7. `save_current_level`.

## Golden path (custom mesh)

1. Import mesh (FBX/OBJ) — prep in Blender: `blender_prep` + modeling FBX skill.
2. Mesh to MetaHuman → Identity → open in Creator — `mesh_to_metahuman`.
3. Same Assemble UEFN + NPC steps as above.

## Golden path (Verse NPC that turns / acts)

```
Assemble UEFN Export
  → physics asset on MH skeletal mesh
  → retarget or author body clips (all on the SAME skeleton)
  → AnimPreset_BasicLocomotion (idle / run)
  → NPCCharacterDefinition + CharacterModifier_VerseBehavior
  → npc_spawner_device
  → npc_behavior: MaintainFocus / NavigateTo / PlayAndAwait(Clip)
```

Details and gotchas: `skill_read_subskill("metahuman", "npc_spawn")`.
Verse AI loops: `skill_read_subskill("verse", "sys_npc_ai")`.
Custom clip authoring: `skill_read_subskill("animation", "anim_authoring")`.
Retarget Mannequin → MH: `skill_read_subskill("animation", "retargeting")`.

## Detail references

Load with `skill_read_subskill("metahuman", "<id>")`:

| id | Topic |
|----|--------|
| `creator_edit` | Presets, body/head modes, materials, wardrobe, Influence Circle |
| `mesh_to_metahuman` | From mesh / video / template; likeness drift; UV match |
| `assemble_uefn_export` | Rig → textures → Assemble UEFN; Python assemble tool |
| `ue_to_uefn_migrate` | Reuse UE MetaHumans; Windows-only notes |
| `npc_spawn` | Blueprint → physics → AnimPreset → NPCDef → Verse AI → spawner |
| `animator_face` | Animator, Live Link, audio; Fortnite Character Device |
| `lod_groom_perf` | LODSync, grooms, island memory |
| `blender_prep` | Scan/sculpt prep for Mesh to MetaHuman |

## Cross-skills

- Body anim retarget / sockets: `skill_read_subskill("animation", "retargeting")`
- Custom NPC definitions (non-MH packs): `skill_read_subskill("animation", "npc_characters")`
- Author new AnimSequences / Level Sequences: `skill_read_subskill("animation", "anim_authoring")`
- Verse `npc_behavior` turn/chase/attack: `skill_read_subskill("verse", "sys_npc_ai")`
- Face/body topology ceilings: blender `face_topology` / `body_anatomy`
- Mesh import: `skill_read_subskill("modeling", "fbx_import_pipeline")`

## Hard limits (do not fight the framework)

- **Children / heavy stylization / crowds** — MetaHuman is photoreal humanoids;
  use other character pipelines for stylized packs and crowd impostors.
- **Playable Fortnite player pawns** — MetaHumans are for **NPCs** (and Animator
  can drive Fortnite characters on the Character Device), not a swap-in player mesh.
- Never invent DNA / bone names — read from `get_skeletal_mesh_info` /
  `list_skeleton_bones` after assemble.

## Verify

`metahuman_get_info` after assemble.
