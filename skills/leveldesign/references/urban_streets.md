---
description: "City streets in uu — hierarchy (boulevard to alley), cross-sections, lane widths for on-foot vs driving maps, intersections, roundabouts, traffic calming as pacing, street trees/lights, transit and pick-up stops"
metadata:
  order: 21
  label: "Urban streets"
  default_enabled: false
  load_condition: "User designs roads, streets, sidewalks, lanes, intersections, roundabouts, a driving/racing/taxi/limo city, crosswalks, street lights or street trees"
---

# Urban streets (UEFN)

Source: NACTO Urban Street Design Guide via *Urban Design Skills* (MIT, A. Bhardwaj), converted to uu.
Rule from `theme_recipes`: **lay the whole road network before the first building.**

## Hierarchy

Lane width: **384** on-foot maps (road is dressing/cover lane), **512** where players drive (Fortnite cars ≈ 500 uu long), **640** for racing, limos, trucks.

| Type | Real ROW | Carriageway | ROW uu (driving) | Notes |
|---|---|---|---|---|
| Boulevard / arterial | 30–40 m | 2×2 lanes + median | 4096–4608 | median 384–640 planted; links districts |
| Avenue / collector | 22–30 m | 2 lanes + parking both sides | 2560–3072 | main shopping street, bus stops |
| Local street | 15–22 m | 2 lanes | 1536–2048 | residential; `theme_recipes` "street 1024" = its carriageway |
| Shared street / woonerf | 8–15 m | flush, no curbs | 1024–1536 | bollards, planters in path, pavers |
| Pedestrian street | 4–20 m | none | 512–1536 | old town, market |
| Alley / service lane | 6 m | 1 lane | 512–768 | block backs, dumpsters, flank routes |

Players should read a street's importance from its width alone.

## Cross-section (building face → centre, mirror the other side)

| Layer | Real | uu | Contents |
|---|---|---|---|
| Frontage zone | 0.3–0.9 m (1.2–2.4 dining) | 32–128 (128–256) | doors, displays, café tables |
| Clear walk zone | 1.8–3.6 m | 256–384 | **nothing** in it |
| Furnishing zone | 0.6–1.8 m | 128–256 | trees, lamps, benches, hydrants, bins |
| Bike lane + buffer | 1.5–2.5 + 0.6 m | 256 | optional |
| Parking lane | 2.1–2.4 m (angled 4.5–5.8) | 256–320 (512–640) | parked cars = cover |
| Travel lane | 3.0–3.3 m | 384 / 512 / 640 | see above |
| Median | 1.2–6.0 m | 256–640 | refuge, trees, tram |

Curb 16–24 uu high. Sidewalk top flush with building floor.

**Avenue, driving (≈ 3072):** `frontage 64 | walk 384 | furnish 192 | park 288 | lane 512 | lane 512 | park 288 | furnish 192 | walk 384 | frontage 64` = 2880, widen frontage to 3072.
**Local residential (1792):** `walk 256 | furnish 128 | lane 512 | lane 512 | furnish 128 | walk 256`.

## Intersections

- Compact corners: curb radius 128–256 on-foot, 384–512 driving, 768+ trucks/racing.
- Crosswalk 256–384 (commercial 384–512) on the walking desire line.
- Curb extensions shorten crossings and give corner cover.
- **T-intersections** make terminated vistas — landmark or notable facade where the stem hits.
- Plazas often sit where major streets meet (Lynch node).

| Roundabout | Real Ø | uu Ø |
|---|---|---|
| Mini | 13–25 m | 1536–2560 |
| Single-lane | 25–30 m | 2560–3072 |
| Multi-lane | 45–55 m | 4608–5632 |
Central island = landmark spot.

## Traffic calming → pacing

| Real measure | UEFN use |
|---|---|
| Chicane | slows drivers; zig-zag cover on foot |
| Speed table / raised crossing | 8–16 uu bump; exaggerate for racing jumps |
| Neckdown / pinch point | chokepoint 384–512 |
| Asphalt → pavers | signals pedestrian zone / district entry |
| Gateway (narrowing + arch/landmark) | readable district border |
| No straight > 30–50 m in shared streets | ≤ 4–6 cells before a bend, planter or junction |

## Streetscape rhythm

| Element | Real | uu |
|---|---|---|
| Street trees | 6–12 m apart | 768–1280 |
| Pedestrian lamp | 4–6 m tall | 400–600 tall, 1280–1536 apart |
| Road lamp | 8–12 m tall | 800–1200 tall, 2560–3072 apart |
| Bench along path | every 30 m | ~3000 |
| Bus shelter | 1.5 × 3–6 m | 192 × 384–640 |
| Bollards | 1.2–1.8 m apart | 128–192 (players pass, cars don't) |
Place with `distribute_actors` (even = man-made). Stagger trees and lamps. Brightest at intersections and crosswalks; commercial streets warmer/brighter than residential (`lighting`).

## Transit & stops (driving / taxi / limo)

- Stops every 1–2 blocks, at nodes.
- Density and shops peak around stations: tallest within ~1 block, tapering out.
- Pick-up/drop-off bay: parking-lane pocket 288–320 × 1024–1536, curb clear of props.
- Station forecourt = small plaza with a landmark.

## Spec template

```
STREET: name · TYPE · MAP: on-foot/driving
ROW: ____ uu (frontage | walk | furnish | park | lanes×N | median | mirror)
Intersections: curb radius __ · crosswalk __ · roundabout Ø __
Rhythm: trees @__ · lamps @__ · benches @__
Pacing: __ · Terminates at: landmark / bend / edge
```
