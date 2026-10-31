---
description: "Async vs synchronous Verse — what <suspends> means, task lifetimes (spawn / branch / sync / race / rush), stop events, defer cleanup, task(t), Sleep/Await, loop rules, event subscriptions, and the rules for calling async code"
metadata:
  order: 5
  label: "Async & structured concurrency — suspends, lifetimes, stop events, defer"
  default_enabled: false
  load_condition: "Anything time-based or event-driven — loops with Sleep, spawn, branch, race, sync, rush, defer, Await, stopping a loop when a player leaves, waiting on events, or 'is this function async?'"
---

## Async vs synchronous — the `<suspends>` model

**The one rule that decides everything: a function is async iff it carries the
`<suspends>` effect.** Async code can pause (across frames/seconds) and resume;
sync ("immediate") code runs to completion in a single instant.

### What is async (`<suspends>`)

A `<suspends>` function may `Sleep`, `Await` events, and call other `<suspends>`
functions. Calling one from another **waits** for it to finish.

```verse
OnBegin<override>()<suspends> : void =        # the entry point IS async
    Trigger.TriggeredEvent.Subscribe(OnActivated)
    spawn{ GameLoop() }                       # lives as long as the device

GameLoop()<suspends> : void =
    loop:
        Sleep(1.0)                            # pauses ~1 second, then resumes
        Tick()
```

| Call | Does |
|------|------|
| `Sleep(Seconds : float)<suspends>` | Pause this task for N seconds. `Sleep(0.0)` yields one frame; `Sleep(Inf)` never returns (a `race` arm that only ends when another wins). |
| `SomeEvent.Await()` | Wait until the event fires once; returns its payload. `Agent := Button.InteractedWithEvent.Await()` |
| `F()` inside `<suspends>` code | Runs F and waits for it. |

### What is NOT async

Plain functions and those marked `<transacts>` / `<computes>` are immediate —
they **cannot** `Sleep` or `Await`, and they return in the same instant.

```verse
TakeDamage<public>(Damage : float)<transacts> : logic = …   # immediate, rollback-safe
GetCount<public>()<transacts> : int = Count                 # immediate getter
BuyWithCurrency(Agent : agent) : void = …                   # immediate event handler
```

Event **handlers** you pass to `.Subscribe` are immediate functions. If a handler
needs to wait, it starts a task with `spawn`.

### The calling rules (this is where compiles fail)

1. A `<suspends>` call is only legal inside another `<suspends>` function or inside
   a `spawn{}` block. Otherwise: "has a suspends effect, which is not allowed in an
   immediate context".
2. **An immediate function can only use `spawn`.** `branch`, `sync`, `race` and
   `rush` all need `<suspends>`.
3. A `<suspends>` call can never sit in a failure context (`if (…)` head, `[]`).

```verse
OnPlayerAdded(NewAgent : agent) : void =        # immediate handler…
    spawn{ StartMouseTracking(NewAgent) }       # …launches async work
```

### Lifetimes — pick the tool by how long the work must live

| Tool | Runs | Ends when | Allowed in | Use for |
|------|------|-----------|------------|---------|
| `F()` | one call | F finishes; the caller waits | `<suspends>` | steps in order |
| `spawn{ F() }` | one call | F finishes, whatever the caller does | immediate or `<suspends>` | starting work from a handler; device-lifetime loops; per-player loops with a stop event |
| `branch:` | several lines | the **enclosing function returns** — all branched work is killed | `<suspends>`, **not inside a `loop` / `for` body** | helpers that must die with a function that keeps running |
| `sync:` | several arms | all arms finish; evaluates to a tuple of results | `<suspends>` | waiting for several things |
| `race:` | several arms | the first arm finishes; the others are cancelled | `<suspends>` | "do X until Y happens" |
| `rush:` | several arms | the first arm finishes; the others keep running **only until the enclosing function returns** | `<suspends>` | rarely useful — see below |

`block:` groups several lines into one arm of `sync` / `race` / `rush`.

**Default:** `spawn` plus a stop event (below) for anything that must keep going;
`race` for "until". Use `branch` only when the function that owns it keeps running
after it, for example:

```verse
RunRound()<suspends> : void =
    branch:
        HudCountdownLoop()           # killed automatically when RunRound returns
    RoundEndedEvent.Await()          # keeps RunRound alive until the round ends
```

A `branch` at the end of `OnBegin` (or any function that then returns) dies at
once — the loop never runs. Branch inside a loop body is rejected by the compiler
("Branch is not currently supported in loops").

### sync, race, rush

```verse
StartBossFight()<suspends> : void =
    sync:
        CloseArenaDoors()          # 3 s
        RevealBossAnimation()      # ~4 s
        PlayIntroMusic()           # 4 s
    EnableBossAI()                 # runs only after all three finished

BoardGame()<suspends> : void =
    race:
        AwaitPlayerLeftGameEvent()   # if this finishes first…
        PlayBoardGame()              # …this is cancelled mid-way
    CleanUpGame()
```

**`rush` is not "finish in the background".** Its losing arms are cancelled the
moment the function containing the `rush` returns. To let the slower work really
finish, start it with `spawn` and race over the tasks — a race never cancels a
spawned task:

```verse
SaveProgress(P : player)<suspends> : void =
    LocalSave := spawn{ SaveToLocal(P) }
    CloudSave := spawn{ SaveToCloud(P) }
    race:
        LocalSave.Await()
        CloudSave.Await()
    ShowSavedNotification()          # after the faster save; the other keeps going
```

### Tasks

`spawn` returns a `task(t)`, where `t` is the spawned function's return type. The
type lives in `/Verse.org/Concurrency`. In 42.40 a task has only `Await()` — there
is **no `Cancel()`**.

```verse
using { /Verse.org/Concurrency }

TimerTask : task(int) = spawn{ RunTimer(30) }   # inside a <suspends> function
Seconds := TimerTask.Await()                    # waits, then returns RunTimer's result
```

### Stopping work — the stop-event pattern

A race cancels its own arms, **not** a task you spawned and then awaited inside an
arm: that task keeps running. To make long work stoppable, race against a stop
event **inside** the task:

```verse
# One per player. Stop() ends the loop so the widget and its data can be freed.
hud_updater := class:
    StopEvent : event() = event(){}

    Start() : void =
        spawn{ UpdatePeriodically() }

    Stop() : void =
        StopEvent.Signal()

    UpdatePeriodically()<suspends> : void =
        race:
            StopEvent.Await()
            loop:
                RefreshGold()
                Sleep(1.0)
```

Signal the stop event when the player **leaves** and when they are **eliminated**
mid-flow (`runtime_pitfalls` §5). A per-player loop left running after its player
is gone keeps every object it references alive — a leak that grows each session.

### Cleanup — `defer`

`defer:` runs its block when the enclosing scope exits — on a normal return **and**
when a `race` cancels it. It cannot call `<suspends>` functions (it can `spawn`).

```verse
using { /UnrealEngine.com/Temporary/SpatialMath }

SpawnTempProp(Asset : creative_prop_asset, Duration : float)<suspends> : void =
    SpawnResult := SpawnProp(Asset, transform{})   # tuple(?creative_prop, spawn_prop_result)
    if (Prop := SpawnResult(0)?):
        defer:
            Prop.Dispose()                       # runs on return and on cancel
        Sleep(Duration)
```

Without the `defer`, a prop spawned inside a race arm that loses is never disposed.

### Loops

- Every `loop` must wait (`Sleep`, an `Await`) or reach a `break`. A loop with
  neither is rejected by the compiler; a loop whose only `break` can never run
  (`if (false?): break`) **compiles but crashes Verse at runtime** by spinning in one
  frame.
- Code after an endless `loop` in the same function never runs. Put long-lived
  loops in their own `<suspends>` function and `spawn` them.

### Subscribing to events (the async trigger surface)

Which events have `.Subscribe` (listenable) and which only `.Await` (your own `event(t)`, UMG event fields — until 43.00): `events_subscriptions`.

`.Subscribe(Handler)` registers an immediate handler; the event calls it later. Two
shapes appear, depending on the API — an event **field** vs an event **accessor
method** `()`:

```verse
Button.InteractedWithEvent.Subscribe(BuyWithCurrency)        # device event field
Spawner.SpawnedEvent.Subscribe(OnPlayerAdded)                # payload: agent
GetPlayspace().PlayerAddedEvent().Subscribe(OnPlayerJoined)  # playspace: method() then .Subscribe; payload: player
FortChar.EliminatedEvent().Subscribe(OnEliminated)
```

Which form (field vs `()` method) and which payload type an event uses comes from
the **digest** — look it up. The handler's parameter must match the payload exactly
(`SpawnedEvent` gives `agent`; `PlayerAddedEvent()` gives `player`;
`trigger_device.TriggeredEvent` gives `?agent`;
`input_trigger_device.ReleasedEvent` gives `tuple(agent, float)`). Payload table:
`devices`. `.Subscribe` returns a `cancelable`; keep it if you plan to `Cancel()`
later.

### Passing extra data into a handler

`.Subscribe` handlers get a fixed signature. To smuggle in extra context, use a
small wrapper class: a `<unique>` class that stores `ExtraData` plus your
`OutputFunc`, and exposes an `InputFunc(Agent : agent)` (the subscribe shape) that
calls `OutputFunc(Agent, ExtraData)`. Subscribe with the wrapper's `InputFunc`. The
`subscribe_helpers` template pack ships these; general function values and
wrappers: `functions`.

### Anti-patterns

| Wrong | Right |
|-------|-------|
| `Sleep` / `Await` in a non-`<suspends>` function | Add `<suspends>`, or move it into `spawn{}` |
| Calling a `<suspends>` fn directly from an immediate handler | `spawn{ AsyncFn() }` |
| `branch{ Loop() }` as the last thing in `OnBegin` | `spawn{ Loop() }` — the branch dies when `OnBegin` returns |
| `branch` inside a `loop` / `for` body | `spawn`, or restructure with `race` |
| `rush` to "finish in the background" | `spawn` each job, race over `Task.Await()` |
| `loop:` with no `Sleep`/`Await`/reachable `break` | Yield every iteration (`Sleep(0.0)` at minimum) |
| Code after an endless loop in the same function | Spawn the loop from its own function |
| Expecting a value back from `spawn` without awaiting | `Task.Await()`, `sync`, or an event |
| Racing against `SpawnedTask.Await()` to stop it | Stop event raced **inside** the task |
| Per-player loop with no stop on leave / elimination | Stop event signalled from both |
| Cleanup at the end of a function that can be cancelled | `defer:` |
| Guessing `.SomeEvent` vs `.SomeEvent()` or its payload type | Check the event's shape in the digest |
