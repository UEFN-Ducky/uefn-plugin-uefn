---
description: "Verse physics — volume PropEnter/PropExit, creative_prop and fort_character velocity/impulse/force APIs"
metadata:
  order: 30
  label: "Verse physics"
  default_enabled: false
  load_condition: "Verse goals, prop enter/exit, ApplyLinearImpulse, SetLinearVelocity, or physics forces on props/characters"
---

# Verse physics APIs

**Always verify** with `search_verse_digest` / `get_verse_api`. Names below match current
Fortnite digest (Physics Beta). Epic marketing docs sometimes say PropEntersEvent —
the digest name is **PropEnterEvent**.

All impulse/velocity/force calls **no-op if Physics is disabled** on the project.

## volume_device

```
PropEnterEvent : listenable(creative_prop)
PropExitEvent  : listenable(creative_prop)
```

Also: `AgentEntersEvent` / `AgentExitsEvent` for agents (separate from props).

```verse
using { /Fortnite.com/Devices }
using { /Verse.org/Simulation }

# Subscribe in OnBegin
TeamAGoal.PropEnterEvent.Subscribe(OnTeamAGoalEnter)

OnTeamAGoalEnter(Prop : creative_prop) : void =
    # score / HUD / reset ball
```

Device UI equivalent: Physics Events Enabled → On Physics Enter / Exit.

## creative_prop

| API | Notes |
|-----|--------|
| `GetLinearVelocity()` / `SetLinearVelocity(v)` | m/s |
| `ApplyLinearImpulse(v)` | N·s |
| `GetAngularVelocity()` / `SetAngularVelocity(v)` | rad/s |
| `ApplyAngularImpulse(v)` | N·m·s |
| `GetMass()` | kg |
| `ApplyForce(v)` | N |
| `ApplyTorque(v)` | N·m |
| `GetDynamic()` / `SetDynamic(logic)` | SetDynamic needs FortPhysicsComponent + Physics enabled |

Spatial math: `/Verse.org/SpatialMath` `vector3` on these APIs (digest).

## fort_character

| API | Notes |
|-----|--------|
| `GetLinearVelocity()` / `SetLinearVelocity(v)` | m/s |
| `ApplyLinearImpulse(v)` | N·s |
| `GetMass()` | kg |
| `ApplyForce(v)` | N |

No angular impulse/torque on character in current digest.

## Reset a physics ball (soccer pattern)

```verse
using { /UnrealEngine.com/Temporary/SpatialMath }   # TeleportTo takes the X/Y/Z vector3

ResetBall()<suspends> : void =
    HidePos := vector3{X := 880.0, Y := 4000.0, Z := 200.0}
    if (FootballA.TeleportTo[HidePos, IdentityRotation()]) {}   # empty body on the SAME line
    Sleep(3.0)
    ResetPos := vector3{X := 0.0, Y := 0.0, Z := 400.0}
    if (FootballA.TeleportTo[ResetPos, IdentityRotation()]) {}
    FootballA.SetLinearVelocity(vector3{})                      # kill drift after the teleport
    FootballA.SetAngularVelocity(vector3{})
```

`if (...):` followed by an unindented next statement is parse error 3100 — an empty
body must be `{}` on the same line.

**Two `vector3` families, and these APIs disagree:** the impulse/velocity calls above
take `(/Verse.org/SpatialMath:)vector3` (fields `Forward` / `Left` / `Up`), while
`creative_prop.TeleportTo` takes `(/UnrealEngine.com/Temporary/SpatialMath:)vector3`
(fields `X` / `Y` / `Z`). In a file that imports both, qualify the type the way the
digest does or the build silently picks the wrong one.

Teleport positions are level-specific — measure in editor.

## Agent checklist

1. `get_verse_api(name="volume_device")` / `get_verse_api(name="creative_prop")` / `get_verse_api(name="fort_character")` before writing.
2. Write under `Verse/<System>/` — never dump at Verse root (`verse_layout`).
3. `workspace_write_file` → `workspace_list_verse_errors`.
4. Wire `@editable` refs with `wire_verse_device_ref` / `wire_verse_prop_assets` (one call at a time).
