---
description: "Reusable MF_ building blocks — depth fade, sine WPO, animated UV/masks, radial centre UV, fake specular. Use for water, glass, lava, fog, ice, cloth, wet beds, any surface."
metadata:
  order: 10
  label: "Reusable MF_ patterns"
  default_enabled: false
  load_condition: "Building material functions, translucent depth, vertex waves, foam/edge masks, radial UV, fake specular, or advanced animated surfaces"
---

# Reusable MF_ patterns (any surface)

Shared math lives in **Material Functions** (`MF_*`). Masters call them.
Inspect functions with `execute_python` + `MaterialEditingLibrary.get_material_function_expressions`
(registry `list_material_expressions` is Material-only). Stay under **500 instructions**.

**Project rule:** create/edit only under the project content mount from
`get_project_info().content_root` (e.g. `/MyProject/Materials/...`). **Never**
`/Game/Materials` — that cooks as `Disallowed reference to /Game/...`.

---

## Depth fade → scalar 0..1

**Classic names:** `MF_FixedDepth` (water pack). Same idea for glass, fog sheets, lava pools.

**Inputs:** `Depth`, `Depth_Scale`, `Depth_Power`

**Math:**
1. `SceneDepth / PixelDepth` → scene/pixel ratio
2. Camera/world Z offset vs `Depth` (AppendVector Constant2(0,0)+Depth)
3. Combined depth difference → mask via ComponentMask.B
4. `OneMinus` → `/ Depth_Scale` → Clamp → `Power(Depth_Power)` → Clamp → **Result**

**Use for:** opacity/deep colour lerp, edge foam masks, wet-band on beds, soft intersections.

---

## Multi-octave sine WPO

**Classic names:** `MF_OceanWavesWPO`, `MF_RiverWavesWPO` (same graph, different defaults).

**No function inputs** — ScalarParameters group `WPO`:
`Master_Speed`, `Master_Intensity`, `Offset`,
`Wave1Scale` / `Speed1` / `Intensity1` (+ Wave2, Wave3).

**Math (3 sine octaves on WorldPosition):**
```
t = Time * Master_Speed
for each wave i:
  s_i = sin( WorldPos_component / WaveiScale + t * Speedi ) * Intensityi
height = (s1 + s2 + s3) + Offset
Vector = Append( (0,0), height ) * Master_Intensity
Scalar = height * Master_Intensity
```

**Defaults (calm / open surface):** Master_Speed 0.3, Intensity 2, Wave1Scale 8192 / Speed1 0.2 / Intensity1 6, Wave2 2048/0.5/1, Wave3 1024/1/0.5.

**Flowing surface:** Master_Speed **-0.5**, Master_Intensity 1, Intensity1 3.

**Use for:** water, flags, soft terrain bob, heat shimmer WPO (tiny intensity).

---

## Animated UV = pan U + depth V

**Classic names:** `MF_OceanDepth_UVs`, `MF_RiverDepth_UVs`.

**Inputs:** Tiling, Speed, Depth, Depth_Scale, Depth_Power

```
panU = Panner(TexCoord0, Time*Speed, speed_x=1).R * Tiling
depthV = DepthFade(Depth + WavesWPO.Scalar, Depth_Scale, Depth_Power)
Result = Append(panU, depthV)
```

Wire the matching WPO MF into the depth add. **Use for:** scrolling normals/foam driven by depth.

---

## Radial UV around a world centre

**Classic names:** `*_Radial` + vector `IslandCentre` / `LakeCentre`.

```
dir      = Normalize(Centre - WorldPosition)
d        = DotProduct(dir, const3)            # -1..1
# There is NO Custom/HLSL node in UEFN, so acos() must be built from standard nodes.
# Cheap standard-node acos approximation (0..1 output, good enough for shore rings):
#   acos(d)/PI  ≈  0.5 - 0.5 * d * (1 + 0.19 * (1 - d*d))
dd       = Multiply(d, d)
poly     = Add(1.0, Multiply(0.19, OneMinus(dd)))
angle01  = Subtract(0.5, Multiply(0.5, Multiply(d, poly)))
angleU   = ComponentMask(Frac(Divide(angle01, Tiling)), R)
depthV   = DepthFade(...)
Result   = AppendVector(angleU, depthV)
```

**No Custom node exists in UEFN** — `list_uefn_material_expression_classes` reports
`"No Custom/HLSL node in UEFN — use these standard nodes only."` Build the curve from
standard nodes as above (or bake it into a small gradient texture and `TextureSample`
it). Never write HLSL here.

**Use for:** island oceans, circular lakes, radial dirt rings, vortex FX.

---

## Crest / sheet motion (UV warp + intensity)

**Classic names:** `MF_OceanWave_Motion` (+ Radial).

**Inputs:** Depth*, SpeedX, Tiling, Variation, Offset, SpeedY (+ Centre on radial)

```
baseUV = DepthUVs(...)
(u,v) = BreakOutFloat2(baseUV)
w = sin( WorldPos.X/Variation + Offset + Time*SpeedY )
uv = Append(u, Power(u, Lerp(0.65, 2.0, BiasScale(w,1,0.5))))
Intensity = Power(OneMinus(Clamp(w)))
Exponent = Lerp(1, 4, Clamp(w))
```

**Use for:** wave crests, lava crust cracks, cloud breaks — sample a mask tex with `uv` × Intensity.

---

## Edge / layer mask + panned UVs

**Classic names:** `MF_Foam_Motion` (+ Radial).

```
Mask = OneMinus( DepthUVs(...).G )   # depth channel
UVs = Panner( TexCoord0 * Tiling, Time * warpedSpeed )
# warp: sin( Speed*Time + WorldPos.X/Variation ) * Offset
```

**Use for:** foam, dirt edges, wet rings, snow melt lines, scum.

---

## Fake multi-lobe specular

**Classic name:** `MF_FakeSpecular`. Needs `MPC_Globals.LightVector` (Material Parameter Collection).

**Params:** Intensity, Intensity1/2/3, Power1/2/3, Speed, UVScale + dual Panners on a sparkle tex.

```
NdotL-like = Clamp( Dot( -LightVector.rgb , ReflectionVectorWS ) )
lobes = Σ Power(NdotL, Poweri) * Intensityi
Result = (panned sparkle samples * lobes) * FakeSpec_Intensity
```

**Use for:** water sparkle, ice, wet metal, glossy plastic without full reflections.

---

## Dependency sketch

```
WavesWPO ──┐
DepthFade ─┼─► DepthUVs ─► Wave_Motion
           │            └─► Foam_Motion / edge masks
           └─► DepthUVs_Radial ─► Motion/Foam Radial
FakeSpecular (standalone; MPC LightVector)
```

## Build order (new empty project)

1. Depth fade MF  
2. Waves WPO MF (calm + flowing variants or one MF with params)  
3. Depth UVs (+ radial if needed)  
4. Wave motion + foam/edge motion  
5. Fake specular + MPC  
6. Masters call MFs — prefer `*_Cheaper` masters under 200 expr for gameplay
