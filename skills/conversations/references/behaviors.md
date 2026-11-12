---
description: "How a talking NPC behaves around a conversation: the conversation events and what each is for, stop walking and face the speaker (race pattern), speaking first and speaking on game events with PromptToTalk, a cooldown, never waiting on StopSayEvent alone, an animation while it talks, holding still, interruption rules, captions, changing the personality mid-game with Join + SetPersonality, clearing history, an intro camera"
metadata:
  order: 5
  label: "Conversations: how it behaves"
  default_enabled: false
  load_condition: "A talking NPC that should greet players, react to being shot or to a game event, stop and look at the player who talks, play an animation or show captions while it speaks, change its personality during the game, or one that walks away or freezes during a conversation"
---

## How it behaves around a conversation

The persona is a voice and a mind. The body is still a normal NPC: it walks with `npc_actions_component`, plays clips with the play-animation controller, and takes damage as a `fort_character`. The **conversation events** tie the two together.

### The conversation events

All on `persona_component`. Subscribe (keep the `cancelable`) or `Await()` them.

| Event | Fires when | Carries | Use it to |
|---|---|---|---|
| `StartHearEvent` | A player starts talking to it | the `agent` | Stop walking, turn to them, remember who spoke |
| `StopHearEvent` | The player stops talking | the `agent` | Show a "thinking" pose |
| `StartSayEvent` | It begins to speak, before moderation | `(?agent, cancelable)`: who caused the line, and a handle that silences it | Start a talk animation; cancel a line you do not want |
| `CommitSayEvent` | The final, moderated text is known | `(?agent, message)` | Captions |
| `StopSayEvent` | The voice ends | `logic`, true when it was interrupted | Go back to walking, apply a pending result, hide captions |
| `PromptFailureEvent` | A reply failed | `ai_error` | Recover; log which error |

**Never wait on `StopSayEvent` alone.** After a failed reply it may never come. Race it with `PromptFailureEvent` and a time limit.

### Stop and face whoever talks

Walk until someone speaks, then stand and look at them until the line is over. Two races, in a loop:

```verse
WanderAndListen(Entity:entity, Persona:persona_component)<suspends>:void =
    if (Actions := Entity.GetComponent[npc_actions_component]):
        Home := Entity.GetGlobalTransform().Translation
        loop:
            # Walk until a player starts talking, or the NPC starts a line of its own.
            Listener:?agent = race:
                block:
                    Wander(Actions, Home)
                    false
                block:
                    Heard := Persona.StartHearEvent.Await()
                    option{Heard}
                block:
                    Persona.StartSayEvent.Await()(0)
            Actions.StopNavigation()
            # Stand and face them until the line ends. A failed reply never ends: the other arms cover that.
            race:
                FaceListener(Actions, Listener)
                AwaitLineEnd(Persona)
                Sleep(MaxTalkSeconds)

Wander(Actions:npc_actions_component, Home:vector3)<suspends>:void =
    loop:
        Sleep(GetRandomFloat(3.0, 5.0))
        Spot := vector3:
            Left := Home.Left + GetRandomFloat(-WanderRadius, WanderRadius)
            Up := Home.Up
            Forward := Home.Forward + GetRandomFloat(-WanderRadius, WanderRadius)
        Actions.NavigateTo(MakeNavigationTarget(Spot), ?MovementType := movement_type.Walking)

# Focus with LockFocus never ends by itself: it is always raced.
FaceListener(Actions:npc_actions_component, Listener:?agent)<suspends>:void =
    if (Speaker := Listener?, Target := Speaker.GetFortCharacter[].GetEntity[]):
        Actions.Focus(Target, ?LockFocus := true)
    else:
        Sleep(Inf)

AwaitLineEnd(Persona:persona_component)<suspends>:void =
    race:
        block:
            Persona.StopSayEvent.Await()
            false
        block:
            Persona.PromptFailureEvent.Await()
            false
```

Why it is built this way:

- `race` cancels the losing arms, so the walk stops being planned the moment someone speaks. `StopNavigation()` stops the step already under way.
- The wander spot is the home position **plus** a random offset. A spot built from the offset alone sends the NPC toward the world origin.
- `Await()` cannot sit inside `option{…}`: bind it on its own line first.
- These vectors are `/Verse.org/SpatialMath` (`Left`, `Up`, `Forward`). Keep `/UnrealEngine.com/Temporary/SpatialMath` out of the same file.

This is in the template `llm_npc_shopkeeper`. Movement, chasing and combat: verse `sys_npc_ai`.

### It speaks first, or about what happens

`PromptToTalk[Instructions, Channel]` tells the persona what to talk *about*; it writes the line itself. It can fail (busy and not allowed to be interrupted, or not in the channel), so it is a `[ ]` call inside an `if`.

```verse
OnDamaged(Result:damage_result):void =
    spawn{ComplainAboutShot()}

# A line caused by the game, not by a player's voice. At most one every 10 seconds.
ComplainAboutShot()<suspends>:void =
    if (ShotLineReady?):
        set ShotLineReady = false
        Line := ShopkeeperText("A player just shot you. Tell them in one short sentence to stop.")
        if (Persona := GetEntity[].GetComponent[persona_component], Channel := MaybeChannel?):
            if (Persona.PromptToTalk[Line, Channel]) {}
        Sleep(10.0)
        set ShotLineReady = true
```

Subscribe with `Char.DamagedEvent().Subscribe(OnDamaged)` on the NPC's own `fort_character` (`using { /Fortnite.com/Game }` for `damage_result`).

| Moment | Instruction to give |
|---|---|
| A player arrives | "Greet the player who just walked in." (after their conversation target is set) |
| It is shot | "A player just shot you. Tell them in one short sentence to stop." |
| A quest is done | "The player brought the three crystals. Thank them and tell them the gate is open." |
| Time is running out | "One minute is left. Warn the player." |

Rules for event lines:

- **Always a cooldown.** Events like damage fire many times a second; each prompt costs a model call and can be rate limited.
- Write the instruction as a fact plus what to do, in plain words. Put any number or name the line needs into the instruction: the model does not see the game.
- To override the interruption rule for one line: `PromptToTalk[Line, persona_interruption_rule.InterruptOnPromptStart, Channel]`.
- For an exact sentence, add "Say only this, nothing else."

### Interruption rule

`set Persona.PromptInterruptionRule = …` (or the Persona Modifier in the editor):

| Rule | Feels like |
|---|---|
| `IgnoreUntilFinished` | A narrator or announcer: finishes every line |
| `InterruptOnPromptStart` | A person: stops the moment you talk |
| `InterruptOnResponseStart` | Keeps talking until the next reply is ready, then switches |

### An animation while it talks

A clip does not loop by itself: ask for many plays and stop it when the line ends.

```verse
using { /Fortnite.com/Animation/PlayAnimation }
using { /Verse.org/Assets }

lively_behavior<public> := class(npc_behavior):
    @editable TalkAnimation:?animation_sequence = false

    OnBegin<override>()<suspends>:void =
        if:
            Persona := GetEntity[].GetComponent[persona_component]
            Anim := GetAgent[].GetFortCharacter[].GetPlayAnimationController[]
            Clip := TalkAnimation?
        then:
            loop:
                Persona.StartSayEvent.Await()
                Playing := Anim.Play(Clip, ?PlayCount := 100.0, ?BlendInTime := 0.3, ?BlendOutTime := 0.3)
                Persona.StopSayEvent.Await()
                Playing.Stop()
```

A one-off move on request (a dance, a bow) is a structured-output field plus `Anim.PlayAndAwait(Clip)` in a spawned function. To keep the body from walking during it, `Char.PutInStasis(stasis_args{})` before and `Char.ReleaseFromStasis()` after. Importing and retargeting clips: `animation` skill. After importing a clip, compile once so Verse can see it.

### Captions

`CommitSayEvent` gives the final text as a `message`; `StopSayEvent` says when to hide it. Put two Verse fields on a UMG widget (a `message` for the text, a `logic` for visibility), set them from the two events (verse `umg_verse_fields`). Captions help every player and are needed by players who cannot hear.

### Changing who it is during the game

The editor text is the start. `SetPersonality` replaces the whole text, so to add to it, join the old text with the new:

```verse
# Add to who it is while the game runs (a betrayal, a new order, a secret it just learned).
AddToPersonality(Persona:persona_component, Extra:message):void =
    NewPersonality := Join(array{Persona.Personality, Extra}, TalkerText("\n"))
    if (Persona.SetPersonality[NewPersonality]) {}
```

Use it for facts only known at runtime (today's stock, the player's quest state, a random budget) and for turns in the story (it becomes hostile, it learns the code). `Session.ClearHistory()` wipes what was said so far: use it between rounds so a new player does not inherit the last one's conversation.

### An intro camera

To show the NPC's face while it greets a player, add a camera to that player's camera director for the length of the line and cancel it on `StopSayEvent` (scenegraph `cameras`). Check the digest first: when this page was written the camera director carried `@experimental`, which blocks publishing.

The examples compile against the installed build's digest. `ShopkeeperText`, `TalkerText`, `MaybeChannel`, `ShotLineReady`, `WanderRadius` and `MaxTalkSeconds` are fields and helpers of the templates.
