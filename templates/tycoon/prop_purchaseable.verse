# SETUP: Prop unlock on a plot. Pay via economy; buying shows its reveal entities.
using { /Verse.org/Simulation }
using { /Fortnite.com/Devices }

prop_purchaseable <public> := class<concrete>(purchaseable):
    Activate<override>()<suspends> : void =
        ShowReveals()
        StartGrantLoop()
