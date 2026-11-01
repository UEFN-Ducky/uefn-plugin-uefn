---
description: "What changed in Verse per Fortnite release (42.20, 42.30, 42.40, 43.00) — chat channels, Unarmed, marketplace, LLM NPCs, ability templates, held items, UMG event fields, text chat, abilities out of Experimental, 43.00 subscribable events, quests (Progression API) publishable, health and damage pipeline, clock/timer, Last[], has_tags, vehicle fuel, PointerZoom — and the names that do not exist"
metadata:
  order: 2
  label: "What's new by release (42.20 → 43.00)"
  default_enabled: false
  load_condition: "Voice or text chat channels, punch / FPS melee, V-Bucks entitlements, talking LLM NPCs, ability templates, held items, UMG button/event fields, or anything a recent Fortnite release changed"
---

## What's new by release

Each line is a rule with the page that has the code. Names marked "does not exist"
were copied from Epic pages or guessed by agents and fail with E3506.

### 42.20 — chat, Unarmed, marketplace

- **Squad voice** = `/Verse.org/Chat` `voice_channel` + `AddChatChannel` on
  `GetSimulationEntity[]`. The speaking check is `IsMemberSpeaking` (`IsSpeaking`
  does not exist). Never build a custom radio. → `sys_chat_channels`
- **Punch / FPS melee** = grant `Unarmed_Creative_V1_Common{}` and place
  `gameplay_camera_first_person_device` with Epic `PlaceDevice`. → scenegraph
  `itemization`
- **Entitlements / V-Bucks** = `using { /UnrealEngine.com/Marketplace }`
  (`MakePriceVBucks`, `BuyOffer`, `GrantEntitlement`); `/Fortnite.com/Marketplace`
  is deprecated aliases. Island Coins stay in `economy` / `GetCurrencyProvider`.
  → `sys_marketplace`

### 42.30 — conversations, ability templates, held items, UMG events

- **Talking NPCs** = `/UnrealEngine.com/Conversations` `persona_component` on an
  `npc_behavior`: `SetPersonality[Msg]`, `PromptToTalk[Msg, Channel]`, structured
  output `GetAISession().RegisterAction(Def, Required, struct, Callback)`, one-shot
  `Session.Prompt(Msg, struct)`, with an `agent_group` + `voice_channel` and
  `Player.SetConversationTarget`. `AppendToPersonality`, `RegisterPromptBinding` and
  `ResponseType` (on Epic's template page) do not exist. Build `<localizes>`
  messages before a `[ ]` call (E3512). Ready-made: `verse_template_apply("llm_npc")`.
  → `sys_conversations`
- **Ability templates**: `x := class(fort_template_ability):` (no type arguments),
  `Targets := array{…}` (`Any` → list `Neutral` etc.). → scenegraph
  `template_abilities`
- **Held items**: `held_item_template`. → scenegraph `held_items`
- **UMG event fields** are creatable; bind `OnButtonClicked` (not `OnClicked`). They
  reflect as `event(tuple())` — `Await` them in a loop (or the Verse UI Kit's
  `Helper.SubscribeToEvent`); in 42.x `.Subscribe` on an `event` fails (works from 43.00). The field
  tools open the widget's editor once so fields reach Verse (`verse_ready`).
  → `umg_verse_field_events`

### 42.40 — text chat, abilities publishable

- **Text chat** = `/Verse.org/Chat` `text_channel(member)` + `has_text_member_info`
  (`CanSend` = read-only, `MessageStyle`), `text_message_style{TextColor,
  ContextMessage}` (`[label]` after the name), `AddChatChannel` / `GetTextChannels`
  on `GetSimulationEntity[]`, 100 members. Verse cannot send or read messages.
  → `sys_text_chat`, template `team_text_chat`
- **Abilities are out of Experimental** (publishable): `ability_context.Instigator`
  and projectile `GetInstigator[]` are `entity` (cast `agent[...]`); `Ability.Use(...)`
  is `no_rollback` (never inside `if`); wedge `Angle` is in radians;
  `fort_self_ability_target_query`; open enums need `_ =>`. → scenegraph
  `custom_abilities`, `template_abilities`
- **Tag lookups**: `GetCreativeObjectsWithTag` and the tag-instance overload of
  `FindCreativeObjectsWithTag` are deprecated — pass the tag **type**. → `classes`

### 43.00 — quests publishable, health pipeline, subscribable events, timers

Read from the 43.00 digests (`++Fortnite+Release-43.00-CL-59596594`); every
snippet on the linked pages compiled in UEFN 43.00 (Nov 1 2026).

- **Events are subscribable**: `event(t)` now implements `listenable(t)`, so
  `MyEvent.Subscribe(Handler)` returns a `cancelable` (UMG event fields too). Delete
  any own `Subscribe` extension on `event` (ambiguous overload); `Await` loops keep
  working. `MakeProxyListenable(L)` wraps a listenable so callers can't cast it back.
  → `events_subscriptions`
- **Progression API is out of Experimental** (publishable) and was rewritten:
  `quest := class<abstract>(objective)`; `Quest.Join(Participant, Info)` / `Abandon`
  replace `JoinQuest` / `AbandonQuest`; `progress_objective` (`SetProgress`,
  `SetRequiredProgress`) replaces `progress_quest_objective`; `basic_quest`
  (`/UnrealEngine.com/Progression`) auto-completes and grants its `quest_reward`s;
  `fort_quest_collection` (`/Fortnite.com/Progression`) shows quests in the Fortnite
  quest UI. 42.x quest code does not compile on 43.00. → `sys_quests`
- **Health and damage pipeline** (Experimental — blocks publishing):
  `/UnrealEngine.com/HealthPipeline` (`health_component`, `health_pool_entry`,
  `damage_event` / `healing_event` sent with `entity.SendUp`,
  `health_adjustment_modifier`) and `/Fortnite.com/FortHealthPipeline` (`fort_health`,
  `fort_shield`, `fort_overshield` + their tags). Built-in weapon damage now hits Scene
  Graph entities. → `sys_health_pipeline`
- **Time**: the `clock` interface, global `SecondsSinceEpochClock`, experimental
  `playable` interface and experimental `timer` (count up or down, `PlayRate`).
  → `sys_rounds_timers`, `sys_time_tracking`
- **Language**: a field initializer may read a preceding `<final>` field (the offline
  LSP still flags it; the UEFN build accepts it); `Array.Last[]` / `Array.Last[N]`.
  → `classes`, `datatypes`
- **Name clash (3588):** a local named `Last` (or another new extension name) is ambiguous
  with `operator'.Last'` inside a class (fields and method locals); rename it (`PrevTime`,
  `LastLogin`). → `compile_errors`
- **Short forms** (not in the release notes; compiled on 43.00): `if. C then X`,
  `spawn. F()`, `array. X`, `option. X`, `F of type:` + an indented archetype block, an
  indented `array:` block = an array, and the `first(X : Xs) { X }` macro (`<decides>` on
  arrays, not failable on generators). → `syntax`
- **LSP lags the compiler**: the Problems panel flags every `listenable.Await()`, preceding
  `<final>` field init, and a 5th or 6th persistent `weak_map`. The UEFN build accepts all
  of these, so trust `workspace_compile_verse`. → `compile_errors`
- **Tags**: creative objects implement `has_tags` (`AddTag`, `ContainsTag[]`,
  `RemoveTag[]`); `tag_view`, `tag_search_criteria` and `GetTags` are deprecated.
  → `classes`
- **Modules**: modules holding reflected assets default to project-wide
  accessibility (new name clashes possible); max `weak_map` vars per module 4 → 6.
  → `modules`, `persistence`, `compile_errors`
- **Devices**: `fort_vehicle` fuel (`GetFuelRemaining`, `GetFuelCapacity`,
  `SetFuelRemaining`, `FuelUsageDriving/Boosting/Idle` + `SetFuelUsage*`);
  `teleporter_device` is `enableable` and teleports props (`Teleport(Prop)`,
  `Activate(Prop)`, `TeleportPropEvent`, `EnterPropEvent`); `SprintedEvent` fires on
  sprint input; `cinematic_sequence_device.GetSequenceLength`. → `devices`
- **UI / input**: Safe Zone widget in UMG; `PointerZoom` is publishable and touch
  pinch values are 50× larger (retune thresholds). → `umg_layout`, `virtualpointer`
- **Interactables**: `basic_interactable_component.OnStarted` now runs when a hold
  starts (not when it ends); on-completion logic belongs in `SucceededEvent`.
- **Scene Graph** (cameras in radians, `FieldOfView`, modifier layers, prefabs inherit
  their parent class, item templates no longer `<final>`): scenegraph pack.
