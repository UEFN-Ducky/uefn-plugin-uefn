---
description: "Director pipeline to build a complete UEFN mode — islandsettings → greybox → flow → combat → spawns → objectives/zones → Verse systems → dress → QA"
metadata:
  order: 0
  label: "Full game director"
  default_enabled: false
  load_condition: "User wants to build a complete game mode, full island, playable match loop, or asks where to start for a whole game not just a pretty map"
---

# Full game director — space + systems in order

Pretty maps without a match loop are demos. This is the **order of work** for a
shippable UEFN mode. Load other leveldesign refs for depth; **do not** re-author
Verse systems — link them.

Scale base (Epic UEFN): 1 uu = 1 cm, grid **512**, wall storey **384**, eye ~**170**.

## One-liner first

Before any cubes:

1. **Mode sentence** — “Players do X until Y wins.”
2. **Win / lose** — score, elimination, timer, race finish, capture.
3. **Player count** — MaxPlayers N → N spawn pads (islandsettings).

If you can’t say the loop in one sentence, don’t blockout yet.

## Pipeline (do not skip steps)

```
1. islandsettings          MaxPlayers + pads + session basics
2. Greybox footprint       SKILL.md greybox / procedural_generation
3. blockout_playtest       eye-height path; fail → re-block
4. player_flow             critical path, junctions, breadcrumbs
5. combat_spaces           cover 96/288, mantle >520, sightlines
6. spawn_and_fairness      LOS-safe pads, equal run-in
7. objectives_in_space     devices on the circulation network
8. zones_and_boundaries    Barrier / kill / OOB / footprint
9. Verse / devices         sys_architecture → rounds/scoring/teams/HUD
10. Dress                  theme_recipes → lighting → cinematic_composition
11. QA                     fairness + screenshots + get_level_bounds
```

Load each step with `skill_read_subskill("leveldesign", "<id>")`.

## Step details

### 1. Session shell
`skill_read_subskill("islandsettings", "session_setup")` (or islandsettings pack).
`wire_player_spawners` when the pad count matches MaxPlayers. Never invent pad
counts — count with `get_all_actors(label_filter=…)` (or Epic `DeviceToolset`).

### 2–3. Greybox then playtest
`blockout_layout` / `area_create` / `pcg_generate` (see leveldesign SKILL.md). Label folders
`Blockout/…`. Serial `spawn_actor` leftovers only — never a bulk `execute_python`
spawn loop. Run `blockout_playtest` **before** theme meshes.

### 4–6. Flow → combat → spawns
Circulation on 512 first (`environment_elements`). Then combat cover pass. Then
spawn pads relative to fight spaces — not the reverse.

### 7–8. Objectives + bounds
Place score/capture/race devices on the path players already take. Seal the
playable footprint. Devices without space design = invisible goals.

### 9. Systems (Verse / Creative)
Start Verse with `skill_read_subskill("verse", "sys_architecture")`, then only
what the mode needs:

| Need | Verse ref |
|------|-----------|
| Rounds / phases | `sys_rounds_timers` |
| Score / win | `sys_scoring` |
| Teams | `sys_teams` |
| NPC waves | `sys_spawning` |
| HUD | `sys_hud` / `sys_hud_template` |

Creative device wiring: uefn pack `creative_devices` / `golden_paths`.

### 10. Dress last
`theme_recipes` → `lighting` → `cinematic_composition`. Art never fixes bad flow.

### 11. Ship checklist
- [ ] Mode one-liner still true in PIE
- [ ] Spawn screenshots: no pad sees another pad / mid-fight LOS
- [ ] Objective visible from approach (eye 170)
- [ ] `get_level_bounds` matches intended footprint
- [ ] MaxPlayers == pad count
- [ ] `save_current_level()`

## Don'ts

- Don't theme before `blockout_playtest` passes.
- Don't write Verse score logic before pads and objectives exist in space.
- Don't duplicate `sys_*` recipes inside leveldesign — link them.
- Don't add 40 Point lights to hide a broken critical path.

## Related

- Spatial atoms → `environment_elements`, `design_styles`
- Deep spatial → `player_flow`, `combat_spaces`, `spawn_and_fairness`, `poi_hierarchy`
- Match glue → `objectives_in_space`, `zones_and_boundaries`
