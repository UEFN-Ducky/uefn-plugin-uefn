---
description: "What changed in UEFN / Fortnite 42.30 (Oct 1 2026) and which skill covers each item — conversations template, held items, ability templates, UMG event fields, Content Pre-Checks, Verse paths, memory in MB, Rocket Racing unpublished, Creator Portal benchmarks, Fab source assets, bug fixes"
metadata:
  order: 1
  label: "42.30 patch (Oct 1 2026)"
  default_enabled: false
  load_condition: "The user asks what is new in UEFN / 42.30 / the latest update / patch notes, or something the 42.30 notes changed (conversations template, held items, ability templates, Content Pre-Checks, Verse paths, Rocket Racing, benchmarks, memory thermometer, Fab source assets)"
---

# UEFN 42.30 (released Oct 1 2026)

Build `++Fortnite+Release-42.30-CL-58557680`. Verified against the 42.30 Verse
digests (diffed with 42.20) and every Epic MCP toolset described live — not
just the release notes. Where the notes and the digest disagree, the digest wins
and the table says so.

## Build with it

| Feature | What it is | Skill |
| --- | --- | --- |
| **Conversations template** | Playable LLM NPC example (haggle a car price) in Project Browser → Feature Examples. The Verse API it uses (`persona_component`, `ai_session.RegisterAction`, `Prompt`, voice channels) | verse `sys_conversations`; template `llm_npc` |
| **Held items** | `held_item_template` (`/Fortnite.com/Armory`, 4230+): a carryable non-weapon prefab, torch by default | scenegraph `held_items` |
| **Ability templates** | `fort_template_ability` no longer parametric (no Verse needed); `Targets` arrays; `Any` → `Neutral`; status-effect removal point; burn `DamagePerSecond`; animation span uses `AnimationSequence` + `play_animation_layer`; attribute modifier point/span (editor-only, not in the digest) | scenegraph `template_abilities` |
| **UMG Verse event fields** (MCP) | `event` fields creatable by tool (≤1 bool/int/float param); bind Custom Button `OnButtonClicked` (`OnClicked` no longer compiles) | verse `umg_verse_field_events` |
| New items | Witch Broom (`WitchBroom_BR_CH6S4_Epic`), Slap Candy Corn (`SlapCandyCorn_BR_CH7S4_Exotic`, applies Slap), weapon Easy Ride Pumpkin Launcher (`EasyRidePumpkinLauncher_BR_CH7S4_Exotic`), Lavish Lair Set prefabs/galleries | leveldesign `content_catalog`, scenegraph `itemization` |
| Weapons (digest only) | `fort_trace_weapon_component` `AllowAimDownSightsInAir` / `DuringReload` + setters | scenegraph `custom_weapons` |

## Editor and platform

| Change | Skill |
| --- | --- |
| **Content Pre-Checks** — moderation flags during cook; never block publish | uefn `content_prechecks` |
| **Verse paths** shown in Content Browser, source control, Reference Viewer, tooltips, copied references (new projects only); **Copy File / Package / Verse Path** menus | uefn `troubleshooting` |
| **Memory thermometer → profiling** (auto every cook, MB: 100,000 units = 300 MB; the thermometer leaves running sessions later) | uefn `creator_portal` |
| **Rocket Racing template islands unpublished**; racing tools (Track Spline Tool, Boost Pads, Volume Hazards, Spawner devices) still work without the template | uefn `creative_devices`, `creator_portal` |
| **Analytics benchmarks** (CTR, 5-min bounce, session length, D1/D7) and **offer validation errors** in Creator Portal | uefn `creator_portal` |
| **UEFN source assets on Fab** (publishing opens Oct 15, 88% revenue) | uefn `creator_portal` |
| Epic MCP: 30 toolsets (Logs, Gameplay Tags, Niagara ×4, Physics Asset, Python, Widget Animation, Curve/Data tables, Material Instance, Primitive, Skeletal/Static Mesh, Texture…); dialogue popups no longer stall MCP | uefn `epic_mcp`, `epic_toolsets` |
| Faster session restart; resave reasons in the log on launch; publish cancel fixed | uefn `troubleshooting` |
| `<localizes>` loads faster on the server (2000+ in one module used to hang) | localization |
| Scene Graph: `OnReceive` runs on the server only (client calls ignored) | scenegraph `verse_authoring` |
| Verse Skeletal Animation stays Experimental; a new API will replace it | animation `runtime_playback` |
| Verse compat: `/Fortnite.com/Marketplace` → `/UnrealEngine.com/Marketplace` (42.20, aliased) | verse `sys_marketplace` |

## Fixes worth knowing

Proximity voice chat works again · unsuppressed Ballistic weapons' audio · consumables no
longer vanish on respawn · Hexylvania Alight Torch 02 flame in Performance Mode · WaterBody
Islands expose Affects Landscape · Exotic weapons with built-in wraps in Item Placer ·
Sidekick styles apply · mobile: moving with all inputs consumed, interact/pick-up icons
overridable, fire button no longer tied to aim · equipping via Verse no longer breaks aim/shoot ·
`RemoveItemEvent.RemovedAmount` · rocket launcher / shockwave impulses on physics islands ·
landscape crashes (brush in a deleted region, old landscapes without edit layers, right-click a
proxy) · spline mesh crash · SkinnedMesh import (inverse bind matrices, multi-root) · material
editor shader count · `RemoveWidgetBinding` returned true for missing bindings.
