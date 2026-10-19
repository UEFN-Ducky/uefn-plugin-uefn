---
name: materials
description: "Create, edit, and fix UEFN materials (2026) — registry tools, MF_ patterns, water recipes, publish validators. Stars/starfield/night sky: starfield_recipe ONLY (no textures, no Niagara). Always layout_material_expressions (never leave nodes stacked). Wire every pin; validate_uefn_asset before ship; UEFN ≠ full Unreal"
license: MIT
metadata:
  label: UEFN Materials
  version: 27
  author: UEFN-Ducky
  copyright: Copyright 2026 Mindful Path Company, LLC
  allow_redistribute: true
  managed_by: uefn-ducky
  source_plugin_id: materials
---

# UEFN Materials — create and fix (2026)

**SERIAL saves:** never parallel `save_current_level` with other heavy editor
calls in the same turn (SERIAL: one mutating/editor call per assistant message.).

Ships with the **Materials** desktop plugin (Settings → Store). Enable the plugin
and opt in under Tools & MCPs so material MCP tools are on the `uefn-ducky` bridge.

Materials are edit-time Content Browser assets under the **project content
mount** from `get_project_info().content_root` (e.g. `/catland/Materials` for
project `catland`) — **never** invent `/Game/...` for new island assets.
`/Game/` is wrong for most UEFN islands and causes unsaved packages + cook
errors (`Disallowed reference to /Game/...`). Verse can only *swap* pre-made
materials at runtime — never author graphs.

**UEFN is not full Unreal Engine.** Many UE/editor tricks fail cook/publish here.
Assume Epic’s Valkyrie validators will reject incomplete graphs, illegal Creative
mesh refs, and illegal property overrides — not “it compiled in the material editor.”

**Advanced surfaces:** load `mf_reusable_patterns` for depth fade / sine WPO /
animated UV masks / radial centre / fake specular (water, glass, lava, ice, cloth…).
Water masters + 1:1 defaults: `water_recipes` + `water_exact_defaults`.
**Stars / night sky (HARD):** `skill_read_subskill("materials", "starfield_recipe")`
— that Catland ALU graph only. Never a star texture. Never Niagara sprites for a
sky dome. Never Additive on a UEFN sky (Opaque Unlit Two-Sided).

## Tool ladder (in order)

0. **Epic first:** `ducky_get_status` → when `epic_mcp_online` use
   `editor_toolset.toolsets.material.MaterialTools` (and material_instance) via
   nested `unreal__*`. 5+ graph ops → ProgrammaticToolset `execute_tool_script`.
1. **Listener second — discover:** `list_uefn_material_expression_classes` (build-aware).
2. **Listener second — create/inspect:** `create_material`, `create_material_instance`,
   `duplicate_material`, `get_material_info`, `list_material_expressions`,
   `get_material_expression_info`.
3. **Flags**: `set_material_flags` (two_sided, blend_mode Opaque/Masked/Translucent,
   shading_model) then `recompile_material`.
4. **Graph (Ducky registry — still ahead of execute_python)**:
   `add_material_expression` → `set_material_expression_property` →
   `connect_material_nodes` / `connect_material_output` →
   `disconnect_material_nodes` / `delete_material_expression` / `clear_material_expressions` →
   **`layout_material_expressions` (REQUIRED)** → **`recompile_material`**.
5. **Apply/tune:** Epic MaterialTools when online; else `assign_material_to_mesh`
   (static + skeletal), `set_material_instance_scalar` / `_vector` / `_texture`.
   Never `mesh.set_material` in `execute_python`.
6. **Publish gate (required after any graph/level change):**
   `validate_uefn_asset({"asset_path": "<content_root>/Materials/M_X"})` — also validate the
   level / GameFeatureData if you placed meshes. Fix every `EditorValidator_Material`
   / `AssetValidator_AssetReferenceRestrictions` / `ValkyrieValidator_Properties` hit
   before claiming done.
7. **`uefn_editor_python_hints(topic="materials")`** before any `execute_python`.
8. **`execute_python` + `MaterialEditingLibrary` last** — only for what Epic and
   registry tools cannot express (see **Rainbow / animated color**).

## Graph editing

```
# FIRST: get_project_info() → content_root (e.g. /catland/) — use THAT, never /Game/
list_uefn_material_expression_classes()
create_material({"asset_name": "M_X", "folder": "/catland/Materials", "base_color": [1,0.2,0.2]})
add_material_expression({"material_path": "/catland/Materials/M_X",
    "expression_class": "Multiply", "pos_x": -300, "pos_y": 0})
set_material_expression_property({..., "index": 2, "property_name": "const_b", "value": 5.0})
connect_material_nodes({...})
connect_material_output({..., "material_property": "emissive_color"})
layout_material_expressions({"material_path": "/catland/Materials/M_X"})
recompile_material({"material_path": "/catland/Materials/M_X"})
validate_uefn_asset({"asset_path": "/catland/Materials/M_X"})
save_asset({"asset_path": "/catland/Materials/M_X"})
save_current_level()
```

Indices SHIFT after delete — re-run `list_material_expressions`.

### Graph layout (hard rule — do not skip)

Agents often dump every node at `(0,0)` → open the material editor and **everything is
stacked on one pile**. That is a broken handoff.

**Required after any add/delete/connect/clear of expressions:**

```
layout_material_expressions({"material_path": "<content_root>/.../M_X"})
```

Also while adding: pass distinct `pos_x` / `pos_y` (step ~200–300 in X, ~120 in Y) so
partial graphs are readable before the final auto-layout. Never claim a material is
done if nodes are piled — layout + save asset first.

**Wire-before-ship:** every `Normalize`, `AppendVector`, `Transform`, `DotProduct`,
`CrossProduct`, `Lerp`, `Multiply`, etc. must have **all required inputs connected**.
UEFN’s `EditorValidator_Material` fails cook with e.g.
`(Node Normalize) Missing Normalize input` or
`(Node AppendVector) Missing AppendVector input A` across SM5/SM6/ES3_1 — even if the
viewport looked OK. After wiring: `list_material_expressions` / `get_material_expression_info`
and confirm pins; never leave orphan math nodes in the graph.

## Golden path (visible in level)

```
# content_root from get_project_info — example uses /catland/
create_material({"asset_name": "M_MyColor", "folder": "/catland/Materials",
                 "base_color": [1.0, 0.2, 0.2]})
get_all_actors(label_filter=…) / get_all_actors(label_filter="...")
assign_material_to_mesh({"actor_path": "<label>", "material_path":
         "/catland/Materials/M_MyColor", "slot_index": 0})
validate_uefn_asset({"asset_path": "/catland/Materials/M_MyColor"})
save_current_level()
```

Verify with `get_asset_info` / `get_material_info` / `validate_uefn_asset` — never assume success.

## UEFN hard rules (2026)

- **≤ 500 instructions** per material (Epic) — keep graphs lean.
- **No Custom/HLSL** node in the UEFN material editor. Use Time, Sine, Lerp,
  Panner, Multiply, Clamp, ConstantBiasScale, Noise, HueShift, QualitySwitch, …
- **Prefer `duplicate_material` of a known-good master** (esp. water/ocean) over
  inventing a 100+ node graph. Half-wired oceans fail publish.
- Defaults: Surface / Opaque or Masked / Default Lit; Two-Sided supported.
- Cross-platform: prefer `MF_QualitySwitch_Material_Attributes` for BR quality tiers.
- Naming: `M_` materials, `MI_` instances, `T_` textures; paths under
  **`get_project_info().content_root`** (e.g. `/catland/...`) — leading slash;
  **never** invent `/Game/...` for new island assets (cook fails).
  Never `Game/...` or `Content/...` without the mount.
- After edits: **`layout_material_expressions`** → `recompile_material` →
  **`validate_uefn_asset`** → `save_asset` → **`save_current_level()`**.
  Skipping layout leaves a stacked graph; skipping validate ships cook failures.
- **Water / plane actors:** do **not** place `/Game/Creative/Environments/Meshes/CP_Ground_Plane`
  (or other Creative-only meshes) as persistent island geometry — cook hits
  `AssetValidator_AssetReferenceRestrictions` / GameFeatureData disallowed reference.
  Use a **project-mount** mesh (e.g. `/catland/...`) for water sheets.
- **Do not force Nanite off** on Fort static mesh components
  (`bForceDisableNanite=True`) — `ValkyrieValidator_Properties` rejects illegal
  property overrides. Reset to default; fix LOD/collision another way.

## Reference files

- `references/creating_materials.md` — solid / textured / animated graphs
  Load when: Creating or wiring a new material
- `references/fixing_materials.md` — diagnose broken graphs / publish validators
  Load when: Material looks wrong, won't compile, or submit/cook fails
- `references/rainbow_material.md` — animated color via Time/Sine (execute_python)
  Load when: Rainbow / pulsing emissive effects
- `references/starfield_recipe.md` — procedural ALU starfield (HARD: only star recipe)
  Load when: stars, starfield, night sky, star sky, sky stars, procedural stars
- `references/runtime_materials_verse.md` — Verse can only swap pre-made materials
  Load when: Runtime material changes from Verse
- `references/texture_import.md` — sRGB, normals, ORM, compression
  Load when: Importing textures or maps look plastic / washed out
- `references/pbr_master_instances.md` — `M_` master + `MI_` instances, foliage, emissive
  Load when: Reusable PBR setup or parameter variants
- `references/blender_handoff.md` — rebuild Principled after FBX
  Load when: Mesh came from Blender and materials need remaking
- `references/mf_reusable_patterns.md` — depth fade, WPO waves, UV/masks, radial, fake specular
  Load when: Building MF_ blocks or any animated/translucent advanced surface
- `references/recipe_recreate.md` — duplicate / instance / rebuild / verify checklist
  Load when: Recreating a master or instance from a recipe
- `references/water_recipes.md` — ocean/river/lake/waterfall/beds architecture
  Load when: Water materials (uses mf_reusable_patterns)
- `references/water_exact_defaults.md` — 1:1 scalar/vector/texture tables + MIC overrides
  Load when: Exact water look or param recreate

## Verify

`recompile_material` then `get_material_info`.

## 42.30 notes

- Epic `editor_toolset.toolsets.material_instance.MaterialInstanceTools` (create and set
  MaterialInstanceConstant parameters) joins `MaterialTools` when `epic_mcp_online` —
  uefn `epic_toolsets` for exact tool names.
- The material editor's shader count no longer includes local vertex factory shaders
  when static-mesh usage is off (viewport and platform stats are now right).
- RVT Texture Sample nodes are colored like Texture Sample nodes.
