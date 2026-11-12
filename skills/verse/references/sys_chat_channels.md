---
description: "Chat channels (/Verse.org/Chat) — the shared model (chat_channel, agent_group membership, AddChatChannel on the simulation entity) and voice channels: voice_channel, mute/cut comms, IsMemberSpeaking + Begin/EndBroadcastEvent. Text channels → sys_text_chat"
metadata:
  order: 14
  label: "Chat channels / voice"
  default_enabled: false
  load_condition: "Voice chat channels, squad comms, muting a team, cutting comms, detecting who is speaking, custom Game Voice Chat, or how voice and text chat channels fit together"
---

## Chat channels — Channel API

> Conversations (AI NPCs that talk) use the same `agent_group` + `voice_channel`, plus `Player.SetConversationTarget(Persona, Channel)`: `skill_read_subskill("conversations", "players_and_channels")`.

Custom **voice** groups so players hear only who you put in the channel, and so
you can mute, cut comms, or react when someone talks. Everything below is
verified against the `Verse.digest.verse` `/Verse.org/Chat` module and
re-checked.

**HARD:** use this API. Never invent `IsSpeaking`, a custom “radio” device, or a
HUD-only mute. **Text chat** has its own channel class,
`text_channel` — `sys_text_chat` (template `team_text_chat`). Island Settings
`VoiceChat` / `TextChatScope` is the *session default* — per-group control is
`voice_channel` / `text_channel`.

```verse
using { /Verse.org/Chat }           # voice_channel, AddChatChannel, has_voice_member_info
using { /Verse.org/AgentGroup }     # agent_group
using { /Verse.org/Simulation }
using { /Fortnite.com/Devices }     # GetSimulationEntity on creative_device
```

`@available` floors differ per type (read them in the digest)
(`IsMemberSpeaking`, `BeginBroadcastEvent`, `EndBroadcastEvent`,
`CanBroadcastChangeEvent`). Uploads older than older-build will not compile the
speaking APIs.

### Digest map

| Symbol | Kind | Notes |
|--------|------|-------|
| `chat_channel` | abstract `<internal>` | Do not construct. `Name : message`, `Group : agent_group_interface`, `Enable` / `Disable` / `IsEnabled` |
| `has_voice_member_info` | interface | `var CanBroadcast : logic` — false = hear-only (still in overlay) |
| `voice_channel(member_info)` | `class<final>(chat_channel)` | Concrete channel. Cap **80** members of `Group` |
| `IsMemberSpeaking(Agent)` | `<decides><reads>` | Fails if not a member or not talking. **Not** `IsSpeaking` |
| `BeginBroadcastEvent()` | `listenable(agent)` | Started talking |
| `EndBroadcastEvent()` | `listenable(agent)` | Stopped talking |
| `CanBroadcastChangeEvent()` | `listenable(tuple(agent, logic))` | Mute flag flipped while they hold a slot |
| `AddChatChannel` | on **simulation entity** | `Sim.AddChatChannel(Channel) : result(void, add_channel_error)` |
| `RemoveChatChannel` | same | deregister |
| `GetVoiceChannels()` | on sim entity | `[]voice_channel(has_voice_member_info)` |
| `text_channel(member_info)` | `class<final>(chat_channel)` | Text chat, cap **100**, `has_text_member_info` (`CanSend`, `MessageStyle`) — `sys_text_chat` |
| `GetTextChannels()` | on sim entity | `[]text_channel(has_text_member_info)` |

`AddChatChannel` fails when the group already has more members than the channel
type allows (voice 80, text 100). One member class can implement both
`has_voice_member_info` and `has_text_member_info`, so one `agent_group` drives a
voice and a text channel (recipe in `sys_text_chat`).

Get the sim entity from a placed `creative_device`: `GetSimulationEntity[]`
(`<transacts><decides>`).

### Member info + group + channel

`has_voice_member_info` is an **interface** — you supply a concrete class, then
an `agent_group` of that type, then the matching `voice_channel`:

```verse
voice_member <public> := class(has_voice_member_info):
    var CanBroadcast<override> : logic = true

ChannelName<localizes>(S : string) : message = "{S}"

# OnBegin of a creative_device:
if (Sim := GetSimulationEntity[]):
    Group := agent_group(voice_member){}
    Chan := voice_channel(voice_member){ Name := ChannelName("Squad"), Group := Group }
    Sim.AddChatChannel(Chan)
    Chan.BeginBroadcastEvent().Subscribe(OnStartedTalking)
    Chan.EndBroadcastEvent().Subscribe(OnStoppedTalking)
```

Membership is the **group**, not a channel-side AddPlayer:

```verse
JoinSquad(Agent : agent, Group : agent_group(voice_member)) : void =
    Group.AddMember(Agent, voice_member{ CanBroadcast := true })

Mute(Agent : agent, Group : agent_group(voice_member)) : void =
    if (Info := Group.GetMemberMap()[Agent]):
        set Info.CanBroadcast = false

# Cut the whole channel (squad split, round end, dramatic silence):
CutComms(Chan : voice_channel(voice_member)) : void =
    Chan.Disable()

# Guard hears talking:
OnStartedTalking(Agent : agent) : void =
    Print("speaking")
```

`IsMemberSpeaking` is `<decides>`:

```verse
if (Chan.IsMemberSpeaking[Agent]):
    AlertGuard()
```

Parental controls / user settings can still block voice even when
`CanBroadcast` is true. Agents beyond the 80 cap are **not** in chat.

### Do not

| Invent | Use |
|--------|-----|
| `IsSpeaking` / `OnSpeak` | `IsMemberSpeaking` / `BeginBroadcastEvent` |
| "Verse has no text chat" | `text_channel` — `sys_text_chat` |
| Custom radio / HUD mute as the comms system | `voice_channel` Enable/Disable + `CanBroadcast` |
| `AddChatChannel` on the player/agent | `GetSimulationEntity[]` then `AddChatChannel` |
