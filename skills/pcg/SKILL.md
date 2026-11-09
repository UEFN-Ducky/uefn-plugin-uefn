---
source_plugin_id: uefn
name: pcg
description: "PCG Editor Tools in UEFN 43.00 (PCG Mode, Shift+7): where every button is and what every setting does — Spacing, Spline Mesh, Area, Place, Scatter and Volume tools, regenerate/cleanup, spawning Fortnite Blueprint props, and how an agent clicks through them or walks the person through them"
license: MIT
metadata:
  label: UEFN PCG Editor Tools
  version: 3
  managed_by: uefn-ducky
  author: UEFN-Ducky
  copyright: Copyright 2026 Mindful Path Company, LLC
  allow_redistribute: true
---

# UEFN PCG Editor Tools

PCG Mode is Epic's set of ready-made placement tools, new in UEFN 43.00. You draw a spline, paint or
drag a volume in the viewport and PCG places meshes or actors. No graph authoring needed.

## Which route

| The job | Route |
|---|---|
| Person wants to draw or paint by hand; roads, fences, rock lines, tree clusters | **PCG Mode** (this skill) |
| Agent builds with the real mouse | `agent_driving` + `build_recipes` |
| Show the person where a button is | `ducky_ui_show` → `agent_driving` |
| Agent must place by exact numbers, no viewport drawing | PCG graphs → `skill_read_subskill("leveldesign", "procedural_generation", section="Route A: PCG graphs (UEFN 43.00+)")` |
| Custom logic (process after raycast, custom nodes) | PCG graphs (same page). The prebuilt tools can't reorder their steps |

## The model

Every tool is the same pipeline: **sampling** (how many points, where) → optional **processing**
(transforms, filters, raycast) → **spawning** (what goes on each point). When a result looks wrong, find
which stage owns it.

## Sub-skills

| Sub-skill | Load when |
|---|---|
| `agent_driving` | **Read first to build by mouse:** the tested click, type and drag helper, why plain clicks fail on menus and teleported drags draw nothing |
| `build_recipes` | Run-and-checked steps for roads with width classes, posts and fences, rock lines, filled areas, hand placing, scatter strokes, volume fills |
| `ui_map` | The location of a menu, tab, tool button, section or Accept/Cancel |
| `spline_tools` | Spacing, Spline Mesh, Area; spline draw modes, raycast rules, draw target |
| `paint_volume_tools` | Place, Scatter, Layered Place; Volume Scatter, Biome Volume |
| `after_placing` | Regenerate, Cleanup, editing a placed tool, spawning Fortnite Blueprints, mass rename |

## Six rules

1. **Deselect everything before you start a tool, including right after Accept** (the new actor stays selected). With an actor selected, the PCG component goes
   *inside that actor* (even a landscape proxy) or overrides the PCG actor you had selected. With nothing
   selected a new actor is created.
2. **Tick the row's checkbox first.** Rows under *Parameters Overrides* stay grey and do nothing until the
   checkbox at their left is on.
3. **Nothing appears until something is on Spawning.** Add at least one element to Static Meshes, or tick
   Spawn Actors and give it a class.
4. **Leave PCG Mode to edit a spline.** The transform gizmo only comes back in Selection Mode.
5. **Static Meshes make one ISM per actor** (cheap, one Outliner row). **Actors spawn one actor per point**
   (costly). Use meshes unless each one must be its own actor.
6. **Each new tool starts from defaults.** Set the mesh and settings again every time.

The `PCGToolComponent` generates in editor worlds only: what it spawns ships, the graph doesn't run in-game.
