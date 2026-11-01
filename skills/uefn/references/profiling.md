---
description: "UEFN profiling tools and budgets (v43.00): Game Performance widget, Spatial Profiler, Timing Insights, Verse Insights, Memory Snapshot, mobile profiling, Creator Portal Technical tab; frame budgets 16.7 ms / 33.3 ms, the 300 MB publish memory limit, and the Epic MCP profiling toolsets"
metadata:
  order: 30
  label: "Profiling tools + budgets (43.00)"
  default_enabled: false
  load_condition: "The user asks how to profile an island, what a profiling tool shows, what the frame time / memory budgets are, or mentions Timing Insights, Verse Insights, Memory Snapshot, Spatial Profiler, Game Performance, hitches, lag or memory over budget"
---

# Profiling an island (43.00)

Every profiling tool reads a **live session**: Launch Session first (MCP:
`ValkyrieFortniteToolset.SessionToolset.StartSession`). No session, no data.

To have an agent run them, see `profiling_mcp` (the troubleshooting loop).
For known causes and their fixes, see `profiling_fixes`.

## Which tool answers what

| Tool | Answers | Use when | MCP toolset (43.00) |
| --- | --- | --- | --- |
| **Game Performance** widget (editor, bottom right) | Is anything over budget now? Frame time, GPU time, memory go yellow/red. It is the source of the in-game performance warning | Always on while you test. **Take a Look** opens the Spatial Profiler | `SpatialProfilerToolset.ProfilerToolset` `GetMonitorPerformanceEnabled` (Monitor Performance) |
| **Spatial Profiler** | **Where** on the map a metric goes over budget: a top-down grid, sampled where the player stands; blue = in budget, red = over | Find the area first, then dig in there | `SpatialProfilerToolset.ProfilerToolset` (`GetMetricStats`, `GetMetricHotspots`) |
| **Timing Insights** | **What** inside a frame costs time: per-frame bars, timing events per thread | Frame time red, hitches, stutter | `InsightsToolset.TimingProfilerToolset` (client target) |
| **Verse Insights** | Which **Verse** functions cost server time | Server frame time high, Verse-heavy island | `InsightsToolset.TimingProfilerToolset` on the **server** target (`verse` channel) |
| **Memory Snapshot** | **What** is loaded: every UObject, its class and its memory, by category (Texture is usually the biggest) | Memory red/yellow, mobile | `InsightsToolset.MemorySnapshotToolset` (local clients only) |
| Memory on every cook | Publish memory in MB, with a per-asset breakdown in the Game Performance report | Every launch / push; over 300 MB blocks publishing | (automatic) |
| **Creator Portal → Projects → Technical** | Live players: Client tab (Client Crashes, Hitch Rate, Missed Frames), Server tab (Frame Time, CPU, Memory, P95/median, version markers) | After publishing, to spot regressions per version | none (web); see `creator_portal` |

## Budgets

| Metric | Budget | Where it comes from |
| --- | --- | --- |
| Client frame time | **16.7 ms** (60 fps = 1000 / 60) | Timing Insights draws the 60 fps line |
| Client frame time, low-end | **33.3 ms** (30 fps) | the second line in the Frames panel |
| Server frame time | **33.3 ms** | Spatial Profiler server source |
| Server CPU | **75 %** | Creator Portal Server tab |
| GPU time (Desktop) | 15 ms | the Spatial Profiler's stats |
| Client memory (Desktop) | ~4.61 GB; the Fortnite client alone uses most of it | Spatial Profiler `thresholdValue` |
| Map memory (publish) | **300 MB** (was 100,000 units) | calculated on every cook |

Budgets depend on the **settings profile**. The Spatial Profiler's
**Metric and Heatmap Settings → Profile** switches Desktop / Mobile. Mobile is
stricter, and switching only changes the thresholds, not the data. Read the live
budget with `ListMetrics` / `GetMetricStats` (`thresholdValue`, in the metric's
`unit`: bytes, microseconds, or a count) instead of hard-coding it.

## Timing Insights: how to read it

1. **Frames panel**: one bar per frame. Bars above the 60 / 30 fps lines are the
   problem frames; click a tall one.
2. **Timing View**: each block is a timing event and wider means slower. Lanes are
   threads (**GameThread** runs game logic and physics). A block under another
   was called by it, so wide **and** deep is the real cost.
3. **Timers panel**: summed and ranked. **Inclusive** = the time with everything it
   called; **Exclusive** = the time by itself. Big inclusive + big exclusive = the
   timer itself is the cost. Big inclusive + small exclusive = look at what it calls.
4. **Callees panel**: follow the hot path (flame icon), the most expensive call at
   each level (also called top-down).

What a capture holds (`GetRecordedChannels`):
- **Client:** `csv` CPU scopes on the game and render threads + `frame`. Shipping
  UEFN clients have no `cpu`/`stats` channel, so csv scopes (e.g. *Effects*,
  *Physics*, *Animation*, *UI*) are the finest timing.
- **Server:** `frame` + `verse` (Verse sampling = Verse Insights).
- **Never recorded:** GPU timing, memory allocations, network traffic, asset loading.
- The `.utrace` timeline starts at **process launch**; the capture is the last
  `elapsedSeconds` of it.

## Verse Insights

- Capture the **server** target (`bIsServer = true` in `ListTargets`), whose trace
  has the `verse` channel. Server capture needs secure tracing on both ends:
  check `CanCapture` first, since a fresh server may not have reported yet.
- Turn on the **Use Verse VM** launch option for the session when you need Verse
  VM timing (VerseVM session toggle, 42.40).
- Hot Verse function → see verse `runtime_pitfalls` (work every tick, polling
  loops, a `for` over every player or prop each frame).

## Memory Snapshot

- Client only, local clients only (`CanSnapshot`). Breakdown by category, then
  by asset, in MB.
- Filters: **Persistent Level** (what your level loads) and **Scene Graph**
  (entities/components) to separate your island from the Fortnite client base.
- Streaming matters. A snapshot shows what is loaded **now**: textures far
  away are mipped down. Stand next to the suspect area (Spatial Profiler:
  right-click a cell → teleport) before you snapshot.
- **Quick Find**: search the snapshot by asset name.
- After changing an asset: **Push Changes**, then take a new snapshot to confirm.

## Mobile

- Switch the Spatial Profiler profile to **Mobile** to see which cells would fail
  on lower-end devices.
- For real numbers, connect UEFN to Fortnite on the phone and profile that client
  (it shows up in `ListClients` / `ListTargets`).
- Memory is the usual mobile failure: textures first (see `profiling_fixes`).

## MCP toolsets (live, 43.00)

| Toolset | Tools |
| --- | --- |
| `InsightsToolset.InsightsTargetToolset` | `ListTargets`, `ListCaptures`, `ListSavedCaptures` |
| `InsightsToolset.TimingProfilerToolset` | `CanCapture`, `StartCapture`, `GetCaptureStatus`, `StopCapture`, `GetRecordedChannels` |
| `InsightsToolset.MemorySnapshotToolset` | `CanSnapshot`, `TakeSnapshot` |
| `SpatialProfilerToolset.ProfilerToolset` | `ListClients`, `AcquireSource`, `ReleaseSource`, `ListSources`, `ListMetrics`, `SetEnabledMetrics`, `StartSampling`, `StopSampling`, `GetSamplingStatus`, `GetMetricStats`, `GetMetricHotspots`, `ClearSamples`, `GetMonitorPerformanceEnabled`, `OpenProfiler`, `RevealMetric` |
| `ValkyrieFortniteToolset.SessionToolset` | `StartSession`, `StopSession`, `StartGame`, `StopGame`, `PushChanges(bVerseOnly)`, `GetSessionStatus`, `GetGameState`, `GetVerseOutput`, `GetClientLogEntries` |

Call them through `unreal__call_tool(toolset_name, tool_name, arguments)`. The
order and arguments are in `profiling_mcp`.
