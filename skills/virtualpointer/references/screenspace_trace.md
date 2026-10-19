---
description: "Find world objects under a tap or click: deproject the Virtual Pointer position into a ray, sweep the scene, API notes and tuning"
metadata:
  label: "Screen-space trace"
---

# Screen-space deproject + world sweep

> **Snippets here are fragments.** The `using` block in this file's first code
> block applies to all of them — copy those imports (or start from the matching
> `verse_template_apply` pack) when pasting into a real `.verse` file.

Detect world objects (Scene Graph entities, props with collision) under the Virtual Pointer after a `PointerSelect` event.

## Deproject

```verse
TraceFromClick(Player : player, ClickX : float, ClickY : float)<reads>:deproject_results =
    Player.DeprojectViewportToWorld(vector3{Left := ClickX, Up := ClickY, Forward := 0.0})
```

- `(Player:player).DeprojectViewportToWorld(ViewportPosition:vector3)<reads>:deproject_results` in `/Verse.org/Input` (FN ≥ 4100).
- Input is screen **cm**: `Left` rightward from top-left, `Up` upward. `Forward` ignored.
- `deproject_results.Origin` = world position of the **camera eye** (not the near plane). `Direction` = normalized ray.
- Because Origin is the eye, the ray can hit geometry between camera and near plane (e.g. the player pawn). Filter those hits or start the sweep further along `Direction`.
- Inverse: `Player.ProjectWorldToViewport(WorldPosition)<decides><reads>:vector3`.

## Sweep from click

Requires `using { /Verse.org/SceneGraph }` — Epic's doc sample omits it and fails with "Unknown identifier `collision_point`" / "Unknown member `FindSweepHits` in `entity`".

```verse
using { /Verse.org/SceneGraph }
using { /Verse.org/SpatialMath }

PlayerClicked(Arg : tuple(player, vector3)):void =
    Player := Arg(0)
    ClickPos := Arg(1)

    Ray := TraceFromClick(Player, ClickPos.Left, ClickPos.Up)
    RayOrigin := Ray.Origin
    RayDir := Ray.Direction

    # Sweep: ray direction * max distance (cm)
    Displacement := RayDir * 50000.0
    StartTransform := transform{Translation := RayOrigin}
    CollisionShape := collision_point{}

    Hits := for:
        Hit : GetSimulationEntity[].FindSweepHits(Displacement, StartTransform, CollisionShape)
    do:
        Hit

    if (FirstHit := Hits[0]):
        Print("HIT something at {FirstHit.ContactPosition}!")
    else:
        Print("MISS")
```

## API notes (digest-verified)

- `(Entity:entity).FindSweepHits(Displacement:vector3, StartGlobalTransform:transform, Volume:collision_volume)<transacts>:generator(sweep_hit)` — `/Verse.org/SceneGraph`. Hits sorted by distance; overlaps first, the blocking hit last.
- `collision_point` is a `<concrete>` `collision_element` (a `collision_volume`), so `collision_point{}` is a valid ray probe. Other probes: `collision_sphere`, `collision_capsule`, `collision_box`.
- `GetSimulationEntity[]` is available on `creative_device` (`/Fortnite.com/Devices`) and on any `entity` — the rootmost scene entity that gives the query its context.
- `sweep_hit` fields include `ContactPosition`, `SourceComponent`, `TargetVolume` — confirm extra members with `get_verse_api("sweep_hit")` before use.

## Tuning

- Max distance `50000.0` cm (500 m) is Epic's sample; shrink for small islands.
- To act on the hit entity, walk `TargetVolume` / target component to its owning `entity` (check `sweep_hit` in the digest for the exact member names).

Full device: `example_trace_device.md` or `verse_template_apply("vp_screenspace_trace")`.
