---
description: "The real Fortnite client a UEFN session launches — fortnite_client_status/wait/capture/move tools and uefn.client.* workflow nodes; never touch a loading client; prove movement from before/after captures"
metadata:
  order: 6
  label: "Fortnite client"
  default_enabled: false
  load_condition: "Play-testing in the real Fortnite client: wait for it, capture it, or move the player after a session launch"
---

## Fortnite client (after a session launch)

These work on the separate Fortnite client window (titled "Fortnite"), never the editor
or the launcher. Start the session first (Epic `SessionToolset.StartSession` /
`StartGame`).

| Tool | Does |
|---|---|
| `fortnite_client_status` | Is the client open, has it loaded into play mode. No input. |
| `fortnite_client_wait(timeout)` | Waits (max 120 s) until it is open AND in play mode (from its log) + 15 s to settle. Does not touch it. |
| `fortnite_client_capture` | Brings the loaded client forward and captures it into the chat. |
| `fortnite_client_move(key, seconds)` | Holds W/A/S/D for 0.1–3 s (always released; stops if focus leaves) with before/after captures. |

Workflow nodes: `uefn.client.wait`, `uefn.client.capture`, `uefn.client.move`; template
**Fortnite client movement check** (Play tests).

**Never touch a loading client (HARD).** No clicks, keys, focus or captures from
`uefn_window_*` while it loads — those only drive UEFN and refuse the client anyway.
Capture and move refuse until the client is in play mode. Loading the client and UEFN on
one GPU can still stall it ("GPU timeout" in `%LOCALAPPDATA%/FortniteGame/Saved/Logs`);
if the client stops responding, report it, do not send more input.

**Prove, don't assume.** `input_sent` is not movement: compare the before/after images
against fixed landmarks; blocked by a wall or unsure → FAIL. Never invent a position,
island code or memory number.
