---
description: "Spawn placement and fairness — lobby vs match pads, no LOS camping, equal run-in, mirror checks, wire_player_spawners / islandsettings links"
metadata:
  order: 10
  label: "Spawn & fairness"
  default_enabled: false
  load_condition: "User asks about spawn pads, spawn camping, respawn fairness, lobby vs match spawns, mirror spawns, or spawn-to-action time"
---

# Spawn and fairness

Bad spawns ruin good arenas. Place pads **after** flow and combat volumes exist
so “safe run-out” is real geometry, not hope.

## Spaces (separate them)

| Phase | Space | Notes |
|-------|-------|-------|
| Pre-match | **Lobby** | Safe, mode signage, practice optional |
| In-match | **Match spawns** | Team/FFA pads facing play |
| Post-match | Lobby or podium | Distinct lighting/props help |

Don’t dump lobby and combat in one undifferentiated room unless the mode is a
tiny box fight (then barriers until round start).

## Spatial rules (every match pad)

1. **No LOS from active fight** into the pad — screenshot from pad and from mid.
2. **Face away** from enemy territory / toward an exit into the map.
3. **≥ 2 exits** from the spawn pocket (prevent door camping).
4. **~3–5 s safe run-out** before first plausible enemy contact (cover along exit).
5. **Equal spawn→action** path length across teams / FFA pads (`measure_distance`
   or eyeball route cells).

## Counts and wiring

- MaxPlayers **N** ⇒ **N** Player Spawn Pads (islandsettings).
- Count: `get_all_actors(label_filter=\"Spawn\")`.
- Wire: `wire_player_spawners("<Verse player-manager label>")` — the argument is the
  **Verse manager device** owning an `AllPlayerSpawners` array. Island Settings is a
  Creative device with no Verse `@editable`, so passing its label fails. Omit the pad
  list to auto-detect pads parented under that manager.
- Session / pad recipes: `skill_read_subskill("islandsettings", "session_setup")`.

Advanced respawn rules (delay, team gate, “don’t spawn on enemies”) → Verse
`sys_spawning` / `sys_rounds_timers` — **not** re-specified here.

## Mode patterns

| Mode | Spawn pattern |
|------|----------------|
| 1v1 | Opposite ends; strict mirror; barrier until start |
| FFA / box | Symmetric ring or corners; no pad sees another |
| Team | Team pockets; equal mid distance; no shared door |
| Deathrun | Start pad + checkpoint pads; activate along path |
| Tycoon | One pad (or cluster) per identical plot |

## Verify checklist

From **each** pad:

```
set_viewport_camera({ at pad, eye ~170, look along intended exit })
take_high_res_screenshot()
```

- [ ] Cannot see enemy spawn or mid camping angle
- [ ] Two exits visible or obvious
- [ ] First fight / objective reachable without a marathon
- [ ] 1v1: mirrored cover distances (`measure_distance`)

Also: spawn-to-spawn screenshot — pads must not see each other.

## Don'ts

- Don’t place pads in the open mid “because it’s fair.”
- Don’t fix spawn kills only with invulnerability timers if LOS is broken — fix space.
- Don’t leave MaxPlayers ≠ pad count.
- Don’t put all team A pads with a shorter path to the objective.

## Related

- Combat around spawns → `combat_spaces`
- Path length → `player_flow`
- Objectives near spawns → `objectives_in_space`
- Director → `full_game_director`
- Island settings → islandsettings pack
