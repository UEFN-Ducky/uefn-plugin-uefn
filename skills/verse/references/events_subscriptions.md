---
description: "Events & subscriptions (43.00, with 42.x notes) — event(t) is listenable in 43.00 so event.Subscribe returns a cancelable, listenable / subscribable / awaitable / signalable, handler shapes, Await loops and race-to-cancel, UMG Verse field events, MakeProxyListenable, migrating off own Subscribe extensions, why 42.x event(t) had no Subscribe, exact compile errors"
metadata:
  order: 5
  label: "Events & subscriptions (42.40 → 43.00)"
  default_enabled: false
  load_condition: "Subscribing to or awaiting events, event(t) vs listenable, cancelable / unsubscribing, UMG event field clicks, 'Unknown member Subscribe in event', a Subscribe extension or event_subscription / AwaitForEvent helper, or the 43.00 subscribable-events change"
---

## Events & subscriptions

Read from the 43.00 `Verse.digest.verse`; the `event(t).Subscribe` pattern **compiled
with 0 errors in UEFN 43.00** (Nov 1 2026), the rest also in 42.40. Concurrency basics
(`spawn`, `race`, `branch`): `async`.

### The five types

| Type | Gives you | Effects |
| --- | --- | --- |
| `awaitable(t)` | `Await()` — suspends until the next signal, returns the payload | `<suspends>` |
| `subscribable(t)` | `Subscribe(Callback)` — calls `Callback(Payload)` on every signal, returns a `cancelable` | `<transacts>` |
| `signalable(t)` | `Signal(Val)` — resumes the awaiters, then calls the subscribers synchronously | — |
| `listenable(t)` | `awaitable(t)` + `subscribable(t)` | |
| `event(t)` | **43.00:** `signalable(t)` + `awaitable(t)` + `listenable(t)` — `Signal`, `Await` **and `Subscribe`**. (42.x: no `Subscribe`.) | |
| `proxy_listenable(t)` | 43.00: `MakeProxyListenable(L)` wraps a `listenable` so callers can Subscribe/Await but not cast it back to your `event` and `Signal` it | `<reads>` |

`event()` is `event(tuple())`; `listenable()` is `listenable(tuple())`.
`cancelable.Cancel()` (`<transacts>`) unsubscribes.

**Where each shows up.** Device events (`Button.InteractedWithEvent`), playspace
(`PlayerAddedEvent()`), `fort_character` (`EliminatedEvent()`), agent groups
(`AddMemberEvent`), voice channels (`BeginBroadcastEvent()`) and abilities
(`BeginUseEvent`) are **listenable** → `.Subscribe(Handler)` or `.Await()`. Your own
`event(t)` fields and **UMG Verse field events** (`event(tuple())`,
`event(tuple(int))`) are **event** → `.Subscribe(Handler)` or `.Await()` in 43.00
(42.x: `.Await()` only).

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

### Subscribe on your own event (43.00)

```verse
using { /Verse.org/Simulation }

picker := class:
    Picked<public>:event(int) = event(int){}

event_user := class:
    Picker:picker = picker{}
    var Sub:?cancelable = false

    Start():void =
        set Sub = option{Picker.Picked.Subscribe(OnPicked)}
        Picker.Picked.Signal(2)          # OnPicked(2) runs synchronously

    Stop():void =
        if (S := Sub?):
            S.Cancel()

    OnPicked(Slot:int):void =
        Print("picked {Slot}")
```

Compiled 0 errors on 43.00. To expose an event without letting callers `Signal` it, return
`MakeProxyListenable(Picked)` from a getter typed `listenable(int)`.

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

**43.00 LSP false positive:** the Problems panel / `workspace_list_verse_errors` shows
"Unknown member `Await` in `listenable(…)`" on these loops, plus cascade errors ("Must be
an array, map, or generator", "Dynamic cast $unknown"). The UEFN build compiles them with
0 errors. Check with `workspace_compile_verse` and never rewrite a working Await loop
because of it.

Start **one** watcher per event source — a second watcher on the same widget runs the
handler twice per click. These loops keep working after 43.00.

### UMG Verse field events

A widget event field reflects as `OnBuyClicked<public>:event(tuple()) = external {}` or
`event(tuple(int))` (read the number with `Picked(0)`). In 43.00:
`Widget.OnBuyClicked.Subscribe(OnBuy)` (keep the `cancelable`, `Cancel()` it when the
widget closes). In 42.x: await it in a loop (above), or on a Verse UI Kit screen use the
kit's `Helper.SubscribeToEvent(Player, Widget.OnBuyClicked, OnBuyClicked)` and
`Helper.ClearAllForPlayer(Player)` on close (works on both).
Field setup and button binding: `umg_verse_field_events`, `verse_ui_kit`.

### 43.00: event(t) is subscribable — migrating 42.x code

43.00 digest: `event<native><public>(t:type) := class(signalable(t), awaitable(t),
listenable(t))` with `Subscribe<native><override>(Callback)<transacts>:cancelable`.
`event.Subscribe` returns a `cancelable` directly (release notes: "Verse events are
subscribable").

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
- **Never write a `Subscribe` extension on `event`** — on 43.00 the built-in exists;
  on a 42.x island use an Await loop. Ducky's Verse lint warns on one. Check a
  project's version with `get_verse_api({"name": "event"})`: `listenable(t)` in the
  parent list means `.Subscribe` on events is fine.

### Exact errors

| Error | Cause | Fix |
| --- | --- | --- |
| 3506 Unknown member `Subscribe` in `event(int)` | **42.x only:** `.Subscribe` on an `event` | 42.x: Await loop / kit helper; or move the island to 43.00. If the message adds "Did you forget to specify using { …/SomeFolder }", another folder defines a `Subscribe` extension — delete it on 43.00 |
| ambiguous overload / name conflict on `Subscribe` | **43.00:** your own `(Event:event(t)).Subscribe` extension clashes with the built-in | delete the extension; `event_subscription` vars become `cancelable` |
| 3502 "… is not yet implemented" | function-typed parameter passed to `Subscribe` | pass a named function / method |
| 3509 parameter expects `tuple(agent, …)` but argument is `tuple(player, …)` (or the reverse) | handler type ≠ payload type | match the digest's payload type |
