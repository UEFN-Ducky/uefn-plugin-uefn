---
description: "Assemble MetaHuman with UEFN Export pipeline — Full Rig, textures, Python assemble tool"
metadata:
  label: "Assemble UEFN Export"
  default_enabled: true
  load_condition: "Assembling a MetaHuman Character for use in UEFN / Fortnite islands"
---

# Assemble — UEFN Export pipeline

Assembly turns a `MetaHuman Character` into runnable assets: Blueprint, body/face
skeletal meshes, materials, grooms, LODSync, AnimBP, IK retargeter under
`Content/MetaHumans/<Name>/` (path may vary slightly by build).

**Always choose UEFN Export** (sometimes labeled “UEFN”) — not UE Optimized or
Cinematic. Fortnite memory budgets depend on the UEFN LOD/texture/groom cut.

## UI steps (canonical)

1. Open the MetaHuman Character → **Assembly** panel.
2. **Create Full Rig** (cloud autorigger; sign in with Epic account if prompted).
3. **Download Texture Source** — pick resolution appropriate for islands
   (prefer lower than cinematic 8K unless a single hero close-up).
4. Select pipeline **UEFN Export**, quality, save location, name.
5. **Assemble** — wait for assets to write. Drag the character Blueprint into a
   level to preview.
6. Persist: save assets / `save_current_level`.

If Assemble is greyed out: confirm Full Rig + textures finished; some builds need
switching away from Assembly and back to refresh the button.

## Python / MCP assemble

```
metahuman_capabilities()          # available must be true
metahuman_can_assemble(path)      # ready / can_build
metahuman_assemble_uefn(path, quality="medium")
```

Uses `MetaHumanCharacterEditorSubsystem.build_meta_human` with
`pipeline_type=UEFN` when the editor exposes it. Character must be open for edit
on some builds (the tool best-effort opens the asset editor).

If `available` is false or assemble fails:

- Fall back to the Assembly UI above.
- Preview builds of MetaHuman sometimes **disable** UEFN Export until a matching
  UEFN version — assemble in a supported pair of engine/UEFN builds, then migrate
  assets (`ue_to_uefn_migrate`).

## Verify

```
metahuman_list(directory="/Game/MetaHumans")   # or {content_root}MetaHumans — omit directory to scan the project mount
metahuman_get_info(asset_path="...")   # expect Blueprint / LODSync / Groom comps
get_skeletal_mesh_info(...)            # body/face meshes after assemble
```

## Next

`npc_spawn` for island placement; `lod_groom_perf` before shipping many MH NPCs.
