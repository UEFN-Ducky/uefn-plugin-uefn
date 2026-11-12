---
description: "What is new or changed in Verse, and the names that do not exist — first verse_digest_changes() for the installed build, then the rules agents get wrong: chat channels, Unarmed, marketplace, LLM NPCs, ability templates, held items, UMG event fields, text chat, subscribable events, quests (Progression API), health and damage pipeline, clock / timer, Last[], has_tags, vehicle fuel, pointer input, loot pools, perception, camera modifier pieces, day sequence device"
metadata:
  order: 2
  label: "What changed, and names that do not exist"
  default_enabled: false
  load_condition: "What is new in Verse or UEFN, what changed after a Fortnite update, a name from a tutorial or an older island that no longer compiles, voice or text chat channels, punch / FPS melee, V-Bucks entitlements, talking LLM NPCs, ability templates, held items, UMG button/event fields, loot pools, perception, camera modifiers"
---

## What changed, and names that do not exist

**Start with the installed build, not this page.** Fortnite updates change the Verse API,
and this page is written by hand.

1. `verse_digest_changes()` lists what the newest Fortnite build on this PC added, removed
   and changed, and which names are no longer experimental. Narrow it with a word:
   `verse_digest_changes("camera")`.
2. `get_verse_api("<name>")` gives the definition with its doc comments.
3. The digest wins over every skill page. A name that is not in the digest does not exist
   in this build; a name with `@experimental` above it blocks publishing.

Below: one rule per feature, with the page that has the code. Names marked "does not
exist" were copied from Epic pages or guessed by agents and fail with E3506.

### Chat, voice, text

- **Squad voice** = `/Verse.org/Chat` `voice_channel` + `AddChatChannel` on
  `GetSimulationEntity[]`. The speaking check is `IsMemberSpeaking` (`IsSpeaking`
  does not exist). Never build a custom radio. → `sys_chat_channels`
- **Text chat** = `text_channel(member)` + `has_text_member_info` (`CanSend` = read-only,
  `MessageStyle`), `text_message_style{TextColor, ContextMessage}`, `AddChatChannel` /
  `GetTextChannels` on `GetSimulationEntity[]`. Verse cannot send or read messages.
  → `sys_text_chat`, template `team_text_chat`
- **Talking NPCs** = `/UnrealEngine.com/Conversations` `persona_component` on an
  `npc_behavior`: `SetPersonality[Msg]`, `PromptToTalk[Msg, Channel]`, structured output
  `GetAISession().RegisterAction(Def, Required, struct, Callback)`, one-shot
  `Session.Prompt(Msg, struct)`, with an `agent_group` + `voice_channel` and
  `Player.SetConversationTarget`. `AppendToPersonality`, `RegisterPromptBinding` and
  `ResponseType` do not exist. Build `<localizes>` messages before a `[ ]` call (E3512).
  Ready-made: `verse_template_apply("llm_npc_shopkeeper")`, `verse_template_apply("llm_npc")`. → the `conversations` skill

### Items, weapons, abilities

- **Punch / FPS melee** = grant `Unarmed_Creative_V1_Common{}` and place
  `gameplay_camera_first_person_device` with Epic `PlaceDevice`. → scenegraph `itemization`
- **Ability templates**: `x := class(fort_template_ability):` (no type arguments),
  `Targets := array{…}` (`Any` → list `Neutral` etc.); `ability_context.Instigator` and
  projectile `GetInstigator[]` are `entity` (cast `agent[...]`); `Ability.Use(...)` is
  `no_rollback` (never inside `if`); wedge `Angle` is in radians; open enums need `_ =>`.
  → scenegraph `custom_abilities`, `template_abilities`
- **Held items**: `held_item_template`, hold poses with
  `fort_item_owner_pose_modifier_component`. → scenegraph `held_items`
- **Prefabs inherit their parent class**: a prefab made from a weapon or item template is a
  subclass of that template in Verse. → scenegraph `custom_weapons`, `custom_items`
- **Loot pools**: weighted loot tables that return item entities (`weighted_loot_pool`,
  `SelectLoot[loot_context{…}]`, Fortnite's own `fort_loot_pool_chest`). Never an Item
  Granter chain for random drops. → `sys_loot_pools`

### Events, quests, health, time

- **Events are subscribable**: `event(t)` implements `listenable(t)`, so
  `MyEvent.Subscribe(Handler)` returns a `cancelable` (UMG event fields too). Delete any own
  `Subscribe` extension on `event` (ambiguous overload); `Await` loops keep working.
  `MakeProxyListenable(L)` wraps a listenable so callers can't cast it back.
  → `events_subscriptions`
- **UMG event fields** are creatable; bind `OnButtonClicked` (not `OnClicked`). They reflect
  as `event(tuple())`. The field tools open the widget's editor once so fields reach Verse
  (`verse_ready`). → `umg_verse_field_events`
- **Quests (Progression API)**: `quest := class<abstract>(objective)`;
  `Quest.Join(Participant, Info)` / `Abandon` (`JoinQuest` / `AbandonQuest` do not exist);
  `progress_objective` (`SetProgress`, `SetRequiredProgress`); `basic_quest` auto-completes
  and grants its `quest_reward`s; `fort_quest_collection` shows quests in the Fortnite quest
  UI. → `sys_quests`
- **Health and damage pipeline**: `/UnrealEngine.com/HealthPipeline` (`health_component`,
  `health_pool_entry`, `damage_event` / `healing_event` sent with `entity.SendUp`,
  `health_adjustment_modifier`) and `/Fortnite.com/FortHealthPipeline`. Built-in weapon
  damage hits Scene Graph entities. `AddModifier(Modifier)` takes the modifier only;
  modifiers run in the order added. → `sys_health_pipeline`
- **Time**: the `clock` interface, global `SecondsSinceEpochClock`, the `playable` interface
  and `timer` (count up or down, `PlayRate`). → `sys_rounds_timers`, `sys_time_tracking`
- **Day and night from Verse**: `day_sequence_device` (`DayNightCycleMode`,
  `DayNightCycleTime`, sun, fog, sky and cloud fields, `FadeIn` / `FadeOut`). → `devices`

### Language and modules

- A field initializer may read a preceding `<final>` field (the offline LSP still flags it;
  the UEFN build accepts it); `Array.Last[]` / `Array.Last[N]`. → `classes`, `datatypes`
- **Name clash (3588):** a local named `Last`, `Distance` (or another extension name) is
  ambiguous inside a class; rename it (`PrevTime`, `LastLogin`, `BoomLength`).
  → `compile_errors`
- **Short forms**: `if. C then X`, `spawn. F()`, `array. X`, `option. X`, `F of type:` + an
  indented archetype block, an indented `array:` block = an array, and the
  `first(X : Xs) { X }` macro. → `syntax`
- **LSP lags the compiler**: the Problems panel flags every `listenable.Await()` and a
  preceding `<final>` field init. The UEFN build accepts them, so trust
  `workspace_compile_verse`. → `compile_errors`
- **Tags**: creative objects implement `has_tags` (`AddTag`, `ContainsTag[]`,
  `RemoveTag[]`). `GetCreativeObjectsWithTag`, the tag-instance overload of
  `FindCreativeObjectsWithTag`, `tag_view`, `tag_search_criteria` and `GetTags` are
  deprecated: pass the tag **type**. → `classes`
- **Modules**: modules holding reflected assets default to project-wide accessibility (new
  name clashes possible); at most six persistent `weak_map` vars per island.
  → `modules`, `persistence`, `compile_errors`
- **Entitlements / V-Bucks** = `using { /UnrealEngine.com/Marketplace }` (`MakePriceVBucks`,
  `BuyOffer`, `GrantEntitlement`); `/Fortnite.com/Marketplace` is deprecated aliases. Island
  Coins stay in `economy` / `GetCurrencyProvider`. → `sys_marketplace`

### Devices, input, UI

- `fort_vehicle` fuel (`GetFuelRemaining`, `GetFuelCapacity`, `SetFuelRemaining`,
  `FuelUsageDriving/Boosting/Idle` + `SetFuelUsage*`); `teleporter_device` is `enableable`
  and teleports props; `SprintedEvent` fires on sprint input;
  `cinematic_sequence_device.GetSequenceLength`. → `devices`
- Input actions (`Move`, `Interact`, `PointerSelect`, `PointerZoom`, `PointerRotate`): read
  each in the digest; one with `@experimental` above it blocks publishing.
  → `sys_input_devices`, `virtualpointer`
- Safe Zone widget in UMG. → `umg_layout`
- `basic_interactable_component.OnStarted` runs when a hold **starts**; on-completion logic
  belongs in `SucceededEvent`. → scenegraph `components`

### Scene Graph

- **Cameras** are built from small modifier pieces stacked in order (attach to entity, boom
  arm, offset, collision push, dampen, set, framing). `fort_orbit_camera_modifier`,
  `fort_fixed_angle_camera_modifier`, `fort_fixed_point_camera_modifier`, modifier
  positions and `FieldOfViewDegrees` do not exist. Angles are radians. → scenegraph `cameras`
- **Perception**: sight, hearing and touch as emitter + detector components with filtered
  subscriptions. → scenegraph `perception`
- Adding a component that already belongs to another entity logs a warning: remove it from
  its entity first, or create a new one. → scenegraph `components`
