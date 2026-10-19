---
description: "Layout composition principles and per-genre level patterns for popular UEFN modes (box fight, zone wars, deathrun, tycoon, prop hunt, adventure)"
metadata:
  order: 1
  label: "Design styles & layouts"
  default_enabled: false
  load_condition: "User asks to design/build a level, arena, map, or a themed area, or names a mode like box fight, zone wars, deathrun, tycoon, prop hunt"
---

## Level design styles — composition first

### The blockout-first workflow

Never start with final art. Rough the space with simple large props or
building pieces, playtest the FLOW, then dress it. Full fly-through audit:
`blockout_playtest`. Whole-mode order: `full_game_director`.

1. Blockout volumes on the 512 grid (`snap_actor_to_grid` 512).
2. Walk it — sightlines, route times, jump gaps (playtest or camera fly-through
   with `set_viewport_camera` + screenshots).
3. Only then swap in themed meshes and set dressing (small grids: 128/64).

Keep the blockout in an Outliner folder (`set_actor_folder "Blockout"`) so it
can be hidden or deleted wholesale later.

### Composition principles (apply to any theme)

- **One focal point per area** — a landmark visible from spawn orients players
  instantly (tower, statue, glow material). Check it's actually visible: frame
  it from the player path with `set_viewport_camera`.
- **Leading lines & lanes** — paths, fences, and light strips pull players
  toward objectives. `distribute_actors` makes clean rhythm (lamp posts,
  pillars) — even spacing reads as designed, uneven as accidental.
- **Verticality** — flat maps play flat; add a high ground worth fighting
  for, but cap it: dominant high ground with full map sightlines ruins flow.
- **Cover rhythm** — in combat spaces alternate open ground and cover every
  2–4 build cells; `measure_distance` between cover pieces to keep dashes
  survivable.
- **Negative space** — do not fill everything. Dense clusters + open breathing
  room beats uniform clutter.
- **Readability** — gameplay-relevant objects (doors, buttons, hazards) must
  contrast with dressing: distinct silhouette, color, or lighting.
- **Theme consistency** — pick one prop family/palette per zone; a medieval
  keep with one sci-fi crate reads as a bug.

### Genre layout patterns (popular UEFN modes)

Deep rules live in the new refs — use these bullets as the mode pick, then load
`combat_spaces`, `spawn_and_fairness`, `player_flow`, `objectives_in_space`,
`zones_and_boundaries` as needed.

- **Box fight** — small symmetric arena (4–8 cells per side), mirrored spawns,
  flat build-off floor, no third-party angles. Symmetry: build one half, then
  `duplicate_actor` + mirror. Empty floors intentional (`combat_spaces`).
  Barriers until start (`zones_and_boundaries`).
- **Zone wars** — mid-size arena + loot spread; every zone reachable without one
  chokepoint; shrinking playable (`zones_and_boundaries`).
- **1v1 arenas** — strict mirror; identical cover distances
  (`measure_distance` + `spawn_and_fairness`).
- **Deathrun** — linear only; checkpoints every 3–6; kill volumes under jumps;
  seal skips (`player_flow`, `objectives_in_space`, `zones_and_boundaries`).
- **Tycoon** — identical plots (`duplicate_actor`), walk lanes between, clear
  unlock sightlines at entrances (`player_flow`, `poi_hierarchy`).
- **Prop hunt** — plausible prop context; `snap_actor_to_ground` everything;
  dressing layers in `environment_elements`.
- **Adventure / quest hub** — hub + spokes; spoke entrances visible from center;
  shorter returns (`player_flow`, `poi_hierarchy`, `objectives_in_space`).

### Fairness & flow checks before shipping

Full checklists: `spawn_and_fairness`, `blockout_playtest`, `full_game_director`.

- Spawn-to-action time roughly equal for all spawns (route-length eyeball).
- No spawn visible from another spawn (screenshot from each spawn point).
- `get_level_bounds` sanity: is the playable footprint what you intended, or
  did a stray actor at 100000,0 stretch it?
