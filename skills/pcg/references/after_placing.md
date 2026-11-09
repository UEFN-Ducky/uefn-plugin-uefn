---
description: "After using UEFN PCG Mode: editing a placed PCG tool actor, Generate / Cleanup / Clear PCG Link, editing the spline, spawning Fortnite Blueprint props with Spawn Actors + Replace Selected Actors, and Shift+F2 mass rename"
metadata:
  order: 4
  label: "After placing"
  default_enabled: false
  load_condition: "Editing or regenerating a placed PCG tool actor, moving its spline, spawning Blueprint props or trees with PCG, or renaming generated actors"
---

## Edit a placed tool

Select the `PCG <Tool> Actor` in the Outliner → click **PCGToolComponent** in Details. Every setting from the
tool is there and applies live. **Generate** rebuilds, **Cleanup** removes what it made.

## Edit the spline

1. Switch to **Selection Mode** (PCG Mode hides the gizmo).
2. Select the actor, then a spline point, and move it.
3. Right-click the spline for **Duplicate Spline Point** and the other spline tools.

## Place Fortnite Blueprint props

The tools **can't spawn Blueprint props from the Fortnite folder** directly. Workaround:

1. Tool → Spawning: untick Static Meshes, tick **Spawn Actors**, add **Actor Classes** → plain `Actor`.
2. Set random offset, rotation and scale **before** generating. Then Accept. The placeholders land in the folder
   `PCG <Tool> Actor_Generated`.
3. Drag the wanted prop into the level once.
4. Select that prop in the Content Browser, select all the placeholders in the Outliner → right-click →
   **Replace Selected Actors with** the prop. Transforms carry over.
5. Delete the one you dragged in.

**Limits:** replaced actors are no longer linked to the tool. **Cleanup won't remove them**, and each regenerate
makes new placeholders, so delete the old ones and replace again. Fortnite Creative placement rules still apply
to anything you replace with.

## Keep track of generated actors

They are all called `Actor`. Select them → **Shift+F2** → type a name, add auto increment. A distinct name
like `ReplaceTree` makes the next replace pass easy to find.
