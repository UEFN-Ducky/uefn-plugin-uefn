---
description: "Verse compiler error catalogue — every Script error code agents actually hit (3512 no_rollback, 3582 divergent initialiser, 3593 internal module, 3588 ambiguous identifier, 3104, 3506, 3509, 3524, 3511, 3514, 3100, 3000, 3502, 9002, plus the 42.40 ability / event changes and the 43.00 changes: weak_map cap 6, asset-module accessibility, SendUp no_rollback, Self in initializers, LSP false positives, quest API renames) with the real cause and a compiling fix"
metadata:
  order: 3
  label: "Compile errors — code → cause → fix"
  default_enabled: false
  load_condition: "workspace_compile_verse or the UEFN build reported a Script error NNNN, or workspace_list_verse_errors names a file — load this before editing"
---

## Compile errors — code → cause → fix

Read the code number, jump to it, apply the fix at the reported line. Counts are
from real agent sessions (113 errors), so the first four cover most of what you
will see. **The offline LSP (`workspace_list_verse_errors`) cannot see 3512, 3582,
3593, 3588 or 3532** — only `workspace_compile_verse` finds them.

**43.00: the offline LSP is behind the compiler.** Verified on 43.00 (Nov 1 2026), it
reports two errors the UEFN build does not:

| LSP says | UEFN build | Do |
| --- | --- | --- |
| "Accessing instance member `X` from this scope is not yet implemented" on a field initializer that reads an earlier `<final>` field | compiles | trust `workspace_compile_verse` (`classes`) |
| "Only 4 persistent `var`s allowed (used 5/6)" | the 43.00 cap is 6, so 5 or 6 compiles | trust the build; the 7th is a real 3502 |
| "Unknown member `Await` in `listenable(…)`" (e.g. `TriggeredEvent.Await()`, `OnDamaged.Await()`), plus follow-on "Must be an array, map, or generator" / "Dynamic cast $unknown" | compiles (same build, 0 errors) | trust the build; `listenable(t)` still has `Await` |

When the two disagree, the `workspace_compile_verse` result is the truth.

**Rule: never "fix" a red squiggle on `listenable.Await()`.** On 43.00 the LSP marks every
`.Await()` on a listenable (`TriggeredEvent`, `SpawnedEvent`, `GrantEvent`, `DeactivateEvent`,
`OnDamaged`, `OnDied` …) as an error, plus the cascade errors after it. Run
`workspace_compile_verse`. If it reports 0 errors, leave the code alone.

### 43.00 errors seen building quests and health code (real compiler)

| Error | Cause | Fix |
|-------|-------|-----|
| 3100 `vErr:S88: Expected expression, got "do" in indented block` | a multi-line `for:` filter block followed by `do:` on its own line | one line: `for (P -> M : Map, Cond) do M` |
| 3506 Unknown member `AwaitRoundStart` in `entity` | tutorial helper, not a 43.00 API | delete it, or write your own wait |
| 3509 No overload of `operator'()'` … `(:generator(inventory_component), :type{0})` | indexing a **generator** (`FindDescendantComponents(...)[0]`) | iterate it, or `first(X : Gen) { X }` (`syntax`) |
| 3502 "Can't use built-in macros other than to invoke them" | `first(X : Gen)` without a body | `first(X : Gen) { X }` |
| 3513 "Expected an expression that can fail in the 'if' condition clause" | `first(…){…}` over a generator alone in an `if` (it can't fail) | add a failable clause (`if (true?, X := first(…){X})`), or bind it outside the `if` |
| 3512 "This first has the 'decides' effect" | `first(…){…}` over an **array** outside a failure context (it fails when empty) | call it in an `if`, or from a `<decides><transacts>` function |
| 3600 "Object archetype must initialize data member Categories" | raw `quest` + `has_quest_presentation` without `Categories` | pass `Categories := array{}` (`sys_quests`) |
| (no error, can't build) `has_icon.Icon` has no default | every category, presented quest and reward needs a texture | pass `Icon := Textures.T_X` from an imported texture at construction |

### 3512 — "calls a function that has the 'no_rollback' effect, which is not allowed by its context" (39 hits)

Cause: a function with **no effect specifier** is `no_rollback`; you called it inside
a failure context (`if (…)` head, `if:` block, `for` filter, `[]` argument, or a
`<decides>` body).

```verse
using { /Verse.org/Simulation }

# before
AliveCount() : int = …
if (AliveCount() = 0):                     # 3512

# fix — give the helper <transacts> (it only reads/writes fields)
AliveCount()<transacts> : int = …
if (AliveCount() = 0):

# or bind first
Alive := AliveCount()
if (Alive = 0):
```

Variants with the same code:

- "This archetype instantiation constructs a class that has the 'transacts' effect,
  which is not allowed by its context" — you built `foo{}` at **module scope**. Move
  it into `OnBegin` or a device field.
- "This invocation calls a function (`(/Verse.org/SceneGraph/entity:)SendUp`) that has
  the 'no_rollback' effect" (43.00 health pipeline) — `Target.SendUp(damage_event{…})`
  inside a `<transacts>` / `<decides>` function or an `if`. Make the sender a plain
  (no-specifier) function and call it on its own line (`sys_health_pipeline`).
- "This division can fail, but `F` does not have the `<decides>` effect" — integer
  `/` outside a failure context. Use `if (Q := Floor[(A * 1.0) / (B * 1.0)])`.
- "calls a function (`WaitForFirstPlayer`) that has effects that are not allowed" —
  a `<suspends>` call from a sync function. Add `<suspends>` to the caller or
  `spawn{}` it.
- "This invocation calls a function (`(/UnrealEngine.com/Abilities/ability:)Use`) that
  has the 'no_rollback' effect" — `Ability.Use(…)` inside `if (…)` or a `<decides>`
  function. Call it on its own line, then `if (Effect := Spawned?):` (42.40, verified).
  Same for `Sim.AddChatChannel(…)`: bind the result first.
- "Case might fail because its argument is an open enumeration type
  `fort_ability_attach_socket`, and doesn't have a default clause (e.g. _ => {})" —
  42.40 made `fort_ability_attach_socket` and `fort_target_query_affiliation`
  `<open>`; a `case` over them needs `_ => …` even when it lists every value.

### 3582 — "Divergent calls (calls that might not complete) cannot be used to define data-members" (17 hits)

Cause: a class field initialiser calls a function.

```verse
var Lanes : []int = ComputeLanes()      # 3582
var Lanes : []int = array{}             # fix; set Lanes = ComputeLanes() in OnBegin
```

Only literals, archetypes (`array{}`, `map{}`, `option{}`, `vector3{…}`, `my_class{}`)
and `<converges>` calls may initialise a field.

### 3593 — "Invalid access of internal module / scoped class from control scope" (16 hits)

**43.00:** modules that contain reflected assets default to project-wide accessibility,
so the asset-folder form of this error should mostly stop. It still applies to your own
nested code folders and to 42.x islands.

Cause: importing a **nested** Assets-digest module (`using { Materials.HexPlatforms }`)
or constructing a prefab (`EP_Weapon_Pistol{}`) that sits in a nested asset
folder, from another module. Assets.digest generates asset folder modules with
no access specifier (internal); the `scoped{…}` prefab class itself is scoped to
the whole island and is fine.

Fix: declare each folder on the path `<public>` in a file of the folder that
contains it (normally `module_declarations.verse`), rebuild, then import:

```verse
# Content/Verse/module_declarations.verse — prefabs in Content/Verse/ArmoryWeapons
ArmoryWeapons<public> := module:
```

Same for your own nested code folders. Full rule: `modules` → "Make a folder
`<public>`". Moving the asset to a top-level folder also works but breaks every
existing reference to it.

### 3588 / 3532 — "Ambiguous identifier; could be (…:)Distance, (/Verse.org/SpatialMath:)Distance" (9 hits)

Cause: you named a field, local or parameter the same as a module function
(`Distance`, `Dogs` twice in one module, …).

43.00 adds a new source: modules that contain reflected assets are now
**project-wide** by default, so asset names (and asset folder names) from anywhere in
the island can clash with your bindings and types. Rename yours, or qualify the asset
(`(/YourIsland/Materials:)M_Glow`), or narrow the `using` path (`modules`).

43.00: a field or local named `Last` (or another new extension name) is ambiguous with
`operator'.Last'` (the new `Array.Last[]`); rename it. Verified on 43.00: `var Last:float`
on a class and `Last := …` inside a method both fail ("could be (…:)Last, (/Verse.org/Verse:)operator'.Last'");
the same local in a module-level function still compiles. Use `PrevTime`, `LastLogin`, `LastSeen`.

Fix: rename the binding (`Dist`, `DistToTarget`). Never use these names for your
own bindings: `Distance DistanceSquared Dot Cross Normalize Lerp Sqrt Sin Cos Tan
Floor Ceil Round Int Min Max Clamp Print Sleep Exp Log Pow Err`. (`Err` is a Verse function:
`if (Err := Result.GetError[])` is 3588 + 3532 "ambiguous with function (/Verse.org/Verse:)Err";
name it `NavError` / `JoinError`.) Never reuse a
module-level name inside a function in the same module. Also clashes: a local
named like a field or method of the class it sits in, a local named like a
folder/module (`Run`, `Shop`, `Hub`…), and short generic names another file in
the same module already defines (`Slice`, `Made`, `Item`, `Data`). Use specific
names (`SliceAt`, `NewMat`, `Controller`).

### 3104 — "Dangling `=` assignment with no expressions or empty braced block on its right hand side" (5 hits)

Cause: a function signature split across lines, so the `=` ends a line with nothing
after it.

```verse
# before
OnHit(Agent : agent,
      Damage : float) : void =
# fix — one line
OnHit(Agent : agent, Damage : float) : void =
```

Also raised by an empty body: put at least one expression (or `{}`) after `=`.

### 3506 — "Unknown identifier `X`" / "Unknown member `X` in `entity`" (6 hits)

Cause: an invented API (`GetPlayspaceForEntity` on `entity` without the Playspaces
import, `NamedColors.White` with only the submodule imported) or a missing
`using`. Epic doc samples frequently omit imports.

Fix: `search_verse_digest("X")`; if present, add the `using` path shown. If absent,
it is almost certainly invented — but core intrinsics such as `Abs`,
`ConcatenateMaps`, `Max`, `Min` are not listed in the digests and still compile, so
the compiler's own "Unknown identifier" is the final word, not the digest. Common: `collision_point` / `FindSweepHits`
need `/Verse.org/SceneGraph`; `GetPlayspace()` needs `/Fortnite.com/Playspaces`;
`fort_character` needs `/Fortnite.com/Characters`; `animation_sequence` needs
`/Verse.org/Assets`; `color{}` needs `/Verse.org/Colors`.

42.40 variants (verified):

- "Unknown member `Subscribe` in `event(int)`" — **42.x only**: your own `event(t)` (or a
  UMG event field) has no `Subscribe` before 43.00; await it in a loop. On 43.00 it
  compiles (`events_subscriptions`).
  If the message adds "Did you forget to specify using { …/SomeFolder }", another
  folder defines a `Subscribe` extension on events — 43.00 rejects that one (below).
- **43.00 (3518):** "Multiple overloads of the function match the provided arguments (:int->void).
  Could be any of: function (/Verse.org/Verse/event:)Subscribe(:int->void) in package Verse
  / function (/YourIsland/Folder:)operator'.Subscribe'(:event(t),:t->void)" — your own
  `(Event:event(t) where t:type).Subscribe(…)` extension (Epic's interim tutorial helper)
  now clashes with the built-in at every call site (verified 43.00). Delete the
  extension; change `event_subscription` vars to `cancelable` (`events_subscriptions`).
- "`CentralAngle` is not an instance data-member of `fort_wedge_ability_target_query`"
  — renamed `Angle`, in radians (90° = `1.5708`).
- "Unknown identifier `self_ability_target_query`" — renamed
  `fort_self_ability_target_query` (Epic's quickstart page still shows the old name).

### 3509 — type mismatch / "No overload of the function matches" (5 hits)

- `tuple(player, rational)` where `tuple(agent, int)` expected → integer `/` gave a
  `rational`; convert: `if (N := Floor[(A * 1.0) / (B * 1.0)])`.
- "No overload of `ToString` matches (:logic)" → there is no `ToString` for `logic`;
  write `if (Flag?) then "true" else "false"`.
- "expects []int but this initializer is []tuple(…)" → you used the `array:` block
  form, which builds a tuple per line. Use `array{1, 2, 3}`.
- "No overload of `=` matches" on two device references (`chair_device`, most
  `*_device`) → devices are not comparable; track them by index in an array
  (`[agent]int`), not by `=` on the device.
- A handler typed `(Player : player)` subscribed to a `listenable(agent)` → match the
  payload exactly (`Arg : agent`, or `Arg : tuple(agent, float)` for
  `ReleasedEvent`).
- "expects a value of type agent->void, but this argument is an incompatible value of type tuple()->void" →
  the handler has **no** parameter; add the one the event sends
  (`OnPressed(Agent : agent) : void`). `trigger_device` sends `?agent` (`devices`).
- "No overload of the function `operator'/'` matches the provided arguments (:int,:type{8.000000})"
  (also `+`, `-`) → only `*` mixes `int` and `float`;
  convert first: `(Count * 1.0) / 8.0`. A float literal needs its decimal point
  (`0.0`, not `0`).

### 3524 — "Must be an array, map, or generator after ':' inside for" (3 hits)

Cause: iterating something that is not iterable, usually because a missing `using`
left a generator call unresolved (`FindSweepHits` without SceneGraph). Fix the import
first; then iterate arrays, maps, or `generator(t)` values only.

### 3502 — "Only 6 persistent `var`s allowed (used 7)" (43.00, verified; 42.x: "Only 4 … (used 5)")

An island may declare at most **six** persistent `weak_map(player, …)` `var`s from
43.00 (four on 42.x), counted across every file. Every offending line gets the error.
Player Core + Economy + Progression + Time Tracker use four, which leaves two free on
43.00. Fix: nest the new data as a field on an existing persistable table
(`sys_owned_weapons` shows the pattern) rather than adding maps. The offline LSP still
quotes "Only 4"; the build's number is the real one.

### 3502 — "`Self` in an instance variable initializer is not yet implemented" (43.00)

A field initializer wrote `Self.Field`. 43.00 lets an initializer read an earlier
`<final>`, non-`@editable` field by its **bare name** (`WarnAt:float = RoundSeconds - 10.0`);
drop `Self.` (`classes`).

### 3506 — 43.00 material inheritance on re-upload (from the upgrade notes, not probed here)

43.00 turns on Verse material inheritance: material instances now inherit from a common
base material class. Rare compile errors when you re-upload:

- **Qualified member access** `Value.(M_Child)Member` fails with "unknown member" when
  `Member` moved to the parent class. Drop the qualification, or name the parent class.
- **Same-name extension methods** on two material classes that now inherit from each
  other conflict. If they're identical, delete the child's; if not, rename one. Tip: rename
  them all to surface every call site, and fix children before parents.

### Type mismatch (likely 3509, not probed) — 43.00 `agent_group.AddMember` / `RemoveMember` return `result(void, …)`

42.x: `AddMember(Agent, Info):result(comparable, add_member_error)`; 43.00 (`/Verse.org/AgentGroup`):
`result(void, add_member_error)` (same for `RemoveMember`). Code that **bound or compared** the old
`comparable` success value (`Key := Group.AddMember(...).GetSuccess[]` then used as a map key or
`=`) gets a type mismatch (3509). Fix: keep your own key (the agent itself), and use
`.GetSuccess[]` only as a yes/no check: `if (Group.AddMember(A, Info).GetSuccess[]):`. Calls in
statement position (chat channels, conversations, text chat pages) are unaffected.

### 3506 — 43.00 Progression API renames (quest code from 42.x)

The quest API was rewritten when it left Experimental. Old names fail with 3506:

| 42.x | 43.00 |
| --- | --- |
| `JoinQuest(Quest, Participant, Info)` / `AbandonQuest(…)` | `Quest.Join(Participant, Info)` / `Quest.Abandon(Participant)` |
| `join_quest_error` / `abandon_quest_error` | `quest_error` |
| `progress_quest_objective` + `SetRequiredCount` | `progress_objective` + `SetRequiredProgress` |
| `quest_objective` | `objective` (`/Verse.org/Progression`) |
| `quest_reward.GrantReward(Participants)` / `GetRecipients` | `quest_reward.Grant(Memberships)`; override `OnGrant` |
| `quest_participant_info.Contributes/Observes/Receives` | `Contribute/Observe/Receive` + `SetContribute/SetObserve/SetReceive` |
| `IsComplete[]` on a quest | `Quest.State = objective_state.Complete` |

Also: a quest that implements `has_description` needs `using { /Verse.org/Presentation }`;
without it the archetype fails with "`Name` is not an instance data-member"
(`sys_quests`).

### 3509 (variant) — "expects a value of type tuple(agent,tuple()), but this argument is … tuple(entity,tuple())"

Since 42.40 `ability_context.Instigator` and `fort_projectile_component.GetInstigator[]`
are entities. Cast before using agent members: `agent[Context.Instigator?]`
(scenegraph `custom_abilities`).

### 3502 (variant) — "Using a value of type … as a value of type … is not yet implemented"

A function-typed **parameter** passed to `Subscribe` on an interface-typed
`listenable(t)` parameter. Pass a named function or method instead (verified 42.40).

### 3000 — "Error getting text contents of snippet `…/Verse/X/file.verse`"

A `.verse` file was deleted on disk while UEFN was open; the build still lists it. Put
the file back, then delete it through Epic `VerseToolset.VerseToolset.Delete` (it
tells the build), or restart the editor. Verified 42.40.

### 3509 (variant) — "The assignment's left hand expression type … cannot be assigned to"

You wrote `set` on an immutable binding: `Prev := 0.0` then `set Prev = P`, or a
name bound in an `if (X := Map[K])` head. Declare it `var Prev : float = 0.0`, or
copy the bound value into a `var` before mutating.

### "Invalid access of internal function … from control scope" (verified)

An Epic API marked `<epic_internal>` cannot be called from creator code, even
though the digest lists it. Confirmed case on 42.10:
`TickEvents.PrePhysics.Subscribe(...)` — `execution_listenable` is
`class<epic_internal>`, so per-frame work must use `OnSimulate` + `loop` +
`Sleep(0.0)` with a measured `GetSimulationElapsedTime` delta (scenegraph
`verse_authoring`). Check for `<epic_internal>` in the digest declaration before
building on any type; the same applies to `party_member_info`.

### Comparisons are failable (3512 variant)

`<`, `<=`, `>`, `>=` on floats carry `<decides>` — `OnGround := Pos.Up <= 1.0`
outside a failure context is E3512. Write it as a `var logic` set inside an `if`:

```verse
var OnGround : logic = false
if (Pos.Up <= GroundHeight + 1.0):
    set OnGround = true
```

### 3511 — "uses parentheses to call a function that has the 'decides' effect"

`<decides>` functions are called with `[]`: `if (Team := Collection.GetTeam[Agent])`.

### 3514 — "Cannot use reserved identifier `_` as definition name"

`_` is reserved. Name the loop variable (`for (Unused : Items)`) or use the value.

### 3100 — "vErr:S88: Expected expression"

Parse error: check 4-space indentation, a `#` comment (never `//` or `/* */`), an
unbalanced `{` `}` or `(` `)`, or a stray `:` at the end of a one-line `if`.

### 9002 — "Cannot find `AI-CatReacts` in Package /…/_Verse/Assets"

An Assets-digest module that is not in this project. The asset folder must exist
under `Content/` and the project must have been built once so the digest lists it.

### Messages to recognise (verified with verse-lsp, 42.40)

| Message | Cause | Fix |
|---------|-------|-----|
| 3512 "This invocation calls a function (`…Sleep`) that has the 'suspends' effect, which is not allowed by its context" | `Sleep` / `Await` / a `<suspends>` call in a function without `<suspends>` | add `<suspends>`, or `spawn{ … }` it (`async`) |
| 3502 "Can't access a function from a preceding type" (shown **at the generic class**) | a class field or function signature naming a generic class is read before it: an earlier folder, an earlier file, or above it in the file | move generic classes to a Content-level folder that sorts first (`Content/Archetypes/`), helpers below the classes (`classes`) |
| 3502 "Module-scoped `var` must have `weak_map` type" | `var X : int` outside any class | put the state on a manager device, or `weak_map(session, …)` (`modules`) |
| 3552 "'branch' is not currently supported in loops" | `branch` inside a `loop` / `for` body | `spawn`, or a `race` (`async`) |
| 3512 "Case might fail because it doesn't handle all possible values and doesn't have a default clause" | `case` over `int` / `string` without `_` | add `_ => …` (`control_flow`) |
| a loop "needs a sub-expression that is async or break" | `loop:` with no `Sleep` / `Await` / `break` | wait each pass, or break (`control_flow`) |

### Tool-side errors that look like compile errors

| Message | Cause | Fix |
|---------|-------|-----|
| "STALE REFLECTION — field has no compiled hash" | Live Script has no readable `__verse_0x…` hash after resolve (build not landed, or a real miss) | Host already compiles + reloads + retries **once**. Do **not** hammer `wire_*`. Check compile output (`WinError 10054` = started), then `get_verse_editables` on the **same** device and wire once. Never place `_v2`. First array item: `wire_verse_device_array(..., target_paths=[one])`. Rewrite: `replace=true` + full list. `skill_read_subskill("uefn", "verse_devices")` |
| "Verse behavior not found … Build Verse Code first" | `set_npc_definition_behavior` before the class existed | build, then retry |
| "Verse struct … not found under _Verse. Recompile Verse" | array field of a new struct, not built | build, then retry |
| "wire_verse_device_array … one target per call" | older app | Pass every target in one `target_paths=[...]` call |

### After fixing

`workspace_list_verse_errors` (offline, catches syntax) → `workspace_compile_verse`
(real build, catches effects/modules) → only then `wire_verse_device_*`,
`set_verse_editable`, `set_npc_definition_behavior`.
