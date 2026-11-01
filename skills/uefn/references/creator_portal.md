---
description: "Publishing and Creator Portal (v42.30 / v42.40 / v43.00) — v43.00 Projects > Technical Client/Server tabs (crashes, hitch rate, missed frames, server frame time / CPU / memory P95), rejection explanations with video/image/thumbnail/audio, Progression API and PointerZoom publishable, EDC feedback form; required Discover artwork from Oct 22 2026 (landscape + portrait thumbnails, logo; gameplay video), the IARC questionnaire inside the publish flow, analytics benchmarks (CTR, bounce, session length, D1/D7), offer validation errors for in-island transactions, memory moving into profiling (MB, 300 MB = 100,000 units), Rocket Racing template islands unpublished, UEFN source assets on Fab (licensing live)"
metadata:
  order: 13
  label: "Creator Portal & publishing (v43.00)"
  default_enabled: false
  load_condition: "Publishing or updating an island, Creator Portal Technical tab (client crashes, hitch rate, missed frames, server frame time / CPU / memory), a moderation rejection and its explanation, thumbnails / key art / logo / trailer / gameplay video for Discover, IARC age rating questionnaire, analytics, benchmarks, retention, CTR, bounce rate, offers / V-Bucks validation errors, publish memory limit or memory thermometer, Rocket Racing islands, selling on Fab, UEFN source assets"
---

# Creator Portal and publishing (v43.00)

## Island performance — Projects > Technical (v43.00)

The **Technical** tab now has two subtabs. Every time-series chart has **version markers**
for each published update, so you can see what an update changed.

| Subtab | Metric | Shown as / target |
| --- | --- | --- |
| Client | **Client Crashes** (new) | % of player sessions that ended because the game failed, against top islands across genres; filter by platform or failure type (incl. memory failures) |
| Client | **Hitch Rate** | how often players see noticeable stutters |
| Client | **Missed Frames** | how often frames are not drawn on time |
| Server | **Frame Time** | P95 and median vs a **33.3 ms** target (30 FPS) |
| Server | **CPU Usage** | share of one core, P95 and median vs a **75%** target |
| Server | **Memory Usage** | GB, P95 and median vs a top-islands benchmark |

High server frame time, CPU or memory lags **every** player in the session. Over target →
reproduce locally with the profiling tools (`profiling`: Spatial Profiler, Timing / Verse
Insights with Server as target, Memory Snapshot), fix, publish, and read the next version
marker. Offer validation errors stay on the same tab (below).

## Rejection explanations (v43.00)

Moderation rejections can now come with: a **gameplay video** capturing the reason (most
common ratings issues), a **preview of the image asset** that triggered it, the
**thumbnail Epic reviewed**, and **playable audio** for rejected sounds. Fix that exact asset
(the Island Media Kit re-exports artwork) and resubmit. Epic: "Island Moderation Tips and FAQs".

## Newly publishable in v43.00

- **Progression API** (quests, objectives, rewards) is out of Experimental — islands using it
  can publish (verse `sys_quests`).
- **PointerZoom** (pinch-to-zoom on the virtual pointer; also mouse wheel and gamepad right
  stick) is out of Experimental (`virtualpointer`).

## Feedback form (v43.00)

The EDC forums have a dedicated **feedback form**, separate from Issues and Bug Reporting:
pick a topic (Verse, UEFN, Creator Portal…), write a summary, attach images or video; the
community upvotes and you follow status by ticket ID. Bugs still go to Issues and Bug Reporting.

## Discover artwork — required from Oct 22 2026

42.40 started a phased Discover redesign (autoplay video, new tile shapes, cleaner
logos). **From Oct 22 2026 an island can't be published or updated without** its
landscape thumbnails, portrait thumbnails and logo (Creator Portal → Promotional Media):

| Asset | Size | Format |
| --- | --- | --- |
| Landscape thumbnail, art + logo | 1920 × 1080 (16:9) | PNG or JPG |
| Landscape thumbnail, art only | 1920 × 1080 | PNG or JPG |
| Portrait thumbnail, art + logo (one flat image) | 1440 × 1920 (3:4) | PNG or JPG |
| Portrait thumbnail, art only | 1440 × 1920 | PNG or JPG |
| Island name logo | 1440 × 608 | **transparent** PNG |

The platform places the logo on art-only tiles itself, at the top or bottom — keep those
areas clear and the logo readable; keep ~200 px top and bottom of landscape art free of
UI (tags, player counts). No Fortnite logo, no third-party IP. Optional: a **trailer**
(15–30 s, 16:9, MOV ProRes, native frame rate, uncompressed stereo; needed for the Hero
carousel / Epic's Picks, GA content only) and, new, a **gameplay video** for the details
page (same specs, real unedited gameplay with UI). Make all of them from the user's own
footage with the **Island Media Kit** plugin (`island-media-kit` skill: artwork exports,
Auto Trailer, gameplay video, ProRes export) — it checks the sizes for you.

## IARC age rating (42.40)

The IARC questionnaire is now a step **inside** the Creator Portal publish flow, before
moderation (no trip to the IARC site). Ratings show on the Ratings tab. Retake it when
an update changes your answers.

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

## Memory: thermometer → profiling (done in v43.00)

- The publish memory limit is unchanged; it now **displays in real units** (e.g.
  **300 MB** instead of 100,000 units), matching other memory tools.
- Memory is calculated **on every cook** (each session launch or pushed change gives a new
  value). Over the limit → the **Game Performance** report at the bottom of the editor
  flags it, with a **per-asset breakdown** of what drives it. Run the publish memory check
  on demand from the profiling tools.
- **The memory thermometer no longer appears in running sessions** (v43.00).
- Ducky's "memory calculation" button keeps working; read results as MB.

## Rocket Racing

Islands built with **Rocket Racing templates are unpublished and no longer
playable**; publishing updates for new or existing Rocket Racing islands is
disabled. The racing tools — **Track Spline Tool, Boost Pads, Volume Hazards,
Spawner devices** — work without the template. To keep an island, convert it to a
regular island (Epic: "Converting Your Island Into a Brand Island"). Vehicle
Locker cars are unaffected.

## UEFN source assets on Fab

Complete, editable systems built with Verse and Scene Graph (AI / NPC behaviors,
vehicles, weapons, UI, environments) that open directly in UEFN. **Licensing is live
since Oct 15 2026** (42.40): browse on Fab or in the **Fab window inside UEFN**; Epic's
free starter kit is the **Verse UI Kit** (verse `verse_ui_kit`). Sellers keep **88%** of
net revenue. Epic: "Upload Unreal Editor for Fortnite Source to Fab".
