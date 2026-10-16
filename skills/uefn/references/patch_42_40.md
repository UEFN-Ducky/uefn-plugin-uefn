---
description: "What changed in UEFN / Fortnite 42.40 (Oct 15 2026) and which skill covers each item — text chat channels, abilities out of Experimental (Instigator ?entity, renames), 43.00 subscribable events, Discover redesign + required artwork from Oct 22, LEGO Brick Editor, HUD Controller touch overrides, VerseVM session toggle, IARC in Creator Portal, Fab source assets, Gatekeeper Shotgun, bug fixes"
metadata:
  order: 1
  label: "42.40 patch (Oct 15 2026)"
  default_enabled: false
  load_condition: "The user asks what is new in UEFN / 42.40 / the latest update / patch notes, or something the 42.40 notes changed (text chat, abilities, Discover thumbnails / logo / gameplay video, LEGO bricks, touch controls, VerseVM, IARC, Gatekeeper Shotgun, 43.00 Verse errors)"
---

# UEFN 42.40 (released Oct 15 2026)

Build `++Fortnite+Release-42.40-CL-59247843`. Checked against the 42.40 Verse digests
(diffed with 42.30), compile probes in UEFN 42.40 and every Epic MCP toolset described
live (30 toolsets / 388 tools — **unchanged** from 42.30). Where the notes and the
digest disagree, the digest wins; rows marked *not in the notes* came from the diff.

## Build with it

| Change | What it is | Skill |
| --- | --- | --- |
| **Text chat channels** | `text_channel` in `/Verse.org/Chat`: team / faction / role chat, `CanSend` (read-only), `text_message_style` colors + `[labels]`, `SystemMessageColor`, `GetTextChannels`, 100 members. Verse can't send or read messages | verse `sys_text_chat`; template `team_text_chat` |
| **Abilities out of Experimental** | Every `/UnrealEngine.com/Abilities` and `/Fortnite.com/Abilities` type lost `@experimental` — islands with custom or template abilities can publish | scenegraph `custom_abilities`, `template_abilities` |
| Abilities use entities | `ability_context.Instigator : ?entity` (was `?agent`), `fort_projectile_component.GetInstigator[] : entity`; target queries return entities | scenegraph `custom_abilities` |
| Renames | wedge `CentralAngle` → `Angle` (**radians**, max 2π); `self_ability_target_query` → `fort_self_ability_target_query` (*not in the notes*; Epic's quickstart still shows the old name) | scenegraph `template_abilities` |
| Open enums | `fort_ability_attach_socket`, `fort_target_query_affiliation` — a `case` needs `_ =>` (3512) | scenegraph `template_abilities` |
| In the digest now | attribute modifier point / span (`fort_attribute_modifier{Attribute, Modifier, Value}`), projectile `LifetimeAfterStop`, `@editable_number` minimums of 0, `torch_mesh` (*not in the notes*); `MakeAbilityEffectComponent` removed | scenegraph `template_abilities`, `held_items` |
| Ability fixes | `Use()` with a player instigator, animations replicate and loop, rejected uses don't run their timeline, `Cancel` stops the timeline, end events fire once (also after unequip mid-use), burn VFX shows | scenegraph `template_abilities` |
| **43.00 Verse errors (upcoming)** | `event(t)` becomes subscribable; your own `Subscribe` extension on events turns into an ambiguous overload — delete it. Published islands keep running | verse `events_subscriptions`, `umg_verse_field_events` |
| Gatekeeper Shotgun | `GatekeeperShotgun_BR_CH7S4_Rare`, `GatekeeperShotgun_BR_CH7S4_Epic`, `GatekeeperShotgun_BR_CH7S2_Legendary` (`/Fortnite.com/Weapons`) | scenegraph `itemization`, leveldesign `content_catalog` |
| Reality Reign | Prefabs + Floor / Wall / Prop galleries, Processor Base, Display Tower | leveldesign `content_catalog` |
| **LEGO Brick Editor** | 50 new bricks, categories by brick type, wider LOD, primitive bricks change type when Kragled | leveldesign `lego_brick_editor` |
| **Touch layout override** | Touch Control Layout Override gets **Apply Canvas Transform** (uncheck for icon-only); Jetpack Jump/Sprint, Shoot with an empty widget, Carry/Drop, pass-through touches fixed | virtualpointer `touch_layout_override` |

## Publishing and Creator Portal

| Change | Skill |
| --- | --- |
| **Discover redesign** (phased): autoplay video, new tile shapes, cleaner logos. **From Oct 22 2026 portrait thumbnails, landscape thumbnails and a logo are required to publish or update**; new gameplay video for the details page | uefn `creator_portal`; island-media-kit makes all of them |
| **IARC questionnaire** now inside the Creator Portal publish flow (before moderation); retake it when an update changes your answers | uefn `creator_portal` |
| **UEFN source assets on Fab**: licensing is live; free Epic kit (Verse UI Kit); Fab window inside UEFN | uefn `creator_portal` |
| Memory: thermometer → profiling, MB instead of units (repeat of 42.30) | uefn `creator_portal` |

## Editor

| Change | Skill |
| --- | --- |
| **VerseVM toggle** (Session menu): test against the new VerseVM instead of BPVM. While on, **Verse Reload is disabled** (Ducky's `workspace_push_verse_changes`) and Live Edit doesn't carry Verse properties | uefn `verse_build_lifecycle` |
| Fixes: Browse To Asset / Ctrl+B on static meshes, publish cancel, errors when closing a project, Entity Prefab Editor viewports (Maximize checkbox, hidden toolbar tools in the menu), glTF skinned-mesh import (repeat of 42.30), Landscape Paint allow-list cursor (repeat), WaterBodyIsland terrain properties | uefn `troubleshooting`, scenegraph `editor_tools`, leveldesign `landscape_foliage` |
| Lore: validation fix-up resaves only the affected packages; a branch archived by someone else no longer shows as active | uefn `troubleshooting` |
| RigMapper V2 rig expressions (MHL_MHH / CDL_CDH) + stale-index fixes | — (MetaHuman rig internals) |
| Roadmap: New Virtual Machine moved to Q4 2026 | — |

## Fixes worth knowing

Shock Rocks no longer break structures with Environmental Damage off · vehicle exit key
shows on keyboard and mouse · **Guard Spawner keeps the weapons you assign in the
editor** · **audio follows the active Scene Graph camera** on a `camera_director` · Seven
Cluster Cannon shows its real damage · Windows GPU stability (AMD launch crashes, Intel
async compute).
