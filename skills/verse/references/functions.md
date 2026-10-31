---
description: "Functions in Verse — anatomy, parameters and returns, your own <transacts><decides> checks, Await payloads, extension functions, ToString overloads, generic functions with where, function types (arrow vs type{} with effects), function values and callback arrays, comparator sorting, and function wrappers"
metadata:
  order: 7
  label: "Functions — checks, extensions, generics, function values"
  default_enabled: false
  load_condition: "Writing a function that can fail, an extension function, a generic function, a ToString for your type, storing or passing a function as a value (callbacks, comparators, handlers), or making functions with different arguments fit one shape"
---

## Functions

Snippets are members of a device or class unless they start with `using` (a
module-level `var` must be a `weak_map` — `modules`).

### Anatomy

`OnBegin<override>()<suspends> : void =` reads name, specifiers (`<override>`),
parameters `( )`, effects (`<suspends>`), return type.

- Arguments match parameters **by position and type**:
  `RunBombTimer(GetRandomFloat(5.0, 15.0), Agent)` for
  `RunBombTimer(Duration : float, Agent : agent)`; swapping them is a type error.
- A non-`void` function returns a value on **every** path; a bare `return` is only
  legal in a `void` function. Stub a new function with `return` / `return false` so
  the file builds while you fill it in.
- `X := SomeEvent.Await()` waits for the event and returns its payload
  (`Agent := Button.InteractedWithEvent.Await()`).

### Your own check that can fail

Declare `<transacts><decides> : void`, list bare conditions in the body (no `if`),
call it with `[]`, flip it with `not`. Reading class fields — including `var`s — is
fine inside it.

```verse
var PressCount : int = 0
var Threshold : int = 42

IsBombDefused()<transacts><decides> : void =
    PressCount >= Threshold

# caller
if (not IsBombDefused[]):
    Explosive.Explode(Agent)
```

A check with several conditions reads better as a named function than as a long
`if:` block:

```verse
CanEscape(Agent : agent, GoldCount : int)<transacts><decides> : void =
    FortCharacter := Agent.GetFortCharacter[]
    FortCharacter.IsCrouching[]
    GoldCount = GoldNeeded
    Switch1.GetCurrentState[]
    not Switch2.GetCurrentState[]
```

### Extension functions

Put the receiver before the name so the call reads `Action.ToInt()`:

```verse
(Action : rps_action).ToInt()<transacts> : int =
    case (Action):
        rps_action.Rock => 0
        rps_action.Paper => 1
        rps_action.Scissors => 2

(Seconds : float).ToTimecode()<transacts> : string = …   # "mm:ss.cc"
```

### `ToString` for your own types

Define `ToString(Value : my_type)<transacts> : string` and `"{Value}"` uses it
automatically inside string braces. Without one, `"{Value}"` fails with "No
overload of the function ToString".

### Generic functions

`where` lets one function take any type that meets a rule:

```verse
# A copy of Map without KeyToRemove. Session maps only — never on a persistence weak_map.
(Map : [KEY]VALUE).RemoveKey(KeyToRemove : KEY where KEY : subtype(comparable), VALUE : type) : [KEY]VALUE =
    var NewMap : [KEY]VALUE = map{}
    for (Key -> Value : Map, Key <> KeyToRemove, set NewMap[Key] = Value) {}
    NewMap
```

A type can also be passed as an argument:
`GeneratePoolFromTag(player_spawner_tag, player_spawner_device)` for a parameter
`t : subtype(creative_object)`, then cast with `t[Object]`. Generic **classes**:
`classes`.

### Function types

The arrow form only fits functions with **no effects**. Anything with
`<transacts>`, `<decides>` or `<suspends>` needs the `type{...}` form — a function
signature with `_` as the name (parameter names optional):

```verse
AddPoints(A : int, B : int) : void = Print("{A + B}")
LessThan(A : int, B : int)<transacts><decides> : void = A < B
WaitASecond()<suspends> : void = Sleep(1.0)

OnPair : tuple(int, int) -> void = AddPoints                         # arrow: several parameters in a tuple
OnPair2 : type{_(:int, :int) : void} = AddPoints                     # same type, signature form
Compare : type{_(:int, :int)<transacts><decides> : void} = LessThan  # effects need the signature form
Delay : type{_()<suspends> : void} = WaitASecond

OnPair(0, 3)
if (Compare[0, 3]):                  # <decides> values are called with []
    Print("less")
spawn{ Delay() }                     # <suspends> values: spawn, or call directly in <suspends> code
```

- Write the name **without** `()` to refer to a function; with `()` you call it.
- A named alias keeps signatures readable:
  `player_connected_to_game <public> := type{_(GamePlayer : game_player) : void}`
  (our `player_manager` event bus).

### Callbacks

A field of a function type stores behaviour another system supplies — this is
how our `player_manager` `Subscribe*` hooks work:

```verse
var PlayerConnectedToGame <private> : []player_connected_to_game = array{}

SubscribePlayerConnected<public>(Callback : player_connected_to_game) : void =
    set PlayerConnectedToGame += array{Callback}      # rare, one-off registration

# on join:
for (Callback : PlayerConnectedToGame):
    Callback(NewGamePlayer)
```

Use the existing `player_manager` hooks and `?option` provider slots before adding
new callback lists (`sys_architecture`).

### Comparators

A sort that takes its rule as a function needs no `if` chain: Epic's merge sort
community snippet takes a `<transacts><decides>` comparator, so
`MergeSort(Scores, GreaterThan)` sorts highest first. The comparator's return type
must match the one the sort declares.

### Function wrappers

When one class must call many functions that take different fixed arguments
(a settings toggle that drives both a per-player save and a global VFX switch),
wrap each so they share one `Call(Value)` shape. The wrapper stores the fixed
arguments:

```verse
# Content/Archetypes/func_wrappers.verse — generic classes, helpers below them
func_wrapper_base<public>(p : type, ret : type) := class<abstract>:
    Call<public>(P : p) : ret

func_wrapper<public>(p : type, ret : type) := class(func_wrapper_base(p, ret)):
    Func<public> : type{_(:p) : ret}
    Call<override>(P : p) : ret = Func(P)

func_wrapper_lhs<public>(lhs : type, p : type, ret : type) := class(func_wrapper_base(p, ret)):
    Func<public> : type{_(:lhs, :p) : ret}
    LHS<public> : lhs
    Call<override>(P : p) : ret = Func(LHS, P)

WrapFunc<public>(Func : type{_(:p) : ret} where p : type, ret : type) : func_wrapper(p, ret) =
    func_wrapper(p, ret){Func := Func}

WrapFuncLHS<public>(Func : type{_(:lhs, :p) : ret}, LHS : lhs where lhs : type, p : type, ret : type) : func_wrapper_lhs(lhs, p, ret) =
    func_wrapper_lhs(lhs, p, ret){Func := Func, LHS := LHS}
```

- Several fixed arguments travel as one tuple, so the wrapped function takes a
  tuple parameter: `SetLogic(OwnerAndKey : tuple(agent, string), Value : logic) : void`.
- `WrapFuncLHS(SetLogic, (Owner, "music"))` and `WrapFunc(SetVfx)` are both a
  `func_wrapper_base(logic, void)` one widget class can call.
- Right-hand, both-sides and "ignore p" variants follow the same pattern.
- Worth it when one class drives many unrelated setters; for two or three, a small
  `if` is simpler.

### Message helpers

UMG text fields take `message`, not `string`:

```verse
S2M<public><localizes>(S : string) : message = "{S}"
operator'+'<public><localizes>(M1 : message, M2 : message) : message = "{M1}{M2}"
```

Gatherable (translated) copy uses named `<localizes>` messages instead —
`localization` skill, `ui_ready`.
