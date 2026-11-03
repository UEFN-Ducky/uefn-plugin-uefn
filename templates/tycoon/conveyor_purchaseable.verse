# SETUP: Conveyor belt on a plot. Its belt pieces and dropper slot markers are entities with a
# tycoon_reveal_component (TypeIndex 3, ItemIndex = this belt's index in Conveyors); buying
# the belt shows them all. Moving belt parts are keyframed (loop), never moved from here.
using { /Verse.org/Simulation }
using { /Fortnite.com/Devices }

conveyor_purchaseable <public> := class<concrete>(purchaseable):
    var LinkedCount <public> : int = 0

    Activate<override>()<suspends> : void =
        ShowReveals()
        StartGrantLoop()

    LinkDropper<public>(Dropper : dropper_purchaseable) : void =
        set LinkedCount = LinkedCount + 1

    UnlinkDropper<public>(Dropper : dropper_purchaseable) : void =
        if (LinkedCount > 0):
            set LinkedCount = LinkedCount - 1

    OnRebirth<override>() : void =
        set LinkedCount = 0
        (super:)OnRebirth()
