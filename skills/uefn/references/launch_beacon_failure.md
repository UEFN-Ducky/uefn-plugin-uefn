---
description: "Launch Session fails at Downloading / 'Waiting for client to be ready' with 'Unable to Play: Failed to connect to beacon' (LogNet ConnectionTimeout 30.00, AValkyrieBeaconClient::OnFailure) while other islands launch — oversized generated Verse data, not the network; measure .verse sizes, shrink to flat []int arrays under ~250 KB, close stale FortniteClient"
metadata:
  order: 21
  label: "Launch fails: Failed to connect to beacon"
  default_enabled: false
  load_condition: "Launch Session / StartSession fails at Downloading, 'Waiting for client to be ready', 'Failed to connect to beacon', BeaconNetDriver ConnectionTimeout, AValkyrieBeaconClient::OnFailure, or the session never connects while other islands launch fine"
---

# Launch fails: "Failed to connect to beacon"

## Symptom: Downloading fails with "Failed to connect to beacon"

- Session Inspector: Preparing, Validating, Uploading, Versioning, Cooking all green; **Downloading**
  fails with status "Waiting for client to be ready".
- Output Log: `LogNet: Error: UEngine::BroadcastNetworkFailure ... ConnectionTimeout ... Elapsed: 30.00`
  on `IpNetDriver BeaconNetDriver`, then `AValkyrieBeaconClient::OnFailure`, then the popup
  **"Unable to Play: Failed to connect to beacon"**.
- Ping to the server works and **another island launches fine on the same PC**.

If another island launches, it is **not the network**. Never send the person to check their
firewall, router or VPN for this.

## Root cause: the island's Verse is too heavy to load in 30 s

The session server builds the island's Verse bytecode on load. Big generated data written as
Verse literals (an array of struct literals, one per element; tens of thousands of floats) stalls
that load past the **30 s beacon timeout**, and it surfaces as a network error.

LimoRide (2026-11-01): about **1.7 MB** of generated Verse data (71,659 terrain floats, ~9,600
lines of route and GPS struct literals). Red flag: modules had already been split to stay under
Verse's **16 MB bytecode cap**. Near that cap you are far past what a session loads in time.

## Rules for generated Verse data (HARD)

1. **All generated Verse data ≤ ~250 KB total** (sum of the generated `.verse` files).
2. **Never a struct literal per element** for big tables. Flat `[]int` arrays (positions in cm,
   headings ×10) decoded by accessor functions that keep the public API.
3. Ragged lists (cell contents, per-route points): one flat `[]int` of values plus one `[]int`
   of start offsets.
4. Derived structures (adjacency, lookups) are **built at runtime** in `OnBegin`, never literals.
5. Cut resolution before writing: coarser grids, junction-only graphs, simplified polylines.

Authoring rules for the data module: verse `sys_world_data`.

## Fix recipe (what worked)

1. **Measure:** list the biggest files under `Content/Verse/**` (`workspace_list_dir` with sizes).
   Generated files over ~50 KB are suspects; over ~250 KB in total is the problem.
2. **Regenerate smaller.** LimoRide: terrain on a 32 m grid instead of 8 m; GPS graph cut to
   junction nodes only (199 nodes); routes simplified with Douglas-Peucker at 1.5 m; cell lists as
   flat ints plus a start array; adjacency built at runtime. **1.7 MB → 239 KB.**
3. Keep the accessor API identical so gameplay code does not change.
4. `workspace_compile_verse` — must build clean.
5. Close any stale `FortniteClient-Win64-Shipping` process left from an earlier session before
   retrying.
6. Launch again (Epic MCP StartSession or Launch Session), then `fortnite_client_wait`. LimoRide
   connected first time after the shrink.

## Diagnostic order

Biggest `.verse` files → shrink generated data → `workspace_compile_verse` → close stale
FortniteClient → StartSession → `fortnite_client_wait`. Look at the network only if a tiny
test island also fails on this PC.
