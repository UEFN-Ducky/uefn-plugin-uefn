---
description: "Building unlock & reveal — prop_purchaseable on a plot, reveal entities (Scene Graph, tycoon_reveal_component) shown and hidden by switching their meshes, never teleported underground or moved with MoveTo"
metadata:
  order: 39
  label: "Game systems — building unlock & plot reveal"
  default_enabled: false
  load_condition: "Unlocking or upgrading buildings/plots, revealing tiers, showing or hiding plot pieces, coupling unlocks to delivery paths"
---

## Building unlock & reveal — `prop_purchaseable`

Tycoon plots: `verse_template_apply("tycoon")` then customize
`prop_purchaseable` on `plot_manager.Props`. Pay with
`PlayerManager.GetCurrencyProvider()` (the island `economy` pack — never a
tycoon-local wallet). Full kit map: `sys_tycoon`. Generators: `sys_generators`.

### Unlock flow

`purchaseable.TryBuy` charges `Price` / `CurrencyIndex`, writes `PlotUnlocks`,
then `ShowReveals()`. Locked rows wait on `Dependents` from a parent buy.

```verse
# After buy (already charged in purchaseable.FinishBuy):
Activate<override>()<suspends> : void =
    ShowReveals()
    StartGrantLoop()
```

Persist owned keys in `game_player_table.PlotUnlocks` via `AddPlotUnlock`.
Rejoin: `plot_manager.ApplySavedUnlocks`.

### Reveal entities (the only reveal in the pack)

What a buy shows is built as Scene Graph entities, placed once in the level (or
in a plot prefab):

1. Give each entity a `tycoon_reveal_component`: `Plot` = its `plot_manager`,
   `TypeIndex` = the purchaseable's array on the plot (0 Props … 9 Shootables,
   10 Collectables), `ItemIndex` = its index there. Several entities can share
   one key (a building made of parts).
2. At simulation start each one registers with its plot
   (`plot_manager.RegisterReveal`) and takes the current state — hidden until
   bought, whichever starts first.
3. Buy / loaded unlock: `ShowReveals()` → `plot_manager.SetRevealShown(Key,
   true)` → every entity with that key `Enable()`s its meshes.
4. `OnRebirth` / unclaim: `HideReveals()` disables them again.

Never teleport a reveal underground, never `MoveTo` it, and never
`RemoveFromParent` + re-add it (it returns invisible with its collision still
there). A reveal that should animate when it appears (rise from the ground, pop
in) plays a `oneshot` keyframe on its own `keyframed_movement_component`
(scenegraph `movement_transforms`).

### Nav / delivery coupling

When plot index N unlocks, enable end-nav set N so delivered entities can
finish at that building (`sys_spawning`). Filter ends by storage fullness if
capacity-gated.

### UI

Plot feedback: `hud_message_device` on the purchaseable. Wallet HUD stays in
Economy (`sys_hud_template` / `sys_canvas_cookbook` for custom canvases).

### Gotchas

- A reveal entity with no `Plot` set never registers and stays visible.
- `TypeIndex` / `ItemIndex` must match the purchaseable's array and index on that
  plot; a wrong pair shows the wrong building.
- Mesh reveal ≠ material swap; pick one visual strategy per entity.
- Never own currency in `Verse/Tycoon/`.
