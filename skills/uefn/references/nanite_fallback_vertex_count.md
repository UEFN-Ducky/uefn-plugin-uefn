---
description: "ValkyrieValidator_StaticMesh 'Vertex count of LOD0 of this Static Mesh's render data is too high (30,000)' blocks launch even with Nanite on — the Nanite fallback mesh is counted; set fallbackTarget PercentTriangles with EditorToolset.ObjectToolset.SetProperties (43.00; was ObjectTools.set_properties), find every offender with one execute_tool_script"
metadata:
  order: 22
  label: "Validator: Vertex count of LOD0 too high (Nanite)"
  default_enabled: false
  load_condition: "Validator error 'Vertex count of LOD0 ... too high', ValkyrieValidator_StaticMesh vertex limit, 30,000 vertices, a Nanite static mesh blocking launch or publish"
---

# Validator: "Vertex count of LOD0 ... too high (30,000)" on Nanite meshes

## Symptom: Vertex count of LOD0 too high blocks launch

`ValkyrieValidator_StaticMesh`: **"Vertex count of LOD0 of this Static Mesh's render data is too
high (30,000)"** blocks Launch Session, even though Nanite is enabled on the mesh.

## Cause: the validator counts the Nanite fallback mesh

For a Nanite mesh, render-data LOD0 is the **Nanite fallback** mesh. The default fallback
(`fallbackTarget: Auto`, `fallbackPercentTriangles: 1`) keeps every triangle, so the fallback is as
heavy as the source.

## Fix: shrink the fallback

No visual change: Nanite still renders the full mesh. Epic MCP (43.00 names; 42.40 used
`ObjectTools.set_properties` / `StaticMeshTools.get_vertex_count` / `AssetTools.*`), per offending StaticMesh:

1. `EditorToolset.ObjectToolset.SetProperties` on the StaticMesh (`instance` = its ref) with
   `values = {"NaniteSettings":{"bEnabled":true,"fallbackTarget":"PercentTriangles","fallbackPercentTriangles":0.5,"generateFallback":"Enabled"}}`
   (0.4–0.7; lower for denser meshes).
2. `EditorToolset.StaticMeshToolset.GetVertexCount(mesh, lodIndex=0)` — it rebuilds immediately. Aim for **≤ 27,000** for margin;
   still too high → lower the percent and repeat.
3. `EditorToolset.AssetToolset.SaveAsset(assetPath)`, then `validate_uefn_asset` → VALID.

Never decimate or re-import the source, and never turn Nanite off for this.

## Find every offender in one pass

One `ProgrammaticToolset.execute_tool_script`:

- `EditorToolset.AssetToolset.FindAssets(filter={"folderPath": "/<project mount guid>", "assetType": "StaticMesh"})`. The mount
  is the **project GUID path** (e.g. `/2d01d3f6-.../`), not `/Game` or `/<ProjectName>`; take it
  from `get_project_info().content_root`.
- `StaticMeshToolset.GetVertexCount` on each; fix those **> 27,000** as above, then save.

LimoRide: 63,862 → 24,749 and 43,951 → 24,366 vertices, all VALID.
