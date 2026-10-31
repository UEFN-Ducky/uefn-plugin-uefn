---
description: "Urban design for cities — real-to-UEFN unit conversion, Lynch/Jacobs/Gehl/Alexander/Cullen/Sitte theory, enclosure ratios, city anti-patterns, router to the urban_* subskills"
metadata:
  order: 20
  label: "Urban design (cities)"
  default_enabled: false
  load_condition: "User builds a city, town, village, downtown, suburb, district, neighborhood, street network, or asks how to make a city feel real, readable, or believable"
---

# Urban design for UEFN cities — start here

Adapted from *Urban Design Skills* by Abhinav Bhardwaj (MIT License, © 2026,
github.com/Abhinavbwj/Urban-Design-Skills-Claude). Real-world planning numbers
are converted to Fortnite/UEFN scale and level-design practice.

The `urban_*` subskills decide **what a city should be**; the rest of this pack
(`theme_recipes`, `environment_elements`, `player_flow`, `cinematic_composition`)
decides **how you place and verify it**.

## Router

| Task | Load |
|---|---|
| Lay out a whole city / town / district | `urban_masterplan` |
| Roads, sidewalks, intersections, roundabouts, driving lanes | `urban_streets` |
| Blocks, footprints, heights, towers, courtyards | `urban_blocks` |
| Plazas, parks, squares, waterfronts, playgrounds | `urban_public_spaces` |
| Downtown vs suburb vs rural edge, frontages, district themes, ruins/industrial | `urban_districts` |
| Score a city layout | `urban_evaluation` |

## Unit conversion (real → UEFN)

1 uu = 1 cm. Fortnite is slightly heroic in height and compressed in distance.

| Real-world quantity | UEFN value | Rule |
|---|---|---|
| Street, sidewalk, lane widths | real m × 100, snap to 128 | 2.4 m sidewalk → 256 |
| Storey (3.0–3.5 m) | **384** | Fortnite wall tile height |
| Ground-floor shop (4–5 m) | **512** | taller ground floor reads "commercial" |
| Building depth 12–18 m | 1024–1536 (2–3 cells) | cell = 512 |
| City block 60–120 m | **compress**: 2048–4096 on-foot, 4096–8192 driving maps | real blocks are too big to be fun on foot |
| 5-min walk (400 m) between "things to do" | 15–25 s of player travel | time it in playtest; budget in seconds |
| Ratios: H:W, coverage %, FAR, open-space % | **unchanged** | ratios are scale-free |

## The theory that makes cities readable

**Kevin Lynch — 5 elements.** Every city level needs all five; a missing one is why players get lost.
- **Paths** — street network; hierarchy visible (avenue wider/brighter than alley).
- **Edges** — rivers, rail, walls, highways; district borders and map boundaries.
- **Districts** — one shared character each (one prop family per district).
- **Nodes** — junctions/plazas where paths meet; objectives, shops, spawns.
- **Landmarks** — one tall/unique thing per district, visible from its entrances.

**Jane Jacobs.** Mixed uses, **short blocks** (frequent corners = route choice = flanks), buildings of varied age, enough density. *Eyes on the street*: windows/doors facing the street make it alive and give vantage points.

**Jan Gehl.** Activity happens at **edges**, not in empty middles. Active facade = a door/window every ~1–2 cells at eye level on hero streets.

**Christopher Alexander.** Small squares 15–21 m (1536–2048 uu) feel best; > 4 storeys loses connection to the street; mark district entries with **gateways**; outdoor space must be **positive** (enclosed, convex), never leftover.

**Gordon Cullen — serial vision.** A street is a sequence of reveals. Bent streets build anticipation; **terminated vistas** pull movement (see `cinematic_composition`).

**Camillo Sitte.** Plazas are outdoor rooms: width = 1–2× surrounding building height; monuments off-centre.

**Ian Bentley.** Permeability, variety, legibility, robustness, richness, personalization (lived-in details).

**Space syntax (Hillier).** The most-connected streets get the most traffic → shops, loot, fights there; quiet homes on segregated streets.

## Enclosure — height : street width

| H:W | Feel | Use |
|---|---|---|
| ≤ 1:6 | no enclosure, sprawl | edges, rural |
| 1:3 – 1:1 | good street room | most streets |
| 1:1 – 2:1 | tight, intimate | old town, markets, alleys |
| ≥ 3:1 | canyon, dark | downtown towers — add lights, deliberate only |

## Anti-patterns

1. **Superblock without passages** — block face > 8 cells with no mid-block alley (≥ 512 wide).
2. **Parking lots fronting the street** — dead frontage; park behind buildings.
3. **Dead-end networks** — every dead end pays out (loot, secret, view) or connects.
4. **Single-use zones** — mix a corner shop, park, landmark into every neighbourhood.
5. **Blank walls on hero streets** — doors, windows, signs, murals.
6. **Oversized roads** — width follows hierarchy.
7. **Empty plaza** — add edges, cover, seating props, a focal point.
8. **Rigid grid over hills** — follow contours where grade > 5–8 %; stairs/terraces.
9. **Road into the void** — every road ends at an edge, landmark, tunnel or bend.
10. **Ambiguous slivers** — buildings flush or ≥ 512 apart (same rule as `theme_recipes`).
11. **Uniform heights** — vary 1–2 storeys per block; corners taller.
12. **Mixed eras per block** — one prop family per district.

## Climate → visual language

| Climate | Streets | Buildings | Dressing |
|---|---|---|---|
| Hot-arid | narrow, H:W 2:1–3:1 for shade | courtyards, thick walls, light colours | arcades, awnings, shade sails, fountains |
| Tropical | wide, rain channels | raised on stilts, deep eaves | dense canopy 40–50 %, verandahs |
| Temperate | H:W 1:2–1:1 | perimeter blocks, mixed | deciduous trees, cafés |
| Cold | compact, sheltered | dense, dark paving | covered walkways, evergreens, snow piles |
