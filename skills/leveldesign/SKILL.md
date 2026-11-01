---
source_plugin_id: uefn
name: leveldesign
description: "UEFN level design — spatial awareness, blockout, player flow, combat/spawns, full-game director, themes, lighting, cinematic composition, procedural generation, urban design (cities, streets, blocks, plazas)"
license: MIT
metadata:
  label: UEFN Level Design
  version: 28
  managed_by: uefn-ducky
  author: UEFN-Ducky
  copyright: Copyright 2026 Mindful Path Company, LLC
  allow_redistribute: true
---

# UEFN Level Design — place things CORRECTLY

## Hard rules (every UEFN skill)

1. **Our architecture is the spine** — systems are our packs on `player_manager`; never a second registry, wallet or save table (verse `sys_architecture`).
2. **Scene Graph first** for anything created, moved or animated at runtime; Creative devices for features Fortnite provides; `creative_prop` only as a fallback (scenegraph SKILL.md).
3. **Never animate by teleporting** — keyframed movement, `MoveTo` glides, `SetOrigin`, chairs for carried players, animation assets for characters (scenegraph `movement_transforms`).
4. **No lag** — events over polling, every loop waits, visuals ~10 Hz, pools, shared materials, HUD and saves on change (verse `runtime_pitfalls`).
5. **Everything stops when its owner goes** — stop events on leave and elimination, `defer` cleanup (verse `async`).
6. **One house code style** (verse `code_style`).
7. **Names come from the digest** (verse `digests`).
8. **Done means played** — build, then one live run; two players for multiplayer (verse `runtime_pitfalls`).

Big levels: fewer, larger pieces; build or stream at most one piece per tick; move one parent, not many children (verse `runtime_pitfalls`).

**Epic UEFN MCP FIRST (HARD):** `ducky_get_status` → when `epic_mcp_online`,
place/move/batch via nested Epic `unreal__*` only
(`unreal__list_toolsets` → `unreal__describe_toolset` → `unreal__call_tool`).
Devices → `ValkyrieFortniteToolset.DeviceToolset` (`PlaceDevice`). Actors/props →
`EditorToolset.LevelToolset` (`AddToSceneFromClass`) / `EditorToolset.ActorToolset`. **5+ placements** →
`editor_toolset.toolsets.programmatic.ProgrammaticToolset` `execute_tool_script`
(not a listener `execute_python` loop). PIC/session →
`ValkyrieFortniteToolset.SessionToolset`. Map: `skill_read_subskill("uefn", "epic_mcp")`.

Ducky listener is **second** — spatial facts (`get_actor_bounds`, `find_clear_area`,
`get_ground_z`), `area_create` / `foliage_scatter`, `spawn_actor` for leftover
props Epic cannot place. **`execute_python` is LAST** — never a placement path,
even if Epic MCP and the listener already failed. Do not skip to Python because
other options were “exhausted”. The listener refuses spawn/move/material scripts.

**CRITICAL — editor mutations are SERIAL:** one heavy MCP call (`unreal__call_tool`,
`spawn_actor`, `wire_*`, `set_actor_*`, `save_current_level`) → wait → next.
Never parallel or same-turn multi — that freezes UEFN. Details:
SERIAL: one mutating/editor call per assistant message.. Gameplay SFX/horns = Creative
**Audio Player** only (`creative_devices`) — never prop kits for “horn”.

**Place like Content Drawer (HARD):** search `/Game/Creative/**` → keep only
`BlueprintGeneratedClass` / `*_C`. **5+ Fortnite pieces** → ProgrammaticToolset
`execute_tool_script` → `EditorToolset.LevelToolset.AddToSceneFromClass`
with `actorType.refPath` = full `Package.Asset_C`, then `set_actor_folder`.
**Never** `AddToSceneFromAsset` for `/Game/Creative` — that spawns
`FortStaticMeshActor` and cook-fails `AssetValidator_AssetReferenceRestrictions`.
Devices → `ValkyrieFortniteToolset.DeviceToolset.PlaceDevice` (location + yaw, no Scale).
Skip `StaticMesh`, `/BakeData/`, `/HLOD/`, `SM_*`, `…/Meshes/`. Leftover
`spawn_actor(asset_path=…_C, label=…, folder=…)` only for props Epic cannot place.
Trees: `foliage_list_sources` → `foliage_scatter(sources=those `_C` paths)`.

The #1 level-design failure is placing blind: guessing coordinates, stacking
actors inside each other, floating props. These tools give you the spatial
facts first — sizes, gaps, free space, ground height — so every placement is
deliberate.

## Multi-area maps FIRST (Hub / Store / Arena / …)

When the user wants a **new area**, hub, store, lobby, arena, or separate
“level” footprint — do **not** invent cubes at the origin. Call:

```
area_list()
area_create({"area_id": "hub", "preset": "hub", "seed": 42})
# next area lands 100000 uu away automatically
area_create({"area_id": "store", "preset": "store", "seed": 43})
save_current_level()
```

Each area gets its own mesh terrain + `Areas/<id>/{Terrain,Blockout,Devices,Props,Foliage}`.
Presets: `blockout_list_presets` → hub | store | arena | corridor | lobby.
Always-on rules: `area_management` (injected into the skill prompt). Real Landscape
Mode Create is manual-only — AI path is `terrain_generate` via `area_create`.

## The spatial toolkit (flat MCP tools)

| Question | Tool |
|----------|------|
| How big is it? | `get_actor_bounds` (origin/extent/min/max/size) |
| How big is the level? | `get_level_bounds` |
| How far apart are these two? | `measure_distance` (center dist + SURFACE gap) |
| Does a box fit here? | `check_area_clear` |
| Where DOES it fit near here? | `find_clear_area` (nearest spots first) |
| How high is the floor? | `get_ground_z` |
| **New named area / greybox** | `area_list`, `area_create`, `blockout_list_presets`, `blockout_layout` |
| **Move/arrange** | `set_actor_transform` (location/rotation on devices; **scale only on props**), `snap_actor_to_ground`, `snap_actor_to_grid`, `align_actors`, `distribute_actors`, `attach_actor`, `duplicate_actor` |
| **Organize** | `set_actor_label`, `set_actor_folder`, `set_actor_tags` |

## Fortnite Content Drawer → MCP (Props / Prefabs / Devices)

Content Drawer **All → Fortnite → Props / Prefabs / Devices** is a **UI gallery**, not
`directory="/Fortnite"` (that path is empty). Placeable Creative content is under
`/Game/Creative/...`. Before inventing cubes or guessing paths, load:

`skill_read_subskill("leveldesign", "content_catalog")`

Quick map:

| Drawer | Search under | Devices API (Verse types) |
|--------|--------------|---------------------------|
| Props (walls, floors, clutter) | `/Game/Creative/BuildingActors/{Walls,Floors,Roofs,Props}`, `/Game/Creative/Environments/...`, `/Game/Creative/Sets/<Theme>` | — |
| Prefabs / themed kits | `/Game/Creative/Sets/<Theme>` (no `/Game/Creative/Prefabs` mount) | Scene Graph prefabs → `scenegraph` skill |
| Devices | `/Game/Creative/Devices` (or `/Game/Creative`) → spawn `…_C` | `list_verse_types(digest="fortnite", kind="class", name_filter="_device")` → `get_verse_api` |

Always `search_assets(search=…, directory=…)` — never `query` / `name_filter`.

## Golden path (precise few-prop placement)

```
ducky_get_status                            # 0. Epic first when epic_mcp_online
unreal__* LevelToolset / PlaceDevice         #    official UEFN MCP
get_asset_info / get_actor_bounds           # 1. know the SIZE
find_clear_area({"near": [x,y,z], "extent": [ex,ey,ez]})   # 2. know it FITS
spawn_actor({"asset_path": "...", "location": <spot>, "label": "...", "folder": "..."})
                                            # 3. leftover props only (Epic-offline / Epic cannot place)
snap_actor_to_ground({"actor_path": "<label>"})            # 4. no floating props
take_high_res_screenshot / set_viewport_camera             # 5. LOOK at it
save_current_level()
```

**ALWAYS folder every place** — `set_actor_folder` after every spawn/label. Prefer
`Areas/<id>/Devices`, `Areas/<id>/Props` (from `area_create`). Legacy nesting
(`Hub/Spawners`, `Blockout/COMBAT`) still ok inside an area. See `area_management`
and `blockout_playtest`.

**Screenshots:** call `take_high_res_screenshot` → use the returned `path` under
`%LOCALAPPDATA%/UEFN-Ducky/tool_captures/` (and `media_url`). Chat snips land
there too. **Never** write, copy, or place captures inside the UEFN project
(`Saved/Screenshots`, `Saved/DuckyCaptures`, or anywhere else). Never Bash
`find` / `ls` for `uefn_ducky_screenshot.png`.

Use this for devices, landmarks, and small arrangements. Rows/fences: spawn one at
a time (or a short loop), then `align_actors` + `distribute_actors`.

## Greybox / large blockout golden path (cities, forests, districts)

**Named areas (hub/store/arena/…):** prefer `area_create` + presets (above) over
hand-placed cubes.

When the user asks for a **large custom** greybox (dozens–hundreds of volumes)
that is not a preset, **do not** issue hundreds of `spawn_actor` turns and
**do not** loop `EditorLevelLibrary.spawn_actor_from_object` inside
`execute_python` (refused; freezes UEFN). Use Epic ProgrammaticToolset for 5+
editor ops, or the layout tools, then serial `spawn_actor` only for leftovers:

```
1. area_list / get_level_bounds + check_area_clear   # find empty footprint / slot
2. area_create / blockout_layout                    # named area or preset volumes
3. pcg_generate / foliage_scatter                   # fill when the user wants scatter
4. spawn_actor(..., label=..., folder=...)          # leftovers only — one per turn
5. set_viewport_camera + screenshot                 # verify
6. save_current_level()                             # once at the end
```

Folder under `Areas/<id>/…` or `Blockout/…`. One editor mutator per assistant
message (SERIAL: one mutating/editor call per assistant message.).

Notes:

- Cube mesh: `/Engine/BasicShapes/Cube.Cube` (100 uu). Scale accordingly.
- Folders: e.g. `BlockoutCity/Canal_Water`, `Building_Island_01`, `Perimeter_Walls`,
  `Forest/ForestExit`, `Castle` — everything in its own Outliner folder.
- Budget: hundreds of actors OK; prefer bigger combined masses over thousands of
  tiny props.
- Never `os.walk` Fortnite install / AppData from `execute_python`.
- **Never** `execute_python` to spawn or assign materials. Epic `unreal__*` first;
  listener (`foliage_scatter` / `spawn_actor`) second; Python LAST — never because
  other options were exhausted.

## UEFN metrics (rules of thumb — verify in playtest)

- 1 uu = 1 cm. The Fortnite **build grid is 512 uu** per cell (floors 512×512,
  a wall story ≈ 384 uu tall) — layouts that respect multiples of 512/384 feel
  native and stay build-fight compatible.
- Player is ~190 uu tall: keep walk-through openings ≥ 256 uu wide and
  ≥ 384 uu tall; combat lanes 2+ cells wide.
- `snap_actor_to_grid` with 512 (structures), 128 (props), 64 (detail).
- `get_ground_z` reports its `method`: "trace" is exact; "aabb_fallback" is a
  bounds approximation — trust it on flat floors, re-check slopes visually.

## Hard rules

- **Bounds are AABB** (axis-aligned): rotated long props report bigger boxes —
  after big rotations re-read bounds before trusting gaps.
- **`check_area_clear` before choosing a site**; for layout tools / serial
  `spawn_actor`, clear the footprint first, then place from a deterministic seed.
- **Verify visually.** After a group of placements: frame it with
  `set_viewport_camera`, `take_high_res_screenshot`, and actually look.
- Deep-dives: see **Reference files** below. Complete mode order:
  `skill_read_subskill("leveldesign", "full_game_director")`.

## Full game (mode, not just a pretty map)

When the user wants a **playable match**, start with the director — not theme art:

`skill_read_subskill("leveldesign", "full_game_director")`

Typical chain: islandsettings → greybox → `blockout_playtest` → `player_flow` →
`combat_spaces` → `spawn_and_fairness` → `objectives_in_space` /
`zones_and_boundaries` → Verse `sys_architecture` → dress (`theme_recipes`,
`lighting`, `cinematic_composition`).

## Lighting (mood / day-night / flat gray)

Prefer one key Directional + Sky, then few local Point/Spot accents. Day Sequence
for time-of-day cycles. Always screenshot after tweaks:
`skill_read_subskill("leveldesign", "lighting")`.

## Terrain & foliage (worldgen)

Prefer `worldgen_capabilities` → `terrain_generate` → `foliage_list_sources` →
`foliage_scatter` over placing one tree actor at a time. Details:
`skill_read_subskill("leveldesign", "landscape_foliage")`.

## After ANY layout change

`save_current_level()` — placements are level data.

## Reference files

Load with `skill_read_subskill("leveldesign", "<id>")`:

| Id | When |
|----|------|
| `area_management` | **Always-on** — per-area terrains, 100k slots, `Areas/<id>/` folders |
| `content_catalog` | Find Fortnite Props / Prefabs / Devices via MCP (Content Drawer map); 43.00 Frenzy Fields galleries/prefabs; Gaussian splats (PLY/SPZ photoreal captures, Experimental, visual only) |
| `full_game_director` | Build a complete mode / whole island game loop |
| `blockout_playtest` | Greybox fly-through, fail before dressing |
| `player_flow` | Critical path, wayfinding, hubs |
| `combat_spaces` | Cover 96/288, mantle >520, sightlines |
| `spawn_and_fairness` | Pads, spawn camping, equal run-in |
| `poi_hierarchy` | Major/minor landmarks, skyline |
| `objectives_in_space` | Capture/hold/race/score placement |
| `zones_and_boundaries` | OOB, Barrier, kill volumes, footprint |
| `environment_elements` | Circulation, volumes, cover, dressing atoms |
| `theme_recipes` | City/forest/ship/dungeon concrete numbers |
| `design_styles` | Genre layout sketches |
| `cinematic_composition` | Vistas, reveals, framing |
| `lighting` | Sun/sky/local lights, Day Sequence (stars → materials `starfield_recipe`) |
| `procedural_generation` | PCG in UEFN 43.00 (MCP `PCGToolset`, PCG Library, reusable PCG tools; forests / cities / POIs, seeds) / seeded mass placement |
| `landscape_foliage` | Terrain + foliage scatter |
| `lego_brick_editor` | LEGO islands: Brick Editor mode, Kragle / Separate, brick rules (42.40) |
| `urban_design` | **Cities start here** — real→uu conversion, Lynch/Jacobs/Gehl, city anti-patterns, router |
| `urban_masterplan` | Lay out a whole city/town: 12-step build order, game-scale parameters |
| `urban_procedural_city` | Generate any settlement from a seed (city, village, colony, station, ruins; grid / organic / radial / vertical): network → blocks → lots → structures → plan file, batch placement, per-match variety |
| `urban_streets` | Street hierarchy, cross-sections, driving lanes, intersections, roundabouts |
| `urban_blocks` | Block typologies, building heights, towers, courtyards, corners |
| `urban_public_spaces` | Plazas, parks, promenades — sizes, Gehl criteria, Power of 10 |
| `urban_districts` | Downtown→suburb transect T1–T6, frontages, district themes |
| `urban_evaluation` | 20-item city layout scorecard |

## Verify

`take_high_res_screenshot` of the placed area. Never leave layout unverified.
