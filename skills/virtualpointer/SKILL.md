---
name: virtualpointer
description: "UEFN Virtual Pointer — cross-platform pointer input via Verse Enhanced Input: TouchMapping, PointerSelect (publishable), PointerZoom (Experimental, not publishable), swipes, taps, pinch zoom/scale, screen-space deproject and world traces. Use when the user mentions virtual pointer, touch mapping, PointerSelect, PointerZoom, pinch, swipe, tap-to-select, or cross-platform on-screen pointer."
license: MIT
metadata:
  label: UEFN Virtual Pointer
  version: 7
  author: UEFN-Ducky
  copyright: Copyright 2026 Mindful Path Company, LLC
  allow_redistribute: true
  managed_by: uefn-ducky
---

# UEFN Virtual Pointer

> **Snippets here are fragments.** The `using` block in this file's first code
> block applies to all of them — copy those imports (or start from the matching
> `verse_template_apply` pack) when pasting into a real `.verse` file.

Add cross-platform pointer input to a UEFN island using Verse Enhanced Input, with custom input mappings, actions, and gestures.

## Publish status (say this first)

| Feature | Status | Publishable |
|---------|--------|-------------|
| `TouchMapping` + `PointerSelect` (tap / click / select, swipes, traces) | Released (FN ≥ 4100) | **Yes** |
| `PointerZoom` (pinch / scroll / right-stick zoom) | **Experimental** (FN ≥ 4120) | **No** — remove before publishing |

Experimental means no backward-compatibility guarantee; the API may change or be removed.

## What it is

The Virtual Pointer lets players point at and interact with on-screen elements on every supported input device. UEFN reads it as a normal pointer, so one gesture path covers console, PC, and mobile.

| Device | Pointer | Pinch / zoom (`PointerZoom`) |
|--------|---------|------------------------------|
| Touch | Finger contact | Two-finger pinch; value = pinch speed, `0` = no change; centered between fingers |
| Mouse + keyboard | Existing mouse pointer | Scroll wheel `-1`…`1` by direction (freewheel behaves like a stick); centered on pointer |
| Controller | On-screen pointer driven by the **left stick** | Right stick Up = zoom in, Down = zoom out, deflection `-1`…`1`; centered on pointer |

Hard facts:
- **Players are put in stasis** (player and camera movement disabled) when entering Virtual Pointer mode. Release with `Player.GetFortCharacter[].ReleaseFromStasis()` (`/Fortnite.com/Characters`) if they must move while the mapping stays on.
- Virtual Pointer **does not work while Fortnite game menus are open**.
- You must `AddInputMapping(TouchMapping)` on each player; no mapping → no events.
- `Abs` is a compiler intrinsic that the digest does not list; it compiles. The swipe template uses a local `AbsF` helper so it stays digest-searchable, either works.
- The world-trace needs `using { /Verse.org/SceneGraph }` for `collision_point` / `FindSweepHits` — Epic's trace sample omits it and fails to compile.
- Templates below were compiled in UEFN (swipe + trace: 0 errors; pinch: only the expected "PointerZoom is experimental" warning 2304).

## Digest facts (verified — never invent names)

| Symbol | Module | Signature / notes |
|--------|--------|-------------------|
| `TouchMapping` | `/Verse.org/Input/UI` | `input_mapping`, FN ≥ 4100 |
| `PointerSelect` | `/Verse.org/Input/UI` | `input_action(vector3)`, FN ≥ 4100 |
| `PointerZoom` | `/Verse.org/Input/UI` | `input_action(vector3)`, FN ≥ 4120, `@experimental` |
| `GetPlayerInput[Player]` | `/Verse.org/Input` | `player` → `player_input` (failable) |
| `AddInputMapping` / `RemoveInputMapping` | `player_input` | Enter / exit Virtual Pointer mode |
| `GetInputEvents(Action)` | `player_input` | → `input_events(t)` |
| `Player.DeprojectViewportToWorld(vector3)` | `/Verse.org/Input` | `<reads>` → `deproject_results{Origin, Direction}` |
| `Entity.FindSweepHits(Displacement, StartTransform, Volume)` | `/Verse.org/SceneGraph` | `generator(sweep_hit)`; use `collision_point{}` for a ray |
| `GetSimulationEntity[]` | on `creative_device` / `entity` | Rootmost scene entity for sweep context |
| `ReleaseFromStasis()` | `fort_character` | Undo the VP-mode stasis |
| `Exp`, `Min`, `Max`, `Abs` (float) | Verse core | Present (`Abs` is unlisted in the digest but compiles) |

### Event payloads (`input_events(t)`, `t = vector3` for pointer actions)

| Event | Payload | Use |
|-------|---------|-----|
| `BeginDetectEvent` | `tuple(player, vector3)` | Pointer down / gesture start |
| `DetectionOngoingEvent` | `tuple(player, vector3, float)` | Held, not yet triggered; `float` = elapsed s |
| `TriggerActivationEvent` | `tuple(player, vector3)` | Fired; repeats while held (use for pointer move) |
| `CancelActivationEvent` | `tuple(player, vector3, float)` | Canceled before activation |
| `EndDetectEvent` | `tuple(player, float)` | Pointer up; `float` = elapsed s. **No position** — cache it from earlier phases |

Handler signatures must match exactly (e.g. `OnPointerUp(Arg : tuple(player, float))`).

### Screen coordinates

`vector3` from pointer events / into `DeprojectViewportToWorld` is in **centimeters**: `Left` positive rightward from the top-left corner, `Up` positive upward (negative below the top edge). `Forward` is ignored. `deproject_results.Origin` is the **camera eye**, not the near plane — filter the player pawn or advance the start along `Direction` if you hit things behind the near clip.

## Golden path

```
1. State publish status: PointerSelect/TouchMapping OK, PointerZoom Experimental (no publish)
2. Prefer a template: verse_template_apply("vp_screenspace_trace" | "vp_swipe_detector" | "vp_pinch_scale" | "virtualpointer")
   → writes Verse/VirtualPointer/<device>.verse (never at Verse root)
3. Per player (join + existing): GetPlayerInput[Player] → AddInputMapping(TouchMapping)
4. Subscribe PointerSelect and/or PointerZoom via GetInputEvents; keep every cancelable per player
5. Select → screen vector3 (Left/Up) → DeprojectViewportToWorld → GetSimulationEntity[].FindSweepHits
6. Exit: cancel subscriptions, RemoveInputMapping(TouchMapping) (also in OnEnd)
7. workspace_list_verse_errors → place device → wire @editable refs
```

## Enable

```verse
using { /Verse.org/Input }
using { /Verse.org/Input/UI }
using { /Verse.org/Simulation }

AddTouchMapping(Player : player):void =
    if (PlayerInput := GetPlayerInput[Player]):
        PlayerInput.AddInputMapping(TouchMapping)
```

Gamepad players see the pointer once `TouchMapping` is added. Players are immobilized (stasis) in this mode.

## Disable

Unsubscribing from `PointerSelect` stops screen-space coordinates. Removing `TouchMapping` exits Virtual Pointer mode. You do **not** need to unsubscribe before removing the mapping.

```verse
RemoveTouchInput(Player : player):void =
    if (PlayerInput := GetPlayerInput[Player]):
        PlayerInput.RemoveInputMapping(TouchMapping)
```

## Templates (New file → Verse, or `verse_template_apply`)

| id | File | What |
|----|------|------|
| `vp_screenspace_trace` | `screenspace_trace_device.verse` | Tap/click → deproject → sweep, prints hit. Publishable. |
| `vp_swipe_detector` | `swipe_detector_device.verse` | Per-player swipe/tap classifier (Up/Down/Left/Right). Publishable. |
| `vp_pinch_scale` | `pinch_scale_device.verse` | PointerZoom pinch → scale a Scene Graph entity. Experimental. |
| `virtualpointer` | all three → `Verse/VirtualPointer/` | Whole pack. |

All templates subscribe existing players + `PlayerAddedEvent`, keep cancelables per player, and clean up in `OnEnd`.

## Testing on mobile (v42.10)

- **Mobile Preview** (UEFN toolbar) now lets you pick a specific iOS/Android device; the preview adds rounded corners, camera cutouts and the correct safe zones, so pointer UI can be checked against real screen bounds.
- **UE Remote** (iOS/Android app) replays touch input from a real phone into the editor session — the only way to test native pinch/swipe recognition before publishing.
- v42.10 also added (digest-verified, `/Fortnite.com/Input/Character`, all Experimental): `Move : input_action(vector3)` on `TraversalMapping`, and `InteractMapping` with `Interact : input_action(logic)`. They are separate from `TouchMapping` and subscribe the same way (`GetInputEvents(Move).TriggerActivationEvent` payload `tuple(player, vector3)`). Details: verse skill `sys_input_devices`.

## Reference files

- `references/enable_disable.md` — Enter/exit VP mode, stasis + `ReleaseFromStasis`, menu caveat
  Load when: Turning Virtual Pointer on/off for a player, or players must move while it is on
- `references/pointer_select.md` — PointerSelect subscribe, event payload table, screen coords
  Load when: Click / tap / select with the virtual pointer
- `references/screenspace_trace.md` — Deproject + FindSweepHits world pick, Origin caveat
  Load when: Hitting world objects / Scene Graph entities from the pointer
- `references/swipe.md` — Full swipe/tap detector (Begin → Trigger → End), direction classification
  Load when: Detecting swipe / flick / drag gestures
- `references/pinch_zoom.md` — PointerZoom device value table, zoom subscribe, pinch-to-scale device
  Load when: Zoom camera or resize props/entities with pinch (Experimental)
- `references/example_trace_device.md` — Full `screenspace_trace_device` sample
  Load when: Scaffolding a complete creative_device for VP picking
- `references/touch_layout_override.md` — Developer touchscreen layouts: UMG Canvas + Touch Control Layout Override (`DeveloperLayoutButtonProxy`) on a HUD Controller, Apply Canvas Transform (42.40), hiding default buttons from Verse
  Load when: Moving, re-icons, recoloring or hiding Fortnite's default touch buttons (Jump, Shoot, Sprint …), HUD Controller touch layout, or mobile buttons the island doesn't use

## Verify

`workspace_compile_verse` then `get_verse_editables` on the pointer device.

## 42.40 mobile fixes

HUD Controller touch layouts: Jetpack Jump/Sprint → Up/Boost, Shoot with an empty override widget, Carry/Drop overridable, overridden Sprint/Shoot/Reload/Crouch let touches pass through; new **Apply Canvas Transform** for icon-only overrides — `touch_layout_override`.

## 42.30 mobile fixes

- Interact and pick-up button icons can be overridden again.
- Shoot/fire button visibility no longer depends on holding Aim.
- Mobile players can no longer move while all their input is consumed.
