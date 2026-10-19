---
description: "Animated rainbow material via standard nodes (Time + Sine + AppendVector)"
metadata:
  order: 2
  label: "Rainbow / animated color"
  default_enabled: false
  load_condition: "User asks for rainbow, animated, cycling, pulsing, or party/disco color material"
---

## Rainbow / animated color material

Prefer registry tools (`create_material`, `add_material_expression`,
`connect_material_nodes`, `layout_material_expressions`) — they cover Time /
Sine / AppendVector. `execute_python` is a **labelled last resort** for a graph
the registry cannot express, and it still freezes UEFN if you author many
materials in one script. Call `uefn_editor_python_hints(topic="materials")`
first. **No Custom/HLSL node** in UEFN; use Time → Multiply(speed) → Sine with
phase offsets → ConstantBiasScale → AppendVector.

### Graph (standard nodes)

1. `Time` × scalar param `Speed` → angle (`× 2π`)
2. **R** = `0.5 + 0.5 * sin(angle)`
3. **G** = `0.5 + 0.5 * sin(angle + 2π/3)`
4. **B** = `0.5 + 0.5 * sin(angle + 4π/3)` (use `Add` before each `Sine`)
5. `AppendVector(R,G)` then `AppendVector(rg, B)` → optional `× 1.8` for glow
6. Connect to **BaseColor** and **EmissiveColor**
7. `recompile_material` → `save_loaded_asset` → `assign_material_to_mesh` → `save_current_level`

### Last-resort recipe (paste into `execute_python` only if registry tools cannot express this graph)

```python
import unreal

def _connect(a, ao, b, bi):
    unreal.MaterialEditingLibrary.connect_material_expressions(a, ao, b, bi)

def build_rainbow(asset_name, folder="/MyProject/Materials", speed=0.8):  # content_root — never /Game/
    unreal.EditorAssetLibrary.make_directory(folder)
    at = unreal.AssetToolsHelpers.get_asset_tools()
    mat = at.create_asset(asset_name, folder, unreal.Material, unreal.MaterialFactoryNew())
    mel = unreal.MaterialEditingLibrary
    mel.delete_all_material_expressions(mat)

    def const1(x, y, v):
        e = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, x, y)
        for ch in "rgba":
            e.set_editor_property(ch, float(v if ch != "a" else 1.0))
        return e

    def bias_scale(x, y, inp, bias=0.5, scale=0.5):
        e = mel.create_material_expression(mat, unreal.MaterialExpressionConstantBiasScale, x, y)
        e.set_editor_property("bias", float(bias))
        e.set_editor_property("scale", float(scale))
        _connect(inp, "", e, "Input")
        return e

    time_e = mel.create_material_expression(mat, unreal.MaterialExpressionTime, -900, 0)
    sp = mel.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -900, 160)
    sp.set_editor_property("parameter_name", unreal.Name("Speed"))
    sp.set_editor_property("default_value", float(speed))
    t_scaled = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, -700, 40)
    _connect(time_e, "", t_scaled, "A")
    _connect(sp, "", t_scaled, "B")
    twopi = const1(-900, 300, 6.28318530718)
    angle = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, -520, 40)
    _connect(t_scaled, "", angle, "A")
    _connect(twopi, "", angle, "B")

    sin_r = mel.create_material_expression(mat, unreal.MaterialExpressionSine, -340, -80)
    _connect(angle, "", sin_r, "Input")
    col_r = bias_scale(-160, -80, sin_r)

    off_g = const1(-520, 200, 2.09439510239)
    ang_g = mel.create_material_expression(mat, unreal.MaterialExpressionAdd, -340, 120)
    _connect(angle, "", ang_g, "A")
    _connect(off_g, "", ang_g, "B")
    sin_g = mel.create_material_expression(mat, unreal.MaterialExpressionSine, -160, 120)
    _connect(ang_g, "", sin_g, "Input")
    col_g = bias_scale(20, 120, sin_g)

    off_b = const1(-520, 360, 4.18879020479)
    ang_b = mel.create_material_expression(mat, unreal.MaterialExpressionAdd, -340, 280)
    _connect(angle, "", ang_b, "A")
    _connect(off_b, "", ang_b, "B")
    sin_b = mel.create_material_expression(mat, unreal.MaterialExpressionSine, -160, 280)
    _connect(ang_b, "", sin_b, "Input")
    col_b = bias_scale(20, 280, sin_b)

    rg = mel.create_material_expression(mat, unreal.MaterialExpressionAppendVector, 220, 40)
    _connect(col_r, "", rg, "A")
    _connect(col_g, "", rg, "B")
    rgb = mel.create_material_expression(mat, unreal.MaterialExpressionAppendVector, 400, 80)
    _connect(rg, "", rgb, "A")
    _connect(col_b, "", rgb, "B")
    boost = const1(400, 280, 1.8)
    bright = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, 560, 120)
    _connect(rgb, "", bright, "A")
    _connect(boost, "", bright, "B")

    mel.connect_material_property(bright, "", unreal.MaterialProperty.MP_BASE_COLOR)
    mel.connect_material_property(bright, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    mel.recompile_material(mat)
    mat.modify(True)
    unreal.EditorAssetLibrary.save_loaded_asset(mat, only_if_is_dirty=False)
    return f"{folder}/{asset_name}"

result = build_rainbow("M_Rainbow", speed=0.8)
```

Then assign: `assign_material_to_mesh(actor_path="<label>", material_path=result, slot_index=0)` and `save_current_level()`.
