# Device for one UMG User Widget instance per player.
# With Epic's Verse UI Kit in the project, prefer the kit's driver pattern instead (skill verse_ui_kit):
# Helper.ShowFullScreen / SubscribeToEvent / FocusWidgetForPlayer / ClearAllForPlayer.
# The widget type is the Assets digest name after build_widget_tree.
# Do not invent card_widget_bp := class. Replace WIDGET with that digest name
# (list_verse_types digest=assets) and uncomment the WIDGET lines.
# Fields: IsIntroActive is a bool (add_verse_field logic). OnCloseClicked is an event field: Await it
# (add_verse_field type event, then bind_widget_event OnButtonClicked; see umg_verse_field_events).
# Event fields have no Subscribe until 43.00; never add your own Subscribe extension (events_subscriptions).
# Buttons on the widget are custom ones (kit buttons or CustomButton), never Loud/Quiet/Regular.
using { /Fortnite.com/Devices }
using { /Fortnite.com/UI }
using { /UnrealEngine.com/Temporary/UI }
using { /Verse.org/Simulation }

umg_widget_device := class(creative_device):

    @editable
    ShowVolume : volume_device = volume_device{}

    @editable
    HideVolume : volume_device = volume_device{}

    var WidgetReady : logic = false
    var Shown : [player]logic = map{}
    StopWatching : event() = event(){}

    # WIDGET: var Widgets : [player]UW_Menu_Screen = map{}

    OnBegin<override>()<suspends>:void =
        ShowVolume.AgentEntersEvent.Subscribe(OnShow)
        HideVolume.AgentEntersEvent.Subscribe(OnHide)

    OnShow(InAgent : agent):void =
        if (Player := player[InAgent], PlayerUI := GetPlayerUI[Player]):
            EnsureInitialized()
            if (set Shown[Player] = true) {}
            # WIDGET:
            # Widget := UW_Menu_Screen{}
            # if (set Widgets[Player] = Widget) {}
            # set Widget.IsIntroActive = true
            # PlayerUI.AddWidget(Widget, player_ui_slot{ InputMode := ui_input_mode.All })
            # PlayerUI.SetFocus(Widget)   # after it is on screen; the widget's Desired Focus Widget picks the control

    OnHide(InAgent : agent):void =
        if (Player := player[InAgent], PlayerUI := GetPlayerUI[Player]):
            if (set Shown[Player] = false) {}
            # WIDGET:
            # if (Widget := Widgets[Player]):
            #     PlayerUI.RemoveWidget(Widget)

    EnsureInitialized():void =
        if (WidgetReady = true):
            return
        # WIDGET: start one watcher per widget instance, not on every volume enter:
        # spawn{ WatchClose(Widget) }
        set WidgetReady = true

    # WIDGET: awaits the close click until the device ends. On 43.00+ this can be
    # Widget.OnCloseClicked.Subscribe(OnCloseClicked) instead (it returns a cancelable).
    # WatchClose(Widget : UW_Menu_Screen)<suspends>:void =
    #     race:
    #         loop:
    #             Widget.OnCloseClicked.Await()
    #             OnClose()
    #         StopWatching.Await()

    OnEnd<override>():void =
        StopWatching.Signal()

    OnClose():void =
        for:
            Player : GetPlayspace().GetPlayers()
            PlayerUI := GetPlayerUI[Player]
        do:
            if (set Shown[Player] = false) {}
            # WIDGET:
            # if (Widget := Widgets[Player]):
            #     PlayerUI.RemoveWidget(Widget)
