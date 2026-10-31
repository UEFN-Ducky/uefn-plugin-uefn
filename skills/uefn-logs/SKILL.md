---
source_plugin_id: uefn
name: uefn-logs
description: Read the real UEFN Output Log (Verse Print / LogVerse lines from play sessions) and the Fortnite client log. Use when a play test "did nothing", to see what Verse printed, or to feed logs into a workflow agent.
license: MIT
metadata:
  label: UEFN Logs
  version: 2
  author: UEFN-Ducky
  copyright: Copyright 2026 Mindful Path Company, LLC
  allow_redistribute: true
---

# UEFN Logs

Verse `Print("...")` from a live session shows up in the UEFN Output Log as
`LogVerse: : <text>`. `get_editor_log` does NOT read that file — use these tools.

Files read (from disk, read-only):
- editor: `%LOCALAPPDATA%/UnrealEditorFortnite/Saved/Logs/UnrealEditorFortnite.log`
- client: `%LOCALAPPDATA%/FortniteGame/Saved/Logs/FortniteGame.log`

## Tools
| Tool | Use |
|------|-----|
| `uefn_logs_sources` | Which files exist and their size |
| `uefn_logs_mark(name)` | Remember the log end before a session |
| `uefn_logs_wait(pattern, fail_pattern, timeout_sec)` | Block until a line appears (stops early on FAIL) |
| `uefn_logs_capture(pattern, mark, max_lines)` | Matching lines since the mark (+ `prompt` for an agent) |
| `uefn_logs_last` | Last capture made by a workflow |

Default pattern: `\[ARRIVAL\]|\[PLAYERCORE\]|LogVerse: .*(Error|error|FAIL)|Script error|VerseRuntime`.
No mark → reads the last ~2 MB of the log.

## Workflow nodes
- `uefn-logs.mark` → put before `uefn.game.start`.
- `uefn-logs.wait` → never aborts; branch on `found` / `failed` / `timed_out`.
- `uefn-logs.capture` → outputs `text`, `lines`, `prompt`, and file `uefn_log_capture.txt`;
  wire into `pipeline.agent` so a ducky diagnoses the run.

Tag your Verse prints (`[ARRIVAL] ...`, `[PLAYERCORE] ...`) so one regex finds the whole flow.

## Empty capture? It usually isn't the game
- The parameter is `mark` (the name you gave `uefn_logs_mark`) — not `since_mark`; a wrong name silently reads the default window.
- Keep `pattern` simple: one tag or `A|B`. Nested groups / lookarounds that don't match return nothing, not an error.
- An editor or session restart rotates the log — mark **again** after every restart, before Play.
- No tagged line at all → the code path never ran (wrong device, handler not subscribed, a placed value disabled it), not "nothing to log".
- Big captures get cut off: lower `max_lines` and narrow the pattern rather than reading everything.
