---
description: "Combat space design — Epic cover/mantle heights (96 / 288 / >520), sightlines, high ground, flanks, build-fight floors, verify both sides"
metadata:
  order: 9
  label: "Combat spaces"
  default_enabled: false
  load_condition: "User asks about cover, combat arenas, sightlines, high ground, flanking, mantle heights, fight spaces, or PvP layout"
---

# Combat spaces — readable fights

Cover and height must be **readable at a glance** (Epic Level Design Fundamentals).
Wrong sizes frustrate: players try to mantle a “wall” that isn’t, or crouch behind
“cover” that doesn’t hide them.

## Epic Fortnite metrics (uu = cm)

| Element | Height | Notes |
|---------|--------|-------|
| Player | ~190 | Eye ~170 for screenshots |
| **Low cover** | **~96** | ~½ player — crouch / peek |
| **High cover** | **≥ 288** | ~1.5× player — hides vs higher ground |
| Wall module | 512 W × **384** H | Standard storey |
| **Unmantleable** | **> 520** | Clearly above mantle; don’t sit at 500–520 |
| Floor cell | 512 × 512 | Snap structures to 512 |

Corridor / lane width for fights: prefer **512–1024** (1–2 cells). Sub-256 is
single-file tense; over ~768 without props feels empty.

## Cover rhythm

- Alternate open ground and cover every **2–4 cells**.
- `measure_distance` between cover pieces — dashes must be survivable for the mode.
- Corners/junctions get peek cover; open floors get **1–2 islands**, not a maze.
- **Less cover is often better** — too much blocks awareness and creates cheese pockets.

| Good cover | Bad cover |
|------------|-----------|
| Flankable from a side | Full protection, no flank |
| Readable height (96 vs 288) | Ambiguous ~200 “maybe mantle?” |
| Width for one player | Fortress for a whole team with no counter |

## Sightlines

Design for engagement bands (rough, mode-dependent):

| Band | Feel | Layout |
|------|------|--------|
| Close | Rooms, tight connectors | Multiple entries |
| Mid | Arenas with partial cover | Broken LOS |
| Long | Rare, telegraphed | Don’t give free map-wide perch |

**Anti-rules:**

- No single high ground with **full-map** sightlines.
- Break long corridors with offsets, pillars, or bends (`player_flow`).
- Verify both sides of a fight: screenshot from A looking at B and reverse.

## High ground budget

- Contested high ground is good; dominant sniper loft is not.
- Stairs/ramps readable; deny silent roof access unless the mode is about it.
- For **box fight / build modes**: leave intentional empty floors — players build
  their own cover. Don’t pre-clutter every cell.

## Flanks vs camping

- Give at least one alternate approach into main arenas (longer/riskier).
- Spawn-adjacent pockets that see the whole mid = camping; seal or soften.
- Mirror competitive maps: identical cover distances both sides
  (`measure_distance`).

## Verify

```
measure_distance between cover pieces / lane widths
set_viewport_camera at eye ~170 on both sides of the engagement
take_high_res_screenshot()
```

Check: can I tell low vs high cover? Is the next cover reachable? Is anyone
spawn-camped from here? (`spawn_and_fairness`)

## Don'ts

- Don’t use 400 uu walls as “unclimbable” — sit clearly **> 520**.
- Don’t fill 100% of the floor with mid props.
- Don’t copy a cinematic vista perch that also wins every aim duel.
- Don’t skip the reverse-angle screenshot.

## Related

- Flow into the fight → `player_flow`
- Cover atoms → `environment_elements`
- Spawns → `spawn_and_fairness`
- Mode order → `full_game_director`
- Genre sketches → `design_styles`
