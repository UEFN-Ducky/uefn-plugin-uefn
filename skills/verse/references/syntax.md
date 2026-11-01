---
description: "Verse language reference — types, effects, control flow, classes, concurrency, the 43.00 dot forms (if. / spawn. / array. / option.), `of` with an archetype block, the indented array: block, the first(X : Xs){X} macro"
metadata:
  order: 2
  label: "Verse syntax reference"
  default_enabled: false
  load_condition: "Writing non-trivial Verse — control flow, classes/structs, options/failure, or concurrency"
---

## Verse syntax reference (cheat-sheet)

Language syntax below is stable. **API names, types, and signatures are not here —
confirm those in the `digests` reference**, and let `workspace_list_verse_errors`
catch mistakes.

This is the one-page quick reference. For depth, load the topic file: **`classes`**
(specifiers, members, subclassing), **`control_flow`** (if/for/loop/case),
**`async`** (suspends/spawn/race/Sleep — async vs not), **`effects`**
(failure/options), **`devices`** (`@editable`/events/agents), **`datatypes`**
(containers/math), **`persistence`** (weak_map), **`ui`** (canvas/widgets),
**`modules`** (using/module layout).

### Bindings & mutation
- `X := expr` — immutable definition (type inferred).
- `X : t = expr` — typed constant; `var X : t = expr` — mutable, reassign with `set X = expr`.
- Compare with `=` (equal) and `<>` (not equal) inside a failure context, e.g. `if (A = B):`.

### Types
- Scalars: `int`, `float`, `logic` (`true`/`false`), `string`, `char`, `void`, `any`.
- `[]t` array, `[k]v` map, `?t` option, `tuple(a, b)`. Array index and `Map[Key]` are **failable**.
- `option`: empty `false`, or a value; unwrap with `X?` (fails if empty). Build with `option{X}`.

### Effects (on a function, in `<>`)
`<suspends>` async · `<decides>` can fail (call with `[]`, pair with `<transacts>`) ·
`<transacts>` rollback-safe (the default choice for getters/helpers) · `<reads>`
world/time reads · `<computes>` pure · `<converges>` pure + terminates (field
initialisers). **No specifier = `no_rollback`**: such a function cannot be called
inside `if (…)`, `if:`, `for` filters, `[]` or a `<decides>` body (E3512). Access:
`<public> <private> <internal> <protected>`; also `<override> <final> <native>
<constructor>`. Details: `effects`; error catalogue: `compile_errors`.

### Hard syntax rules the compiler enforces
- Signature and `=` on **one line** (splitting parameters across lines is E3104).
- `_` is reserved (only legal as the `case` default) — never a binding name.
- Never name a binding `Distance`, `Dot`, `Cross`, `Normalize`, `Lerp`, `Floor`, `Min`, `Max`, `Print`, `Sleep` (ambiguity E3588).
- Tuples index with `T(0)`; arrays/maps with failable `A[0]`.
- `int / int` is failable and yields `rational`; convert with `* 1.0` and `Floor[]`.
- Array literal is `array{…}`. On 43.00 an indented `array:` block with one element per line is also an array (`Many:[]int = array:` + `1` / `2` / `3` lines compiles); on 42.x it built tuples (3509). One line per element; never `array: 1, 2`.
- Field initialisers are literals/archetypes only — never a call (E3582).
- An empty body is `if (set M[K] = V) {}` on **one line**; `if (…):` followed by `{}` on the next line is parse error 3100 "Expected expression, got {".
- A field or local may not share a name with a module (folder) in the project: `var Progression : ?xp_awarder` next to a `Verse/Progression/` folder is E3532 ambiguous.

### Control flow (blocks are `:` + indent, or `{ …; … }`)
```verse
using { /Verse.org/Simulation }

if (Cond):
    DoThing()
else:
    DoOther()

for (Item : Collection):
    Print("{Item}")

for (I := 0..9):        # inclusive range
    HandleIndex(I)

loop:
    if (Done?):
        break
```
- `case (X):` with `Pattern => expr` branches and `_ =>` default.
- `return X` exits a function; string interpolation is `"{Expr}"`.

### Short forms that compile on 43.00 (verified Nov 1 2026)

They appear in no release note. They work and are fine to read in tutorials, but our
house style (`code_style`) keeps the long forms in new code.

| Form | Means | Long form |
|------|-------|-----------|
| `if. A.Length = 1 then Print("one")` | one-line `if` (statement) | `if (A.Length = 1) then Print("one")` |
| `V:int = if. O? > 5 then 1 else 0` | one-line `if` as a value | `if (O? > 5) then 1 else 0` |
| `spawn. Later()` | start a task | `spawn{ Later() }` |
| `A:[]int = array. 7` | one-element array | `array{7}` |
| `O:?int = option. 7` | an option | `option{7}` |
| `Area := TakeBox of vp_box:` + indented `W := 2.0` / `H := 3.0` | call with one archetype argument built from the indented block (`Entity.SetLocalTransform of transform:` + `Translation := …`) | `TakeBox(vp_box{W := 2.0, H := 3.0})` |
| `first(X : Xs) { X }` | first element of an **array** that passes the filters (`first(X : Xs, X > 2) { X }`); `<decides>`, fails when none match, so call it in a failure context | `Xs[0]` or a `for` |
| `first(C : Gen) { C }` | first element of a **generator** (`FindDescendantComponents`); **not failable** (alone in an `if` it is 3513). Tutorials write `if (true?, C := first(C : Gen) { C }):` | `for (C : Gen) { …; break }` |

`first` must have a body: `first(X : Xs)` with no `{ … }` is 3502 "Can't use built-in macros
other than to invoke them".

### Classes / structs / enums / interfaces
```verse
my_widget := class:
    var Count : int = 0
    Bump():void = set Count = Count + 1

point := struct:
    X : float
    Y : float

team_color := enum{Red, Blue}        # not `team`: that clashes with /Verse.org/Simulation (3532)

healer := interface:
    Heal(Agent : agent):void
```
- Subclass a device: `my_device := class(creative_device):`. Instantiate: `point{X := 1.0, Y := 2.0}`.
- UEFN entry point is `OnBegin<override>()<suspends>:void =` on a `creative_device`.
- `@editable Field : trigger_device = trigger_device{}` exposes a Details-panel device ref (wire it in UEFN, or with `wire_verse_device_ref` when online).

### Concurrency (inside a `<suspends>` context)
- `branch { F() }` — background task **cancelled when the scope exits** (default inside `<suspends>` code).
- `spawn { F() }` — independent task that outlives the caller; the only option from a sync handler.
- `sync:` run all, wait for all (tuple of results) · `race:` first wins, others **cancelled** · `rush:` first wins, others **keep running**.
- `Sleep(Seconds : float)<suspends>` waits. Subscribe to events: `Device.SomeEvent.Subscribe(Handler)` — event and handler shapes come from the digest.
