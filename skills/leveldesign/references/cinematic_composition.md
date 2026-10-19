---
description: "Cinematic composition for level design — terminated vistas (a castle framed at the end of a road), reveal sequences, pinch-and-release, framing devices, landmark hierarchy, silhouette, atmospheric depth, and how to verify every shot with camera + screenshot"
metadata:
  order: 5
  label: "Cinematic composition"
  default_enabled: false
  load_condition: "User wants a level to look cinematic/epic/dramatic, asks about vistas, views, reveals, framing a landmark or castle, first impressions, skylines, or how a space should FEEL on approach"
---

## Cinematic composition — stage the level like shots

Players experience a level as a sequence of camera frames along their route.
Design the frames, not just the floor plan: decide WHERE the player is when
they first see each landmark, and WHAT surrounds it in that frame. Every
technique below ends the same way — put the camera where the player will be
and look (`set_viewport_camera` at eye height ~170 uu + `take_high_res_screenshot`).

### Terminated vistas — the castle down the road

The single highest-impact trick: aim a straight circulation segment directly
at a landmark so the road itself frames the approach.

- Put the landmark ON the route axis (same X or Y as the road centerline),
  not beside it. Off-axis by half a road width already weakens the shot.
- Approach length 3000–6000 uu of straight route pointed at it; shorter and
  it arrives before it registers, much longer and it flattens out.
- Landmark must clear the foreground: taller than everything flanking the
  route by at least one storey (384 uu). Rough presence check — height at
  least 1/4 of the viewing distance (a 6000 uu approach wants a 1500+ uu
  tall landmark) — then verify with the camera, not the math.
- Rising ground or steps toward the landmark strengthens it; the silhouette
  climbs the sky as you approach.
- Verify from the START of the approach at eye height: is the landmark
  centered, unobstructed, above the flanking rooflines/treelines?

### The reveal sequence — denial and reward

Don't show the landmark once and keep it in frame forever. Sequence it:

1. **Glimpse** — a partial view early (between buildings, through trees, over
   a wall): only a spire or glow.
2. **Denial** — the route bends or drops and the landmark disappears for
   2–4 cells of travel.
3. **Full reveal** — the route opens into the terminated vista or a plaza
   with the landmark dominating the frame.

Screenshot all three beats from the player path — the glimpse must read as
"the same thing" (distinctive silhouette or color), or the reveal loses its
payoff.

### Pinch and release

Compress space right before opening it: a tight threshold (256–384 uu wide,
384 ceiling) or narrow alley that dumps into a grand volume or open vista
makes the open space feel twice its size. Use at dungeon-to-hall transitions,
alley-to-plaza, forest-path-to-clearing, corridor-to-hangar. The pinch should
last 1–2 cells — long enough to feel, short enough not to annoy.

### Framing devices

Put a frame INSIDE the frame at key viewpoints: an arch, gate, twin trees,
hangar doorway, two flanking towers. Place the device 512–1024 uu in front of
the viewpoint on the route axis so the landmark sits inside its opening.
Check at eye height that the opening actually contains the landmark — a frame
that crops the subject is worse than no frame.

### Landmark hierarchy — one weenie, many anchors

- **Primary landmark** ("weenie"): the tallest/brightest thing on the map,
  visible from most outdoor areas — players orient by it constantly. ONE per
  map.
- **Secondary anchors**: one per zone (see Environment elements), each with a
  distinct silhouette so zones are tellable apart at a glance.
- Never let a secondary anchor out-scale the primary from common viewpoints —
  it hijacks orientation.

### Silhouette and skyline

Composition reads by outline first. Vary rooflines/treetops/hull towers so the
skyline has rhythm — a flat skyline reads as unfinished, a spiky uniform one
as noise. Aim for: mostly mid height, occasional low gap, one dominant peak
(the landmark). Check by screenshotting the skyline from the main approaches
and squinting: does the eye land on the landmark?

### Atmospheric depth — three grounds

Compose big views in layers: **foreground** interest within ~1000 uu (a fence,
rocks, a lamppost edge-of-frame), **midground** subject (the landmark or
volume cluster), **background** backdrop (mountains, hull wall, sky). A view
with no foreground element feels like a void; frame-edge props anchor scale.
Fog/haze between grounds (if the project uses it) multiplies perceived
distance.

### Light draws the eye

The brightest, highest-contrast point in frame is where players look and
walk. Light the objective/landmark brighter than its surroundings; keep
competing bright spots out of key frames. In interiors, alternate lit and dim
segments — pools of light every 2–4 cells pace the route and make the lit
destination read as "forward".

### The verification pass (non-negotiable)

Walk the level as a camera:

1. List the key beats: spawn view, each zone entrance, each reveal, the
   terminated vistas.
2. For each: `set_viewport_camera` at the player position, eye height
   ~170 uu above ground (`get_ground_z` first), aimed along the route.
3. `take_high_res_screenshot` and actually look: subject framed? foreground
   anchor present? competing clutter? skyline rhythm?
4. Fix by moving dressing/landmarks — re-shoot until the frame works.

Spawn views matter most: the first frame a player ever sees should be a
composed shot, not the back of a wall.
