---
description: "Do every animation step yourself: which steps have an MCP tool (Ducky or Epic), and the exact UEFN menu path to click when one doesn't — Sequencer tracks, Layered Control Rig, Import Sequence, Bake, Retarget Animations dialog, IK Retargeter pose and export, Property Matrix, Player Reference and Cinematic device options — plus the capture → hover → click → capture loop"
metadata:
  label: "Animation steps: tool or click (UEFN UI map)"
  default_enabled: false
  load_condition: "An animation step has no tool or its tool returned available:false, you need the exact UEFN menu path for an animation action, or you are about to ask the person to click something in Sequencer, Control Rig, IK Retargeter, Property Matrix or the Content Drawer"
---

# Animation steps: tool or click

Never hand an animation step to the person. Use the tool if there is one; if it reports
`available: false` or no tool exists, click it yourself with the loop at the end.

## Step → tool → UI path

| Step | Tool first | UI path when there is no tool |
|------|-----------|-------------------------------|
| Probe what this build allows | `anim_author_capabilities`, `ik_retarget_capabilities` | — |
| Import FBX (Mixamo) | `import_asset` | Content Drawer → **Import** → Skeleton **None** (first) / existing → **Use T0 As Reference Pose** → **Import All** |
| Quick retarget, no IK rigs of your own | `retarget_animation_pipeline` | Right-click clip → **Retarget Animations** → Source mesh (Mixamo) → Target mesh **M_Medium_Base** / **F_Medium_Base** / FN_Mannequin → Export |
| Retarget with control | `create_ik_rig_asset` … `retarget_animation` (`retargeting`) | Right-click → **Animation → Retargeting → IK Rig** / **IK Retargeter**; in the rig **Auto Create Retarget Chains** + **Auto Create IK**; retargeter → **Edit Retarget Pose** → Asset Browser → **Export Selected Animations** |
| Fix A/T pose | `create_retarget_pose` + `set_retarget_pose_bone_rotation` | Retargeter → **Running Retarget** toggle → **Edit Retarget Pose** → rotate upperarm_l/r; Target Mesh Scale |
| New Level Sequence + bind | `create_level_sequence`, `add_sequence_binding` | Content Drawer → right-click → **Cinematics → Level Sequence** → open → **+ Track → Actor To Sequencer** |
| Animation clip on a track | — (Epic `SequencerControlRigTools.load_anim_into_rig` loads into a rig) | Actor row **+** → **Animation** → pick clip |
| Transform keys | `add_transform_keys` | Actor row **+** → **Transform**, key with Enter |
| Control Rig track | Epic `SequencerControlRigTools.find_or_create_track` | Actor row **+** → **Control Rig** → **Filter by Asset Skeleton** off (shows Fortnite rigs) → **Layered** on for additive → Body Rig / FX Control Rig |
| Key controls | Epic `get_controls_info`, `set_transform`, `key_controls_at_frames` | Animation Mode, **G** off, select control, move, **Enter** |
| Clip into a rig (edit it) | Epic `load_anim_into_rig` / `bake_to_control_rig` | Rig track right-click → **Import Sequence** or mesh track → **Bake to Control Rig** → **Reduce Keys** on |
| Additive section on a rig | — | Rig track **+** → **Additive** |
| Bake to AnimSequence | `bake_sequence_to_anim` / Epic `export_anim_sequence` | Mesh track right-click → **Bake Animation Sequence** → name → **Export To Animation Sequence** |
| Additive Local Space | `set_anim_additive_type` | Right-click clip → **Asset Actions → Edit Selection in Property Matrix** → **Additive Anim Type → Local Space** → Save |
| Hand-keyed clip | `create_anim_sequence`, `set_anim_bone_keys` | — |
| Animated Mesh device | `configure_animated_mesh` | Details → Skeletal Mesh, Animation, Loop, Play Rate |
| Player Reference / Cinematic device options | Epic `DeviceToolset.SetDeviceProperty` (`ListClassicDeviceOptions` / `SetClassicDeviceOption`) | Details: Hologram Strength 0, Show Base off; Sequence, Loop Playback, Visibility |
| Camera Cut **Can Blend** | none (UI only, `sequencer_cinematics`) | Right-click **Camera Cuts** track → **Can Blend** |
| Verse sees a new clip | `workspace_compile_verse` (Assets digest refresh) | — |

`unreal__describe_toolset` before the first Epic call each session for argument names, and
look for a `layered` / `additive` argument on `find_or_create_track` before clicking.

## The click loop (UEFN must be open, person told first)

Recipe and helper: `skill_read_subskill("pcg", "agent_driving")` — the same PowerShell
hover-then-click helper drives Sequencer and the Content Drawer.

1. `uefn_window_list` (empty `rect` = minimized; restore it) → `uefn_window_capture`.
2. Read the target's pixel from the capture. **Hover first, then click**: a plain
   `uefn_window_click` on a menu item closes the menu, picks nothing, and still says `ok`.
3. Move the pointer away, capture again, confirm the change. One UI change, one capture.
4. Text fields and search boxes: click, then type with the helper; `uefn_window_key` sends
   single keys only (Enter to key a control, G for game view).
5. Popups (Save, Export, Bake dialogs): `uefn_popups` → `uefn_popup_press(hwnd, n)`.
6. Finish with a tool read-back: `get_sequence_info`, `get_anim_sequence_info`,
   `get_ik_rig_info`. A capture that looks right is not proof.

Sequencer layout hints: tracks on the left (the **+** sits on each row's right edge), keys on
the timeline; right-click menus open at the pointer. Wait about 1 s after expanding a row and
2–3 s after opening a dialog or asset picker.
