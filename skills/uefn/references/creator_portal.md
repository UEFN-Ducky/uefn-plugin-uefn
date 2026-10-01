---
description: "Publishing and Creator Portal (v42.30) — analytics benchmarks (CTR, bounce, session length, D1/D7), offer validation errors for in-island transactions, memory moving into profiling (MB, 300 MB = 100,000 units), Rocket Racing template islands unpublished, UEFN source assets on Fab"
metadata:
  order: 13
  label: "Creator Portal & publishing (v42.30)"
  default_enabled: false
  load_condition: "Analytics, benchmarks, retention, CTR, bounce rate, offers / V-Bucks validation errors, publish memory limit or memory thermometer, Rocket Racing islands, selling on Fab, UEFN source assets"
---

# Creator Portal and publishing (v42.30)

## Analytics benchmarks

Percentile goals that compare your island with the top islands in its genre, on
the Creator Portal analytics charts you already use: **click-through rate**,
**bounce rate (5-minute)**, **average session length**, **D1 retention**,
**D7 retention**. Toggle benchmarks on a chart: your line over shaded percentile
bands and a dashed cohort median.

Reading them: CTR above peers but bounce worse than peers usually means the
thumbnail / Discover promise does not match the first minutes in game — fix the
opening, not the thumbnail.

## Offer validation errors (in-island transactions)

Project page → **Technical** tab: errors grouped by error type, offer and link
mode; filter by link mode or error; sort newest/oldest. Select a row for details
(prices outside the allowed range, offers over max entitlements…) with counts and
the latest time. Fix offers in Verse (`/UnrealEngine.com/Marketplace`, verse
`sys_marketplace`) and republish.

## Memory: thermometer → profiling

- The publish memory limit is unchanged (**100,000 units**) but will be shown as
  **300 MB**, matching other memory tools.
- Memory is calculated **automatically on every cook** (any session launch or push).
  Over the limit → the **Game Performance** report at the bottom of the editor says
  so, with a **per-asset memory digest** showing what drives it. Manual calculation
  still works.
- A later release removes the memory thermometer from running sessions.
- Ducky's "memory calculation" button keeps working; read results as MB going forward.

## Rocket Racing

Islands built with **Rocket Racing templates are unpublished and no longer
playable**; publishing updates for new or existing Rocket Racing islands is
disabled. The racing tools — **Track Spline Tool, Boost Pads, Volume Hazards,
Spawner devices** — work without the template. To keep an island, convert it to a
regular island (Epic: "Converting Your Island Into a Brand Island"). Vehicle
Locker cars are unaffected.

## UEFN source assets on Fab

Sell complete, editable systems built with Verse and Scene Graph that other
creators open and modify in UEFN. Uploads are open; publishing starts **Oct 15
2026**; you keep **88%** of net revenue. Epic: "Upload Unreal Editor for Fortnite
Source to Fab".
