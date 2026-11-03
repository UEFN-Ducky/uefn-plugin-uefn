---
description: "Full plot tycoon — tycoon_controller, plot_manager, purchaseable types, rebirth, persist nest on player_core"
metadata:
  order: 38
  label: "Game systems — tycoon plots & purchaseables"
  default_enabled: false
  load_condition: "Building a tycoon / idle plot — claim pads, purchaseables, droppers, conveyors, pets, rebirth"
---

## Tycoon — plots that consume island packs

**Consume, don't own (HARD):** apply `player_core` → `economy` → `progression` →
`time_tracker` → `tycoon`. Wire `@editable PlayerManager` on `tycoon_controller`
and each `plot_manager`. Pay with `GetCurrencyProvider()`, XP with
`GetXPAwarder()`, offline with `GetPlaytimeProvider()`. Never put a wallet,
XP table, or persist `weak_map` in `Verse/Tycoon/` (a fifth map is error 3502).

Progress nests on Player Core `game_player_table`: `PlotRebirths`, `PlotUnlocks`,
`PlotLevels` (defaulted fields). Helpers: `PackPlotUnlock` / `AddPlotUnlock` /
`AddPlotRebirth` / `GetPlotLevel`.

```
tycoon_controller  →  []plot_manager
plot_manager       →  typed []purchaseable arrays + runtime collectables/gifts/wheels
purchaseable       →  TryBuy → RemoveCurrency → AddPlotUnlock → Activate()
```

Claim modes on the controller: `Manual` (plot ClaimButton), `Fill` (first free
plot on join), `Teleport` (Fill + `ClaimTeleporter.Teleport`).

### Add a purchaseable type

1. New file under `Verse/Tycoon/` subclassing `purchaseable`.
2. Override `Activate()<suspends>` for post-buy behavior (call `StartGrantLoop()`
   if you still want interval grants).
3. Add `@editable MyThings : []my_thing_purchaseable` on `plot_manager`.
4. `Initialize(Self, TypeIndex, I)` in `InitializeAll` and a branch in
   `FindPurchaseable`.

```verse
my_thing_purchaseable <public> := class<concrete>(purchaseable):
    Activate<override>()<suspends> : void =
        ShowReveals()
        StartGrantLoop()
```

Type indices in the shipped pack: 0 prop, 1 generator, 2 dropper, 3 conveyor,
4 upgrader, 5 npc, 6 pet, 7 dancefloor, 8 hitable, 9 shootable, 10 collectable
(`CollectableRevealType`, runtime pickups).

### What a purchase shows: reveal entities (Scene Graph)

Every mesh a buy reveals — a building, belt pieces, a pet, a pickup — is a Scene
Graph entity with a `tycoon_reveal_component`: `Plot` (its `plot_manager`),
`TypeIndex` and `ItemIndex` (the purchaseable's array and index). It registers
with the plot when it starts and begins hidden; `ShowReveals()` /
`HideReveals()` switch its meshes with `Enable()` / `Disable()`
(`plot_manager.SetRevealShown`). Nothing is teleported underground and nothing
uses `MoveTo`. Details: `sys_buildings`.

- Pet: the pet entity also carries a `keyframed_movement_component`;
  `pet_purchaseable` re-aims a short keyframe segment at the owner every
  `FollowSeconds` (`FollowSpeed`, `FollowGap`), flat on the plot.
- Belt: belt pieces that move are keyframed on their own (KFM `loop`), and show
  with the conveyor's reveal key.

Dependents: `@editable Dependents : []plot_link` (TypeIndex + ItemIndex). Buy
unlocks those rows. `StartsLocked := true` until a parent buys.

### Rebirth

`plot_manager` RebirthButton: charge `RebirthCost * multiplier^rebirths` through
Economy, drain known currency indices, `AddPlotRebirth` (clears unlocks/levels),
`OnRebirth` on every purchaseable. Later `GrantToAgent` scales by
`GrantMultiplier ^ PlotRebirths`.

### Belt

Droppers `Activate` call `FindConveyor(ConveyorIndex).LinkDropper`. Upgraders
multiply `plot_manager.BeltMultiplier`. Buttons, triggers and HUD are Creative
devices; everything visible that appears or moves is a reveal entity. Audio =
`audio_player_device` only.

### Runtime (not purchaseables)

`plot_collectable`, `timed_gift`, `money_wheel` init on claim via `ShowRuntime`.
A pickup's mesh is a reveal entity with TypeIndex 10 and its index in `Collectables`.
They grant through `GrantToAgent` (same rebirth scale).

HUD: Economy owns the wallet canvas. Plot feedback is `hud_message_device` on
the purchaseable / plot. Reveals are entities with `tycoon_reveal_component`
(see `sys_buildings`). Generators: `sys_generators`.
