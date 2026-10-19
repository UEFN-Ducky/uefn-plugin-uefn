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

**B1 — Precise (few props):** compute positions, then one `spawn_actor` per actor
with `check_area_clear` / `snap_actor_to_ground` / folders.

**B2 — Large greybox (preferred for cities/forests):** after surveying a clear
footprint, `blockout_layout` / `area_create` / `pcg_generate` / `foliage_scatter`
with Content Drawer `_C` `sources=` from `foliage_list_sources` (skip mesh / BakeData / HLOD hits).
Leftover cubes: serial `spawn_actor(..., label=..., folder=...)` — one per
assistant message. Never an `execute_python` spawn loop (freezes UEFN).

Non-negotiables:

- **Deterministic seed.** Derive every position from an explicit seed the user
  can re-run (say the seed in your summary). Same seed → same level.
- **Clear the site first.** `check_area_clear` on the full footprint before bulk
  place. For precise mode, clear each spot; for greybox, clear once then place
  from computed coords via layout tools / serial `spawn_actor`.
- **Tag the generation**: every spawned actor gets a folder like
  `Generated/<name>` or `BlockoutCity/...` + labels. Regenerate foliage =
  `foliage_clear_generated` then re-scatter Creative sources. Never regenerate
  on top of a previous run. Never `delete_actors` (refused).
- **Never revive `spawn_actor_batch` / `batch_commands`.**

### Pattern cookbook (positions you compute)

- **Grid + jitter** — rows/cols at `spacing`, each offset by ±jitter (< 40% of
  spacing keeps rows readable). Streets/orchards/crates.
- **Scatter with min-distance** — random points, reject any closer than
  `min_dist` to an accepted point (track accepted list), then
  place survivors (`spawn_actor(..., label=..., folder=...)` — one per turn).
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
