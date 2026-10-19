---
description: "Player flow — critical path, breadcrumbs, junctions, visual guidance, hub/spoke vs linear, eye-height verify (Epic corridor 512)"
metadata:
  order: 8
  label: "Player flow"
  default_enabled: false
  load_condition: "User asks about player path, flow, wayfinding, where to go next, breadcrumbs, junctions, critical path, getting lost, hub and spokes, or navigation"
---

# Player flow — where players go next

Flow is the path players take without a quest marker. If playtesters hesitate at
the same junction, it’s a **design** bug. Build circulation first
(`environment_elements`), then guide.

Epic / UEFN scale: corridor avg **512** wide; walk min **256**; don’t exceed
**~768** or the lane feels empty. No route longer than ~**6 cells (3072 uu)**
without a bend, junction, or break.

## Critical path

1. Write the intended path: `Spawn → Beat1 → Beat2 → … → Win`.
2. Lay that as the **artery** (1024+ uu / 2+ cells for combat-viable) or
   **connector** (512–768) per `environment_elements` tiers.
3. Optional **flanks** are thinner and longer — never clearer than the critical path
   unless you want players to prefer them.
4. `check_area_clear` along the route after dressing — a crate in the lane is a
   choke; do it on purpose.

## Flow shapes

| Shape | Use |
|-------|-----|
| **Linear** | Deathrun, tutorial, on-rails adventure — one forward; seal skips |
| **Hub + spokes** | Quest hub, social lobby — each spoke entrance visible from hub center |
| **Three-lane** | Competitive arenas — close / mid / close with connectors |
| **Open POI graph** | Adventure / zone-ish — majors connected by readable trails |

Pick one shape per mode. Mixing hub + forced linear without gates confuses players.

## Visual guidance (breadcrumbs)

Players should see the next destination from the current spot when possible.

| Cue | How |
|-----|-----|
| Landmark sightline | Major POI framed from approach (`poi_hierarchy`, `cinematic_composition`) |
| Contrast threshold | Door/gate brighter or silhouetted vs wall |
| Warm light pull | Amber key on the correct exit (`lighting`) |
| Asymmetric junction | Correct path wider / brighter / more dressed |
| Elevation | Tall landmark uphill; downhill invites motion |
| Leading lines | Fences, trim, lamp rhythm via `distribute_actors` |

At a T-junction: if both arms look identical, players pick wrong 50% — break symmetry.

## Backtracking

- Return paths **shorter or clearer** than outbound when the mode needs hub returns.
- Dead ends need a readable turnaround (landmark behind, light, wider mouth).
- Don’t hide the only exit behind the camera’s default facing.

## Verify loop (required)

At every junction and beat start:

```
set_viewport_camera({ location near ground + eye ~170 uu, look toward intended next })
take_high_res_screenshot()
```

Ask: “Would I know where to go with no UI?” If no → fix guidance **before** theme art.

Also `measure_distance` along the critical path for spawn→first-action fairness
(`spawn_and_fairness`).

## Don'ts

- Don’t rely on HUD arrows to fix bad geometry.
- Don’t leave infinite straight sightlines (camping + boredom).
- Don’t dress the wrong path more richly than the critical path.
- Don’t skip eye-height checks (top-down lies).

## Related

- Atoms → `environment_elements`
- Combat on the path → `combat_spaces`
- Spawns → `spawn_and_fairness`
- Landmarks → `poi_hierarchy`, `cinematic_composition`
- Whole mode order → `full_game_director`
