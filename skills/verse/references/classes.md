---
description: "How to declare classes, structs, enums, interfaces — every specifier, members, methods, subclassing, parametric types"
metadata:
  order: 3
  label: "Classes, structs, enums & specifiers"
  default_enabled: false
  load_condition: "Creating or subclassing a class/struct/enum/interface, or unsure which class specifier (<concrete>/<unique>/<final>/<persistable>) to use"
---

## Classes, structs, enums, interfaces

> **Snippets here are fragments.** The `using` block in this file's first code
> block applies to all of them — copy those imports (or start from the matching
> `verse_template_apply` pack) when pasting into a real `.verse` file.

Everything here matches the project's own `Verse/**` files — the shapes below
compile. **API type names still come from the digests**, only the *syntax* is here.

### The definition operator

A type is a name bound with `:=` to a `class`/`struct`/`enum`/`interface`/`module`
body. The body is `:` + indent, **or** `{ … }` braces — both are valid Verse.

```verse
using { /UnrealEngine.com/Temporary/UI }

my_thing := class:            # indent style
    Field : int = 0

my_thing := class{ Field : int = 0 }   # brace style — same thing
```

### class — the specifier menu

```verse
name <accessor> := class<spec><spec>(Superclass, Interface…):
    <members>
```

Specifiers and what each buys you:

| Specifier | Meaning / when to use |
|-----------|-----------------------|
| `class(creative_device)` | **A placed device.** Subclass of `creative_device`; gets `OnBegin`, shows in UEFN with `@editable` fields. `player_manager := class(creative_device):` |
| `class(tag)` | A **tag** for `FindCreativeObjectsWithTag(collectable_coins)` (pass the tag **type**; `GetCreativeObjectsWithTag` and the tag-instance overload are deprecated in 42.40). Write it `collectable_coins := class(tag){}` |
| `class()` / `class:` | Plain class — a helper/manager you `new` yourself. `save_service := class():` |
| `<concrete>` | **Every field has a default**, so it can be made with `{}` and used as an `@editable` struct or array element. `tower_data := class<concrete>():` |
| `<unique>` | **Reference identity** — instances compare with `=` / `<>` and can be map keys; needed for stateful helper objects. `game_player := class<unique>():` (devices are **not** comparable — track them by index, 3509) |
| `<final>` | Cannot be subclassed. Pair with `<persistable>`. |
| `<persistable>` | Instances can be stored in a `weak_map` and survive between sessions. **Must** be `<final>` and hold only persistable data. `player_level := class<final><persistable>:` → see the `persistence` reference. |
| `<abstract>` | Cannot be built with `{}`; may declare functions without a body that every concrete child must define. |
| `<transacts>` | Instances are usable inside `<transacts>` contexts (rollback-safe). Combines as `class<concrete><unique><transacts>()`. |

Specifiers stack: `mini_game_instance := class<concrete><unique><transacts>():`.

### Members: data & methods

```verse
top_hud_system := class<unique>():
    # immutable field, has a default → part of a <concrete> archetype
    MaxCount : int = 10
    # mutable field — reassign later with `set`
    var Count : int = 0
    # @editable → shows in the UEFN Details panel (device classes only)
    @editable Trigger : trigger_device = trigger_device{}
    # method: Name<access>(params)<effects> : ret = body
    Bump<public>() : void = set Count = Count + 1
    GetCount<public>()<transacts> : int = return Count
```

- Access specifiers: `<public> <private> <internal> <protected>` (default is
  most-restrictive within the module). Put them right after the name:
  `AddKill<public>(): void = …`.
- `var` = mutable; without `var` the field is a constant. `@editable var Price : int = 100`
  is both editor-exposed **and** mutable.
- One-line methods: `ResetKills<public>(): void = set KillCount = 0`.

### Instantiating (the archetype `{ … }`)

Make an instance by writing the type name then `{ FieldName := Value, … }`. Fields
with defaults may be omitted:

```verse
point{X := 1.0, Y := 2.0}       # set fields
player_level{}                  # all-default (needs every field defaulted)
texture_block{ DefaultImage := Textures.T_Empty }   # override one field
```

Containers use the same form: `array{}`, `map{}`, `array{A, B}`.

### `<constructor>` functions (custom makers)

A function that returns a fresh instance can be a `<constructor>`; it uses the
archetype body form (`:= type:`), which lets it set fields positionally:

```verse
MakePlayerWallet<constructor>(OldWallet: player_wallet, NewCurrencies: []currency_data) <transacts> := player_wallet:
    Currencies := NewCurrencies
    # …carry over other fields from OldWallet
```

For most helper "make a copy with one field changed" cases a plain `<transacts>`
function that returns `type{ … }` is enough — reserve `<constructor>` for when you
want the archetype body form.

### struct — value type

`struct` is a **value** (copied on assignment, no identity). Use it to group
`@editable` device refs or plain data. Same specifier `<concrete>` applies.

```verse
leaderboard_entry := struct:
    Name : string
    Score : int

prop_game_timers <public> := struct<concrete>():
    @editable HubTimer <public> : timer_device = timer_device{}
    @editable GameTimer <public> : timer_device = timer_device{}
```

class vs struct: pick **struct** for plain grouped data/config passed by value;
pick **class** when you need identity (`<unique>`), inheritance, persistence, or
it's a device (`creative_device`).

### enum

```verse
game_phase := enum{ Warmup, Active, Ended }
team_color := enum{ Red, Blue }
```

Never reuse an engine type name for your own type: `team := enum{…}` clashes with
`/Verse.org/Simulation`'s `team` in every device file (3532, ambiguous — verified
with verse-lsp, 42.40). Treat `player`, `agent` and `entity` the same way.

Refer to a value as `game_phase.Active`; compare with `=` / `<>`; match with `case`
(a `case` that lists every value needs no `_`; one over `int` / `string` does —
`control_flow`). An `@editable` enum field is a Details dropdown:
`@editable StartPhase : game_phase = game_phase.Warmup`.

Enums are bare: write the helpers you need beside them — `ToString` (used
automatically by `"{Phase}"`), `ToInt`, an int-to-enum converter (`functions`).
Do not add a sentinel value (`Size`) at the end: every `case` then needs an arm for
it and it shows in the Details dropdown.

### Inheritance and overrides

```verse
powerup := class<abstract><unique>:
    @editable EquipButton : button_device = button_device{}
    Name : string = "None"

    Init() : void =
        EquipButton.InteractedWithEvent.Subscribe(Equip)

    Equip(Agent : agent) : void = {}

    ApplyEffect(Target : agent) : void          # no body: every concrete child defines it

instakill_powerup := class<concrete><final>(powerup):
    Name<override> : string = "Instakill"       # fields can be overridden too

    Init<override>() : void =
        (super:)Init()                          # run the parent's version as well

    ApplyEffect<override>(Target : agent) : void =
        if (FortCharacter := Target.GetFortCharacter[]):
            FortCharacter.Damage(99999.0)
```

- One parent class; `<override>` on every function or field that replaces the
  parent's, including a parent function with no body.
- `(super:)Name()` calls the parent's version; if the direct parent did not
  override it, the call reaches the nearest ancestor that did.
- A variable of the parent type holds any child (`var Current : ?powerup = false`),
  and calls run the child's version.
- **Details shows a subclass picker** for an `@editable` field typed as an abstract
  parent: `@editable Powerups : []powerup = array{}` lets a designer choose a
  concrete child per element and edit its fields. The children must be
  `<concrete>`.

### interface

A class has one parent class but **any number of interfaces**, so behaviour shared
by unrelated classes lives in an interface.

```verse
edible := interface:
    Eat() : void =
        Print("Eaten")

fruit := class:
    Sweetness : float = 1.0

apple := class(fruit, edible){}                 # parent class first, then interfaces
sandwich := class(edible){}                     # interfaces alone are fine

TryEat(Food : fruit) : void =
    if (Meal := edible[Food]):                  # cast to the interface; fails if not edible
        Meal.Eat()
```

- An interface works as a field, variable or array type (`Lunch : edible = sandwich{}`).
- An interface can hold fields, `var`s included, with defaults
  (`var Count : int = 0`); implementing classes `set` them like their own.
- When two interfaces declare the same name, qualify it:
  `(initializable:)Init<override>() : void =`, call `(resettable:)Init()`, read
  `(resettable:)Counter`. Qualifying even without a clash makes the source obvious.
- Scene Graph components must inherit `component`, so an interface is how a
  component gets shared behaviour (`design_patterns`).

### Generic (parametric) classes

A class can take type parameters; a type used as a map key must be
`subtype(comparable)`:

```verse
scoreboard(key_type : subtype(comparable), score_type : type) := class:
    var Board : [key_type]score_type = map{}

    SetScore(Key : key_type, Score : score_type) : void =
        if (set Board[Key] = Score) {}

    GetScore(Key : key_type)<transacts><decides> : score_type =
        Board[Key]

# as a device field:
Scores : scoreboard(player, int) = scoreboard(player, int){}
```

**Parse order.** Anything that **names** a generic class — a class field of its
type, or a function whose signature returns or takes it — must be parsed after
the class: below it in the same file, or in a file or folder that sorts later.
Otherwise the build fails with 3502 "Can't access a function from a preceding
type", reported **at the generic class**, not where the cause is. Put generic
classes in a Content-level folder that sorts first (`Content/Archetypes/`, before
`Content/Verse/`) with helper functions below the classes in the same file. Code
that only uses one inside a function body is not affected; plain classes are not
affected. (Verified with verse-lsp, 42.40.) Pools and function wrappers built this
way: `design_patterns`, `functions`.

Generic functions (`where t : type`) are in `functions`.

### Subclassing a device — the canonical entry point

```verse
using { /Fortnite.com/Devices }
my_device := class(creative_device):
    @editable Trigger : trigger_device = trigger_device{}
    OnBegin<override>()<suspends>:void =
        Trigger.TriggeredEvent.Subscribe(OnActivated)
    OnActivated(Agent : ?agent):void =
        if (A := Agent?):
            Print("triggered")
```

See the `devices` reference for `@editable`, events, and agents/players; the
`async` reference for what `<suspends>` unlocks.

### `concrete_subtype` fields (validator enforced from v42.10)

`@editable Kinds : []concrete_subtype(entity) = array{}` lets a designer pick classes to instantiate with `Kind{}`. From v42.10 the editor validates that **every class placed in such a field is itself `<concrete>`** (all fields have defaults). A non-concrete class there fails validation when you republish, even though already-published islands keep working. Make your own prefab/item classes `class<concrete>` (or `<final><concrete>`) before exposing them this way; stock `/Fortnite.com/Weapons` and `/Fortnite.com/Items` classes already are.
