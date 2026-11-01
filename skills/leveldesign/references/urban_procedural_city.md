---
description: "Generate any settlement from a seed — city, town, village, fantasy keep, sci-fi colony, ruins, station decks — in any theme and layout style (grid, organic, radial, linear, terraced, vertical): seed → network → blocks → lots → structures → dressing → one plan file that drives placement and Verse world data; validation, batched placement, regeneration, per-match variation"
metadata:
  order: 26
  label: "Procedural settlements (cities, towns, any theme)"
  default_enabled: false
  load_condition: "User asks to generate, randomise or procedurally build a city, town, village, base, colony, district, ruins, station or any network of paths and buildings, or wants a different layout per seed or per match"
---

# Procedural settlements (seeded) — any theme, any scale

Turns the urban rules (`urban_masterplan`, `urban_streets`, `urban_blocks`,
`urban_districts`, `urban_public_spaces`) into a **generated** layout. It works for any
"paths + parcels + structures" place: a modern city, a medieval town, a frontier village,
a sci-fi colony, a ruined city, a space-station deck, a fantasy capital, a tycoon street.
Same seed → same layout. One plan file feeds the level AND Verse (`verse` → `sys_world_data`).

## 0. Inputs (ask once, then decide)

| Input | Examples | Drives |
|---|---|---|
| `seed` | any int | every random choice |
| movement | on foot · vehicles · mounts · flying · parkour · mixed | path widths, block size, dead-end rule, vertical links |
| footprint + anchor | `get_level_bounds` / `area_list`; any placed device or actor as the origin | world frame: every position is relative to the anchor |
| scale | hamlet (1 district) · town (2–4) · city (5–8) | centres, primary routes |
| layout style | see table below | network step |
| theme + kit | the project's meshes/prefabs, Fortnite prefabs (`content_catalog`), or greybox | structure pick, prop family per district |
| budget | max actors / memory | density, which dressing to skip |

Survey the kit first: each piece's footprint in 512-uu cells, height (storeys × 384 uu), and
tags (use, era, size). No kit → greybox cubes and label volumes; dress later.

### Layout styles (pick per settlement or per district)

| Style | Network rule | Fits |
|---|---|---|
| Grid | orthogonal streets, seeded T-junction removal | modern city, colony, tycoon street |
| Organic | streets follow terrain contours + shortest paths between seeds; irregular blocks | medieval / old town, villages, ruins |
| Radial | ring roads + spokes from a centre (castle, plaza, core) | fantasy capital, fortress town, hub worlds |
| Linear | one spine (road, river, canal, corridor) with lots on both sides | frontier/main-street town, station corridor |
| Terraced | streets along contour lines, stairs/ramps between levels | hillside / cliff towns |
| Vertical | stacked decks linked by lifts, ramps, bridges | space station, megacity, tree city |
| Islands | separate clusters linked by bridges / ferries / jump pads | archipelago, floating islands |

Mixing is normal: an organic old core inside a grid newer town.

## 1. Generate the plan (offline, deterministic)

Run the generator as scratch code in the chat sandbox (`sandbox_run`) or in Blender
(`blender_execute_blender_code`) — never a `.py` in the island. One seeded RNG; never an
unseeded random call.

1. **Constraint mask** — 512-uu cells: water, cliffs/slope > 15 %, hazards, out of bounds = no-build.
2. **Centres** — the main centre (plaza, keep, core, market) near the site middle with seeded
   jitter; larger places add sub-centres at gateways, water, transport or resources.
3. **Primary routes** — 2–4 routes from the centre to the entries (6–8 for big cities), in the
   chosen style. Vehicle maps add a loop; vertical layouts add the main lift/ramp cores.
4. **Secondary network** — fill each district in its style. Block size grows from centre to
   edge (`urban_masterplan` matrix: 4–6 cells core → 12–20 edge). Snap to 512. Keep the graph
   connected, ≥ 1.4 links per node, and no unearned dead ends (none at all for vehicles).
5. **Nodes** — every junction: id, position, legs, and a control type when the game needs one
   (signal, gate, checkpoint, roundabout, portal, lift). Gateways get the strongest landmark.
6. **Blocks** — the faces between paths, inset by half the path width + edge strip.
7. **Zones** — intensity by distance to the nearest centre (Transect T6 → T2 in
   `urban_districts`), re-themed as needed: core/market → residential → outskirts/farms.
8. **Open spaces** — reserve the main plaza/courtyard first (`urban_public_spaces`), then parks,
   yards or gardens by min-distance scatter. Carved on purpose, never leftovers.
9. **Lots** — split blocks along their long side until frontage fits the zone; flag corners.
10. **Structures** — per lot, a kit piece that fits the footprint and the zone's height band;
    face the busiest frontage; zone setback. Landmarks at the centre, at **terminated vistas**
    (end of every long straight) and at gateways. Never the same piece on adjacent lots.
11. **Dressing** — lights, trees, furniture, signs, clutter along paths at a fixed spacing per
    path type; control props (signals, gates, banners) only where step 5 put them, never
    standing in a lane or on a bridge/deck unless designed so.
12. **Gameplay** — spawns at the centre or entries, objectives / missions / shops at landmarks,
    one per district; combat or chase spaces per `combat_spaces`.

### Output: one plan file everyone reads

```json
{"seed": 4417, "anchor": "<device or actor label>", "units": "uu relative to anchor, yaw deg",
 "style": "grid", "theme": "<theme>",
 "paths": [{"id": 0, "kind": "primary", "width": 2560, "pts": [[0, 0, 0], [12800, 0, 0]]}],
 "nodes": [{"id": 12, "pos": [12800, 0, 0], "legs": [0, 3, 7], "control": "signal", "axisA": [0, 7]}],
 "blocks": [{"id": 5, "zone": "core", "use": "mixed", "poly": [[1536, 1536], [6144, 1536], [6144, 6144], [1536, 6144]]}],
 "lots": [{"id": 40, "block": 5, "corner": true, "poly": [[1536, 1536], [3584, 1536], [3584, 3584], [1536, 3584]]}],
 "instances": [{"kit": "<mesh or prefab>", "pos": [2560, 2560, 0], "yaw": 90, "lot": 40, "cat": "Structures"}],
 "pois": [{"kind": "spawn", "pos": [0, -1536, 0]}, {"kind": "objective", "id": 0, "pos": [20480, 9216, 0]}]}
```

Keep it in `%LOCALAPPDATA%/UEFN-Ducky/exports/<Name>/` and copy it to
`%LOCALAPPDATA%/UnrealEditorFortnite/Saved/<Name>/`: UEFN script tools only read files under
the editor's `Saved` folder.

## 2. Validate the plan BEFORE placing

A failure means a new seed or new parameters, never hand fixes in the level.

- Network connected; every block and POI reachable with the game's movement.
- Paths take 20–30 % of the built area (outdoor towns); corridors/decks by `environment_elements`.
- Coverage and heights per zone inside the `urban_masterplan` matrix (or the theme's own table).
- No footprint overlaps a path or another footprint; walkable gaps ≥ 256 uu.
- Control props only on their nodes, outside lanes.
- Main open space within 1 block of the centre; an open space within ~3 blocks of every block.
- Total instances ≤ the budget.
- Score a top-down render of the plan with `urban_evaluation`.

## 3. Build it in UEFN

Masterplan phase order; each phase ends playable and saved.

1. **Ground + paths** — a path kit per segment, or ground/path meshes baked per tile in Blender
   (`procedural-modeling`) and imported (`uefn` import rules: FBX in cm, pre-rotate against
   Epic `import_file`'s 90° turn, complex-as-simple collision on walkable/drivable meshes,
   convex hulls on props). Tiles baked in the anchor frame are placed at the anchor, yaw 0, scale 1.
2. **Centre first** — main space + landmark + first blocks at the art bar.
3. **Structures + dressing** — one `execute_tool_script` per batch of ~500–800 instances read
   from the plan; labels `<Name>_<idx>_<kit>`; Outliner folders
   `Generated/<Name>_<seed>/<District>/<cat>`. Ground snap: 5 downward traces, take the
   median, and compare with the plan's Z (a trace under a bridge or deck hits the deck).
4. **Gameplay actors** — spawns, objectives, control props; give each kind a Verse tag so code
   finds them by tag.
5. **Materials** — one master + one instance per surface group, assigned by slot-name prefix
   (imported slots get a `_NNN` suffix) in one batched `EditorToolset.StaticMeshToolset.SetMaterial`. Never
   default a texture parameter to `/Engine/...` (the validator rejects it and blocks publishing).

**Regenerate:** census `Generated/<Name>_<seed>/`, confirm nothing outside it references those
actors (`get_verse_editables`, Verse tags), delete that folder's actors, place the new seed.
Never place a seed on top of an old one.

## 4. Verify

- Actor count per kit = plan count (exact).
- `get_level_bounds` — no outliers.
- `take_high_res_screenshot` top-down, plus eye-height shots at 3 nodes, the main space and one
  gateway or bridge.
- `urban_evaluation` ≥ its threshold; fix in its order.
- If Verse reads the layout: world data regenerated from the same plan (`sys_world_data`) and compiled.
- `save_current_level()`.

## 5. A different layout every match (runtime)

Editor-time generation is the main route. For per-match variety:

| Way | How | Cost |
|---|---|---|
| Fixed network, varied lots | Paths and ground placed once; at round start a Verse device fills lots from a seeded kit table with Scene Graph prefabs or `SpawnProp` (`verse` → `sys_spawning`) | prop budget per round; pool and reuse |
| District chunk swap | Pre-built chunks per district slot; show one per slot each round | memory for every chunk |
| Room / cell grids | Roguelike Game Designer plugin `rgd_*` (templates → `rgd_build_level_in_uefn`) | grid-of-rooms layouts |

Verse's random is unseeded: use the seeded RNG in `sys_world_data` so a round seed gives every
player (and Play Tester, on a fixed seed) the same layout.

## Report

```
<NAME> · seed <n> · style <style> · theme <theme> · movement <mode> · footprint __×__ uu · anchor <actor>
Paths __ (primary __ / secondary __) · nodes __ (controlled __) · blocks __ · lots __
Instances __ in __ batches (count check ok) · open spaces __ · POIs __
Evaluation __/100 · world data <compiled / not needed>
```
