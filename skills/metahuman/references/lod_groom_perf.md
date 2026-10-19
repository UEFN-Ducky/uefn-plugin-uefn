---
description: "UEFN MetaHuman LODSync, hair groom settings, island memory budgets"
metadata:
  label: "MetaHuman LOD and groom performance"
  default_enabled: false
  load_condition: "Tuning MetaHuman LODs, grooms, or memory for Fortnite islands"
---

# LOD, groom, and island performance

UEFN MetaHumans use a **reduced LOD/texture/groom** cut versus cinematic UE.
Still treat each MH NPC as expensive — prefer a few heroes, not crowds.

## LODSync

Assembled Blueprints include **LODSync** so face/body (and related meshes) drop
LODs together. Inspect with `metahuman_get_info` (component kind `lod_sync`).

Tuning tips (editor Details on the assembled BP):

- Lower **Forced LOD** / reduce max LODs for distant NPCs or debug missing eyes
  (common beginner fix: force a mid LOD if LOD0 eyes disappear in viewport).
- Prefer the UEFN assemble quality tier that matches the shot (medium for most
  gameplay NPCs).

Rough reference ceilings (cinematic MH, for scale — UEFN is lower):

| Part | Order of magnitude |
|------|--------------------|
| Head LOD0 | ~24k verts (cinematic); UEFN starts from a lower table |
| Body LOD0 | ~30.5k verts (cinematic Epic body) |

For island work, trust **UEFN Export** defaults first; only then hand-tune
LODSync / MetaHuman component / groom components.

## Hair grooms

- Strand hair is costly; UEFN leans on **cards** at lower LODs.
- Groom memory does not magically stream away — many simultaneous MH NPCs with
  full grooms will blow VRAM/island budgets.
- Reduce groom quality on background NPCs; hide or simplify beards/lashes when
  far from camera.

## Practical budgets

- **1–3** hero MetaHuman NPCs with careful LOD/groom: usually fine after UEFN Export.
- **Crowds**: do not instance dozens of full MH — use Fortnite characters,
  impostors, or non-MH meshes (animation `npc_characters`).
- Test on target platforms (including lower-end) before publish.

## Agent workflow

1. `metahuman_get_info` → note LODSync / Groom components.
2. Adjust in BP Details; save.
3. PIE with the real spawner count you will ship.
4. If memory fails, drop assemble quality, simplify grooms, or reduce MH count.
