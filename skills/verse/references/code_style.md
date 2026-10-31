---
description: "House Verse code style — folder and file layout, member order inside a device, formatting (spacing, spawn{}, else if, array{}), naming (snake_case types, PascalCase members, verb-first functions, roles), access and effects defaults, constants vs @editable, and the tutorial quirks never to copy"
metadata:
  order: 3
  label: "Code style — how our Verse is written"
  default_enabled: false
  load_condition: "Writing or reviewing any new .verse file, naming types/functions/fields, formatting code, or copying code from a tutorial or Epic page into the project"
---

## Code style — how our Verse is written

Every template pack is written this way; new code matches it so packs, agents and
people read each other's files without friction. When code from a video or Epic
page is copied in, it is re-written in this style first.

### Layout

- One system per folder (`Verse/Economy/`, `Verse/Shop/`); the file name is the
  main class name (`economy_manager.verse` holds `economy_manager`).
- Generic (parametric) classes live in a Content-level folder that sorts first
  (`Content/Archetypes/`), with any helper functions **below** the classes in the
  same file (parse order — `classes`).
- Order inside a file: `using` lines → module-level types and constants → classes.
- Order inside a device or manager: `@editable` fields → constants → `var` state →
  `OnBegin` → public API → event handlers → private helpers.

### Formatting

```verse
using { /Fortnite.com/Devices }
using { /Verse.org/Simulation }

# Grants the starter loadout once per player.
starter_loadout_device := class(creative_device):
    @editable StartButton : button_device = button_device{}
    @editable Granters : []item_granter_device = array{}

    GrantDelaySeconds : float = 0.5
    var Granted : [agent]logic = map{}

    OnBegin<override>()<suspends> : void =
        StartButton.InteractedWithEvent.Subscribe(OnStartPressed)

    OnStartPressed(Agent : agent) : void =
        if (not Granted[Agent]):
            spawn{ GrantAll(Agent) }

    GrantAll(Agent : agent)<suspends> : void =
        Sleep(GrantDelaySeconds)
        for (Granter : Granters):
            Granter.GrantItem(Agent)
        if (set Granted[Agent] = true) {}
```

| Rule | Write | Not |
|------|-------|-----|
| Spaces around `:` and `=` in declarations | `Score : int = 0`, `OnBegin<override>()<suspends> : void =` | `Score:int=0` |
| Space after keywords | `if (X = 0):`, `for (Item : Items):`, `case (Phase):` | `if(X=0):` |
| `spawn` with braces | `spawn{ RunTimer(Agent) }` | `spawn. RunTimer(Agent)` |
| Arrays with braces | `array{Agent}` | `array. Agent` |
| `using` with braces | `using { /Verse.org/Random }` | `using. /Verse.org/Random` |
| Chained conditions | `else if (Holding[Agent]):` | `else. if:` |
| `else` body indented on its own line | `else:` + indented body | `else. Print(...)` |
| `@editable` on the same line as its field | `@editable Lock : lock_device = lock_device{}` | — (both build; one line is our style) |
| Indent | 4 spaces | tabs, 2 spaces |
| Comments | `#` explaining **why** | `//`; comments restating the code |

### Naming

| Kind | Style | Examples |
|------|-------|----------|
| Types (classes, enums, interfaces) | `snake_case` | `economy_manager`, `rps_action`, `player_spawner_tag` |
| Fields, functions, locals, parameters | PascalCase | `BlueScore`, `GrantAll`, `Agent` |
| Functions | verb first | `GrantLoadout`, `GetPlayerSlot`, `ApplyEffect` |
| Event handlers | `On` + event | `OnStartPressed`, `OnPlayerRemoved` |
| Events | ends in `Event` | `StopEvent`, `RoundEndedEvent` |
| `logic` fields and `<decides>` checks | a question | `IsOpen`, `HasKey`, `CanEscape[]` |
| Manager roles | Manager / Tracker / Controller / Service | `progression_manager`, `player_time_tracker` |

- Spell names out: `Prop`, `Spawner`, `FortCharacter`, `Agent` — not `PM`, `OBJ`,
  `FC`, `A`. Spell-check them; they appear in Details and logs.
- Never `*_system`, `fortnite_*`, or "wallet" in a type name.
- Tags are `class(tag){}`: `player_spawner_tag := class(tag){}`.

### Access and effects

- `<public>` only on what another folder calls; manager state is `<private>`.
- Getters and helpers are `<transacts>` so callers can use them in `if` heads.
- A yes/no check that can fail is `<transacts><decides> : void` and is called with `[]`.
- Magic numbers become a named constant (`GrantDelaySeconds : float = 0.5`) or an
  `@editable` when a designer should tune them.

### Tutorial quirks never copied

`if(X=0):`, `else. if:`, `spawn. F()`, `array. X`, `using. /Path`, one- and
two-letter names, `Switch_1` underscores, misspelled names, a trailing `return` at
the end of `OnBegin`, scratch loops left in `OnBegin`, a `Size` value at the end
of an enum, `GetPlayers()` only at game start instead of our `player_manager`.
