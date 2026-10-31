---
description: "Score a city layout — 20-item 1–5 scorecard (Lynch legibility, network, street quality, public spaces, gradient, game fit), thresholds out of 100, evidence rules, fix order"
metadata:
  order: 26
  label: "Urban evaluation"
  default_enabled: false
  load_condition: "User asks to review, score, critique, or improve a city/town layout, or why a city map feels confusing, empty, fake or boring"
---

# Urban evaluation (UEFN)

Source: design-evaluation skill (Gehl + Bentley + PPS + CPTED + Healthy Streets), *Urban Design Skills* (MIT, A. Bhardwaj).

Score each item 1–5 (1 absent/broken, 3 acceptable, 5 excellent) from evidence: eye-height (~170 uu) and top-down `take_high_res_screenshot`, `measure_distance`, a fly-through. Never score from memory.

## Scorecard

**Legibility (Lynch)**
1. Paths — hierarchy readable from width/lighting alone.
2. Edges — every district bounded; map border sealed and plausible.
3. Districts — one prop/material family each, name-worthy character.
4. Nodes — main junctions/plazas hold an objective, shop or landmark.
5. Landmarks — one per district, visible from its entrances; readable skyline.

**Network**
6. Permeability — short blocks; passages ≥ 512 on long faces; ≥ 2 routes between districts.
7. Dead ends — none, or each pays out.
8. Terminated vistas — straights end in landmark/bend, not void or blank wall.
9. Gateways — district entries marked.

**Street quality**
10. Enclosure — H:W 1:3–1:1 on most streets; canyons on purpose.
11. Active frontage — hero streets: door/window/sign every 1–2 cells.
12. Streetscape rhythm — even trees/lamps/furniture; walk zone clear.
13. Scale — eye-level detail; facade broken every 2–4 cells; roofline varies.

**Public spaces**
14. Plaza proportion — width 1–2× edge height, enclosed 3–4 sides.
15. Power of 10 — ≥ 10 things to do in the main space, ≥ 3 per sub-area.
16. Active edges — cover/seating/shops at edges; 30–40 % open floor.

**Gradient & mix**
17. Density gradient — tallest at centre, steps down; no two-zone jumps.
18. Mix — every neighbourhood has a shop, park/playground, civic building.

**Game fit**
19. Gameplay space — sightlines, cover, flanks suit the mode (`combat_spaces`, `player_flow`); vehicle clearances hold.
20. Performance — repeated kits/instancing; sane prop counts per district.

## Thresholds (/100)

| Score | Verdict |
|---|---|
| < 50 | Poor — re-plan network/gradient before dressing |
| 50–64 | Below average — fix every 1–2 |
| 65–79 | Good |
| 80–89 | Very good |
| 90+ | Excellent |
Ship rule: items 1–9 all ≥ 3 (dressing can't fix legibility or network).

## Report

```
CITY EVALUATION — name — date
Total __/100 (verdict)
Lowest 3: #__ — fix · #__ — fix · #__ — fix
Evidence: screenshots [paths], measurements [list]
```
Fix order: network → gradient → public spaces → frontage → dressing.
