---
description: "AI terrain + foliage tools — capability-probed mesh heightfields and instanced foliage scatter (not one actor per tree)"
metadata:
  order: 6
  label: "Landscape & foliage (worldgen)"
  default_enabled: false
  load_condition: "User asks for landscape, terrain, heightmap, foliage, vegetation, forest scatter, biome, or sculpted ground without placing individual tree assets"
---

## Landscape & foliage — worldgen tools

UEFN-Ducky can **form terrain** and **scatter vegetation as instances**, but foliage
still needs source meshes / FoliageTypes. The win is avoiding one StaticMeshActor
per tree and avoiding hundreds of terrain cubes.

### Capability probe first

```
worldgen_capabilities()
→ terrain_backend: mesh | unavailable
→ landscape_create: unavailable
→ landscape_sculpt_existing: noop_no_visible_change
→ foliage_backend: hism | static_mesh_actors | unavailable
```

- **mesh** terrain (`terrain_generate`) = GeometryScript heightfield — the AI create+sculpt path that works.
- **Real Landscape create with panels is unavailable from Python** on this UEFN build:
  `spawn_actor(actor_class="Landscape")` → `LandscapePlaceholder` (0 panels). Panels live on
  `LandscapeStreamingProxy`. Only Landscape Mode → **Create** builds them.
  T3D shows `ComponentSizeQuads` / `GridSize`, but those props are not Python-editable.
  Call `landscape_create` for the structured unavailable response + UI steps; after
  Create, call `landscape_rename`. Use `landscape_list` / `landscape_get_info` for panels.
- **Landscape sculpt via Python is a verified NO-OP on visible terrain.** `landscape_export/import_heightmap_from_render_target` exist and the data round-trips (export reads back what import wrote), but importing a full white/max heightmap left the terrain perfectly flat with proxy bounds Z unchanged — even after `force_layers_full_update()`. So `landscape_sculpt` (verify/add/set) writes only a buffer, not geometry. **For AI-sculpted terrain use `terrain_generate` (mesh).** `landscape_sculpt` is retained for parity in case a future engine build composites imports.
- **Default foliage (`auto`/`actors`)**: Content Drawer Actor Blueprints (`_C`) —
  the same class drag-drop places. Scatter only those `_C` paths. Skip `StaticMesh` /
  BakeData / HLOD hits — never spawn a mesh “and fix later”.
  HISM often does not render; IFA crashes. Cap actor demos ≤120; `foliage_clear_generated`.
- **`placement_mode='hism'`**: experimental HISM containers.

### Golden path (demo biome)

```
worldgen_capabilities({})
check_area_clear / find_clear_area          # pick empty footprint
terrain_generate({
  location, size_uu: 12800, resolution: 65, seed: 42,
  stamps: [
    {type:"hill", x:-2000, y:0, radius:2500, height:1200},
    {type:"valley", x:2000, y:500, radius:2200, height:900},
    {type:"flatten", x:0, y:0, radius:1800, height:0, strength:1}
  ],
  level_folder: "Generated/WorldgenDemo"
})
foliage_list_sources({search:"tree"})       # Content Drawer `_C` + project
# MUST pass sources= from that list (`_C` Blueprints only)
foliage_scatter({
  center, extent, sources:[<paths from foliage_list_sources>], seed:42,
  density_per_100m2: 6, min_distance: 400, max_instances: 120,
  clear_first: true, level_folder: "Generated/WorldgenDemo"
})
set_viewport_camera + take_high_res_screenshot
save_current_level()
```

If `foliage_list_sources` is empty: `search_assets(search="Tree", directory="/Game/Creative/Environments", limit=20)` and scatter the `…_C` Blueprint paths. Skip `StaticMesh` / BakeData / HLOD hits.

### Hard rules

- One heavy editor command per turn (`terrain_generate`, `foliage_scatter`, …).
- Deterministic `seed` required; report it.
- Regenerate = `terrain_remove_generated` / `foliage_clear_generated` then rebuild.
- Budget: resolution ≤ 129; instances ≤ 2500 (default demo ≪ that).
- Never scale Fortnite Creative devices (buttons, triggers, volumes, barriers, pads). Actor scale breaks them. Resize via Details Width/Height/zone (`SetDeviceProperty`). Foliage scale variance is fine on props only.
- Organize under `Generated/WorldgenDemo` and tag `WorldgenGenerated`.

## 43.00 landscape changes

- **Layer Allow List is read-only in Details** on a landscape component. Edit it in
  **Landscape mode** (Paint): select the component, **`=`** adds it to the allow list,
  **`-`** removes it. Paint mode now gives clearer add/remove feedback.
- **Landscape spline tangents** can be manipulated again (fixed).
- **Water Body Island** exposes terrain properties (Affects Landscape etc.) — turn
  Affects Landscape off so it stops overwriting sculpting.
- Fixed crashes: older landscapes without edit layers, grass type name conflict /
  duplicate grass types, Landscape Layer Blend with an invalid Height input, closing the
  editor via Python in Landscape Mode. Shortcuts (comma, period, Esc) no longer fire
  while typing; no shader warnings entering Landscape Paint.
- Big scatter (forests, fields) → PCG is now in UEFN: see `procedural_generation`.

## 42.30 landscape changes (42.40 repeats the Layer Allow List and proxy right-click fixes)

- **42.40:** WaterBodyIsland exposes its terrain properties.

- **WaterBodyIsland** now exposes **Affects Landscape** — turn it off so the island
  stops overwriting your sculpting.
- Paint mode **Layer Allow List**: the cursor and target-layer indicator show
  add-to / remove-from allow list.
- A grass-name clash on fallback fixup is now a log warning plus a **Map Check**
  warning with an action to force-rebuild landscape grass data (it used to assert).
- Landscape shortcut keys (comma, period, Escape) no longer fire while typing in a text box.
- Crashes fixed: brush stroke starting in a deleted region (steep angles), loading old
  landscapes without edit layers, right-clicking a landscape proxy.
- RVT Texture Sample material node now has the same color as a Texture Sample.
