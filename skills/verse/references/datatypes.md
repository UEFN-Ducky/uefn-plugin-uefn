---
description: "Data — scalars, arrays/maps/tuples/options, bindings & mutation, arithmetic, string/number formatting, and collection operations (Length, iteration, +=)"
metadata:
  order: 8
  label: "Types, containers & operations"
  default_enabled: false
  load_condition: "Working with numbers/strings/arrays/maps/tuples, mutating state (var/set), or doing math/formatting"
---

## Types, containers & operations

Type names are **lowercase**. Language types are stable; engine/gameplay types
(`vector3`, `agent`, `trigger_device`) come from the digests.

### Scalars

| Type | Notes |
|------|-------|
| `int` | whole numbers |
| `float` | decimals — literals need a dot: `1.0`, `3600.0` |
| `logic` | boolean: `true` / `false`. Test with `X?` in a failure context |
| `string` | text, `"…"`, interpolate with `"{Expr}"` |
| `char` | single character |
| `void` | no value (common return type) |
| `any` | top type (rare) |

`int` and `float` don't auto-convert — write `float` literals with `.0`, and go
`float → int` with `Floor[…]` / `Round[…]` / `Int[…]` (failable, use `[]`):

```verse
if (Value := Floor[Hours]):
    set TempHours = Value
```

### Bindings & mutation

```verse
X := expr                 # immutable, type inferred
X : t = expr              # immutable, typed
var X : t = expr          # mutable
set X = expr              # reassign a var
set Count += 1            # compound: += -= *= /= also work
```

- `:=` defines; `=` inside a failure context **compares**. Don't confuse them.
- Fields follow the same rule: `var Count : int = 0` vs `MaxCount : int = 10`.

### Containers

| Form | Type | Literal | Access |
|------|------|---------|--------|
| Array | `[]t` | `array{}`, `array{A, B}` | `Arr[Index]` — **failable** |
| Map | `[k]v` | `map{}` | `Map[Key]` — **failable** |
| Tuple | `tuple(a, b)` | `(A, B)` | `T(0)` — parentheses, not failable (`T[0]` is for arrays) |
| Option | `?t` | `false`, `option{X}` | `X?` — **failable** |

```verse
var UpdatedCurrencies : []currency_data = array{}
var PlayerStatsMap : weak_map(player, game_player_table) = map{}
@editable PropDisguises : []disguise_device = array{}
```

- All indexed access **fails** on a bad key/index → use inside `if`/`for` (see the
  `effects` reference).
- `weak_map(player, v)` is the persistence map keyed by player — see the
  `persistence` reference.

### Array operations

```verse
Arr.Length                                  # element count (int)
set UpdatedCurrencies += array{NewEntry}    # append one item (builds a new array)
for (Item : Arr):                           # iterate elements
    Use(Item)
for (I := 0..Arr.Length - 1):               # iterate indices
    UseAt(I)
if (First := Arr[0]):                       # safe first element
    Use(First)
Pick := GetRandomInt(0, Arr.Length - 1)     # random index (with /Verse.org/Random)
```

**Build arrays with a `for` expression**, never with `+=` inside a loop. Each `+=`
copies the whole array, so appending N items one at a time costs about N²/2
copies — a lag source in big levels. The last line of each pass is the element;
head filters drop passes:

```verse
Numbers := for (X := 0..42) do X
Alive := for (Agent : Agents, FortCharacter := Agent.GetFortCharacter[], FortCharacter.IsActive[]) do Agent
set ActiveDucks = for (Index -> Duck : Shuffle(PropManipulators), Index < NumDucks):
    Duck.ShowProps()
    Duck
```

`+=` is fine for a rare one-off append (registering a callback, adding one item).

More array methods (`/Verse.org/Verse`, no `using`; all return a new array):

| Method | Returns | Fails when |
|--------|---------|------------|
| `Arr.Find[Item]` | index of the first match | not found |
| `Arr.RemoveFirstElement[Item]` / `Arr.RemoveAllElements(Item)` | array without it | first form: not found |
| `Arr.RemoveElement[Index]`, `Arr.Remove[Start, Stop]` | array without those | bad index |
| `Arr.Insert[Index, Items]`, `Arr.ReplaceElement[Index, Item]` | changed array | bad index |
| `Arr.Slice[Start, Stop]` / `Arr.Slice[Start]` | part of the array | bad index |
| `Arr.ReplaceFirstElement[Old, New]` / `Arr.ReplaceAllElements(Old, New)` | changed array | first form: not found |

Element type must be `comparable` for the find/remove/replace-by-value forms.
`set Arr[I] = X` fails unless index `I` already exists — append instead.
`Shuffle(Arr)` (`/Verse.org/Random`) returns a random order; shuffle then take the
first N to pick N distinct items. Sorting takes a comparator function (`functions`).

### Maps

```verse
var StartTimes : [agent]float = map{}                     # usually a var
Names : [int]string = map{0 => "Zero", 1 => "One"}        # fixed pairs use =>

if (set StartTimes[Agent] = GetSecondsSinceEpoch()) {}    # write: failable
if (StartTime := StartTimes[Agent]):                       # read: fails if absent
    Print("{StartTime}")
for (Key -> Value : StartTimes):                           # iterate
    Print("{Value}")
```

- Keys must be comparable: `int`, `float`, `string`, `agent`, `player`, enums, and
  classes marked `<unique>`. Devices are not comparable (3509) — key by index.
- Maps cannot be `@editable`; arrays can.
- There is no in-place remove: rebuild without the key
  (`for (K -> V : Map, K <> Gone, set NewMap[K] = V) {}`, or the generic
  `RemoveKey` in `functions`). **Session maps only** — never remove keys from a
  persistence `weak_map` (`persistence`).

### Tuples

Multiple values without a named type; index positionally with **parentheses**:

```verse
Args : tuple(agent, float) = …               # e.g. input_trigger_device.ReleasedEvent payload
Agent := Args(0)
HeldSeconds := Args(1)
```

Note: `/UnrealEngine.com/Temporary/SpatialMath` `GetYawPitchRollDegrees()` returns
an **array** `[]float` (index with failable `YPR[0]` inside an `if`), while the
`/Verse.org/SpatialMath` overload returns `tuple(float, float, float)` (`YPR(0)`).
Check which one your `using` brings in.

### Arithmetic & comparison

- `+ - * /` on numbers. **`/` on two `int`s is failable and yields `rational`**,
  not `int` — it only compiles inside a failure context and cannot be passed where
  an `int` is expected. Convert to float first (`X * 1.0`) and use `Floor[]`:
  `if (Mins := Floor[(Total * 1.0) / 60.0])`.
- `int * float` gives a `float` — that is how `* 1.0` converts. `+`, `-` and `/`
  between an `int` and a `float` do not compile ("no match for int / float").
- `Floor[X] or 0` supplies a value when the failable call fails.
- Compare: `< <= > >=`, and `=` / `<>` (equal / not-equal) **in a failure
  context**: `if (Found = false):`, `for (…, Key <> OutAgent):`.
- Combine: `and`, `or`, `not` — `if (Dist <= Range and Dist < ClosestDistance):`.
- Handy math (compile-verified): `Abs`, `Max`, `Min`, `Clamp`, `Floor[]`, `Round[]`,
  `Int[]`, `Sqrt`, `Sin`, `Lerp`, `Distance(A, B)`, `GetRandomInt`. `Abs` and
  `ConcatenateMaps` are compiler intrinsics that the digests do not list but that
  compile fine. Never name your own bindings after these functions (`Distance := …`
  is E3588).

```verse
TempH := Max(0.0, Health - Damage)
Dist := Distance(TowerPos, PropPos)
```

### Strings & number formatting

Interpolation embeds any expression; build display strings by hand (e.g. a
time formatter, or currency scaling):

```verse
"{MinutesString}:{SecondsString}"
var HoursString : string = if (TempHours < 10) { "0{TempHours}" } else { "{TempHours}" }
FlagText := if (Flag?) then "on" else "off"     # there is no ToString(logic); branch instead
```

Array literals are `array{1, 2, 3}`. The `array:` block form builds a **tuple per
line**, which is E3509 when assigned to `[]int`.

`SomeString.Length` gives character count. For on-screen text use a `<localizes>`
`message` helper, not a raw `string` (see the `devices` reference).

### Math/spatial types (from the digests)

`vector3{X:=, Y:=, Z:=}`, `rotation`, `transform`, `vector2` for UI sizes. Read
world position via `Prop.GetTransform().Translation`; move with
`PropObject.MoveTo(TargetPos, Rotation, Time)` / `MoveTo(...)` inside a
`<suspends>` loop. Exact members live in `UnrealEngine.digest.verse` — search
before using.
