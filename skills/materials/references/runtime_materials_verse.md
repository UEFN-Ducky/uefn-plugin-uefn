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

### Swap an entity's material (Scene Graph — use this first)

Entities have no `SetMaterial`. Each mesh's generated class in
`Assets.digest.verse` has one `@editable var` per material slot, named after the
slot — for example `SM_Card := class<final>(mesh_component)` with
`var MAT_Card : material`. Set that slot on the entity's mesh component; the
materials are classes in the same digest, so build one with `{}`:

```verse
using { /Verse.org/SceneGraph }

PaintBrass(Card : entity) : void =
    if (Mesh := Card.GetComponent[SM_Card]):
        set Mesh.MAT_Card = MAT_Brass{}
```

Slot and material names differ per mesh: read them from the project's Assets
digest (`search_verse_digest` with the Assets `digest_path`) and build once to
confirm. Two looks that never mix can also be two child mesh entities, one shown
(`SetShown`, scenegraph `verse_authoring`).

### Swap a `creative_prop`'s material (physics props only)

```verse
using { /Fortnite.com/Devices }
using { /Verse.org/Assets }        # asset reflection

# Materials appear under the project's Assets digest, e.g. Materials.M_Red
if (Prop := MyPropRef?):
    Prop.SetMaterial(Materials.M_Red)
```

- Works on `creative_prop` (spawned or placed props that allow manipulation).
  Anything else Verse changes at runtime is an entity — use the slot above.
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

### Verse material inheritance

From UEFN generates material **instances as subclasses of their parent
material class** in the Assets digest (MI_Red derives from M_Base). Effects:

- A function taking the parent type accepts every instance: write one
  `SetTint(M:M_Base)` helper instead of one per instance.
- Less runtime memory for islands that use many material properties from Verse
  (counts from the current upload on).
- Check the real class chain in the project's Assets digest after a build
  (`search_verse_digest("M_Base")`) — never assume it.

**Upgrade errors on re-upload (rare):**

| Error | Cause | Fix |
| --- | --- | --- |
| `unknown member` on `Value.(MI_Red)Param` | qualified access, but `Param` moved up to the parent class | drop the qualifier (`Value.Param`) or qualify with the parent: `Value.(M_Base)Param` |
| conflicting / ambiguous extension method | same-name extension methods on a child and its parent material class | identical → delete the child's; different → rename one. Tip: rename all of them to surface every call site, fix children before parents |

Material redirectors now generate Verse aliases too: renaming/moving a material
keeps old references compiling with a deprecation warning (needs **Reflect UE
Redirectors into Verse Manifest** in Project Settings).

### Design pattern

- Pre-build one `M_` parent with parameter nodes + one `MI_` per themed variant.
- Gameplay states → `SetMaterial(MI_StateX)` swaps (cheap, reliable), parameter
  drives only for continuous effects (health tint, charge glow).
- Set up the editor-side assets with the `creating_materials` reference; wire
  device/Verse logic with the uefn pack's tools.
