# SETUP: Apply player_core → economy → progression → time_tracker → tycoon.
# NEVER own a wallet / XP table here. Pay and grant via PlayerManager slots.
# What a purchase shows = entities with a tycoon_reveal_component (TypeIndex / ItemIndex =
# this item's array and index on the plot); buying switches their meshes on.
using { /Verse.org/Simulation }
using { /Fortnite.com/Devices }
using { PlayerCore }

activatable <public> := interface:
    Activate<public>()<suspends> : void

rebirthable <public> := interface:
    OnRebirth<public>() : void

gated <public> := interface:
    Lock<public>() : void
    Unlock<public>() : void

plot_link <public> := class<concrete>:
    @editable TypeIndex <public> : int = 0
    @editable ItemIndex <public> : int = 0

buy_wrapper := class:
    Item : purchaseable
    OnAgent(Agent : agent) : void = Item.TryBuy(Agent)
    OnMaybeAgent(Maybe : ?agent) : void =
        if (Agent := Maybe?):
            Item.TryBuy(Agent)

grant_wrapper := class:
    Item : purchaseable
    OnAgent(Agent : agent) : void = Item.GrantFromEvent(Agent)
    OnMaybeAgent(Maybe : ?agent) : void =
        if (Agent := Maybe?):
            Item.GrantFromEvent(Agent)

purchaseable <public> := class<abstract>(activatable, rebirthable, gated):
    var OwnerPlot <public> : ?plot_manager = false
    var TypeIndex <public> : int = 0
    var ItemIndex <public> : int = 0
    var IsOwned <public> : logic = false
    var IsLocked <public> : logic = false
    var RunId <public> : int = 0
    var BuyHook <public> : ?buy_wrapper = false

    @editable DisplayName <public> : string = "Item"
    @editable Price <public> : float = 100.0
    @editable CurrencyIndex <public> : int = 0
    @editable XPOnBuy <public> : int = 0
    @editable GrantAmount <public> : float = 0.0
    @editable GrantCurrencyIndex <public> : int = 0
    @editable GrantInterval <public> : float = 0.0
    @editable StartsLocked <public> : logic = false
    @editable Dependents <public> : []plot_link = array{}
    @editable BuyButton <public> : button_device = button_device{}
    @editable BuyTrigger <public> : trigger_device = trigger_device{}
    @editable SuccessHud <public> : hud_message_device = hud_message_device{}
    @editable ErrorHud <public> : hud_message_device = hud_message_device{}
    @editable SFX <public> : audio_player_device = audio_player_device{}

    Message<localizes>(String : string) : message = "{String}"

    PackedKey<public>()<transacts> : int = PackPlotUnlock(TypeIndex, ItemIndex)

    Initialize<public>(Plot : plot_manager, NewType : int, NewIndex : int) : void =
        set OwnerPlot = option{Plot}
        set TypeIndex = NewType
        set ItemIndex = NewIndex
        set IsOwned = false
        set IsLocked = StartsLocked
        HideReveals()
        Hook := buy_wrapper{Item := Self}
        set BuyHook = option{Hook}
        BuyButton.InteractedWithEvent.Subscribe(Hook.OnAgent)
        BuyTrigger.TriggeredEvent.Subscribe(Hook.OnMaybeAgent)
        if (StartsLocked = true):
            Lock()
        else:
            Unlock()

    TryBuy<public>(Agent : agent) : void =
        if (Plot := OwnerPlot?):
            if (Plot.IsClaimedBy(Agent) = false):
                ErrorHud.SetText(Message("Not your plot"))
                ErrorHud.Show(Agent)
            else if (IsOwned = true):
                ErrorHud.SetText(Message("Already owned"))
                ErrorHud.Show(Agent)
            else if (IsLocked = true):
                ErrorHud.SetText(Message("Locked"))
                ErrorHud.Show(Agent)
            else:
                CommitBuy(Agent, Plot)

    CommitBuy<public>(Agent : agent, Plot : plot_manager) : void =
        if (Wallet := Plot.PlayerManager.GetCurrencyProvider()?):
            if (Wallet.GetCurrency(Agent, CurrencyIndex) >= Price):
                if (Wallet.RemoveCurrency[Agent, CurrencyIndex, Price]):
                    FinishBuy(Agent, Plot)
                else:
                    ErrorHud.SetText(Message("Purchase failed"))
                    ErrorHud.Show(Agent)
            else:
                ErrorHud.SetText(Message("Not enough currency"))
                ErrorHud.Show(Agent)
        else if (Price <= 0.0):
            FinishBuy(Agent, Plot)
        else:
            ErrorHud.SetText(Message("Economy not available"))
            ErrorHud.Show(Agent)

    FinishBuy<public>(Agent : agent, Plot : plot_manager) : void =
        set IsOwned = true
        AddPlotUnlock(Agent, PackedKey())
        if (XPOnBuy > 0):
            if (XP := Plot.PlayerManager.GetXPAwarder()?):
                XP.AddXP(Agent, XPOnBuy)
        SFX.Play(Agent)
        SuccessHud.SetText(Message("Unlocked {DisplayName}"))
        SuccessHud.Show(Agent)
        ShowReveals()
        UnlockDependents(Plot)
        spawn{ Activate() }

    ApplyLoadedUnlock<public>(Agent : agent) : void =
        set IsOwned = true
        set IsLocked = false
        ShowReveals()
        spawn{ Activate() }

    UnlockDependents<public>(Plot : plot_manager) : void =
        for (Link : Dependents):
            if (Other := Plot.FindPurchaseable(Link.TypeIndex, Link.ItemIndex)?):
                Other.Unlock()

    Activate<override>()<suspends> : void =
        StartGrantLoop()

    StartGrantLoop<public>()<suspends> : void =
        if (GrantInterval <= 0.0):
            loop:
                Sleep(3600.0)
        else:
            Gen := RunId
            loop:
                Sleep(GrantInterval)
                if (RunId <> Gen):
                    break
                if (IsOwned = false):
                    break
                GrantTick()

    GrantTick<public>() : void =
        if (Plot := OwnerPlot?):
            Plot.GrantToOwner(GrantCurrencyIndex, GrantAmount)

    GrantFromEvent<public>(Agent : agent) : void =
        if (Plot := OwnerPlot?):
            if (Plot.IsClaimedBy(Agent) = true):
                if (IsOwned = true):
                    Plot.GrantToAgent(Agent, GrantCurrencyIndex, GrantAmount)
                    if (XPOnBuy > 0):
                        if (XP := Plot.PlayerManager.GetXPAwarder()?):
                            XP.AddXP(Agent, XPOnBuy)

    OnRebirth<override>() : void =
        set RunId = RunId + 1
        set IsOwned = false
        HideReveals()
        if (StartsLocked = true):
            Lock()
        else:
            Unlock()

    Lock<override>() : void =
        set IsLocked = true

    Unlock<override>() : void =
        set IsLocked = false

    HideReveals<public>() : void =
        if (Plot := OwnerPlot?):
            Plot.SetRevealShown(PackedKey(), false)

    ShowReveals<public>() : void =
        if (Plot := OwnerPlot?):
            Plot.SetRevealShown(PackedKey(), true)
