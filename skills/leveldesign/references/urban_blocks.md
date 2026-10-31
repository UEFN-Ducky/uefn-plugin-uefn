---
description: "City blocks and buildings in cells/uu — 9 block typologies, block size and mid-block passage rules, height vs coverage, courtyards, corners, facade variation, towers"
metadata:
  order: 22
  label: "Urban blocks & buildings"
  default_enabled: false
  load_condition: "User asks about city blocks, building footprints, building heights, skyscrapers, towers, courtyards, apartment blocks, rowhouses, suburbs, density, or how big buildings and blocks should be"
---

# Urban blocks & buildings (UEFN)

Source: block-and-density skill, *Urban Design Skills* (MIT, A. Bhardwaj). Cell = 512, storey = 384 (`urban_design` conversion).

## Block typologies

| Type | Block (cells) | Coverage | Height | Character / gameplay |
|---|---|---|---|---|
| **Perimeter block** | 6×6 – 8×8 | 55–70 % | 4–8 st (1536–3072) | continuous street wall, hidden courtyard pocket |
| **Courtyard block** | 5×5 – 7×7 | 40–55 % | 3–6 st | several yards; loot rooms |
| **Row / terrace** | 4 × 10–16 | 50–65 % | 2–4 st | narrow houses (lot 1–1.5 cells), back gardens |
| **Mansion block** | 4×6 – 5×7 | 50–65 % | 5–8 st | big apartment buildings with lobbies |
| **Tower-podium** | 6×6 – 8×8 | podium 60–75 %, tower 15–30 % | podium 3–5 + tower 20–60 st | downtown core; tower = landmark |
| **Superblock / tower-in-park** | 12–30 per side | 20–35 % | 8–30 st | open lawns, long sightlines |
| **Villa / garden** | 5×8 – 6×10 | 25–35 % | 1–3 st | suburb, fences, yards |
| **Campus** | 10–20 per side | 25–40 % | 1–6 st | school, base, HQ; quads |
| **Hybrid** | variable | variable | mixed | rowhouses + mid-rise + one tower — best variety |

Pick by intensity: low → villa/row; medium → courtyard/mansion; high → perimeter/hybrid; very high → tower-podium. By feel: enclosed → perimeter/row/mansion; open → superblock/villa/campus.

## Block rules

- 4–8 cells per side on-foot, up to 16 on driving maps.
- **Mid-block passage:** a face > 8 cells needs a passage every 4–6 cells, **≥ 512 wide**, sightline end-to-end. Covered passages ≤ 3 cells and lit.
- Every block has ≥ 2 street frontages.
- **Building depth** 2–3 cells (1024–1536); deeper reads as warehouse/mall.
- **Courtyard:** narrowest side ≥ surrounding wall height (45° rule) and ≥ 4 cells.
- Opposite facades ≥ 4 cells apart across courtyards.
- **Service** in a rear alley 512–768: bins, docks, garage doors — off the hero street.
- **Parking** behind, below or inside the block, never as the street frontage.

## Height ↔ coverage (same density, different city)

FAR = floor area ÷ site area (scale-free).

| FAR | Low-rise | Mid-rise | High-rise |
|---|---|---|---|
| 1 | 2 st, 50 % | 4 st, 25 % | 10 st, 10 % |
| 2 | 2 st, 100 % | 4 st, 50 % | 8 st, 25 % |
| 3 | 3 st, 100 % | 6 st, 50 % | 10 st, 30 % |
| 5 | 5 st, 100 % | 10 st, 50 % | 20 st, 25 % |
| 8 | 8 st, 100 % | 16 st, 50 % | 32 st, 25 % |

- **Low-rise, high coverage:** intimate, many doors, tight lanes — old town, market.
- **Mid-rise 4–8 st at 50–65 %:** best all-round — strong streets, real courtyards. Default.
- **High-rise, low coverage:** open ground, long sightlines — downtown core only; each tower is a landmark.

## Variation & character

- Vary height **1–2 storeys** per block; never one flat roofline.
- **Corners:** +1–2 storeys, shop/café ground floor, chamfer 384–512 at 45° or a turret.
- **Facade segments:** change material/colour/windows or recess/project 128–256 every 2–4 cells; > 8 cells of one facade reads as copy-paste.
- Balconies, awnings, signage = personalization. One module kit, varied trims (`duplicate_actor` + `align_actors`).
- Ground floor 512 (shops) vs 384 (homes) — the eye reads use from ground-floor height and glass.

## Towers

- Podium 3–5 storeys; tower stepped back ≥ 384–768 from the podium face.
- Towers ≥ 5 cells apart; slim plates (≤ 4×4 cells) read elegant.
- Tallest at centre / transit node, stepping down to edges.
- H:W > 3:1 goes dark — plan street lights or accept a night-canyon mood.

## Block spec

```
BLOCK id · typology · transect zone
Size __×__ cells · passages @__
Depth __ · storeys __–__ (corner +__) · coverage __%
Courtyard __×__ (≥ wall height?)
Ground floor shops/homes · active frontage __%
Service alley __ · parking behind/podium/none
Facade segment every __ cells · landmark corner?
```
