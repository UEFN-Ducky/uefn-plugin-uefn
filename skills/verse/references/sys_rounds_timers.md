---
description: "Round flow & timers — the game state machine (phase functions chained by events), custom timer devices with typed events, which clock to use, and drift-free countdowns that update the HUD only when the shown second changes"
metadata:
  order: 25
  label: "Game systems — rounds, phases & timers"
  default_enabled: false
  load_condition: "Building match/round flow, game phases/state machine, countdowns, or a custom timer with events"
---

## Rounds, phases & timers

Names below are generic — a round game usually alternates an **active** phase and a
**hold** phase; rename to fit your mode.

### The game state machine (phase functions + events)

Instead of a formal state enum, the match is a chain of **phase functions**, each of
which sets up its phase, starts a timer, and the timer's finished-event calls the
next phase. `OnBegin` bootstraps; loops run in `spawn`:

```verse
using { /Fortnite.com/Devices }
using { /Verse.org/Simulation }
match_controller := class(creative_device):
    var RoundStarted : logic = false
    var EndingStarted : logic = false

    StartRound<public>(InstigatorAgent : ?agent) : void =
        set RoundStarted = true
        if (Level := ActiveLevel?):
            Level.StartBarrierDevice.Disable()
            RoundTimers.RoundTimer.ResetForAll()
            RoundTimers.RoundTimer.Start()
            spawn{ RoundTimerLoop() }          # HUD countdown loop
            StartActivePhase(InstigatorAgent)   # → enter first sub-phase

    StartHoldPhase<public>(InstigatorAgent : ?agent) : void =
        if (EndingStarted?):                    # guard: don't chain past the end
            return
        RoundTimers.HoldPhaseTimer.ResetForAll()
        RoundTimers.HoldPhaseTimer.Start()
        for (Event : PhaseChangedEvent):        # notify subscribers
            Event()
        spawn{ HoldPhaseLoop() }
        # StartActivePhase will be called again when this phase's timer ends
```

Principles that keep this manageable:

- **One function per phase** (`StartRound` → `StartActivePhase` → `StartHoldPhase` →
  … → ending → results). Each does setup + start-timer; the timer's finished event
  advances to the next.
- **Boolean guards** (`RoundStarted`, `EndingStarted`) stop double-entry and stop
  chaining once the match ends.
- **`spawn` the per-phase loops** (movement, HUD tick, phase cycling) so they run
  concurrently; a phase change flips a flag that lets the loop `break`.
- Snapshot teams into arrays (`TeamA`, `TeamB`) at round start and drive the phase
  from those (see `sys_teams`).

Store round-scoped devices in `struct<concrete>` bundles so one `@editable` exposes
them all (`round_timers`, `team_a_devices`, `team_b_devices`).

### Custom timer device

A reusable countdown/count-up device with `@editable` config, per-player HUD, and a
**typed event bus** (same pattern as `sys_player_data`):

```verse
using { /Fortnite.com/Devices }
timer_started  <public> := type{_(CurrentTime : float):void}
timer_finished <public> := type{_(FinalTime : float):void}

custom_timer_device := class(creative_device):
    @editable var TimerDuration : float = 15.0
    @editable CountDown : logic = true
    var IsRunning <public> : logic = false
    var CurrentTime : float = 0.0
    var TimerFinishedEvents <private> : []timer_finished = array{}

    SubscribeTimerFinished<public>(Event : timer_finished) : void =
        set TimerFinishedEvents += array{Event}
```

Consumers wire phase advancement to the finished event:
`RoundTimers.HoldPhaseTimer.SubscribeTimerFinished(OnHoldPhaseDone)`.

### Which clock

| Need | Use |
|------|-----|
| Wait once | `Sleep(Seconds)` |
| A countdown or stopwatch | a deadline on `GetSimulationElapsedTime()` (`<transacts>`, resets each session), checked ~10 times a second |
| Motion every frame | nothing in Verse — keyframed movement (scenegraph `movement_transforms`) |
| Real-world time across sessions (logins, offline earnings) | `GetSecondsSinceEpoch()` (`<reads>`) → `sys_time_tracking` |

Never count `Sleep(1.0)` passes as seconds: each pass runs a little long, so the
count drifts. Measure against the clock instead.

### Countdown loop (no drift, no per-frame HUD)

```verse
RunTimer()<suspends> : void =
    if (IsRunning?):
        return                                  # one loop per timer
    set IsRunning = true
    EndTime := GetSimulationElapsedTime() + TimerDuration
    var ShownSeconds : int = -1
    loop:
        if (not IsRunning?):
            break                               # Stop() clears the flag
        Remaining := EndTime - GetSimulationElapsedTime()
        if (Remaining <= 0.0):
            set IsRunning = false
            for (Callback : TimerFinishedEvents):
                Callback(0.0)
            break
        if (Seconds := Ceil[Remaining], Seconds <> ShownSeconds):
            set ShownSeconds = Seconds
            UpdateTimerUI(Seconds)              # only when the number changes
        Sleep(0.1)
```

- **Single-instance guard** (`IsRunning`) so `Start()` twice doesn't run two
  loops.
- **Fire the finished callbacks, then `break`.** Subscribers advance the phase.
- `Sleep(0.1)` is plenty for a seconds display; `Sleep(0.0)` (every frame) only
  for logic that must react within a frame, and never with UI work inside.
- A per-player countdown also races the player's stop event (`async`).

### Countdowns you don't need to hand-roll

For simple waits, the Fortnite `timer_device` (from the digest) has
`Start`/`SuccessEvent`. Use the custom device when you need per-player HUD, count-up,
or your own event payloads; use the built-in when a plain countdown will do.
