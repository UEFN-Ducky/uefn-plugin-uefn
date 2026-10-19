---
description: "Recipes: solid color, parameterized, textured, and animated materials via registry tools — wire every pin, validate_uefn_asset before ship"
metadata:
  order: 1
  label: "Creating materials"
  default_enabled: false
  load_condition: "User asks to create or build a material, material instance, or animated effect"
---

## Creating materials

**Folder hard rule:** `get_project_info()` → `content_root` (e.g. `/MyProject/`).
Create only under `{content_root}Materials/...`. **Never** `/Game/Materials` —
that causes unsaved packages and cook `Disallowed reference to /Game/...`.
Omit `folder` on `create_material` and the listener pins the project mount.

**UEFN gate:** after any graph change → **`layout_material_expressions`** →
`recompile_material` → `validate_uefn_asset` → `save_asset`. Never leave nodes
stacked at one position. Missing `Normalize` / `AppendVector` inputs fail cook
on SM5/SM6/ES3_1 even if the viewport looked fine. See `fixing_materials`.

### Solid color (registry only — preferred)

```
# FIRST: get_project_info() → content_root (example /MyProject/)
create_material({"asset_name": "M_Red", "folder": "/MyProject/Materials",
                             "base_color": [1, 0, 0]})
# or omit folder — listener pins content_root + Materials
```

Creates, wires BaseColor, recompiles, and saves in one call.

### Node graphs via registry tools (preferred)

```
create_material({"asset_name": "M_Glow", "folder": "/MyProject/Materials"})
add_material_expression({"material_path": "/MyProject/Materials/M_Glow",
    "expression_class": "Constant3Vector", "pos_x": -300, "pos_y": 0})  # -> index 0
set_material_expression_property({"material_path": ".../M_Glow", "index": 0,
    "property_name": "constant", "value": [0, 1, 1, 1]})             # float lists auto-wrap LinearColor
connect_material_output({"material_path": ".../M_Glow", "from_index": 0,
    "material_property": "emissive_color"})
layout_material_expressions({"material_path": "/MyProject/Materials/M_Glow"})
recompile_material({"material_path": "/MyProject/Materials/M_Glow"})
validate_uefn_asset({"asset_path": "/MyProject/Materials/M_Glow"})
save_asset({"asset_path": "/MyProject/Materials/M_Glow"})
```

`expression_class` accepts the short name (`Multiply`, `Sine`, `ScalarParameter`) or the
full `MaterialExpression*` name. `get_material_expression_info` shows a node's properties
when a `set` fails; `get_material_info` shows blend mode, parameters, and parent.

**Layout:** always call `layout_material_expressions` after wiring. Omitting it is why
opened graphs show every node stacked on top of each other. While adding nodes, set
distinct `pos_x`/`pos_y` (do not default everything to 0,0).

**Before `recompile_material`:** every `AppendVector` has A+B; every `Normalize` has
its vector input; every `Lerp` has A/B/Alpha (or intentional defaults). Delete unused
math nodes — orphans still fail `EditorValidator_Material`.

### Last resort: node graphs via execute_python

Only for a graph the registry tools (`add_material_expression` /
`connect_material_nodes` / `layout_material_expressions`) cannot express.
One material per script — never a batch. This freezes UEFN if you loop.

Reflection gotchas — these WILL bite if ignored:

- `MaterialExpressionConstant3Vector`: `set_editor_property("constant", unreal.LinearColor(r,g,b,1))` — no `.r/.g/.b` attrs.
- `MaterialExpressionConstant`: no `.constant` — `set_editor_property("r"|"g"|"b"|"a", float)`.
- `MaterialExpressionScalarParameter`: `set_editor_property("parameter_name", unreal.Name("Speed"))` + `set_editor_property("default_value", 1.0)`.
- Connect: `MaterialEditingLibrary.connect_material_expressions(src, "", dst, "InputName")`;
  final pins: `connect_material_property(expr, "", unreal.MaterialProperty.MP_BASE_COLOR)`
  (also `MP_EMISSIVE_COLOR`, `MP_ROUGHNESS`, `MP_METALLIC`, `MP_OPACITY_MASK`).
- Always finish: `recompile_material(mat)` → `mat.modify(True)` →
  `EditorAssetLibrary.save_loaded_asset(mat, only_if_is_dirty=False)`.

Skeleton (replace `/MyProject` with your `content_root`):

```python
import unreal
at = unreal.AssetToolsHelpers.get_asset_tools()
folder = "/MyProject/Materials"  # NEVER /Game/Materials
unreal.EditorAssetLibrary.make_directory(folder)
mat = at.create_asset("M_Glow", folder, unreal.Material, unreal.MaterialFactoryNew())
mel = unreal.MaterialEditingLibrary
mel.delete_all_material_expressions(mat)
c = mel.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -300, 0)
c.set_editor_property("constant", unreal.LinearColor(0, 1, 1, 1))
mel.connect_material_property(c, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
mel.recompile_material(mat); mat.modify(True)
unreal.EditorAssetLibrary.save_loaded_asset(mat, only_if_is_dirty=False)
```

### Animated (rainbow / pulse) — standard nodes only

Time → Multiply(speed) → Sine per channel with phase offsets → ConstantBiasScale
(bias 0.5, scale 0.5) → AppendVector → BaseColor/Emissive. Full runnable recipe:
reference **Rainbow / animated color** (shipped with this skill pack). Do NOT reach for
MaterialExpressionCustom — the UEFN editor has no Custom node; standard nodes cover it.

### Stars / starfield / night sky (HARD — one recipe)

This is **not** rainbow and **not** a textured sky. Load
`skill_read_subskill("materials", "starfield_recipe")` and run that graph only.
Never `T_StarField`, never a 5-node texture sky, never Niagara sprites for a
dome. Rebuild an existing `M_StarSky` / `M_Starfield` in place. Opaque Unlit
Two-Sided, emissive only.

### Material instances + parameters

Give the parent material Scalar/Vector/Texture *parameter* nodes (not constants),
then create the instance and drive it:

```
create_material_instance({"asset_name": "MI_X", "folder": "/MyProject/Materials",
                          "parent_material_path": "/MyProject/Materials/M_X"})
set_material_instance_scalar({"material_instance_path": "/MyProject/Materials/MI_X", "param_name": "Speed", "value": 2.0})
set_material_instance_vector({"material_instance_path": "/MyProject/Materials/MI_X", "param_name": "Tint",  "color": [1,0,0,1]})
set_material_instance_texture({"material_instance_path": "/MyProject/Materials/MI_X", "param_name": "Tex",   "texture_path": "/MyProject/Textures/T_X"})
```

### Inspect an existing graph

`list_material_expressions({"material_path": "/MyProject/Materials/M_X"})`
returns indexed nodes for `connect_material_nodes` (from_index/from_output →
to_index/to_input).
