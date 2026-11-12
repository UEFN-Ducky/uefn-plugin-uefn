---
description: "Agent-led AI asset pipeline for an ARPG-style island: the agent writes every prompt and drives every tool, image-model 4-side turnaround → Tripo multiview → quad Smart Mesh ~10k → Smart UV → texture for crowd monsters and loot, text-to-motion cast moves, video-to-rig monster animation, spell VFX, damage numbers, health bars, shape-based inventory"
metadata:
  label: "AI game asset pipeline"
  default_enabled: false
  load_condition: "User wants to make monsters, enemies, loot, spells or a whole ARPG / dungeon / survivor level with AI-generated models, pictures, animation and effects"
---

# AI game asset pipeline

From *Can It Code? — "AI Can Now Make Game VFX. Here's My Workflow"*
(2026-11-09): a graveyard level with spells, 50 monsters, damage numbers, loot and
an inventory, all made by an agent.

## The method: conversation, not prompts

The person gives ideas and direction and asks questions; **the agent writes the
prompts and drives every tool itself** (MCP or small scripts). Never hand the
person prompts to paste.

## One tool per job

| Job | Tool in the video | Ducky route |
|-----|-------------------|-------------|
| Pictures, turnarounds, flipbook sheets | GPT image | `ducky_generate_image` |
| Picture → short clip (fire on black, spell pattern) | Seedance 2.5 (cheaper models work) | external |
| Monsters, props, loot | Tripo | `tripo-api` |
| Cast moves from one sentence | NVIDIA Kimodo | `animation` |
| Monster animation from an AI video | video2rig (github.com/canitcode/video2rig) | `rigging` |
| Spells | the agent | `vfx` `ai_spell_vfx` |

## Monsters and loot

1. Image model draws the monster from **4 sides: front, left, right, back** (same
   style, plain background).
2. All 4 into Tripo **multiview**, so the back is not guessed.
3. **Smart Mesh, quads**, with a poly target: crowd monsters **~10,000** each.
4. **Smart UV** unwrap, then Tripo paints the texture onto that UV.
5. Every monster, the meteor rock and every loot item came from this path.

In UEFN: import under `content_root`, keep LOD0 / Nanite fallback under the
validator limit (`nanite_fallback_vertex_count`), simple collision
(`collision-proxy`), NPC setup through `npc-ai`.

## Combat feel and loot

- A damage number on every hit, a health bar on the aimed enemy (Health &
  Damage pipeline, `recent_changes`; HUD through the UI kit).
- Many enemies: spread spawns over frames (`verse_insights` spawn-burst fix).
- Loot drops are 3D items; the inventory gives each item **as many slots as its
  shape**, and every item changes the hero (fire damage, life, cast speed). The
  first inventory was bad — plan for iterations.
- Stats, currency and XP stay in our packs (`player_core`, `economy`,
  `progression`); item modifiers consume them, never a mode-owned table.

## Porting

The same pictures and numbers rebuilt in Godot looked almost identical: the look
lives in the textures and numbers, not the engine. Keep a per-spell table of
counts, lifetimes and sizes.
