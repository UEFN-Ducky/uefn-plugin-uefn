---
description: "The Verse that lets a player talk to a persona NPC: agent_group + voice_channel + AddChatChannel on the simulation entity + SetConversationTarget; the smallest working npc_behavior; players who join late or leave; several talking NPCs (one conversation target per player, target the one they stand next to); shared history in one channel; cleanup"
metadata:
  order: 3
  label: "Conversations: who can talk to it"
  default_enabled: false
  load_condition: "A player cannot talk to a persona NPC, no talk prompt shows, players who join late cannot talk, several talking NPCs in one island, NPCs that should hear each other, or cleaning up a conversation"
---

## Who can talk to it

Three things must all be true before a player sees the talk prompt:

1. The NPC's agent and the player are members of the same **agent group**.
2. A **voice channel** built on that group is added to the **simulation entity**.
3. The player's **conversation target** is that NPC's persona, on that channel.

None of this can be set in the editor. It is always Verse, in the NPC's `npc_behavior`.

```
agent_group ── members: the NPC's agent + each player
     │
voice_channel{Group := that group} ── Sim.AddChatChannel(Channel)
     │
Player.SetConversationTarget(Persona, Channel)
```

Membership belongs to the group. A channel has no `AddMember`.

### The smallest behavior a player can talk to

Compiled against the installed build's digest. Put it on a definition that has a Persona Modifier (`setup`).

```verse
using { /Fortnite.com/AI }
using { /Fortnite.com/Playspaces }
using { /UnrealEngine.com/Conversations }
using { /Verse.org/AgentGroup }
using { /Verse.org/Chat }
using { /Verse.org/SceneGraph }
using { /Verse.org/Simulation }

# A voice channel needs a concrete member-info class.
talker_member<public> := class(has_voice_member_info){}

TalkerText<localizes>(Text:string):message = "{Text}"

talker_behavior<public> := class(npc_behavior):
    var MaybeGroup:?agent_group(talker_member) = false
    var MaybeChannel:?voice_channel(talker_member) = false
    var Cancels:[]cancelable = array{}

    OnBegin<override>()<suspends>:void =
        if:
            Entity := GetEntity[]
            NPCAgent := GetAgent[]
            Sim := Entity.GetSimulationEntity[]
            Playspace := Entity.GetPlayspaceForEntity[]
        then:
            Group := agent_group(talker_member){}
            Channel := voice_channel(talker_member){Name := TalkerText("Talk"), Group := Group}
            set MaybeGroup = option{Group}
            set MaybeChannel = option{Channel}
            Group.AddMember(NPCAgent, talker_member{CanBroadcast := true})
            Sim.AddChatChannel(Channel)
            for (Player : Playspace.GetPlayers()):
                AddPlayer(Player)
            set Cancels += array{Playspace.PlayerAddedEvent().Subscribe(AddPlayer)}
            set Cancels += array{Playspace.PlayerRemovedEvent().Subscribe(RemovePlayer)}

    AddPlayer(Player:player):void =
        if:
            Group := MaybeGroup?
            Channel := MaybeChannel?
            Persona := GetEntity[].GetComponent[persona_component]
        then:
            Group.AddMember(Player, talker_member{CanBroadcast := true})
            Player.SetConversationTarget(Persona, Channel)

    RemovePlayer(Player:player):void =
        Player.ClearConversationTarget()
        if (Group := MaybeGroup?):
            Group.RemoveMember(Player)

    OnEnd<override>():void =
        for (Cancel : Cancels):
            Cancel.Cancel()
        if (Entity := GetEntity[]):
            if (Playspace := Entity.GetPlayspaceForEntity[]):
                for (Player : Playspace.GetPlayers()):
                    Player.ClearConversationTarget()
            if (Sim := Entity.GetSimulationEntity[], Channel := MaybeChannel?):
                Sim.RemoveChatChannel(Channel)
```

What each line is for:

| Line | Without it |
|---|---|
| `Group.AddMember(NPCAgent, …)` | `PromptToTalk` fails: the persona is not in the channel |
| `Sim.AddChatChannel(Channel)` | The channel exists in Verse only; nobody is connected |
| `Group.AddMember(Player, …)` | The player's speech does not reach the NPC |
| `Player.SetConversationTarget(Persona, Channel)` | No talk prompt on that player's screen |
| `PlayerAddedEvent` | Players who join after the NPC spawned can never talk to it |
| `OnEnd` cleanup | A despawned NPC stays the player's target and its channel stays registered |

`GetPlayspace()` does not exist on `npc_behavior`: go through `GetEntity[]` → `GetPlayspaceForEntity[]`. `AddMember`, `RemoveMember`, `AddChatChannel` and `RemoveChatChannel` return a `result`; they are plain calls, not `[ ]` calls.

### Several talking NPCs

A player has **one** conversation target. If every NPC sets itself as the target in `OnBegin`, the last one to spawn wins and the others cannot be talked to. Give each NPC its own group and channel, and make a player a member only while they stand next to it:

```verse
using { /Fortnite.com/Characters }
using { /Verse.org/SpatialMath }

nearby_talker_behavior<public> := class(npc_behavior):
    @editable TalkRange:float = 500.0

    OnBegin<override>()<suspends>:void =
        if:
            Entity := GetEntity[]
            NPCAgent := GetAgent[]
            Persona := Entity.GetComponent[persona_component]
            Sim := Entity.GetSimulationEntity[]
        then:
            Group := agent_group(talker_member){}
            Channel := voice_channel(talker_member){Name := TalkerText("Talk"), Group := Group}
            Group.AddMember(NPCAgent, talker_member{CanBroadcast := true})
            Sim.AddChatChannel(Channel)
            # There is no event for "a player walked up", so check twice a second.
            loop:
                Sleep(0.5)
                if (Playspace := Entity.GetPlayspaceForEntity[]):
                    Here := Entity.GetGlobalTransform().Translation
                    for (Player : Playspace.GetPlayers(), There := Player.GetFortCharacter[].GetEntity[].GetGlobalTransform().Translation):
                        if (Distance(Here, There) <= TalkRange):
                            if (not Group.GetMemberMap()[Player]):
                                Group.AddMember(Player, talker_member{CanBroadcast := true})
                                Player.SetConversationTarget(Persona, Channel)
                        else if (Group.GetMemberMap()[Player]):
                            Group.RemoveMember(Player)
                            if (Player.GetConversationTarget[](0) = Persona):
                                Player.ClearConversationTarget()
```

Add the same cleanup as above. A player who walks from one NPC to the next is released by the first and claimed by the second.

### One channel or many

| Setup | Result |
|---|---|
| One channel, one NPC, all players | Everyone hears the NPC and it hears everyone. The usual shop, guide or host |
| One channel per NPC, players join by distance | Private talks; each NPC keeps its own history |
| Two personas in the **same** channel | Their sessions share history: each knows what was said to the other. Use it for a pair that plays off each other |

Players in a voice channel can also hear each other on it. A voice channel holds up to 80 members.

### What the player still needs

Voice chat on and, for a child's account, the AI permission (`setup`). Code cannot turn these on. If the prompt shows and no answer comes, subscribe to `PromptFailureEvent` and print which error it was (`verse_api`).

Next: `structured_output` (the game reacts to what was said), `behaviors` (it moves and speaks on its own).
