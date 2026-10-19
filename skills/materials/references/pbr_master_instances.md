---
description: "Master M_ + MI_ instance PBR pattern — Scalar/Texture parameters via registry tools, ORM, masked foliage, two-sided, emissive, 500-instruction budget"
metadata:
  order: 6
  label: "PBR master & instances"
  default_enabled: false
  load_condition: "User wants a reusable master material, material instances, parameters, ORM PBR setup, foliage masked, two-sided, or emissive glow materials"
---

# PBR master materials + instances

Author **one** master `M_` with parameters; ship variants as `MI_`. Keeps you under
Epic's **≤ 500 instructions** per material and matches Fortnite content style.

## Pattern

```
M_Prop_Master          ← graph + parameters (edit rarely)
  MI_Prop_Wood
  MI_Prop_Metal
  MI_Prop_Paint_Red
```

```
# folder = get_project_info().content_root + "Materials" — never /Game/Materials
create_material({"asset_name": "M_Prop_Master", "folder": "/MyProject/Materials"})
# add TextureSampleParameter / ScalarParameter / VectorParameter via registry…
create_material_instance({"parent_material_path": "/MyProject/Materials/M_Prop_Master",
                          "asset_name": "MI_Prop_Wood",
                          "folder": "/MyProject/Materials/Instances"})
set_material_instance_texture({...})
set_material_instance_scalar({...})
set_material_instance_vector({...})
recompile_material({"material_path": "/MyProject/Materials/M_Prop_Master"})
assign_material_to_mesh({... "material_path": ".../MI_Prop_Wood"})
save_current_level()
```

Prefer registry tools (`add_material_expression`, `connect_material_nodes`,
`set_material_expression_property`). Probe classes:
`list_uefn_material_expression_classes`.

## Recommended parameters (master)

| Parameter | Type | Drives |
|-----------|------|--------|
| `BaseColorTex` / `BaseColor` | Texture / Vector | Albedo |
| `ORM` or `Roughness` / `Metallic` / `AO` | Texture / Scalar | PBR data |
| `NormalTex` | Texture | Tangent normal |
| `EmissiveTex` / `EmissiveColor` / `EmissiveStrength` | Texture / Vector / Scalar | Glow |
| `OpacityMask` | Texture / Scalar | Masked cutout |
| `Tint` | Vector | Multiply on BaseColor for cheap variants |

Wire: BaseColor → Base Color; Normal → Normal; ORM.G → Roughness; ORM.B → Metallic;
ORM.R multiply into BaseColor (optional); OpacityMask → Opacity Mask when blend is Masked.

## Flags (`set_material_flags`)

| Use | Blend | Two-sided | Notes |
|-----|-------|-----------|-------|
| Solid prop | Opaque | no | Default Lit |
| Foliage / cards | **Masked** | **yes** often | Opacity Mask + clip |
| Glass / soft glow | Translucent | maybe | Costly; sparingly |
| Neon sign | Opaque + Emissive | no | EmissiveStrength |

After flags: `recompile_material` → save → `save_current_level()`.

## Recipes (short)

**Metal prop** — high Metallic (0.8–1), low Roughness (0.2–0.4), cool BaseColor.

**Painted wood** — Metallic 0, Roughness 0.5–0.8, tinted BaseColor, subtle Normal.

**Masked foliage** — Masked + Two-Sided; OpacityMask from alpha or `_Msk`; keep instruction
count low (no heavy noise stacks).

**Emissive accent** — small EmissiveColor * Strength; don't replace all lighting
(see leveldesign `lighting`).

**Quality tiers** — prefer `QualitySwitch` / Fortnite quality material attributes when
available (`list_uefn_material_expression_classes`); keep BR tiers lean.

## Instance discipline

- Change **parameters on `MI_`**, not duplicate masters per color.
- One master per domain (props / characters / trim) beats one mega-master with 80 params.
- If graph exceeds ~500 instructions: split or bake complexity into textures
  (`texture_import`, Blender `texture_bake`).

## Don'ts

- Don't ship Unique material graphs per crate color — use `MI_` + Tint.
- Don't use Custom/HLSL nodes (blocked in UEFN).
- Don't assign the master to every mesh if instances exist — assign `MI_`.
- Don't skip recompile + level save.

## Related

- Texture settings → `texture_import`
- Blender rebuild → `blender_handoff`
- Node recipes → `creating_materials`
- Runtime swap → `runtime_materials_verse`
