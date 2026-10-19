---
description: "Prepare scans/sculpts in Blender for Mesh to MetaHuman and UEFN import"
metadata:
  label: "Blender prep for MetaHuman"
  default_enabled: false
  load_condition: "Cleaning a scan or sculpt in Blender before Mesh to MetaHuman"
---

# Blender prep for Mesh to MetaHuman

Mesh to MetaHuman accepts FBX/OBJ at MetaHuman scale. Clean input → better
Identity fit → less likeness cleanup in Creator.

## Checklist before export

1. **Units / scale** — work in meters; adult human ~1.7–1.9 m. Fortnite characters
   are ~1.9 m tall — keep heads proportional.
2. **Pose** — neutral face; body between A-pose and T-pose on recent MH versions
   (strict A-pose on older). Apply transforms (location/rotation/scale).
3. **Topology** — watertight-ish head; close mouth holes if the solver needs a
   continuous surface. Extreme stylization will be pulled toward photoreal.
4. **Single subject** — one head (or head+body) mesh; remove scan junk, floor,
   clothing you do not want conformed unless intentional.
5. **Export** — FBX or OBJ; for MH topology round-trips enable habits that
   preserve UVs (Match Vertices by UVs on reimport).

## Topology ceilings (reference)

See blender skill refs (do not invent denser “hero” meshes than UEFN needs):

- `skill_read_subskill("blender", "face_topology")` — MH head LOD table
- `skill_read_subskill("blender", "body_anatomy")` — MH body LOD verts
- Clothing/skinning notes: `character_clothing`

## Import into UEFN

1. `get_project_info()` → `content_root`, then `import_asset` / Content Browser
   into e.g. `{content_root}MetaHumanSource/` — never invent `/Game/MetaHumanSource/`.
2. Mesh to MetaHuman — `mesh_to_metahuman`.
3. Creator refine → Assemble UEFN → `npc_spawn`.

## Agent tools

- Blender MCP (`blender_*`) for cleanup when the Blender plugin is enabled.
- Modeling skill for FBX import options:
  `skill_read_subskill("modeling", "fbx_import_pipeline")`.
- After UEFN import: `get_static_mesh_info` / `get_skeletal_mesh_info` before
  starting Identity.
