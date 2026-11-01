---
description: "Common UEFN performance causes and their fixes (v43.00): what each looks like in a capture and the MCP toolset that fixes it. CPU Niagara particles with per-particle collision (spawn rate × lifetime), oversized textures (Maximum Texture Size), heavy Verse loops, too many Scene Graph entities/components, Nanite fallback meshes, mobile memory"
metadata:
  order: 32
  label: "Profiling fixes (43.00)"
  default_enabled: false
  load_condition: "A profile or capture shows a cost (Effects / particles, textures, Verse, entities, meshes, memory) and the user or agent needs the cause and the fix; or the user asks whether to use GPU or CPU particles, how big textures should be, or how to cut memory"
---

# Profiling fixes: cause → evidence → fix

Find the cost first (`profiling_mcp`), then match it here. Every fix is a normal
editor edit: ask before applying, save, `SessionToolset.PushChanges`, then
re-capture and compare. Call `unreal__describe_toolset` before the first call to
a toolset; argument and property names are Epic's.

## Quick table

| Cause | Evidence in the capture | Fix | Fix toolset (43.00) | Skill |
| --- | --- | --- | --- | --- |
| CPU Niagara with per-particle collision | Client trace: the *Effects* csv scope takes most of the frame; GPU time fine; frame time red only near the effect (Spatial Profiler hotspot) | GPU sim; turn off collision nobody sees; lower spawn rate × lifetime; fixed bounds; culling on | `NiagaraToolsets.NiagaraToolset_System` | vfx |
| Oversized textures | Memory Snapshot: *Texture* is the top category; 4K maps on small props; `MaxTextureSize = 0` | Maximum Texture Size 512 / 1024, then a new snapshot | `EditorToolset.ObjectToolset` `SetProperties`; `EditorToolset.TextureToolset` `GetSize` | texture-workflow |
| Heavy Verse loops | Server trace `verse` channel: one function on top; server frame time > 33.3 ms; `GetVerseOutput` spam | Event-driven instead of per-tick; batch; cache lookups | `VerseToolset.VerseToolset` (edit + build), `PushChanges {bVerseOnly: true}` | verse `runtime_pitfalls` |
| Too many Scene Graph entities / components | Memory Snapshot (Scene Graph filter) grows with entity count; server frame time grows with spawned entities | Pool and reuse; fewer components per entity; remove per-tick components | `ValkyrieToolset.EntityToolset` (`FindEntities`, `GetComponents`, `RemoveComponent`) | scenegraph `components` |
| Nanite fallback meshes | Mobile / low-end: mesh memory high; heavy meshes with no Nanite or a dense fallback | Lower the fallback triangle count / LODs; Min LOD per quality level | `EditorToolset.StaticMeshToolset` (`SetQualityLevelMinLodDefault`, Nanite and LOD tools) | uefn `nanite_fallback_vertex_count` |
| Mobile memory | Spatial Profiler **Mobile** profile: red memory cells; a phone client over budget | Textures first, then mesh LODs, then fewer unique assets loaded at once | as above | `profiling` (Mobile) |

## CPU Niagara with per-particle collision

**Math first.** Live particles = spawn rate × lifetime. Epic's demo:
`5,000/s × 8 s = 40,000 particles`, each with **CPU collision every frame** =
40,000 traces per frame → *Effects* ~40 of 46 ms, ~22 FPS.

**Read the emitter** (`NiagaraToolset_System`: `GetSystemSummary`,
`GetEmitterSummary`, `GetModuleTopology`, `GetEmitterData`): sim target, spawn
rate, lifetime, Collision module enabled, bounds, distance / visibility culling.

**Fix, in order of payoff:**
1. **Collision you can't see** (underwater, behind geometry): disable the
   Collision module (`SetModuleEnabled`), and kill particles at the surface with
   a shorter lifetime instead.
2. **Spawn rate × lifetime**: e.g. 3,000/s × 4 s = 12,000 live (Epic's manual fix).
3. **GPU sim** (`SetEmitterData`, sim target GPU). GPU emitters need **fixed
   bounds** that box the real effect; huge bounds (the demo's were ~220 m) cull
   badly. If splashes are wanted, use GPU **depth-buffer** collision (on-screen
   surfaces only, cheap).
4. **Culling on**: distance and visibility culling, so it stops when nobody sees it.

Staying on CPU with collision off and a shorter lifetime already takes ~40 ms to
under 1 ms; GPU gives headroom. Re-capture: every frame under the 60 fps line.

## Oversized textures

**Evidence:** Memory Snapshot near the props (stand close: streaming mips far
textures down; the demo's six 4K maps showed ~5 MB at snapshot time but cost ~96 MB
at full resolution). A 4K normal map is ~21 MB, a 4K base color ~11 MB (21 MB
with alpha). Small props (18–43 cm) never need 4K.

**Fix:** `EditorToolset.TextureToolset.GetSize {texture: {refPath}}` to confirm,
then `EditorToolset.ObjectToolset.SetProperties {instance: {refPath},
values: "{\"MaxTextureSize\": 512}"}` (or 1024 for hero props). Save, push, and
take a new snapshot. Worst case drops from ~96 MB to ~1.5 MB at 512 or ~6 MB at
1024, and the download shrinks too. Report how much of the overage that removes:
most of client memory is the Fortnite client itself.

## Heavy Verse loops

**Evidence:** server Timing capture with the `verse` channel (Verse Insights); one
function dominates. `GetVerseOutput` shows runtime errors or log spam every tick.

**Fix:** subscribe to events instead of polling with `Sleep`; never loop over
every player / prop every frame; cache `GetPlayers` / lookups; spread work
across frames. Edit with `VerseToolset`, build, `PushChanges {bVerseOnly: true}`.
Patterns: verse `runtime_pitfalls`, `async`, `events_subscriptions`.

## Too many Scene Graph entities / components

**Evidence:** memory and server time rise with spawned entities; the Memory
Snapshot's **Scene Graph** filter shows thousands of entities / components.

**Fix:** count them with `ValkyrieToolset.EntityToolset.FindEntities` /
`GetComponents`; pool entities instead of spawning and destroying; drop
components that tick but do nothing; merge static visuals into one mesh
component. See scenegraph `components`.

## Nanite fallback meshes

**Evidence:** mobile / low-end memory or frame time is high around heavy meshes;
the mesh has Nanite with a dense fallback, or no LODs.

**Fix:** `EditorToolset.StaticMeshToolset`: check Nanite and the triangle count,
generate or trim LODs, and set the Min LOD per quality level
(`SetQualityLevelMinLodDefault`). Rules and limits: uefn `nanite_fallback_vertex_count`.

## Mobile memory

Profile with the **Mobile** profile or on a real phone (`profiling` → Mobile).
Fix order: textures (Maximum Texture Size) → mesh LODs / Min LOD → fewer unique
assets in one area (split with streaming / data layers). Re-check every cell that
was red.
