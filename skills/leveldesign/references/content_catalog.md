---
description: "Map Content Drawer (All → Fortnite → Props / Prefabs / Devices) to real MCP search paths — walls, floors, prop kits, Creative devices, Verse digests that list every device API; 43.00 Frenzy Fields galleries/prefabs, Gaussian splats (PLY/SPZ, Experimental, visual only)"
metadata:
  order: 2
  label: "Content catalog (Props / Prefabs / Devices)"
  default_enabled: false
  load_condition: "User asks to place props, walls, floors, prefabs, galleries, Creative devices, browse Content Drawer / Fortnite catalog, find what Fortnite assets exist to build with, or mentions a gaussian splat, photoreal scan / capture, PLY, SPZ, real-world capture, Frenzy Fields, farm or barn"
---

## Content Drawer ≠ asset mount

In the editor UI: **Content Drawer → All → Fortnite → Props / Prefabs / Devices**.

That **Fortnite** tree is a **UI gallery filter**, not a registry path. These all return empty:

- `directory="/Fortnite"`
- `directory="/Game/Props"`
- `directory="/Game/Creative/Prefabs"`
- `directory="/Game/Creative/Galleries"`

**Placeable Fortnite Creative content lives under `/Game/Creative/...`.** Always scope `search_assets` / `list_assets` there (or a subfolder below). Param is **`search=`** (not `query` / `name_filter`). Prefer `limit=10..50` + `fields=["asset_name","package_path","asset_class"]` + `offset` to page.

**Placeable Fortnite Creative content lives under `/Game/Creative/...`.** Always scope `search_assets` / `list_assets` there (or a subfolder below). Param is **`search=`** (not `query` / `name_filter`). Prefer `limit=10..50` + `fields=["asset_name","package_path","asset_class"]` + `offset` to page. Keep only **`BlueprintGeneratedClass` / `*_C`**.

The hit's `path` is `{package}.{asset}` — append `_C` for the Content Drawer class.

**5+ pieces (HARD):** ProgrammaticToolset `execute_tool_script` →
`EditorToolset.LevelToolset.AddToSceneFromClass` with `actorType.refPath` = that `Package.Asset_C`,
then `LevelToolset.SetActorFolder` in the same script. Example house kit:
`/Game/Creative/Sets/ArtDeco_Bank/BuildingPieces/AD_Bank_Floor.AD_Bank_Floor_C`.

**Never** `AddToSceneFromAsset` on `/Game/Creative` (mesh or not) — that creates
`FortStaticMeshActor` and fails `AssetValidator_AssetReferenceRestrictions`. Leftover
single props Epic cannot place: `spawn_actor(asset_path=…_C, label=…, folder=…)`.
Devices: `PlaceDevice` only. Then `save_current_level`.

---

## Props (walls, floors, roofs, dressing)

| Content Drawer idea | Search here | Example |
|---------------------|-------------|---------|
| Walls / doors / windows | `/Game/Creative/BuildingActors/Walls` | `search_assets(search="Wall", directory="/Game/Creative/BuildingActors/Walls", limit=20)` |
| Floors / sidewalks | `/Game/Creative/BuildingActors/Floors` | `search="Sidewalk"` or `search="CP_"` |
| Roofs | `/Game/Creative/BuildingActors/Roofs` | `search="Roof"` |
| Indoor / clutter props | `/Game/Creative/BuildingActors/Props` | `search="Chair"` / `search="Crate"` (huge — keep `limit` small) |
| Rocks | `/Game/Creative/BuildingActors/Props` | `search="Rock"` — prop `_C` only (e.g. `CP_Prop_Artemis_Desert_MedRock_01_C`). Never `Environments/.../Meshes` |
| Cliff / nature pieces | `/Game/Creative/Environments/Props` | `search="Cliff"` / `search="Cave"` |
| Building greebles | `/Game/Creative/Items/Building_Parts` | `search="Ring"` |
| Themed kits (castle, military, houses…) | `/Game/Creative/Sets/<Theme>` | e.g. `ArtDeco_Bank` floors/walls/stairs (`AD_Bank_*_C`), `GrayBox`, `MilitaryBase` |
| Prop-set packs | `/Game/Creative/Sets/PropSets` | `Playgrounds`, `Primitives`, … |
| **Harrowville** (v42.10, horror) | `search_assets(search="Harrowville")` | Floor/Stair/Roof, Wall, Prop, Cliff galleries + `Harrowville House`; pairs with the Harrowville: Environment template |
| **Stone Sanctum** (v42.20, temple) | `search_assets(search="Stone Sanctum")` | Temple + Floor / Wall / Roof / Prop / Foundation galleries. Place `_C` via `LevelToolset.AddToSceneFromClass` |
| **Cluster Coast** (v42.10, coastal) | `search_assets(search="Cluster Coast")` | Floor, Wall, Roof, Prop galleries + `Duck Yacht`, `Salty Duck` |
| Trees / hedges | `/Game/Creative/Environments` | `search="Tree"` / `ApolloTrees` / `ApolloHedges` / `AthenaHedges` |

**First pass:** search `/Game/Creative/**` → keep only `BlueprintGeneratedClass` `_C`.
Place with `LevelToolset.AddToSceneFromClass` (batch) or leftover `spawn_actor(…_C)`. Skip
`StaticMesh`, `/BakeData/`, `/HLOD/`, `SM_*`, `…/Meshes/` — page or search again.
**Never** `AddToSceneFromAsset`. Trees: `/Game/Creative/Environments`
(ApolloTrees, hedges) via `foliage_list_sources` → `foliage_scatter(sources=` those `_C` paths).

**Browse folders** (like expanding Content Drawer):

```
list_assets(directory="/Game/Creative/BuildingActors", recursive=false, limit=50)
list_assets(directory="/Game/Creative/Sets", recursive=false, limit=50)
list_assets(directory="/Game/Creative/Sets/GrayBox", recursive=false, limit=50)
```

**Name patterns:** Creative props often use `CP_*` or theme prefixes (`GrayBox_*`, `MilitaryBase_*`). Prefer a short keyword + a **narrow `directory`** over a global `/Game` crawl.

**Do not** greybox with `/Engine/BasicShapes/Cube` when the user asked for Fortnite props — search the table above first.

---

## Prefabs / kits (Content Drawer “Prefabs”)

There is **no** `/Game/Creative/Prefabs` mount for MCP. What the drawer calls Prefabs maps to:

1. **Themed Creative kits** under `/Game/Creative/Sets/<Theme>` (and BuildingActors pieces) — place each Blueprint `_C` like a prop.
2. **Scene Graph prefabs** (entities) — different system: `skill_read_subskill("scenegraph", …)` → `create_prefab_from_entities` / `instantiate_prefab`.
3. **Playsets** (`FortPlaysetItemDefinition`, `PID_*` under `/Game/Playsets`) — item definitions, **not** the usual `spawn_actor` prop path. Prefer Sets / BuildingActors for level dressing.

Workflow for a themed kit:

```
list_assets(directory="/Game/Creative/Sets", recursive=false, limit=50)   # pick theme
search_assets(search="GrayBox", directory="/Game/Creative/Sets/GrayBox", limit=30,
              fields=["asset_name","package_path","asset_class"])
# keep BlueprintGeneratedClass …_C — LevelToolset.AddToSceneFromClass, never AddToSceneFromAsset
```

---

## Devices (Content Drawer + Verse APIs)

Two layers — never confuse them.

**SERIAL:** place/wire one MCP call at a time —
SERIAL: one mutating/editor call per assistant message..

**Sound / horn / SFX / alarms:** search **Devices** for Creative **Audio Player**
(`search_assets(search="Audio", directory="/Game/Creative")`) — never prop kits
or Speakers as the gameplay horn. Recipe:
`skill_read_subskill("uefn", "creative_devices")`.

| Layer | What it is | How to discover | How to place / use |
|-------|------------|-----------------|--------------------|
| **Blueprint in level** | Creative device actor | `search_assets(search="Teleporter", directory="/Game/Creative/Devices", limit=10)` or `directory="/Game/Creative"` | Epic `DeviceToolset` `PlaceDevice` first; leftover `spawn_actor(asset_path="…_C", label=…, folder=…)` then `GetDeviceProperties` / `SetDeviceProperty` |
| **Audio Player** | Gameplay SFX / horns | `search_assets(search="Audio", directory="/Game/Creative", limit=15)` | Epic `PlaceDevice` first; leftover spawn `…_C` → wire `@editable audio_player_device` **one field per turn** |
| **Verse API type** | `teleporter_device`, `button_device`, `audio_player_device`, … | Digests (below) | `@editable` typing / `get_verse_api` — **never** `spawn_actor(actor_class="teleporter_device")` |

Device folders live under `/Game/Creative/Devices/<Name>/` (Button, Teleporter, CharacterSpawner, CaptureArea, … — 100+ folders). List them:

```
list_assets(directory="/Game/Creative/Devices", recursive=false, limit=200)
```

Deep dive: `skill_read_subskill("uefn", "creative_devices")`.

### Digests list every device API

Offline OK — no listener. **All** Epic Creative/Verse device types are in the Fortnite digest:

```
list_verse_digests()
list_verse_types(digest="fortnite", kind="class", name_filter="_device", limit=50)
# page with offset; total is hundreds — always name_filter
search_verse_digest(query="teleporter")
get_verse_api(name="teleporter_device")
```

| Digest | Use for |
|--------|---------|
| `fortnite` | Epic devices, gameplay, characters (`*_device`, modules under `/Fortnite.com`) |
| `verse` | Language + Scene Graph |
| `unrealengine` | Engine APIs |
| `assets` | **This project's** Verse-visible custom materials/meshes/prefabs |

Do **not** call unfiltered `list_verse_devices` (huge dump). Prefer `list_verse_types(…, name_filter=…)` or `search_verse_digest`.

Custom project assets in Content Browser (weapons, imported meshes): `search_assets` under the project `/Game/<Project>/…` path — digests only cover Verse-visible ids.

---

## Golden search → place loop

```
0. ducky_get_status — Epic unreal__* when epic_mcp_online
1. Pick directory from tables above (never /Fortnite)
2. search_assets(search="<keyword>", directory="…", limit=20, fields=[…])
3. Pick a BlueprintGeneratedClass path ending in `_C` (the search hit `path` is not spawnable as-is — append `_C`)
4. get_asset_info / get_actor_bounds after one test spawn if scale is unknown
5. Creative devices → Epic DeviceToolset PlaceDevice
   props → Epic LevelToolset.AddToSceneFromClass (5+ → ProgrammaticToolset execute_tool_script)
   leftovers → spawn_actor(…_C, label=..., folder=...) → snap_actor_to_ground
6. take_high_res_screenshot → save_current_level
```

If zero hits: broaden keyword **or** step up one folder (e.g. Walls → BuildingActors → Creative), never jump to inventing cube greybox unless the user asked for greybox.

## v42.10 additions worth knowing

- **Horror audio:** 166 Audio Control Buses under Content Drawer Horror — search Creative audio devices, not BR environment meshes.
- **Foliage:** `search_assets(search="Tree", directory="/Game/Creative/Environments")` then spawn only `…_C` Blueprint hits. Skip `StaticMesh` / BakeData / HLOD.
- **Paintable landscape layer:** project or Creative materials only — never invent `/Game/Materials`.
- `CP_Prop_Rock_Wall_Moss` now exposes top-moss colour selection.
- New Rare/Epic/Legendary **Striker Burst AR** variants for loadouts.
- Themes: horror → Harrowville set + Horror audio; temple / stone ruin → Stone Sanctum; coastal/beach → Cluster Coast set.

## New in 43.00

| Content | Kind | Where / name |
| --- | --- | --- |
| **Frenzy Fields** | Floor, Wall, Roof and Props **galleries**; **Fields** prefab and **Barn** prefab | Content Browser → Fortnite → Galleries / Prefabs, search "Frenzy Fields". Farm / barnyard / countryside themes. Place the `*_C` Blueprint you find (`LevelToolset.AddToSceneFromClass`), never the meshes inside it |

### Gaussian splats (Experimental, 43.00)

Photoreal captures of real places (a room, building, landscape) used as an
environment or backdrop.

- **Import:** `.ply` or `.spz` file → Content Browser import (same as FBX). Then drag the
  splat asset from the Content Browser into the level.
- **Experimental:** the island can't be published while it uses one (Experimental
  rule); fine for private versions and edit sessions.
- **Platforms:** renders on every supported UEFN platform, **including mobile**, through a
  native render path. Still check memory (Memory Snapshot) — captures are large.
- **Niagara:** splats can be driven through Niagara for creative effects (dissolves,
  reveals, distortion) — see the `vfx` pack.
- **Not collision:** a splat is visual only. Add blocking volumes / invisible props
  where players walk; never expect gameplay to hit it.
- **Use for:** backdrops and set pieces. Gameplay geometry stays meshes/props.

## New in 42.40

| Content | Kind | Verse / catalog name |
| --- | --- | --- |
| **Gatekeeper Shotgun** | Weapon (Rare / Epic / Legendary) | `GatekeeperShotgun_BR_CH7S4_Rare`, `GatekeeperShotgun_BR_CH7S4_Epic`, `GatekeeperShotgun_BR_CH7S2_Legendary` (`/Fortnite.com/Weapons`; the Legendary is named CH7**S2**) |
| **Reality Reign** | Prefabs + Floor / Wall / Prop galleries, Processor Base, Display Tower | Content Browser → Fortnite → Prefabs / Galleries, search "Reality Reign". `search_assets("RealityReign" / "Reign")` under `/Game/Creative` found nothing on Oct 16 2026 — browse the folders and place the `*_C` you find there |
| **LEGO bricks** | 50 new bricks in the LEGO Brick Editor (LEGO islands) | `lego_brick_editor` |

## New in 42.30

| Content | Kind | Verse / catalog name |
| --- | --- | --- |
| **Lavish Lair Set** | Prefabs & galleries | In the editor: Content Browser → Fortnite → Prefabs / Galleries, search "Lavish Lair". Its asset name is not indexed under "Lavish" or "Lair" in the 42.30 registry, so browse the Prefabs/Galleries folders and place the `*_C` you find there |
| **Witch Broom** (Ch6S4) | Item | `WitchBroom_BR_CH6S4_Epic` (`/Fortnite.com/Items`) |
| **Slap Candy Corn** | Consumable (applies Slap) | `SlapCandyCorn_BR_CH7S4_Exotic` (`/Fortnite.com/Items`) |
| **Easy Ride Pumpkin Launcher** | Exotic weapon | `EasyRidePumpkinLauncher_BR_CH7S4_Exotic` (`/Fortnite.com/Weapons`) |

Grant items/weapons with `Inventory.AddItemDistribute(WitchBroom_BR_CH6S4_Epic{})`
(scenegraph `itemization`). Racing: Rocket Racing *template* islands were
unpublished in 42.30; build tracks with the Track Spline Tool, Boost Pads, Volume
Hazards and vehicle spawners on a normal island (uefn `creative_devices`).
