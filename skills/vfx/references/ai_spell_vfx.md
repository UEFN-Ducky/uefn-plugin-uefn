---
description: "Spell and ability VFX with no VFX artist: an AI pattern video as the reference, every spell split into flipbook / code / mesh parts, three sources for the flipbook (AI video, image-model sheet, pure code) with cost and when to pick each, camera-facing sprite stacking, sprite trails, a flying light, spell upgrades, cast moves"
metadata:
  label: "AI spell VFX"
  default_enabled: false
  load_condition: "User wants spells, ability effects, projectiles, fireballs, lightning, meteors or magic circles, or wants AI-generated fire/smoke/explosion flipbooks"
---

# AI spell VFX — parts, not one video

Workflow from *Can It Code? — "AI Can Now Make Game VFX. Here's My Workflow"*
(2026-11-09): four Diablo-style spells built in Unreal by an agent, then ported to
Godot. Adapted to UEFN below.

## Lesson 1 — one video is not a spell

A video on a quad reads from one camera angle only. A 3D spell flies in any
direction and hits enemies anywhere, so a spell is **separate parts + timing**.

## Step 1 — a pattern video first

Before building, make a short AI video of the **whole spell seen from the game
camera** (top-down for an ARPG). It is the reference for which parts exist, their
order and their timing. When done, compare the spell to it frame by frame from the
same camera.

## Step 2 — every part is one of three things

| Part | Examples | Built as |
|------|----------|----------|
| **Flipbook** (the "living picture") | fire, smoke, explosion, burning ground | sprite sheet on a camera-facing sprite (SubUV) |
| **Code** | sparks, light, trail, glow, shockwave | stock modules, no texture or a soft dot |
| **Mesh** | meteor rock, debris | mesh renderer with a project mesh (`create_niagara_mesh`, Tripo or Blender model) |

Most of a spell is code. The flipbook is the hard part.

## Step 3 — a round body from flat sprites

- Core: a flipbook (the video used **64 frames, 8×8**) on a sprite that always faces
  the camera, so it looks round from every side. One sprite is not enough: **stack
  2–4 core sprites** with different size, rotation and start frame.
- Tail: many tiny sprites spawned along the path (spawn per unit distance), each
  shrinking and dying in **~0.1 s**.
- Light: one light renderer particle rides with the projectile so the ground glows
  under it. One light per spell.
- The fireball was **4 emitters**: core flipbook, sprite tail, sparks, light. Each
  emitter is just count, lifetime and size rules — one `add_niagara_emitter` each.

## Step 4 — three ways to make the flipbook

| Way | How | Cost | Look | Pick for |
|-----|-----|------|------|----------|
| **AI video** | image model draws one fire on black → video model animates it → cut frames into a sheet | ~$0.50–1 a clip, ~$3 a spell | most realistic; best magic circles | hero effects |
| **Image sheet** | image model draws the whole grid in one picture (~2 min) | no extra cost | surprisingly close to video | quick tests, most effects |
| **Pure code** | noise, gradients, stock modules, no picture | free | least realistic | stylized games |

Black background → additive material, no alpha cleanup. Cut a clip into a sheet
with ffmpeg in the sandbox: `-vf "fps=<frames/seconds>,scale=256:256,tile=8x8"`.

## Step 5 — upgrades reuse the parts

New counts and timing on the same parts: fireball → triple fireball, lightning orb
→ chain lightning (jumps target to target), meteor → meteor shower. The demo kept
60+ FPS with 50 monsters on screen.

## Step 6 — a cast move per spell

One hand animation for every spell gets boring fast. Give each spell its own cast
move (text-to-motion) and line its release frame up with the VFX impact
(`vfx_design` timing envelope). Every hit shows a damage number; the aimed enemy
gets a health bar.

## In UEFN

- The video built Niagara with a Python script. **Never in UEFN**: one emitter per
  call through `stock_module_assembly` (V2 InitializeParticle, ParticleState first).
- Flipbook: import the sheet under `{content_root}<Effect>/Textures`, an additive
  translucent particle material with Particle SubUV, sprite renderer
  **Sub Image Size 8×8** and the stock **SubUV Animation** module. Sheets ≤ 2048²
  (`uefn` `profiling_fixes`, oversized textures).
- Overdraw is the #1 cost: few large core sprites, tiny short-lived tail sprites,
  no per-particle collision.
- The projectile itself is a Scene Graph entity moved by
  `keyframed_movement_component` (hard rule 3) with the system attached; impacts
  through the 43.00 Health & Damage pipeline.
- Pictures: `ducky_generate_image`. Models: `tripo-api`. Blender-baked flipbooks:
  `vfx-fx` `game-fx-export`. Whole pipeline (monsters, loot, inventory):
  `uefn` `ai_game_pipeline`.
