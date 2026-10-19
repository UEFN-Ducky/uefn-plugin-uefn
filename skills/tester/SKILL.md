---
source_plugin_id: tester
name: tester
description: "UEFN testing suite — device-graph simulation, Verse harness asserts, session probes"
license: MIT
metadata:
  label: UEFN Testing
  version: 11
  author: UEFN-Ducky
  copyright: Copyright 2026 Mindful Path Company, LLC
  allow_redistribute: true
---

# Tester — verify before play

**CRITICAL — never parallel place/wire:** Tester audits and simulates. Fixing
unwired refs uses uefn tools **one call per turn** — never same-turn multi
`wire_verse_*` / `spawn_actor` / `save_current_level`. Leave place/wire recipes
to SERIAL: one mutating/editor call per assistant message. / `creative_devices`.

**Spawn template:** Settings → Duckies → **Tester** (or `ducky_spawn_chat` / New Ducky → Tester). That profile ships with packs `tester` + `uefn` + `verse` + `islandsettings` + `ponytail`, both `builtin_uefn` + `builtin_ducky` MCP groups, and the full testing tool surface always unlocked.

Work loop: **snapshot → audit → simulate → create tests → run → view results**.

Do **not** ask the user to manually press buttons in-game first. Prove wiring offline, then prove math with the Verse harness, then use session probes only when something still needs a live check.

Load `mcp_toolkit` for the full tool cheat sheet (`skill_read_subskill("tester", "mcp_toolkit")` if not already in context).

## STOP ladder

- UEFN offline (no UEFN MCP and no listener) → still run workspace Verse discovery + write harness files; do not wait for a connection for file work.
- No live graph (`tester_list_devices.live` is null / `device_graph_snapshot` errors) → **do not call it again** and do not `reload_listener`. The tool already tried UEFN MCP then the listener with full busy-wait. Continue with the `workspace` nodes it returned. `uefn_online` / `listener_online` in that payload is the health verdict — a slow or empty snapshot is not "offline".
- `session_status` / `get_editor_log` / `actor_state_*` need the listener. Skip them when `listener_online` is false; report from sim + harness instead.
- Harness compile fails → `workspace_list_verse_errors` and fix every reported line; never paste placeholders.

## Golden path

1. `tester_list_devices` / `device_graph_snapshot` — inventory devices + edges.
2. `device_graph_audit` — fix unwired `@editable` refs and orphan devices before simulating.
3. `simulate_device_event` or `tester_create_simulation` + `tester_run_simulation` — prove button → trigger → granter / teleport / score chains offline.
4. Create asserts: `verse_test_add_case` (or `verse_test_scaffold` + `workspace_write_file`) → `verse_test_run` → `tester_get_results` / `verse_test_results`.
5. `tester_list_tests` to see what you already created. Only if needed: `session_status`, `actor_state_snapshot` / `actor_state_diff`.

## Create your own tests (MCP)

| Goal | Tool |
|------|------|
| List existing tests | `tester_list_tests` |
| Save offline wiring scenario | `tester_create_simulation(name, device, expect_effects=[…])` |
| Run + PASS/FAIL offline scenario | `tester_run_simulation(name=…)` |
| Add leveling/movement assert | `verse_test_add_case(name, kind, actual/expected/…)` |
| View harness PASS/FAIL | `tester_get_results` / `verse_test_results` |
| Custom full `.verse` test file | `workspace_write_file` under `Verse/DuckyTests/` |

## Do not / do instead

| Do not | Do instead |
|--------|------------|
| Start PIE to check wiring | `simulate_device_event` on a snapshot |
| Guess which devices are wired | `device_graph_audit` |
| Hand-wave leveling math | `ExpectEqual` / `ExpectInRange` in the harness |
| End with "tell me to playtest" | Run the tools and report PASS/FAIL yourself |

This guide is already in your context — load reference files with `skill_read_subskill("tester", …)` only when their condition applies.

## Verify

`verse_test_run` then `tester_get_results` — report PASS/FAIL. Never ask the user to playtest.

## 42.30 notes

- Logs from Epic when `epic_mcp_online`: `EditorToolset.LogsToolset.GetLogEntries(category,
  pattern, maxEntries)` (editor: Verse compile results, blueprint errors, Content Pre-Checks)
  and `ValkyrieToolset.SessionToolset.GetClientLogEntries(pattern, maxResults, startLine)`
  (the launched client).
- Restarting a session is faster; Launch Session logs why assets needed resaving.
- Fixed: proximity voice chat, consumables vanishing on respawn, the Ready Up button
  missing for a UEFN island, a false "party members cannot change game modes" error.
