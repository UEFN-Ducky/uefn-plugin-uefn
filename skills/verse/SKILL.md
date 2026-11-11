---
source_plugin_id: uefn
name: verse
description: "Writing Verse source — syntax, effects (no_rollback/transacts/decides), task lifetimes, compile-error fixes, lag-free runtime rules, system recipes on our player_manager packs, and finding APIs via digests. Source only: placed-device wiring and level ops → uefn skill; Scene Graph entities/prefabs/motion → scenegraph skill."
license: MIT
metadata:
  label: UEFN Verse
  version: 59
  managed_by: uefn-ducky
  author: UEFN-Ducky
  copyright: Copyright 2026 Mindful Path Company, LLC
  allow_redistribute: true
---

# Verse — writing code for UEFN

Source files are read and written with `workspace_*` (offline OK). In-editor build /
file ops when Epic MCP is online: `VerseToolset.VerseToolset` (43.00 name; was `ValkyrieToolset.VerseToolset`) (`BuildAll`, …).
Placing devices and wiring `@editable` refs is **serial** — one heavy editor call per
message, never `_v2` copies of a device (`skill_read_subskill("uefn", "verse_devices")`).

## Hard rules (every UEFN skill)

1. **Our architecture is the spine.** Every system is its own folder and pack; players, currency, XP, playtime, inventory and saves come from our packs, and game modes consume `player_manager` `?option` slots — never a second registry, wallet or save table. → `sys_architecture`
2. **Scene Graph, always.** Anything the code creates, moves, shows, hides or animates at runtime is an entity / Entity Prefab; devices only for features Fortnite provides; `creative_prop` only for Fortnite physics props (`physics` skill), never moved or hidden from Verse. → scenegraph SKILL.md
3. **Motion is keyframed, always — no `MoveTo`, ever.** Every runtime move of an entity — door, lift, platform, spin, bob, projectile, one glide, a chaser, a pet — is `keyframed_movement_component`: `SetKeyframes`, then `Play()`. Never `SetGlobalTransform` / `TeleportTo` in a loop. Place once → `SetGlobalTransform`; follow → `SetOrigin`; carry a player → a keyframed platform they stand on; characters → animation assets. → scenegraph `movement_transforms`
4. **No lag.** Events over polling; every loop waits; per-tick work is pure state, visuals ~10 Hz; pool entities, share materials; build arrays with `for`, never `+=` in a loop; HUD updates on change; saves on change. → `runtime_pitfalls`
5. **Everything stops when its owner goes.** Per-player loops race a stop event signalled on leave and elimination; cleanup in `defer`; never `branch` at the end of `OnBegin`. → `async`
6. **One house code style** — our templates' style. → `code_style`
7. **Names come from the digest.** Copy names from a loaded skill or `search_verse_digest`; never deprecated calls. → `digests`. Snippets in every skill are fragments: the `using` block of a file's first code sample applies to all of them.
8. **Done means played.** Clean build, then one live run with tagged `Print`s (two players for multiplayer) and the done checklist. → `runtime_pitfalls`

## Verse must-knows

- **Effects decide whether it compiles.** No effect specifier = `no_rollback`: not callable in `if (…)`, `if:`, `for` filters, `[]` or a `<decides>` body. Give every getter/helper `<transacts>`; pair `<decides>` with `<transacts>`; bind no-effect device getters on the line before the `if`. Field initialisers are literals; `int / int` is a failable `rational`. These rules were 72 % of real compile errors. → `effects`, `compile_errors`
- **Folders before files.** Never write `.verse` at `Content/Verse/` root (only `module_declarations.verse` and tiny shared helpers). One system per folder; `workspace_list_dir("Verse")` first; reuse the system's folder. Generic (parametric) classes go in a Content-level folder that sorts first, helpers below them (3502). → `modules`
- **Persistence `weak_map`.** Never remove keys; never delete persistable fields without migration; rebuild + `set`; six persistent weak_maps per island from 43.00 (four on 42.x; Player Core + Economy + Progression + Time Tracker use four; the 7th is error 3502). Prefer nesting in the shared table over new maps. → `persistence`, `sys_persistence_migration`
- **Player manager flow.** `player_manager` bus → `Init` (persist row) → each manager's `OnPlayerJoined` (config, then HUD). Roles are Manager / Tracker / Controller / Service. → `sys_architecture`
- **UI = Epic's Verse UI Kit first**, custom kit buttons only (never Loud/Quiet/Regular presets). → `verse_ui_kit`, then the layer you write (`umg_widgets` index → `umg_*`; tools `umg_mcp_tools`). The widget type is its Assets digest name — never invent `MyUMGWidget := class`. How it looks: load **`ui_design`** before laying out any screen and run its checklist before calling it done, so game UI looks designed, not AI-made. Code-built canvas only as a fallback: `sys_canvas_cookbook` → `sys_hud_template` → `sys_custom_buttons` (`SetFocus` before `AddWidget`) → `sys_ui_menus`. Gatherable copy: `localization` skill, `ui_ready`.
- **Digests are read only.** Never write, patch or delete any `*.digest.verse`.
- **Syntax.** `X := value` is constant; `var X : t = value` changes only through `set`. Types are lowercase (`int float logic string`); `[]t` array, `[k]v` map, `?t` option, `tuple(…)`, element `T(0)`; `array{}` not `array:`; no `ToString(logic)`. Comments are `#`, never `//`. A `{}` body stays on the same line as its `if (…)` (a lone `{}` on the next line is parse error 3100); an `if (…):` / `for (…):` body always goes on the next line — `if (X): Stmt` on one line is parse error S76 and `for (…): Stmt` is 3514; for a value write `if (X) then A else B`. → `syntax`
- **Recent releases** (chat channels, Unarmed, marketplace, LLM NPCs, ability templates, UMG event fields, 43.00 events) → `whats_new`.

## What are you building? Load these

| Task | Load (1–3, then write) |
|------|------------------------|
| A placed device: `@editable`, `OnBegin`, events and handlers; 43.00 vehicle fuel / refuel, teleporting props | `devices` |
| Any player-driven system (score, stats, joins, leaves) | `sys_architecture`, `sys_player_data` |
| Currency, shop, XP, levels, playtime | apply the pack first; `sys_economy` / `sys_progression` / `sys_time_tracking` |
| Quests, objectives, missions, achievements in the Fortnite quest UI (43.00) | `sys_quests` |
| Saves across sessions | `persistence`, `sys_persistence_migration` |
| Rounds, phases, countdowns | `sys_rounds_timers` |
| Scores, kills, streaks, leaderboards, king of the hill | `sys_scoring` |
| Analytics events, funnels, accolades | `sys_analytics` |
| Input triggers, held keys, Register/Unregister per player | `sys_input_devices` |
| Anything that loops, waits, races or must stop | `async`, `events_subscriptions` |
| Moving, animating or attaching anything | scenegraph `movement_transforms` |
| Spawning things at runtime, waves, pools | `sys_spawning`, `design_patterns` |
| Ground height, paths, obstacles, GPS / NPC routes without raycasts; seeded random | `sys_world_data` |
| NPCs and enemies | `sys_npc_ai` (+ the `npc-ai` skill) |
| NPCs that talk (LLM persona, conversations) | `sys_conversations` |
| Damage, healing, elimination | `sys_damage_health` |
| Destructible props, custom health pools, damage types, damaging entities (43.00, Experimental) | `sys_health_pipeline` |
| Teams, party, chat | `sys_teams`, `sys_party`, `sys_chat_channels`, `sys_text_chat` |
| Weapons and items | `sys_owned_weapons`, `sys_inventory` (+ scenegraph `custom_weapons`, `custom_items`) |
| Tycoon / idle | `sys_tycoon`, `sys_generators`; unlocking / revealing buildings `sys_buildings` |
| Paid entitlements, V-Bucks offers | `sys_marketplace` |
| On-screen overlay or grid minigame | `sys_minigame_overlay` |
| Any UI | `verse_ui_kit` → `umg_*`; per-player HUD `sys_hud` |
| Language: types, arrays, maps | `datatypes` |
| Language: if, for, loops, case | `control_flow` |
| Language: classes, enums, interfaces, generics | `classes` |
| Language: function types, extension and generic functions, callbacks | `functions` |
| Reusable patterns (slot index, pools, registries, mixins) | `design_patterns` |
| Code layout, naming, formatting | `code_style`, `modules` |
| Anything that ticks, moves, spawns many things or serves several players | `runtime_pitfalls` |
| A Script error | `compile_errors` |

`skill_read_subskill("verse")` with no id lists every reference with its load
condition. Load the closest 1–3, then write; "Details:" links inside a page are
optional deep-dives, never prerequisites.

## Template packs (before you write a system)

1. `workspace_list_dir("Verse")` — reuse `PlayerCore` / `Economy` / `Progression` if present.
2. `verse_template_list()` — ids, folders, files, and the `?option` slots each pack registers or consumes.
3. Missing pack → `verse_template_apply(id)`: `player_core`, `economy`, `progression` before `tycoon` / `shop`. NPC islands: `npc_core`.
4. `verse_template_get(id)` to read the source before customising.

Game modes (`tycoon`, match, arena) **consume** `player_manager` slots
(`GetCurrencyProvider`, `GetXPAwarder`, `GetPlaytimeProvider`) and the per-player
slot index (`GetPlayerSlot`); they never own a wallet, XP table or second
`player_manager`. Never name things `*_system`, "wallet" or `fortnite_*`: use
`economy_manager`, `progression_manager`, `player_time_tracker`, `save_service`.
`verse_template_verify()` rebuilds every installed template when UEFN is open.

## Digests

`list_verse_digests()` → `search_verse_digest(query)` (search, never dump) →
`get_verse_api(name)` for the exact signature. `Assets.digest.verse` holds your own
assets (prefabs, meshes, widgets); pass `digest_path=` to search only it. Budget ~5
lookups per task, then write. Core intrinsics `Abs`, `ConcatenateMaps`, `Max`, `Min`
compile although no digest lists them. Details: `digests`.

## Error checks and verify

1. `workspace_list_verse_errors()` first on any fix-errors turn (never `ping`, `get_project_info`, `ducky_get_errors`, `execute_python` or listener tools to hunt errors), and after every edit (incremental; never `full=true` to re-confirm). It is **syntax only** — it cannot see effect (3512), module (3593) or ambiguity (3588) errors.
2. `workspace_compile_verse` once Problems is clean, and **before** any `wire_verse_*` / `set_verse_editable` / `workspace_push_verse_changes` (otherwise STALE REFLECTION). Any `Script error NNNN` → `compile_errors`.
3. Gameplay, camera, movement and UI changes need one short live run: tagged `Print`s while building (read them with `uefn-logs`), one frame, a second player for multiplayer; remove debug prints before shipping.

## Anti-patterns

| Wrong | Right |
|-------|-------|
| `.verse` files at `Verse/` root, or a mode-local wallet / XP / registry | System folders and our packs |
| Guessed device / asset / function names | A loaded skill, else `search_verse_digest` once |
| No-effect helper inside `if (…)` | `<transacts>` on the helper, or bind it first |
| Wiring `@editable` refs before a build | `workspace_compile_verse`, then wire |
| `MoveTo` anywhere; `TeleportTo` / `SetGlobalTransform` in a loop; a bob or spin loop | `keyframed_movement_component` for every entity move (`SetKeyframes` + `Play()`); carried players stand on a keyframed platform |
| `RemoveFromParent`, then `AddEntities` the same entity back; hiding a prop by teleporting it underground | `Disable()` / `Enable()` the entity's meshes; removal is final |
| Spawn/dispose effects in bursts; one material per mesh | Pools; one cached material per colour |
| Whole level built in one `OnBegin` pass | Split across ticks |
| `branch{ Loop() }` at the end of `OnBegin`; per-player loop with no stop | `spawn` + stop event on leave and elimination |
| HUD refreshed on a timer | Update on the event that changed the value |
| Clean `workspace_list_verse_errors` treated as "it compiles" | Build, then one live run |
| `// comment` | `#` comment |
| Editing any `*.digest.verse` | Never |
