---
description: "Water application of reusable MF_ patterns — ocean/river/lake/rapids/waterfall/beds stacks, cheaper variants, MIC parents. Paths under active project only."
metadata:
  order: 12
  label: "Water material recipes"
  default_enabled: false
  load_condition: "Ocean, lake, river, rapids, waterfall, pond, caustics, shore bed, or water foam materials"
---

# Water recipes (application of MF_ patterns)

Uses `mf_reusable_patterns` + `recipe_recreate`. Exact scalar/vector/texture tables: `water_exact_defaults`.

**Folder (example):** `{content_root}Materials/Water/` (e.g. `/MyProject/Materials/Water/`) — never `/Game/Materials`.

## Family map

| Use | Full | Cheaper | Core MF_ |
|-----|------|---------|----------|
| Ocean | `M_Ocean` (~337) | `M_Ocean_Cheaper` (~192) | WavesWPO, Depth_UVs, Wave_Motion, Foam_Motion, FixedDepth, FakeSpecular |
| Ocean distance | `M_Ocean_Distance` | — | foam + depth + fake spec |
| Ocean radial | `M_Ocean_Radial` | `_Cheaper` | `*_Radial` + `IslandCentre` |
| Lake | `M_Lake` | `_Cheaper` | River WPO/Depth_UVs + FixedDepth + radial `acos` MF_ + `LakeCentre` |
| River | `M_River` | `_Cheaper` | river MF stack |
| Rapids | `M_Rapids` | `_Cheaper` | FixedDepth + foam tex / vertical mask |
| Waterfall | `M_Waterfall` | `_Cheaper` | directional foam + WPO (no ocean MF_) |
| Clean | `M_Water_Clean` | `_Cheaper` | self-contained ripples |
| Opaque / pixel | `M_Water_Opaque` / `M_Water_Pixelated` | — | FakeSpecular / FlipBook |
| Pond scum | `M_PondScum` | `_Cheaper` | layered plants + FakeSpecular |
| Beds | `M_Sand`, `M_Riverbank`, `M_RapidsBank`, `M_River_Rock` | — | wetness / caustics / WPO |
| FX | `M_Waterfall_Foam`, `M_WaterSplash`, `M_Caustics` | — | Unlit / Additive / Opaque |

## MIC_ parents

- `MIC_Lake_Waterfall` → `M_Lake` (+ cheaper twin)
- `MIC_Waterfall_Arc` → `M_Waterfall` (+ cheaper)
- `MIC_PondScum` / `MIC_Riverbank_Pond` → matching masters

## Ocean look (how it stacks)

1. WPO ← WavesWPO  
2. Colour ← Lerp(Colour, ColourDeep, FixedDepth)  
3. Crest foam ← Wave_Motion UVs × foam tex  
4. Edge foam ← depth mask × panned EdgeFoam  
5. Normals near/far by depth; refraction  
6. FakeSpecular + cubemap fresnel  

**Radial:** set `IslandCentre` to island world XY. Prefer Cheaper for gameplay LOD.

## River / lake / rapids

Shared: River WavesWPO + Depth_UVs + FixedDepth + FakeSpecular.  
Lake adds radial edge (`acos`) + `LakeCentre`.  
Rapids: vertical mask × falling foam panners × depth opacity (often no full river WPO MF).

## Waterfall / clean / FX

Waterfall: texture-driven foam sheets + directional bands + light WPO.  
Clean: small self-contained ripple graph (no MF_).  
Caustics / splash / foam puff: tiny Opaque / Additive / Unlit graphs.

## Shore beds

Sand/Riverbank: albedo+normal + caustics + WavesWPO so the wet line tracks water. Match `WaveOffset` / wet params to the water master's Depth.

## Workflow

1. `duplicate_material` closest master (never hand-rebuild 337-node ocean).  
   Inventing `M_OceanWaves` with half-wired Normalize/AppendVector **will fail cook**.
2. Tune via `water_exact_defaults` or MI overrides.  
3. **`layout_material_expressions`** (never leave a stacked graph) →
   `recompile_material` → **`validate_uefn_asset`** on the `M_` (and any `MI_`) →
   `save_asset` → `save_current_level()`.  
4. ≤500 instructions; prefer `*_Cheaper`.

## Water sheet mesh (publish blockers)

Do **not** use `/Game/Creative/Environments/Meshes/CP_Ground_Plane` (or other Creative
gallery planes) as the ocean surface actor — submit hits
`AssetValidator_AssetReferenceRestrictions` and GameFeatureData “Disallowed reference”.

Do **not** set `bForceDisableNanite=True` on the Fort static mesh component —
`ValkyrieValidator_Properties` rejects that override.

**Do:** place a project-owned plane/mesh under the project content mount from
`get_project_info().content_root` (e.g. `/MyProject/Meshes/SM_WaterSheet`) — import or
duplicate the Creative plane into island content rather than referencing it in place.
Assign `MI_Ocean*` / water MI, then `validate_uefn_asset` on the **level** as well as
the material.
