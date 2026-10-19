---
description: "Symptom→fix table: checkerboard, black material, missing Normalize/AppendVector pins, EditorValidator_Material cook fails, illegal Creative mesh refs, Nanite overrides"
metadata:
  order: 2
  label: "Fixing materials"
  default_enabled: false
  load_condition: "A material looks wrong, missing, black, checkerboard, edits do not show, cook/submit fails, Missing Normalize/AppendVector input, or AssetReferenceRestrictions"
---

## Fixing materials — symptom → fix

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Grey/checkerboard (WorldGridMaterial) | Material reference lost or asset missing | `get_asset_info("<path>")` → missing: recreate or `search_assets(search=...)` for the real path → `assign_material_to_mesh` again |
| Material renders black | Nothing wired to BaseColor/Emissive, or Masked blend with OpacityMask 0 | `list_material_expressions` → wire color via `connect_material_nodes` / `connect_material_output` → `recompile_material` |
| Edit made but level still shows old look | Recompile or saves skipped | `recompile_material` → save asset → `save_current_level()` — all three, in order |
| **Everything stacked on one spot in material graph** | Nodes added at `(0,0)` / layout skipped | `layout_material_expressions` → `save_asset`. Always layout after graph edits |
| Asset "created" but not in Content Browser | Never saved / wrong folder (invented `/Game/...` or missing leading `/`) | Must be under `content_root` (e.g. `/MyProject/Materials`); verify with `does_asset_exist`; re-save with `save_asset` |
| Cook: Disallowed reference to `/Game/Materials/...` | New mats created under `/Game/` instead of project mount | Recreate under `{content_root}Materials/...`, reassign actors, delete `/Game/` junk |
| Texture parameter empty after import | Import created a different path than assumed | `search_assets(search="T_...")` for the actual `/Game/...` path, then `set_material_instance_texture` |
| Material too heavy / fails to render on some platforms | Over the ~500-instruction UEFN cap | Simplify the graph: fewer Noise nodes, bake effects into textures, use `MF_QualitySwitch_Material_Attributes` |
| Wanted a Custom/HLSL node | UEFN's editor has no Custom node | Rebuild with standard nodes (Time, Sine, Panner, Lerp, ConstantBiasScale) |
| Wrong mesh slot changed | Multi-slot mesh | Try `slot_index` 0..n with `assign_material_to_mesh`; inspect actor via `get_actor_properties` |
| UEFN crashes compiling shaders / DDC errors | Corrupt DerivedDataCache or broken install | User action: close UEFN, delete the project's `Saved/` + local DerivedDataCache, verify UEFN in the Epic launcher |
| Verse `SetMaterial` does nothing at runtime | Prop not manipulable, or the post-v33.00 instanced-material regression | Ensure the target is a `creative_prop` that allows manipulation; test with a plain (non-instance) material; see runtime reference |
| **`(Node Normalize) Missing Normalize input`** | Normalize with no vector wired | Wire a float3 (or delete the node). Confirm with `get_material_expression_info` → `recompile_material` → `validate_uefn_asset` |
| **`(Node AppendVector) Missing AppendVector input A`** (or B) | AppendVector half-wired | Wire **A and B**. Common when building RGB from Sines — both AppendVector stages need both pins. Delete unused Appends |
| **Failed to translate Material for platform(s) … SM5/SM6/ES3_1** | Same as missing pins — cook translation fails on all targets | Fix missing inputs first; do not “ship anyway.” Prefer `duplicate_material` of a known-good water/PBR master |
| **`AssetValidator_AssetReferenceRestrictions` / illegally references `/Game/Creative/.../CP_Ground_Plane`** | Persistent actor uses a Creative gallery mesh UEFN forbids as a project dependency | Delete/replace the actor mesh with a **project** `/Game/...` static mesh (import or duplicate into the project). Reset illegal refs. Re-validate the **level** + GameFeatureData |
| **`ValkyrieValidator_Properties` … `bForceDisableNanite` override True** | Illegal FortStaticMeshComponent property override | Reset `bForceDisableNanite` to default (False). Do not force-disable Nanite to “fix” water planes |
| **`Sky materials must be opaque or masked, and unlit`** | Additive (or lit) blend on a UEFN sky | `set_material_flags` **Opaque Unlit Two-Sided**. Keep the `starfield_recipe` graph — do not swap to a texture |
| **Disallowed reference … Plugin: \<Island\>** (GameFeatureData) | Same illegal Creative mesh ref pulled into the cooked plugin | Fix the level actor first; re-save level; re-validate GameFeatureData |

## Publish / cook gate (do this)

UEFN ≠ full Unreal. The material editor can look fine while **submit validation fails**.

1. `recompile_material` on every edited `M_` / parent of `MI_`.
2. `validate_uefn_asset({"asset_path": "<content_root>/Materials/..."})` on the material.
3. If you placed or retargeted meshes: validate the **umap** and fix
   `AssetValidator_AssetReferenceRestrictions` / `ValkyrieValidator_Properties`.
4. Only then `save_asset` / `save_current_level()`.

Real failure example (ocean waves):

```
M_OceanWaves : (Node Normalize) Missing Normalize input
M_OceanWaves : (Node AppendVector) Missing AppendVector input A
OceanWave_Surface illegally references: /Game/Creative/.../CP_Ground_Plane
bForceDisableNanite override True → ValkyrieValidator_Properties
```

Fix graph pins **and** replace the Creative ground plane — both are hard blockers.

## Debug order

1. `validate_uefn_asset` on the material (and level if placed) — read the exact node/property.
2. `get_asset_info` on the material path — does it exist, what class is it?
3. `list_material_expressions` — empty? unconnected Normalize / AppendVector / Lerp?
4. `get_material_expression_info` on the failing index — which pins are empty?
5. Wire or delete → `recompile_material` → `validate_uefn_asset` again.
6. Assign + `save_current_level()` — then re-inspect in the viewport.
7. Still wrong → `get_editor_log(filter_str="material")` / AssetLog for compiler output.

## Agent anti-patterns (do not)

- Invent a full ocean/water graph from scratch without duplicating a known-good master.
- Leave math nodes in the graph “for later” with empty pins.
- Use `/Game/Creative/Environments/Meshes/CP_Ground_Plane` as a permanent water sheet.
- Set `bForceDisableNanite` (or other Fort component overrides) to paper over mesh issues.
- Treat Unreal Engine marketplace/Custom HLSL tutorials as valid in UEFN.
