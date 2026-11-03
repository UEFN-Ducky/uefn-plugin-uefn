# SETUP: Add to every entity a plot shows when something is bought: a reveal mesh, a belt
# waypoint, a pet, a pickup. Set Plot, TypeIndex (the plot_manager array it belongs to:
# 0 Props, 1 Generators, 2 Droppers, 3 Conveyors, 4 Upgraders, 5 NPCs, 6 Pets,
# 7 Dancefloors, 8 Hitables, 9 Shootables, 10 Collectables) and ItemIndex (the item's
# index in that array). It starts hidden; the plot switches its meshes on and off, it never
# teleports it. A pet entity also needs a keyframed_movement_component.
using { /Verse.org/SceneGraph }
using { /Verse.org/Simulation }
using { PlayerCore }

CollectableRevealType<public> : int = 10

tycoon_reveal_component <public> := class<final_super>(component):
    @editable Plot <public> : ?plot_manager = false
    @editable TypeIndex <public> : int = 0
    @editable ItemIndex <public> : int = 0
    # Off for things players walk through when shown (a pickup inside a trigger).
    @editable SolidWhenShown <public> : logic = true

    OnBeginSimulation<override>() : void =
        (super:)OnBeginSimulation()
        if (Owner := Plot?):
            Owner.RegisterReveal(Self)

    RevealKey<public>()<transacts> : int = PackPlotUnlock(TypeIndex, ItemIndex)

    # Enable / Disable have no effect specifier: straight-line code only. Disable() only
    # stops rendering, so collision and queries are switched too (no invisible walls).
    SetShown<public>(Shown : logic) : void =
        Solid := if (Shown?, SolidWhenShown?) then true else false
        for (Mesh : Entity.FindDescendantComponents(mesh_component)):
            set Mesh.Collidable = Solid
            set Mesh.Queryable = Shown
            if (Shown?):
                Mesh.Enable()
            else:
                Mesh.Disable()
