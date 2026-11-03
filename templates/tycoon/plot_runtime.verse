# SETUP: Runtime plot extras (not in GetPurchaseArray) — collect, timed gift, money wheel.
# A pickup's mesh is an entity with a tycoon_reveal_component: TypeIndex 10
# (CollectableRevealType), ItemIndex = its index in the plot's Collectables.
using { /Verse.org/Simulation }
using { /Fortnite.com/Devices }
using { /Verse.org/Random }
using { PlayerCore }

collect_wrapper := class:
    Item : plot_collectable
    OnMaybeAgent(Maybe : ?agent) : void =
        if (Agent := Maybe?):
            Item.TryCollect(Agent)

gift_wrapper := class:
    Item : timed_gift
    OnAgent(Agent : agent) : void = Item.TryClaim(Agent)

wheel_wrapper := class:
    Item : money_wheel
    OnAgent(Agent : agent) : void = Item.TrySpin(Agent)

plot_collectable <public> := class<concrete>:
    Message<localizes>(String : string) : message = "{String}"
    var OwnerPlot <public> : ?plot_manager = false
    var Taken <public> : logic = false
    var Hook <public> : ?collect_wrapper = false
    var ItemIndex <public> : int = 0

    @editable PickupTrigger <public> : trigger_device = trigger_device{}
    @editable GrantAmount <public> : float = 10.0
    @editable CurrencyIndex <public> : int = 0
    @editable XPOnCollect <public> : int = 0
    @editable SuccessHud <public> : hud_message_device = hud_message_device{}

    Initialize<public>(Plot : plot_manager, Index : int) : void =
        set OwnerPlot = option{Plot}
        set ItemIndex = Index
        set Taken = false
        W := collect_wrapper{Item := Self}
        set Hook = option{W}
        PickupTrigger.TriggeredEvent.Subscribe(W.OnMaybeAgent)
        Park()

    RevealKey<public>()<transacts> : int = PackPlotUnlock(CollectableRevealType, ItemIndex)

    ShowFor<public>(Agent : agent) : void =
        set Taken = false
        if (Plot := OwnerPlot?):
            Plot.SetRevealShown(RevealKey(), true)

    TryCollect<public>(Agent : agent) : void =
        if (Plot := OwnerPlot?):
            if (Plot.IsClaimedBy(Agent) = true):
                if (Taken = false):
                    set Taken = true
                    Plot.GrantToAgent(Agent, CurrencyIndex, GrantAmount)
                    if (XPOnCollect > 0):
                        if (XP := Plot.PlayerManager.GetXPAwarder()?):
                            XP.AddXP(Agent, XPOnCollect)
                    SuccessHud.SetText(Message("Collected"))
                    SuccessHud.Show(Agent)
                    Park()

    Park<public>() : void =
        if (Plot := OwnerPlot?):
            Plot.SetRevealShown(RevealKey(), false)

    OnRebirth<public>() : void =
        set Taken = false
        Park()

timed_gift <public> := class<concrete>:
    Message<localizes>(String : string) : message = "{String}"
    var OwnerPlot <public> : ?plot_manager = false
    var Ready <public> : logic = false
    var RunId <public> : int = 0
    var Hook <public> : ?gift_wrapper = false

    @editable DelaySeconds <public> : float = 30.0
    @editable ClaimButton <public> : button_device = button_device{}
    @editable GrantAmount <public> : float = 50.0
    @editable CurrencyIndex <public> : int = 0
    @editable SuccessHud <public> : hud_message_device = hud_message_device{}
    @editable ErrorHud <public> : hud_message_device = hud_message_device{}

    Initialize<public>(Plot : plot_manager, Index : int) : void =
        set OwnerPlot = option{Plot}
        set Ready = false
        W := gift_wrapper{Item := Self}
        set Hook = option{W}
        ClaimButton.InteractedWithEvent.Subscribe(W.OnAgent)

    StartFor<public>(Agent : agent) : void =
        set RunId = RunId + 1
        set Ready = false
        spawn{ WaitThenReady() }

    WaitThenReady<public>()<suspends> : void =
        Gen := RunId
        Sleep(DelaySeconds)
        if (RunId = Gen):
            set Ready = true

    TryClaim<public>(Agent : agent) : void =
        if (Plot := OwnerPlot?):
            if (Plot.IsClaimedBy(Agent) = false):
                ErrorHud.SetText(Message("Not your plot"))
                ErrorHud.Show(Agent)
            else if (Ready = false):
                ErrorHud.SetText(Message("Not ready"))
                ErrorHud.Show(Agent)
            else:
                set Ready = false
                Plot.GrantToAgent(Agent, CurrencyIndex, GrantAmount)
                SuccessHud.SetText(Message("Gift claimed"))
                SuccessHud.Show(Agent)

    OnRebirth<public>() : void =
        set RunId = RunId + 1
        set Ready = false

money_wheel <public> := class<concrete>:
    Message<localizes>(String : string) : message = "{String}"
    var OwnerPlot <public> : ?plot_manager = false
    var Enabled <public> : logic = false
    var Hook <public> : ?wheel_wrapper = false

    @editable SpinButton <public> : button_device = button_device{}
    @editable Outcomes <public> : []float = array{10.0, 25.0, 50.0, 100.0}
    @editable CurrencyIndex <public> : int = 0
    @editable SuccessHud <public> : hud_message_device = hud_message_device{}
    @editable ErrorHud <public> : hud_message_device = hud_message_device{}

    Initialize<public>(Plot : plot_manager, Index : int) : void =
        set OwnerPlot = option{Plot}
        set Enabled = false
        W := wheel_wrapper{Item := Self}
        set Hook = option{W}
        SpinButton.InteractedWithEvent.Subscribe(W.OnAgent)

    EnableFor<public>(Agent : agent) : void =
        set Enabled = true

    TrySpin<public>(Agent : agent) : void =
        if (Plot := OwnerPlot?):
            if (Plot.IsClaimedBy(Agent) = false):
                ErrorHud.SetText(Message("Not your plot"))
                ErrorHud.Show(Agent)
            else if (Enabled = false):
                ErrorHud.SetText(Message("Wheel locked"))
                ErrorHud.Show(Agent)
            else if (Outcomes.Length > 0):
                Pick := GetRandomInt(0, Outcomes.Length - 1)
                if (Amount := Outcomes[Pick]):
                    Plot.GrantToAgent(Agent, CurrencyIndex, Amount)
                    SuccessHud.SetText(Message("Won {Amount}"))
                    SuccessHud.Show(Agent)

    OnRebirth<public>() : void =
        set Enabled = false
