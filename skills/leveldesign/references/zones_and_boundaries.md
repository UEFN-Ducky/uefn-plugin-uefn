---
description: "Zones and boundaries — playable footprint, Barrier/kill volumes, OOB, sealed seams, storm-feel shrink at device level, get_level_bounds sanity"
metadata:
  order: 14
  label: "Zones & boundaries"
  default_enabled: false
  load_condition: "User asks about map bounds, out of bounds, kill volumes, barriers, playable area, storm circle, sealing the map, or level bounds wrong"
---

# Zones and boundaries

Contain the playable space so players never see the void or walk off the island.
Theme picks the **material** (cliff, hull, tree line); the **job** is identical
(`environment_elements` Boundaries).

## Playable footprint

1. Decide intended min/max in cells (512 uu).
2. Build soft or hard edges: facades, cliffs, fog, Barrier devices, kill volumes.
3. `get_level_bounds` — if a stray actor sits at 100000,0, the “level” is a lie;
   delete or move it.

Open themes: **2–3 rows** of boundary depth (trees/rocks), not a single paper wall.
Enclosed themes (ship, dungeon): **fully sealed** — `measure_distance` seams; 20 uu
slivers are peek exploits and light leaks.

## Tools / devices

| Tool | Use |
|------|-----|
| Geometry walls / landscape | Soft world edge |
| **Barrier** device | Invisible/visible keep-in; tile-sized; pre-round team splits |
| Damage / kill volumes | Hard OOB punish |
| Storm / zone devices | Shrinking playable (mode-dependent) |

Inspect real options with Epic `DeviceToolset` `GetDeviceProperties` or `get_all_actors(label_filter=…)`. Barrier / volume / trigger size is a Details property (`Width` / `Height` / `Depth` / zone / tiles) via `SetDeviceProperty` — **never actor Scale** (that breaks Fortnite devices). Barrier size is often in **tiles** (1 tile ≈ one grid cell) — confirm on device.

## Soft vs hard OOB

| Style | Feel | When |
|-------|------|------|
| Soft (fog, scenery) | Immersive | Adventure, social |
| Hard (Barrier + kill) | Competitive clarity | Arena, deathrun, gallery |
| Hybrid | Pretty edge + kill below | Large islands |

Deathrun / race: kill volumes under every fail jump. Galleries: Barrier so players
can’t walk onto targets.

## Storm-feel shrink (device-level)

For zone-wars-like modes: use Storm / volume devices to shrink safe area over
phases — place so final circles land on **interesting mid** geometry, not empty
corners. Don’t reimplement storm math in Verse unless the mode needs custom logic
(`sys_rounds_timers` for phase timing only).

## Pre-match barriers

Box fight / 1v1: Barriers hold players on sides until round start, then disable
via device channels / Verse. Keep Barrier extents matching the greybox
(`design_styles` box fight notes).

## Verify

```
get_level_bounds()
# walk edge: set_viewport_camera along boundary, eye 170
take_high_res_screenshot()
```

- [ ] No void / unfinished skybox from playable path
- [ ] No seam peeks in interiors
- [ ] OOB punish consistent (all edges)
- [ ] Shrinking zones end on usable space

## Don'ts

- Don’t leave one open cliff “because the camera never looks there.”
- Don’t rely on invisible walls without a readable soft cue in adventure maps.
- Don’t stretch bounds with debug cubes left in the level.
- Don’t invent Storm device field names — inspect.

## Related

- Boundary atoms → `environment_elements`
- Objectives inside the zone → `objectives_in_space`
- Spawns inside safe areas → `spawn_and_fairness`
- Director → `full_game_director`
