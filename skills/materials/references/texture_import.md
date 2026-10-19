---
description: "Texture import for UEFN — sRGB vs linear, normal compression, ORM packing, import_asset settings, washed-out / plastic failure table"
metadata:
  order: 5
  label: "Texture import"
  default_enabled: false
  load_condition: "User imports textures, maps look wrong (washed out, plastic, inverted normals), asks about sRGB, ORM, compression, or texture settings after FBX/PNG import"
---

# Texture import — maps that actually shade

Wrong texture settings are the #1 cause of "plastic / washed out / inverted bumps"
after Blender or Marketplace import. Fix maps before authoring complex graphs.

## Naming

| Map | Prefix | Typical file |
|-----|--------|--------------|
| Base Color / Albedo | `T_…_BC` or `_D` | PNG/TGA |
| Normal | `T_…_N` | PNG/TGA |
| ORM (AO+Rough+Metal) | `T_…_ORM` | packed RGB |
| Roughness alone | `T_…_R` | grayscale |
| Metallic alone | `T_…_M` | grayscale |
| Ambient Occlusion | `T_…_AO` | grayscale |
| Emissive | `T_…_E` | color |
| Opacity / Mask | `T_…_Msk` | grayscale |

Paths under `{content_root}Textures/...` (e.g. `/MyProject/Textures/...`).

## Import

```
# FIRST: get_project_info() → content_root (e.g. /MyProject/)
import_asset({"source_file": "C:/art/T_Crate_BC.png",
              "destination_path": "/MyProject/Textures"})
# or omit destination_path / pass "" and let the listener auto-pin
get_asset_info({"asset_path": "/MyProject/Textures/T_Crate_BC"})
save_asset / save_directory → save_current_level()
```

Import is not durable until saved. After batch imports: `fixup_redirectors` if
you moved/renamed.

Confirm texture properties with `get_asset_info` / `execute_python` +
`Texture` / `Texture2D` APIs (`uefn_editor_python_hints` first). Don't assume
sRGB from the filename.

## Color space rules

| Map | sRGB / color space | Notes |
|-----|--------------------|-------|
| Base Color, Emissive | **sRGB** (yes) | Albedo is color data |
| Normal | **Linear / Non-Color** | Never sRGB — purple looks wrong if sRGB |
| Roughness, Metallic, AO, Mask, ORM | **Linear / Non-Color** | Data maps |
| Packed ORM | Linear; sample channels correctly in material | R=AO G=Rough B=Metal (common) |

If Base Color looks too dark/flat: check you didn't mark it Non-Color.
If Normal looks flat or inverted green: check Linear + green channel (DirectX vs OpenGL).

## Compression (UEFN / Unreal)

- Default BC for color; normals use normal-map compression when flagged as Normal.
- Don't leave a normal map as "Default" color compression when the editor exposes a
  Normal group — bumps will crawl.
- Masks used in Masked blend: keep sharp; avoid heavy lossy blur on opacity edges.

Exact enum names vary by build — `describe_class` / property dump before setting
via `execute_python`.

## ORM packing (preferred for instances)

One texture, three channels:

- **R** = Ambient Occlusion  
- **G** = Roughness  
- **B** = Metallic  

In the material: `TextureSample` → mask/component → Roughness / Metallic / multiply AO into BaseColor.
See `pbr_master_instances` for the master/`MI_` pattern.

## Failure table

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Plastic shiny everything | Roughness missing / Metallic=1 / sRGB on rough | Linear roughness; check Metal |
| Washed pastel albedo | sRGB off on BC or exposure | sRGB on Base Color |
| Inverted / crawling bumps | Normal as sRGB or wrong green | Linear normal; flip green if needed |
| Seams sparkle | Compression on mask / low res | Sharper mask; higher res trim |
| Black material | Missing texture path / unsaved import | Reimport; save asset |
| Works in Blender, wrong here | FBX didn't bring graphs | Rebuild with `blender_handoff` |

## Don'ts

- Don't feed sRGB normals into Normal input.
- Don't pack ORM then sample as if each file were separate without channel masks.
- Don't skip `save_asset` after import.
- Don't invent compression enum strings — reflect first.

## Related

- Master + instances → `pbr_master_instances`
- Blender Principled rebuild → `blender_handoff`
- Graph tools → `creating_materials`
