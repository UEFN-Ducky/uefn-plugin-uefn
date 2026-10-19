---
description: "POI hierarchy — major/minor landmarks, spacing, skyline, interest pockets on path, hub/adventure patterns (not full BR systems)"
metadata:
  order: 12
  label: "POI hierarchy"
  default_enabled: false
  load_condition: "User asks about landmarks, POIs, points of interest, skyline, map readability, interest density, or major vs minor destinations"
---

# POI hierarchy — orientation without a minimap

Landmarks tell players where they are and where to go. One strong silhouette beats
five competing towers. Cross-link `cinematic_composition` for approach shots and
`player_flow` for pathing.

## Tiers

| Tier | Role | Rules |
|------|------|-------|
| **Major** | Zone identity | One per zone; visible from every zone entrance |
| **Minor** | Connector / sub-goal | On paths between majors; smaller mass / glow |
| **Micro** | Dressing interest | Crates, signs — never compete with majors |

Majors need height and/or unique color/emissive. Verify:

```
set_viewport_camera at each entrance, eye ~170
take_high_res_screenshot()  # landmark must read
```

## Spacing

- Majors far enough that silhouettes don’t merge on the skyline.
- Approach length for a terminated vista: often **3000–6000 uu** of readable
  route aimed at the landmark (`cinematic_composition`).
- Minors every few cells along arteries — breadcrumbs, not clutter.
- `measure_distance` between majors when placing hubs so travel time feels
  intentional.

## Interest density

- Put loot / interactables / side content **on the critical path** or clearly
  marked side pockets — not in off-map dead ends with no return cue.
- Dense pockets + open breathing room > uniform 100% prop coverage
  (`environment_elements` dressing layers).
- Gameplay objects (buttons, objectives) must contrast with dressing.

## Patterns (adventure / hub — not full BR)

| Pattern | POI use |
|---------|---------|
| Hub + spokes | Hub landmark center; each spoke has its own major at the end |
| Linear beats | One landmark per beat; next visible before current ends |
| Open graph | 3–5 majors; trails readable; minors on connectors only |

Full Battle Royale storm/loot economy is **out of scope** — use majors/minors for
readability; systems stay in Verse / Creative devices.

## Skyline checklist

- [ ] From spawn / hub, at least one major readable
- [ ] Zone entrances frame their major (`cinematic_composition`)
- [ ] No two majors same height + same color in one view
- [ ] High ground for vista ≠ unbeatable sniper perch (`combat_spaces`)

## Don'ts

- Don’t place five “main towers” in one district.
- Don’t hide the only landmark behind fog and call it mystery without a glimpse.
- Don’t use Creative devices as skyline (scale/collision lies).
- Don’t dress minors louder than majors.

## Related

- Framing → `cinematic_composition`
- Path → `player_flow`
- Themes → `theme_recipes`
- Director → `full_game_director`
