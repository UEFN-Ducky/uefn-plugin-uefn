---
description: "What changed in Verse per Fortnite release (42.20, 42.30, 42.40, 43.00) — chat channels, Unarmed, marketplace, LLM NPCs, ability templates, held items, UMG event fields, text chat, abilities out of Experimental, subscribable events — and the names that do not exist"
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
  `Helper.SubscribeToEvent`); `.Subscribe` on an `event` fails until 43.00. The field
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

### 43.00 — subscribable events

- `event(t)` becomes subscribable. Never write your own `Subscribe` extension on
  events (it becomes an ambiguous overload); `Await` loops keep working.
  → `events_subscriptions`
