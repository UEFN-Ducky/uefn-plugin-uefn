---
description: "Verse Insights (v43.00): profile the server's Verse code in a live session. Use Verse VM, Tools → Profile → Timing Insights on the Server target, Save to File and naming traces, the Frames / Timing View / Timers panels (Game Frame vs Instance mode, Incl vs Excl, native and bytecode), isolate a timer, find the Verse path, the spawn-burst fix (spread work across frames with Mod + Sleep, one AddEntities per batch), before/after trace comparison, and the agent flow through unreal-insights"
metadata:
  order: 33
  label: "Verse Insights: read + fix (43.00)"
  default_enabled: false
  load_condition: "The user asks how to use or read Verse Insights, which Verse function makes the server hitch or lag, why a spawn / reset / build spikes the server frame, or how to compare two Timing Insights traces"
---

# Verse Insights (43.00)

Verse Insights records **which Verse functions run on the server in each game
frame and how long each took**. Use it for server hitches, spikes when something
spawns or resets, and server frame time over **33.3 ms**. Client costs
(particles, textures) are in `profiling` / `profiling_fixes`.

## 1. Record a capture (editor)

1. **Use Verse VM, before launching.** Launch Session's **⋮** menu →
   **Session Options** → **Use Verse VM**. Without it, Timing Insights shows the
   banner *"Server and Verse profiling are only available when the server runs
   the Verse VM"*. Verse Reload is off while it is on (`verse_build_lifecycle`).
2. **Tools → Profile → Timing Insights.** Set the target dropdown (top left) to
   **Server**, not your client.
3. **File → Save to File** to keep the trace. It only applies to captures
   started **after** you turn it on.
4. **Start.** You can start before or during the session. Reproduce the hitch
   (step on the pad, press reset), then **Stop**.
5. **Rename the saved trace** before the next run (`session1`, `session2`):
   File → open the trace folder. A new recording overwrites the old one.

## 2. Read it

| Panel | What it shows | What to do |
| --- | --- | --- |
| **Frames** | One bar per server game frame (60 / 30 fps lines at 16.7 / 33.3 ms) | Click the tallest bar. 1 s = 0.9 FPS on the server |
| **Timing View** (*Verse Sampling* track) | That frame as a call tree: a block under another was called by it; **wider = slower** | Walk down from the top (`OnSimulate` → handler → …). The deepest block that is still wide is the culprit |
| **Timers** | Every timer, named after its Verse function, summed and sortable | Sort by time, then by Count |

**Timers modes** (the **Mode** dropdown):
- **Game Frame**: Max / Avg / Med / Min per game frame. Use it to find the one
  function that spikes a single frame.
- **Instance**: **Count** (calls), **Incl** (total with everything it calls),
  **Excl** (its own time). A handler with a large Incl and about zero Excl only
  waits on its callees, so look below it. A very high Count is a red flag.
- `native` and `bytecode` timers at the bottom are where time is actually spent:
  engine calls (`AddEntities`, component setup) vs your Verse bytecode.

**Find the code:** hover a timer or block. The tooltip often shows the Verse path
(`/you@fortnite.com/Island/SceneGraph/Gameplay/quarry_component...`).

**Isolate:** double-click a timer to isolate it. Turn on **Main Graph** and
double-click again to get that function's own time graph across all frames
(zoom out to see whether every frame pays it or only a few spike).

## 3. Common cause: a burst in one frame

The video's case: `SpawnQuarry` spawned ~1,000 (agent run: 512) entities in one
`for` loop with no yield. The worst server frame was **~1,000–1,300 ms** vs a
normal ~33 ms. `OnSimulate` (native, once per new entity) and `AddEntities` took
most of it.

**Fix: spread the work over frames.** A function that does a lot of work should
be `<suspends>` and yield every N items:

```verse
# inside a <suspends> function; SleepMod = items per frame (e.g. 10)
var C:int = 0
for (F := 0..Len - 1, L := 0..Width - 1):
    set C += 1
    Entity.AddEntities(array{EP_Cube{}})        # EP_Cube = your entity prefab
    # ...set up the new entity...
    if (Mod[C, SleepMod] = SleepMod - 1). Sleep(0.0)   # yield one frame
```

- `Mod[X, Y]` is `<decides>` (`Verse.digest`), so it goes in `if (...)` with brackets.
- `Sleep(0.0)` yields one frame. Make `SleepMod` an `@editable` so you can tune
  it without code changes (10 per frame took the spike frame to **18 ms**).
- **Batch:** build one array per layer and call `AddEntities` **once** instead
  of once per entity.
- **Pool** instead of destroy + respawn on reset (`sys_spawning`, verse `runtime_pitfalls` §4).
- Each spawned prefab pays for its components (`rigid_body`, replication,
  transform, material). Drop the ones it doesn't need.

The total time stays about the same. It just no longer lands in one frame, so
the server stops hitching.

## 4. Compare before / after

**File → Open Trace File** → the renamed `session1` trace, then `session2`.
Compare the worst frame and the top timer's Max in Game Frame mode. Report
before → after (e.g. worst frame 1,298 → 206 ms, longest call ~500 → 31 ms).
If a smaller spike remains, the next timer down (here per-entity `OnSimulate`) is
the next fix.

## 5. Agent flow (MCP)

- Capture: `InsightsToolset.TimingProfilerToolset` on the **server** target
  (`ListTargets` → `bIsServer: true` → `CanCapture` → `StartCapture` → person
  reproduces → `StopCapture`). The full loop and rules are in `profiling_mcp`.
- Read: in the video, Claude Code read the `.utrace` through a separate
  **`unreal-insights`** MCP server, next to `unreal-mcp`. It reported the worst
  frame, the timeline, the time per function and the Verse file behind them.
  If that server is connected, list its tools and use them; tool names were not
  shown on screen, so never guess them. If it is not connected, open the trace
  in Timing Insights with the person (sections 2 and 4).
- Then: read the Verse file it names, propose the fix (section 3), **ask**, edit,
  build, `SessionToolset.PushChanges {bVerseOnly: true}`, capture again with the
  same action, and report the deltas.
