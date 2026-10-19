---
description: "Mesh to MetaHuman — Identity from mesh, video, or template; likeness drift; UV match"
metadata:
  label: "Mesh to MetaHuman"
  default_enabled: true
  load_condition: "Converting a scan, sculpt, or custom head/body mesh into a MetaHuman Identity"
---

# Mesh to MetaHuman

Turn a custom head/body (scan, sculpt, GenAI mesh, DCC export) into a
**MetaHuman Identity**, then refine in Creator and Assemble with **UEFN Export**.

Enable **MetaHuman Animator** and **MetaHuman Animator Depth Processing** for
depth/video identity paths.

## Input types

| Source | Notes |
|--------|--------|
| **From Mesh** | Static or skeletal mesh (FBX/OBJ). Neutral expression for heads. |
| **From Video** | Depth / performance footage → Neutral Pose + markers → Identity Solve |
| **From Template** | Source already on MetaHuman topology / UV layout — cleaner fit |

## From Mesh (typical)

1. Import the mesh into the project (`import_asset` or Content Browser). Prep
   scale/pose in Blender first — `blender_prep`.
2. Open **Mesh to MetaHuman** on that mesh (Creator / Identity tools).
3. Track markers on the Neutral Pose; adjust control points if the auto tracker
   misses features.
4. **Identity Solve** fits template topology to the target volume (local).
5. Cloud backend creates the MetaHuman Identity → open as a starting
   `MetaHuman Character` in Creator.
6. Sculpt/materials as needed — expect **likeness drift** (distinctive features
   pull toward the database average). Plan manual head work after fit.
7. Assemble with **UEFN Export** — `assemble_uefn_export`.

## From Template (MetaHuman topology)

Use when the source already uses MetaHuman topology or standard MH UVs
(e.g. FBX round-trip). **Mesh Fit** builds a MetaHuman-standard rig; **Replace**
updates body/head verts on an existing character.

If vertex order changed after DCC export/import (triangulation), enable
**Match Vertices by UVs**.

## Key concepts

| Term | Meaning |
|------|---------|
| Neutral Pose | Mesh of the face at rest |
| Tracker / Markers | Curves on facial features; drag control points to fix |
| Identity Solve | Fit template mesh to target (local) |
| Template Mesh | Standard topology head inside the Identity asset |
| MetaHuman Backend | Cloud step that builds the MetaHuman from the fitted template |

## Agent rules

- Do not invent landmark positions — guide the user in the Identity UI.
- After Identity exists, `metahuman_list` / `metahuman_get_info` to find the
  Character asset path.
- Body-only or full-body conform depends on engine version (combined head+body
  conform on newer MH releases). If body fit fails, assemble head-first then
  wardrobe, or use Creator body sliders.

## Next

`creator_edit` → `assemble_uefn_export` → `npc_spawn`
