---
description: "Theme recipes that fill in the environment element system with concrete uu values and prop direction — worked recipes for city, forest, spaceship/sci-fi, dungeon corridors, plus a fill-in template to derive any new theme (castle, underwater, desert ruins...)"
metadata:
  order: 4
  label: "Theme recipes"
  default_enabled: false
  load_condition: "User names a specific theme to build — city, town, village, forest, jungle, spaceship, space station, dungeon, cave, castle, underwater, ruins, backrooms, or any other setting"
---

## Theme recipes — element values per setting

Prereq: the **Environment elements** reference defines the element system
(circulation, volumes, thresholds, landmarks, cover, dressing, boundaries).
A theme is just that checklist with concrete numbers and prop families filled
in. Recipes below; last section is the template for themes not listed.

### City / urban

| Element | Value |
|---------|-------|
| Circulation | Streets 1024 uu, main avenues 1536–2048, alleys 512, sidewalks 256–384 raised beside roads; right-angle grid snapped to 512 |
| Volumes | Building footprints n × 512, storeys 384 (2–4 storeys typical); city blocks 4–8 cells per side |
| Thresholds | Storefronts/doors on the street face, 256–512 wide; garage/loading doors up to 1024 |
| Landmarks | One tall structure per district, visible from street level at district entrances |
| Cover | Parked cars (~500 uu), dumpsters, planters every 2–4 cells along combat streets |
| Dressing | Lampposts/hydrants via `distribute_actors` (even = urban); one prop family per district — mixing eras per block reads as a bug |
| Boundaries | Unbroken outer building facades or fences; never a road running to the void |

Rules of the theme: buildings either touch flush or leave a walkable alley
≥ 512 uu — never an ambiguous 100–300 uu sliver. Lay the full road network
before the first building. Organize one Outliner folder per district.

### Forest / natural

| Element | Value |
|---------|-------|
| Circulation | Winding paths 512–1024 uu, NO right angles; bends every 2–4 cells |
| Volumes | Clearings 2000+ uu across as the gameplay rooms; connect via paths |
| Thresholds | Path mouths framed by paired trees/rocks so entrances read |
| Landmarks | One oversized tree, rock spire, or ruin per region |
| Cover | Trunks, boulders, and fallen logs double as cover — check spacing with `measure_distance` |
| Dressing | Tree spacing tiers: sparse 1500–2500 uu, medium 1000–1500, dense 600–1000; random yaw + scale variance on ALL foliage (never devices); layers: canopy trees → bushes/rocks (128) → ground scatter (64) |
| Boundaries | Tree lines 2–3 rows deep or cliffs; a single row of trees leaks the skybox |

Rules of the theme: `snap_actor_to_ground` every tree — floating canopies and
buried trunks betray the scene; on slopes trust only `get_ground_z` method
"trace". Uniform spacing reads as a tree farm — jitter positions. Verify
combat sightlines through trunks with an eye-height (~170 uu) screenshot.
Mass scattering: `foliage_list_sources` → `foliage_scatter(sources=Content Drawer `_C` paths)`.
Spawn `_C` first pass — skip mesh / BakeData / HLOD hits. See **Procedural generation**.

### Spaceship / sci-fi station

| Element | Value |
|---------|-------|
| Circulation | Corridors 384–512 uu, main spine 768–1024; strict grid, right angles or 45s |
| Volumes | Crew rooms 1–2 cells, ceilings 384–512; hangar/bridge/reactor go grand — 768+ ceilings, 4+ cells |
| Thresholds | Airlock-style doorframes at every volume transition, strong contrast (lit frames); 256–512 wide |
| Landmarks | The grand volumes ARE the landmarks — reactor glow, bridge windows visible down the spine |
| Cover | Consoles, crates, bulkhead ribs every 2–3 cells in fight corridors |
| Dressing | Greebles/pipes/panels on the 64 grid; repeat modules via `duplicate_actor` — repetition reads as engineering, drift reads as sloppy |
| Boundaries | Hull — FULLY enclosed, zero skybox leaks; `measure_distance` surface gap = 0 at every module seam |

Rules of the theme: build from repeated modules (corridor piece, door piece,
room shell) and `duplicate_actor` + `align_actors` them; hand-placed one-offs
break the manufactured look. Lighting is the wayfinding — one accent color
for the main route, another for side areas.

### Dungeon / closed corridors

| Element | Value |
|---------|-------|
| Circulation | Tight 256–384 uu for tension, standard 512; loops beat dead ends — every dead end must pay out (loot, secret) |
| Volumes | Modular rooms 2–4 cells; keep entry/exit openings at consistent positions per module so kits chain cleanly |
| Thresholds | Doorways 256 × 384 minimum; gates/portcullis for gated progression |
| Landmarks | Distinct feature per junction — brazier, statue, banner — so players can navigate without a map |
| Cover | Pillars and crates at corners for peeking; chokepoints on purpose at room entrances |
| Dressing | Torch/light rhythm via `distribute_actors`; debris scatter on 64 grid, denser in old/ruined wings |
| Boundaries | Solid rock/wall everywhere; kill volume under every pit and gap |

Rules of the theme: build one room kit, verify its seams (`measure_distance`
gap 0), then `duplicate_actor` per room — never hand-rebuild. No corridor
longer than 6 cells without a junction or bend. Interior = sealed: screenshot
down every corridor to catch light leaks.

### New theme template

For any theme not listed (castle, underwater base, desert ruins, backrooms,
farm, volcano lair...), fill one line per element, then follow the standard
build order:

```
Theme: ___
Circulation: widths + straight or winding + grid angle
Volumes:     room/space sizes, ceiling tier (384 tight / 768 grand), open or enclosed
Thresholds:  door style + width, what makes them contrast
Landmarks:   one per zone — what is it, where visible from
Cover:       what props double as cover, spacing
Dressing:    prop family (ONE per zone), rhythm (even=man-made / jitter=natural), 3 layers
Boundaries:  material (walls/cliffs/hull/trees/fog), sealed or open-air
```

Sanity rules that never change: element numbers come from the element system
(cell 512, storey 384, opening 256 × 384); one prop family per zone;
`get_actor_bounds` one sample mesh before mass placement; blockout first,
dress second (see **Design styles & layouts**).
