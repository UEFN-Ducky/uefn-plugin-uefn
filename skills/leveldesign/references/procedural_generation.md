---
description: "Procedural generation best practice in UEFN: the two routes (PCG graphs vs algorithmic placement), seeded patterns, collision-checked spawning, cleanup and perf budgets"
metadata:
  order: 2
  label: "Procedural generation"
  default_enabled: false
  load_condition: "User asks for procedural/PCG generation, scattering many props, random layouts, mazes, dungeons, forests, or generated arenas"
---

## Procedural generation — two routes

### Route A: PCG graphs (when a graph already exists)

`pcg_get_graph_info` on the actor's PCGComponent, then `pcg_generate` with
`force=true` (cleanup + regenerate). **Graph editing is not exposed** — graphs
are authored in the editor; tools can only inspect metadata and regenerate.
Prefer this route for foliage/scatter the project already has a graph for.

### Route B: algorithmic placement

Two sub-routes:

**B1 — Precise (a few props):** compute positions, then `spawn_actor` per actor
with `check_area_clear` / `snap_actor_to_ground` / folders. Five or more actors →
B2's batch script instead.

**B2 — Large (cities, forests, thousands of props):** compute every position offline
into a plan file (seeded), then place it with **one Epic `execute_tool_script` per
batch of ~500–800 actors** (thousands of actors in a handful of batches). The script
tools read files only under `%LOCALAPPDATA%/UnrealEditorFortnite/Saved/`, so stage the
plan there. Greybox alternatives: `blockout_layout` / `area_create` / `pcg_generate` /
`foliage_scatter` with Content Drawer `_C` `sources=` from `foliage_list_sources`
(skip mesh / BakeData / HLOD hits). Never an `execute_python` spawn loop (freezes UEFN).
Cities, towns, villages, colonies, bases, ruins (any theme): `urban_procedural_city`.

Non-negotiables:

- **Deterministic seed.** Derive every position from an explicit seed the user
  can re-run (say the seed in your summary). Same seed → same level.
- **Validate the plan before placing** (overlaps, walkable gaps, budget). A bad
  plan means a new seed, not hand fixes in the level.
- **Clear the site first.** `check_area_clear` on the full footprint before bulk
  place.
- **Tag the generation**: every spawned actor gets a folder like
  `Generated/<name>_<seed>/...` + labels. Regenerate = census that folder, check
  nothing else references its actors (`get_verse_editables`, Verse tags), delete
  them with Epic `unreal__*` actor tools, then place the new seed. Foliage:
  `foliage_clear_generated` then re-scatter. Never regenerate on top of a
  previous run.
- **Count check:** actors placed per kind = plan count.
- **Never revive `spawn_actor_batch` / `batch_commands`.**

### Pattern cookbook (positions you compute)

- **Grid + jitter** — rows/cols at `spacing`, each offset by ±jitter (< 40% of
  spacing keeps rows readable). Streets/orchards/crates.
- **Scatter with min-distance** — random points, reject any closer than
  `min_dist` to an accepted point (track accepted list), then
  place survivors (B2 batch script; `spawn_actor` only for a handful).
- **Radial** — N points on a circle (angle = i·2π/N): arena cover, stone
  circles, spawn rings.
- **Path/corridor** — walk a polyline; place segments every `step`.
- **Rooms + corridors (dungeon)** — non-overlapping rectangles padded by wall
  thickness; door gaps ≥ 256 uu.
- **Maze** — generate on paper first (recursive backtracker on a cell grid,
  cell = 512 uu), then place wall pieces.

### Budgets & performance

- Set a **hard actor budget before generating** (density × area). Hundreds of
  actors: fine. Thousands of individual small props: editor pain — prefer bigger
  combined meshes or lower density.
- Spawn in modest passes and screenshot between passes when iterating by hand;
  for one-shot greybox, `blockout_layout` / `area_create` plus one screenshot
  is enough. Never a Python spawn loop.

### Verify a generation

1. `get_level_bounds` — footprint sane, no runaway outliers.
2. Screenshot from 2–3 cameras plus one top-down.
3. Spot-check walkable gaps (≥ 256 uu where players pass).
4. `save_current_level()`.
