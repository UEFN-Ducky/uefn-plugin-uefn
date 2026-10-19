---
description: "MetaHuman Animator, Live Link Face, audio-driven face; Fortnite Character Device"
metadata:
  label: "MetaHuman face animation"
  default_enabled: false
  load_condition: "Capturing or applying facial animation to MetaHumans or Fortnite characters in UEFN"
---

# Face animation — Animator, Live Link, audio

Body locomotion is retargeting (`animation` skill). **Face** uses MetaHuman
Facial Description Standard (MHFDS) control / solve paths.

## Options

| Path | Hardware / input | Quality | Notes |
|------|------------------|---------|--------|
| **Live Link Face** | iPhone TrueDepth / Android Live Link Face | Good live | Real-time preview; Wi‑Fi to editor |
| **MetaHuman Animator** | Depth take (iPhone / stereo HMC / etc.) | Best offline | Needs Identity + Performance asset |
| **Audio-driven** | Sound file | Mid | Lip sync strong; emotion overrides on newer MH |
| **Face Control Rig** | Hand keys | Polish | ~200 named controls; portable across MH |

MetaHuman Animator in UEFN also works with **Fortnite characters** and the
**Character Device** — useful when the island hero is a FN cosmetic, not a MH NPC.

## Animator outline

1. Enable MetaHuman Animator (+ Depth Processing for depth solves).
2. Capture or import footage; establish **Neutral Pose** / Identity if needed
   (can reuse Mesh-to-MH Identity).
3. Create a **MetaHuman Performance** (or equivalent Performance asset on your
   build); process the take offline.
4. Apply the resulting animation through the face Control Rig channels the
   assembled MetaHuman exposes, then **bake it to an AnimSequence**
   (`bake_sequence_to_anim`, or right-click the track → Bake Animation Sequence).
   Baked clips are what ships; AnimBP editing is not the UEFN path.
5. For cinematics: Sequencer + assembled MH. For gameplay NPCs: prefer short
   **baked** face loops (or audio) — continuous Live Link is editor/previs, not
   the island default.

## Agent rules

- Face capture UI and Live Link Hub setup are **user/editor** steps — document
  and verify assets with `search_assets` / `get_asset_info`.
- Do not claim depth solve succeeded without a Performance result asset on disk.
- Body clips that look wrong after retarget are a **retarget pose** problem, not a
  skeleton-surgery problem: use Common `RTG_metahuman` / `IK_MetaHuman` when
  present, then `create_retarget_pose` + `set_retarget_pose_bone_rotation`. Never
  copy bones between skeletons.

## Cross-links

- Body clips: `skill_read_subskill("animation", "retargeting")`
- Sequencer props: `skill_read_subskill("animation", "sequencer_cinematics")`
