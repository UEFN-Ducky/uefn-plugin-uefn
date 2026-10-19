---
description: "Per-area landscapes + folders — one terrain per Hub/Store/etc., 100k-uu slots, always Areas/<id>/…"
metadata:
  order: 0
  label: "Area management"
  default_enabled: true
  always_on: true
  load_condition: "Building multi-area maps, hubs, stores, lobbies, arenas, or any new greybox/landscape layout"
---

# Area management — separate worlds, always foldered

Multi-area games must **not** pile geometry at the origin. Each named area is its
own far-away footprint with its own Outliner tree.

## Hard rules

1. **One area = one terrain + one folder tree.** Never mix Hub props into Store.
2. **Call tools first** — `area_list` → `area_create(area_id, preset=…)` before
   freehand `spawn_actor` / inventing cubes.
3. **Never leave actors at Outliner root.** Nest under `Areas/<id>/…`.
4. **AI “landscape” = `terrain_generate` via `area_create`.** Real Landscape Mode
   → Create is manual-only. The `landscape_create` tool **does exist** but is a
   probe: on UEFN it returns `unavailable` plus the UI steps, so call it only to
   confirm — never as the create path. Do not expect `landscape_sculpt` to change
   visible terrain.

## Slot grid

| Slot | Origin (uu) |
|------|-------------|
| 0 | `[0, 0, 0]` |
| 1 | `[100000, 0, 0]` |
| 2 | `[200000, 0, 0]` |
| n | `[n * 100000, 0, 0]` |

`area_create` assigns the next free slot (or reuses an existing area’s origin).

## Folders

```
Areas/<area_id>/Terrain
Areas/<area_id>/Blockout
Areas/<area_id>/Devices
Areas/<area_id>/Props
Areas/<area_id>/Foliage
```

Tags: `Area:<id>` on area actors; blockout cubes also `BlockoutGenerated`.

## Blockout presets

`blockout_list_presets` → `hub` | `store` | `arena` | `corridor` | `lobby`

```
area_create({"area_id": "hub", "preset": "hub", "seed": 42})
area_create({"area_id": "store", "preset": "store", "seed": 43})
# later dress / devices under Areas/hub/Devices, Areas/store/Props, …
save_current_level()
```

Replace greybox only: `blockout_layout(area_id, preset)` (clears prior Blockout).

## After create

- Place devices/props **inside that area’s folder**, near its origin.
- Verify with `set_viewport_camera` at the area origin + screenshot.
- Connect areas later with teleporters — do not move terrains next to each other.
