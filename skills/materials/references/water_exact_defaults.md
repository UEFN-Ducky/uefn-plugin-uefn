---
description: "1:1 scalar/vector/texture defaults for water masters and MIC overrides — lake, river, rapids, waterfall, ocean cheaper, clean, beds, pond, caustics."
metadata:
  order: 13
  label: "Water exact defaults"
  default_enabled: false
  load_condition: "Need exact water look defaults, MIC overrides, or recreate lake/river/waterfall/ocean params"
---

# Water exact defaults

**Bit-identical graphs:** `duplicate_material` existing `M_*` in the active project. Tables below are for instances / rebuilds. Textures live beside materials under the project water folder.

---

## M_Lake / M_Lake_Cheaper (~253–261) — Translucent DefaultLit

**MF_:** River WavesWPO, River Depth_UVs, FixedDepth, FakeSpecular, BreakOutFloat3Components, radial `acos` ×4 + `LakeCentre`. Epic's shipped MF_ assets contain those acos nodes already — **reuse the MF_, do not author a Custom node** (UEFN has none; `mf_reusable_patterns` has the standard-node approximation if you must rebuild it).

| Param | Texture |
|-------|---------|
| SubtleNormal | `T_Water_Normal_Subtle` |
| WaterNormal | `T_Water_Normal` |
| RoughNormal | `T_Water_Normal_Large` |
| EdgeNormals | `T_Water_EdgeNormals` |
| CubeMap (Cheaper) | `T_Cubemap` |

Hard: `T_Noises`

```
Colour (0.05,0.05,0.05,1) | ColourDeep (0,0,0,1)
LakeCentre — world XY of lake (MUST set per level)
Metallic 0 | Specular 0.5 | Roughness 0.05
Opacity 0.5 | OpacityDeep 1 | FadeDistance 5
Refraction 0.1 | RefractionIndex 0.9
River_Depth -15 | River_DepthScale 171.47632 | River_DepthPower 1
NormalIntensity 2 | Lake_Tiling 1 | Lake_Speed 1
WaterNormal_Intensity 0.15 | WaterNormal_Tilng 4 | WaterNormal_Speed 0.5
SubtleNormal_Speed 2 | SubtleNormal_Tilng 15 | SubtleNormal_Intensity 0.05
SubtleNoise_VariationPower 2 | SubtleNoise_VariationIntensity 2
SubtleNormal_VariationSpeed 0.25 | SubtleNormal_VariationTilng 1
RoughNormal_Intensity 0.2 | RoughNormal_Tilng 5 | RoughNormal_Speed 1
RoughNormal_VariationTilng 1 | RoughNormal_VariationSpeed 0.1
RoughNoise_VariationIntensity 0.75 | RoughNoise_VariationPower 1.25
Lake1_Intensity 0.25 | Lake1_Speed 0.025 | Lake1_NormalIntensity 0.75 | Lake1_Variation 512
Lake2_Intensity 0.25 | Lake2_Speed 0.05 | Lake2_NormalIntensity 0.75 | Lake2_Variation 1024
Lake_Offset 5 | Lake_Variance 4096
EdgeNormalUV_ScaleX 0.1 | EdgeNormal_Depth 0 | EdgeNormal_DepthScale 35
EdgeNormal_Depth_Power 1 | EdgeNormal_Speed 1 | EdgeNormal_Mask 3.14159 | EdgeNormal_Intensity 1
```

Cheaper: + `CubeMap_Intensity 0.5`, `CubeMap_Fresnel 3`.

**MIC_Lake_Waterfall:** Lake1_Intensity 0.25, Lake1_Speed 0.2, Lake2_Speed 0.1, LakeCentre per level.

---

## M_River (~222) / M_River_Cheaper (~149)

**MF_:** River WavesWPO, River Depth_UVs, FixedDepth, FakeSpecular, BreakOutFloat3Components.  
Textures: same Subtle/Water/Rough/Edge normals as lake. Hard: `T_Noises`.

```
Colour (0.05,0.05,0.05,1) | ColourDeep (0,0,0,1)
Metallic 0 | Specular 0.5 | Roughness 0.05
Opacity 0.5 | OpacityDeep 1 | FadeDistance 5
Refraction 0.05 | RefractionIndex 1.1
River_Depth -15 | River_DepthScale 50 | River_DepthPower 1
River_Tiling 1 | River_Speed 1 | NormalIntensity 2
WaterNormal_Intensity 0.1 | WaterNormal_Tilng 5 | WaterNormal_Speed 2
SubtleNormal_Speed 2 | SubtleNormal_Tilng 12 | SubtleNormal_Intensity 0.05
SubtleNoise_VariationPower 2 | SubtleNoise_VariationIntensity 2
SubtleNormal_VariationSpeed 0.25 | SubtleNormal_VariationTilng 1
RoughNormal_Intensity 0.2 | RoughNormal_Tilng 4 | RoughNormal_Speed 1
RoughNormal_VariationTilng 0.5 | RoughNormal_VariationSpeed 0.1
RoughNoise_VariationIntensity 0.75 | RoughNoise_VariationPower 1.25
EdgeNormal_Tiling 4 | EdgeNormal_Speed 1 | EdgeNormal_Intensity 2
RiverEdge_Depth -5 | RiverEdge_DepthScale 20 | RiverEdge_DepthPower 0.4
River1_Speed 0.1 | River1_Intensity 0.15 | River1_NormalIntensity 0.5 | River1_Variation 512
River2_Speed 0.05 | River2_Intensity 0.15 | River2_NormalIntensity 0.5 | River2_Variation 1024
River_Offset 0 | River_Variance 4096
```

Cheaper: drop rough + River2; + CubeMap 0.5/3; ColourDeep `(0.0627, 0.0628, 0.065, 1)`.

---

## M_Rapids (~166)

**MF_:** FixedDepth + BreakOutFloat2Components. Hard: `T_Water_Normal_Large`, `T_Water_EdgeNormals`, `T_Noise_Stormy`, `T_Ocean_Foam`.

```
Colour (0.05,0.05,0.05,1) | ColourDeep (0,0,0,1)
Metallic 0 | Specular 0.5 | Roughness 0
Opacity 0.8 | OpacityDeep 1
River_Depth -5 | River_DepthScale 50 | River_DepthPower 1
Normals_Tiling 3 | Normals_Speed 2 | Normals_Intensity 1
Normals_Variation_Tiling 1 | Normals_Variation_Speed 1 | Normals_Variation_Intensity 0.25
VerticalMask_Falloff 4
FallingMask_Speed 2.5 | FallingMask_Tilng 2 | FallingMask_Intensity 3
LightFoam_Tiling 4 | LightFoam_Speed 2
MediumFoam_Speed 3 | MediumFoam_Tiling 3
HeavyFoam_Speed 4 | HeavyFoam_Tiling 2
Foam_Distortion_Scale 1024 | Foam_Distortion_Intensity 0.02
Foam_WPO_Intensity 12.5 | Foam_WPO_Scale 32
Foam_Intensity 2.5 | Foam_Falloff 1.6 | WPO_Vertex_Intensity 25
```

Cheaper: + CubeMap 0.5/3.

---

## M_Waterfall (~192) + MIC_Waterfall_Arc

Hard: `T_Waterfall_Foam`, `T_Waterfall_Foam_Directional`, `T_Noise_Stormy`. Colour `(1,1,1,1)`.

```
Metallic 0 | Roughness 0.1 | Opacity 0.5 | Fresnel 6 | VariationScale 4096
Waterfall_Speed 0.5
EdgeMask_Tiling 0.5 | EdgeMask_Speed 2
Foam1_Speed 4 | Foam1_Tiling 1 | Foam2_Speed 10 | Foam2_Tiling 2
Foam_Intensity 0.1 | Foam_Contrast 3 | Foam_Falloff 2
DirectionalFoam_Intensity 0.3 | DirectionalFoam_Contrast 2.5
DirectionalFoam1_Speed 6 | Tiling 0.75 | Intensity 2
DirectionalFoam2_Speed 10 | Tiling 1 | Intensity 2
DirectionalFoam3_Speed 10 | Tiling 1 | Intensity 0.5
DirectionalFoam4_Speed 10 | Tiling 1 | Intensity 1
WPO_Vertex_Intensity 1 | Foam_WPO_Scale 2 | Foam_WPO_Intensity 8
```

**MIC_Waterfall_Arc:** Opacity 0.25, Waterfall_Speed 4, EdgeMask_Tiling 8, Foam1_Tiling 8, Foam2_Tiling 12, DirectionalFoam1–4 Tiling 8/10/12/16.

Foam puff: `M_Waterfall_Foam` Unlit Translucent, `RadialGradientExponential` + `T_Waterfall_Foam`.

---

## M_Ocean_Cheaper (~192) — recommended gameplay ocean

**MF_:** Ocean WavesWPO, Depth_UVs, Wave_Motion, Foam_Motion, FixedDepth, FakeSpecular.

| Param | Texture |
|-------|---------|
| EdgeFoam / Wave1_Foam | `T_Ocean_EdgeFoam` |
| SeaFoam | `T_Ocean_Foam` |
| CubeMap | `T_Cubemap` |
| Normal_Large | `T_Water_Normal_Large` |

```
Colour (0.1703, 0.1816, 0.245, 1) | ColourDeep (0.0394, 0.0373, 0.06, 1)
Opacity 0.6 | OpacityDeep 1.5 | Emissive 2 | FadeDistance 25
Ocean_Depth 0.035 | Ocean_DepthScale 50 | Ocean_DepthPower 1
CubeMap_Intensity 0.1 | CubeMap_Fresnel 12
Wave1_Tiling 2 | Wave1_SpeedX 0.02 | Wave1_Power 3 | Wave1_Scale 16
Wave1_Speed 0.1 | Wave1_Varience 7500 | Wave1_Offset 0
EdgeFoam_Scale 20 | EdgeFoam_Power 3 | EdgeFoam_SpeedX 0.02 | EdgeFoam_Tiling 2
EdgeFoam_Emissive 1.5 | EdgeFoam_Depth 0
Foam1_Tiling 4 | Foam1_Power 2 | Foam1_Scale 30 | Foam1_Depth 0
Foam1_Speed 0.1 | Foam1_Varience 6000 | Foam1_Offset 4
Foam1_HeightOffset 100 | Foam1_HeightScale 125 | Foam1_HeightPower 3
Foam2_Tiling 4 | Foam2_Power 2 | Foam2_Scale 25 | Foam2_Depth 0
Foam2_Speed 0.15 | Foam2_Varience 6000 | Foam2_Offset 2
Foam2_HeightOffset 90 | Foam2_HeightScale 100 | Foam2_HeightPower 1
SeaFoam_Emissive 0.5
FarNormal_Variation 9000 | FarNormal_Offset 5 | FarNormal_Flatten 0.5
FarNormal_UVScale 512 | FarNormal_Speed 0.05
OceanShore_Speed 0.1 | OceanShore_Intensity 0.5 | OceanShore_NormalIntensity 2 | OceanShore_Variation 3000
Ocean1_Variation 512 | Ocean1_NormalIntensity 2 | Ocean1_Intensity 0.5 | Ocean1_Speed 0.3
Ocean_Offset 100
```

Full `M_Ocean` / Radial / Distance: **duplicate only**. Radial: set `IslandCentre`.

---

## Clean / beds / pond / caustics

**M_Water_Clean:**
```
Metallic 0 | Specular 0.255 | Roughness 0.08
Fresnel Power 0.2 | Diffuse Multiplier 0.08
Wave Size 1024 | Smaller Ripples 1.5 | Medium Ripples 0.5 | Larger Ripples 0.25
Wave Speed 0.25 | Wave Height 20 | Wave Normal Speed 2
Opacity 0.5 | Refraction 1.05 | Fade Distance 100
Water_Colour_Dark (0, 0.3255, 0.2235, 1)
Water_Colour_Light (0.6439, 0.6031, 0.815, 1)
Normals: Subtle / Large / Water
```

**M_Caustics:** Metallic 0 | Roughness 0.5 | Intensity 1 | Speed 0.25 | Tiling 3 | Colour (0.8,0.8,0.8,0) | `T_Caustics`

**M_Sand** (+ Ocean WavesWPO): Tiling 4 | NormalIntensity 0.5 | Roughness 0.5 | RoughnessMap 0.15 | SeaBedDiffuse 0.5 | SeaBedRoughness 1 | Wet_Roughness -0.4 | Wet_Diffuse 0.75 | WaveOffset 10 | Intensity 3 | Speed 0.25 | CausticTiling 4

**M_Riverbank** (+ River WavesWPO): same pattern; RiverBed* names; WaveOffset 2 | Intensity 1.25. **MIC_Riverbank_Pond:** Intensity1/2/3 = 0, Speed 0.1

**M_PondScum (keys):** Opacity 0.8 | plants/algae/moss layer tilings + SurfaceMask scales 20000/3000/1500 | Coverage 0.6 | Density 35 | SurfacePlants Scale 64 / Far 512 | Foam_Scale 85 | Height 0.75 | HeightRatio -0.025. **MIC:** FakeSpec_Intensity 0.05, Speed 0.05, UVScale 1024
