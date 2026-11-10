---
description: "Mixamo chain table for IK Rigs, Mixamo T-pose to FN A-pose retarget pose, editor retargeter UI path, Sequencer key interpolation and curve editing, Animation section properties (play rate, offsets, loop, ease, weight)"
metadata:
  label: "Mixamo chains + Sequencer key editing"
  default_enabled: false
  load_condition: "Retargeting Mixamo clips onto FN Mannequin / M_Medium_Base, smoothing robotic Control Rig keys, or editing Animation sections (play rate, trim, loop, blend) in Sequencer"
---

## Mixamo → FN Mannequin / M_Medium_Base

`list_skeleton_bones` only guesses `biped` / `mannequin`. A Mixamo skeleton comes back
`unknown`, so pass its chains explicitly to `add_retarget_chains`. Read the real names
first: depending on the importer the namespace stays (`mixamorig:Hips`) or is stripped
(`Hips`). Use whichever `list_skeleton_bones` returns.

| Chain | Start | End |
|-------|-------|-----|
| (root, `set_retarget_root`) | mixamorig:Hips | — |
| Spine | mixamorig:Spine | mixamorig:Spine2 |
| Head | mixamorig:Neck | mixamorig:Head |
| LeftClavicle | mixamorig:LeftShoulder | mixamorig:LeftShoulder |
| RightClavicle | mixamorig:RightShoulder | mixamorig:RightShoulder |
| LeftArm | mixamorig:LeftArm | mixamorig:LeftHand |
| RightArm | mixamorig:RightArm | mixamorig:RightHand |
| LeftLeg | mixamorig:LeftUpLeg | mixamorig:LeftFoot |
| RightLeg | mixamorig:RightUpLeg | mixamorig:RightFoot |

Chain names match the biped/mannequin presets, so `auto_map_retarget_chains` pairs them.

- **Pose mismatch is the main problem.** Mixamo is in a **T-pose**. The FN Mannequin and
  M_Medium_Base are in an **A-pose**. In the retargeter, give the target a retarget pose
  that raises `upperarm_l` / `upperarm_r` about 45° to a T (`create_retarget_pose` +
  `set_retarget_pose_bone_rotation`, see `retargeting` §3b). Re-bake one clip and check
  the hands before you batch the rest.
- Editor UI equivalent: IK Rig per mesh → **Auto Create Retarget Chains** + **Auto
  Create IK**. This works for Mixamo ↔ FN, but not for Biped (see `retargeting`). Then
  in the IK Retargeter: Source = Mixamo rig, Target = FN rig → **Edit Retarget Pose** →
  Asset Browser → select clips → **Export Selected Animations**.
- Mixamo download: **FBX**, **With Skin**, **60 FPS**, **In Place**. For the first clip,
  use **Import All**. Import every later clip onto that same Mixamo skeleton, not a new one.

## Sequencer key editing (Control Rig and Transform tracks)

- **Interpolation:** select keys, then right-click (or use the key toolbar) → **Auto /
  User / Break** (cubic, smooth), **Linear**, or **Constant** (stepped). Freshly keyed
  rig poses can look robotic. Select them all and set **Auto** (orange keys = cubic).
  Headless: `add_transform_keys` takes `interp` `auto | linear | constant`.
- **Blocking → spline:** block the poses with Constant first, then switch to Auto when
  the timing reads right.
- **Curve Editor** (track context menu or toolbar) shows tangents. Flatten the first and
  last keys of a loop so velocity matches across the seam.
- Holding a pose: copy the key (Ctrl+C), move the playhead, paste (Ctrl+V).
- Removing a limb from an imported clip: after **Bake to Control Rig** (Reduce Keys on),
  select that control's keys and delete them. The limb falls back to the rig's rest pose.

## Animation section properties (right-click a clip → Properties)

| Property | Use |
|----------|-----|
| Play Rate | Speed up or slow down the clip inside the sequence |
| Start / End Offset | Trim the clip without re-baking |
| Loop (drag the section edge past the clip length) | Repeat a cycle, e.g. a run under a long Transform move |
| Ease In / Ease Out (top-corner triangles) | Crossfade overlapping clips on one track |
| Weight (keyable) | Fade a layered clip in or out |
| When Finished → Keep State | The actor holds its last pose after the sequence ends |

Run → jump → run: put the three clips on **one** Animation track, overlap them a few
frames, and drag the ease triangles. Add a Transform track keyed at takeoff and landing.
Use In Place clips, or the root motion and the Transform track will fight.
