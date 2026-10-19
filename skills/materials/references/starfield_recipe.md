---
description: "HARD: the only UEFN star / starfield / night-sky recipe — Catland ALU graph, no textures, no Niagara, no other graphs"
metadata:
  order: 2
  label: "Starfield (only recipe)"
  default_enabled: false
  load_condition: "User asks for stars, starfield, star sky, night sky, sky stars, procedural stars, T_StarField, or a star dome / sky sphere"
---

# Starfield — the only recipe

**This is the only way to make stars in UEFN.** There is no texture path, no
simpler graph, no Niagara sprite sky, no particle dome, no Mixamo/stock
`T_StarField`. If the island already has `M_StarSky` / `M_Starfield` / similar,
**rebuild that asset in place** so mesh assignments stay. Never orphan. Never
delete a broken star material to "fix" it.

Source look: Catland live graph on `/catland/SolarSystem/Materials/M_Starfield`
(~70 live nodes). Ignore leftover dead nodes at the top of that asset.

Load this subskill: `skill_read_subskill("materials", "starfield_recipe")`.

## Never

| Never | Instead |
|-------|---------|
| Texture sample / `T_StarField` / panoramic star JPG | This ALU graph |
| Invent a 5-node "star sky" | This graph, same params |
| Niagara / sprite / mesh particles as a night sky | This material on a sky sphere / dome |
| Additive blend on a UEFN **sky** material | **Opaque** Unlit Two-Sided (validator) |
| `/Game/Materials/...` | `{content_root}Materials/M_Starfield` |
| Custom / HLSL node | Standard nodes only |
| 70 serial registry `add_material_expression` calls | One `execute_python` (this graph is the labelled last resort — registry would freeze the editor) |
| Create a second star material and leave the old one assigned | Rebuild the assigned asset |

Catland's source used **Additive**. `validate_uefn_asset` on a UEFN sky:
`Sky materials must be opaque or masked, and unlit.` **Always ship Opaque.**
Graph is otherwise 1:1. Emissive only (BaseColor unwired = black).

## Flags (HARD)

Surface domain. **Unlit. Two-Sided. Opaque.** EmissiveColor only.

## Asset path

1. `get_project_info()` → `content_root` (e.g. `/uefnmcp/`).
2. `search_assets(search="M_Star")` (and `M_Starfield` / `M_StarSky`). If a
   star/sky material already exists, **that path is the target**.
3. Else `create_material` name `M_Starfield`, folder `{content_root}Materials`
   (omit folder to pin the mount). **Never** `/Game/Materials`.
4. Call `uefn_editor_python_hints(topic="materials")`, then one
   `execute_python` with `build_starfield("<path>")` below.
5. `layout_material_expressions` is inside the script. Then
   `validate_uefn_asset` → `save_asset` → `save_current_level`.

## Graph (live nodes only)

Direction (tiles around actor origin — works on a sky sphere):

1. WorldPosition (default) → TransformPosition **World → Local** → Normalize = `dir`

Stars (Voronoi mask + simplex tint/brightness/twinkle):

2. Voronoi ALU Noise on `dir * StarDensity` (scale 1, quality 1, levels 1,
   turbulence off, output 0–1, repeat 512, level_scale 2)
3. `starMask = 1 − SmoothStep(StarCore, StarGlow, voronoi)`
4. SimplexTex Noise on `dir * (StarDensity * 0.97)` (same noise flags as Voronoi)
5. Tint: `Lerp(Hot, Mid, Saturate(n*2))` and
   `Lerp(Mid, Cool, Saturate(n*2 − 1))` via ConstantBiasScale bias −1 scale 1;
   pick with `SmoothStep(0.49, 0.51, n)`
6. Brightness: `Floor + Scale * Power(Frac(n * 7.31), Curve)`
7. Twinkle: `Sine(Time * TwinkleSpeed + n * 6.2832)` period 1 →
   CBS bias 1 scale 0.5 → `Lerp(1 − TwinkleAmount, 1, remapped)`
8. `stars = starRGB * starMask * bright * twinkle`

Nebula (faint, horizon-faded):

9. SimplexTex levels 3 turbulence **on**, `dir * NebulaScale`
10. fade `1 − Abs(dir.B)` (ComponentMask B only)
11. `nebula = noise * fade * NebulaColor * NebulaIntensity`

Output:

12. `(stars + nebula) * StarIntensity` → **EmissiveColor** only

Wire every pin. No unused math nodes (orphans fail `EditorValidator_Material`).

## Default params (1:1)

| Name | Type | Default |
|------|------|---------|
| StarDensity | scalar | 72 |
| StarCore | scalar | 0.02 |
| StarGlow | scalar | 0.08 |
| StarColorHot | vector | (0.60, 0.74, 1) |
| StarColorMid | vector | (1, 1, 0.96) |
| StarColorCool | vector | (1, 0.52, 0.30) |
| BrightnessCurve | scalar | 3 |
| BrightnessScale | scalar | 4 |
| BrightnessFloor | scalar | 0.03 |
| TwinkleSpeed | scalar | 2.2 |
| TwinkleAmount | scalar | 0.18 |
| NebulaScale | scalar | 1.7 |
| NebulaColor | vector | (0.12, 0.15, 0.31) |
| NebulaIntensity | scalar | 0.02 |
| StarIntensity | scalar | 1.6 |

Do not retune unless the user asked. These are the look.

## Last-resort builder (`execute_python` — this graph only)

One material, one script. `mat_path` = existing sky/star asset, or the new
`M_Starfield` path. In-memory only — never write a `.py` into the island.

```python
import unreal

def build_starfield(mat_path):
    mel = unreal.MaterialEditingLibrary
    mat = unreal.EditorAssetLibrary.load_asset(mat_path)
    if not mat:
        raise RuntimeError("missing " + mat_path)

    mat.set_editor_property("blend_mode", unreal.BlendMode.BLEND_OPAQUE)
    mat.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    mat.set_editor_property("two_sided", True)
    mel.delete_all_material_expressions(mat)

    px = {"x": -2800}

    def mk(cls, y, dx=0):
        return mel.create_material_expression(mat, cls, int(px["x"] + dx), int(y))

    def conn(a, ao, b, bi):
        mel.connect_material_expressions(a, ao, b, bi)

    def sp(name, val, y):
        e = mk(unreal.MaterialExpressionScalarParameter, y)
        e.set_editor_property("parameter_name", unreal.Name(name))
        e.set_editor_property("default_value", float(val))
        return e

    def vp(name, r, g, b, y):
        e = mk(unreal.MaterialExpressionVectorParameter, y)
        e.set_editor_property("parameter_name", unreal.Name(name))
        e.set_editor_property("default_value", unreal.LinearColor(r, g, b, 1.0))
        return e

    def cst(val, y):
        e = mk(unreal.MaterialExpressionConstant, y)
        e.set_editor_property("r", float(val))
        return e

    def noise(fn, levels, turb, y, omin=0.0, omax=1.0):
        e = mk(unreal.MaterialExpressionNoise, y)
        e.set_editor_property("scale", 1.0)
        e.set_editor_property("quality", 1)
        e.set_editor_property("output_min", float(omin))
        e.set_editor_property("output_max", float(omax))
        e.set_editor_property("levels", int(levels))
        e.set_editor_property("repeat_size", 512)
        e.set_editor_property("noise_function", fn)
        e.set_editor_property("turbulence", bool(turb))
        e.set_editor_property("level_scale", 2.0)
        return e

    wp = mk(unreal.MaterialExpressionWorldPosition, 0)
    tp = mk(unreal.MaterialExpressionTransformPosition, 80, 220)
    tp.set_editor_property("transform_source_type", unreal.MaterialPositionTransformSource.TRANSFORMPOSSOURCE_WORLD)
    tp.set_editor_property("transform_type", unreal.MaterialPositionTransformSource.TRANSFORMPOSSOURCE_LOCAL)
    nd = mk(unreal.MaterialExpressionNormalize, 80, 440)
    time = mk(unreal.MaterialExpressionTime, 900)
    conn(wp, "XYZ", tp, "")
    conn(tp, "", nd, "VectorInput")

    StarDensity = sp("StarDensity", 72.0, -40)
    mul_d = mk(unreal.MaterialExpressionMultiply, 40, 220)
    conn(nd, "", mul_d, "A")
    conn(StarDensity, "", mul_d, "B")
    voro = noise(unreal.NoiseFunction.NOISEFUNCTION_VORONOI_ALU, 1, False, 40)
    conn(mul_d, "", voro, "World Position")
    StarCore = sp("StarCore", 0.02, 200)
    StarGlow = sp("StarGlow", 0.08, 280)
    ss = mk(unreal.MaterialExpressionSmoothStep, 200, 220)
    conn(StarCore, "", ss, "Min")
    conn(StarGlow, "", ss, "Max")
    conn(voro, "", ss, "Value")
    starMask = mk(unreal.MaterialExpressionOneMinus, 200, 440)
    conn(ss, "", starMask, "")

    c097 = cst(0.97, 420)
    mul097 = mk(unreal.MaterialExpressionMultiply, 420, 220)
    conn(StarDensity, "", mul097, "A")
    conn(c097, "", mul097, "B")
    mul_pos = mk(unreal.MaterialExpressionMultiply, 500, 440)
    conn(nd, "", mul_pos, "A")
    conn(mul097, "", mul_pos, "B")
    simp = noise(unreal.NoiseFunction.NOISEFUNCTION_SIMPLEX_TEX, 1, False, 500)
    conn(mul_pos, "", simp, "World Position")

    Hot = vp("StarColorHot", 0.60, 0.74, 1.0, 680)
    Mid = vp("StarColorMid", 1.0, 1.0, 0.96, 760)
    Cool = vp("StarColorCool", 1.0, 0.52, 0.30, 840)
    c2a = cst(2.0, 680)
    mul2a = mk(unreal.MaterialExpressionMultiply, 680, 220)
    conn(simp, "", mul2a, "A")
    conn(c2a, "", mul2a, "B")
    satA = mk(unreal.MaterialExpressionSaturate, 680, 440)
    conn(mul2a, "", satA, "")
    lerpHM = mk(unreal.MaterialExpressionLinearInterpolate, 760, 660)
    conn(Hot, "RGB", lerpHM, "A")
    conn(Mid, "RGB", lerpHM, "B")
    conn(satA, "", lerpHM, "Alpha")

    c2b = cst(2.0, 920)
    mul2b = mk(unreal.MaterialExpressionMultiply, 920, 220)
    conn(simp, "", mul2b, "A")
    conn(c2b, "", mul2b, "B")
    cbs = mk(unreal.MaterialExpressionConstantBiasScale, 920, 440)
    cbs.set_editor_property("bias", -1.0)
    cbs.set_editor_property("scale", 1.0)
    conn(mul2b, "", cbs, "")
    satB = mk(unreal.MaterialExpressionSaturate, 920, 660)
    conn(cbs, "", satB, "")
    lerpMC = mk(unreal.MaterialExpressionLinearInterpolate, 1000, 880)
    conn(Mid, "RGB", lerpMC, "A")
    conn(Cool, "RGB", lerpMC, "B")
    conn(satB, "", lerpMC, "Alpha")

    c049 = cst(0.49, 1120)
    c051 = cst(0.51, 1200)
    ssPick = mk(unreal.MaterialExpressionSmoothStep, 1160, 220)
    conn(c049, "", ssPick, "Min")
    conn(c051, "", ssPick, "Max")
    conn(simp, "", ssPick, "Value")
    starRGB = mk(unreal.MaterialExpressionLinearInterpolate, 1160, 440)
    conn(lerpHM, "", starRGB, "A")
    conn(lerpMC, "", starRGB, "B")
    conn(ssPick, "", starRGB, "Alpha")

    c731 = cst(7.31, 1360)
    mul731 = mk(unreal.MaterialExpressionMultiply, 1360, 220)
    conn(simp, "", mul731, "A")
    conn(c731, "", mul731, "B")
    frc = mk(unreal.MaterialExpressionFrac, 1360, 440)
    conn(mul731, "", frc, "")
    BrightnessCurve = sp("BrightnessCurve", 3.0, 1440)
    powe = mk(unreal.MaterialExpressionPower, 1440, 220)
    conn(frc, "", powe, "Base")
    conn(BrightnessCurve, "", powe, "Exp")
    BrightnessScale = sp("BrightnessScale", 4.0, 1520)
    mulB = mk(unreal.MaterialExpressionMultiply, 1520, 220)
    conn(powe, "", mulB, "A")
    conn(BrightnessScale, "", mulB, "B")
    BrightnessFloor = sp("BrightnessFloor", 0.03, 1600)
    bright = mk(unreal.MaterialExpressionAdd, 1600, 220)
    conn(mulB, "", bright, "A")
    conn(BrightnessFloor, "", bright, "B")

    TwinkleSpeed = sp("TwinkleSpeed", 2.2, 1760)
    mulTS = mk(unreal.MaterialExpressionMultiply, 1760, 220)
    conn(time, "", mulTS, "A")
    conn(TwinkleSpeed, "", mulTS, "B")
    c628 = cst(6.2832, 1840)
    mulPh = mk(unreal.MaterialExpressionMultiply, 1840, 220)
    conn(simp, "", mulPh, "A")
    conn(c628, "", mulPh, "B")
    addPh = mk(unreal.MaterialExpressionAdd, 1840, 440)
    conn(mulTS, "", addPh, "A")
    conn(mulPh, "", addPh, "B")
    sine = mk(unreal.MaterialExpressionSine, 1840, 660)
    sine.set_editor_property("period", 1.0)
    conn(addPh, "", sine, "")
    cbsT = mk(unreal.MaterialExpressionConstantBiasScale, 1840, 880)
    cbsT.set_editor_property("bias", 1.0)
    cbsT.set_editor_property("scale", 0.5)
    conn(sine, "", cbsT, "")
    TwinkleAmount = sp("TwinkleAmount", 0.18, 1960)
    omAmt = mk(unreal.MaterialExpressionOneMinus, 1960, 220)
    conn(TwinkleAmount, "", omAmt, "")
    c1 = cst(1.0, 2040)
    twinkle = mk(unreal.MaterialExpressionLinearInterpolate, 1960, 440)
    conn(omAmt, "", twinkle, "A")
    conn(c1, "", twinkle, "B")
    conn(cbsT, "", twinkle, "Alpha")

    m1 = mk(unreal.MaterialExpressionMultiply, 2200, 0)
    conn(starRGB, "", m1, "A")
    conn(starMask, "", m1, "B")
    m2 = mk(unreal.MaterialExpressionMultiply, 2200, 160)
    conn(m1, "", m2, "A")
    conn(bright, "", m2, "B")
    stars = mk(unreal.MaterialExpressionMultiply, 2200, 320)
    conn(m2, "", stars, "A")
    conn(twinkle, "", stars, "B")

    NebulaScale = sp("NebulaScale", 1.7, 2400)
    mulN = mk(unreal.MaterialExpressionMultiply, 2400, 220)
    conn(nd, "", mulN, "A")
    conn(NebulaScale, "", mulN, "B")
    nebN = noise(unreal.NoiseFunction.NOISEFUNCTION_SIMPLEX_TEX, 3, True, 2400)
    conn(mulN, "", nebN, "World Position")
    maskB = mk(unreal.MaterialExpressionComponentMask, 2480, 220)
    maskB.set_editor_property("r", False)
    maskB.set_editor_property("g", False)
    maskB.set_editor_property("b", True)
    conn(nd, "", maskB, "")
    absB = mk(unreal.MaterialExpressionAbs, 2480, 440)
    conn(maskB, "", absB, "")
    fade = mk(unreal.MaterialExpressionOneMinus, 2480, 660)
    conn(absB, "", fade, "")
    mulNF = mk(unreal.MaterialExpressionMultiply, 2560, 220)
    conn(nebN, "", mulNF, "A")
    conn(fade, "", mulNF, "B")
    NebulaColor = vp("NebulaColor", 0.12, 0.15, 0.31, 2640)
    mulNC = mk(unreal.MaterialExpressionMultiply, 2640, 220)
    conn(mulNF, "", mulNC, "A")
    conn(NebulaColor, "RGB", mulNC, "B")
    NebulaIntensity = sp("NebulaIntensity", 0.02, 2720)
    neb = mk(unreal.MaterialExpressionMultiply, 2720, 220)
    conn(mulNC, "", neb, "A")
    conn(NebulaIntensity, "", neb, "B")

    addAll = mk(unreal.MaterialExpressionAdd, 2880, 80)
    conn(stars, "", addAll, "A")
    conn(neb, "", addAll, "B")
    StarIntensity = sp("StarIntensity", 1.6, 2960)
    out = mk(unreal.MaterialExpressionMultiply, 2960, 80)
    conn(addAll, "", out, "A")
    conn(StarIntensity, "", out, "B")
    mel.connect_material_property(out, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)

    mel.layout_material_expressions(mat)
    mel.recompile_material(mat)
    mat.modify(True)
    n = len(list(mel.get_material_expressions(mat) or []))
    print("OK", n, mat.get_editor_property("blend_mode"), mat.get_editor_property("shading_model"))
    return mat_path

build_starfield("/MyProject/Materials/M_Starfield")  # replace with content_root path
```

Then `validate_uefn_asset` → `save_asset` → `save_current_level`.
If validate says sky must be opaque: flags are already Opaque — do not switch
to Additive to "match Catland."
