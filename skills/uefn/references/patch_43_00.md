---
description: "What changed in UEFN / Fortnite 43.00 (Nov 2026) and which skill covers each item — PCG in UEFN, Progression API (quests) publishable + renamed, Health & Damage Pipeline, subscribable events, clock/timer/playable, Last[], tags on creative objects, held-item poses, Teleporter props, vehicle fuel, Scene Graph cameras in radians, weak_map 6, MCP rename to EditorToolset.* + profiling / PCG / Sequencer / MetaSound / Prefab / Scene Capture toolsets, Creator Portal Technical tab, Verse asset redirectors, Data Recovery, Gaussian splats, USD import, breaking changes and known issues"
metadata:
  order: 0
  label: "43.00 patch (Nov 2026, current)"
  default_enabled: false
  load_condition: "The user asks what is new or what changed in UEFN / 43.00 / the latest update / patch notes, or something the 43.00 notes changed (PCG, quests / Progression, health pipeline, Subscribe on events, timers, tags, cameras FieldOfView / radians, MCP toolset names, profiling, Creator Portal Technical, redirectors, Data Recovery, a new 43.00 Verse compile error)"
---

# UEFN 43.00 (current)

Checked against the 43.00 Verse digests (diffed with 42.40) and every Epic MCP toolset
described live in UEFN 43.00 (**56 toolsets / 826 tools**, 42.40: 30 / 388). Where the notes
and the digest disagree, the digest wins; rows marked *not in the notes* came from the diff.
42.40 → `patch_42_40`.

## Build with it

| Change | What it is | Skill |
| --- | --- | --- |
| **Progression API out of Experimental** | Quests and objectives publishable: `/Verse.org/Progression` `quest`, `objective`, `quest_participant`, `quest_membership`; `/UnrealEngine.com` `basic_quest`, `has_quest_rewards`, `has_quest_presentation`, `progress_objective` | verse `sys_quests` (linked from `sys_progression`, `sys_architecture`) |
| Progression renames (*not in the notes*) | `JoinQuest` → `Quest.Join(Participant, Info)` returning `result(quest_membership, []quest_error)`; `AbandonQuest` → `Quest.Abandon`; `quest_objective` → `objective`, `SetRequiredCount` → `SetRequiredProgress`; `quest_reward` → `Grant` / `Preview` / `CanReceive`; participant info `Contributes/Observes/Receives` → `Contribute/Observe/Receive`. Old experimental code stops compiling | verse `sys_quests` § migrating, `compile_errors` |
| **Health & Damage Pipeline** (Experimental, blocks publish) | `/UnrealEngine.com/HealthPipeline` `health_component`, pools, damage/healing events and modifiers; Fortnite shield/overshield pools; built-in weapons damage entities; 9 known issues | verse `sys_health_pipeline` (from `sys_damage_health`) |
| **Events are subscribable** | `event(t)` implements `listenable(t)` (`@available 4300`) — `MyEvent.Subscribe(Handler)` works; a hand-written `Subscribe` extension now clashes (delete it). New `proxy_listenable` / `MakeProxyListenable` | verse `events_subscriptions`, `async`, `umg_verse_field_events`, `whats_new` |
| **clock / timer / playable** | `clock`, `SecondsSinceEpochClock`, `playable` (Play / Pause / Resume / Stop + events, `playable_stop_reason`), `timer` (ReferenceClock, PlayRate, Start/EndSeconds, Get/SetSeconds) | verse `sys_rounds_timers`, `sys_time_tracking` |
| `Last[]` | `Array.Last[]`, `Last[OffsetFromLast]` (`<computes><decides>`) | verse `datatypes` |
| Preceding `<final>` field init | a field initialiser may read a preceding `<final>` field (8 limits) | verse `classes` |
| Tags on creative objects | `has_tags` (`@available 4300`; islands uploaded before 43.00 don't get it), `AddTag` / `RemoveTag` / `ContainsTag` …; `GetTags`, `tag_view`, `tag_search_criteria` deprecated → `FindCreativeObjectsWithTag(tag)` | verse tags page, `devices` |
| `timeline_element` per-agent duration (*not in the notes*) | `SetRemainingDurationForAgent` / `GetRemainingDurationForAgent`; class now `<abstract>` | verse `sys_rounds_timers` |
| `AddMember` / `RemoveMember` (*not in the notes*) | return `result(void, …)` instead of `result(comparable, …)` | verse `compile_errors` |
| `BeginFire` / `EndFire` / `IsFiring[]` (*not in the notes*) | `@available 4300` firing control | scenegraph `custom_weapons` |
| **Held item poses** | `fort_item_owner_pose_modifier_component` on `held_item_template`: fire torch (default), flashlight, map, small / large consumable | scenegraph `held_items` |
| Prefabs inherit their parent class | `pistol_template`, `assault_rifle_template`, `sub_machine_gun_template`, `shotgun_template`, `held_item_template` are no longer `<final>`; a prefab is its parent's subclass in Verse | scenegraph `custom_weapons`, `custom_items`, `held_items` |
| **Teleporter + props** | `Teleport` / `Activate` with a `creative_prop`, `TeleportPropEvent`, `EnterPropEvent`, `enableable`, physics props | verse `devices`; uefn `creative_devices` |
| **Vehicle fuel** | `SetFuelRemaining`, `SetFuelUsageDriving/Boosting/Idle`; `GetFuelRemaining` / `GetFuelCapacity` return -1.0 with no fuel | verse `devices` |
| `SprintedEvent` | fires on sprint input change (was movement start/stop) | verse `devices` |
| Interactable hold logic | `OnStarted` now at hold start; move completion logic to `SucceededEvent` | scenegraph `components` |
| **Scene Graph cameras** | angles in **radians**, `FieldOfView` (was `FieldOfViewDegrees`), modifier layers, user modifiers run on the server; `camera_body` / `camera_lens` not `<final>`; `has_camera_modifier` removed; `GlobalModifierPosition` / `VisualModifierPosition` removed | scenegraph `cameras`, `custom_player_controller` |
| Scene Graph handles (*not in the notes*) | `entity_handle`, `component_handle(t)`, `mesh_part_handle`; Source/TargetMeshHandle on hit and overlap results | scenegraph `components`, `movement_transforms` |
| Same-frame overlap / sweep | results valid the same frame — drop the `Sleep(0.0)` workaround | scenegraph `movement_transforms` |
| No proxy actors | the editor works with entities directly; advice that finds entities through proxy actors is stale | scenegraph `editor_tools` |
| **Scene Graph performance** | cheaper bulk spawning, cheaper moves, the server skips unmoved entities, less reinstancing on compile / push, faster mass deletes, less client memory for many Verse objects / material properties, better memory tracking. Some gains need a **new cook** | scenegraph `SKILL` (43.00 performance), uefn `profiling` |
| `weak_map` limit 4 → 6 | per island persistent `weak_map`s | verse `persistence` |
| Asset modules default to project-wide | Verse modules with reflected assets are project-accessible by default | verse `modules` |
| NPC actions (*not in the notes*) | `npc_actions_component` (`NavigateTo`, `Focus`, `Idle`, …), `guard_actions_component` (`Tether`) replace deprecated NPC calls | npc-ai pack; verse `devices` § NPC |
| HUD Controller | per-button **Apply Canvas Transform** (separate from Override Icon); **Interact + Pickup** override (shared, static); layout data scales buttons | uefn `creative_devices` |
| Cinematic Sequence device | `GetSequenceLength()<transacts>:float` | uefn `creative_devices`; animation |
| **PointerZoom publishable** | pinch-to-zoom, also mouse wheel and right stick; **touch values 50× larger** (retune thresholds) | `virtualpointer` |
| Safe Zone widget | UMG safe-area container | verse `umg_layout`, `umg_palette` |
| **PCG in UEFN** | PCG graphs on actors (PCG Component), PCG Library, deterministic seeds; MCP PCG toolset | leveldesign `procedural_generation`; uefn `epic_toolsets` |
| **Gaussian splats** (Experimental) | PLY / SPZ import as photoreal backdrops, all platforms | leveldesign `content_catalog` |
| Frenzy Fields | Floor / Wall / Roof / Props galleries, Fields + Barn prefabs | leveldesign `content_catalog` |
| **Chaos outfit / cloth in Dataflow** | make cloth and MetaHuman clothing in UEFN | metahuman `assemble_uefn_export` |
| **USD import (Interchange)** | `.usd/.usda/.usdc/.usdz` → meshes, materials, textures, skeletal anims; no USD export | modeling import |
| Animation | RigMapper preview panel; Control Rig Dynamics convex collider / confiner | animation |
| Materials | Verse material inheritance, RVT displacement, Substrate SLW in RT | materials |

## MCP

| Change | Skill |
| --- | --- |
| **Toolsets renamed (breaking):** `editor_toolset.toolsets.{actor,asset,scene,…}` → `EditorToolset.{Actor,Asset,Level,…}Toolset` with PascalCase tools (`SceneTools.add_to_scene_from_class` → `LevelToolset.AddToSceneFromClass`, arg `actorType`); `ValkyrieToolset.{Device,Session}Toolset` → `ValkyrieFortniteToolset.*`; `VerseToolset.VerseToolset`; `ConsoleToolset.LogsToolset`; Python toolset `EnablePythonForMainProject` | uefn `epic_toolsets` (rename table), `epic_mcp` |
| New toolsets: PCG + PCGSpatial, 7 Sequencer, MetaSound authoring, SoundWave, Prefab, Scene Capture, Curve Atlas, Player State, Insights (Target / Timing / Memory Snapshot), Spatial Profiler, UMG Debug, Widget Static Analysis, Agent Skills, Python Scripting, Geometry | uefn `epic_toolsets` |
| **Profiling via MCP**: Timing / Verse Insights, Memory Snapshot, Spatial Profiler | uefn `profiling`, `profiling_mcp`, `profiling_fixes` |
| Cinematics (Sequencer), MetaSound audio, IK Retargeter (in the notes; no IK Retargeter toolset in the live list) | uefn `epic_toolsets`; animation; uefn `audio_metasound`, `creative_devices` (audio) |
| Exec Python vs programmatic toolset (Ducky: `execute_python` stays last resort) | uefn `epic_mcp_ops` |
| Classic devices in DeviceToolset: `ListClassicDeviceOptions` / `SetClassicDeviceOption`; `SetDeviceProperty` is Verse-device only | uefn `epic_mcp_ops`, `creative_devices` |
| MCP settings in **Editor Settings** (not per project), Start / Stop, config setup button, server instructions, image content, auto-start fix | uefn `epic_mcp` |

## Publishing and Creator Portal

| Change | Skill |
| --- | --- |
| **Projects > Technical**: Client (Client Crashes, Hitch Rate, Missed Frames) and Server (Frame Time 33.3 ms, CPU 75%, Memory GB; P95 / median; version markers) | uefn `creator_portal` |
| Rejection explanations with gameplay video, image preview, reviewed thumbnail, audio | uefn `creator_portal` |
| Memory on every cook, real units (MB), per-asset breakdown, thermometer gone | uefn `creator_portal`, `profiling` |
| Progression API and PointerZoom publishable; Health Pipeline still Experimental | verse `sys_quests`; `virtualpointer`; verse `sys_health_pipeline` |
| EDC feedback form (separate from bug reports) | uefn `creator_portal` |

## Editor

| Change | Skill |
| --- | --- |
| **Verse asset redirectors** (Project Settings → Reflect UE Redirectors into Verse Manifest): old names become deprecated aliases; Replace References / Force Delete | uefn `verse_build_lifecycle` |
| **Data Recovery**: objects with a missing Verse class become placeholders and **block saving** until fixed (Tools → Data Recovery) | uefn `verse_build_lifecycle` |
| Verse diagnostics for packages incremental compilation skipped | uefn `verse_build_lifecycle` |
| Python in **Editor Preferences**, enabled **per project** (Ducky's `init_unreal.py` needs it) | uefn `troubleshooting` |
| Live edit: entity prefab assets, snap tools, Blocking / Post Process volumes (Water Body Exclusion still needs push) | uefn `troubleshooting`; scenegraph `editor_tools` |
| `ValkyrieMap=` command line overrides the startup map | uefn `troubleshooting` |
| Compact connectivity HUD | uefn `fortnite_client` |
| Profiling: Verse Insights in Timing Insights (Server target, Use Verse VM), Memory Snapshot filters, mobile profiling, Quick Find | uefn `profiling`, `verse_insights` |
| Editor QoL: copy/paste vectors and transforms as Verse literals (LUF ↔ engine), custom grid transform, actor picker picks entities, performance-validation Content Browser filters, Lumen in the Prefab Editor | scenegraph `editor_tools` |
| Lore: VS Code diff for `.uefnproject` / `.verse` / `.uplugin`, no 24 h reminder, `Lore.vsix`, Branch Explorer fixes | uefn `troubleshooting` |

## Fixes worth knowing

`InvalidIslandVersionOnServer` after version history changes · launch stuck on an idle
client · persistence item duplication on multi-disconnect · JSON parser near 32-bit int max
(verse `persistence`) · `FindEntitiesWithComponent` / `FindComponents` missing components
added in lifetime functions · `Enable()` starting sound / particles with AutoPlay off ·
`basic_interactable_component.Cooldown` with a Duration · `interaction_component.Disable()`
still prompting · Verse class object editables now independent per prefab instance · crash
assigning a device to an optional `@editable` on a Verse component · pasting a device shared
its `@editable` device reference with the original · `SetPresentableToPlayers` across entities ·
Social Synergy API outside edit sessions · Virtual Pointer with a PS5 controller · Pickaxe
emote damage while disabled · migrated assets missing until restart · VFX via Sequencer ·
undo push flag, voice-mute crash, live-edit entity placement error, World Partition client
edits · in-game UI (split-screen transactions, disabled custom buttons, in-world UI order) ·
audio (streaming subtitles wait for play, Windows mic list) · Python `unreal.Array` / `Set`
in-place ops returned None, `>=` acted like `>` (uefn `epic_mcp_ops`).

## Known issues

| Issue | Workaround | Skill |
| --- | --- | --- |
| Scene Graph cameras don't activate on play servers; `GetComponent[camera_director_component]` fails (fixed 43.10) | private-only `using { /Fortnite.com/SceneGraphCameras }`; Third Person Controls device for interaction | scenegraph `cameras` |
| Wedge target query misses actor-less entities, so wedge abilities don't damage them (fixed 43.10) | use another target query | scenegraph `template_abilities` |
| Health Pipeline: rockets ricochet, lightweight projectiles, some non-ballistic weapons, lingering AoE once, physics collisions, healing items, hit FX, no team filtering, zero-delta entries | see the page | verse `sys_health_pipeline` |
| Adding a component that already belongs to another entity logs a warning (future error) | remove it first or create a new one | scenegraph `components` |

## Upgrade notes (breaking on 43.00)

| Break | Fix | Skill |
| --- | --- | --- |
| Own `Subscribe` extension on `event` → ambiguous overload | delete it; use the built-in `Subscribe` | verse `events_subscriptions`, `compile_errors` |
| `FieldOfViewDegrees`, degree angles on cameras | `FieldOfView`, radians | scenegraph `cameras` |
| `GlobalModifierPosition` / `VisualModifierPosition` removed | modifier layers | scenegraph `cameras`; verse `compile_errors` |
| Asset module accessibility clash (modules with reflected assets no longer need an accessibility specifier, so more identifiers are visible across the project) | add qualifiers or adjust your `using` paths (3588 ambiguous identifier) | verse `modules`, `compile_errors` |
| Material inheritance: qualified member access `Value.(Class)Member` fails with "unknown member" when `Member` moved to a parent class; same-name extension methods on material classes that now inherit from each other conflict | remove the qualification (`Value.Member`) or name the **parent** class that now declares the member; extension methods: delete the child's if identical, else rename (rename all to surface every call site; fix children before parents) | materials `runtime_materials_verse`; verse `compile_errors` |
| Experimental Progression code (`JoinQuest`, `quest_objective`, …) | migrate to the renamed API | verse `sys_quests` |
| Touch values 50× larger | retune thresholds | `virtualpointer` |
| MetaHuman normals are no longer recalculated automatically when you assemble a character from MetaHuman Creator | if the existing normals are wrong, assemble again (the separate Interchange DNA Import Settings option only turns normal recalculation off) | metahuman `assemble_uefn_export` |
| Epic MCP 42.40 toolset / tool names | 43.00 names | uefn `epic_toolsets` |

Compile-probe error codes for each break: verse `compile_errors`. Roadmap: Epic's UEFN roadmap
page (New Virtual Machine still listed for Q4 2026 in 42.40).
