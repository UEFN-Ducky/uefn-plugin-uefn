---
source_plugin_id: uefn
name: conversations
description: "UEFN LLM conversations: AI-powered NPCs that talk to players by voice (Persona Modifier + persona_component). Where each thing is done: the persona, voice and name in the NPC Character Definition and Prompt Editor; who can talk to it, what it says about game events and how its words change the game (structured output) in Verse. Use for talking NPC, AI NPC, LLM, persona, voiced character, shopkeeper, quest giver that listens, haggling, password guard, narrator. Not the Conversation device (scripted dialog)."
license: MIT
metadata:
  label: "UEFN Conversations (AI NPCs that talk)"
  version: 1
  managed_by: uefn-ducky
  author: UEFN-Ducky
  copyright: Copyright 2026 Mindful Path Company, LLC
  allow_redistribute: true
---

# Conversations: AI NPCs that talk

A player holds the talk key and speaks. The NPC hears it, answers in character with a voice, remembers the session, and can hand your Verse code data about what was said so the game reacts.

Two parts make one talking NPC, and each has its own place:

- **The persona** (who it is): set in the editor, on the NPC Character Definition.
- **The behavior** (what it does in the game): written in Verse, in an `npc_behavior`.

## Where to do what

| You want | Where | Page |
|---|---|---|
| Who it is: personality, what it knows, how it talks | Editor: NPC Character Definition → **Persona Modifier** → Character Facts | `setup`, `persona_prompts` |
| Its voice, face animation, what happens when it is interrupted | Editor: Persona Modifier | `setup` |
| Its name on screen | Editor: **UI Modifier** → Display Name | `setup` |
| How it looks | Editor: Cosmetic modifier (a Fortnite character brings its own voice and personality) | `setup` |
| Try replies without starting a session | Editor: **Edit in Prompt Editor** | `setup` |
| Let players talk to it at all | Verse: group + voice channel + conversation target | `players_and_channels` |
| Players who join late, several talking NPCs | Verse | `players_and_channels` |
| Its words change the game (give an item, open a gate, close a deal) | Verse: **structured output** (`RegisterAction` + a struct) | `structured_output` |
| Ask it a silent question and get data back | Verse: `Session.Prompt` | `structured_output` |
| It speaks because of a game event (shot, timer, quest done) | Verse: `PromptToTalk` | `behaviors` |
| It stops walking and faces whoever talks | Verse: conversation events + `npc_actions_component` | `behaviors` |
| Captions, an animation while it talks | Verse: say events | `behaviors` |
| Who it is changes mid-game | Verse: `SetPersonality` | `behaviors` |
| Every name and signature | The digest; summary here | `verse_api` |

Nothing about the persona is written in Verse unless it has to change while the game runs. Text in the editor can be tested in the Prompt Editor in seconds; text in Verse needs a session.

## Build one, in order

1. **Definition:** an NPC Character Definition of the Custom character type, with a Persona Modifier and a UI Modifier (`setup`).
2. **Persona:** write the personality, pick the voice, and test replies in the Prompt Editor until it sounds right (`persona_prompts`).
3. **Behavior:** `verse_template_apply("llm_npc_shopkeeper")` (wanders, faces the speaker, hands out items, reacts to being shot) or `verse_template_apply("llm_npc")` (haggling, a silent question, captions). Change the struct and what the callback does for your game.
4. **Compile:** `workspace_compile_verse`, then set the class as the definition's Verse Behavior (`set_npc_definition_behavior`). A persona with no Verse behavior cannot be talked to.
5. **Place:** drag the definition into the level. It places an NPC Spawner.
6. **Play:** start a session with voice chat on, walk up, hold the key shown on screen and talk.
7. **Check each part:** the talk prompt shows, it answers, the game reacts, a second player can talk too.

## How one exchange runs

1. The player holds the talk key: `StartHearEvent`, then `StopHearEvent` when they let go.
2. The speech goes to the model with the personality and the session's history. The reply text comes back with any structured output.
3. The NPC starts to speak: `StartSayEvent`. The line passes moderation: `CommitSayEvent` carries the final text. The voice ends: `StopSayEvent`.
4. If the reply fails (rate limit, timeout, moderation): `PromptFailureEvent`. Never count on a `StopSayEvent` after a failure.

The model only knows what the personality, the history and your prompts tell it. It does not see the level, the score or the player's inventory unless you say so in text.

## When it does not work

| What you see | Cause |
|---|---|
| No talk prompt on screen | The player has no conversation target, the player or the NPC is not in the channel's group, the channel was not added to the simulation entity, or the definition has no Verse behavior |
| The prompt shows, it never answers | Voice chat is off, the account's AI permission is off, or the reply failed: subscribe to `PromptFailureEvent` and read the error type |
| It answers, the game does not react | No `RegisterAction`, or `Required` is false and the description never fits, or the callback waits for a `StopSayEvent` that never came |
| The callback runs twice per reply | `RegisterAction` was called once per player. Register once per NPC |
| It walks off while a player talks | Nothing stops navigation on `StartHearEvent` (`behaviors`) |
| It stands still forever | The code waits on `StopSayEvent` alone and the reply failed. Race it with `PromptFailureEvent` and a time limit |
| With two talking NPCs only one can be talked to | A player has one conversation target. Set it to the NPC they stand next to (`players_and_channels`) |
| `SetPersonality` or `PromptToTalk` does not compile | Both can fail: call them with `[ ]` inside an `if` |
| Error 3512 on a `[ ]` call | A `<localizes>` message was built inside it. Build the message on the line above |
| Error 3506 unknown name | `AppendToPersonality`, `RegisterPromptBinding`, `ResponseType` and `voice_channel.AddMember` do not exist (`verse_api`) |

## Hard rules (every UEFN skill)

1. **Our architecture is the spine** — systems are our packs on `player_manager`; never a second registry, wallet or save table (verse `sys_architecture`).
2. **Scene Graph, always** — anything created, moved, shown, hidden or animated at runtime is an entity / Entity Prefab; Creative devices only for features Fortnite provides; `creative_prop` only for Fortnite physics props (`physics` skill), never moved or hidden from Verse (scenegraph SKILL.md).
3. **Motion is keyframed, always — no `MoveTo`, ever** — every runtime move of an entity (door, lift, platform, spin, bob, projectile, one glide, a chaser, a pet) is `keyframed_movement_component`: `SetKeyframes`, then `Play()`. Never a transform or `TeleportTo` written in a loop. Place once with `SetGlobalTransform`; follow with `SetOrigin`; carry a player on a keyframed platform they stand on; characters use animation assets (scenegraph `movement_transforms`).
4. **No lag** — events over polling, every loop waits, visuals ~10 Hz, pools, shared materials, HUD and saves on change (verse `runtime_pitfalls`).
5. **Everything stops when its owner goes** — stop events on leave and elimination, `defer` cleanup (verse `async`).
6. **One house code style** (verse `code_style`).
7. **Names come from the digest of the installed build** (verse `digests`). The digest wins over every skill page: after a Fortnite update, or when a name does not compile, call `verse_digest_changes()`; an `@experimental` line above a name means it blocks publishing.
8. **Done means played** — build, then one live run; two players for multiplayer (verse `runtime_pitfalls`).

An NPC walks with `npc_actions_component` (`NavigateTo`): that is the character's own movement, not an entity move, so rule 3 does not apply to it. Event lines (`PromptToTalk`) always have a cooldown (rule 4). Every subscription and `RegisterAction` is cancelled in `OnEnd` (rule 5).

## Limits to tell the person

- Replies are in English only.
- Players need voice chat on. A child's account needs the parental control for AI features turned on.
- One persona per character definition. Not available on brand islands.
- Epic's rules (Developer Rule 1.22): no medical or mental-health advice persona, no romantic companion, no working around the safety layer. Never tell players their voice is recorded or stored; it is not.

## Subskill map

| Want | Load |
|---|---|
| Create the definition, add the Persona Modifier, voice, name, Prompt Editor, spawner | `setup` |
| Write a personality that behaves, with examples | `persona_prompts` |
| Group, voice channel, conversation target, late joiners, several NPCs | `players_and_channels` |
| Struct fields, `RegisterAction`, `Session.Prompt`, patterns for game mechanics | `structured_output` |
| Speak on game events, stop and face the speaker, animation, captions, changing personality | `behaviors` |
| Every type, member, event and error from the digest | `verse_api` |

Related: `skill_read_subskill("verse", "sys_npc_ai")` (movement and combat behaviors), `skill_read_subskill("verse", "sys_chat_channels")` (voice channels), `skill_read_subskill("npc-ai", "character_definitions")` and `skill_read_subskill("animation", "npc_characters")` (building the character).
