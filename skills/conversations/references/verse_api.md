---
description: "The Conversations Verse API as the installed build's digest has it (/UnrealEngine.com/Conversations): persona_component members and events, ai_session (Prompt, RegisterAction, ClearHistory), prompt_binding_definition, @ai_description, player conversation target functions, voice classes, ai_error types, the modules to import, and names that do not exist"
metadata:
  order: 6
  label: "Conversations: Verse API"
  default_enabled: false
  load_condition: "Looking up a Conversations type, member, event, error or voice class; a compile error on a persona or ai_session name; which modules to import for a talking NPC"
---

## Conversations Verse API

Read the live version with `get_verse_api("Conversations")`. This page is a summary of the digest of the build it was written against; the digest wins (rule 7). After a Fortnite update call `verse_digest_changes("Conversations")`.

### Imports

```verse
using { /UnrealEngine.com/Conversations }   # persona_component, ai_session, prompt_binding_definition, voices, errors
using { /Verse.org/Chat }                   # voice_channel, has_voice_member_info, AddChatChannel
using { /Verse.org/AgentGroup }             # agent_group
using { /Verse.org/SceneGraph }             # GetComponent, entity
using { /Verse.org/Simulation }             # player, agent, cancelable
using { /Fortnite.com/AI }                  # npc_behavior, npc_actions_component
using { /Fortnite.com/Playspaces }          # GetPlayspaceForEntity, PlayerAddedEvent
```

### `persona_component`

The Persona Modifier adds it to the spawned NPC's entity: `GetEntity[].GetComponent[persona_component]`.

| Member | Notes |
|---|---|
| `Personality:message` | Read only. Change with `SetPersonality` |
| `SetPersonality(New:message)<transacts><decides>` | Replaces the whole text. `[ ]` call |
| `Voice:voice_model` / `SetVoice(New:voice_model)<transacts><decides>` | `[ ]` call |
| `var PromptInterruptionRule:persona_interruption_rule` | `IgnoreUntilFinished`, `InterruptOnPromptStart`, `InterruptOnResponseStart` |
| `GetAISession()<transacts>:ai_session` | History, silent prompts, structured output |
| `PromptToTalk(Instructions:message, Channel)<transacts><decides>` | Speak about something. Fails when the interruption rule blocks it or the persona is not in a channel |
| `PromptToTalk(Instructions, Rule, Channel)<transacts><decides>` | Same, with the interruption rule for this one line |
| `StartHearEvent`, `StopHearEvent` | `listenable(agent)` |
| `StartSayEvent` | `listenable(tuple(?agent, cancelable))`, before moderation |
| `CommitSayEvent` | `listenable(tuple(?agent, message))`, the final text |
| `StopSayEvent` | `listenable(logic)`, true when interrupted |
| `PromptFailureEvent` | `listenable(ai_error)` |

Personas in the same voice channel share conversation history between their sessions.

### `ai_session`

| Member | Notes |
|---|---|
| `ClearHistory()<transacts>` | Forget what was said |
| `Prompt(Prompt:message, response_type)<suspends>:result(response_type, ai_error)` | A silent question; the answer is your struct |
| `RegisterAction(Definition:prompt_binding_definition, Required:logic, output_type, Callback)<transacts>:cancelable` | Side output the model sends with a reply. `Required := true`: with every reply |

`prompt_binding_definition := struct{Name:message, Description:message}`: what the model reads to decide when to send the output.

`@ai_description("…")` goes above each field of an output struct. Allowed field types: numbers, `logic`, enums, `message`, agents, and structs or arrays of those.

Read a `result`: `if (Value := Reply.GetSuccess[])`, `if (Error := Reply.GetError[])`.

### Player functions

| Function | Notes |
|---|---|
| `Player.SetConversationTarget(Persona, Channel)<transacts>` | The persona this player talks to with the talk key. The persona must be in that channel with the player |
| `Player.GetConversationTarget[]` | `tuple(persona_component, voice_channel(…))`; fails when there is none |
| `Player.ClearConversationTarget()<transacts>` | The player can no longer prompt a persona |

### Group and channel (`/Verse.org/AgentGroup`, `/Verse.org/Chat`)

| Call | Notes |
|---|---|
| `agent_group(member_class){}` | Holds the members. `AddMember(Agent, Info)`, `RemoveMember(Agent)`, `GetMemberMap()` |
| `voice_channel(member_class){Name := …, Group := Group}` | The channel on that group. `Enable()`, `Disable()` |
| `Sim.AddChatChannel(Channel)` / `Sim.RemoveChatChannel(Channel)` | On the simulation entity. Return a `result` |
| `class(has_voice_member_info){}` | The member class. `CanBroadcast:logic` |

More on channels: verse `sys_chat_channels`.

### Errors

`ai_error` (`.Message:message`) and its subclasses `ai_timeout_error`, `ai_throttled_error`, `ai_moderated_error`, `ai_character_limit_error`. Test with a cast: `if (ai_throttled_error[Error])`.

| Error | Meaning | Do |
|---|---|---|
| `ai_throttled_error` | Too many requests | Slow down event lines; retry later |
| `ai_timeout_error` | No answer in time | Let the player try again |
| `ai_moderated_error` | The line was blocked and replaced | Nothing; reword the personality if it happens often |
| `ai_character_limit_error` | Text too long | Shorten the personality or the instruction |

### Voices

Each voice is a class under `voice_model`, used as `Persona.SetVoice[guild_voice{}]`. The digest lists them with a short description of the sound. A class marked `<epic_internal>` belongs to a locked Fortnite character and cannot be constructed in your code; pick those in the Persona Modifier with the matching character.

### Names that do not exist

Each of these is error 3506. Older tutorials use them.

| Do not write | Write |
|---|---|
| `Persona.AppendToPersonality(…)` | `Persona.SetPersonality[Join(array{Persona.Personality, Extra}, Separator)]` |
| `Session.RegisterPromptBinding(Def, F)` | `Session.RegisterAction(Def, Required, struct_type, F)` |
| `prompt_binding_definition{…, ResponseType := T}` | `prompt_binding_definition{Name := …, Description := …}`; the struct type is `RegisterAction`'s third argument |
| `Channel.AddMember(…)` | `Group.AddMember(…)` on the channel's `agent_group` |
| A `text_channel` for typed conversations | `PromptToTalk` and `SetConversationTarget` take a `voice_channel` |
| `GetPlayspace()` in an `npc_behavior` | `GetEntity[].GetPlayspaceForEntity[]` |

Ducky's Verse lint flags the old persona names.
