---
description: "Build a whole city/town step by step — 3 frameworks, 12-step masterplan order, game-scale parameter matrix, centre sizing, build phases, driving-map extras"
metadata:
  order: 25
  label: "Urban masterplan"
  default_enabled: false
  load_condition: "User asks to build, lay out, plan or generate a whole city, town, village, island city, or several districts from scratch"
---

# Urban masterplan — build a city step by step (UEFN)

Source: masterplan-design skill, *Urban Design Skills* (MIT, A. Bhardwaj), turned into a level-build order. Placement tools: this pack's `SKILL.md`, `area_management`, `procedural_generation`, `full_game_director`. Blockout first, dress second.

## Before you start

- Movement: on-foot, driving, racing, mixed → lane widths and block size (`urban_streets`, `urban_design`).
- Footprint: `get_level_bounds` / `area_list`.
- Size: hamlet (1 district), town (2–4), city (5–8 character areas).

## Three frameworks (before any building)

1. **Movement** — entries (bridges, tunnels, spawns), primary routes across the whole site, secondary grid, locals, pedestrian zones, alleys.
2. **Green-blue** — rivers, coast, hills (> 15 % slope stays green), park hierarchy, greenways. Water and green are free edges.
3. **Built form** — centre(s), edges, density gradient, landmark / gateway / terminated-vista sites.

## The 12 steps

| # | Step | Output | UEFN action |
|---|---|---|---|
| 1 | Constraints | buildable vs not (steep, water, edges) | read terrain; mark no-build |
| 2 | Connections | entries, views in/out | spawn-to-city routes, bridges |
| 3 | Primary routes | 2–4 main streets (6–8 large city) crossing the site | boulevards/avenues; follow terrain |
| 4 | Centres | main centre at primary-route junction / station / waterfront | reserve central plaza + landmark |
| 5 | Secondary grid | blocks: 4–6 cells at centre, 8–16 at edges | snap 512; prefer T-junctions; ≥ 1.4 links per node; no unearned dead ends |
| 6 | Density gradient | zone per block T5/T6 → T4 → T3 (`urban_districts`) | colour-code blockout |
| 7 | Blocks | typology per block, passages (`urban_blocks`) | greybox footprint × storeys (384) |
| 8 | Uses | shops on main streets/corners, civic anchors, homes, industry at an edge | label volumes |
| 9 | Public spaces | central plaza, squares, parks near every block (`urban_public_spaces`) | carve from blocks, not leftovers |
| 10 | Climate & theme | widths, H:W, materials (`urban_design`) | one prop family per district |
| 11 | Check | `urban_evaluation` | eye-height fly-through, `measure_distance`, screenshots |
| 12 | Character areas | 3–8 named districts | one Outliner folder per district; dress |

Then dress (`theme_recipes`, `landscape_foliage`), light (`lighting`), devices, QA (`blockout_playtest`).

## Parameter matrix (game scale)

| Context | Storeys | Coverage | Open space | Block side (cells) | Street ROW (uu, driving) |
|---|---|---|---|---|---|
| Rural edge (T2) | 1–2 | 20–35 % | 40–60 % | 12–20 | 1024–1536 |
| Suburb (T3) | 1–3 | 40–50 % | 30–40 % | 8–12 | 1536–2048 |
| Neighbourhood (T4) | 3–6 | 50–65 % | 20–30 % | 6–8 | 1792–2560 |
| Centre (T5) | 4–12 | 60–75 % | 15–25 % | 4–6 | 2560–3072 |
| Core (T6) | 8–40 | 65–80 % | 10–20 % | 4–6 | 3072–4608 |

Streets take 20–30 % of urban area; more → empty asphalt, less → claustrophobic.

Central plaza: width-to-edge-height 2:1–4:1 → town ≈ 2048–4096 across; city 4096–6000 split into rooms.

## Build phases

1. **Enabling:** terrain, water, primary roads, sealed edges.
2. **Catalyst:** the centre — plaza, landmark, first mixed-use blocks, finished to the art bar first.
3. **Growth:** neighbourhood rings, secondary streets, parks.
4. **Maturation:** edges, industrial, rural fringe, passages.
5. **Detail:** dressing, signs, decals, lights, NPCs/traffic.
Each phase ends playable.

## Driving maps (racing, taxi, limo, delivery)

- Loop around the centre + 2–3 cross routes; no dead ends.
- Lanes 512–640; curb radii 384–768; roundabouts at district gateways.
- Straights ≤ 8 blocks, ending in a landmark or bend; one hill, one tunnel/underpass, one bridge.
- Pick-up/drop-off pockets at nodes; destinations are landmarks, navigable without a minimap.

## Summary template

```
CITY: name · mode · playable __×__ uu
Districts: [name — zone — landmark — prop family] × N
Primary routes __ · centre at __ · block size __ cells
Public spaces: plaza __ · parks __ · greenways __
Gradient: T6/T5 at __ → T4 → T3 → T2 edge
Edges: __ · Phases: 1 __ 2 __ 3 __ 4 __
```
