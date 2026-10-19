---
description: "Offline device-graph snapshot, audit, and event simulation"
metadata:
  label: Device simulation
  default_enabled: true
  load_condition: "Auditing wiring, simulating button/trigger chains, or explaining what a device will fire"
  order: 10
---

# Device simulation

## Tools

- `device_graph_snapshot` — nodes (label/class/kind/editables) + edges (verse refs + creative bindings).
- `device_graph_audit` — unwired refs, dangling targets, orphans, cycles, missing spawn pads.
- `simulate_device_event(device, event)` — propagate an event through wired edges; returns ordered `trace` + `effects`.

## Common events

| Source | Event | Typical downstream |
|--------|-------|--------------------|
| Button | `InteractedWithEvent` | Trigger / GrantItem / Activate |
| Trigger | `TriggeredEvent` | GrantItem / Play / Teleport / Score |
| Volume | `AgentEntersEvent` | Trigger / GrantItem |
| Timer | `SuccessEvent` | GrantItem / Show HUD |

## Reading a trace

Each step: `device ← incoming` and optional effects (`grant_item`, `teleport`, `movement`, `score`, `hud`, `cinematic`).
If a step is `skipped`, the target semantics do not receive that signal — fix wiring or pick the correct receive function.

## Tester panel

Right-rail **Tester** tab lists devices (live via UEFN MCP first, listener second, Verse sources last). Status is UEFN connected/offline from the same cheap probes as Connections — never snapshot success. **Sim** on a row runs `simulate_device_event` and shows the trace inline.
