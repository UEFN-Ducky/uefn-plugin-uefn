---
description: "Turn Virtual Pointer on and off per player with the TouchMapping input mapping, stasis while it is on, device mapping, caveats and custom mappings"
metadata:
  label: "Enable and disable"
---

# Enable / disable Virtual Pointer

> **Snippets here are fragments.** The `using` block in this file's first code
> block applies to all of them — copy those imports (or start from the matching
> `verse_template_apply` pack) when pasting into a real `.verse` file.

## Enable

Virtual Pointer is enabled per player by adding the `TouchMapping` input mapping. Custom input maps must be added to players for any custom input to apply in game.

```verse
using { /Verse.org/Input }
using { /Verse.org/Input/UI }

AddTouchMapping(Player : player):void =
    if (PlayerInput := GetPlayerInput[Player]):
        PlayerInput.AddInputMapping(TouchMapping)
```

Once `TouchMapping` is added the player is in Virtual Pointer mode; gamepad players see the on-screen pointer.

Do it for players already present **and** for late joiners:

```verse
OnBegin<override>()<suspends>:void =
    Playspace := GetPlayspace()
    for (Player : Playspace.GetPlayers()):
        AddTouchMapping(Player)
    Playspace.PlayerAddedEvent().Subscribe(AddTouchMapping)
```

## Stasis (players cannot move)

For input-mechanism parity, **player and camera movement are disabled** when entering Virtual Pointer mode. If the player must still move while the mapping is active, release them:

```verse
using { /Fortnite.com/Characters }

ReleasePlayer(Player : player):void =
    if (Character := Player.GetFortCharacter[]):
        Character.ReleaseFromStasis()
```

`ReleaseFromStasis()<transacts>:void` lives on `fort_character`. Call it after `AddInputMapping(TouchMapping)`.

## Device mapping (how the pointer is defined)

| Platform | Pointer source |
|----------|----------------|
| Touch | Finger contact |
| Mouse and keyboard | Existing mouse pointer |
| Controller | Virtual on-screen pointer driven by the **left stick** |

## Caveats

- Does **not** work while the Fortnite game menus are open.
- `TouchMapping` and `PointerSelect` are **publishable** (FN ≥ 4100). `PointerZoom` is **Experimental** (FN ≥ 4120) and cannot be published.
- An `input_action` only fires while at least one `input_mapping` that references it is active on that player.

## Disable

Unsubscribing from `PointerSelect` stops screen-space coordinate delivery. Removing `TouchMapping` exits Virtual Pointer mode. You do **not** have to unsubscribe before removing the mapping.

```verse
RemoveTouchInput(Player : player):void =
    if (PlayerInput := GetPlayerInput[Player]):
        PlayerInput.RemoveInputMapping(TouchMapping)
```

Always also clean up in `OnEnd`:

```verse
var SubsByPlayer : [player][]cancelable = map{}

OnEnd<override>():void =
    for (Player -> Subs : SubsByPlayer):
        for (Sub : Subs):
            Sub.Cancel()
        if (PlayerInput := GetPlayerInput[Player]):
            PlayerInput.RemoveInputMapping(TouchMapping)
    set SubsByPlayer = map{}
```

## Custom mappings

For custom `input_mapping` / `input_action` assets see Epic's "How to Add Player Input". Confirm asset names via the Assets digest (`list_verse_types(digest="assets")`) — never invent them.
