---
description: "Build order for any island — the systems-side golden path across skills: plan the systems, session shell, our core packs, mode logic, Scene Graph objects, devices placed and wired serially after a build, UI kit screens, saves, two-player verify, then dress; each step names the page to load"
metadata:
  order: 1
  label: "Build order — any island, end to end"
  default_enabled: false
  load_condition: "Building a whole game, mode or feature set from scratch, or unsure which skill and step comes next while building an island"
---

## Build order — any island

The level-space pipeline (greybox, flow, combat, spawns, objectives, dress) is
leveldesign `full_game_director`. This page is the systems side that runs through
it. Each step names what to load; do them in order and do not skip the verify.

| # | Step | Load |
|---|------|------|
| 0 | **Plan.** One sentence: "players do X until Y wins". List the systems (players, currency, XP, rounds, score, UI) and, for each, the pack or `sys_*` page it comes from. Decide what is Scene Graph, what is a device. | verse `sys_architecture`; scenegraph SKILL.md "What to build it with" |
| 1 | **Session shell.** `MaxPlayers`, teams, spawn pads (one per player). | islandsettings `session_setup` |
| 2 | **Core packs.** `workspace_list_dir("Verse")`, then apply what is missing: `player_core` first, then `economy`, `progression`, `time_tracker` only if the mode uses them. | verse SKILL.md "Template packs" |
| 3 | **Mode logic** in its own folder, consuming `player_manager` slots and hooks: phases, score, teams. Per-player lanes or plots use `GetPlayerSlot`. | verse `sys_rounds_timers`, `sys_scoring`, `sys_teams`, `design_patterns` |
| 4 | **Runtime objects** as Entity Prefabs with components; motion with keyframed movement; pools for anything short-lived. | scenegraph SKILL.md, `movement_transforms`; verse `sys_spawning` |
| 5 | **Build Verse**, then place devices and wire `@editable` refs one call at a time. | uefn `verse_build_lifecycle`, `verse_devices`, `creative_devices` |
| 6 | **UI** as Verse UI Kit screens, updated on events. | verse `verse_ui_kit`, `sys_hud` |
| 7 | **Saves** on the one player table, written on change. | verse `persistence` |
| 8 | **Verify.** Clean build; one live run with tagged `Print`s; a second player; the done checklist. | verse `runtime_pitfalls`; `uefn-logs` |
| 9 | **Dress last.** | leveldesign `theme_recipes`, `lighting` |

### Rules that apply at every step

- Every system is its own folder; nothing at `Verse/` root.
- Editor mutations are serial — one heavy call per message.
- Nothing moves per tick from Verse; nothing loops without a way to stop.
- A step is done when it works in a live run, not when it builds.
