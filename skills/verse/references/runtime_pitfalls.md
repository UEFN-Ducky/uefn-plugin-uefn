---
description: "Runtime traps that compile clean but break play — server-only Verse and per-tick network cost, moving players (chair/MoveTo, never per-tick teleport), the computation limit, shared materials, pooling, cached maths, handler debounce, key reuse between gameplay and menus, elimination mid-flow, per-player vs shared state, and the done checklist"
metadata:
  order: 4
  label: "Runtime pitfalls — compiles clean, plays wrong"
  default_enabled: false
  load_condition: "Writing anything that runs every tick, moves players / props / entities, spawns many entities or materials, streams level pieces, handles input or menus, or must work for several players at once — and before calling gameplay done"
---

## Runtime pitfalls — compiles clean, plays wrong

None of these show up as a Script error. Each one cost real sessions several
rounds of "it lags" / "it's stuck" / "it doesn't show" after a clean build.

### 1. Verse runs on the server — motion it drives is replicated

Every transform you write from Verse is sent to every client. A per-tick
`SetGlobalTransform` / `TeleportTo` / `MoveTo` loop at 30+ Hz looks choppy on
clients and costs network for each moved object.

- Timed or continuous motion → `keyframed_movement_component` (Scene Graph) or a
  device's `MoveTo(Pos, Rot, Seconds)`: the client interpolates the glide.
- Gameplay that must tick fast (physics-like state, collision checks) can still
  tick fast — keep it **pure state** and push visuals on a slower clock
  (~10 Hz), each glide aimed one visual step **ahead** so the next one starts
  before the last ends (no stop-start stutter).
- Never move dozens of separate visual pieces each tick; move one parent.

### 2. Moving a player: seat them, never teleport each tick

- Per-tick `TeleportTo` on a `fort_character` jitters the camera, fights
  stasis, and can drop the player out of the intended spot.
- To carry a player with something moving: seat them in a `chair_device`
  (`Seat(Agent)`, optionally `DisableExit`) and move the **chair** with
  `MoveTo(Pos, Rot, Seconds)` (inherited from `creative_device_base`). The
  camera follows smoothly.
- A seated player **cannot** be teleported — `Eject` (after `EnableExit`) first,
  then teleport. Every exit path (finish, quit, elimination, hub return) must
  eject.
- `Seat` can silently not take on the first try (player still loading,
  mid-animation): retry a few times with a short `Sleep`, then fall back.

### 3. The per-tick computation limit

`ErrRuntime_ComputationLimitExceeded` / "InfiniteLoop" kills the device at
runtime, often only when the level is big.

- Never build a large level, grid or list in one `OnBegin` pass — split it with
  `Sleep(0.0)` every N items, or stream **one piece per tick**.
- Precompute lookup tables once (`OnBegin`, or lazily per index) instead of
  replaying a long calculation from 0 inside a per-tick helper — that cost
  grows every frame you play.
- Cache expensive per-index results in a `[int]t` map.

### 4. Share materials, pool entities

- One material instance per mesh = thousands of client loads and no batching.
  Cache **one material per colour/variant** (a `[string]material` map, or a
  `weak_map(session, …)` at module scope) and reuse it.
- Creating and destroying entities in bursts (effects, debris, streamed
  pieces) hitches. Keep a pool: hide on expiry, re-show and move on reuse;
  remove the pool only on teardown.
- Streamed level pieces: fewer, larger pieces beat many tiny ones; keep a fixed
  window ahead/behind and build at most one piece per tick.

### 5. Handlers, keys and state

- **A shared handler fires once per subscribed source.** Subscribing one
  handler to several triggers/buttons (or to both Pressed of two devices bound
  to the same key) runs it several times per press — debounce with a
  per-agent last-time map (`GetSimulationElapsedTime()`), ~0.2 s.
- **Gameplay keys reused by a menu press its buttons instantly.** If the player
  was holding/mashing Space or E when a result screen opens, that screen's
  button fires. Gate menu input by state and a short delay (≥1 s) after the
  screen opens; let an explicit on-screen button bypass the gate.
- **Gate every action by state.** An action fired the same tick as a state
  change (start / end / restart) gets dropped or cancelled — check the state
  inside the action, not only in the caller.
- **Elimination mid-flow:** subscribe to the character's `EliminatedEvent`
  while a player is inside any sequence (ride, seat, minigame, cutscene) and
  clean up from it — otherwise their state stays "in progress" forever.
  `elimination_result` needs `using { /Fortnite.com/Game }`.

### 6. Several players at once

- Give each player their own slot (lane, plot, seat, camera, HUD) from the
  start: an `[agent]int` slot map, allocated centre-out, freed on leave/finish.
- **Never reset shared state when one player starts.** Reset shared data only
  when no player is using it (`ActiveCount() = 0`).
- Devices are not comparable: track which device a player has by **index**, not
  by `=` on the device (3509).

### 7. UI that never appears

- A display function whose only caller is a preview/test path leaves the
  real HUD at 0 — grep for a real gameplay caller of every `Update*`/`Show*`.
- Verse `color_block` is a solid fill: it cannot fade, so a "vignette" or
  gradient becomes an opaque panel. Use a texture or skip the effect.
- Translucent 3D effects spawned near the camera wash the screen out — keep
  them short-lived or away from the camera.

### Done checklist (before saying a gameplay change works)

1. What runs every tick, and what crosses the network every tick?
2. Are new entities and materials pooled / shared?
3. Placed-device values and start-up options checked (`uefn` skill)?
4. Any key doing two jobs without a gate?
5. Works with two or more players?
6. Cleans up when the player is eliminated mid-flow?
7. Clean build **and** one short live run (tagged `Print`s + one frame) —
   a clean build proves syntax and effects, not behaviour.
