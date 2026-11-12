---
description: "Perception — /Verse.org/Perception: entities that see, hear and feel touch. Emitter on what can be sensed, detector on what senses it: sight (sight_emitter_component, sight_detector_component with HalfAngle / Range / hysteresis / NearClipRadius, Clarity), hearing (hearing_emitter_component passive loudness or one-shot Emit, hearing_detector_component, sound tags), touch (touch_emitter_component, touch_detector_component, collision hit), filtered Subscribe that sends events down to an entity, reading them in OnReceive, a compiled guard-eyes component, and writing your own sense with spatial_sense_emitter / spatial_sense_detector"
metadata:
  order: 15
  label: "Perception (sight, hearing, touch)"
  default_enabled: false
  load_condition: "Guards or NPCs that spot players, line of sight, vision cones, stealth, detection, hearing sounds or footsteps, noise, alerting enemies, touch or contact sensing on entities, perception, sight_detector_component, hearing_detector_component, touch_detector_component, sense_detection_event"
---

## Perception — what an entity sees, hears and touches

Each sense is a pair: an **emitter** component on the thing that can be sensed and a
**detector** component on the thing that senses. Use it for guards spotting intruders,
creatures reacting to noise, objects reacting to contact. Never poll distances or run
raycasts in a loop for this.

> Read the API from the digest before you write: `get_verse_api("sight_detector_component")`,
> `search_verse_digest("Perception")`. An `@experimental` line above a name in the digest
> means islands that use it cannot be published yet; if that line is gone, they can.

```verse
using { /Verse.org/Perception }
using { /Verse.org/SceneGraph }
using { /Verse.org/Simulation }
```

### The pairs

| Sense | On what is sensed | On what senses | Data |
|-------|-------------------|----------------|------|
| Sight | `sight_emitter_component` (`VisibilityPoints`, `PassiveEmissionEnabled`) | `sight_detector_component`: `HalfAngle` (radians, up to pi/2), `Range` (cm), `HysteresisAngle`, `HysteresisRange`, `NearClipRadius` | `sight_data`: `Clarity` 0.0 to 1.0, `Position`, `DetectorPosition` |
| Hearing | `hearing_emitter_component`: `PassiveEmissionEnabled`, `PassiveEmissionLoudness` (decibels), `PassiveEmissionSoundTags`; `Emit(hearing_data{...})` for a one-shot sound | `hearing_detector_component` | `hearing_data`: `Loudness`, `Position`, `SoundTags` |
| Touch | `touch_emitter_component` | `touch_detector_component` (`Meshes`, `AddMeshComponents`, `RemoveMeshComponents`) | `touch_data`: `Hit` (the collision hit) |

- The sight cone points along the detector entity's **Forward** axis.
- Hysteresis is the extra angle or distance a target keeps being seen after it was spotted, so detection does not flicker at the edge.
- Touch looks **up** the hierarchy from the entity that was hit for the nearest `touch_emitter_component`; with none in the ancestry no event fires. Check the digest comment on `touch_detector_component` for what it cannot detect yet.
- Add a `mesh_component` to an emitter or detector entity to sense by volume instead of by a point.

### Events

`Detector.Subscribe(Receiver, Filter)` returns a `cancelable`. Every detection that passes
`Filter` is **sent down** to `Receiver`, where a component reads it in `OnReceive`.

| Event | Fields |
|-------|--------|
| `sight_detection_event` | `DetectedEntity`, `DetectionState`, `Emitter`, `Detector`, `SightData` |
| `hearing_detection_event` | the same, with `HearingData` |
| `touch_detection_event` | the same, with `TouchData` |

`DetectionState` is `sense_detection_state`: `Active` (started), `Inactive` (ended),
`Instant` (a one-shot, such as an emitted sound). The enum is open, so a `case` needs `_ =>`.
For values that follow an ongoing detection call `Detector.GetCurrentSightData[Emitter]`
(or `GetCurrentHearingData`, `GetCurrentTouchData`); they fail when the detection is over.

### A guard that sees (compiled)

Put this on the guard entity next to a `sight_detector_component`. Whatever should be seen
(a player's character entity, a prop) needs a `sight_emitter_component`.

```verse
guard_eyes_component := class<final_super>(component):

    var SightSub : ?cancelable = false

    OnBeginSimulation<override>() : void =
        (super:)OnBeginSimulation()
        if (Eyes := Entity.GetComponent[sight_detector_component]):
            set SightSub = option{Eyes.Subscribe(Entity, ClearEnough)}

    OnEndSimulation<override>() : void =
        if (Sub := SightSub?):
            Sub.Cancel()
        (super:)OnEndSimulation()

    # Filter: only detections this guard cares about reach OnReceive.
    ClearEnough(Seen : sight_detection_event)<decides><reads> : void =
        Seen.SightData.Clarity >= 0.5

    OnReceive<override>(SceneEvent : scene_event) : logic =
        if (Seen := sight_detection_event[SceneEvent]):
            case (Seen.DetectionState):
                sense_detection_state.Active => OnSpotted(Seen.DetectedEntity)
                sense_detection_state.Inactive => OnLost(Seen.DetectedEntity)
                _ => {}
            true
        else:
            false

    OnSpotted(Target : entity) : void =
        Print("guard sees a target")

    OnLost(Target : entity) : void =
        Print("guard lost the target")
```

### A one-shot sound others can hear

```verse
MakeNoise(Source : entity, Decibels : float) : void =
    if (Voice := Source.GetComponent[hearing_emitter_component]):
        Voice.Emit(hearing_data{Loudness := Decibels})      # reaches detectors as Instant
```

### Your own sense

Implement `spatial_sense_emitter` on a component for what is sensed and
`spatial_sense_detector` (with its `EmitterType`) on a component for what senses; call
`RegisterEmitter[]` / `RegisterDetector[]` and handle `OnSpatialChange(Emitter, State)`.

### Rules

- The filter is `<decides><reads>`: it only reads the event and succeeds or fails. No side effects in it.
- Keep the `cancelable` from `Subscribe` and cancel it when the owner leaves (`OnEndSimulation`).
- Memory of what was seen, combining senses and forgetting over time are yours to build on top of these events (a component with a small state machine).
- NPC behaviour stays in the `npc-ai` skill; perception only tells it what was sensed.
