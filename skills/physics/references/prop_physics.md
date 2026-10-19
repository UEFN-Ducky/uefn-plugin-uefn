---
description: "FortPhysics on props — Simulate, mass, gravity, Start Awake, damping, impulse multiplier, constraints, collision"
metadata:
  order: 10
  label: "Prop physics"
  default_enabled: false
  load_condition: "Adding Fort Physics, tuning mass/damping/impulse, Start Awake, or rotation/translation constraints"
---

# Prop physics (Fort Physics)

All Fortnite props in a physics-enabled project can simulate. Prefer **simple collision**
(sphere/box) for performance.

## Two ways to add

1. **Fortnite Tools** — toolbar Selection Mode → Fortnite Tools → select props → **Add Physics**.
   Also: Remove Physics, Select all physics / non-physics props.
2. **Component** — prop Details → + Add → **Fort Physics** → check **Simulate Physics**.

Custom mesh import: open static mesh → ensure Simple Collision (e.g. Add Sphere Simplified
Collision) → Collision Preset Block All → Convert to Prop → add Fort Physics.

## User options

| Option | Effect |
|--------|--------|
| **Mass** | Heavier → less response to the same force. Override Mass when you need an exact kg value. |
| **Enable Gravity** | Apply gravity when simulating. |
| **Start Awake** | If unchecked, prop sleeps until a force hits it (crates that fall only when struck). |
| **Linear Damping** | Slows translation over time (balloons: higher = float less freely). |
| **Angular Damping** | Slows rotation over time. |
| **Impulse on Hit Multiplier** | Scales hit impulse; range about −5..5 (default 1). Soccer ball often ~3. |

## Constraints

Add **Rotation** and **Translation** constraints on the Fort Physics component to lock
axes (e.g. keep a plank from tipping unwanted ways). See Unreal Physical Constraint
Reference for axis meaning.

## Recipe presets

**Soccer ball (light, punchy):**

- Simulate Physics: true
- Override Mass: true, Mass: 20
- Linear Damping: 0.1
- Angular Damping: 0.3
- Impulse On Hit Multiplier: 3.0

**Heavy puzzle cube:**

- Simulate Physics: true
- Override Mass: true, Mass: 75
- Enable Gravity: true
- Start Awake: true

**Bridge plank (heavy, damped):**

- Mass: 500
- Linear Damping: 0.5
- Angular Damping: 0.5

## Agent notes

- Editor-placed physics props are unique instances — they do not auto-reset when
  dropped unless the round restarts or Verse teleports them.
- After component edits: save the level (`save_current_level`).
