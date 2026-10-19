---
description: "Physics puzzle dungeon — weighted cubes, Switch/Prop Mover platforms, Volume On Physics Enter bridge drop"
metadata:
  order: 60
  label: "Puzzle dungeon"
  default_enabled: false
  load_condition: "Building a physics puzzle room with cubes, moving platforms, or a falling bridge"
---

# Physics puzzle dungeon

Single-player room: drop physics cubes with moving platforms, push a cube into a
Volume to trigger a pillar that knocks a bridge across a gap.

## 1. Project / Island Settings

1. Blank (or any) island → enable **Physics**.
2. Island Settings example:

| Setting | Value |
|---------|--------|
| Max Players | 1 |
| Teams | Team Index: 1 |
| Team Size | 1 |
| Start With Pickaxe | false |
| Environment Damage | Off |

One Player Spawner, Team Index 1. Pair MaxPlayers with pads (`islandsettings`).

## 2. Room (required elements)

- One entrance, one exit; walls/fences so exit is only reachable via bridge.
- Two high platforms that hold physics cubes until Prop Movers pull away.
- Gap that needs a bridge; pillar (or similar) that can push the bridge down.
- Theme example: Underworld / Brimstone props under Fortnite → Props.

## 3. Physics cubes

For each cube (Cube 1, Cube 2):

1. Place colored cube prop; scale e.g. W/D 1.5, H 2; optional stone MI.
2. + Add → **Fort Physics**:

| Option | Value |
|--------|--------|
| Simulate Physics | true |
| Override Mass | true |
| Mass | 75 |
| Enable Gravity | true |
| Start Awake | true |

Editor-placed props are unique — no device respawn; round restart or Verse to reset.

## 4. Cube 1 platform (Switch → Prop Mover)

1. Floor piece as platform; Prop Mover intersects it; arrow = retract direction.
2. **Cube 1 Prop Mover:** Distance 20, Speed 5, Should Move From Start **false**.
   Advanced: On AI/Player/Prop Collision → Continue; damages 0.
3. **Cube 1 Switch** (e.g. Ancient Lever on pedestal) → Prop Mover **Start** ← Switch **On Turned On**.
4. Place Cube 1 on the platform.

## 5. Cube 2 platform + Volume

1. Duplicate Switch + Prop Mover for Cube 2 (same mover settings).
2. Floor depression (visual cue) + **Volume**: Visible false; Player Events on;
   **Physics Events Enabled** true.
3. Player turns Cube 2 Switch → platform moves → cube drops → player pushes cube
   into Volume.

## 6. Bridge + pillar

1. Duplicate a physics cube → rename Bridge; scale thin/tall (e.g. Depth 0.25, Height 10).
2. Fort Physics: Mass **500**, Linear/Angular Damping **0.5**.
3. Place Bridge vertical at gap edge so the pillar will hit it.
4. Pillar prop + **Pillar Prop Mover** toward Bridge:

| Option | Value |
|--------|--------|
| Distance | 4 |
| Speed | 1 |
| Should Move From Start | false |
| Allow Reverse Past Start | false |
| On Player/AI Collision | Stop |
| On Prop Collision | Continue |

5. Pillar Prop Mover **Start** ← Volume **On Physics Enter**.

Flow: Cube 2 enters Volume → pillar moves → Bridge falls across gap → exit reachable.

## Agent tips

- Devices under `/Game/Creative` via `search_assets`; label + folder everything.
- Prefer Prop Mover over Sequencer (`faq_limits`).
- Tune Distance/Speed/Mass to room scale after first PIE.
- Optional Verse later for round reset of cube transforms — not required for the tutorial loop.
