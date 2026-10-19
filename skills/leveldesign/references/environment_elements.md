---
description: "Universal environment element system — decompose ANY themed space (city, forest, spaceship, dungeon, castle...) into circulation, volumes, thresholds, landmarks, cover, dressing, and boundaries, each with Fortnite-scale uu numbers and the MCP tool that verifies it"
metadata:
  order: 3
  label: "Environment elements"
  default_enabled: false
  load_condition: "User asks to build any themed environment, area, or scene (city, town, forest, spaceship, dungeon, castle, base...) or asks how to structure/scale a space"
---

## Environment element system — build anything from the same parts

Every environment — city street, forest trail, spaceship deck, dungeon crawl —
is the SAME set of elements wearing different props. Decompose the request into
these elements first, assign each a number, THEN start placing. Themes are
recipes over this system (see **Theme recipes**).

Scale base: 1 uu = 1 cm, build cell 512 uu, wall storey 384 uu, player ~190 uu
tall (eye height ~170 uu).

### Scale anchors (check BEFORE mass placement)

Imported/marketplace meshes lie about their scale constantly. Before placing a
mesh in quantity, `get_actor_bounds` on one instance and compare against:

- Player: 190 uu tall — a "door" shorter than 384 or narrower than 256 is decoration, not a door.
- Build cell: 512 × 512 floor, 384 storey.
- Car: ~500 uu long. Room: 2–4 cells. House: 2–3 storeys ≈ 768–1152 uu tall.

If a "building" is 800 uu tall it reads as a shed; if a "crate" is 512 uu it
reads as a room. Fix placement plans to the real bounds — never rescale
Creative devices to compensate.

### Circulation — how players move

Roads, corridors, forest paths, ship passages: all one element with three
width tiers. Critical path / breadcrumbs / junctions: `player_flow`.

| Tier | Width | Feel |
|------|-------|------|
| Artery | 1024+ uu (2+ cells) | main street, ship spine, highway — combat-viable lane |
| Connector | 512–768 uu | side street, standard corridor, forest path |
| Tight lane | 256–384 uu | alley, vent, crawlspace — tense, single-file |

- Lay the circulation network FIRST, snapped to the 512 grid
  (`snap_actor_to_grid` 512); every other element hangs off it.
- Routes stay prop-free: `check_area_clear` along the route before and after
  dressing. A prop in a lane converts the lane to a chokepoint — do that on
  purpose or not at all.
- No route runs longer than ~6 cells (3072 uu) without a junction, bend, or
  break — straight infinite sightlines play badly in every theme.

### Volumes — the spaces players occupy

Rooms, buildings, clearings, hangars, plazas: enclosed or open, same rules.

- Footprints in multiples of 512 uu; interior ceilings ≥ 384 uu (tight) or
  768+ uu (grand — hangar, throne room, atrium).
- Open-air "rooms" (clearings, plazas, courtyards) read as spaces at
  2000+ uu across; smaller reads as a wide spot in a path.
- Size by purpose: fight spaces 2–4 cells minimum per side, transit spaces can
  be corridor-tier, showcase spaces (landmark rooms) go grand-ceiling.
- `find_clear_area` with the full volume extent before committing a location.

### Thresholds — transitions between volumes

Doors, gates, airlocks, bridges, cave mouths, tunnel entrances.

- Walkable minimum 256 wide × 384 tall; generous is 512 × 384.
- Gameplay thresholds must CONTRAST with the wall around them — silhouette,
  color, or light — or players walk past them.
- Sealed edges: `measure_distance` between adjacent wall/hull modules; surface
  gap must be 0. A 20 uu sliver between wall pieces is a peek exploit and a
  visual leak.

### Landmarks — orientation

- One focal point per zone, visible from every entrance to that zone: tower,
  statue, glowing sign, reactor core.
- Verify visibility for real: `set_viewport_camera` at player eye height
  (~170 uu above ground) at each entrance, `take_high_res_screenshot`, look.

### Cover rhythm — combat pacing

Epic readability (UEFN Level Design Fundamentals): **low cover ~96 uu**,
**high cover ≥ 288 uu**, walls that must block mantle clearly **> 520 uu**
(don’t sit near the mantle height). Deep pass: `combat_spaces`.

- Alternate open ground and cover every 2–4 cells; `measure_distance` between
  cover pieces to keep dashes survivable.
- Corners and junctions get peek cover; dead-flat open volumes get 1–2
  islands of cover, not uniform clutter.
- Flow into fights: `player_flow`. Spawns relative to cover: `spawn_and_fairness`.

### Dressing layers — visual density without chaos

Three layers, three grids (`snap_actor_to_grid`):

1. **Primary** (512): structural silhouette — buildings, big rocks, hull
   modules. Defines the space from a distance.
2. **Secondary** (128): mid props — crates, market stalls, bushes, consoles.
3. **Detail** (64): scatter — debris, small foliage, greebles.

- Man-made rhythm: even spacing via `distribute_actors` (lampposts, pillars) —
  even reads as designed. Natural: jitter positions and randomize yaw —
  uniform trees read as a plantation, not a forest.
- Yaw randomization on every organic/scatter prop; scale variance is fine on
  foliage and rocks. NEVER actor-scale Fortnite Creative devices — resize
  volumes/triggers/barriers via Details Width/Height/zone (`SetDeviceProperty`).
- Budget: dress dense pockets and leave breathing room; uniform 100% coverage
  is worse than 60% clustered.

### Boundaries — containing the playable space

The theme picks the material, the job is identical: no player sees or walks
off the edge of the world.

- Options: building facades, cliffs, tree lines, hull plating, fog walls,
  barrier + kill volumes.
- `get_level_bounds` to confirm the intended footprint (one stray actor at
  100000,0 stretches it silently).
- Enclosed themes (ship, dungeon, interior) are FULLY sealed — check every
  module seam; open themes need boundary depth (2–3 rows of trees, not one).

### Grounding & verticality

- `snap_actor_to_ground` everything walkable-adjacent; on slopes trust only
  `get_ground_z` method "trace", re-check "aabb_fallback" visually.
- Add contested high ground worth fighting for, but cap it: dominant high
  ground with full-map sightlines ruins flow in every theme.

### Build order (any theme)

1. Circulation network on the 512 grid.
2. Volumes hung off the network (`find_clear_area` each).
3. Thresholds sealed and contrasted.
4. Landmarks + sightline screenshots.
5. Cover pass, then dressing layers 512 → 128 → 64.
6. Boundary check (`get_level_bounds`), `save_current_level()`.
