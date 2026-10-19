---
description: "MetaHuman Creator in UEFN — presets, body/head edit modes, materials, wardrobe, Influence Circle"
metadata:
  label: "MetaHuman Creator edit"
  default_enabled: true
  load_condition: "Editing a MetaHuman Character asset in Creator before Assemble"
---

# MetaHuman Creator — edit in UEFN

Creator lives **inside the editor** (UE 5.6+ / current UEFN). There is no
browser-streamed Creator session for new characters. Autorig + texture
synthesis still need network access to Epic’s backend.

## Prerequisites

1. Epic Launcher → UEFN/engine install → Options → enable **MetaHuman Creator
   Core Data**. Without Core Data, Creator opens but **skin editing is disabled**.
2. `Edit → Plugins` → enable **MetaHuman Creator** (and related MetaHuman
   Character / Character Editor plugins your build lists). Restart the editor.
3. Optional: **MetaHuman Animator** (+ Depth Processing) for face capture.

## Create a character asset

```
Content Browser → right-click → MetaHuman → MetaHuman Character
```

Opens Creator with panels roughly:

| Panel | Use |
|-------|-----|
| **Presets** | Drag a starting identity into the viewport |
| **Body** | Height, weight, proportions (Shape vs Skeleton mode) |
| **Head** | Blend / Conform / Transform / Sculpt |
| **Materials** | Skin, eyes, makeup, freckles |
| **Wardrobe** | Clothing sets (Fab library grows over time) |
| **Assembly** | Rig, textures, export pipeline — see `assemble_uefn_export` |

## Body modes

- **Shape mode** — keep skeleton proportions compatible with shared anim
  libraries; vary silhouette/shape. Prefer for a roster that shares locomotion.
- **Skeleton mode** — shift proportions (age/fitness variants) while keeping a
  related silhouette. Retarget carefully afterward.

## Head: Influence Circle

Drag other `MetaHuman Character` assets onto the Influence Circle. Place
influences and blend with the control point. **Sculpts accumulate** — returning
the blend point to center does **not** undo earlier work. Save named iterations
(`MH_<Name>_v1`, `_v2`) as you go.

## Materials & wardrobe

Tune skin tone, eyes, makeup in Materials. Wardrobe applies clothing sets;
custom dynamic cloth (Marvelous / CLO USD) is a separate advanced pipeline —
out of scope for the basic UEFN NPC path. Prefer wardrobe sets that already
assemble cleanly for UEFN Export.

## What agents should do

- Guide the user through Creator UI for sculpt/blend/wardrobe (no thin MCP
  sculpt tools).
- After edits, run `metahuman_list` / `metahuman_get_info` only once assets exist
  on disk (post-assemble or for the Character asset path).
- Never claim Assemble succeeded without UEFN Export (or a successful
  `metahuman_assemble_uefn` when capabilities allow).

## Next

`skill_read_subskill("metahuman", "assemble_uefn_export")`
