---
description: "Events & subscriptions (42.40 → 43.00) — event(t) vs listenable / subscribable / awaitable / signalable, Subscribe returns cancelable, handler shapes, Await loops and race-to-cancel, UMG Verse field events, why event(t) has no Subscribe in 42.40, the 43.00 change (event(t) subscribable by default; delete your own Subscribe extensions), exact compile errors"
metadata:
  order: 5
  label: "Events & subscriptions (42.40 → 43.00)"
  default_enabled: false
  load_condition: "Subscribing to or awaiting events, event(t) vs listenable, cancelable / unsubscribing, UMG event field clicks, 'Unknown member Subscribe in event', a Subscribe extension or event_subscription / AwaitForEvent helper, or the 43.00 subscribable-events change"
---

## Events & subscriptions

Read from the 42.40 `Verse.digest.verse`; every pattern below **compiled with 0 errors
in UEFN 42.40** (Oct 16 2026). Concurrency basics (`spawn`, `race`, `branch`): `async`.

### The five types

| Type | Gives you | Effects |
| --- | --- | --- |
| `awaitable(t)` | `Await()` — suspends until the next signal, returns the payload | `<suspends>` |
| `subscribable(t)` | `Subscribe(Callback)` — calls `Callback(Payload)` on every signal, returns a `cancelable` | `<transacts>` |
| `signalable(t)` | `Signal(Val)` — resumes the awaiters, then calls the subscribers synchronously | — |
| `listenable(t)` | `awaitable(t)` + `subscribable(t)` | |
| `event(t)` | **42.40:** `signalable(t)` + `awaitable(t)` — `Signal` and `Await` only, **no `Subscribe`** | |

`event()` is `event(tuple())`; `listenable()` is `listenable(tuple())`.
`cancelable.Cancel()` (`<transacts>`) unsubscribes.

**Where each shows up.** Device events (`Button.InteractedWithEvent`), playspace
(`PlayerAddedEvent()`), `fort_character` (`EliminatedEvent()`), agent groups
(`AddMemberEvent`), voice channels (`BeginBroadcastEvent()`) and abilities
(`BeginUseEvent`) are **listenable** → `.Subscribe(Handler)` or `.Await()`. Your own
`event(t)` fields and **UMG Verse field events** (`event(tuple())`,
`event(tuple(int))`) are **event** → `.Await()` in 42.40.

### Subscribe (listenable)

```verse
using { /Verse.org/Simulation }

OnBegin<override>()<suspends>:void =
    Sub := Button.InteractedWithEvent.Subscribe(OnPressed)   # keep it to unsubscribe
    GetPlayspace().PlayerAddedEvent().Subscribe(OnPlayerAdded)

OnPressed(Agent:agent):void = {}
OnPlayerAdded(Player:player):void = {}
```

- The handler's parameter must match the payload exactly (`agent`, `player`,
  `tuple(agent, float)` …) — the digest says which. A `tuple()` payload takes a
  handler with no parameters (`OnClosed():void`) or `(E:tuple())`.
- Handlers are synchronous. To wait inside one, `spawn{ Async() }`.
- Pass a **named** function or method. Passing a function-typed *parameter* into
  `Subscribe` on an interface-typed `listenable(t)` parameter fails: Script error
  3502 "… is not yet implemented" (verified 42.40).

### Await (event, and anything awaitable)

```verse
picker := class:
    Picked<public>:event(int) = event(int){}
    Stop<public>:event() = event(){}

# Every pick until Stop wins the race.
WatchPicked(P:picker)<suspends>:void =
    race:
        loop:
            Slot := P.Picked.Await()
            Print("picked {Slot}")
        P.Stop.Await()

Fire(P:picker):void =
    P.Picked.Signal(2)
    P.Stop.Signal()
```

Start **one** watcher per event source — a second watcher on the same widget runs the
handler twice per click. These loops keep working after 43.00.

### UMG Verse field events

A widget event field reflects as `OnBuyClicked<public>:event(tuple()) = external {}` or
`event(tuple(int))` (read the number with `Picked(0)`). In 42.40: await it in a loop
(above), or on a Verse UI Kit screen use the kit's `Helper.SubscribeToEvent(Player,
Widget.OnBuyClicked, OnBuyClicked)` and `Helper.ClearAllForPlayer(Player)` on close.
Field setup and button binding: `umg_verse_field_events`, `verse_ui_kit`.

### 43.00: event(t) becomes subscribable

Epic (42.40 release notes and the UMG field events tutorial): from **43.00** `event(t)`
is subscribable by default and `event.Subscribe` returns a `cancelable` directly.

- **Published islands keep running.** Unpublished code that defines its *own*
  `Subscribe` on events gets ambiguous-overload / name-conflict errors when built on
  43.00. Epic's tutorial shipped exactly such a helper: an `event_subscription` class,
  an `AwaitForEvent` function and the extension
  `(Event:event(t) where t:type).Subscribe(Callback(:t):void):event_subscription`
  — it compiles on 42.40, and Epic says to remove it for 43.00.
- **Migrate:** delete the `Subscribe` extension (and `event_subscription` /
  `AwaitForEvent` if nothing else uses them). Calls like
  `Widget.OnBuyClicked.Subscribe(OnBuy)` keep compiling against the built-in one; a
  variable typed `: event_subscription` becomes `: cancelable` (`.Cancel()` is the same).
- **Until 43.00 ships**, never write a `Subscribe` extension on `event` — use an Await
  loop. Ducky's Verse lint warns on one. Once a project's digest shows `event` with
  `subscribable` (`get_verse_api({"name": "event"})`), `.Subscribe` on events is fine.

### Exact errors (42.40)

| Error | Cause | Fix |
| --- | --- | --- |
| 3506 Unknown member `Subscribe` in `event(int)` | `.Subscribe` on an `event` in 42.40 | Await loop / kit helper. If the message adds "Did you forget to specify using { …/SomeFolder }", another folder defines a `Subscribe` extension — 43.00 will break that one |
| 3502 "… is not yet implemented" | function-typed parameter passed to `Subscribe` | pass a named function / method |
| 3509 parameter expects `tuple(agent, …)` but argument is `tuple(player, …)` (or the reverse) | handler type ≠ payload type | match the digest's payload type |
