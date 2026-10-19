---
description: "General recreate checklist — duplicate masters, instance overrides, MF rebuild order, verify. Any material family."
metadata:
  order: 11
  label: "Recipe recreate checklist"
  default_enabled: false
  load_condition: "Recreating, duplicating, or rebuilding a material recipe / master / instance"
---

# Recreate materials — checklist (any family)

## 1) Prefer duplicate (guaranteed exact)

```
duplicate_material  # source M_* in active project → new name same folder
create_material_instance  # parent M_* → apply scalar/vector/texture overrides
layout_material_expressions  # if graph was edited — never leave nodes stacked
recompile_material → validate_uefn_asset → save_asset → save_current_level()
assign_material_to_mesh
```

## 2) New instance only

1. Load the family recipe + exact defaults subskill.
2. `create_material_instance` with correct parent.
3. `set_material_instance_scalar` / `_vector` / `_texture` for every listed value.
4. World-centre params (`LakeCentre`, `IslandCentre`, etc.) must match the level.

## 3) MF_ missing (new project)

1. Migrate the whole content folder into the **active** project (still project-local).
2. Or rebuild MF_ via `mf_reusable_patterns`, then masters from the family recipe.
3. Never write Engine / AppData / other projects.

## 4) Verify

- `get_material_info` — blend mode, expression_count **< 500**
- **`validate_uefn_asset`** — no Missing Normalize/AppendVector; no illegal refs
- Viewport: depth colour, WPO motion, edge masks, centre vectors
- Prefer `*_Cheaper` when hitching

## Do not

- Skip `save_current_level()` after assign (old look on island)
- Use a Custom/HLSL node at all — UEFN has none (`list_uefn_material_expression_classes`); build curves from standard nodes (`mf_reusable_patterns` shows the acos approximation)
- Hand-rebuild 300+ node masters when `duplicate_material` exists
- Invent a texture / 5-node / Niagara star sky — `skill_read_subskill("materials", "starfield_recipe")` only
