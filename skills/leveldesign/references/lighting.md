---
description: "UEFN lighting — directional/sky/point/spot lights, Day Sequence, fog/post-process, mobility, interior vs exterior recipes, verify with screenshots"
metadata:
  order: 7
  label: "Lighting"
  default_enabled: false
  load_condition: "User asks about lights, lighting, day/night, sky, sun, fog, mood, atmosphere, dark scene, flat gray look, or making a space feel lit"
---

# Lighting — make the island read

Flat gray scenes kill form. Light is layout: decide sun direction, fill, and accents
before polishing props. Verify every change with `set_viewport_camera` +
`take_high_res_screenshot` (or PIE). Load this when the ask is mood, day/night,
or "why does it look washed out."

**Stars / night sky (HARD):** not lighting, not a texture, not Niagara sprites.
`skill_read_subskill("materials", "starfield_recipe")` only.

## Units reminder

- 1 uu = 1 cm. Player eye ≈ **170 uu**.
- Fortnite build cell = **512 uu**. Place practical lights on cell centers when possible.

## Light types (what to place)

| Role | Typical actor / device | Use |
|------|------------------------|-----|
| Key (sun) | Directional Light | Exterior key; one dominant |
| Sky / ambient | Sky Light + sky / atmosphere | Fill so shadows aren't pure black |
| Local fill | Point / Spot / Rect | Interiors, caves, neon accents |
| Time of day | Day Sequence device | Animated sun/sky cycle |
| Atmosphere | Exponential Height Fog, Post Process Volume | Depth + grade |

Discover what exists:

```
get_all_actors(label_filter=\"Day\")
get_all_actors(class_filter="DirectionalLight")
get_all_actors(class_filter="SkyLight")
get_all_actors(class_filter="PointLight")
```

Spawn engine lights with `spawn_actor` when the class/asset is available in the
project; Creative lighting devices via Epic `ValkyrieToolset.DeviceToolset` (`ListDeviceAssets`) or `get_all_actors(label_filter=…)`.
Confirm class names with `list_actor_classes` / `search_assets` — don't invent paths.

Tune via `get_actor_properties` → `set_actor_properties` (Intensity, LightColor,
Temperature, AttenuationRadius, Inner/OuterConeAngle, Mobility). Re-read after set.

## Mobility (UEFN reality)

| Mobility | When |
|----------|------|
| **Static** | Baked / unchanging — prefer for most set dressing |
| **Stationary** | Fixed position, dynamic shadows (build-dependent) |
| **Movable** | Moving or toggled lights — costlier; use sparingly |

Don't make every prop light Movable. One key Directional + Sky, then few local accents.

## Starting values (Fortnite-readable)

Exterior day:

- Directional: warm white (~5500–6500 K) or slight gold; intensity high enough that
  materials show albedo (if everything is matte gray, raise key *or* fix materials —
  see materials pack).
- Sky Light: capture or low intensity fill so cavities read.
- Sun pitch ~35–55° for readable form; noon-flat washes normals.

Interior:

- Dim or kill Directional contribution in sealed rooms (geometry / fog / intensity).
- Point lights: attenuation covering the room (512–2048 uu typical); warm key + cooler fill.
- Spot for shafts / doorways; aim at floor or hero prop, not the camera.
- Emissive materials (`materials` pack) as glow panels — not a substitute for all fill.

Night / neon:

- Low Directional; colored Point/Spot accents; fog density up slightly for depth.
- Avoid pure #00FF00 neon — desaturate; Fortnite grading already punches color.

## Day Sequence vs static

- **Static look**: place Directional + Sky, set once, leave Day Sequence off or unused.
- **Cycle / mood beats**: Day Sequence device — set time, transitions; one device owns TOD.
- Don't fight Day Sequence with a second Directional you keep re-aiming every test.

Wire/trigger Day Sequence like other Creative devices (Epic `DeviceToolset` `GetDeviceProperties` /
Epic `DeviceToolset` `SetDeviceProperty`). Verify exact field names on the device.

## Fog + post

- Exponential Height Fog: slight density for depth; too much = milky wash.
- Post Process Volume (unbound or large): exposure, contrast, saturation — subtle.
- After fog/PP changes: screenshot from the same camera as before.

## Interior vs exterior recipes

**Exterior plaza**

1. One Directional (key) + Sky Light.
2. Landmark gets rim from sun angle (compose with `cinematic_composition`).
3. Optional Spot on hero statue / door.
4. Screenshot at eye height on approach path.

**Interior room**

1. Ceiling Point or Rect as key; cooler fill opposite.
2. Doorway Spot leaking exterior color into the room.
3. Emissive trim on important edges.
4. Screenshot from doorway *and* room center — both must read.

## Flat gray / muddy failure table

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Everything gray, no form | No key light / intensity ~0 | Add/raise Directional or Point |
| Plastic / blown highlights | Exposure + albedo too bright | Lower light or darken BaseColor |
| Pure black caves | No Sky / bounce / fill | Sky Light or dim Point fill |
| Looks fine in editor, dark in PIE | Day Sequence / device state | Check TOD device + play from start |
| Neon scream | Oversaturated LightColor | Desaturate; use emissive materials |
| Flicker / cost | Too many Movable lights | Static/Stationary; fewer accents |

## Verify loop

```
set_viewport_camera({... eye ~170 uu on player path ...})
take_high_res_screenshot()
# compare: can you read silhouettes? key direction? hero accent?
save_current_level()
```

For cinematic approaches, also load `cinematic_composition`.

## Don'ts

- Don't add 40 Point lights "to make it pretty" — three good lights beat forty bad ones.
- Don't skip screenshots after light tweaks.
- Don't confuse the **Light** UI theme plugin with engine lighting — this ref is the skill.
- Don't leave Day Sequence and a hand-aimed sun fighting each other.

## Related

- Materials / emissive fill → `materials` pack (`creating_materials`, `pbr_master_instances`).
- Shot framing → `cinematic_composition`.
- Atmosphere mood in layout → `theme_recipes`, `design_styles`.
