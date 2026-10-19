---
description: "Blockout playtest — label volumes, eye-height fly-through, jump/choke/skip audit, fail criteria before theme art"
metadata:
  order: 11
  label: "Blockout playtest"
  default_enabled: false
  load_condition: "User is greyboxing, blockouting, playtesting a rough map, asks when to stop dressing, or flow feels wrong before art"
---

# Blockout playtest — fail grey before dressing

Never start with final art. Rough volumes → walk the flow → only then theme
(`design_styles`, `theme_recipes`). Large greybox placement: leveldesign SKILL.md
**Greybox / large blockout golden path** (`blockout_layout` / `area_create` /
`pcg_generate` / `foliage_scatter`, serial `spawn_actor` leftovers — never a
bulk `execute_python` spawn loop).

## Label intent

Every volume states its job — use Outliner folders + labels:

| Folder / tag | Meaning |
|--------------|---------|
| `Blockout/SAFE` | Lobby, heal, no combat |
| `Blockout/COMBAT` | Fight space |
| `Blockout/TRANSIT` | Corridor / connector |
| `Blockout/PUZZLE` | Non-combat challenge |
| `Blockout/REWARD` | Loot / unlock beat |
| `Blockout/LANDMARK` | Major silhouette mass |

```
set_actor_folder / set_actor_label
```

If you can’t name the function, the space isn’t designed yet.

## Metrics while blocking

- Snap structure to **512**; storey **384**; openings ≥ **256×384**.
- Cover placeholders at **~96** (low) and **≥288** (high); walls that must block
  mantle **> 520** (`combat_spaces`).
- Keep blockout in `Blockout/…` so you can hide/delete wholesale.

## Eye-height fly-through (required)

Simulate the critical path (`player_flow`):

1. Start at each spawn pad (or lobby exit).
2. `set_viewport_camera` at ground + **~170** uu eye, look along intended forward.
3. `take_high_res_screenshot` at: spawn exit, every junction, every combat entry,
   objective approach, landmark reveal.
4. Note hesitation: “Where do I go?” / “Can I jump that?” / “Am I spawn-camped?”

Top-down editor view **does not** count as playtest.

## Audit list

| Check | How |
|-------|-----|
| Jump gaps | Intended jumps clear; skips sealed |
| Chokes | Unintended single-file from prop clutter — clear or intentional |
| Skip routes | Side sightlines / roof access that bypass beats |
| Scale lies | `get_actor_bounds` on “doors” / “buildings” vs 384/512 |
| Footprint | `get_level_bounds` — no stray actor at 100000 |
| Clear routes | `check_area_clear` along artery after props |

## Fail → re-block (stop dressing)

Return to volumes if any are true:

- Players (or you) get lost at the same junction twice
- Spawn sees mid / enemy pad
- Landmark not visible from zone entrances
- Corridor wider than ~768 with no purpose (empty) or under 256 (broken)
- Theme art already started — **tear art back**, don’t paint over bad flow

## Pass → next

`player_flow` polish → `combat_spaces` → `spawn_and_fairness` → objectives/zones →
then `theme_recipes`. Order: `full_game_director`.

## Don'ts

- Don’t scatter marketplace props before the fly-through passes.
- Don’t “fix flow” with only brighter materials — fix geometry.
- Don’t spawn hundreds of cubes via parallel `spawn_actor` or an `execute_python`
  spawn loop — `blockout_layout` / `area_create` / serial `spawn_actor`.
- Don’t delete Blockout folder until final art replaces it on purpose.

## Related

- Greybox tools → leveldesign SKILL.md, `procedural_generation`
- Flow / combat / spawns → `player_flow`, `combat_spaces`, `spawn_and_fairness`
- Director → `full_game_director`
