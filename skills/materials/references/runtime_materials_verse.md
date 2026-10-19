---
description: "Swapping materials and driving parameters at runtime from Verse (SetMaterial, asset reflection)"
metadata:
  order: 3
  label: "Runtime materials (Verse)"
  default_enabled: false
  load_condition: "User wants materials to change during gameplay (Verse/runtime)"
---

## Runtime materials from Verse

Verse cannot create materials. Everything visible at runtime must exist as an
editor asset first; Verse swaps between pre-made materials/instances.

### Swap a prop's material

```verse
using { /Fortnite.com/Devices }
using { /Verse.org/Assets }        # asset reflection

# Materials appear under the project's Assets digest, e.g. Materials.M_Red
if (Prop := MyPropRef?):
    Prop.SetMaterial(Materials.M_Red)
```

- Works on `creative_prop` (spawned or placed props that allow manipulation).
- The material asset is referenced through **asset reflection** — it shows up in
  the `Assets.digest.verse` after building Verse code; no @editable needed, but an
  `@editable` material field also works for designer-facing setups.

### Parameters at runtime

Texture, Scalar, and Vector (Vec4/color) parameters on a **material instance**
can be changed from Verse and apply live to any prop the instance is set on —
create ONE instance asset, `SetMaterial` it once, then set parameters on it.

Known issue: creators reported instanced-material parameter setting breaking
after Fortnite v33.00 — if parameters stop applying, retest with a plain material
swap to isolate, and check the Epic forums thread "Setting Materials with
parameters from verse Not working after v33.00".

### Design pattern

- Pre-build one `M_` parent with parameter nodes + one `MI_` per themed variant.
- Gameplay states → `SetMaterial(MI_StateX)` swaps (cheap, reliable), parameter
  drives only for continuous effects (health tint, charge glow).
- Set up the editor-side assets with the `creating_materials` reference; wire
  device/Verse logic with the uefn pack's tools.
