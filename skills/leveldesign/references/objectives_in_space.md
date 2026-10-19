---
description: "Objectives in space — capture/hold/deliver/race/elimination layouts relative to circulation; device placement; links to Verse scoring/rounds (no duplicate sys_*)"
metadata:
  order: 13
  label: "Objectives in space"
  default_enabled: false
  load_condition: "User asks about objectives, capture points, hold zones, delivery, race finish, win conditions in the level, or where to place score devices"
---

# Objectives in space

Win conditions live on the **circulation network**, not in a random corner.
This ref is spatial placement + device roles. Scoring/round **code** → Verse
`sys_scoring`, `sys_rounds_timers`, `sys_architecture`.

## Place after flow

Order: greybox → `player_flow` → `combat_spaces` → **then** objectives → spawns
tuned to objective distance (`spawn_and_fairness`).

Rule: from the approach, eye ~170, the objective (or its landmark) must be
**readable** — silhouette, color, or light (`lighting`, `poi_hierarchy`).

## Layout patterns

| Mode intent | Spatial pattern | Device hints |
|-------------|-----------------|--------------|
| **Elimination** | Fair mid; spawns equal distance | Round Settings / Elimination; pads |
| **Score race** | Targets or galleries on clear lanes | Score devices / galleries; Barrier keep-out |
| **Capture / hold** | Contested volume mid-map; cover ring; flanks | Capture area / volume triggers |
| **Deliver / escort** | Path with choke + open beats; end deposit visible | Triggers along path; end zone |
| **Race** | Linear or circuit; checkpoints on path only | Checkpoint pads / triggers; no skips |
| **Hub quests** | Objective at spoke end; gate at hub mouth | Triggers / Verse unlock |

For Creative field names: Epic `DeviceToolset` `GetDeviceProperties` / `SetDeviceProperty`
— never invent options.

## Spacing rules

- Objective volume sized for the mode (hold: room for attackers + defenders;
  not a closet unless intentional).
- Cover around objectives follows `combat_spaces` (96 / 288); leave attack angles.
- Don’t put the only capture pad inside one team’s spawn pocket.
- Race checkpoints every **3–6** obstacles/beats (deathrun); intended route only.

## Sightline to goal

```
set_viewport_camera on approach path, eye ~170, look at objective
take_high_res_screenshot()
```

If the goal is invisible until you’re on top of it, add landmark / light /
threshold contrast.

## Systems links (do not duplicate)

| Need | Load |
|------|------|
| Backbone | `skill_read_subskill("verse", "sys_architecture")` |
| Score / win | `sys_scoring` |
| Rounds / timer | `sys_rounds_timers` |
| Teams | `sys_teams` |
| HUD callouts | `sys_hud` |
| Session / pads | islandsettings `session_setup` |

## Verify

- [ ] Objective on critical path or clearly marked spoke
- [ ] Approach screenshot reads the goal
- [ ] Spawns equidistant for competitive objectives
- [ ] Skips sealed (`blockout_playtest`)
- [ ] Round can start → play → end without manual editor hacks

## Don'ts

- Don’t hide the win condition behind identical dressing props.
- Don’t implement score in Verse before the volume exists in the level.
- Don’t give one team a unique doorway onto the point.
- Don’t copy full Verse recipes here — link `sys_*`.

## Related

- Bounds → `zones_and_boundaries`
- Flow / combat / spawns → `player_flow`, `combat_spaces`, `spawn_and_fairness`
- Director → `full_game_director`
