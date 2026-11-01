---
description: "My island has frame drops / hitches / lag / stutter / low FPS / memory over budget / runs badly on mobile: profile it and fix it through the Epic UEFN MCP (v43.00). The agent loop: running session, baseline capture (Spatial Profiler stats, Timing Insights trace, Memory Snapshot), read it, propose fixes, ask, apply, push, re-capture and compare. Symptom to tool table and the exact InsightsToolset / SpatialProfilerToolset calls"
metadata:
  order: 31
  label: "Profile + fix via MCP (43.00)"
  default_enabled: false
  load_condition: "The user says the island has frame drops, hitches, lag, stutter, low FPS, a performance warning, memory over budget, runs badly on mobile or a slow server, or asks the agent to profile / optimize the island"
---

# Profile and fix an island through MCP

When the person says *"my island has frame drops / hitches / lags / is over
memory, take a look"*, follow this loop. Epic's own demo (Oct 31 2026) runs it
end to end: frame drops traced to a CPU Niagara waterfall at **46 ms median**
(budget 16.7 ms), fixed, then re-captured with every frame under budget.

Tools and budgets: `profiling`. Causes and fixes: `profiling_fixes`.
Calls go through `unreal__call_tool(toolset_name, tool_name, arguments)`; Epic
MCP rules (check every result, serial calls) are in `epic_mcp`.

## The loop

1. **Session running.** `ValkyrieFortniteToolset.SessionToolset.GetSessionStatus`
   must be `Connected` and `GetGameState` `Running`. If not, ask before
   `StartSession` (it uploads the island) and `StartGame`.
2. **Baseline.** Capture before touching anything (recipes below): Spatial
   Profiler stats for the symptom's metric, then a Timing capture (frame time) or
   a Memory Snapshot (memory). Write down median, worst and the % of samples over budget.
3. **Read it.** Name the cost: the top csv scope / timer, the Verse function, or
   the top memory assets. Find the actor or asset behind it (search the level,
   open the Niagara system / texture / mesh and read its settings).
4. **Propose, then ask.** Show a table: metric → value → budget, the cause in one
   line with the math (e.g. `5,000/s × 8 s = 40,000 particles`), and the fix with
   its expected gain. Ask before applying (`ducky_ask_user`). Answer follow-up
   questions (CPU vs GPU, is the collision needed) from `profiling_fixes`.
5. **Apply.** Normal editor edits through the right toolset (Niagara, Object,
   StaticMesh, Verse). Save the assets.
6. **Push.** `SessionToolset.PushChanges` (`bVerseOnly: true` when only Verse
   changed; it is much faster).
7. **Re-capture and compare.** Same capture, same spot, same action as the
   baseline. Report before → after per metric. Still over budget → back to 3.

## Symptom → tool

| Symptom | First tool | Then | Look for |
| --- | --- | --- | --- |
| Frame drops / hitches / low FPS | Spatial Profiler frame time stats + hotspots | Timing capture on the **client** | csv scope eating the frame (*Effects*, *Physics*, *Animation*, *UI*) |
| Server hitch, lag, rubber-banding | Spatial Profiler on the **server** source | Timing capture on the **server** (`verse` channel) | Verse functions; server frame time > 33.3 ms |
| Memory over budget / warning | Spatial Profiler memory stats | Memory Snapshot on the client | top Texture / StaticMesh assets in MB |
| Only bad on mobile | Spatial Profiler with the **Mobile** profile | Memory Snapshot near the red cells; profile a phone client | textures, Nanite fallback meshes |
| Verse hot function / runtime errors | `SessionToolset.GetVerseOutput` | server Timing capture | per-tick loops, runtime error spam |
| Publish blocked on memory | Game Performance report (memory on cook, 300 MB) | Memory Snapshot | per-asset MB |

## Recipes (exact 43.00 calls)

**Targets.** `InsightsToolset.InsightsTargetToolset.ListTargets {}`. The first
call (and the first after idle minutes) **fails while discovery starts**: call it
again. Each entry has `instanceId`, `displayName` and `bIsServer`. The client is `bIsServer: false`.

**Timing capture (Timing / Verse Insights).**
1. `InsightsToolset.TimingProfilerToolset.CanCapture {instanceId}` → `bCanUse`, or a `reason`.
2. `StartCapture {instanceId}`. A server needs a few seconds for the secure handshake.
3. The person **reproduces the hitch**: walk to the area, trigger the effect.
   About 20 s is enough. `GetCaptureStatus {instanceId}` shows `elapsedSeconds`.
4. `StopCapture {instanceId}` → `.utrace` path. `InsightsTargetToolset.ListCaptures {}`
   lists this session's captures; `ListSavedCaptures {}` lists older ones.
5. Read it: the `unreal__*` toolsets don't analyze a trace. If a separate
   **`unreal-insights`** MCP server is connected (seen next to `unreal-mcp` in
   Epic's 43.00 Verse Insights demo), list its tools and read the trace with them.
   Otherwise open the file in Timing Insights with the person (`verse_insights`
   for server / Verse traces), or read its csv scopes and frame events with a
   trace reader in the sandbox. What a trace holds: `GetRecordedChannels {kind: "Client"|"Server"}`.

**Memory Snapshot.**
1. Stand near the suspect area (streaming hides far textures).
2. `InsightsToolset.MemorySnapshotToolset.CanSnapshot {instanceId}`; local clients only.
3. `TakeSnapshot {instanceId}` → trace path (every loaded UObject, its class and memory).
   It can take up to ~90 s.

**Spatial Profiler stats (the quickest numbers).**
1. `SpatialProfilerToolset.ProfilerToolset.GetMonitorPerformanceEnabled {}`. Note it:
   if it was on, it **must be on again when you finish**, sampling the same metrics.
2. `ListClients {}` (retry once), then `AcquireSource {instanceId}`.
3. Poll `ListSources {}` until `numAvailableQuantityMetrics > 0`; keep the `handle`.
4. `ListMetrics {source: handle}` → `metric.classPath`, `unit`, `thresholdValue`.
5. `SetEnabledMetrics {source, metricIds: [{classPath}]}` → `StartSampling {}`.
6. Play / reproduce, then `GetMetricStats {source, metric}` → median, max,
   `numValuesOutsideThreshold / numValues`, `normalizedValue` (1.0 = at budget).
   `GetMetricHotspots {source, metric, maxResults: 10}` → worst cells (a server
   puts every sample in one cell at the origin).
7. `StopSampling {}`. `RevealMetric {source, metric}` shows it to the person.
   Units are bytes, microseconds (÷ 1000 = ms) or a count.

## How to read and report

| Metric | Value | Budget | |
| --- | --- | --- | --- |
| Frame Time | 46 ms median, ~22 FPS (161 ms worst) | 16.7 ms | over in 100 % of samples |
| GPU Time | 5.4 ms median | 15 ms | ok |
| Memory Usage | 4.92 GB median | 4.61 GB | over in 100 % |
| Map Memory (publish) | 40 MB | 300 MB | ok |

- **Frame time:** report the median and the worst (or P95), not the mean. One
  scope taking most of the frame (here *Effects* ~40 of 46 ms) is the cause.
- **GPU fine + frame time bad** = CPU-bound (game thread): particles on the CPU,
  physics, Verse, animation.
- **Memory:** the top assets by MB at snapshot time, and their full-resolution
  cost (streaming hides it).

Then give the cause (actor / asset, the setting, the math), the fix, the expected
gain, and a question. Example: *"frame drops → Timing capture → Effects ~40 of
46 ms → NS_Waterfall CPU collision on 40,000 particles → GPU sim, collision off →
re-capture: every frame under the 60 fps line."*

## Rules

- **One capture at a time.** Don't overlap a Timing capture, a snapshot and a
  sampling run on the same target; their numbers bleed into each other.
- **Check every `unreal__*` result.** A failed capture can still return a
  payload, not an error. Anything that isn't an explicit success is a stop (see `epic_mcp`).
- **Results vary run to run.** Compare medians from the same spot and action, and
  re-capture before claiming a fix worked. Agents won't take the same steps each run.
- **The person reviews the edits.** Fixes are regular editor changes. Say what
  you changed (asset, property, old → new) so they can undo it.
- **Restore what you touched:** the Monitor Performance state and acquired sources
  (`ReleaseSource {instanceId, bDiscardData}` only once the person is done with them).
- Memory: most of the client's ~4.9 GB is Fortnite itself. Say how much of the
  overage your fix removes, not "fixed".
- Never restart UEFN or the session just to profile, and never use `execute_python`
  for something a toolset covers.
