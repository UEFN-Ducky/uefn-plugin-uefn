---
description: "Full Tester MCP toolkit — create, run, and view tests (always load for Tester Ducky)"
metadata:
  label: MCP toolkit
  default_enabled: true
  load_condition: "Any Tester Ducky turn — cheat sheet of every testing MCP tool"
  order: 1
---

# Tester MCP toolkit

You have these tools **every turn** on the Tester profile (not keyword-gated).

## Inventory & audit

| Tool | Use |
|------|-----|
| `tester_list_devices` | Device outliner — one call returns `live` graph, `workspace` nodes, `audit`, `uefn_online`, `listener_online`, `error`. UEFN MCP first, listener second, Verse sources last. Call once per turn; if `live` is null do not re-call or `reload_listener`. |
| `device_graph_snapshot` | Raw nodes + edges JSON (same ladder inside). Use `tester_list_devices` unless you need the bare snapshot. |
| `device_graph_audit` | Unwired refs, orphans, cycles, missing spawn pads |
| `get_all_actors(label_filter=…)` / `inspect_verse_device` / Epic `GetDeviceProperties` | Deep-dive one device |

## Offline simulation (create + run)

| Tool | Use |
|------|-----|
| `simulate_device_event(device, event)` | One-shot propagation trace |
| `tester_create_simulation(name, device, expect_effects=[…])` | Save `.ducky/tests/<name>.json` |
| `tester_run_simulation(name=…)` | Run saved scenario → PASS/FAIL vs expected effects |
| `tester_list_tests` | List harness cases + saved simulations |

Effect kinds: `grant_item`, `teleport`, `score`, `movement`, `hud`, `cinematic`, `timer`, `spawn`, `signal`, `verse`.

## Verse harness (create + run + view)

| Tool | Use |
|------|-----|
| `verse_test_scaffold` | Write `Verse/DuckyTests/ducky_test_device.verse` |
| `verse_test_add_case` | Append ExpectEqual / ExpectTrue / ExpectInRange |
| `workspace_write_file` | Custom full test `.verse` under `Verse/DuckyTests/` |
| `workspace_list_verse_errors` | Fix compile errors |
| `verse_test_run` | Compile + push (+ optional session) |
| `tester_get_results` / `verse_test_results` | Parse `[DUCKY-TEST]` PASS/FAIL |

## Session probes (last resort — listener required; skip when `listener_online` is false)

| Tool | Use |
|------|-----|
| `session_status` | Is play/PIE active? |
| Epic `ValkyrieToolset.SessionToolset` `StartGame` / `StopGame` | Start/stop session |
| `get_editor_log` | Stream/filter log (`since_offset`, `regex`) |
| `actor_state_snapshot` / `actor_state_diff` | Movement/teleport before/after |

## Authoring recipe

1. `tester_list_devices` → pick devices to cover  
2. `tester_create_simulation` for each critical button/trigger chain  
3. `tester_run_simulation` until offline PASS  
4. `verse_test_add_case` for leveling/movement math  
5. `verse_test_run` → `tester_get_results`  
6. Reply with a compact PASS/FAIL table — never "please playtest"
