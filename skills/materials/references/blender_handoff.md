---
description: "Rebuild Blender Principled materials in UEFN after FBX — slot order, value mapping, what never survives export, checklist"
metadata:
  order: 7
  label: "Blender → UEFN materials"
  default_enabled: false
  load_condition: "User exported from Blender, materials look wrong in UEFN, asks to rebuild Principled BSDF, FBX materials missing, or Blender handoff"
---

# Blender → UEFN material handoff

FBX/glTF **does not** bring Blender node graphs into UEFN. Expect slots + maybe
embedded textures; **rebuild** with the materials pack. Blender side:
`skill_read_subskill("blender", "materials_shading")` and `uefn_export`.

## What survives vs dies

| Survives (sometimes) | Dies |
|----------------------|------|
| Mesh material **slots** / names | Principled node graph |
| Texture file paths if packed/copied | Complex Mix / procedural noise |
| Rough order of slots | Exact IOR / transmission setups |
| Simple BaseColor constants (unreliable) | Geometry Nodes materials |

Always: import textures separately (`texture_import`) → build `M_`/`MI_`
(`pbr_master_instances`) → `assign_material_to_mesh`.

## Principled → UEFN mapping

| Blender Principled (4.x) | UEFN material input |
|--------------------------|---------------------|
| Base Color | Base Color (sRGB texture or constant) |
| Metallic | Metallic (scalar or ORM.B) |
| Roughness | Roughness (scalar or ORM.G) |
| Normal Map → Normal | Normal (linear) |
| Alpha / clip | Opacity Mask + Masked blend |
| Emission Color * Strength | Emissive Color * strength scalar |
| Specular IOR Level | Usually leave default; don't chase Blender specular |
| Transmission / SSS | Approximate or skip — UEFN node limits |

Socket names in Blender change across versions — list inputs if a script fails.
In UEFN, stay on nodes from `list_uefn_material_expression_classes`.

## Slot order checklist

1. In Blender: name materials `MAT_*`, one logical surface per slot; apply before export.
2. Export FBX with materials; copy `T_*` textures beside the FBX.
3. `import_asset` mesh → `get_static_mesh_info` / material slot list.
4. Import each texture with correct color space (`texture_import`).
5. Create `MI_` from project master (or new `M_` if needed).
6. `assign_material_to_mesh` per `slot_index` — **match Blender slot order**.
7. `recompile_material` → save assets → `save_current_level()`.
8. Screenshot in-editor; fix plastic/wash with roughness/metal/sRGB table.

## Golden path (agent)

```
import_asset(mesh) + import_asset(textures)
get_static_mesh_info / get_material_info
create_material_instance or create_material
set_material_instance_texture / _scalar / _vector
assign_material_to_mesh({"slot_index": 0, ...})
recompile_material → save → save_current_level()
take_high_res_screenshot / assign verify
```

If import created stub materials: replace them — don't fight broken auto materials.

## Don'ts

- Don't expect Blender Mix/Noise trees to appear in UEFN.
- Don't assign one material to all slots when Blender had three.
- Don't leave textures as sRGB normals.
- Don't skip level save after assign (island keeps old look).

## Related

- `texture_import`, `pbr_master_instances`, `creating_materials`
- Mesh import → modeling `fbx_import_pipeline`
- Blender export → `uefn_export` / `skeletal_export`
