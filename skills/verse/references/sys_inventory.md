---
description: "Per-player inventory — persistable item entry arrays, immutable add/remove, quantity checks, re-granting physical items on load, and per-entry persist vs reset flags"
metadata:
  order: 33
  label: "Game systems — inventory & owned items"
  default_enabled: false
  load_condition: "Building a per-player item inventory, owned-collection of soft ItemId bags, stackable items, re-granting Creative granter items on join, or persist vs session-reset item flags. Armory owned guns → sys_owned_weapons"
---

## Inventory & owned items

A per-player inventory is a **named collection of stackable entries** in the
shared persistable table, plus a runtime manager and a placed device that
hooks the **player-manager connected bus** — same programming flow as wallet /
level (`sys_architecture`, `sys_player_data`, `sys_economy`). Names are generic.

**Player custom firearms** — prefab/grant API →
`skill_read_subskill("scenegraph", "custom_weapons")`. Owned collectible +
canvas shop + persist → `skill_read_subskill("verse", "sys_owned_weapons")`.
**Custom non-weapon Scene Graph items** →
`skill_read_subskill("scenegraph", "custom_items")`. This file is soft persist
bags + Creative Item Granter — not Armory guns.

### Layers (same five-part shape)

```
persistable inventory_entry + player_inventory  → nested in shared table
inventory_save_service                   → rebuild-and-store
inventory_manager (class<unique>)         → field on game_player_services
inventory_manager_device                  → SubscribePlayerConnected + InitializeAll
```

### Persistable shapes

```verse
inventory_entry := class<final><persistable>:
    ItemId <public> : string = ""
    Quantity <public> : int = 0

player_inventory := class<final><persistable>:
    Entries <public> : []inventory_entry = array{}
```

Designer config (`class<concrete>`, not persisted):

```verse
item_config := class<concrete>():
    @editable ItemId <public> : string = ""
    @editable DisplayName : string = ""
    @editable Persistable : logic = true          # false → reset to 0 on join
    @editable ItemIcon : ?texture = false
    @editable ItemGranter : item_granter_device = item_granter_device{}
    @editable GranterSlotIndex : int = 0
```

### Immutable add / remove (persistence manager)

Same guard and rebuild pattern as currency:

```verse
# The entry with Amount added when it is ItemId; any other entry unchanged.
AddToEntry(Entry : inventory_entry, ItemId : string, Amount : int)<transacts> : inventory_entry =
    if (Entry.ItemId = ItemId):
        inventory_entry{ItemId := ItemId, Quantity := Entry.Quantity + Amount}
    else:
        Entry

AddItem(Agent : ?agent, ItemId : string, Amount : int) : void =
    if:
        RealAgent := Agent?
        Player := player[RealAgent]
        Player.IsActive[]
        OldTable := PlayerStatsMap[Player]
    then:
        Old := OldTable.PlayerInventory.Entries
        Known := for (Entry : Old, Entry.ItemId = ItemId) do Entry
        Bumped := for (Entry : Old) do AddToEntry(Entry, ItemId, Amount)
        Updated := if (Known.Length > 0) then Bumped else Old + array{inventory_entry{ItemId := ItemId, Quantity := Amount}}
        NewInv := player_inventory{Entries := Updated}
        if (set PlayerStatsMap[Player] = UpdateInventory(OldTable, NewInv)) {}
```

Arrays are built with for-expressions, never `+=` inside a loop (`datatypes`).

`UpdateInventory` must copy **every** other nested field on the shared table.
Remove: subtract; drop the entry at zero (or clamp). Always guard `set` in `if`.

### Quantity checks (on the manager)

```verse
# Entries is this player's saved player_inventory.Entries.
GetQuantity(Entries : []inventory_entry, ItemId : string)<transacts> : int =
    Matches := for (Entry : Entries, Entry.ItemId = ItemId) do Entry.Quantity
    Matches[0] or 0

HasItem(Entries : []inventory_entry, ItemId : string, Amount : int)<transacts> : logic =
    if (GetQuantity(Entries, ItemId) >= Amount) then true else false
```

Call `HasItem` before `RemoveItem`. Never trust the caller.

### Persist vs reset on join

After config is pushed, walk saved entries against config:

- **Persistable = true** — keep quantity; re-grant physical items if needed
- **Persistable = false** — write quantity `0`
- **Unknown id** — leave unchanged or drop (pick one policy)

### Re-granting physical items

Verse persistence does not restore Fortnite backpack items. Drive
`item_granter_device` from the digest on load / add. Removal typically uses
`conditional_button_device` (confirm members with `search_verse_digest`).

```verse
GrantItemsForEntry(Config : item_config, Agent : agent, Amount : int) : void =
    if (Amount <= 0):
        return
    Config.ItemGranter.SetNextItem(Config.GranterSlotIndex)
    for (I := 1..Amount):
        Config.ItemGranter.GrantItem(Agent)
```

### Placed device wiring (exact pattern — mirror wallet/level)

```verse
using { /Fortnite.com/Devices }
inventory_manager_device := class(creative_device):
    @editable PlayerManager : player_manager = player_manager{}
    @editable ItemConfigs : []item_config = array{}

    OnBegin<override>()<suspends> : void =
        PlayerManager.SubscribePlayerConnected(OnPlayerJoined)
        InitializeAllPlayerInventories()

    InitializeAllPlayerInventories() : void =
        Agents := Self.GetPlayspace().GetPlayers()
        for (Agent : Agents):
            if (CPlayer := PlayerManager.GetGamePlayer(Agent)?):
                OnPlayerJoined(CPlayer)
            # else: wait for PlayerConnected bus

    OnPlayerJoined(GamePlayer : game_player) : void =
        # 1) config first  2) persist init / re-grant  3) HUD
        GamePlayer.Services.InventoryManager.SetItemConfigs(ItemConfigs)
        GamePlayer.Services.InventoryManager.InitializeInventoryState(
            option{GamePlayer.MyAgent},
            ItemConfigs
        )
        GamePlayer.Services.InventoryManager.ShowHUD(GamePlayer.MyAgent)
```

**Order is mandatory:** `SetItemConfigs` → `InitializeInventoryState` → `ShowHUD`.
Reversing grants against an empty config list.

**HUD guard:** `var HudAdded : logic = false` so Subscribe + InitializeAll do not
stack two canvases.

### Runtime manager

`inventory_manager := class<unique>():` — holds `MyAgent`, config array,
optional canvas, persistence manager. Public API: `AddItem`, `RemoveItem`,
`GetQuantity`, `HasItem`, `ShowHUD` / `RemoveHud`. Add the field on
`game_player_services` so it exists before any device's `OnPlayerJoined`.

### Calling from gameplay

```verse
if (CPlayer := Manager.GetGamePlayer(Agent)?):
    if (CPlayer.Services.InventoryManager.HasItem("Key", 1)):
        CPlayer.Services.InventoryManager.RemoveItem("Key", 1)
```

Look up through the manager — do not assume a cached `game_player` without the
registry.

### Gotchas

- Same bus race as every system: Subscribe **and** InitializeAll walk.
- Handler signature must match `player_connected_to_game`.
- Persist row must already exist (`Init` on the manager ran first).
- Carry inventory in every shared-table `Update…` helper.
- Stable string `ItemId`; confirm granter APIs via digest.
