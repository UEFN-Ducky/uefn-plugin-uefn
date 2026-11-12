# Talking shopkeeper: an AI-powered NPC that wanders, stops and faces whoever talks to it,
# hands out the item the player asks for, and complains when it is shot.
#
# Where things go:
#   * WHO it is (personality, voice, name) -> the NPC Character Definition: Persona Modifier + UI Modifier.
#     Test replies there with Edit in Prompt Editor, before any session.
#   * WHAT it does in the game -> this file. NPC Character Behavior -> Verse Behavior -> llm_npc_shopkeeper_behavior.
#   * Drag the definition into the level (it places an NPC Spawner). Players need voice chat on.
#
# What it shows:
#   * one voice channel with the NPC and every player, players who join later included
#   * the stock list added to the personality from Verse (Join + SetPersonality)
#   * structured output: the model fills `shopkeeper_reply` on every reply (RegisterAction, Required)
#   * a line said because of a game event (PromptToTalk when the NPC is damaged)
#   * walking around until someone talks, then standing still and facing them until the line ends
using { /Fortnite.com/AI }
using { /Fortnite.com/Characters }
using { /Fortnite.com/Game }
using { /Fortnite.com/Playspaces }
using { /Fortnite.com/Weapons }
using { /UnrealEngine.com/Conversations }
using { /UnrealEngine.com/Itemization }
using { /Verse.org/AgentGroup }
using { /Verse.org/Chat }
using { /Verse.org/Random }
using { /Verse.org/SceneGraph }
using { /Verse.org/Simulation }
using { /Verse.org/SpatialMath }

# A voice channel needs a concrete member-info class.
shopkeeper_member<public> := class(has_voice_member_info){}

# What the shop sells. None = the player asked for nothing (or for something not in stock).
shopkeeper_item<public> := enum:
    None
    PumpShotgun
    ShockwaveHammer
    AssaultRifle

# Structured output: the model fills these fields; @ai_description tells it how.
shopkeeper_reply<public> := struct:
    @ai_description("The item the player asked you to hand over in what they just said. None when they asked for nothing or for something you do not sell.")
    Item:shopkeeper_item = shopkeeper_item.None
    @ai_description("The player who is talking to you.")
    Customer:?agent = false

ShopkeeperText<localizes>(Text:string):message = "{Text}"

llm_npc_shopkeeper_behavior<public> := class(npc_behavior):
    # How far from its spawn point it walks, in centimeters.
    @editable WanderRadius:float = 750.0
    # It stops waiting for a line to end after this many seconds (a failed or moderated reply never ends).
    @editable MaxTalkSeconds:float = 30.0

    var MaybeGroup:?agent_group(shopkeeper_member) = false
    var MaybeChannel:?voice_channel(shopkeeper_member) = false
    var Cancels:[]cancelable = array{}
    var LastHeard:?agent = false
    var ShotLineReady:logic = true

    OnBegin<override>()<suspends>:void =
        if:
            Entity := GetEntity[]
            NPCAgent := GetAgent[]
            Persona := Entity.GetComponent[persona_component]
            Sim := Entity.GetSimulationEntity[]
            Playspace := Entity.GetPlayspaceForEntity[]
        then:
            # 1. One voice channel: the NPC and every player are members of its group.
            Group := agent_group(shopkeeper_member){}
            Channel := voice_channel(shopkeeper_member){Name := ShopkeeperText("Shop"), Group := Group}
            set MaybeGroup = option{Group}
            set MaybeChannel = option{Channel}
            Group.AddMember(NPCAgent, shopkeeper_member{CanBroadcast := true})
            Sim.AddChatChannel(Channel)
            for (Player : Playspace.GetPlayers()):
                AddCustomer(Player)
            set Cancels += array{Playspace.PlayerAddedEvent().Subscribe(AddCustomer)}
            set Cancels += array{Playspace.PlayerRemovedEvent().Subscribe(RemoveCustomer)}
            # 2. Game facts the personality needs. Build messages BEFORE a [ ] call (a <localizes> call inside one is error 3512).
            Stock := ShopkeeperText("You sell exactly three items: a pump shotgun, a shockwave hammer and an assault rifle. They are free. Never offer anything else.")
            NewPersonality := Join(array{Persona.Personality, Stock}, ShopkeeperText("\n"))
            if (Persona.SetPersonality[NewPersonality]) {}
            # 3. Structured output, registered once for the whole session.
            ReplyDef := prompt_binding_definition:
                Name := ShopkeeperText("ShopReply")
                Description := ShopkeeperText("Signals whenever a player has spoken to you.")
            Session := Persona.GetAISession()
            set Cancels += array{Session.RegisterAction(ReplyDef, true, shopkeeper_reply, OnReply)}
            # 4. Game events it reacts to.
            set Cancels += array{Persona.StartHearEvent.Subscribe(OnHeard)}
            if (Char := NPCAgent.GetFortCharacter[]):
                set Cancels += array{Char.DamagedEvent().Subscribe(OnDamaged)}
            # 5. Walk around; stand still and face the speaker while a conversation runs.
            WanderAndListen(Entity, Persona)

    AddCustomer(Player:player):void =
        if:
            Group := MaybeGroup?
            Channel := MaybeChannel?
            Persona := GetEntity[].GetComponent[persona_component]
        then:
            Group.AddMember(Player, shopkeeper_member{CanBroadcast := true})
            # Without a conversation target the talk prompt never shows for this player.
            Player.SetConversationTarget(Persona, Channel)

    RemoveCustomer(Player:player):void =
        Player.ClearConversationTarget()
        if (Group := MaybeGroup?):
            Group.RemoveMember(Player)

    OnHeard(Speaker:agent):void =
        set LastHeard = option{Speaker}

    # The model's side output for one reply. Decide with enums, numbers and logic, never with the spoken text.
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

    OnEnd<override>():void =
        for (Cancel : Cancels):
            Cancel.Cancel()
        if (Entity := GetEntity[]):
            if (Playspace := Entity.GetPlayspaceForEntity[]):
                for (Player : Playspace.GetPlayers()):
                    Player.ClearConversationTarget()
            if (Sim := Entity.GetSimulationEntity[], Channel := MaybeChannel?):
                Sim.RemoveChatChannel(Channel)
