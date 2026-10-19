---
description: "Physics-compatible Creative devices, Volume physics events, Prop Mover vs Sequencer"
metadata:
  order: 20
  label: "Physics devices"
  default_enabled: false
  load_condition: "Wiring Air Vent, Volume, Prop Mover, Barrier, Bouncer, or device events with physics props"
---

# Physics-compatible devices

Tested with physics props:

Air Vent, Barrier, Bouncer, Bouncer Trap, Volume, D-Launcher, Damage Volume,
Hover Platform, Pinball Bumper, Pinball Flipper, Prop Mover, Skydive Volume,
Teleporter, Trigger, Water, Crash Pad, Explosives, Carryable Spawner.

Browse experimental devices: Fortnite → Devices → `!Experimental`.

## Volume

Detect physics props entering/exiting:

| Setting | Value |
|---------|--------|
| Visible in Game | false (usually) |
| Player Events Enabled | as needed |
| **Physics Events Enabled** | **true** |

Device bindings: **On Physics Enter** / **On Physics Exit** (payload: Creative Prop).

Volume / trigger / barrier **size** is a Details property (`Width` / `Height` /
`Depth` / zone) via `SetDeviceProperty` — **never actor Scale** (breaks Fortnite
devices). Location and rotation are fine.

Verse listenables on `volume_device`: `PropEnterEvent` / `PropExitEvent`
(`listenable(creative_prop)`). Confirm with digests before coding.

## Prop Mover

Preferred way to move level geometry that must **hit** physics props.

- Place so the device intersects the prop; holographic arrow = move direction.
- Common: Distance / Speed; **Should Move From Start** false when Switch/Volume starts it.
- Collision behaviors (Advanced): Continue vs Stop for AI / Player / Prop.
- **Limits (documented v42.10):** only **one** Prop Mover can be active at a time; the one
  activated last takes precedence; the active mover can **rotate or translate, not both**.
  Chain movers (Finish → next Start) instead of overlapping them.

**Never use Sequencer** for motion that should interact with physics — different
thread; props will not collide correctly.

## Useful patterns

| Pattern | Devices |
|---------|---------|
| Keep ball in bounds | Barrier (Zone Shape **Hollow Box**; sink bottom below ground so spawns work) |
| Clear goal mouth | Air Vent, Knockup Force Multiplier low (e.g. 0.1) |
| Drop a platform | Switch / Button / Volume → Prop Mover **Start** |
| Physics switch | Volume **On Physics Enter** → Prop Mover / Trigger |

## Agent wiring

- Place devices via `search_assets` under `/Game/Creative` (not `/Fortnite` gallery).
- Prefer `label` + `folder` on `spawn_actor` (same tick). Separate `set_actor_label` /
  `set_actor_folder` only when renaming an existing actor.
- Creative device fields: Epic `DeviceToolset` `GetDeviceProperties` / `SetDeviceProperty`.
- Event array binds in Details (Functions ← Events) when not using Verse.
