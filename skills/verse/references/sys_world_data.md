---
description: "World data instead of raycasts — export any level's layout (ground height, paths, obstacles, zones, nodes, routes, navigation graph) as generated Verse data and query it: flat []int arrays, ≤ ~250 KB generated data total (bigger fails launch with 'Failed to connect to beacon'), spatial hash, stub-first API, seeded RNG, shared timed cycles"
metadata:
  order: 27
  label: "Game systems — world data (no raycasts)"
  default_enabled: false
  load_condition: "Verse needs to know the ground height, the nearest path, obstacles, water or zones at a position (vehicles, NPC paths, AI, GPS, minimap, safe respawn, placement checks), or a procedural layout needs reproducible random"
---

# World data in Verse (no raycasts)

Verse can't trace against meshes. Anything that asks "what is under or near me" reads a
**generated data module** built from the same plan that placed the level (for example
`leveldesign` → `urban_procedural_city`, or any layout you generate or export):

- vehicles, mounts or custom movement following the ground and paths;
- NPCs and crowds walking routes and avoiding obstacles;
- GPS lines, minimaps and quest pointers;
- safe respawn / exit spots (not in water, not inside a wall);
- runtime placement checks for spawned props.

## Layout

```
Content/Verse/WorldData/
  world_data_api.verse     # hand-written: types and queries, the only file consumers read
  world_data_gen_0.verse   # generated: flat []int arrays; all gen files together ≤ ~250 KB
```

Consumers write `using { WorldData }` and never edit the module. The generator owns the gen files.
Rename the module per game if several layouts exist.

## Rules

1. **Stub first.** Write the API with tiny stub data (one path, one obstacle, flat ground) and
   build it before the real data exists, so every consumer compiles in parallel.
2. **Flat `[]int` arrays, never a struct literal per element.** `PathX:[]int = array{…}` (cm,
   headings ×10) plus accessor functions that decode them (`GetNode(I)`, `RoutePoint(R, I)`).
   Ragged lists = one flat values array + one start-offset array. Build adjacency and other
   derived tables at runtime in `OnBegin`, never as a literal.
2b. **Size budget (HARD): all generated Verse data ≤ ~250 KB total.** The session server builds
   the bytecode on load; past the 30 s beacon timeout the launch fails at Downloading with
   "Failed to connect to beacon", which looks like a network error. Cut resolution before writing:
   terrain grid 32 m not 8 m, GPS graph junction nodes only, routes Douglas-Peucker ~1.5 m.
   Splitting modules to dodge the 16 MB bytecode cap means you are already far over.
   Symptom and recovery: `skill_read_subskill("uefn", "launch_beacon_failure")`.
3. **Store cm in UEFN space**, relative to the level's anchor. The generator converts; Verse never does.
4. **Spatial hash for anything searched by position** (obstacles, path samples, zones): fixed
   cells (e.g. 64 m) in CSR form — `CellStart` (cells + 1 entries) and `CellItems` — and query
   only the 3×3 cells around the point.
5. **Only what code reads.** Visual-only props cost build time and nothing reads them.
6. **Regenerate, never hand-edit** the gen files. The source is the plan file on disk, not data
   held only in a running tool (it is gone after a restart).

## API shape (take what the game needs)

| Query | Use |
|---|---|
| `GroundZ(X, Y):float` | walk/drive height: path surface first, then the terrain grid |
| `GroundZNear(X, Y, Z):float` | multi-level places: the surface closest above/below `Z` (bridges, decks, floors) |
| `IsWater[X, Y]`, `InZone[X, Y, Kind]` | hazards, regions, safe spots |
| `PathNearest[X, Y]:path_hit` | point, heading, kind, half width — follow a lane or route, respawn on a path |
| `ObstacleHit[Box]:push` | box-vs-obstacle → push-out direction and depth |
| `Nodes`, `Routes` | junction legs, lane offsets, stop points, control type |
| `NavNearestNode`, `NavPath(From, To)` | Dijkstra / A* over the path graph for GPS or NPC routes |
| `MapUV(X, Y)` | world → minimap texture UV |

## Spatial hash cell

```verse
CellSize<public>:float = 6400.0

# MinX, MinY, CellsX, CellsY come from the generated file.
CellIndex(X:float, Y:float)<transacts><decides>:int =
    CX := Floor[(X - MinX) / CellSize]
    CY := Floor[(Y - MinY) / CellSize]
    CX >= 0
    CY >= 0
    CX < CellsX
    CY < CellsY
    CY * CellsX + CX
```

Then, for each of the 3×3 cells, walk `CellItems` from `CellStart[C]` to `CellStart[C + 1] - 1`.

## Seeded random

`/Verse.org/Random` can't be seeded. For a layout that is the same for every player in a
round, and for fixed-seed tests:

```verse
seeded_rng := class:
    var State:int = 1

    Next()<transacts>:int =
        if (S := Mod[State * 1103515245 + 12345, 2147483648]):
            set State = S
        State

    # Lo..Hi inclusive
    Range(Lo:int, Hi:int)<transacts>:int =
        if (V := Mod[Next(), Hi - Lo + 1]):
            Lo + V
        else:
            Lo
```

`State` stays below 2^31, so the product fits in `int`. Seed it from the round number or an
`@editable Seed:int`; Play Tester runs use a fixed seed.

## Shared timed cycles (signals, gates, bridges, hazards)

Anything that cycles across the map (traffic lights, drawbridges, lava vents, patrol shifts)
runs on **one shared clock**: phase = `Mod[Elapsed, Cycle]`, with each node's offset and axis
from the data. Example: traffic signals with a 20 s cycle, GREEN 8 s / AMBER 2 s per axis,
axis B offset by half a cycle so A and B are never open together. Movers ask
`MustStop(Node, Axis, DistToLine)`. Find the props **by tag** and update them only when the
phase changes, never every tick (`runtime_pitfalls`).

## Checks

- A `world_data_selfcheck_device` prints PASS/FAIL at game start: `GroundZ` at the anchor =
  anchor Z ± 10 cm, a known path point finds its path, a known obstacle box hits, a nav path
  exists between two POIs. Add `Print("[PTEVENT] …")` lines for Play Tester.
- `workspace_compile_verse` succeeds with the real generated data, not only the stub.
