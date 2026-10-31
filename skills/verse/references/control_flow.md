---
description: "Control flow — if / else, the if:/then:/else: block form, all for-loop shapes, loop/break, case, and how failure drives branching"
metadata:
  order: 4
  label: "Control flow — if, for, loop, case"
  default_enabled: false
  load_condition: "Writing branching or iteration — if/for/loop/case, ranges, map iteration, filters, or break/return"
---

## Control flow

Blocks are `:` + indent **or** `{ …; … }`. Everything below is used verbatim in
`Verse/**`.

### `if` — condition *or* failure

`if (…)` is a **failure context**: the parens can hold a `logic` test **or** a
failable expression whose success drives the branch. Bindings made in the head
are in scope in the body.

```verse
if (CurrentAmount >= Price):          # plain logic test
    Buy()
else:
    Deny()

if (MyPlayer := AllPlayers[Agent]):   # map lookup that may fail; binds MyPlayer on success
    Use(MyPlayer)

if (A := Agent?):                     # unwrap an option; body runs only if it held a value
    Print("{A}")
```

- Compare with `=` (equal) and `<>` (not-equal) **inside** a failure context:
  `if (Currency.CurrencyName = CurrencyName):`.
- Chain conditions with `and` / `or` / `not`: `if (Dist <= Range and Dist < ClosestDistance):`.
- `<>` is not-equal; `><` is not an operator. Strings compare only with `=` and `<>`.
- A `logic` needs `?` to become a test (`if (Done?):`); comparisons fail or succeed
  on their own.
- Chain a second test with `else if (…):`:

```verse
if (CanEscape[Agent, GoldCount]):
    Lock.Open(Agent)
else if (ConditionalButton.IsHoldingItem[Agent, 1]):   # key items are 0-based
    Lock.Open(Agent)
else:
    Print("Escape conditions not met")
```

### The `if: / then: / else:` block form

For **several** conditions that must *all* succeed, list them under `if:` and put
the success body under `then:`. This is the standard shape for player lookups:

```verse
if:
    RealAgent := Agent?
    Player := player[RealAgent]
    Player.IsActive[]
    OldTable := PlayerStatsMap[Player]
then:
    UsePlayer(Player, OldTable)
else:
    Print("Unable to resolve player")
```

Every line under `if:` is failable and evaluated in order; the first failure jumps
to `else:`. `then:`/`else:` are optional (bare `if:` with only the block runs the
body for side effects and swallows failure).

**Effect rule for anything inside `if (…)` / `if:` / `for (…)` heads:** every call
there must be rollback-safe. A helper declared with **no effect specifier** is
`no_rollback` and is a compile error (E3512) in these positions — give it
`<transacts>`, or bind its result to a local before the `if`. `<suspends>` calls
are never allowed in a head. See `effects` and `compile_errors`.

### `for` — every shape used here

```verse
# 1. iterate an array's elements
for (Button : Buttons):
    Button.InteractedWithEvent.Subscribe(BuyWithCurrency)

# 2. iterate a map as Key -> Value
for (Key -> Value : InputMap):
    if (Value?):
        set Count += 1

# 3. filter with a trailing failable clause (comma) — skips non-matching items
for (Key -> Value : AllPlayers, Key <> OutAgent):
    Remove(Value)

# 4. numeric range 0..N-1 (inclusive on both ends)
for (Index := 0..CurrencyIcons.Length - 1):
    Draw(Index)

# 5. nested loops for a grid
for (Row := 0..GridHeight - 1):
    for (Col := 0..GridWidth - 1):
        Cell(Row, Col)
```

- `A..B` is an **inclusive** range: `0..10` runs 11 times, `0..Count - 1` runs
  `Count` times, and `10..0` runs **zero** times (start must be ≤ end).
- `for (Index -> Item : Arr)` gives each element with its 0-based index on arrays
  (and key -> value on maps). On a generator (`FindCreativeObjectsWithTag`,
  `FindDescendantEntities`) it still compiles, but the left name is the element,
  not an `int` — make an array first (`Found := for (X : Gen) do X`) when you need
  indexes.
- The filter clause (form 3) is any failable expression; items that fail it are
  skipped, not aborted.
- `for` used as an expression builds an array (the last line of each pass is the
  element) — the way to build arrays without `+=` (`datatypes`).

### `loop` — infinite until `break`

`loop` runs forever; you leave it with `break`. It almost always lives in a
`<suspends>` function with a `Sleep` so it yields (see the `async` reference):

```verse
MovementLoop<private>()<suspends> : void =
    loop:
        if (not IsAlive? or not IsMoving?):
            break
        MoveOneStep()
        Sleep(MoveSpeed)      # yield each iteration — never a busy loop
```

Every `loop` must wait (`Sleep`, an `Await`) or reach a `break`. A loop with
neither is rejected by the compiler; one whose only `break` can never run
(`if (false?): break`) **compiles but crashes Verse at runtime**. Code after an
endless `loop` in the same function never runs — spawn long-lived loops from their
own function (`async`).

### `case` — match a value

```verse
case (Phase):
    game_phase.Active => StartActive()
    game_phase.Ended  => ShowResults()
    _ => DoNothing()          # _ is the default branch (the only place `_` is legal — never as a binding name)
```

- A `case` over an enum that lists **every** value needs no `_` (one there anyway
  is warning 2302, unreachable).
- A `case` over `int`, `string` or an open enum (42.40 ability enums) must end with
  `_ => …`; without it the case can fail (3512).
- An arm can hold several lines: put them indented under `Value =>`.

Use `case` for enums and fixed value sets; use `if`/`else` chains for ranges and
compound conditions.

### `return`, `break`, and expression results

- `return X` exits the enclosing function with `X`. Many one-liners skip it:
  `GetCount<public>() : int = Count`.
- `break` exits the nearest `loop`/`for`.
- Almost everything is an expression — `if` can produce a value:
  `var HoursString : string = if (TempHours < 10) { "0{TempHours}" } else { "{TempHours}" }`.
  The `then`/`else` keyword form also works:
  `if (TheLogic?) then "True" else "False"`.

### String interpolation

`"{Expr}"` embeds any expression: `Print("Added {Amount} {CurrencyName}")`. For
on-screen text use a `<localizes>` message helper (see the `devices` reference),
not raw strings.
