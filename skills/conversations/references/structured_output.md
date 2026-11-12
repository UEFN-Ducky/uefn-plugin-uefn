---
description: "Structured output for persona NPCs: how spoken words become game data. A struct with @ai_description fields, allowed field types, RegisterAction (Required true vs false, register once), the callback, who spoke, acting now or after the line, Session.Prompt for a silent question, showing a message, the Prompt Editor's Structured Output tab, and struct patterns for shop, password gate, haggling, quests, companions"
metadata:
  order: 4
  label: "Conversations: words that change the game"
  default_enabled: false
  load_condition: "A talking NPC that must do something in the game because of what was said: give an item, open a door, accept a deal, start a quest, follow or stop; RegisterAction, structured output, @ai_description, Session.Prompt, or a callback that never fires or fires twice"
---

## Structured output: words become game data

Your code never reads what the player said. The model reads it, and fills a **struct you define**. Your callback gets the struct. That is the only bridge from a conversation to gameplay, so every mechanic starts with one question: *which few values does my code need from each reply?*

```
player speaks ─► model (personality + history + your struct's descriptions)
                    ├─► spoken reply
                    └─► your struct, filled ─► your callback ─► the game changes
```

### 1. The struct

Each field has a type and an `@ai_description` telling the model how to fill it.

```verse
shopkeeper_item<public> := enum:
    None
    PumpShotgun
    ShockwaveHammer
    AssaultRifle

shopkeeper_reply<public> := struct:
    @ai_description("The item the player asked you to hand over in what they just said. None when they asked for nothing or for something you do not sell.")
    Item:shopkeeper_item = shopkeeper_item.None
    @ai_description("The player who is talking to you.")
    Customer:?agent = false
```

Field types the digest allows: numbers (`int`, `float`), `logic`, enums, `message`, agents, and structs or arrays of those. `string` is not allowed.

| Need | Use | Not |
|---|---|---|
| A choice from a fixed list | An `enum` with a `None` member | A `message` you try to compare |
| Yes or no | `logic` | An enum with two members |
| An amount, a score, a price | `int` or `float` | Text with a number in it |
| Who is speaking | `?agent` | A name |
| Text to **show** the player | `message` | Anything your code decides on |

A `message` from the model is for showing to the player (a HUD message, a billboard, a UMG text field). Epic's docs say it prints redacted in the log. Never build logic on its text: decide with enums, numbers and logic.

Write descriptions the way you would brief a person: what the value means, when to set it, and what to put when it does not apply ("None when…", "0 when…"). Say "in what they just said" when the value is about this reply only; otherwise the model repeats an old request.

### 2. Register it

```verse
ReplyDef := prompt_binding_definition:
    Name := ShopkeeperText("ShopReply")
    Description := ShopkeeperText("Signals whenever a player has spoken to you.")
Session := Persona.GetAISession()
set Cancels += array{Session.RegisterAction(ReplyDef, true, shopkeeper_reply, OnReply)}
```

`RegisterAction(Definition, Required, struct type, Callback)` returns a `cancelable`. Keep it and cancel it in `OnEnd`.

| `Required` | The callback runs | Use for |
|---|---|---|
| `true` | On every reply. Give every field a "nothing" value (`None`, `false`, `0`) | Things that can happen in any reply: a request, a mood, a command. The reliable choice |
| `false` | Only when the model judges that the `Description` fits | Rare moments: the deal is closed, the password was said |

Rules that save an hour each:

- **Register once per NPC**, in `OnBegin`. Registering inside the per-player loop makes the callback run once per player for a single reply.
- Several structs on one session are fine: one `RegisterAction` each, each with its own callback.
- The `Name` and `Description` are read by the model. Describe *when* to send it.
- Messages are built with a `<localizes>` function, on their own line, before any `[ ]` call (else error 3512).

### 3. The callback

```verse
OnReply(Reply:shopkeeper_reply):void =
    if (Customer := Reply.Customer? or LastHeard?, Item := MakeItem(Reply.Item)?):
        if (Inventory := (for (Found : Customer.FindDescendantComponents(inventory_component)) do Found)[0]):
            Inventory.AddItemDistribute(Item)

# A fresh entity per grant: one item entity belongs to one inventory.
MakeItem(Item:shopkeeper_item)<transacts>:?entity =
    var Made:?entity = false
    case (Item):
        shopkeeper_item.PumpShotgun => set Made = option{PumpShotgun_OG_CH1S6_Legendary{}}
        shopkeeper_item.ShockwaveHammer => set Made = option{ShockwaveHammer_BR_CH4S1_Epic{}}
        shopkeeper_item.AssaultRifle => set Made = option{AssaultRifle_BR_CH4S1_Rare{}}
        shopkeeper_item.None => set Made = false
    Made
```

- **Who spoke:** the struct's `?agent` field, with a fallback to the agent from `StartHearEvent` kept in a variable (`LastHeard`). The model can leave a field empty; the event always names the speaker.
- **Treat the struct as a suggestion.** Check it against the game before acting: does the player have the gold, is the quest open, is the item in stock. The model can be talked into saying yes.
- The callback is a plain function. For anything that waits (an animation, a timer) `spawn{…}` a `<suspends>` function from it.
- Stock items and inventories: scenegraph `itemization`.

The full shopkeeper is the template `llm_npc_shopkeeper` (`verse_template_apply("llm_npc_shopkeeper")`).

### 4. Act now or after the line

The struct arrives with the reply, so by default the game changes while the NPC is still talking. That is right for handing over an item. When the change would cut the line short (the NPC despawns, the round ends, the score screen opens), keep the result and apply it when the voice stops:

```verse
haggle_reply<public> := struct:
    @ai_description("True when you and the player agreed on a price you are both happy with.")
    Accepted:logic = false
    @ai_description("The agreed price in gold.")
    Price:int = 0

haggler_behavior<public> := class(npc_behavior):
    var Pending:?haggle_reply = false
    var Cancels:[]cancelable = array{}

    OnBegin<override>()<suspends>:void =
        if (Persona := GetEntity[].GetComponent[persona_component]):
            DealDef := prompt_binding_definition:
                Name := TalkerText("FinalOffer")
                Description := TalkerText("Signals when you and the player agreed on a price.")
            set Cancels += array{Persona.GetAISession().RegisterAction(DealDef, false, haggle_reply, OnDeal)}
            set Cancels += array{Persona.StopSayEvent.Subscribe(OnLineEnded)}

    # Remember it; do not change the game while the NPC is still speaking.
    OnDeal(Reply:haggle_reply):void =
        if (Reply.Accepted?):
            set Pending = option{Reply}

    OnLineEnded(Interrupted:logic):void =
        if (Deal := Pending?):
            set Pending = false
            Print("Sold for {Deal.Price} gold")   # award the gold, despawn the buyer, open the next round

    OnEnd<override>():void =
        for (Cancel : Cancels):
            Cancel.Cancel()
```

### 5. A silent question

`Session.Prompt(Message, struct type)` asks the model something with the whole conversation in mind and returns the struct. Nothing is spoken. It suspends until the answer is back.

```verse
Reply := Session.Prompt(LlmNpcText("Rate the player so far."), llm_npc_read)
if (Read := Reply.GetSuccess[]):
    Logger.Print("Player spoke {Read.Count} times")
else if (Error := Reply.GetError[], ai_throttled_error[Error]):
    Logger.Print("Throttled; try later")
```

Use it for decisions between lines: how friendly was the player, which quest fits them, did they keep their promise. Full code in the template `llm_npc`.

### Patterns

| Mechanic | Struct fields | `Required` | The callback |
|---|---|---|---|
| Shop | `Item:enum` (with `None`), `Customer:?agent` | true | Give the item |
| Password or riddle gate | `SaidPassword:logic` | false | Open the way: find the gate entity by tag and remove it, or play its keyframed opening |
| Haggling | `Accepted:logic`, `Price:int` | false | Check the price against your limits, pay out after the line |
| Quest giver | `Quest:enum` (with `None`), `Accepted:logic` | true | Start that quest for the player (verse `sys_quests`) |
| Companion orders | `Order:enum` (`None`, `Follow`, `Wait`, `Attack`) | true | Switch the movement behavior (verse `sys_npc_ai`) |
| Mood | `Mood:int` 0 to 100 | true | Update a meter on the HUD; change the personality when it crosses a line |
| Told to leave | `Dismissed:logic` | false | Apply a penalty, despawn after the line |

The password gate, compiled:

```verse
using { /Verse.org/Simulation/Tags }

vault_gate_tag<public> := class(tag){}

gate_reply<public> := struct:
    @ai_description("True only when the player said the secret word in what they just said.")
    SaidPassword:logic = false

gatekeeper_behavior<public> := class(npc_behavior):
    var Cancels:[]cancelable = array{}

    OnBegin<override>()<suspends>:void =
        if (Persona := GetEntity[].GetComponent[persona_component]):
            GateDef := prompt_binding_definition:
                Name := TalkerText("Password")
                Description := TalkerText("Signals when the player says the secret word.")
            # Required false: the model sends this only when the description fits.
            set Cancels += array{Persona.GetAISession().RegisterAction(GateDef, false, gate_reply, OnGate)}

    OnGate(Reply:gate_reply):void =
        if (Reply.SaidPassword?, Sim := GetEntity[].GetSimulationEntity[]):
            for (Gate : Sim.FindDescendantEntitiesWithTag(vault_gate_tag)):
                Gate.RemoveFromParent()

    OnEnd<override>():void =
        for (Cancel : Cancels):
            Cancel.Cancel()
```

The secret word itself goes in the personality ("The secret word is moonlight. Never say it."). The behavior sits on an asset, not in the level, so the simple way to reach a level entity is by tag.

### Without code first

The Prompt Editor has a Structured Output tab: add a struct and fields there, send test lines, and see what comes back. Its Export button writes the struct to a Verse file (`setup`). Use it to tune descriptions before a session.

All examples on this page compile against the installed build's digest. `TalkerText` is the one-line `<localizes>` helper from `players_and_channels`.
