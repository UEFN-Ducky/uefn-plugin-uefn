---
description: "Map of every way something animates in UEFN (skeletal clips, player, NPCs, cinematics, props, Scene Graph, materials, morphs, faces, UI, physics), what plays it, whether it publishes, and which skill page covers it"
metadata:
  label: "Every UEFN animation system (map)"
  default_enabled: false
  load_condition: "Choosing how to make something move in UEFN, or the request names an animation system you have not used yet"
---

# Every animation system in UEFN

Start by asking what moves. Then use the row's player and skill page.

| What moves | Authored with | Played in game by | Publishes | Skill page |
|------------|---------------|-------------------|-----------|------------|
| Skeletal mesh prop / statue | Control Rig bake, FBX/Mixamo, bone keys | **Animated Mesh device** | Yes | `animation` `runtime_playback` |
| Player body (dance, cutscene beat) | Same clips on the player skeleton | Verse `GetPlayAnimationController` | Yes | `animation` `player_animation` |
| Player overlay (wave, giant/tiny) | Layered Control Rig → Additive Local Space | Verse `GetPlayAnimationController` | Yes | `animation` `player_animation` |
| NPC locomotion / attacks | Clips on one skeleton | AnimPreset + NPCCharacterDefinition + `npc_behavior` | Yes | `animation` `npc_characters`, `npc-ai` |
| Cutscene, camera, choreography, FX bursts, sound cues | Level Sequence (transform, animation, Niagara, audio, camera cut tracks) | **Cinematic Sequence device** | Yes | `animation` `sequencer_cinematics` |
| Clips from another skeleton | IK Rig + IK Retargeter (Biped, Mannequin, Mixamo presets) | — | — | `animation` `retargeting`, `mixamo_sequencer_editing` |
| Moving Scene Graph entity (door, lift, platform, spin, bob, pet) | `keyframed_movement_component` | Verse | Yes | `scenegraph` `movement_transforms` |
| Creative prop transform | `animation_controller` keyframe deltas | Verse | Yes | `animation` `anim_authoring` Route 4 |
| Skeletal clip on a Scene Graph entity | `PlaySkeletalAnimation` | Verse | **No** (experimental) | `animation` `runtime_playback` |
| Surface motion (scroll, pulse, wave, wind sway) | Material graph (Time, Panner, World Position Offset) | Always on | Yes | `materials` `creating_materials` |
| Particles, trails, bursts | Niagara | VFX Spawner device / sequence track | Yes | `vfx`, `vfx-fx` |
| Shape keys / morph targets | Blender shape keys → FBX with morphs | Baked into clips (curves) | Yes | `rigging` `bpy-shape-keys`, `modeling` `fbx_import_pipeline` |
| Faces (MetaHuman) | MetaHuman Animator, Live Link Face, audio-driven | Sequence / character device | Yes | `metahuman` `animator_face` |
| UI widgets | UMG widget animation tracks | Verse / widget events | Yes | tools `create_widget_animation`, `add_animation_keys`, `bind_widget_animation` |
| Physics-driven props | Physics on Fortnite props | Simulation | Yes | `physics` |
| Clips made in Blender | Blender actions → FBX | Any player above | Yes | `blender-animation`, `blender` `skeletal_export` |

## Not available in UEFN

Animation Blueprints, Montages, anim notifies and Animation Modifiers are full Unreal
features. Build the motion as a baked clip, chain clips from Verse (`Await` one `Play`,
then start the next), and put timed effects on Sequencer tracks instead of notifies.
