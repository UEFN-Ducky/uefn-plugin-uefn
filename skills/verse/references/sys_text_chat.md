---
description: "Text chat channels (v42.40) — /Verse.org/Chat text_channel: team / faction / role chat, has_text_member_info CanSend (read-only) and a per-member MessageStyle, text_message_style colors + [context] labels, SystemMessageColor, AddChatChannel / RemoveChatChannel / GetTextChannels, the 100-member cap, one group for voice + text; Verse cannot send or read messages"
metadata:
  order: 14
  label: "Text chat channels (v42.40)"
  default_enabled: false
  load_condition: "Custom text chat: team / faction / role chat, who can type, read-only or muted players, chat colors or [labels] after names, system message color, listing text channels, or voice and text chat for the same group"
---

## Text chat channels (v42.40)

`text_channel` lets Verse put players into their own text chat channels, decide who
may type, and color and label their messages. Everything on this page is from the
42.40 `Verse.digest.verse` `/Verse.org/Chat` module and **compiled with 0 errors,
0 warnings in UEFN 42.40** (ExampleProject1, Oct 16 2026). Ready-made device:
`verse_template_apply("team_text_chat")`. Voice channels and the shared model:
`sys_chat_channels`.

**What Verse can and can't do.** It controls *channels*: membership, who may type,
how messages look, on/off. It **cannot** send a message, read what players type,
filter words, or react to a message — there is no message API and no message event
(voice channels have speaking events; text channels have none). LLM NPC
conversations take a `voice_channel` only (`sys_conversations`).

```verse
using { /Verse.org/Chat }         # text_channel, has_text_member_info, text_message_style
using { /Verse.org/AgentGroup }   # agent_group
using { /Verse.org/Colors }       # color, NamedColors, MakeColorFromHex
using { /Verse.org/Simulation }
using { /Fortnite.com/Devices }   # GetSimulationEntity on creative_device
```

`@available {MinUploadedAtFNVersion := 4240}` on every text type: an island uploaded
before 42.40 cannot use them. `AddChatChannel` / `RemoveChatChannel` are older (4000).

### API map (42.40 digest)

| Symbol | Kind | What it is |
| --- | --- | --- |
| `text_channel(member_info)` | `class<final>(chat_channel)` | The channel. Inherited `Name : message`, `Group : agent_group_interface(member_info)`. Own: `var SystemMessageColor : color`, `var MessageStyle : text_message_style`, `Enable()`, `Disable()`, `IsEnabled[]` |
| `has_text_member_info` | interface you implement | `var CanSend : logic` — `false` = read-only (still sees users and messages). `var MessageStyle : ?text_message_style` — this player's own style; `false` = use the channel's |
| `text_message_style` | `class<concrete>` | `TextColor : color`, `ContextMessage : ?message` — shown in square brackets after the name: `Jonesy [Tilted Towers]: gg`. Fields are not `var`: build a new style to change one |
| `(Entity).AddChatChannel(Channel)` | on any entity in the simulation | `result(void, add_channel_error)`. Fails if the channel's group already has more than **100** members |
| `(Entity).RemoveChatChannel(Channel)` | same | `result(void, remove_channel_error)` |
| `(Entity).GetTextChannels()` | `<reads>` | `[]text_channel(has_text_member_info)` — every text channel registered in the simulation |

How it behaves (Epic, digest comments): a player can be in several text channels;
members past 100 are left out of the chat; parental controls and the player's own
settings can still block chat; a style change only affects **new** messages;
`SystemMessageColor` colors lines like "Now chatting in Team Red." and "You cannot
write in …". Island Settings `TextChatScope` stays the session default
(`islandsettings`); custom channels are added on top.

### Recipe — a team channel

```verse
team_text_member := class(has_text_member_info):
    var CanSend<override>:logic = true
    var MessageStyle<override>:?text_message_style = false

ChatText<localizes>(S:string):message = "{S}"

team_chat_device := class(creative_device):
    var MaybeRed:?text_channel(team_text_member) = false
    var MaybeRedGroup:?agent_group(team_text_member) = false

    OnBegin<override>()<suspends>:void =
        if (Sim := GetSimulationEntity[]):
            RedGroup := agent_group(team_text_member){}
            Label := ChatText("Red")                    # build messages first
            Red := text_channel(team_text_member):
                Name := ChatText("Team Red")
                Group := RedGroup
                MessageStyle := text_message_style{TextColor := NamedColors.Red, ContextMessage := option{Label}}
                SystemMessageColor := NamedColors.Yellow
            AddResult := Sim.AddChatChannel(Red)        # no_rollback: outside any if
            if (AddResult.GetSuccess[]):
                set MaybeRed = option{Red}
                set MaybeRedGroup = option{RedGroup}
                for (Player : GetPlayspace().GetPlayers()):
                    RedGroup.AddMember(Player, team_text_member{})
```

- Membership **is the group**: `Group.AddMember(Agent, team_text_member{})` /
  `Group.RemoveMember(Agent)` (both `<transacts>`, both return a `result`). There is no
  channel-side `AddPlayer`.
- `SystemMessageColor` and `MessageStyle` have defaults — leave them out for Fortnite's
  look. A member class that overrides nothing also works:
  `lobby_member := class(has_text_member_info){}`.
- `Name` is a `message`. Call `<localizes>` functions before building `option{…}` or
  calling a `[ ]` function (E3512 otherwise).
- `AddChatChannel` is not `<transacts>`: call it on its own line, then test the result
  with `GetSuccess[]` / `GetError[]`.

### Read-only, labels, restyle, off, remove

Methods to add to `team_chat_device`:

```verse
    # Methods on team_chat_device (above).
    # Read-only for one player (muted, spectator, dead).
    MakeReadOnly(Agent:agent):void =
        if (Group := MaybeRedGroup?, Info := Group.GetMemberMap()[Agent]):
            set Info.CanSend = false

    # A [Captain] label and gold text for one player; set it back to false to undo.
    MakeCaptain(Agent:agent):void =
        if (Group := MaybeRedGroup?, Info := Group.GetMemberMap()[Agent]):
            Label := ChatText("Captain")
            set Info.MessageStyle = option{text_message_style{TextColor := NamedColors.Gold, ContextMessage := option{Label}}}

    Restyle():void =
        if (Red := MaybeRed?):
            set Red.MessageStyle = text_message_style{TextColor := MakeColorFromHex("#FF5050")}
            set Red.SystemMessageColor = NamedColors.White

    Silence():void =
        if (Red := MaybeRed?):
            Red.Disable()            # Enable() turns it back on; IsEnabled[] tests it

    Unregister():void =
        if (Sim := GetSimulationEntity[], Red := MaybeRed?):
            Sim.RemoveChatChannel(Red)
```

`Sim.GetTextChannels()` lists every registered text channel (also ones another device
made), typed with the base `has_text_member_info`.

### Voice and text for the same group

One member class can implement both interfaces, so one `agent_group` drives a voice
channel and a text channel (compiled 42.40):

```verse
squad_member := class(has_voice_member_info, has_text_member_info):
    var CanBroadcast<override>:logic = true
    var CanSend<override>:logic = true
    var MessageStyle<override>:?text_message_style = false

# in OnBegin, with Sim := GetSimulationEntity[]
SquadGroup := agent_group(squad_member){}
Voice := voice_channel(squad_member){Name := ChatText("Squad voice"), Group := SquadGroup}
Text := text_channel(squad_member){Name := ChatText("Squad"), Group := SquadGroup}
Sim.AddChatChannel(Voice)
Sim.AddChatChannel(Text)
```

Remember the caps differ: voice 80, text 100.

### Not verified live

Compiling proves the API; how the in-game chat widget lists custom channels next to
the `TextChatScope` default and how a player switches channel were not checked in a
session. Say so if the user asks, and test in a session before promising a look.

### Do not

| Wrong | Right |
| --- | --- |
| "Verse can't do text chat" / a HUD-only chat | `text_channel` (42.40) |
| Sending, reading, filtering or logging messages from Verse | Not possible — no message API or event |
| `Channel.AddMember(...)` | `Group.AddMember(Agent, member{})` |
| `AddChatChannel` on a player | on `GetSimulationEntity[]` (any entity in the simulation) |
| `if (Sim.AddChatChannel(C).GetSuccess[])` | `R := Sim.AddChatChannel(C)` then `if (R.GetSuccess[])` |
| `set Style.TextColor = …` | build a new `text_message_style{…}` and set the channel's or member's `MessageStyle` |
| `text_channel` with `SetConversationTarget` / `PromptToTalk` | voice channels only |
