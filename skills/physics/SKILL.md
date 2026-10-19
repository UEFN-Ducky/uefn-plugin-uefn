---
name: physics
description: "UEFN Physics Beta — enable project physics, FortPhysics props, compatible devices, Verse impulses/volume prop events, soccer + puzzle recipes"
license: MIT
metadata:
  label: UEFN Physics
  version: 8
  author: UEFN-Ducky
  copyright: Copyright 2026 Mindful Path Company, LLC
  allow_redistribute: true
  managed_by: uefn-ducky
---

# UEFN Physics (Beta)

**CRITICAL — editor mutations are SERIAL:** wire Volume / Prop Mover / Trigger
refs one MCP call at a time → wait → next. Never parallel wire/spawn/save.
Details: SERIAL: one mutating/editor call per assistant message..

Physics in UEFN simulates collisions, explosions, and motion (F=ma). Feature is
**Beta** — publishable, but tools change often. Prefer a project copy before enabling.

**Not supported** on brand templates. UEFN only (not Fortnite Creative).

## Enable

Use the island / project tool for Beta Physics (do not send Project Settings homework).

## Golden path

```
1. Enable Physics via the project tool
2. Place or import prop → ensure Simple Collision (sphere/box when possible)
3. Add Fort Physics (Details → + Add → Fort Physics) OR Fortnite Tools → Add Physics
4. Simulate Physics = true; tune Mass / Damping / Impulse On Hit
5. Wire Volume / Prop Mover / Trigger (device whitelist)
6. Verse: subscribe PropEnterEvent / PropExitEvent; impulse via digests
```

## Hard rules

- **Budget:** stay near ≤50 simple simulated shapes (boxes/spheres). Complex collision costs more.
- **No vehicles** — unstable on physics islands.
- **No Sequencer ↔ physics.** Sequenced objects do not interact with the physics thread. Use **Prop Mover**.
- **Movement gaps:** walk/run/sprint/jump/fall/swim/crouch/glide/skydive OK. Mantle, slide, zipline, grind rails, DBNO not available with physics.
- **Never invent Verse API names.** Confirm with `search_verse_digest` / `get_verse_api` on `volume_device`, `creative_prop`, `fort_character`. Digest names (verified): `PropEnterEvent`, `PropExitEvent` — not PropEnters/PropExits.

## Add physics to props

| Method | Steps |
|--------|--------|
| Fortnite Tools | Selection Mode → Fortnite Tools → select props → **Add Physics** (also Remove / Select all physics) |
| Component | Details → + Add → **Fort Physics** → Simulate Physics |

## Compatible devices (tested)

Air Vent, Barrier, Bouncer, Bouncer Trap, Volume, D-Launcher, Damage Volume,
Hover Platform, Pinball Bumper, Pinball Flipper, Prop Mover, Skydive Volume,
Teleporter, Trigger, Water, Crash Pad, Explosives, Carryable Spawner.

Experimental devices live under Fortnite → Devices → `!Experimental` when browsing.

## Verse (quick)

- `volume_device`: `PropEnterEvent` / `PropExitEvent` → `listenable(creative_prop)`
- Volume device UI: enable **Physics Events** for On Physics Enter/Exit bindings
- `creative_prop`: linear/angular velocity, mass, linear/angular impulse, force, torque, Get/SetDynamic
- `fort_character`: linear velocity, mass, linear impulse, force

Details: load `verse_physics`.

## Reference files

- `references/prop_physics.md` — FortPhysics options, constraints, collision
  Load when: Tuning mass/damping/impulse or adding physics to props
- `references/devices.md` — Compatible devices, Volume physics events, Prop Mover
  Load when: Wiring devices with physics props
- `references/verse_physics.md` — Volume prop events + prop/character impulse APIs
  Load when: Verse goals, kicks, forces, or prop enter/exit
- `references/faq_limits.md` — FAQ and hard limits
  Load when: Perf, vehicles, Sequencer, weapons, Creative questions
- `references/soccer_game.md` — Physics soccer island recipe
  Load when: Building a pickaxe soccer / ball game
- `references/puzzle_dungeon.md` — Physics puzzle room recipe
  Load when: Cubes, moving platforms, bridge drop puzzles

## Verify

`device_graph_audit` on wired volumes / movers. Enable Physics via the project tool — do not send Project Settings homework.

## 42.30 notes

- Rocket Launchers now push characters on impact and Shockwave Grenades launch
  characters and physics props correctly on physics-enabled islands (they used to
  pull them back to the blast point).
- Epic `PhysicsToolsets.PhysicsAssetToolset` creates and edits Physics Assets when
  `epic_mcp_online` (uefn `epic_toolsets`).
