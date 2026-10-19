---
description: "Bring existing Unreal Engine MetaHumans into UEFN — re-assemble UEFN Export or migrate assets"
metadata:
  label: "UE → UEFN MetaHuman migrate"
  default_enabled: false
  load_condition: "Moving MetaHuman assets from a full Unreal Engine project into UEFN"
---

# UE → UEFN MetaHuman migrate

MetaHumans built for full Unreal Engine are **not** automatically island-safe.
UEFN needs the **UEFN Export** assembly cut (smaller LODs, textures, simplified
face materials, groom tuning).

## Preferred path: re-assemble for UEFN

1. Open the same `MetaHuman Character` (or recreate from Identity) in an editor
   build that still exposes **UEFN Export**.
2. Assembly → **UEFN Export** → Assemble into a folder you will copy/migrate.
3. Migrate/copy the assembled package into the UEFN project (Migrate Tool or
   copy `Content/MetaHumans/...` carefully with dependencies).
4. Open in UEFN; verify with `metahuman_get_info` / PIE on an NPC spawner.

## Alternate: migrate already-UEFN assets

If you previously assembled with UEFN Export (even from a UE project), migrate
that **assembled** output — Blueprint + meshes + materials + Common shared
folder refs. Migrating only the Character source asset without UEFN assemble
leaves cinematic-sized content.

## Platform notes

- **UEFN MetaHuman export/work**: Windows-focused in Epic’s support matrix.
- Keep **Common** MetaHuman shared assets once per project; avoid duplicating
  Common for every character when the assemble options allow sharing.

## Do not

- Ship cinematic LOD0 + strand-heavy grooms into a published island and hope
  memory works — use UEFN Export and `lod_groom_perf`.
- Mix skeletons from a UE4 marketplace pack with MetaHuman DNA without a full
  Mesh-to-MH / Creator rebuild.

## Next

`npc_spawn` · `lod_groom_perf`
